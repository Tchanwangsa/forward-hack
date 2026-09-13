# Telemetry API

**What this is.** The spec for the service in front of the PulseOne fleet. It is the reason the agent has something to react to in real time, and the reason telemetry arrives already classified.

PulseOne hubs are network-connected and already report to a clinical dashboard. This API is the surveillance tap on that connection — it is not a new capability bolted onto the device, it is a second consumer of a stream that already exists.

**The hinge:** an event's `code` is the indicator's `Internal Code`. A hub emitting `CONN-LINK-LOSS` has classified itself as IND-01. Workflow 1 does no work on telemetry; all of its work is on the human-authored sources.

**And the stream now has a second consumer inside the product.** It is tier 1's primary source as well as tier 2's — see §5. Fleet size throughout: **250 hubs**, per [`mock-company-v2/README.md`](../mock-company-v2/README.md).

---

## 1. Endpoints

```
POST /v1/telemetry/events        hub → cloud.  {hub_id, ts, code, severity, sw_version, payload}
GET  /v1/fleet/hubs              current state: online/offline, last_seen, sw, battery, pairing
GET  /v1/fleet/hubs/{hub_id}     unit detail + event history
GET  /v1/telemetry/events        ?code=&from=&to=&customer=&lot=&sw_version=&ward=
GET  /v1/metrics/indicators      deterministic rates per indicator × cohort, denominators shown
POST /v1/webhooks/threshold      fires the agent when a rate crosses its escalation threshold
```

Six endpoints, two write and four read. Nothing else is needed for any of the three tiers — tier 1's outage watch reads `GET /v1/telemetry/events` and nothing more.

### `POST /v1/telemetry/events`

Ingest. Called by hubs, and by the backfill job (§4) with historical timestamps.

| Field | Type | Notes |
|---|---|---|
| `hub_id` | string | `HUB-04111`. The API resolves serial ↔ hub ID; devices may send either. |
| `ts` | RFC 3339 | Device clock. Stored alongside the server receipt time — they disagree, and the gap is real. |
| `code` | enum | One of the seven indicator internal codes, or `HEARTBEAT`. |
| `severity` | `info · warn · error` | Device's own judgement. Not the indicator's review function. |
| `sw_version` | string | `1.1.0`. Authoritative — this is what fixes the blanks in the incident log's `SW Version at Time`. |
| `payload` | object | Code-specific. See §2. |

Idempotent on `(hub_id, ts, code)`. A hub reconnecting after an outage replays its buffer; duplicates are dropped, not counted twice. **This matters for the denominator**: a replayed buffer that counts five times is a fabricated signal.

Returns `202` with an `event_id`.

### `GET /v1/fleet/hubs`

The Fleet screen's data. One row per hub: `hub_id`, `serial`, `customer_id`, `organisation`, `ward_id`, `bed_id`, `hw_revision`, `sw_version`, `unit_status`, `pairing_status`, `last_seen`, `online` (derived: `last_seen` within the offline threshold), `battery_pct`, `install_date`.

Seeded from the `PulseOne Hub Inventory` sheet and kept current by telemetry. Where they disagree, telemetry wins for `sw_version` and `last_seen`; the inventory sheet wins for `customer_id`, `ward_id`, `install_date` and `unit_status`, which no device knows.

### `GET /v1/telemetry/events`

The query surface tier 1's outage watch and WF 1, 3 and 4 all run on. Filterable by `code`, time range, `customer`, `lot`, `sw_version`, `ward`, `hub_id`. Cursor-paginated. `lot` resolves through the Patch Lot Allocation sheet, since a hub does not know which patch lot it is reading.

### `GET /v1/metrics/indicators`

**Deterministic.** No model runs behind this endpoint. Returns, per indicator × cohort:

