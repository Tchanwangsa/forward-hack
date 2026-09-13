# Registers and schema

**What this is.** The eleven tables the product reads and writes, the indicator rule set that is the engine, and how the two denominators are computed. Supersedes `archive/REGISTER-SHAPES-V0.md`, which described nine tables and a product where the registers were only input.

Companions: [`ARCHITECTURE.md`](ARCHITECTURE.md) (the three tiers), [`CAPTURE-AGENTS.md`](CAPTURE-AGENTS.md) (who drafts into what), [`WORKFLOW.md`](WORKFLOW.md) (why this shape is legitimate), [`DIAGRAMS.md`](DIAGRAMS.md) (tier 2's five workflows, referenced below as WF 1–5), [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md) (the artifacts behind the rows), [`MOCK-DATA.md`](MOCK-DATA.md) (how the data is generated).

---

## The map

Tables are grouped by **who writes the rows**, because that is what the three-tier reframe changed.

```text
RAW SOURCES              CAPTURE-FED REGISTERS           ANALYSIS OUTPUT
upstream artifacts       human-kept, tier-1 drafted      system-maintained

telemetry stream ──► Incident & Outage Log ──┐
mailboxes ─────────► Client Comms Log ───────┤        ┌── Signal Register
        └──────────► Complaint Register ─────┤        │   what breached and why
transcripts ───────► Client Comms Log        ├─ T2 ──►├── Product NC Register
service system ────► Returns & Replacements ─┤        │   signed by a human
ward rounds ───────► Data Check & T'shooting ┘        ├── CAPA Register ◄── T3
                                                      │   recurrence, opened by a human
REFERENCE                                             └── Agent Action Log
Customer Orgs & Hubs   ── denominators, resolution        every action, every verdict
PMS Plan & Report      ── the approved indicator rule set
```

| # | Register | Class | Writes |
|---|---|---|---|
| 1 | `PM-Customer-Organisations-and-Hubs-Record.xlsx` | Reference | Human (the system of record) |
| 2 | `PM-Incident-and-Outage-Log.xlsx` | Capture-fed | Human + **outage watch** |
| 3 | `Product-Return-and-Replacement-Register.xlsx` | Capture-fed | Human + **RMA capture** |
| 4 | `PM-Data-Check-and-Troubleshooting-Log.xlsx` | Capture-fed | Human + **field-check nudge** |
| 5 | `PM-Client-Communications-Log.xlsx` | Capture-fed | Human + **inbox triage**, **meeting scribe** |
| 6 | `Complaint-Register.xlsx` | Capture-fed | **NEW.** Human decides, **inbox triage** recommends |
| 7 | `PMS-Plan-and-Report-Register.xlsx` | Reference | Human (controlled documents) |
| 8 | `Signal-Register.xlsx` | System-maintained | Tier 2, WF 3–4 |
| 9 | `Product-NC-Register.xlsx` | System-maintained | Tier 2, WF 5, human signs |
| 10 | `CAPA-Register.xlsx` | System-maintained | **NEW.** Tier 3 recommends, human opens |
| 11 | `Agent-Action-Log.xlsx` | System-maintained | Every tier |

---

## Storage and ownership

**Postgres is the application's system of record.** It stores the capture queue, proposed completions, signals, Product NC drafts, CAPA recommendations, human decisions, provenance and the append-only action log. The application writes through narrow, validated workflow operations; the model does not receive unrestricted database credentials or arbitrary SQL access.

The customer-controlled reference and capture-fed spreadsheets remain authoritative for the human source records during the pilot. They are imported into versioned Postgres snapshots, and the analysis reads a completed database view that combines each untouched source row with accepted capture-layer additions and completions.

In the pilot those spreadsheets are seven live Google Sheets, one per workbook, reached through a service account that is invited to each file rather than holding blanket access. Access is therefore per register: the agent can hold the Incident log without the Complaint register. See [`SHEETS.md`](SHEETS.md).

The `.xlsx` names for the four system-maintained registers describe controlled exports and the deterministic demo fixtures, **not four live files that the agent edits directly**. Each export carries an as-at timestamp and database snapshot/version so it can be reproduced.

SQLite is acceptable for an isolated developer demo, but it is not the target architecture: approvals, background workers, multiple users and concurrent workflow writes make Postgres the safer default.

Ownership still belongs to people. **System-maintained** means the workflow creates and updates the operational record; it does not mean the model is accountable for the decision. Human gates remain mandatory wherever the table says a person decides, signs, opens, approves or closes.

---

## 1. The indicator rule set

Seven rows, from the `Indicators & Thresholds` sheet of `PMS-Plan-and-Report-Register.xlsx`. A machine-readable rule set that a named human approved in a controlled document before any of the data existed. Everything tier 2 does hangs off it. Unchanged by the reframe.

| ID | Product | Description | Internal Code | Denominator | Baseline (trailing 12mo) | Escalation Threshold | Review Function | Source Document |
|---|---|---|---|---|---:|---|---|---|
| IND-01 | PulseOne | Loss of wireless communication between sensor and receiver | `CONN-LINK-LOSS` | per 100 unit-months in service | 1.3 | 2.0x baseline | Quality | PMS-PLAN-001 v3.0 |
| IND-02 | PulseOne | Unit not reporting to clinical dashboard | `HUB-OFFLINE` | per 100 unit-months in service | 0.9 | 2.5x baseline | Quality | PMS-PLAN-001 v3.0 |
| IND-03 | PulseOne | Battery performance below specification | `BATT` | per 100 unit-months in service | 0.6 | 2.0x baseline | Quality | PMS-PLAN-001 v3.0 |
| IND-04 | PulseOne | False or inappropriate alert | `ALERT-FALSE` | per 100 unit-months in service | 1.1 | 2.0x baseline | Clinical | PMS-PLAN-001 v3.0 |
| IND-05 | PulsePatch | Adhesive failure / patch detachment | `ADHESIVE` | per 1,000 patches distributed | 0.4 | 2.0x baseline | Quality | PMS-PLAN-002 v2.0 |
| IND-06 | PulsePatch | Skin reaction at application site | `SKIN` | per 1,000 patches distributed | 0.12 | Any increase — clinical review | Clinical | PMS-PLAN-002 v2.0 |
| IND-07 | PulseOne | Display or physical damage | `DISPLAY` | per 100 unit-months in service | 0.8 | 3.0x baseline | Service | PMS-PLAN-001 v3.0 |

Comparison window for all seven: **rolling 90 days vs trailing 12 months.** As at 2026-09-13 that is 2026-06-15 → 2026-09-13 against 2025-09-13 → 2026-09-13.

Three properties make this the engine rather than a lookup table:

1. **The threshold was committed in advance.** The 2.0x was not chosen after seeing the data. That is the difference between a signal and a story.
2. **The internal codes are the telemetry event codes.** A hub emits `CONN-LINK-LOSS`; that string *is* IND-01. Telemetry lands pre-classified and the human-authored sources do not — which is the entire reason tier 1 exists.
3. **IND-06 has no multiplier.** "Any increase — clinical review" is not a number, so the rule engine must carry a threshold *kind*, not just a value.

### Threshold evaluation

| Threshold kind | Written as | Breach test |
|---|---|---|
| `ratio` | `2.0x baseline`, `2.5x baseline`, `3.0x baseline` | `observed_90d_rate >= multiplier × baseline` |
| `any_increase` | `Any increase - clinical review` | `observed_90d_rate > baseline`, routed to Clinical regardless of magnitude |

`Review Function` (Quality / Clinical / Service) decides who the signal is assigned to, not whether it is raised.

---

## 2. Denominators

Both come from `PM-Customer-Organisations-and-Hubs-Record.xlsx`, which is why that file matters more than the other six. Neither is ever entered by hand, and **no capture agent may write to either sheet** — a bot that can move the denominator can move every rate in the product.

### 2.1 Unit-months in service — IND-01, 02, 03, 04, 07

From the `PulseOne Hub Inventory` sheet, 250 rows.

```text
for each hub in cohort:
    start = max(Install Date, window_start)
    end   = min(accrual_end, window_end)        # accrual_end per the table below
    contribution = max(0, days(end - start)) / 30.44

denominator = sum(contributions) / 100        # "per 100 unit-months"
rate        = event_count / denominator
```

`Unit Status` governs inclusion. Six values, and **two of them mean the same thing**:

| Unit Status | Rows | Accrues? | `accrual_end` |
|---|---:|:---:|---|
| `In service` | 202 | yes | window end |
| `Installed` | 19 | yes | window end — same state, different data-entry habit. Treating these as two states is a denominator bug. |
| `At depot (RMA)` | 6 | yes | the day it went to the depot |
| `Decommissioned` | 8 | yes | its decommission date |
| `Spare` | 9 | **no** | — sitting in a cupboard |
| `Shipped - not installed` | 6 | **no** | — not on a patient yet |

The sheet has **no decommission-date and no depot-date column**, because the real one has neither. Both are inferred — from the RMA register's `Date Received`, or failing that `Last Online (local)` — and the inference is recorded, not hidden. Ground truth carries the true values in `hubs.csv` (`decommission_date`, `depot_from`, `accrual_end`) so the denominator can be recomputed exactly.

As at 2026-09-13: **2,504.2** unit-months trailing 12 months, **650.3** rolling 90 days.

### 2.2 Patches distributed — IND-05, IND-06

From the `PulsePatch Stock Allocation` sheet, 275 allocation rows. The grain is lot × customer — one lot fans out to several customers.

```text
denominator = sum(Patches Allocated where Shipped Date in window, for cohort) / 1000
```

Distribution, not consumption. Asteria ships boxes; it does not know when a patch is applied. The denominator is therefore an estimate and is labelled as one. A row with a blank `Shipped Date` is allocated but not shipped and does not count.

As at 2026-09-13: **110,125** patches trailing 12 months, **41,938** rolling 90 days.

### 2.3 Cohorts

The same rate is computed at every level that has a plausible common cause. A signal names the tightest cohort that still breaches.

| Cohort | Key | Source of the key |
|---|---|---|
| Fleet | `all` | — |
| Software version | `1.0.0` (69) · `1.0.2` (112) · `1.1.0` (36) · `1.1.1` (33) | `SW Version (last observed)`, or `SW Version at Time` on the incident row when present — **and after tier 1, the telemetry event's own version, which is the only one that is reliably right** |
| Hardware revision | `H1` (125) · `H2` (89) · `H2.1` (36) | Hub Inventory. The plan says H1/H2; the data also contains H2.1. The data wins. |
| Customer organisation | `CUST-0012` … | Hub Inventory / Lot Allocation |
| Ward | `WARD-3B` … | Hub Inventory `WardID` |
| Patch lot | `L-2604-B19` … | Lot Allocation |

Cohort denominators use the same formulas over the subset. A cohort below a configured minimum of unit-months or patches is reported with its rate suppressed — a 3.0x ratio over 4 unit-months is arithmetic, not a signal.

---

## 3. Capture-fed registers

**Column names, column order and the mess are preserved exactly** — the abbreviation sloppiness, the blank cells, the two date formats, the organisation-name variants. That is the problem the product solves; tidying it deletes the product.

### 3.0 The two capture columns

Every capture-fed register gains the same two columns, appended after the existing ones so the original order is untouched:

| Column | Values | Why |
|---|---|---|
| `Row Origin` | `Human` · `Agent (accepted)` · `Agent (edited)` | Whether a human typed this row or a capture bot drafted it and somebody confirmed. A row is never `Agent (pending)` in the register — a pending draft lives in the capture queue, not here. |
| `Captured From` | `tel:TEL-2026-0084210` · `eml:<msgid>` · `tx:TX-2026-0187@00:14:02-00:14:28` · `wo:WO-21412` · `round:RD-2026-0412` | The artifact. Resolvable, or it is a bug. Blank on human rows. |

**Completions are not in these columns.** When a bot proposes a value for a blank cell on an existing human row, the source row is not touched — the proposal lives in the capture layer with its evidence, and downstream analysis reads the completed view. See §6.

### 3.1 `PM-Customer-Organisations-and-Hubs-Record.xlsx` — 3 sheets, reference only

**`Organisations`** (16 rows, 18 cols)
`CustomerID · Organisation Name · Legal Entity Name · Location · State · Country/Region · Status · Timezone · Record ID · Customer Since · PulseOne Units (total) · PulseOne Units (in service) · Wards · Primary Contact · Primary Contact Email · Channel · Account Owner · Notes`

AU / NZ / UK / NO. `Status` carries `Active`, `Active (Distributor)`, `Evaluation`, `Onboarding`, `Inactive`. The unit counts here are a stale human summary and will disagree with a count of the inventory sheet — **the inventory sheet is authoritative**.

*(Note: this sheet's `Channel` column is the sales channel. The comms log's new `Channel` column in §3.5 is the communication medium. Same word, different meaning, both from the real files.)*

**`PulseOne Hub Inventory`** (250 rows, 15 cols) — *the most important sheet in the product*
`HubID · Serial Number · CustomerID · Organisation · WardID · BedID · HW Revision · SW Version (last observed) · SW Version Observed On · Install Date · Unit Status · Pairing ID · Pairing Status · Last Online (local) · Notes`

`SW Version Observed On` is what makes the SW-version cohort honest: a version is a last-observed value with a date, not a fact. Some of those dates are stale by months, and one or two are a year in the future because somebody typed the wrong year. Tier 1's telemetry heartbeats are what turn this column into a timeline.

**`PulsePatch Stock Allocation`** (275 rows, 10 cols)
`Lot Code · Product Code · Manufactured · Expiry · CustomerID · Organisation · Patches Allocated · Boxes · Shipped Date · Notes`

### 3.2 `PM-Incident-and-Outage-Log.xlsx` — 737 rows, 20 + 2 cols

`Incident/Outage ID · Pairing ID · Pairing Status · Organisation · HubID · Serial Number · WardID · BedID · Last Online · Offline Duration (hrs) · Reported Date · Incident Description · Status · Date of Last Email Sent · Reported By · Assigned To · SW Version at Time · Notes · Event Code · Source`

Plus `Row Origin` · `Captured From`.

| Column | Values | Why |
|---|---|---|
| `Event Code` | one of the seven internal codes, **blank on 27% and wrong on 9% of human-entered indicator rows** | The join to the indicator set. Telemetry fills it correctly; ward staff do not fill it at all. |
| `Source` | `Telemetry` · `Dashboard alert` · `Ward staff` · `Email` | How much to trust `Event Code` |

307 of the 737 rows carry an indicator; 430 are logistics, site network, user error and duplicates. **62 indicator events that actually happened have no row here at all.** That set is [outage watch](CAPTURE-AGENTS.md#1-outage-watch)'s headline.

`SW Version at Time` is blank on 35% of rows, and — the part that matters — on 13 of the 15 rows in the primary story. `Last Online` is a snapshot copied from the inventory rather than the time of the incident: a column that looks event-related and is not.

### 3.3 `Product-Return-and-Replacement-Register.xlsx` — 308 rows, 20 + 2 cols

`RMA Number · Date Raised · Organisation · CustomerID · Product · Serial Number · HW Rev · SW Version · Customer Reported Fault · Date Received · Technician Findings · Component Replaced · Linked Complaint · Disposition · Replacement Serial · Date Closed · Technician · Warranty Status · Notes · Linked Signal`

Plus `Row Origin` · `Captured From`.

The register's whole value is the gap between `Customer Reported Fault` and `Technician Findings`. *"Unit alarming for no reason"* against *"Configuration reset to ward profile, no hardware fault"* is an `ALERT-FALSE` event and an explanation in the same row. `Serial Number` appears as `PO-P1-004226`, `SN 4216`, `P1100-4563`, and with trailing whitespace.

`SW Version` is blank on 48% and recoverable from the hub inventory as at `Date Raised` — a completion that is a *join*, not a transcription. `Linked Complaint` is blank on 83% and now has a register to point at (§3.6).

### 3.4 `PM-Data-Check-and-Troubleshooting-Log.xlsx` — 712 rows, 15 + 2 cols

`Check ID · Date · Organisation · Ward · Bed · PulseOne-PulsePatch Pairing · Serial Number · Patch Lot · Hardware Issues · Alert Misclassifications · Patient & Alert Issues · Software Issues · Issue Found · Checked By · Action Taken`

Plus `Row Origin` · `Captured From`.

Four free-text issue columns, mostly blank, mapping *imperfectly* onto the seven indicators. The hardest classification job in the dataset.

| Column | Typical content | Usually maps to |
|---|---|---|
| `Hardware Issues` | "Battery below spec on load test", "Comms module suspect", "Patch edge lift observed" | IND-03, IND-01, IND-05 |
| `Alert Misclassifications` | "Bed exit flagged, patient in bed", "Movement classified as exit on turn" | IND-04 |
| `Patient & Alert Issues` | "6x false RR alert overnight", "Patch fell off, reapplied", "Skin prep may be a factor" | IND-04, IND-05, IND-06 |
| `Software Issues` | "E-207 / E-211 pair", "1.1.0 alert logic", "Threshold set to default not ward profile" | IND-01, IND-04 |

The mapping is deliberately imperfect: an adhesive finding sits in `Hardware Issues`, a battery finding sometimes sits in `Software Issues` as "Charge state reporting wrong", and one row can carry two indicators. `Serial Number` is blank on 26% and is sometimes the bare `4111`; `Patch Lot` is blank on 51%; `Action Taken` on 66%.

### 3.5 `PM-Client-Communications-Log.xlsx` — 566 rows, 15 + 3 cols

`Comm ID · Email Subject · Date of Initial Email · Date of Last Email Sent · Status · Type · Organisation · Client Contact · Contact Role · Contact Email · Handled By · Mailbox · Notes · Attachments · Cross-reference`

Plus **`Channel`** · `Row Origin` · `Captured From`.

| Added column | Values | Why |
|---|---|---|
| `Channel` | `Email` · `Meeting` · `Phone` · `Portal` | ISO 13485 §8.2.1 is **one** feedback net. A concern raised in a Tuesday site visit and the same concern emailed on Wednesday are the same feedback; splitting them into two registers means tier 2 has to re-join them to see it. One register, one column, and the analysis reads across channels for free. |

This is why there is no standalone Client Feedback Log. It is a live decision, not a settled one — if a separate register is wanted it is one column and one file, not a re-architecture.

`Email Subject` stays named that on a `Channel = Meeting` row, holding the meeting title. The column is misnamed for meetings and stays misnamed, because the real file is. `Mailbox` and `Attachments` are blank on meeting rows.

`Type` is `Technical query · Complaint · Service request · Training request · Escalation · Feedback · General enquiry · Order / stock` — human-assigned and unreliable. **`Type = Complaint` here is a casual label, not a complaint record.** The formal object is §3.6. `Notes` is where the signal actually is ("NUM reports patch to receiver dropping out ~3x per night"). `Cross-reference` is free text — `See RMA`, `Logged in incident log`, `Raised at PMS review`, `Linked to CMP-0200` — an unreliable join the agent should use as a hint, never as a key.

### 3.6 `Complaint-Register.xlsx` — **NEW**

One row per formal complaint. Recommended by [inbox triage](CAPTURE-AGENTS.md#2-inbox-triage), **classified by a human**, and it has a lifecycle of its own.

**Why it is its own register and not a comms-log row.** A complaint under ISO 13485 §8.2.2 is a record with an owner, an investigation decision, a closure rationale and a vigilance screen. A comms-log row is a note about a conversation. Conflating them is how complaint registers end up simultaneously over-populated (every grumpy email) and under-populated (the real ones logged as `Technical query`). It is also product- and externally-sourced, so it survives the PMS-only scope cut cleanly.

| Field | Notes |
|---|---|
| `Complaint ID` | `CMP-2026-0041` |
| `Date Received` · `Date Opened` | received is the customer's clock; opened is ours, and the gap is a metric |
| `Channel` | `Email` · `Meeting` · `Phone` · `Portal` — same vocabulary as the comms log |
| `Organisation` · `CustomerID` | resolved |
| `Complainant` · `Contact Role` · `Contact Email` | |
| `Product` | PulseOne / PulsePatch |
| `Serial Number` · `Patch Lot` | as reported, and resolved |
| `Complaint Description (as reported)` | **the customer's words, never the agent's paraphrase** |
| `Indicator` · `Event Code` | agent-proposed, at a confidence; human confirms |
| `Investigation Required (Y/N)` · `Investigation Summary` | human |
| `Vigilance screen required (Y/N)` | **human-only. The agent never fills this field.** Vigilance is out of scope ([`ARCHITECTURE.md`](ARCHITECTURE.md)); the field exists to mark the boundary rather than hide it. |
| `Linked Comm` · `Linked Incident` · `Linked RMA` | → §3.5, §3.2, §3.3 |
| `Linked Signal` · `Linked NC` | → §4.1, §4.2, when tier 2 picks it up |
| `Status` | `Open · Under investigation · Closed · Declined` |
| `Owner` | named person |
| `Date Closed` · `Closure Rationale` | mandatory on any terminal status |
| `Customer Informed (Y/N)` · `Date Informed` | the outbound communication is itself a human gate |
| `Row Origin` · `Captured From` | as §3.0 |

**`Declined` is a first-class status with a rationale.** A recommendation the human rejected is a record that the screen happened, exactly as `Closed - no action` is on a signal. A complaint register with no declined rows is a register nobody is actually screening.

### 3.7 `PMS-Plan-and-Report-Register.xlsx` — 3 sheets, reference only

**`PMS Documents`** (24 rows, 10 cols)
`Document ID · Title · Type · Version · Status · Approved Date · Next Review Due · Owner · Frequency · Notes`

Holds the plans the indicators cite (PMS-PLAN-001 v3.0 approved 2026-02-12, PMS-PLAN-002 v2.0), the half-yearly reports WF 5 writes into, and the monthly trend working files — one of which is `Overdue`, noted *"Data pending from service team"*. That overdue row is the product's business case sitting in the customer's own spreadsheet.

**`Indicators & Thresholds`** (7 rows, 10 cols) — §1 above.

**`PMS Review Meetings`** (22 rows, 9 cols)
`Meeting ID · Date · Meeting Type · Attendees · Chair · Minutes Status · Items Reviewed · Actions Raised · Notes`

Where a signal goes to be discussed, and — after tier 1 — where a transcript exists for each row. The Signal Register's `Raised at PMS meeting` points here; tier 3 reads the minutes for its recurrence argument.

---

## 4. System-maintained registers

### 4.1 Signal Register — 18 rows of history

One row per breach or cluster tier 2 raises. Written by WF 3, updated by WF 4.

| Field | Notes |
|---|---|
| `Signal ID` | `SIG-2026-0014` |
| `Raised` | timestamp, automatic |
| `Indicator` · `Product` | |
| `Cohort` | `all · lot · sw_version · site · ward · hw_revision` |
| `Cohort value` | `1.1.0` |
| `Observed rate` · `Baseline` · `Threshold` · `Ratio` | all computed, all reproducible |
| `Window start` · `Window end` | the rolling 90 days actually used |
| `Event count` · `Denominator value` | numerator and denominator, shown so the rate can be checked |
| `Linked events` | every incident / RMA / check / comm / complaint ID that contributed |
| `Capture-dependent (Y/N)` | **new.** Whether this signal is visible without tier 1's drafted rows and completions. On the primary story this is `Y`, and it is the most persuasive single cell in the product. |
| `Agent rationale` | what it thinks, including the innocent explanation it considered |
| `Status` | `Open · Monitoring · Promoted · Closed - no action` |
| `Reviewed By` · `Review date` · `Outcome rationale` | the human gate, mandatory on any terminal status |
| `Linked NC` | set when promoted |
| `Raised at PMS meeting` | → `PMS Review Meetings.Meeting ID` |

**`Closed - no action` is a permanent row with a rationale, never a deletion.** A signal the team correctly dismissed is evidence the surveillance is working.

### 4.2 Product NC Register — 5 rows of history

One row per confirmed product nonconformity. Drafted by WF 5, signed by a human.

| Field | Notes |
|---|---|
| `NC ID` | `NC-2026-007` |
| `Raised From` | → `Signal ID`. An NC always has a signal behind it. |
| `Date raised` · `Product` | |
| `Affected scope` | serials and lots, resolved from Hub Inventory + Lot Allocation — not a version string |
| `Units in field` | count of affected units still accruing |
| `Description` · `Indicator` | |
| `Evidence links` | source row IDs, every one |
| `Containment` | what was done, or the recorded decision that nothing was |
| `Investigation owner` · `Root cause` | human-written |
| `Disposition` | agent proposes from what the RMAs actually did; human decides |
| `CAPA considered (Y/N)` · `CAPA rationale` | **`N` requires a rationale.** A no-CAPA decision is a record. |
| `Linked CAPA` | → §4.3, set when one is opened |
| `Status` · `Approved By` · `Date closed` | |

### 4.3 `CAPA-Register.xlsx` — **NEW**

One row per CAPA. Recommended by tier 3, **opened by a human**. See [`CAPA.md`](CAPA.md) for the reasoning that produces the recommendation.

**Scope discipline.** Tier 3 recommends opening a CAPA and drafts its problem statement, its evidence, and the recurrence argument. It does **not** run the investigation, implement the action, verify effectiveness, or close it. Full CAPA execution stays out of scope; the fields below that belong to execution exist so the register is a real register, and the agent leaves them alone.

| Field | Notes | Agent |
|---|---|:---:|
| `CAPA ID` | `CAPA-2026-003` | drafts |
| `Date recommended` · `Date opened` | the gap is a metric | drafts / — |
| `Trigger` | `Recurrence · Cross-register convergence · Prior NC ineffective · Single severe NC · External` | drafts |
| `Raised From` | the NCs, signals and complaints behind it — **a CAPA usually has several** | drafts |
| `Problem statement` | agent drafts, human owns. What is actually wrong, in one paragraph, with the numbers. | drafts |
| `Recurrence evidence` | the argument: what recurred, over what period, in which registers, and why it is one failure mode and not three | drafts |
| `Prior action` | the earlier NC, containment or CAPA that was supposed to have fixed this, and what it did | drafts |
| `Why prior action did not hold` | agent proposes, human confirms — **the sharpest field in the register** | drafts |
| `Product` · `Affected scope` | resolved to serials and lots, as §4.2 | drafts |
| `Indicator(s)` | a CAPA may span more than one | drafts |
| `Decision` | `Opened · Declined · Deferred` | — **human** |
| `Decision rationale` | mandatory either way. `Declined` is a record. | — **human** |
| `Owner` · `Target date` | | — human |
| `Root cause` · `Corrective action` · `Preventive action` | execution | — human |
| `Effectiveness check` · `Effectiveness verified (Y/N)` · `Date closed` | execution | — human |
| `Status` | `Recommended · Open · Implemented · Verifying · Closed · Declined · Deferred` | — human |
| `Row Origin` · `Captured From` | as §3.0 | drafts |

**`Declined` and `Deferred` both require a rationale**, and both stay in the register permanently. `Why prior action did not hold` is the field that makes this register worth having: a CAPA system whose history does not record why the last fix failed will recommend the same fix again.

### 4.4 Agent Action Log — empty at demo start

Every classification, calculation, draft and email the agent produces across all three tiers is appended during the live demo. The fixture contains the header only so the run's activity is unambiguous.

`Action ID · Timestamp · Tier (1–3) · Workflow · Autonomy level · Inputs (artifact + source record IDs) · Rule/model version · Output · Human verdict (accepted / edited / rejected) · Reviewed By · Notes`

`Tier` is new, and `Workflow` now means the capture bot for tier 1 rows, WF 1–5 for tier 2, and the sweep for tier 3.

Three things it buys:

- **Provenance, cheaply.** Any agent-written value traces to the rows and artifacts behind it by following `Inputs`. There is no separate claim/binding layer — the log *is* the provenance layer.
- **A correction signal.** `Human verdict = edited` on a capture draft is the honest measure of whether a bot is any good, and it names how it was wrong.
- **Reproducibility.** `Rule/model version` means a rate computed in March stays explainable in September, even after the indicator table is revised.

---

## 5. What the reframe changed

For anyone holding the old nine-table picture in their head:

| | Before | Now |
|---|---|---|
| Registers | 9 | 11 — plus Complaint (§3.6) and CAPA (§4.3) |
| The comms log | one register for email | one register for **all** feedback channels, via `Channel` (§3.5) |
| Who writes the source registers | humans only | humans **and** tier-1 capture bots, marked by `Row Origin` (§3.0) |
| Provenance of a row | the Agent Action Log | the Action Log **plus** `Captured From` → a raw artifact ([`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md)) |
| The five workflows | the product | **tier 2** of three ([`DIAGRAMS.md`](DIAGRAMS.md)) |
| CAPA | out of scope entirely | **recommending** one is tier 3; executing one is still out |
| Signals | a rate and a cohort | plus `Capture-dependent (Y/N)` (§4.1) |

---

## 6. Provenance, in five rules

The old schema carried a three-layer `source_record` / `evidence_claim` / `field_binding` abstraction. It is gone. Provenance still matters, and it costs five rules instead of three tables:

1. **Source rows are never edited.** A wrong serial in the RMA register stays wrong in the RMA register. The agent's reading of it lives in the capture layer and the Action Log.
2. **A capture agent adds rows and proposes completions; it never rewrites history.** A completion is a proposed value for a blank or contradicted cell, held with its evidence outside the source row. Analysis reads the completed view; the customer's spreadsheet stays theirs.
3. **Every agent-written field names its inputs.** A drafted row names its artifact. A signal lists its linked events. An NC lists its evidence links. A CAPA names the prior action it says did not hold.
4. **Every computed number carries its inputs.** A rate is stored with its event count, its denominator value, and its window — so it can be recomputed, not just believed.
5. **Every human verdict is recorded, including the negative ones.** Capture draft rejected, complaint declined, signal closed–no action, CAPA not needed, classification edited.

That is enough to walk backwards from any CAPA to the telemetry events, emails and transcript passages behind it, which is the only thing the three-layer model was buying.

---

## 7. Out of scope

The three deep-research files in [`reference/`](reference/) stay on disk and stay correct. They cover considerably more than this product does. Unchanged by the reframe except where noted:

Vigilance, reportability and regulatory clocks — including the `Vigilance screen required` field in §3.6, which exists and is never written by the agent. Production and manufacturing NCs. MRB and disposition of nonconforming stock. Advisory notices and FSCA. **CAPA execution** — recommending is §4.3, running one is not. Audit, training, change control, supplier quality, management review. `reference-data/clock-rules/` stays on disk; nothing reads it.

**No capture agent writes to a reference register.** Not the Hub Inventory, not the Lot Allocation, not the Indicators sheet. Both denominators and the entire rule set come from those files, and an agent that can edit them can move every number in the product.
