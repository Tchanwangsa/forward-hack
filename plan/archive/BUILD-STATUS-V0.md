# V0 Data Seed — Build Status

> **SUPERSEDED — historical record.**
>
> This is the build log of the **v0 dataset**, generated 2026-09-13 against the previous
> nine-workflow / vigilance-clock design. That design was replaced. The current shape is
> five workflows over nine registers with no vigilance machinery — see
> [`../README.md`](../README.md).
>
> Nothing here describes the current dataset. It is kept because the generation techniques,
> the imperfection calibration, and the decisions it closed are worth re-reading. Section
> references into `../REGISTER-SHAPES-V0.md` point at sections that no longer exist.

Started 2026-09-13. Goal: generate everything `mock-company/` needs for the V0 journey in
[`REGISTER-SHAPES-V0.md` §9](../REGISTER-SHAPES-V0.md), so the product has real data to ingest.

## Decisions closed before any generation started

All four open decisions in [`REGISTER-SHAPES-V0.md` §10](../REGISTER-SHAPES-V0.md) are now closed in
[`mock/asteria/GENERATION-CONTRACT-V0.md`](../mock/asteria/GENERATION-CONTRACT-V0.md):

| # | Decision | Resolution |
|---|---|---|
| 1 | US market presence | **Added.** Feb 2026 entry, one importer, one hospital network, two sites. Buys the §803.3(b)(2) awareness asymmetry, an EU authorised representative, and an `outsourced_handler` awareness class. |
| 2 | `90 Not a complaint` placement | Both — terminal complaint state *and* a pointer back to the feedback event. Already settled in §10.2. |
| 3 | Which signal | **PulseOne.** Reusable → `active_installed_base` denominator, against PulsePatch's `units_distributed_in_period`. One register, two aggregation rules, per §7.1. |
| 4 | Holiday calendars | IE, NL, US federal, AU/VIC for 2025–26, as `reference-data/` — the only place in the repo allowed to state real-world fact. |

The cast grew from 12/8/15/30 to **13 employees / 11 orgs / 17 sites / 38 contacts**. Identifier
schemes, serial and lot ranges, and the 2025-03-01 → 2026-08-31 window are fixed in the contract.

The physical root cause, the seven mandatory confounders, and the demo journey's raw material are in
[`mock/asteria/PRIVATE-WORLD-V0.md`](../mock/asteria/PRIVATE-WORLD-V0.md) — private, and deliberately
withheld from the source renderers, because a renderer that knows the answer writes records that are
plausible only because the answer is known.

## Architecture

```text
  world simulator  →  plan/mock/asteria/world/world.json   PRIVATE
                      every event carries `observations`:
                      which system saw it, when, knowing what
                                    │
                                    │  renderers read observations, never the truth
                                    ▼
  six renderers    →  mock-company/                        PRODUCT-FACING
                      source-native only. no private IDs. no answer key.
                                    │
                                    ▼
  freeze           →  manifest · checksums · leak scan · integrity checks
  evaluation       →  derived AFTER the freeze, stored outside mock-company/
```

The `observations` mechanism is the load-bearing idea. Missing fields are generated as *a system that
did not know a fact*, never as a random null — which is what [`MOCK-DATA.md`](../MOCK-DATA.md)'s
imperfection model actually requires and what makes the messiness defensible rather than arbitrary.

## Task status

| # | Task | Owner | Status |
|---|---|---|---|
| 1 | World simulator → `world.json` | subagent | **done · verified** — 4,977 events, all checks pass |
| 2 | QMS controlled documents, templates, register | subagent | **done · verified** |
| 3 | Holiday + clock-rule reference data, clock implementation | subagent | **done · verified** |
| 4 | ERP · CRM · installed base (structured exports) | subagent | **done · verified** |
| 5 | Support tickets · service · RMA | subagent | **done · verified** |
| 6 | Email corpus (`.eml`) | subagent | **done · verified** |
| 7 | Slack export · Drive working documents | subagent | **done · verified** |
| 8 | QMS quality records (complaints, NC, CAPA, vigilance, audits) | subagent | **done · verified** |
| 9 | Meetings · PMS working files | subagent | **done · verified** |
| 10 | Freeze: manifest, checksums, integrity checks | subagent | **done · verified** |
| 11 | Evaluation set | subagent | **done · verified** |

## Verified deliveries

### Task 3 — regulatory reference data · accepted 2026-09-13

`reference-data/holidays/` (IE, NL, US federal, AU-VIC 2025–26) · `reference-data/clock-rules/`
(`us-21cfr803.json`, `eu-mdr-art87.json`, `jurisdictions.json`) · `tools/clock/` (89 tests, passing).

Independently re-verified rather than accepted on report: Easter 2026 = 5 April (so IE Easter Monday
6 Apr, NL Ascension 14 May both check out), 4 July 2026 is a Saturday so the US observes 3 July,
first Monday of May 2026 is the 4th. Every holiday entry's stored weekday matches its date. Exactly
one date carries `confidence: unverified` — the Friday before the AFL Grand Final, which is genuinely
un-gazetted — and it is in the AU calendar, which no statutory clock computes against.

