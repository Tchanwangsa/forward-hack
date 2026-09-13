# Registers and schema

**What this is.** The nine tables the product reads and writes: six source registers modelled on real files, and three the agent owns. Plus the indicator rule set, which is the engine, and how the two denominators are computed.

Companions: [`WORKFLOW.md`](WORKFLOW.md) (why this shape is legitimate), [`DIAGRAMS.md`](DIAGRAMS.md) (the five workflows, referenced below as WF 1–5), [`TELEMETRY-API.md`](TELEMETRY-API.md) (the live event source), [`MOCK-DATA.md`](MOCK-DATA.md) (how the data is generated).

```text
SOURCE REGISTERS                          AGENT REGISTERS
six spreadsheets a real PMS team keeps    three tables the agent writes

Customer Orgs & Hubs   ──┐                ┌── Signal Register
Incident & Outage Log  ──┤                │   what breached and why
Returns & Replacements ──┼── WF 1,2 ──▶───┼── Product NC Register
Data Check & T'shooting──┤                │   signed by a human
Client Communications  ──┤                └── Agent Action Log
PMS Plan & Report      ──┘                    every action, every verdict
```

---

## 1. The indicator rule set

Seven rows, from the `Indicators & Thresholds` sheet of `PMS-Plan-and-Report-Register.xlsx`. This is a machine-readable rule set that a named human approved in a controlled document before any of the data existed. Everything the product does hangs off it.

| ID | Product | Description | Internal Code | Denominator | Baseline (trailing 12mo) | Escalation Threshold | Review Function | Source Document |
|---|---|---|---|---|---:|---|---|---|
| IND-01 | PulseOne | Loss of wireless communication between sensor and receiver | `CONN-LINK-LOSS` | per 100 unit-months in service | 1.3 | 2.0x baseline | Quality | PMS-PLAN-001 v3.0 |
| IND-02 | PulseOne | Unit not reporting to clinical dashboard | `HUB-OFFLINE` | per 100 unit-months in service | 0.9 | 2.5x baseline | Quality | PMS-PLAN-001 v3.0 |
| IND-03 | PulseOne | Battery performance below specification | `BATT` | per 100 unit-months in service | 0.6 | 2.0x baseline | Quality | PMS-PLAN-001 v3.0 |
| IND-04 | PulseOne | False or inappropriate alert | `ALERT-FALSE` | per 100 unit-months in service | 1.1 | 2.0x baseline | Clinical | PMS-PLAN-001 v3.0 |
| IND-05 | PulsePatch | Adhesive failure / patch detachment | `ADHESIVE` | per 1,000 patches distributed | 0.4 | 2.0x baseline | Quality | PMS-PLAN-002 v2.0 |
| IND-06 | PulsePatch | Skin reaction at application site | `SKIN` | per 1,000 patches distributed | 0.12 | Any increase — clinical review | Clinical | PMS-PLAN-002 v2.0 |
| IND-07 | PulseOne | Display or physical damage | `DISPLAY` | per 100 unit-months in service | 0.8 | 3.0x baseline | Service | PMS-PLAN-001 v3.0 |

Comparison window for all seven: **rolling 90 days vs trailing 12 months.**

Three properties make this the engine rather than a lookup table:

1. **The threshold was committed in advance.** The 2.0x was not chosen after seeing the data. That is the difference between a signal and a story.
2. **The internal codes are the telemetry event codes.** A hub emits `CONN-LINK-LOSS`; that string *is* IND-01. Telemetry lands pre-classified and the human-authored sources do not.
3. **IND-06 has no multiplier.** "Any increase — clinical review" is not a number, so it cannot be evaluated by the same comparison as the others. The rule engine must carry a threshold *kind*, not just a threshold value.

### Threshold evaluation

| Threshold kind | Written as | Breach test |
|---|---|---|
| `ratio` | `2.0x baseline`, `2.5x baseline`, `3.0x baseline` | `observed_90d_rate >= multiplier × baseline` |
| `any_increase` | `Any increase - clinical review` | `observed_90d_rate > baseline`, routed to the Clinical review function regardless of magnitude |

`Review Function` (Quality / Clinical / Service) decides who the signal is assigned to, not whether it is raised.

---

## 2. Denominators

Both come from `PM-Customer-Organisations-and-Hubs-Record.xlsx`, which is why that file matters more than the other five. Neither is ever entered by hand.

### 2.1 Unit-months in service — IND-01, 02, 03, 04, 07

From the `PulseOne Hub Inventory` sheet (178 rows).

```text
for each hub in cohort:
    start = max(Install Date, window_start)
    end   = min(decommission date if any, window_end)
    contribution = max(0, days(end - start)) / 30.44

denominator = sum(contributions) / 100        # "per 100 unit-months"
rate        = event_count / denominator
```