```json
{
  "indicator_id": "IND-04",
  "internal_code": "ALERT-FALSE",
  "cohort": {"kind": "sw_version", "value": "1.1.0"},
  "window": {"start": "2026-06-15", "end": "2026-09-13", "days": 90},
  "event_count": 14,
  "denominator": {"basis": "unit_months_in_service", "value": 0.98, "unit": "per 100 unit-months",
                  "hubs_counted": 36, "is_estimate": false},
  "observed_rate": 14.28,
  "baseline": 1.1,
  "threshold": {"kind": "ratio", "multiplier": 2.0, "value": 2.2},
  "ratio": 12.98,
  "breached": true,
  "event_ids": ["EVT-...", "..."],
  "rule_version": "PMS-PLAN-001-v3.0"
}
```

`event_ids` is not optional. A rate that cannot be opened up into the events behind it is a number nobody can check, and Workflow 3 needs them to write the signal.

Denominator formulas are in [`REGISTERS.md` §2](REGISTERS.md#2-denominators). This endpoint is their only implementation — the dashboard, the agent and the webhook all read the same computation.

### `POST /v1/webhooks/threshold`

Outbound. Fires at the agent when `breached` flips false → true for an indicator × cohort, and once per period thereafter while it stays breached (no re-firing on every nightly run).

```json
{
  "event": "threshold.breached",
  "indicator_id": "IND-04",
  "cohort": {"kind": "sw_version", "value": "1.1.0"},
  "ratio": 12.98,
  "metrics_url": "/v1/metrics/indicators?indicator=IND-04&cohort=sw_version:1.1.0",
  "fired_at": "2026-09-13T02:14:00Z"
}
```

Signed with an HMAC header. The agent verifies, fetches the full metric, and runs Workflow 3. **The webhook carries no rationale and no recommendation** — it is a trigger, not an opinion.

---

## 2. Event codes

Seven codes plus a heartbeat. They are the indicator internal codes, unchanged.

| Code | Indicator | Emitted when | Payload |
|---|---|---|---|
| `CONN-LINK-LOSS` | IND-01 | Patch-to-hub link drops during an active session | `{duration_s, rssi_at_loss, pairing_id, patch_lot?}` |
| `HUB-OFFLINE` | IND-02 | Cloud detects no heartbeat past the offline threshold | `{last_seen, offline_duration_h, ward_wide}` |
| `BATT` | IND-03 | Battery capacity or discharge rate outside spec | `{capacity_pct_nominal, cycles, on_dock}` |
| `ALERT-FALSE` | IND-04 | An alert is raised and then dismissed/silenced as inappropriate | `{alert_type, threshold_profile, dismissed_by_role, ward_profile_applied}` |
| `ADHESIVE` | IND-05 | Signal-loss pattern consistent with patch detachment | `{patch_lot, wear_time_h, pairing_id}` |
| `SKIN` | IND-06 | *Never emitted by a device.* Clinical observation only. | — |
| `DISPLAY` | IND-07 | Display or power-on self-test fault | `{fault, post_code}` |
| `HEARTBEAT` | — | Every N minutes | `{battery_pct, sw_version, pairing_status}` |

Two consequences worth stating plainly:

- **`SKIN` has no telemetry path.** A patch cannot detect a rash. IND-06 is populated entirely from the troubleshooting log, RMAs and client emails — which is why its threshold is "any increase, clinical review" rather than a multiplier. One indicator is deliberately human-only, and the product should not pretend otherwise.
- **`ALERT-FALSE` is a judgement, even from a device.** A hub can see that an alert was silenced in four seconds; it cannot see whether the alert was wrong. The payload's `ward_profile_applied` flag is the honest part — it is the field that makes the planted 1.1.0 story findable, because the defaulting profile is a fact the device knows.

`HUB-OFFLINE` is generated cloud-side, not by the hub. A unit that is offline cannot report that it is offline.

---

## 3. Data model

```text
hub              seeded from PulseOne Hub Inventory, kept live by heartbeats
  hub_id · serial · customer_id · ward_id · bed_id · hw_revision
  sw_version · install_date · unit_status · pairing_id · last_seen · battery_pct

telemetry_event  append-only, never updated
  event_id · hub_id · ts_device · ts_received · code · severity · sw_version
  payload · source (device | backfill) · dedupe_key

indicator_rule   loaded from the Indicators & Thresholds sheet
  indicator_id · product · code · denominator_basis · baseline
  threshold_kind · threshold_value · window_days · review_function · source_document

metric_snapshot  computed, one row per indicator × cohort × run
  ... the GET /v1/metrics/indicators payload, stored so a rate stays explainable later
```

`telemetry_event` is append-only. A wrong event stays in the table; corrections are new rows.

---

## 4. Backfill

The fleet has twenty months of register history in spreadsheets — rows from 2025-01-01, installs from 2024-09-15 — and no history in the event table. Backfill makes the two agree well enough to compute a trailing-12-month baseline.

**Order:**

1. **Hubs** from `PulseOne Hub Inventory` — 250 rows, all fields. This also establishes the denominator, since every hub's `Install Date` and `Unit Status` are here. Two of the six `Unit Status` values (`Spare`, `Shipped - not installed`) do not accrue, and a hub that does not accrue must never contribute to a numerator either.
2. **Real events** from the existing registers, in this precedence: incident log rows with a usable `Event Code` → RMA rows whose technician findings map to a code → troubleshooting rows whose free-text columns map to a code → client communications typed as complaints. Each backfilled event carries `source: backfill` and the source row ID it came from.
3. **Synthetic filler** — routine heartbeats and a baseline rate of ordinary events, generated per hub over its in-service period, calibrated so that the trailing-12-month rate lands near the baselines the PMS plan already states (1.3, 0.9, 0.6, 1.1, 0.4, 0.12, 0.8). This is the only place the dataset is fitted to a number, and it is fitted to a number the customer's own controlled document already committed to.
4. **The planted rise** is *not* generated here. It lives in the source registers and comes through step 2, so it is discoverable by joining sources rather than by reading one.

**Rules:**

- Backfilled events keep their original timestamps. Nothing is stamped "now".
- `source: backfill` is visible in every API response. A rate computed mostly from backfill should say so.
- Backfill is idempotent and re-runnable from the frozen register set.

**Live streaming.** During the demo a generator posts real events at an accelerated clock so the fleet visibly moves, a threshold visibly crosses, and the webhook visibly fires. The accelerated clock is a demo setting, not a second code path.

---

## 5. The stream as tier 1's source

Before the reframe this API had one consumer: the indicator engine, counting events against a denominator. It now has two, and the second one is the reason the first can be trusted.

**Outage watch reads this stream and drafts incident rows.** It is tier 1's first and strongest capture bot ([`CAPTURE-AGENTS.md` §1](CAPTURE-AGENTS.md#1-outage-watch)), and the artifact it reads is specified as a file in [`UPSTREAM-SOURCES.md` §1](UPSTREAM-SOURCES.md#1-telemetry-stream) — `sources/telemetry/events.ndjson` is exactly what `POST /v1/telemetry/events` would have written.

Three things the stream knows that the incident log does not:

**The events nobody logged.** 369 indicator events happened; 307 reached the incident log. Of the 62 that did not, **44 are hub codes this stream carries outright** — `CONN-LINK-LOSS`, `HUB-OFFLINE`, `BATT`, `ALERT-FALSE`, `DISPLAY`. Those 44 rows do not exist in the customer's register and can be drafted from the stream alone. That is the single clearest thing the product does.

**The version at the moment of the fault.** `sw_version` on the event is authoritative, present on every event, and reported by the hub as it happened. `SW Version at Time` is blank on 35% of incident rows, and — the part that matters — on thirteen of the fifteen rows in the primary story. The register's own `SW Version (last observed)` is a last-observed value with a stale date; the heartbeat stream turns that column into a timeline.

**The episode, not the flap.** A hub that goes offline eleven times in six days is one incident, and `dedupe_key` plus the `ward_wide` flag is how outage watch groups a burst into an episode and carries the site-wide co-occurrence into the drafted `Notes`. A bot that turns a hospital network cutover into ten separate incident rows has made the register worse, not better — and the near-miss story is exactly that shape.

Two constraints on what this bot may draft, both of them already true of the stream and restated here because they are the boundary between capture and invention:

- **`SKIN` is never emitted** (§2). A patch cannot detect a rash. Zero `SKIN` rows may ever carry `Source = Telemetry`; if outage watch produces one, it has invented an event, and that is a failing test rather than a rough edge.
- **`ADHESIVE` is inferential.** The stream does carry it, but as a signal-loss pattern *consistent with* detachment — an inference, not an observation. Outage watch may draft `CONN-LINK-LOSS`, `HUB-OFFLINE`, `BATT`, `ALERT-FALSE` and `DISPLAY` as confident rows; it may only raise `ADHESIVE` as a **low-confidence question** for a human to confirm against the ward, never as a committed classification. Fifteen of the 62 unlogged events are `ADHESIVE`, and the honest answer on all fifteen is a question.

Everything else about this API is unchanged. It is still read-only to the agent, still deterministic behind `/v1/metrics/indicators`, and still carries no authority over the fleet roster — and **no capture agent writes to it**. Outage watch reads events and drafts register rows; it does not post events.

---

## 6. AWS mapping

| Component | Service | Why |
|---|---|---|
| Device ingest | **IoT Core** (MQTT) → rules engine | What device fleets actually use. Per-device certs, no per-hub credentials in the cloud. |
| HTTP ingest and reads | **API Gateway** + **Lambda** | Six endpoints, spiky traffic, no servers. |
| Event store | **Timestream** (events) or **DynamoDB** (`hub_id` partition, `ts` sort) | Append-only time series with a device partition key. DynamoDB is the hackathon answer; Timestream is the right one. |
| Fleet state | **DynamoDB** | One item per hub, updated by heartbeat. |
| Register set | **S3** (the eleven workbooks, frozen and versioned) | Immutable sources with object versioning. |
| Upstream artifacts | **S3** (`sources/` — mail, transcripts, work orders, rounds) | Tier 1's input. Same immutability rule, and the same reason: a drafted row has to be walkable back to the artifact it came from. |
| Nightly Measure run | **EventBridge Scheduler** → Lambda | Cron with a queryable history. |
| Threshold webhook | **EventBridge** custom bus → **SNS** / HTTPS target | The agent is one subscriber; the dashboard can be another. |
| Metric snapshots | **DynamoDB** or **Aurora Serverless** | Small, queried by cohort. |
| Agent invocation | **Lambda** (or **Step Functions** for WF 4–5) | Investigate and Record are multi-step with a human gate — Step Functions' wait-for-callback is exactly that shape. |
| Secrets, HMAC keys | **Secrets Manager** | |
| Audit | **CloudWatch Logs** + the Agent Action Log table | The action log is the product's audit trail; CloudWatch is the platform's. |

For 48 hours: API Gateway + Lambda + DynamoDB + EventBridge covers all six endpoints and the webhook. IoT Core and Timestream are the production answer and worth naming in the pitch; neither is needed to demo.

---

## 7. What this API is not

- **Not clinical.** It carries no patient identity, no waveforms, no vital-sign values. Ward and bed, never who is in it.
- **Not a control plane.** Nothing here writes to a device. No remote configuration, no firmware push.
- **Not the source of truth for the fleet roster.** The hub inventory sheet is. Telemetry updates state; it does not create or retire units.
- **Not an alarm system.** Ward alerts are the clinical dashboard's job and always will be. This is surveillance over months, not seconds.