The §803.3(b)(2) asymmetry works on the real demo timestamp. Same awareness event, 2026-06-12 18:40
AEST:

```text
30_calendar_day     · any_employee           → due 2026-07-12  (read in Europe/Dublin)
5_work_day_803_53_a · any_employee           → NO DUE DATE
                                               "does not start this clock"
5_work_day_803_53_a · ae_collection_duties   → due 2026-06-22
```

I recomputed 2026-06-22 by hand: five work days from Friday 12 June, skipping Juneteenth on Friday
19 June. It skips it.

**Correction.** The rendered register and `tools/clock` both give **2026-07-13** for the 30-day row,
not the 2026-07-12 above, because the US clock is read in `Australia/Melbourne` where 18:40 +01:00
falls on the next day. Both readings are defensible and the difference is exactly the hazard §5.3
describes. `eval/clock-truth.json → timezone_sensitivity` records every US row under both bases and
requires a product to **name the basis it used** rather than to pick the one we happened to pick.

Three judgement calls the agent made that I would not have specified and am keeping:

1. **US calendar-day clocks do not roll off a weekend.** Part 803 states no roll-forward rule and the
   reference did not verify one, so the encoding carries `confidence: verified_as_absence` rather than
   importing the EU rule. Importing it would have been precisely the fabrication §5.4 forbids.
2. **Germany is in the enum, loaded, and still unavailable.** The MDR rule set applies, but no German
   holiday calendar is loaded and Q14's roll-forward is national. It is the cheapest possible
   demonstration that `clock_rules_available` is a *data* question, not a regime question.
3. **Dates past 2026 refuse rather than assume.** `calendar_out_of_range` instead of silently treating
   2027 as ordinary working days.

### Task 2 — QMS controlled documents · accepted 2026-09-13

42 files in `mock-company/qms/` — 22 PDF, 19 DOCX, 1 XLSX register. Leak scan clean (it reads inside
DOCX/XLSX zip containers, so this is a real result, not a filename check).

Verified rather than accepted on report: both "scanned" PDFs have a genuinely **zero-length text
layer** — they are images, and an ingestion pipeline must OCR them or fail honestly. The register
discrepancies are real: it lists `QMS-SOP-002` at Rev 3 while the folder holds Rev 4, lists
`QMS-SOP-005` under its *pre-Rev-3 title* while the folder holds "Investigation and CAPA Rev 4", and
lists `QMS-SOP-013` with a dead UNC path and no file at all. Row 29 is hidden, 23 `TODAY()` formulas
are live, and status is spelled six different ways.

The PMS Plan is properly vague: its Art. 88 indicators read "To be established" / "None set", and the
only numbers anywhere in it are operational (a provisional 2.0% return action level, quality
objectives). So the product's honest output is *"no threshold is specified in the PMS plan"* — which
§7.1 says is the finding, not a bug. Its §6.1 already splits PulseOne (installed base, episodes of
use) from PulsePatch (units distributed in period), which is the two-denominator contrast the whole
signal choice was made for.

Three decisions the agent had to make that the contract had not settled, now folded back into it:

1. **Device classification** — EU Class IIa (Annex VIII Rule 10), AU Class IIa, US Class II. PSUR
   cadence and PMS scoping depend on it, so it could not stay open. Now fixed in contract §3.2b.
2. **Nobody may be invented, but an 80-person company has a Managing Director.** Resolved by naming
   only roster people and showing every other position as an unnamed role box with a headcount, with
   QMS approval formally delegated to the Management Representative. Defensible and realistic.
3. **The effective vigilance procedure has no 21 CFR Part 803 content at all.** US entry was Feb 2026,
   the RA specialist started in March, Rev 3 is still in draft. This is the understaffing the contract
   already describes, and it means US reportability assessments in the window are being made without a
   procedure covering them — which is a finding a real audit would produce. Now pinned in §3.2c so no
   downstream record contradicts it.

### Task 1 — world simulator · accepted 2026-09-13 after one rejection

`plan/mock/asteria/world/world.json` — 6.5 MB, 4,699 events, 900 device units, 38 event types.
`tools/generators/world/` — 12 modules, 50 internal checks, byte-identical across runs.

**Rejected first time for two blockers**, both found by walking the data rather than reading the report:

1. The nine awareness events for the Dublin journey had `feedback_no: null` and linked to the
   occurrence instead of the feedback event — so the most important records in the dataset could not
   be joined to their complaint. The other 180 awareness events linked correctly; the demo path had
   bypassed the numbering pass. Now 189/189 carry both.
