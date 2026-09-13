# Mock data

**What this is.** How the dataset is generated: eleven tables, a telemetry event history, and the upstream artifacts those tables are transcribed *from*, for one fictional company over twenty months.

Shapes and columns are in [`REGISTERS.md`](REGISTERS.md). The artifacts are specified in [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md) — this file does not repeat that spec, it says where the artifact layer sits in the generation story. The company is [`mock/asteria.md`](mock/asteria.md). This file is about *generation behaviour* — how the data gets to be realistically imperfect, which is the part that makes or breaks the product.

## Governing principle

**Simulate the business first. Let the findings emerge from the data.**

The messiness is the product value. The registers really do say `RNH` and `Royal North Hospital`, `SN 4216` and `PO-P1-004216` and `4111`; `SW Version at Time` really is blank on a third of the incident rows. An agent that only works on clean data is worth nothing, and a dataset that is clean cannot demonstrate otherwise.

**And the register row is not the bottom of the stack.** Generate the artifact as complete truth — the telemetry event, the email thread, the transcript, the work order, the ward round — then render the register row as a lossy human transcription of it, and leave some rows untranscribed entirely. The gap between the artifact and the row is what tier 1 is worth, and it cannot be measured unless both exist.

Do not:

- Decide what the agent should find, then manufacture confirming rows in one place.
- Put a clean shared identifier in every register.
- Make every record complete and mutually consistent.
- Scatter random corruption and call it realism.
- Edit the dataset after seeing product results in order to improve the demo.

Do:

- Model ordinary operations over time — most events are boring and stay boring.
- Give each register a distinct owner, purpose, vocabulary and update habit.
- Let each register record only what its users would actually know.
- Produce omissions, delays, shorthand and disagreement that follow from *who filled the row in*.
- Treat the artifact as the complete record and the row as somebody's account of it, so every blank has a documented cause upstream.
- Freeze and version the set before evaluation.

## Layers

```text
Private world            what actually happened inside Asteria
  never an input to the product, contains no desired conclusions
        │
        ▼
Upstream artifacts       what the source systems recorded, faithfully
  telemetry events · .eml threads · transcripts · work orders · ward rounds
  complete, and strictly more informative than any row derived from them
        │
        ▼
Capture-fed registers    what five different teams wrote down about it
  partial, inconsistent, human — and sometimes not written at all
        │
        ▼
Frozen product input     the xlsx files + the event store + sources/
        │
        ▼
Independent evaluation   compare product output against the private world
```

The private world keeps the company coherent. It is never ingested. The artifact layer **is** ingested — it is tier 1's input, not answer key — which is why it has to be generated as a faithful record rather than as a set of hints. What the register row *should have said* is answer key, and lives in `ground-truth/`.

