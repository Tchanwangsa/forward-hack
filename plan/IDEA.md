# The product

## One line

**An agent that fixes the registers before it analyses them: five capture bots watch the sources a PMS register is transcribed from and draft the rows nobody wrote, then the indicator engine runs on a register that is actually complete, then a third tier asks whether the same thing has happened before.**

Not a compliance engine. Not an eQMS. A colleague who takes the minutes, and only then does the maths.

**The registers are not the input. They are the output.** That is the whole argument, and [`ARCHITECTURE.md`](ARCHITECTURE.md) is the spine that states it in full.

## The problem, in measured numbers

Real post-market surveillance analysis fails, and it does not fail at the arithmetic. It fails because the logs it runs on are incomplete and everyone involved already knows it.

In the register set this product is built against ([`mock-company-v2/`](../mock-company-v2/README.md), ground truth in `mock-company-v2/ground-truth/`):

| The world | The register | Gap |
|---|---|---|
| 369 indicator events actually happened | 307 reached the incident log | **62 events — 17% — were never written up at all** |
| 307 logged rows | 197 carry the correct event code | 27% blank, 9% wrong |
| — | — | **The register correctly identifies 53% of what happened** |

And on the rows that do exist, the fields the analysis needs are the fields nobody filled in: `SW Version at Time` blank on 35% of incident rows, `SW Version` blank on 48% of RMAs, `Patch Lot` blank on 51% of ward checks, `Action Taken` blank on 66% of them, `Contact Role` blank on 46% of comms rows.

The sharpest instance is inside the primary story. Of the fifteen `ALERT-FALSE` events on SW 1.1.0 in the live 90-day window, **two** carry a correct `SW Version at Time`. The cohort that *is* the finding is not recoverable from the register as a human left it. No amount of analytical cleverness gets it back. Somebody has to go and read the telemetry.

The customer's own spreadsheet says so out loud: the August 2026 trend working file is `Overdue`, noted *"Data pending from service team"*; the H1 2026 PMS report is at v0.4, noted *"Reviewer on leave, due date at risk"*; a troubleshooting row reads *"Ward busy, check incomplete."* The business case is already written, in the file the analysis was supposed to read.

## Who it is for

**Primary user:** the PMS or quality specialist at a small or medium medical-device company — one person, sometimes half a person, responsible for knowing whether anything has changed about a product that is already in hospitals.

**Secondary, and new with tier 1:** the people whose rows the bots draft — the support inbox, the service workshop, the clinical support staff who walk the wards. They do not want a surveillance tool. They want the row to already be there when they open the spreadsheet.

**Supporting users:** the quality manager who signs the NC, the clinical reviewer who owns the alert-related indicators, the service lead whose RMA data feeds it.

## The job it does

A device manufacturer with a few hundred units in the field already has a PMS plan. That plan already names the failure modes it watches, the denominator for each, a baseline, and a threshold that triggers escalation. All of that was approved, in a controlled document, by a named person. None of it is the hard part.

The hard part is in two halves, and only one of them is usually named.

**The named half** is the monthly work of computing it: joining eleven tables — hub inventory, patch allocations, the incident log, the RMA register, the troubleshooting log, the communications log, the complaint register — none of which share an identifier, all of which spell the customer's name differently. The agent does that join every night and shows its working.

**The unnamed half** is that four of those tables are human transcriptions of something that happened somewhere else, and the transcription is late, partial, or was never made. A hub going quiet at 03:40 is a telemetry event that somebody was supposed to turn into an incident row. A nurse unit manager describing night-time false alerts in a Tuesday site visit is a comms row somebody was supposed to file. A technician measuring a battery at 61% of nominal wrote it in a work order, not in the register the rate is computed from.

Tier 1 does that half. It watches the source, resolves the entities, classifies the event, drafts the row, and a human confirms it. Then tier 2's join is a join over data that reflects the world.

## Where it sits

It does not replace the customer's systems of record. It reads the sources *behind* them, drafts into the five capture-fed registers, and system-maintains four workflow registers in Postgres.

```text
UPSTREAM SOURCES                     the artifacts a register is transcribed from
telemetry stream · mailboxes · meeting transcripts · service work orders · ward rounds
        │            │              │                      │                 │
        ▼            ▼              ▼                      ▼                 ▼
TIER 1 · CAPTURE   outage watch · inbox triage · meeting scribe · RMA capture · field-check nudge
        observe ─► resolve ─► classify ─► draft the row ─► HUMAN CONFIRMS
        │
        ▼  registers now actually complete — 53% coverage becomes real coverage
CAPTURE-FED REGISTERS                REFERENCE
incidents · returns · checks         Customer Orgs & Hubs — 250 hubs, both denominators
comms · complaints                  PMS Plan — 7 indicators, baselines, thresholds
        │                                     │
        ▼                                     ▼
TIER 2 · ANALYSIS → NC     Watch · Measure · Raise · Investigate · Record
        │
        ▼  recommend: file a Product NC?                    ◄── HUMAN GATE
TIER 3 · CAPA              overlap across registers · recurrence · prior NCs that didn't hold
        │
        ▼  recommend: open a CAPA?                          ◄── HUMAN GATE
        │
        ▼
Agent registers                              React dashboard
Signal · Product NC · CAPA · Action Log      Capture queue · Fleet · Indicators
                                             Signal queue · NC drafts
```