2. **No** vigilance obligation carried a governing awareness event. §4.7 requires exactly one per row
   and §5.5 asserts it as a grain invariant; without it the clock cannot run and the reference
   implementation cannot be wired to the data. Now 22/22, each with a `governing_awareness` decision
   record naming the human who selected it.

The Dublin event now resolves exactly as `REGISTER-SHAPES-V0.md` §9 wants:

```text
VIG-2026-0010  US  not_reportable              ← Hamish Doyle    any_employee              18:40+01
VIG-2026-0008  IE  uncertain_reporting_anyway  ← Lotte Janssen   authorised_representative 18:38+01
VIG-2026-0009  NL  90_not_applicable           ← Lotte Janssen
```

The agent deviated from my instruction on one point and was right to. I had specified the authorised
representative's awareness at 18:42, which is *after* the account manager's 18:40 — so "EU awareness
predates Asteria's" would have been false and a strict MDCG Q15 reading would have selected the same
person for both rows, collapsing the asymmetry. It moved the AR to 18:38. Same Friday, same beat, and
now the EU clock genuinely starts before Asteria knows anything at all.

**The module-lot join was claimed but did not exist.** `comms_module_lot` appeared in zero observation
`knows` lists, making `PRIVATE-WORLD-V0.md`'s "the join is available in the sources, it has simply
never been made" false as generated. Now there is a three-hop path with no shared key, which I walked
myself using only what the source observations expose:

```text
SN-4471 → manufactured 2026-01-13   installed-base device master
        → batch BLD-H21-2603         QMS device-history index (build date range, no component lot)
        → CM-4412                    ERP production consumption (its own lot grammar)
```

QMS genuinely cannot see the component lot, and the production order carries only a `serial_block_hint`
spanning 4015–4510 rather than an allocation — because serial labels are not issued in build order.
Discoverable, and inconvenient. The 2.9× hardware-revision + software-version cut is untouched, so the
cohort is still *found* there and the lot only *confirms* it.

### Task 4 — ERP · CRM · installed base · accepted 2026-09-13 after one fix

17 CSV files, 8,169 rows. The three systems read as three systems: CRM fully-quoted Title Case with
`D MMM YYYY` dates, ERP `ABBREV_UPPER` with CRLF and `DD/MM/YYYY`, installed base snake_case ISO. None
carry a timezone, which is itself the data-quality problem contract §2 wants.

Southern Cross appears four ways in CRM (72 / 21 / 15 / 17) and only as the legal name in ERP. 280 of
775 dispatched units were never registered, `SN-4471` among them. Median last software-version
observation is 70 days stale, p90 134, max 495. The corrected order line survives as two revisions
rather than an overwrite.

**One fix, and the bug was mine.** I had banned the comms module lot code in the leak scanner, which
forced every supplier lot into a single grammar and collapsed the two-grammar design into a string
match. Scanner and contract corrected; the agent restored the split and added an assertion that the
two tables' lot sets stay disjoint. Verified: intersection is empty, and the join now requires a
reader to bridge `L4412` ↔ `CM-4412` themselves.

An unplanned detail fell out of it that is better than anything specified: `CM-4390` was supplied by
Corvin Electronics and `CM-4412` by **Halden Components**. The second-source supplier is visible in the
goods receipts, and no record anywhere says why that matters.

**Two pushbacks accepted rather than overruled.** The renderer omitted `serial_block_hint` from the
production order because the ERP observation does not know it — my task text was wrong and its output
was right. And it refused to fabricate the missing cancelled order, which is the correct behaviour
under contract §9.3.

### Task 7 — Slack export · Drive · accepted 2026-09-13

559 channel-day files, 966 messages across 6 channels, plus 12 Drive files and 21 rows of Drive-v3
metadata. Structurally validated by me, not by report: **0 orphan replies** (every `thread_ts`
resolves to a root in the same channel), **0 unresolved user ids**, **0 duplicate timestamps**, 76 raw
`<@U…>` mentions and 61 `<url|label>` links left unresolved exactly as a raw export leaves them, 185
reaction arrays, 18 edits, `blocks`/`rich_text` alongside flat `text` on 959 of 966.

The best detail is one I did not ask for: **daily buckets are UTC, as Slack actually writes them.** A
Melbourne workday straddles two files, thread roots and their replies can land in different day files,
and 21 day files span two Melbourne dates. Anything that naively treats a Slack day file as a day will
be wrong, which is true of the real thing.

Drive imperfections confirmed on disk: two files named `Investigation notes.docx` in different folders
with different MD5s and different subject matter; `Complaint tracker (OLD do not use).xlsx` marked
`trashed: true` and still fully readable; and `Q3 numbers for Meridian.xlsx` shared with two
`@meridianmedpartners.com` addresses while still containing the AU and IE rows — an ordinary
oversharing mistake nobody in the fiction has noticed.