`Unit Status` governs inclusion:

| Unit Status | Count? | Note |
|---|:---:|---|
| `In service` | yes | 151 rows |
| `Installed` | yes | 7 rows — same meaning, different data-entry habit. Treating these as two states is a bug. |
| `Spare` | no | On site, not monitoring a patient |
| `Shipped - not installed` | no | |
| `At depot (RMA)` | no | Contributes up to the date it left, not after |
| `Decommissioned` | no | Contributes up to its decommission date |

Install Date is populated on every row; there is no decommission-date column, so the decommission date is inferred from the RMA register (`Date Received`) or, failing that, `Last Online (local)`. That inference is recorded, not hidden.

### 2.2 Patches distributed — IND-05, IND-06

From the `PulsePatch Stock Allocation` sheet (70 allocation rows across 22 lots).

```text
denominator = sum(Patches Allocated where Shipped Date in window, for cohort) / 1000
```

Distribution, not consumption. Asteria ships boxes; it does not know when a patch is applied. The denominator is therefore an estimate and is labelled as one. A row with a blank `Shipped Date` is allocated but not shipped and does not count.

### 2.3 Cohorts

The same rate is computed at every level that has a plausible common cause. A signal names the tightest cohort that still breaches.

| Cohort | Key | Source of the key |
|---|---|---|
| Fleet | `all` | — |
| Software version | `1.0.0 · 1.0.2 · 1.1.0 · 1.1.1` | `SW Version (last observed)`, or `SW Version at Time` on the incident row when present |
| Hardware revision | `H1 · H2 · H2.1` | Hub Inventory. The plan says H1/H2; the data also contains H2.1. The data wins. |
| Customer organisation | `CUST-0012` … | Hub Inventory / Lot Allocation |
| Ward | `WARD-3B` … | Hub Inventory `WardID` |
| Patch lot | `L-2507-B66` … | Lot Allocation |

Cohort denominators use the same formulas over the subset. A cohort with fewer than a configured minimum of unit-months or patches is reported with its rate suppressed — a 3.0x ratio over 4 unit-months is arithmetic, not a signal.

---

## 3. Source registers

Six files. **Column names, column order and the mess are preserved exactly** — the abbreviation sloppiness, the blank cells, the two date formats, the organisation-name variants. That is the problem the product solves; tidying it deletes the product.

### 3.1 `PM-Customer-Organisations-and-Hubs-Record.xlsx` — 3 sheets

**`Organisations`** (14 rows, 18 cols)
`CustomerID · Organisation Name · Legal Entity Name · Location · State · Country/Region · Status · Timezone · Record ID · Customer Since · PulseOne Units (total) · PulseOne Units (in service) · Wards · Primary Contact · Primary Contact Email · Channel · Account Owner · Notes`

AU / NZ / UK / NO. `Status` carries `Active`, `Active (Distributor)`, `Evaluation`, `Onboarding`, `Inactive`. The unit counts here are a stale human summary and will disagree with a count of the inventory sheet — the inventory sheet is authoritative.

**`PulseOne Hub Inventory`** (178 rows, 15 cols) — *the most important sheet in the product*
`HubID · Serial Number · CustomerID · Organisation · WardID · BedID · HW Revision · SW Version (last observed) · SW Version Observed On · Install Date · Unit Status · Pairing ID · Pairing Status · Last Online (local) · Notes`

`SW Version Observed On` is what makes the SW-version cohort honest: a version is a last-observed value with a date, not a fact.

**`PulsePatch Stock Allocation`** (70 rows, 10 cols)
`Lot Code · Product Code · Manufactured · Expiry · CustomerID · Organisation · Patches Allocated · Boxes · Shipped Date · Notes`

One lot fans out to several customers, so the grain is lot × customer.

### 3.2 `PM-Incident-and-Outage-Log.xlsx` — 96 rows, 18 + **2 new** cols

`Incident/Outage ID · Pairing ID · Pairing Status · Organisation · HubID · Serial Number · WardID · BedID · Last Online · Offline Duration (hrs) · Reported Date · Incident Description · Status · Date of Last Email Sent · Reported By · Assigned To · SW Version at Time · Notes`

| Added column | Values | Why |
|---|---|---|
| `Event Code` | one of the seven internal codes, **sometimes blank or wrong on human-entered rows** | The join to the indicator set. Telemetry fills it correctly; ward staff do not fill it at all. |
| `Source` | `Telemetry` · `Dashboard alert` · `Ward staff` · `Email` | How much to trust `Event Code` |

`SW Version at Time` is blank on roughly a third of rows. That gap is what WF 4's missing-data callout is for, and it is the single biggest obstacle to the SW-version cohort.

### 3.3 `Product-Return-and-Replacement-Register.xlsx` — 58 rows, 19 + **1 new** col