Telemetry is no longer a layer of its own. The event stream is the first of the artifacts: still backfilled from the registers and the fleet per [`TELEMETRY-API.md` §4](TELEMETRY-API.md#4-backfill), still streaming live in the demo, and now also the source outage watch reads.

One honest note about order. That diagram is the *logical* order, and the build order is the reverse: the register pack already exists, is already verified, and already carries four planted stories at measured strengths, so the artifacts are generated **to be consistent with rows that are already frozen** rather than the rows being re-derived from artifacts. Re-deriving would risk all of that to gain nothing. The only permitted movement in the register pack is additive — the two capture columns of [`REGISTERS.md`](REGISTERS.md) §3.0 and the two new workbooks. Every existing cell value, row count, indicator rate and story strength stays exactly as verified.

## What gets generated

**The registers** — as built and verified in [`mock-company-v2/`](../mock-company-v2/README.md):

| Artefact | Grain | Volume |
|---|---|---|
| `Organisations` | one per customer | 16 |
| `PulseOne Hub Inventory` | one per hub | 250 |
| `PulsePatch Stock Allocation` | lot × customer | 275 |
| `Incidents & Outages` | one per incident | 737 — of which 307 carry an indicator |
| `Returns & Replacements` | one per RMA | 308 |
| `Data Check & Troubleshooting` | one per check visit | 712 |
| `Client Communications` | one per thread, any channel | 566 |
| `Complaint Register` | one per formal complaint | **new** — small by nature, and `Declined` rows are part of it |
| `PMS Documents` · `Indicators & Thresholds` · `PMS Review Meetings` | — | 24 · 7 · 22 |

**The upstream artifacts** — specified in [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md), generated into `mock-company-v2/sources/`:

| Artefact | Grain | Read by |
|---|---|---|
| `telemetry/events.ndjson` · `heartbeats.ndjson` | one per device event; heartbeats thinned to ~1/day/hub | outage watch, and every tier-2 rate |
| `mail/{support,service,quality}/*.eml` | one per message, threaded by RFC 5322 headers | inbox triage |
| `meetings/transcripts/*.txt` | one per meeting, timestamped speaker turns | meeting scribe |
| `service/work-orders.csv` · `technician-notes.csv` · `parts-replaced.csv` | joined on `work_order_id` | RMA capture |
| `ward-rounds/rounds.ndjson` | one record per round, free-text per bed | field-check nudge |

The four agent registers (Signal, Product NC, **CAPA**, Agent Action Log) are **not generated** for the live window. The product writes them. What exists is a back-catalogue — 18 historical signals, 5 closed NCs, 316 logged actions, none of them touching a planted story — because a believable history is precedent for the agent to find, while a pre-written finding is the answer.

Period: register rows span twenty months ending at the demo date of 2026-09-13. Hub install dates precede it, from 2024-09-15.

## Source behaviours

Each register is written by different people, for a different purpose, and that is where its imperfections come from.

| Register | Owner | Purpose | Natural characteristics |
|---|---|---|---|
| **Organisations / Hub Inventory / Lot Allocation** | Operations | Know what is installed where | Summary counts (`PulseOne Units (in service)`) drift out of date against the inventory sheet. `SW Version (last observed)` is stale by design — its `Observed On` date proves it. Some `Legal Entity Name` and `Primary Contact Email` cells are simply empty. |
| **Incidents & Outages** | Support / service | Track outages to resolution | Populated by a mix of `Dashboard alert`, `Ward staff` and named staff. `SW Version at Time` blank on ~⅓ of rows because whoever logged it did not look it up. `Offline Duration (hrs)` often blank. Organisation written as whatever the logger types: `St. Auburn`, `Grampian Royal`, `Nordvik (dist)`. |
| **Returns & Replacements** | Service ops | Track units through the workshop | Technician shorthand. Serial formats vary within one column: `PO-P1-004226`, `SN 4216`, `P1100-4563`, one with trailing whitespace. `Date Received` in `26/03/2026` where the rest of the column is ISO. `Linked Complaint` mostly empty. Customer-reported fault and technician finding frequently disagree — that disagreement is the register's whole value. |
| **Data Check & Troubleshooting** | Field / clinical support | Routine on-site checks | Four free-text issue columns, mostly blank. `Issue Found` is `Y` on about half. Organisation abbreviated hardest of any register (`RNH`, `Cath Hill`, `St. Auburn`, `Northbridge`). Serial sometimes the bare `4111`. Some checks abandoned: `Action Taken = "Ward busy, check incomplete"`. |
| **Client Communications** | Support / quality mailboxes | Track threads with customers | `Type` is human-assigned and unreliable — real complaints filed as `Technical query`. The actual content is in `Notes`, truncated. `Cross-reference` is free text: `See RMA`, `Logged in incident log`, `Raised at PMS review`, occasionally a real `Linked to CMP-0200`. |
| **Complaint Register** | Quality | The formal complaint record | Written slowly and by one person, so `Date Received` and `Date Opened` are days apart and the gap is itself a metric. Under-populated relative to what the mailboxes actually contain — the real complaints that were logged as `Technical query` in the comms log are the ones that never reached it. |
| **PMS Plan & Report Register** | Quality (one person) | The controlled PMS documents | Reflects one person's workload. Reports at v0.4 `Draft`, a trend file `Overdue`, notes like *"Reviewer on leave, due date at risk"* and *"Data pending from service team"*. |

**Where the loss happens is now generated, not asserted.** Each source behaviour above is a *transcription* behaviour: the artifact holds what the source system recorded, and the register row holds what a busy person carried across from it. A ward nurse does not read a serial off the back of a hub, so the round note has the bed and the pairing and the check row has a blank — and the blank is fillable, from the artifact, by a join. A bench technician always reads the serial, so that column is clean and the `SW Version` column is not, because the workshop system never knew it. Every blank in a capture-fed register should trace to a person who would not have known, or to a step where a known fact was dropped on the way to the spreadsheet. `ground-truth/capture-targets.csv` records which of the two it was, per field, and that file is the scorecard's answer key.

## Realistic imperfection model

Messiness is governed by source behaviour, never by random corruption. These four axes are requirements, not accidents.

### Identity variation

The same organisation, unit or person appears differently in every register.

| Canonical | As written | Where |
|---|---|---|
| Royal North Hospital | `RNH`, `Royal North`, `RNH Health Services` | Troubleshooting, Incidents, RMAs, Comms |
| St Auburn Private Hospital | `St. Auburn`, `Auburn Private`, `St Auburn Private Hospital` | all |
| Brackenmoor Royal Infirmary | `Brackenmoor Royal`, `Brackenmoor Health Board` | Incidents, Comms |
| Kaimanu District Hospital | `Kaimanu`, `Kaimanu DHB`, `Kaimanu District Health` | RMAs, Comms |
| Nordvik Medical Distribution | `Nordvik`, `Nordvik (dist)`, `Nordvik Medical` | all |
| Serial numbers (canonical `PO-P1-004111`) | bare `4111`; `SN 4216`; `P1100-4563`; `PO-P1-004213 ` with a trailing space | Troubleshooting, RMAs, Incidents |
| PulseOne P1-100 | `P1-100`, `PulseOne P1-100` | RMAs |

Rules: every register picks its naming habit and mostly keeps it; a register written by several people is inconsistent *within itself*; abbreviation gets worse the more hurried the context (the troubleshooting log, filled in on a ward, is the worst). At least one serial pair must be a genuine transcription conflict, so two readings survive to a human.

### Timing variation

- `Date Raised` and `Date Received` on an RMA are weeks apart, and sometimes out of order with `Date Closed`.
- Incidents logged days after they occurred; `Last Online` in the past relative to `Reported Date`.
- Troubleshooting checks batched — several sites on one day, then nothing for a fortnight.
- Email threads where `Date of Last Email Sent` is months after the initial email, and some where it is the same day.
- Two date formats in one column (`2026-03-26` and `26/03/2026`), because someone pasted from a different locale.
- Distributor-reported events arriving in batches, delayed relative to direct customers.

### Completeness variation

- `SW Version at Time` blank on ~⅓ of incident rows. **This is the single most consequential gap** — it is the direct obstacle to the SW-version cohort and what Workflow 4's missing-data callout exists to surface.
- `Serial Number` and `Patch Lot` missing on many troubleshooting rows.
- `HW Rev` and `SW Version` blank on some RMAs.
- `Contact Email`, `Legal Entity Name`, `Attachments` frequently empty.
- Checks abandoned partway with a note saying so.
- Service findings never copied back into the related communication thread.

Missingness must follow from the situation. A ward nurse does not read a serial off the back of a hub; a bench technician always does. Generate the gap where the person would not have known, not uniformly at random.

### Classification variation

- `Event Code` on the incident log is correct where `Source = Telemetry`, inconsistent where `Source = Dashboard alert`, and blank or wrong where a human typed the row.
- `Type` on the communications log is the logger's guess. Complaints filed as `Technical query` and vice versa.
- The troubleshooting log's four issue columns hold the wrong kind of issue often enough to matter: adhesive findings under `Hardware Issues`, battery findings under `Software Issues` as "Charge state reporting wrong".
- One row can legitimately carry two indicators ("Patch fell off, reapplied" + "Skin prep may be a factor").
- Vocabulary differs per team: service says "comms module intermittent under thermal load", the ward says "keeps dropping out", quality says "loss of wireless communication between sensor and receiver". All three are IND-01.

## The planted threads

Four, and only one is the headline. All must be discoverable **only by joining registers** — no single source may reveal any of them.

| Thread | Shape | Why it is there |
|---|---|---|
| **IND-04 on SW 1.1.0** (headline) | `ALERT-FALSE` crosses 2.0x in the rolling 90 days, concentrated in hubs on SW 1.1.0 across three organisations. Troubleshooting rows say "1.1.0 alert logic" and "Threshold set to default not ward profile"; RMA findings on the same cohort say "no hardware fault" and "configuration reset to ward profile"; client emails complain about night-time false alerts. | The demo. The fleet-wide rate is unremarkable; the cohort rate is not. |
| **IND-03 on H1 units past ~18 months** | `BATT` cluster on older H1 hardware, with RMAs recording "Battery module replaced, capacity 61% of nominal". | A second, quieter signal on a different cohort axis, to prove the first was not a one-off. |
| **IND-05 on one or two patch lots** | `ADHESIVE` cluster confined to specific lots, visible only once events are joined to the lot allocation. | Exercises the second denominator and the lot cohort. |
| **The near-miss** | A rate rise that looks like a signal and is fully explained by a hospital network outage — ward-wide, one site, one week, with the outage visible in the comms log. | So a human can correctly close it as *no action*. A system that only ever finds problems has not demonstrated judgement. |

The *pattern* is planted in the world model; the *rows* are produced by the normal source behaviours above. No register is hand-edited to make a thread work.

**And the headline thread is now double-locked.** It is discoverable only by joining registers *and* only after tier 1 has run: of the fifteen `ALERT-FALSE` events on SW 1.1.0 in the live window, two carry a correct `SW Version at Time`. The cohort does not exist in the register set as a human left it. That is a property of the dataset to preserve, not a defect to generate around — it is what makes the Signal Register's `Capture-dependent (Y/N)` cell mean something.

## Generation sequence

1. **Fix the company state** — organisations, wards, staff, products, SW versions, HW revisions, lots.
2. **Build the fleet** — hubs with install dates, wards, beds, HW revisions, SW version history and statuses. This is the denominator; get it right first.
3. **Advance the world twenty months** — ordinary operations at configured rates, plus the four planted threads as *world conditions* (a defective alert-logic build shipped in 1.1.0), not as rows.
4. **Emit the artifacts** — for each world event, the record its source system would actually hold: a telemetry event, an email thread, a transcript passage, a work order and its notes, a ward-round observation. Complete and faithful; strictly more informative than any row derived from it. Spec in [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md).
5. **Let each register observe** — each source adapter decides whether it *transcribes* an artifact at all, when, which fields its users carried across, how it names things, and which columns it leaves blank. Some artifacts are never transcribed; 62 indicator events reach no incident row at all.
6. **Render** — xlsx, exact column names and order, two date formats, trailing spaces preserved, plus the two capture columns per [`REGISTERS.md`](REGISTERS.md) §3.0.
7. **Backfill telemetry** from the fleet and the registers, per [`TELEMETRY-API.md` §4](TELEMETRY-API.md#4-backfill). Calibrate routine event rates so the trailing-12-month rates land near the baselines the PMS plan already states.
8. **Integrity checks** — referential integrity where a register would have it, plausible date ordering, and confirmation that variation follows configured behaviour rather than noise. Every `Captured From` pointer resolves to a real artifact; every `.eml` parses and every thread chain closes; every cited transcript span lands on a real speaker turn. Check no real company, patient or employer information is present.
9. **Freeze** — version, private seed, checksums. Immutable during development.
10. **Evaluate independently** — only after freezing, build the answer key from the private world.

Steps 4 and 5 are the reframe's whole contribution to generation, and they are one step logically: **the artifact is the truth, the row is somebody's account of it, and the delta is the product's value.** As built, the order is inverted — the register pack is frozen first and the artifacts are written to agree with it — so step 5's job in practice is to *document* each existing blank's cause rather than to produce it.

## Evaluation

Derived after generation, kept out of the product's reach.

| Dimension | Question |
|---|---|
| **Capture — recovery** | Of the 62 indicator events with no incident row, how many does tier 1 draft? Of the blanks `capture-targets.csv` marks as fillable, how many get filled? |
| **Capture — accuracy** | Of the fields it filled, how many match the world? Scored against ground truth, never against whether a reviewer clicked accept. |
| **Capture — restraint** | Does it leave blank what its source does not evidence? Does it file an incident for a hub that is `Spare`? Does it ever emit a telemetry-sourced `SKIN` row — which would be an invented event? |
| **Capture — episodes** | Does the near-miss burst arrive as one episode or as ten incidents? |
| Classification | Does each event get the right indicator code? Broken out by source, because telemetry is easy and ward free-text is not. |
| Entity resolution | Which rows genuinely refer to the same hub, lot, organisation? Does the agent avoid false merges on the near-identical serials? |
| Calculation | Are rates reproducible from the stored numerator and denominator? Are the right hubs included in the denominator? |
| Cohort attribution | Does the agent find the tightest cohort that breaches, or stop at the fleet? |
| Judgement | Does it raise the three real threads? Does it correctly close the near-miss? How many signals does it raise that a specialist would call noise? |
| **Coverage lift** | The headline: indicator events correctly represented in the registers, before and after capture. The measured baseline is 53%. |
| Traceability | Can every number be walked back to source rows via the Agent Action Log, and from a drafted row to its artifact? |

The answer key for the register layer is `mock-company-v2/ground-truth/` as built — `hubs.csv`, `events.csv`, the four `*-links.csv` files, `organisation-variants.csv`, `patch-allocations.csv`, `verification.txt`. The artifact layer extends it with five more files, specified in [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md) §Ground truth for artifacts:

| File | What it scores |
|---|---|
| `artifact-index.csv` | every artifact → the event(s) it evidences and the register row it was transcribed into, blank where it never was |
| `capture-targets.csv` | per (register, row, field): the true value, what the human wrote, and which artifact a bot should be able to fill it from |
| `meeting-items.csv` | which transcript spans are genuinely filable, and what each becomes |
| `complaint-truth.csv` | which threads are genuinely complaints, which are ambiguous, and why |
| `episodes.csv` | raw telemetry events → the episode they belong to, so de-duplication is scorable |

`capture-targets.csv` is the load-bearing one. Without it, "the bot filled 340 blanks" is unscorable — the claim has to be *the bot filled 340 blanks and 328 of them match the world*.

A qualified reviewer may judge whether an output is useful. The dataset must not declare that a specific decision was objectively required unless that decision exists as an authorised event in the private world.

## Acceptance criteria

- Twenty months of coherent history, most of it uneventful.
- Each register stands alone as a plausible export from its owning team.
- Cross-register relationships exist **without** a shared identifier.
- Every imperfection traces to a documented source behaviour, not to a random corruption pass.
- The four planted threads are discoverable by joining, and by joining only — and the headline thread only after tier 1 has run.
- The near-miss is genuinely ambiguous before the join and genuinely innocent after it.
- The four agent registers hold back-catalogue only, and nothing inside the live window.
- **Every artifact is strictly more informative than the row derived from it**, and a blank that no artifact can fill exists and is marked as such — so "100% completion" is not the target and cannot be gamed.
- **All 62 unlogged indicator events have an artifact**, split 44 hub-code / 15 adhesive-inferential / 3 human-only.
- The register pack's existing cell values, row counts, indicator rates and story strengths are unchanged; the only movement is additive.
- No desired conclusions or evaluation labels in any product-facing file.
- A product failure cannot be hidden by changing the dataset afterwards.

## Ownership note

`mock-company-v2/`, `tools/` and `reference-data/` are owned by the data-generation workstream. This file is the contract they generate against, and [`mock-company-v2/README.md`](../mock-company-v2/README.md) is the authority on what was actually built — where the two disagree, the README wins and this file is wrong. The upstream artifact layer is in progress against [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md). The superseded v0 dataset build is logged in [`archive/BUILD-STATUS-V0.md`](archive/BUILD-STATUS-V0.md).