**One spec item could not be met and should not have been.** I asked for out-of-hours Slack traffic
from the European correspondents. The world contains no European Slack authors at all, so meeting it
literally would have meant inventing events — the one thing renderers must not do. It rendered the
underlying point through UTC bucketing and the EU authorised representative's guest accounts instead.
Correct refusal; if real EU Slack traffic is wanted it has to originate in the world simulator.

### Tasks 5 & 6 — support/service and email · accepted 2026-09-13

**Support and service.** 253 tickets, 745 comments, 680 status changes, 168 work orders, 70 RMAs,
11 attachments. Requirement #12 verified on a real pair: `TKT-7261` carries the nurse's words
*"display stopped updating and the buttons did nothing"* with serial `SN 1025`; `WO-21431` on `SN-1025`
records `technician_finding: freeze not reproduced`, disposition RTS. Five separate columns keep the
customer's symptom, the technician's finding, the work done, the test result and the disposition apart
— which is the distinction a merged "resolution" field destroys.

UDI is empty on every product-issue ticket, and absent from the general-request form entirely, so
*not provided* and *not applicable* stay distinguishable. 181 tickets archived, 2 soft-deleted,
34 reopened, `other_general` on 85 of 253.

**Email.** 561 `.eml` across 5 mailboxes, 244 threads. **0 parse failures, 0 dangling `In-Reply-To`,
561 unique Message-IDs** — every thread reconstructs from headers alone. External senders carry
Gmail-shaped Message-IDs and Asteria carries Outlook-shaped ones, which nobody asked for and which is
exactly right.

The demo thread is the best artefact in the dataset so far:

```text
Fri 12 Jun 2026 18:40 +0100   Aoife Gallagher → Hamish Doyle, Cc the EU authorised rep
Mon 15 Jun 2026 08:55 +1000   FW: — zero added text, no signature, just the Outlook quoted chain
Mon 15 Jun 2026 09:34 +1000   support@ replies to the customer
```

The Cc on the Friday message is where the authorised representative's 18:38 awareness comes from — it
is visible in a header, not asserted anywhere. And a second two-address trap emerged on its own: Aoife
sends from `aoife.gallagher@` and later replies from `a.gallagher@` in the same thread.

**Three refusals, all correct.** Service has no "job done Friday, entered Tuesday" because every
service observation sits within ±9.4 h of its event — fabricating the lag would have contradicted
`observations[].at`, which *is* the definition of when that system recorded it. `via.channel` is
`unknown` on 126 tickets rather than invented. And a mailing-list digest was impossible because an
external list means an external organisation, which contract §4 forbids — so it became an internal
automated summary instead.

**One judgement call I am keeping.** The label photographs show what is printed on the label, including
the UDI-DI, while the ticket's UDI field is empty. That is the only place rendered content exceeds the
observation's `knows` — and it is the sharpest form of requirement #3: the UDI *is* in the evidence,
photographed by a nurse, and nobody typed it into the field the regulation requires. A product that
reads it off the image is doing something a human did not.

### Task 8 — QMS quality records · accepted 2026-09-13

293 record files + 4 register workbooks: 108 feedback events, 62 complaints, 40 investigations, 18 NCs,
6 CAPAs, 22 vigilance obligations, 5 audits with 14 findings. Open records are DOCX, closed and
approved ones PDF with signature renditions, all rendered as filled instances of the controlled forms
task 2 produced — so the records and their blank forms cannot drift typographically.

**The cross-agent check I most wanted, passed.** Two agents that never communicated agree on a
regulatory deadline:

```text
tools/clock          IE 15-day from 2026-06-12T18:38+01 → 2026-06-29   (nominal 27 Jun is a Saturday)
vigilance-register   Due: 29 Jun 2026
```

The deadlines in these records are computed through `vigilance_clock`, not invented, and the AU rows
say "no clock rules loaded" rather than guessing — §5.4 behaviour reaching the data, not just the code.

**The 82% gap is an intended property and is now documented as one.** 57 of 68 complaints carry no
reportability determination (the figure was 51 of 62 before the world was regenerated; the verified
current number lives in `eval/field-truth.json → reportability_coverage`). The agent flagged this as the sharpest tension in the spec and it was
right to. The resolution is that the two rules bind at different levels: *"negative decisions are
records, not absences"* is a requirement on **the register's design**, which is met — all eleven
assessed complaints have terminal states with rationale, named decider and date. Whether the fictional
company met that requirement is a **fact about the company**, and contract §3.2c settles it: US entry
in February, no RA specialist until March, an effective vigilance procedure containing no Part 803
content at all.

Generating the missing 51 would invent human decisions the world does not record, which §9 rule 3
forbids, and would destroy the finding. *"82% of your complaints have no recorded reportability
determination, and here are the eleven that do"* is a day-one product finding, citable, and takes a
human weeks to establish by hand. The README now carries it under a heading that says **do not "fix"
it**.

**A deliberate rule-version divergence, isolated to one place.** Every vigilance record now carries a
`Rule version applied` / `Rule set currently loaded` pair read live from `reference-data/clock-rules/`:

```text
Ireland         applied MDCG 2023-3 Rev.1          loaded mdcg-2023-3-rev2@1.0.0    ×2   ← the divergence
United States   applied 21 CFR 803 (2024 edition)  loaded us-21cfr803@1.0.0         ×6   no divergence
Australia       applied Not applicable             loaded none                      ×7
```

The Irish rows record that the determination was made under Rev.1, that the deadline has **not** been
recomputed under Rev.2, and why — recomputing would replace a date that was defensible on the day with
one that was not yet available. This is precisely what §5.3 puts a `rule_version` field there for.

Two bugs it found while doing that, which I had missed: the Australian rows were citing MDCG 2023-3
on TGA determinations where nothing was computed, and the Irish submission section was citing
21 CFR 803.56 for follow-up numbering. Both now jurisdiction-conditional.

### Task 9 — meetings and PMS · accepted with one correction

89 meeting files and 61 PMS files. `calendar.ics` carries 55 `VEVENT`s — 11 `RRULE` masters, 44
`RECURRENCE-ID` overrides, a cancelled occurrence, `EXDATE`s, two `VTIMEZONE`s — and every one of the
61 world meetings resolves at the **exact instant** across all three Australian DST transitions and
Dublin GMT. The trending workbook has 542 formula cells, and the planted `Summary!B25` error is
genuinely wrong: a `SUMIFS` over `$N$2:$N$60` against 61 data rows, returning 48 where 49 is correct,
and the row it drops was received 2026-08-29 — inside the window it claims to cover.

The best artefacts are the losses between transcript and minutes: a 2026-07-09 exchange about the queue
feeling heavier that never reaches the approved minutes, and a trend decision deferred to email in the
transcript but recorded as decided-on-the-day in the approved PDF, which `QMS-TMP-001` explicitly
forbids.

**One correction:** it invented a PulsePatch pack size of 5 per box; `products.md` fixes it at 10. It
flagged the invention itself, which is why it was caught. The highlighted assumption cell stays — a
hard-coded constant with a hand-typed note beside it *is* the embedded-calculation-logic requirement.

### The claim I got wrong

I wrote earlier that the aggregate PulseOne complaint rate is flat, and cited my own recomputation.
That was true of the denominator I happened to choose and not of another:

```text
per 100 shipped units      OLS +0.0069/month, Spearman +0.212      flat
per 100 registered units   0.60 → 1.59 → 1.53 → 1.92 → 1.69 → 2.10  not flat
```

Only 495 of 775 dispatched units are ever registered, and the coverage is not uniform over time. The
PMS renderer measured the second, refused to manufacture the flatness my brief asserted, and rendered
what the data actually said. It was right and I was overconfident.

This is now being characterised properly rather than patched. If the trend genuinely reverses by
denominator basis, that is **more** valuable than the flatness I asked for: it is what §7.1's
denominator enum exists to express, it pairs with a PMS plan that specifies no threshold, and it makes
the honest product output *"your trend reverses depending on a denominator basis your plan does not
specify"*. But it has to be a known property with numbers attached, not something discovered during a
demo.

### Task 1 rework — the reachability sweep

The sweep I asked for after the `order_cancelled` miss found **18 real defects**, far more than the one
that prompted it:

| Defect | Consequence |
|---|---|
| `decision_recorded.reportability` never emitted | §4.7 says the reportability call *is* a decision row; the rationale was on the register instead |
| `.closure` and `.capa_required` never emitted | negative CAPA and closure decisions had no rows at all |
| `triage_state` `duplicate`/`void` never emitted | §4.4's "terminal link, never a deletion" had nothing to point at |
| `complaint.status` `not_a_complaint` never emitted | register decision #2's terminal state never occurred |
| `vigilance.clock_class` `5_work_day` never emitted | **one of the two clocks the whole demo is about** |
| no unit ever decommissioned | `products.md`'s lifecycle stopped one stage short |
| C2, C3, C6, C7 | **four of seven confounders silently under-producing or not implemented at all** |
| complaints dated 2024 | before the simulation window opened |
| `cands[:9]` on vigilance candidates | every *sampled* US row forced to `90_not_applicable` |

That last one matters most for what I had already accepted: the US vigilance story I verified was the
demo path only. Outside it, US vigilance barely existed.

It also corrected my arithmetic on the cancellation — I assumed 406 draws where only 65 reach the
branch, so a miss was 3.6% likely, not 10⁻⁹. Its reframing was better than my diagnosis: the defect
was never the miss, it was that **a named acceptance criterion was left to a coin flip.** Now every
declared-behaviour-with-one-instance is designated deterministically from the eligible set, with the
seed still choosing *which*.

Six absences that were genuinely out of scope now sit in a `DELIBERATELY_ABSENT` table with a reason
each, so an intentional gap can no longer be mistaken for an unreachable branch.