Three parts are first-class, not accessories:

**The telemetry API.** PulseOne hubs are network-connected and already report to a clinical dashboard, which is what makes this physically plausible. The hub emits an event code that *is* the indicator's internal code, so telemetry arrives pre-classified. The reframe strengthens it rather than displacing it: the stream is now **tier 1's primary source as well as tier 2's**, because it is the one source that is machine-truthful about the field nobody fills in. It knows the SW version at the moment of the fault, and it knows about the 44 hub-code events that never reached the incident log at all. See [`TELEMETRY-API.md`](TELEMETRY-API.md).

**The dashboard.** Five screens, and the new one is the important one: the **capture queue** — drafted rows and completions awaiting confirmation, grouped by bot, with the artifact shown beside the draft so a reviewer can confirm without leaving the screen. Then Fleet, Indicators, Signal queue, NC drafts. See [`DASHBOARD.md`](DASHBOARD.md).

**The Agent Action Log.** Every classification, calculation, draft and email the agent produced, across all three tiers, with the human's verdict on it. This is what makes the rest believable, and with tier 1 it gains the most useful column in the product: `Human verdict = edited` on a capture draft is the honest measure of whether a bot is any good, and it names how it was wrong.

## The three tiers

| Tier | What it does | Unit of work | Output | Human gate |
|---|---|---|---|---|
| **1 · Capture** | five bots, one per source, drafting into one register each | one artifact → one or more drafted rows | a drafted register row, or a completion for a blank cell | confirm each drafted row — **always level 3, never automatic** |
| **2 · Analysis → NC** | the indicator engine over the now-complete registers | one indicator × cohort × window | a Signal, then a drafted Product NC | promote signal → NC; approve/close NC |
| **3 · CAPA** | recurrence and overlap across registers and across time | one failure mode across registers and time | a CAPA recommendation | the CAPA-considered decision, and opening one |

Tier 1 is detailed in [`CAPTURE-AGENTS.md`](CAPTURE-AGENTS.md), tier 3 in [`CAPA.md`](CAPA.md). Tier 2 is the five workflows, unchanged in substance and specified in [`DIAGRAMS.md`](DIAGRAMS.md):

| # | Tier-2 workflow | Trigger | Autonomy |
|---|---|---|---|
| 1 | **Watch** | any new event in any source | Automatic |
| 2 | **Measure** | nightly, and on every new event | Automatic, deterministic |
| 3 | **Raise** | a rate crosses its threshold, or a cluster appears | Draft |
| 4 | **Investigate** | a human opens a signal | Recommend / Execute with approval |
| 5 | **Record** | a human promotes a signal | Draft, human signs |

Most events stop at Measure. That is correct behaviour: a surveillance system that raises a signal per event is as useless as one that raises none.

## Autonomy levels

Every action carries an explicit level, and it is visible in the UI.

1. **Observe** — read and organise.
2. **Recommend** — suggest a classification, a next step, a complaint, a CAPA.
3. **Draft** — prepare a register row, a record, or a message for review.
4. **Execute with approval** — act after a named user confirms.
5. **Automatic** — low-risk, pre-authorised: normalisation, entity resolution, rate calculation, the nightly run.

**Capture is level 3, always.** No capture bot is ever promoted to level 5, however good its accept rate gets. A register row committed without a human is a record the company cannot defend, and the accept rate is itself a metric worth continuing to measure.

### Gates no confidence level may bypass

- Committing any drafted register row (tier 1)
- Classifying an inbound communication as a **complaint** (tier 1 recommends, a human decides)
- Promoting a Signal to a Product NC (tier 2)
- Approving or closing a Product NC (tier 2)
- The CAPA-considered decision, and opening a CAPA (tier 3)
- Any outbound customer communication (any tier)

A capture draft rejected, a complaint declined, a signal closed as *no action*, a CAPA judged unnecessary — each is a permanent record with a named reviewer and a rationale. Never a deletion.

## What makes it defensible rather than clever

**The threshold was committed in advance.** The agent does not decide what "too high" means. A named person did, in PMS-PLAN-001 v3.0, before the data existed. MDR Art. 88 requires exactly that — see [`WORKFLOW.md`](WORKFLOW.md).

**The calculation is code, not a model.** Rates, denominators and ratios are computed deterministically and stored with their inputs. The model explains a number it did not produce.