`RMA Number · Date Raised · Organisation · CustomerID · Product · Serial Number · HW Rev · SW Version · Customer Reported Fault · Date Received · Technician Findings · Component Replaced · Linked Complaint · Disposition · Replacement Serial · Date Closed · Technician · Warranty Status · Notes`

Added: **`Linked Signal`** — the back-link from an RMA to the signal it contributed to.

The register's whole value is the gap between `Customer Reported Fault` and `Technician Findings`. "Unit alarming for no reason" against "Configuration reset to ward profile, no hardware fault" is an `ALERT-FALSE` event and an explanation in the same row. `Serial Number` appears as `PO-P1-004226`, `SN 4216`, `P1100-4563`, and with trailing whitespace.

### 3.4 `PM-Data-Check-and-Troubleshooting-Log.xlsx` — 150 rows, 15 cols

`Check ID · Date · Organisation · Ward · Bed · PulseOne-PulsePatch Pairing · Serial Number · Patch Lot · Hardware Issues · Alert Misclassifications · Patient & Alert Issues · Software Issues · Issue Found · Checked By · Action Taken`

Four free-text issue columns, mostly blank, mapping *imperfectly* onto the seven indicators. This is the hardest classification job in the dataset and the best demonstration of WF 1.

| Column | Typical content | Usually maps to |
|---|---|---|
| `Hardware Issues` | "Battery below spec on load test", "Comms module suspect", "Patch edge lift observed" | IND-03, IND-01, IND-05 |
| `Alert Misclassifications` | "Bed exit flagged, patient in bed", "Movement classified as exit on turn" | IND-04 |
| `Patient & Alert Issues` | "6x false RR alert overnight", "Patch fell off, reapplied", "Skin prep may be a factor" | IND-04, IND-05, IND-06 |
| `Software Issues` | "E-207 / E-211 pair", "1.1.0 alert logic", "Threshold set to default not ward profile" | IND-01, IND-04 |

The mapping is deliberately imperfect: an adhesive finding sits in `Hardware Issues`, a battery finding sometimes sits in `Software Issues` as "Charge state reporting wrong", and one row can carry two indicators. `Serial Number` is blank on many rows and is sometimes the bare `4111`.

### 3.5 `PM-Client-Communications-Log.xlsx` — 128 rows, 15 cols

`Comm ID · Email Subject · Date of Initial Email · Date of Last Email Sent · Status · Type · Organisation · Client Contact · Contact Role · Contact Email · Handled By · Mailbox · Notes · Attachments · Cross-reference`

`Type` is `Technical query · Complaint · Service request · Training request · Escalation · Feedback · General enquiry · Order / stock` — human-assigned and unreliable. `Notes` is where the signal actually is ("NUM reports patch to receiver dropping out ~3x per night"). `Cross-reference` is free text: `See RMA`, `Logged in incident log`, `Raised at PMS review`, `Linked to CMP-0200` — an unreliable join the agent should use as a hint, never as a key.

### 3.6 `PMS-Plan-and-Report-Register.xlsx` — 3 sheets

**`PMS Documents`** (18 rows, 10 cols)
`Document ID · Title · Type · Version · Status · Approved Date · Next Review Due · Owner · Frequency · Notes`

Holds the plans the indicators cite (PMS-PLAN-001 v3.0, PMS-PLAN-002 v2.0), the half-yearly reports WF 5 writes into, and the monthly trend working files — one of which is `Overdue`, with the note "Data pending from service team". That overdue row is the product's business case sitting in the customer's own spreadsheet.

**`Indicators & Thresholds`** (7 rows, 10 cols) — §1 above.

**`PMS Review Meetings`** (17 rows, 9 cols)
`Meeting ID · Date · Meeting Type · Attendees · Chair · Minutes Status · Items Reviewed · Actions Raised · Notes`

Where a signal goes to be discussed. The Signal Register's `Raised at PMS meeting` points here.

---

## 4. Agent-owned registers

### 4.1 Signal Register

One row per breach or cluster the agent raises. Written by WF 3, updated by WF 4.

| Field | Notes |
|---|---|
| `Signal ID` | `SIG-2026-0014` |
| `Raised` | timestamp, automatic |
| `Indicator` | `IND-04` |
| `Product` | PulseOne / PulsePatch |
| `Cohort` | `all · lot · sw_version · site · ward · hw_revision` |
| `Cohort value` | `1.1.0` |
| `Observed rate` · `Baseline` · `Threshold` · `Ratio` | all computed, all reproducible |
| `Window start` · `Window end` | the rolling 90 days actually used |
| `Event count` · `Denominator value` | the numerator and denominator, shown so the rate can be checked |
| `Linked events` | every incident / RMA / check / comm ID that contributed |
| `Agent rationale` | what it thinks, including the innocent explanation it considered |
| `Status` | `Open · Monitoring · Promoted · Closed - no action` |
| `Reviewed By` · `Review date` · `Outcome rationale` | the human gate, mandatory on any terminal status |
| `Linked NC` | set when promoted |
| `Raised at PMS meeting` | → `PMS Review Meetings.Meeting ID` |