**Employee availability is now an entity fact**, not just a pair of events: 0 violations across actors,
owners, deciders, approvers, auditors, attendees, action owners, Slack authors and email senders. And
**0 offset/timezone mismatches** across 4,977 events — with the rule written into `SCHEMA.md` that no
offset mismatch is ever deliberate. Dropping an offset is a renderer decision about how a system
records time; lying about one is nobody's.

### The coordinated regeneration — 2026-09-13

Two agents were killed mid-task by a session limit. `world.json` had already been written (4,977
events); `mock-company/` was stale against it. I re-ran all six renderers myself rather than relaunching
agents, and fixed five defects that only appear when a renderer meets a world it was not written
against. Every one was a *renderer* assuming something about the world instead of reading it:

| Defect | Fix |
|---|---|
| `crm.py` crashed on the new `order_cancelled` event type | Added the branch. Sales logs the cancellation at 11:19; ERP updates status at 15:19. |
| `orders.csv` had no status column at all, so the cancellation could not be rendered | Added `ORD_STAT` / `CANC_DT` / `CANC_RSN`. Requirement #13's cancellation half now exists. |
| Support/service asserted **hardcoded counts** from the previous world (253 tickets, 168 WOs) | Expectations now derived from the world's own observation counts. A frozen count becomes a lie the moment the world changes, and then fails as an assertion rather than as the dropped row it was meant to guard against. |
| The email generator kept a **stale private copy** of my withdrawn `CM-4412` ban | Removed. See below. |
| `meetings-pms` passed `pms=None` into a transcript renderer that asserts its figures come from the PMS data | Wired the loaded data through. The transcripts and the workbook now quote the same numbers by construction. |

**A judgement call on the module lot.** The email renderer emits `CM-4412` in depot service reports.
I checked whether that collapses the three-hop join and it does not: 8 units out of ~900 carry it, so
it is a breadcrumb, not the cohort, and the *population* still needs the manufacture-date → build-batch
→ component-lot join across three systems. A strip-down report recording the module lot it found is an
ordinary thing for a service report to say, and it is plausibly how a real investigator first notices.

**A check that was wrong, not data that was wrong.** The QMS records generator asserted that every
cross-jurisdiction divergence carries two written rationales, and three failed. The data was right: those
three are **market-scope** differences (reported in AU, *not marketed* in the US), where the `90 not
applicable` row correctly carries no reportability rationale. Only the Dublin event is a divergence **on
the merits** — two jurisdictions assessing the same facts and reaching opposite conclusions. The check now
separates the two and requires at least one of the latter, which is what contract §8 #5 actually asks for.

### An accidental defect I decided to keep

Four Australian TGA vigilance rows cite **EU MDR Article 87(7)** in their rationale and use EU clock-class
values on a TGA determination. This was not planted — it emerged from generation and I found it while
diagnosing the divergence check.

I am keeping it. `REGISTER-SHAPES-V0.md` §4.7 quotes FDA citing a manufacturer under §803.17(a)(2) for
precisely this: combining language from other regulators' requirements in a way that produces incomplete
or non-reporting. A quality specialist copying EU phrasing onto an Australian determination is exactly
the kind of error a real small QA function makes, and *"your AU determinations cite an EU article that
does not apply in Australia"* is a citable finding the product should surface. It is recorded in the
evaluation set as such — and recorded as accidental, so no later reader believes we designed it.

### The demo journey survives regeneration

Verified end to end across six independently regenerated sources. The ward is now St Anne's, the
complaint is `CMP-2026-0034`, and the three-way date dispute is intact:

```text
EMAIL   Fri, 12 Jun 2026 18:40 +0100   Aoife Gallagher, Dublin, Cc the EU authorised rep
EMAIL   Mon, 15 Jun 2026 08:55 +1000   forwarded with no added text
TICKET  TKT-7404  created 2026-06-14T23:10Z   (= Monday 09:10 AEST)
QMS     CMP-2026-0034  date_received 2026-06-12, opened 2026-06-17
```

Five awareness events, three vigilance rows, two governing awareness events. The account manager's
awareness now lands at **2026-06-13T03:40+10:00** — the Melbourne instant of that Friday Dublin evening,
i.e. Saturday morning local. The timezone fix made the beat sharper than it was.

`SN-4417`, the transposed serial, is a real H2.1 unit at **Southern Cross Randwick, Australia**;
`SN-4471` is at **St Brendan's Dublin, Ireland**. A resolver that picks wrong attributes an Irish
incident to an Australian hospital.

### The denominator question, answered

The world now ships a `--cohorts` analysis. The answer is more interesting than either of my guesses:

```text
basis                        slope     rho    verdict       C5 cancels
active_installed_base       +0.0018  +0.282  flat          yes
units_distributed_in_period +0.0025  +0.288  flat          yes
registered_units            +0.0139  +0.341  trending up   NO
```