**The denominator is real, and no capture bot may touch it.** Unit-months in service comes from install dates and unit statuses in the hub inventory; patches distributed comes from lot allocations and shipped dates. Neither is typed by a human, and neither is writable by an agent — a bot that can move the denominator can move every rate in the product.

**The capture layer is scored against ground truth, not against whether a human clicked accept.** This is the fourth point and it is the one that stops tier 1 being a demo trick. A tired reviewer accepting everything scores identically to a perfect bot, so accept rate is reported *and* discounted: every filled field is checked against `ground-truth/capture-targets.csv`, and the headline is field accuracy and coverage lift, not the verdict. The honest limit is stated with it — on the free-text sources there is no clean recall ceiling, because "items a human would have wanted filed from this meeting" has no ground truth beyond the ones we planted, so precision leads for the transcript and ward-round bots.

**Entity resolution is plumbing, not a feature.** The registers really do say `RNH` and `Royal North Hospital`, `SN 4216` and `PO-P1-004216` and `4111`. That has to work. It is never a screen and never the pitch.

## Metrics the demo can actually show

Capture first, because it is the tier that is new and the tier whose numbers are hardest to argue with.

| Metric | Why it is measurable here |
|---|---|
| **Rows recovered** | Register rows that did not exist and should have. 62 events have no incident row; 44 of them are hub codes outage watch owns outright. |
| **Blanks filled, by column** | Per column, against the measured baselines: 35% of `SW Version at Time`, 48% of RMA `SW Version`, 51% of `Patch Lot`, 46% of `Contact Role`. |
| **Field accuracy** | Of what it filled, how much matches the world — scored against `capture-targets.csv`, not against the human's typed value. |
| **Classification accuracy** | Drafted event code vs `true_code`, broken out by source, because telemetry is easy and ward free-text is not. |
| **Accept / edit / reject** | The human verdict per bot, from the Agent Action Log. `Edited` is the useful one. |
| **Capture latency** | Artifact timestamp → drafted row, against a human baseline of median 0 days, p90 5 days *for the rows that got written at all*. |
| **Coverage lift** | The headline. Indicator events correctly represented in the registers: **53% → target**. The target is to-be-measured once the capture run is scored; its ceiling is the 44 recoverable rows plus the blanks `capture-targets.csv` marks as fillable. |
| Time from event to human assessment | Telemetry timestamp → signal raised → reviewed. All three are in the data. |
| Signals raised vs signals promoted | The precision of tier 2's judgement, visible in the Signal Register. |
| Capture-dependent signals | The Signal Register's `Capture-dependent (Y/N)` column — signals that are invisible without tier 1. On the primary story this is `Y`. |
| Events correctly attributed to a cohort | Against the events the specialist could attribute by hand. |
| Monthly analysis effort | Currently a manual multi-way spreadsheet join that is presently overdue. |

## Hackathon scope

Build order is [`ARCHITECTURE.md`](ARCHITECTURE.md) §Build order, and this list is that list:

1. **Outage watch** (telemetry → incident log). The strongest single demo: it creates rows that do not exist and fills `SW Version at Time` on rows that do. Everything downstream depends on it.
2. **Inbox triage** (mailboxes → comms log, plus a complaint recommendation). The complaint recommendation is the first place a human gate is genuinely interesting.
3. **Meeting scribe** (transcript → comms log, `Channel = Meeting`). Demos live and needs no integration story.
4. **Tier 2**, all five workflows. Lands the `ALERT-FALSE` / SW 1.1.0 finding and correctly closes the network-maintenance near-miss.
5. **Tier 3**, one convincing CAPA recommendation. Cross-register overlap on the `BATT` / H1 thread, plus a prior NC that did not hold.
6. **RMA capture** and **field-check nudge** — stubbed: the same primitive wired to a thinner source, enough to show the pattern generalises.

Plus the telemetry API underneath all of it, backfilled from the hub inventory and incident log so all 250 units have plausible history, then streaming live during the demo; and the Agent Action Log, populated throughout.

**Design only, do not build:** the React dashboard. Specify the five screens; if one gets a thin implementation it is the capture queue, because tier 1 is what gets built first.

**The honest scope risk.** Five capture bots plus two analysis tiers is a lot for a hackathon. Three built properly beats five half-wired, and the two stubs must still be visibly the same primitive — a stub that looks like a different product costs more than it saves. Tier 2 and tier 3 each need to land **once, convincingly**, on a planted story: the NC path on `ALERT-FALSE` / SW 1.1.0, the CAPA path on `BATT` / H1. Anything past that is a bonus.

**Do not attempt:** vigilance or reportability of any kind, production NCs, MRB, **CAPA execution**, audit or training modules, a general eQMS, or any claim that the product guarantees compliance.