**`Closed - no action` is a permanent row with a rationale, never a deletion.** A signal the team correctly dismissed is evidence the surveillance is working.

### 4.2 Product NC Register

One row per confirmed product nonconformity. Drafted by WF 5, signed by a human.

| Field | Notes |
|---|---|
| `NC ID` | `NC-2026-007` |
| `Raised From` | → `Signal ID`. An NC always has a signal behind it. |
| `Date raised` · `Product` | |
| `Affected scope` | serials and lots, resolved from Hub Inventory + Lot Allocation — not a version string |
| `Units in field` | count of affected units still `In service` |
| `Description` · `Indicator` | |
| `Evidence links` | source row IDs, every one |
| `Containment` | what was done, or the recorded decision that nothing was |
| `Investigation owner` · `Root cause` | human-written |
| `Disposition` | agent proposes from what the RMAs actually did; human decides |
| `CAPA considered (Y/N)` · `CAPA rationale` | **`N` requires a rationale.** A no-CAPA decision is a record. |
| `Status` · `Approved By` · `Date closed` | |

### 4.3 Agent Action Log

Every classification, calculation, draft and email the agent produced. This is the audit trail and the demo's credibility.

`Action ID · Timestamp · Workflow (1–5) · Autonomy level · Inputs (source record IDs) · Rule/model version · Output · Human verdict (accepted / edited / rejected) · Reviewed By · Notes`

Three things it buys:

- **Provenance, cheaply.** Any agent-written value can be traced to the source rows behind it by following `Inputs`. There is no separate claim/binding layer — the log *is* the provenance layer, and one table is enough because the agent only ever writes three kinds of thing: a classification, a number, or a draft.
- **A correction signal.** `Human verdict = edited` on a classification is training data for WF 1 and the honest measure of whether the agent is any good.
- **Reproducibility.** `Rule/model version` means a rate computed in March stays explainable in September, even after the indicator table is revised.

---

## 5. Provenance, in four rules

The old schema carried a three-layer `source_record` / `evidence_claim` / `field_binding` abstraction. It is gone. Provenance still matters, and it costs four rules instead of three tables:

1. **Source rows are never edited.** A wrong serial in the RMA register stays wrong in the RMA register. The agent's reading of it lives in the Agent Action Log.
2. **Every agent-written field names its inputs.** A Signal lists its linked events; an NC lists its evidence links; an Action Log row lists its source record IDs.
3. **Every computed number carries its inputs.** A rate is stored with its event count, its denominator value, and its window — so it can be recomputed, not just believed.
4. **Every human verdict is recorded, including the negative ones.** Closed–no action, CAPA-not-needed, classification-rejected.

That is enough to walk backwards from any NC to the emails and telemetry events behind it, which is the only thing the three-layer model was buying.

---

## 6. Out of scope

The three deep-research files in [`reference/`](reference/) stay on disk and stay correct. They cover considerably more than this product now does. What is **no longer in scope**, and therefore no longer implemented:

| Reference section | Status |
|---|---|
| `REGISTER-REF-complaint-vigilance.md` §3 — vigilance / regulatory reporting register, awareness sets, 2/10/15-day and 5/30-day clocks, submission versioning, MIR fields | **Out.** No vigilance, no reportability, no clocks. |
| `REGISTER-REF-complaint-vigilance.md` §2 — full complaint register | **Mostly out.** Complaints exist as rows in the Client Communications log (`Type = Complaint`), not as a modelled register. |
| `REGISTER-REF-nc-capa-audit.md` §1 — NC register | **Narrowed.** Product NCs only. No production/manufacturing NCs, no MRB, no disposition-of-nonconforming-stock workflow, no pre-delivery fork. |
| `REGISTER-REF-nc-capa-audit.md` §2 — CAPA register | **Out.** CAPA appears only as a considered/not-considered decision with a rationale on the Product NC. |
| `REGISTER-REF-nc-capa-audit.md` §3–4 — audit findings, change control | **Out.** |
| `REGISTER-REF-document-action-pms.md` §2–5 — document, training, action, risk registers | **Out**, except the PMS Documents sheet, which is a source register in its own right. |
| `REGISTER-REF-document-action-pms.md` §6 — PMS register and the denominator problem | **In, and load-bearing.** §2 above is its narrowed implementation. |
| `reference-data/clock-rules/` | **Out.** Files stay on disk; nothing reads them. |

Nothing is deleted. Widening later is a lookup, not a re-research.