Registration coverage falls from **70% to 58%** across the window (rho −0.932). The rise on registered
units is a **denominator artefact** — an eighth confounder, discovered rather than designed. So my "flat"
claim was right on both lawful bases, the PMS renderer's "not flat" was a real measurement, and the
resolution is that the basis it used is corrupted by declining coverage. Both observations were correct.

### The cohort ranking, and why I overrode my own decision rule

I had said: raise the planted rate if the true cohort does not rank top-three. It ranks **11th of 46** on
the lawful denominator at 1.61×. By my own rule I should have raised it. I am not going to, and the
ranking is why:

```text
 1  ward: SITE-16 Surgical Recovery 3W          7.75x  p=0.016   n=3   ← small-n trap
 2  module lot CM-4412 + sw>=1.2.0              2.56x  p=0.043         ← the cross-system join
 3  module lot CM-4412                          2.50x  p=0.049
 4  hw_rev x sw: H1 + 1.1.0                     2.40x  p=0.077         ← C5, a genuine rival
...
11  hw_rev x powersave: H2.1 + sw>=1.2.0        1.61x  p=0.284         ← the coarse cut
```

Five of the ten cuts ahead of the coarse cut are *the same finding* seen through a different lens. The
cut a human could make unaided is weak; **the cut that requires joining three systems ranks second with
p=0.043**, on every denominator basis and both time windows. That is the product thesis stated as a
number, and raising the planted rate would make the coarse cut strong enough that the cross-system join
would no longer be necessary — which would weaken the demo, not strengthen it.

Rank 1 is a single ward with n=3: a small-sample trap that a naive ranker surfaces first and a competent
one discounts. On the PulsePatch side the top cut is lot `PP72-2541C` at 21×, p=3.3e-10 — confounder C3,
a *real* signal on the other product family that the company already found, investigated and closed. The
product must not claim credit for it.

### Task 11 — evaluation set · accepted 2026-09-13

`plan/mock/asteria/eval/` — 1,325 source identifiers mapped across 14 classes, 2,500 source keys →
world events, 28 multi-channel merges that must happen, **18 near-duplicate pairs that must not**, all
68 complaints' mandated fields, 21 clock truths, and the cohort rankings per denominator basis. Plus
`SCORING.md`: 1,000 points, of which **340 are honest negatives, refusals and empty-state
discrimination against 370 for discoveries**, with *unbounded* fabrication penalties. Its three
reference profiles are the point — a "confident fabricator" scores deeply negative, and an "honest null
run" that finds nothing and says so scores ≈300 with no penalties.

Ten spot-checks re-verified against the rendered files, each extracting the surrounding context from
the file itself. The denominator artefact was independently reproduced from the installed-base CSVs
alone: coverage 70.3% → 58.4%, against the world's 70% → 58%.

**Six cases are marked ambiguous rather than resolved**, which is the most valuable thing in the set.
`SN-4417` is the sharpest: ward, site and software version all point at `SN-4471`, the digits point at
a real registered unit in Randwick, and the recorded answer is *"ambiguous — human gate only"*, with the
evidence for each side and a note that **either silent choice is wrong**. It also found that one
roster trap has degraded — a contact's full address survives only as a clipped cell in the org-chart
PDF — and excluded it from scoring rather than pretending it still works.

### A defect the evaluation set found, and the fix

It reported that the vigilance register's `Clock rules available?` column was **inverted**: every
Australian row read "Yes" beside a Due cell saying TGA rules are not loaded, while status-90 US and NL
rows read "No" although their rules *are* loaded.

I checked and it was worse than reported — the column contradicted itself inside a single row, and it
inverted the one behaviour `REGISTER-SHAPES-V0.md` §5.4 exists to demonstrate.

The cause was a category error in the world: `clock_rules_available` was a per-row fact conflating
*"rules exist for this jurisdiction"* with *"a due date was computed for this row"*. But whether we hold
clock rules is a fact about `reference-data/clock-rules/`, not about the fictional company — the world
should never have owned it. The renderer now reads `jurisdictions.json` directly:

```text
Australia       No    No AU clock rules loaded    x8
Ireland         Yes   29 Jun 2026                 x1
Netherlands     Yes   Not applicable              x1
United States   Yes   dates, or Not applicable    x11
```

Two of the evaluation set's four findings (FIND-02, FIND-03) described precisely this defect. Once
fixed, I **removed them from the answer key** rather than marking them resolved: a stale finding would
mark a correct product wrong for failing to find a bug that no longer exists. FIND-01 and FIND-04 stay,
because those are statements the fictional company's own records make — EU vocabulary on a TGA
determination, and a clock class the loaded rules cannot compute — and a real QA function makes exactly
those mistakes.

### Task 10 — the freeze · accepted, and it found five real defects

`source-manifest.yaml` (11 sources, 55 path patterns, every file claimed by exactly one source),
`README.md`, `CHECKSUMS.sha256` (1,689 files, 16,592,591 bytes), and `tools/freeze/integrity.py` —
**111 checks in 7 groups**, with a `--self-test` that breaks a throwaway copy five ways and confirms
the suite raises the right check at the right severity for each.