## The demo beat

It runs in two movements, and the first one is the point.

**Movement one — capture.** A telemetry event arrives at 03:41 from a hub at Cathedral Hill running SW 1.1.0: `ALERT-FALSE`, alert dismissed in four seconds, `ward_profile_applied: false`. Nobody at the ward will write this up. Outage watch drafts the incident row — organisation resolved canonically, serial canonical, event code correct, **`SW Version at Time` = 1.1.0** — with the raw event beside it, and a reviewer accepts it in one click. In the same queue: a completion proposing `1.1.0` for the thirteen existing incident rows in that story where the column is blank or stale, and a comms row drafted from a site-visit transcript where a nurse unit manager describes night-time false alerts and never mentions a software version, because she does not know it.

**Movement two — analysis.** `ALERT-FALSE` (IND-04) is at 3.08 per 100 unit-months over the rolling 90 days, 2.80x the 1.10 baseline against a 2.0x threshold. The rise is not fleet-wide: sliced by software version, 1.1.0 hubs run **14.28** and everything else runs **1.09**, across exactly three organisations — and inside those same three sites, 1.1.0 hubs run 18.32 against 1.35 for their non-1.1.0 neighbours. It is the software, not the site.

No single source shows it. Troubleshooting rows say "1.1.0 alert logic" and "Threshold set to default not ward profile"; RMA findings on the same cohort say "Configuration reset to ward profile, no hardware fault"; client emails complain about night-time false alerts; the incident log has the events and 35% of its `SW Version at Time` column is blank. The join shows it — **and the join only works because movement one happened.** Toggle tier 1 off and the cohort collapses: two of the fifteen story rows carry a version. The Signal Register says so in one cell, `Capture-dependent = Y`.

Then two things that show judgement rather than enthusiasm. A second, deliberately innocent case — ten `HUB-OFFLINE` rows at one site inside six days, nine of them carrying a note about a hospital network maintenance window and seventeen client emails saying the same — is correctly closed as *no action*, because a system that only ever finds problems has not demonstrated judgement. And tier 3 reads across the `BATT` thread: seventeen RMA rows reading `Battery module replaced, capacity 61% of nominal`, an H1 cohort that never breaches at fleet level, and a prior signal left on *monitoring* that asked service to record measured capacity — which service then did, into a register nobody read back against the signal. That is a CAPA recommendation, and a human decides.

## Risks

| Risk | Safeguard |
|---|---|
| **A capture bot invents a row** | It may fill only fields its source evidences, and a blank is a correct answer. `SKIN` has no telemetry path at all — zero telemetry-sourced `SKIN` rows may ever exist, and one is proof of invention. `ADHESIVE` from telemetry is an inference, so it is raised as a low-confidence question, never a committed classification. Every drafted row carries `Captured From`, and a row that cannot be walked back to its artifact is a bug. |
| **A reviewer rubber-stamps the drafts** | Accept rate is not accuracy, and is never reported as if it were. Field accuracy is scored against ground truth. The queue shows the artifact beside the draft so confirming is a reading act rather than a clicking act, nothing is pre-selected, and edit rate per bot is tracked precisely because a bot with a 100% accept rate and a bored reviewer looks identical to a good one. |
| The model invents a number | Calculations are code. The model is given the result and asked to explain it. |
| A confident misclassification propagates | Low-confidence classifications go to a human as a question, not a draft; every verdict is logged; a rate is always shown with its contributing event IDs. |
| The agent raises noise | Minimum-denominator suppression, cohort tightening, episode de-duplication in capture (a hub that flaps eleven times in six days is one incident), and `Closed - no action` as a first-class outcome with a rationale. |
| Patient information in the sources | The registers hold ward and bed, never patient identity. Transcripts and emails are the new exposure and the same rule holds: ward and bed, never who is in it. |
| It becomes another eQMS | It drafts into five customer-controlled registers and system-maintains four workflow registers in Postgres. Nothing is migrated, and no source row is ever edited — a completion lives in the capture layer, and the customer's spreadsheet stays theirs. |

## Open questions

- Does the agent write proposed values back into the customer's incident log, or hold completions in its own layer? (Settled for now in favour of its own layer — see [`REGISTERS.md`](REGISTERS.md) §Provenance — but it is the decision most likely to be argued with.)
- What is the minimum denominator below which a cohort rate is suppressed?
- What confidence threshold turns a capture draft into a question instead? Too high and the queue fills with questions; too low and the reviewer is rubber-stamping guesses.
- Is one feedback register with a `Channel` column right, or does client feedback want its own file? It is one column and one workbook, not a re-architecture.
- Is the half-yearly PMS report section a real deliverable for the demo, or a stretch?
- Should the agent open a signal on a *cluster* that has not breached any threshold — and if so, what makes that defensible under Art. 88's pre-committed-baseline logic?