The agent **did not fix a single failure it found**, which was the instruction and the right call:
the data was produced by seven other agents against a contract, so an integrity failure is a finding,
not a chore. It fixed three bugs in its own checker and reported the rest.

**Five defects. I fixed four at source and re-rendered; one is deferred.**

| Defect | Cause | Resolution |
|---|---|---|
| 41 PMS CSVs ended **`CR CR LF`** | `newline="\r\n"` on `open()` *and* `lineterminator="\r\n"` on the writer, so Python translated the newline twice | `newline=""` — the csv module's documented requirement |
| An action-register row dated **after the as-at** | action dates were not bounded by the tracker's own export cut-off | clamped |
| Three merged tickets had a **broken `previous_value` chain** | the merge's closing transition was timestamped mid-lifecycle | the merge close is now the last transition, because it is the last thing that happens to a merged ticket |
| An internal note **predated its own ticket** | complaint-link notes took the complaint's timestamp, clamped only at the upper end | floored at ticket creation — a complaint may predate its ticket, but an agent cannot annotate a ticket that does not exist |
| **23 observations predating the unit's build** | the bad dates are in the **world**, not the renderer | **Open.** Fixing it means regenerating the world and re-rendering all six sources. Deferred to 0.2.0: 0.6% of one file is not worth destabilising a coherent 0.1.0 late in an unattended run. `integrity.py` fails on it loudly. |

A fifth of my own making surfaced during this: my earlier patch derived the expected RMA count from a
single observation kind, but an RMA row has two origins — a return, or a depot work order carrying an
RMA number. Counting one turned a correct render into a failure. Fixed.

**Final state:** 1,690 files, leak scan CLEAN, checksums verified, integrity **110 of 111 passing**
with the one deferred defect documented in the pack README under a heading that distinguishes it from
the deliberate messiness. *That messiness is behaviour; these are bugs* — a defect explained away as
realism is a defect you ship twice.

### Two limitations worth knowing

**`leak_scan.py` cannot read PDF body text.** It decodes DOCX and XLSX containers, but for PDFs it
only sees uncompressed strings — in practice the `/Title` of 275 files and none of their content, which
is the entire QMS record set. `integrity.py` decompresses the content streams (ASCII85, then Flate) and
scans the real text. Both are clean, but **integrity's result is the one that means something**, and
anyone adding a PDF-producing generator should know the cheaper scanner will not catch a leak in it.

**Identifiers people quote do travel between sources, deliberately.** An order number reaches a CRM row
and a sales email; a complaint number reaches six sources; a device serial reaches ten of eleven, in
four surface forms including a zero-padded one. None of these is a key any system *stores* against a
customer — they are numbers printed on paperwork and retyped by hand, which is what a real dataset looks
like. The freeze reports the serial spread as `info` rather than hiding it, so the next person can argue
with the judgement instead of discovering it. The joins that matter are intact: **no ERP identifier in
the installed-base export, no CRM key in support, and organisation resolution is genuinely unsolved by
grep** — the same organisation really is written four ways.

## Contract amendments made mid-build

- **Freeze date moved 2026-09-01 → 2026-09-10**, with per-source export cut-offs varying across
  2026-09-01…09. The world contained 11 events after its own declared freeze; trimming them would have
  broken referential integrity, so the cleaner fix makes sources disagree about what the latest record
  is — which is the "different export cut-off dates" imperfection `MOCK-DATA.md` asks for anyway.
- **The ban on the word `signal` is lifted.** The QMS author flagged it and was right: PulseOne
  transmits a wireless signal, service notes say *signal strength*, *safety signal* is ordinary PMS
  vocabulary. Banning the word makes honest records unwritable. What is banned is the *claim* — no
  record may assert a group of events is a signal or name a root cause. The scanner checks the claim,
  not the word, and never did check the bare word.

## Review harness

`tools/freeze/leak_scan.py` — run against any renderer's output before accepting it. Fails on private
IDs (including inside DOCX/XLSX zip containers), evaluation vocabulary, answer-key files, and Markdown
masquerading as a source format.

```bash
python3 tools/freeze/leak_scan.py --root mock-company
```

Subagent self-reports are not accepted as evidence; every task is verified independently against this
scanner and against the volume and imperfection tables in the contract.

## Known risks

- **~~The dataset could come out too easy.~~ Correction: it may have come out too hard, and my "flat
  aggregate" claim was only true of one denominator.** See below — this is now the open question.
- **Six renderers writing in parallel could drift.** Guarded by the rule that no task edits another
  task's output. A broken join means the world is wrong, and the world gets fixed and regenerated.
- **Format discipline.** Markdown is the easy way out and is a failed deliverable everywhere except
  documentation. The leak scanner checks for `.csv` files that are secretly Markdown tables.
