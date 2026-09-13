# PMS — the domain note

**Purpose.** The minimum domain a reader needs to judge whether the product's shape is legitimate. This is not a compliance engine to be implemented — it is the justification for three design decisions: **indicator plus pre-committed threshold, over a computed denominator** (§2); **capture as a feedback-completeness obligation rather than a convenience** (§1); and **recommending a CAPA while leaving its execution alone** (§3.2).

**Standing caveat.** ISO 13485 is copyrighted. Clause numbers and titles are stated; requirement text is paraphrased. EU MDR text is public and quoted.

---

## 1. What PMS is

Post-market surveillance is the planned, continuous activity of watching a device that is already in the field and deciding whether anything about its real-world behaviour has changed.

It is **not** a reaction to a single complaint. It is an aggregation layer that sits above the operational registers, reads them on a schedule, and produces two things: periodic reports, and signals that something warrants a look. It also, if it is honest, has to reach *beneath* those registers — because the registers only contain what somebody found time to write down.

The five clauses that survive the cut:

| Clause | What it requires | What it justifies here |
|---|---|---|
| ISO 13485 §8.2.1 — Feedback | Gather data from production and post-production, as a documented process, and feed it into risk management and analysis. *All* feedback, not only the subset that turns out to be a complaint. | Tier 1 (capture) and tier 2's WF 1 — every source, not just the complaint inbox. |
| ISO 13485 §8.2.2 — Complaint handling | Complaints are recorded, evaluated, and investigated, with documented justification when they are not investigated. | The Complaint Register as a record with a lifecycle of its own — see §3.1. |
| ISO 13485 §8.4 — Analysis of data | Determine, collect, and analyse data demonstrating QMS suitability and effectiveness, including **characteristics and trends of processes and product**. | Tier 2's WF 2 exists at all. |
| ISO 13485 §8.5.2 / §8.5.3 — Corrective and preventive action | Act to eliminate the *cause* of a nonconformity so it does not recur (8.5.2), and to prevent one that has not yet occurred (8.5.3). Both are documented procedures, and the action taken must be proportionate. | Tier 3 — the CAPA *recommendation*, and the reason executing one is out of scope. See §3.2. |
| MDR Art. 83–88 | Plan a PMS system (83), document it in a PMS plan (84), report on it (85–86), and report a **statistically significant increase** in incident frequency or severity against a baseline **specified in the technical documentation** (88). | The indicator table, its baselines, and its pre-committed thresholds. |

Art. 88 is the load-bearing one. It says the comparison baseline must be specified *in advance*, in a controlled document. That is precisely the shape of the `Indicators & Thresholds` sheet — a product, a code, a denominator, a trailing-12-month baseline, and an escalation threshold, approved before the data arrived.

### Why capture is an obligation and not a convenience

The easy reading of tier 1 is that it saves people typing. That is not the argument, and the regulation is the reason.

§8.2.1 does not ask for a feedback *inbox*. It asks for a feedback *process*, documented, that gathers data from production and post-production activities and feeds it into risk management and into the analysis of §8.4. MDR Art. 83(2) is blunter and is public text: the PMS system must be suitable for "actively and systematically gathering, recording and analysing" relevant data on the quality, performance and safety of the device. **Actively** and **systematically** are doing work in that sentence. A process that records feedback only when a busy person finds time to transcribe it is neither.

And §8.4 asks the analysis to demonstrate the *effectiveness* of the quality management system — not the existence of one. A feedback process that can be shown to have missed 62 of 369 indicator events, 17% of what happened, has a demonstrable effectiveness problem, and it is the kind of problem an auditor can evidence directly from the company's own registers. So can a company's own trend report: the August 2026 working file is `Overdue`, noted *"Data pending from service team"*.

Two boundaries on that argument, because it is easy to overreach:

- **This is not a claim that the product makes anyone compliant.** Nothing here guarantees compliance, and a capture layer that is right most of the time is a capture layer that is wrong some of the time, at a rate somebody has to measure and a human has to catch. Every drafted row passes a human gate for exactly that reason.
- **Completeness is not the same as reportability.** Recovering a missed event tells the company something happened. It does not decide whether the event is reportable, and it starts no clock. Vigilance and reporting to regulatory authorities — ISO 13485 §8.2.3 territory — stay out of scope in full.

---

## 2. Why indicator-plus-threshold is the right shape

Three properties, none of which a raw event count has:

**A denominator.** Fifteen link-loss events is not a number you can act on. Fifteen events per 100 unit-months in service, against a baseline of 1.3, is. Art. 86(1) requires the denominator and accepts that it is an estimate — which is exactly what "patches distributed" is.

**A baseline that predates the data.** The 2.0x multiplier was committed in PMS-PLAN-001 v3.0 by a named approver. Nobody chose it after seeing the rise. This is what separates a signal from a post-hoc story, and it is why the agent can compute a breach without anyone accusing it of p-hacking.

**A cohort.** A fleet-wide rate hides everything. The same rate computed per software version, per lot, per site and per ward is what turns "IND-04 is up" into "IND-04 is up on SW 1.1.0 across three organisations". Finding the tightest cohort that still breaches is the analytical work.

The calculation is deterministic code. The model only ever *explains* a number it did not compute.

---

## 3. Product NC — what we mean, and what we don't

A **nonconformity** is non-fulfilment of a requirement. A **product NC** here means: a confirmed deficiency in a device that has been released from the organisation's control — the fleet in the field, not stock in the building.

That boundary comes from the §3.4 complaint definition, which turns on *released from the organisation's control*, and it decides everything we are not doing:

| Not in scope | Why |
|---|---|
| Production / manufacturing NCs | There is no external signal an agent can monitor. Product still in the factory is a different clause and a different team. |
| MRB and disposition of nonconforming stock | Physical product under the organisation's control. Nothing to watch. |
| Vigilance, reportability, regulatory clocks | Deliberately out. No 2/10/15-day or 5/30-day deadlines, no reportability determination, no submissions. |
| Advisory notices, FSCA, recalls | Downstream of a decision the product does not make. |
| Audit findings, training, change control, supplier quality, management review | Internal, human-only, no external signal. |
| CAPA **execution** | Tier 3 recommends opening one and drafts the argument. Running the investigation, implementing the action, verifying effectiveness and closing it are human work and out of scope. See §3.2. |

The one distinction worth keeping from the CAPA world, because it prevents a specific and common error:

| Term | ISO 9000:2015 | Means |
|---|---|---|
| **Correction** | 3.12.2 | Eliminates the *detected* nonconformity. Reflash the hub, replace the battery module. Fixes this unit. |
| **Corrective action** | 3.12.3 | Eliminates the *cause*, prevents recurrence. Fix the alert logic in 1.1.2. |

Twenty-four RMAs dispositioned "Repaired and returned" are twenty-four corrections. They are not a corrective action, and a Product NC closed on them alone is closed on the wrong thing. The register keeps them separate.

### 3.1 The complaint record — why it is not a comms-log row

§8.2.2 treats a complaint as a **record with a lifecycle**: received, evaluated, investigated or justifiably not investigated, and closed — with the justification documented when no investigation follows, and with a route to §8.2.3 reporting if the evaluation turns up something reportable. An owner, a decision, a rationale, a closure.

A row in the client communications log with `Type = Complaint` is none of that. It is a note about a conversation, typed by whoever answered the mailbox, and in this register set the `Type` column is unreliable in both directions — real complaints filed as `Technical query`, and ordinary technical queries filed as `Complaint`. A label a support inbox applies for its own filing convenience is not an evaluated record, and treating it as one produces a complaint register that is simultaneously over-populated with grumpy emails and under-populated with the complaints that matter.

So the two objects stay separate, and the boundary between them is a human gate. Tier 1 **recommends** a complaint with its reasoning and the sentences it relied on; a human classifies; the decision is a record either way, which is why `Declined` is a first-class status with a mandatory rationale. A complaint register with no declined rows is a register nobody is actually screening — the same logic as *Closed — no action* on a signal.

Two limits held deliberately. The agent never fills `Vigilance screen required (Y/N)`: the field exists to mark the §8.2.3 boundary rather than to hide it, and vigilance is out of scope. And `Complaint Description (as reported)` holds the customer's words, never a paraphrase, because the evaluation an auditor reads has to be an evaluation of what was actually alleged.

### 3.2 CAPA — recommending is legitimate, executing is out

§8.5.2 requires action to eliminate the *cause* of a nonconformity so that it does not recur, proportionate to the effects encountered; §8.5.3 requires the same logic for a nonconformity that has not yet occurred. Both are documented procedures with a review step, and both begin with someone deciding that this problem warrants one.

That decision is the only part of the CAPA world this product touches, and it is defensible for a narrow reason: **the decision turns on evidence of recurrence, and evidence of recurrence is exactly what an aggregation layer over the registers can assemble and a person cannot.** The same failure mode appearing in the incident log, the RMA register and the ward checks; a cohort that reappears two quarters after a containment; a prior NC whose disposition was twenty-four repairs and no change to the product. Assembling that argument, naming the prior action and stating why it did not hold is retrieval and joining. It is the same work as the cohort slice in a signal, one level up.

Everything after the decision is judgement, engineering and verification: root cause, the corrective action itself, the preventive action, the effectiveness check. None of it has an external signal an agent can monitor, and an effectiveness check drafted by the system whose analysis prompted the CAPA is a circularity nobody should accept. So tier 3 stops at a recommendation, and the CAPA Register's execution fields are left for a human — see [`REGISTERS.md`](REGISTERS.md) §4.3.

One consequence worth stating plainly: a recommendation is not a finding, and `Declined` and `Deferred` are correct outcomes with rationales, exactly as on a signal or a complaint. A tier that recommends a CAPA on every recurrence it can construct an argument for is as useless as one that recommends none.

---

## 4. Vocabulary that matters

| Term | Means here | Common error |
|---|---|---|
| Feedback (§8.2.1) | All post-market information, from any source | Treating only complaints as feedback |
| Feedback completeness | Whether the process actually gathered what happened — measurable, and measured here at 53% | Assuming a register that exists is a register that is complete |
| Capture | Drafting the register row from the artifact it should have been transcribed from | Calling it data entry. The classification and the resolution are the work; the typing is not. |
| Complaint (§3.4) | Alleged deficiency in a device released from the organisation's control | Excluding usability issues — "the alarm wakes the patient" is a complaint |
| Complaint record (§8.2.2) | An evaluated record with an owner, a lifecycle and a closure rationale | Treating a comms-log row labelled `Complaint` as one |
| CAPA (§8.5.2 / §8.5.3) | Action on the cause, so it does not recur — or does not occur | Opening one per nonconformity, or calling a repair one |
| Indicator | A named, coded failure mode with an approved denominator and baseline | Confusing it with an event code's *count* |
| Baseline | The trailing-12-month rate stated in the PMS plan | Recomputing it from the current window, which defeats the point |
| Threshold | The multiplier that defines escalation, committed in advance | Choosing it after seeing the data |
| Denominator | Unit-months in service, or patches distributed | Using shipped units as a proxy for units in service |
| Signal | A breach or cluster worth a human look | Treating it as a finding. Most signals close as no action. |
| Product NC | Confirmed deficiency in released product | Using it for anything still under the organisation's control |
| Correction (ISO 9000 3.12.2) | Fixes the unit | Calling a repair a corrective action |
| Cohort | The slice a rate is computed over | Reporting only the fleet rate |

---

## 5. Where the agent sits

A PMS specialist already does all of this. The register set in the customer's own spreadsheets shows exactly how well: the August 2026 trend working file is marked `Overdue` with the note *"Data pending from service team"*, and the H1 2026 PMS report is at v0.4 with *"Reviewer on leave, due date at risk"*.

The work is not hard. It is joining eleven tables, by hand, every month, and it does not get done when the person doing it is on leave. The agent watches continuously, computes the rates the plan already specifies, and raises what breaches. The specialist decides what it means.

The harder half is upstream of that join and is not usually described as work at all: four of those tables are transcriptions, made late or not made, of things that happened in a telemetry stream, a mailbox, a ward round and a workshop. The specialist does not do that half either — the support inbox, the service bench and the ward do, in the gaps between their actual jobs, which is why 62 of 369 indicator events never got written down. Capture is the agent doing that half so that the join means something.

Every gate that decides something stays human: confirming a drafted row, classifying a communication as a complaint, promoting a signal, approving an NC, the CAPA-considered call, opening a CAPA, and anything sent to a customer.

---

## Citations

Primary sources verified September 2026.

**Standards** (clause numbers verified; text paraphrased — ISO 13485 and ISO 9000 are copyrighted)

- ISO 13485:2016 official listing — [iso.org/obp](https://www.iso.org/obp/ui/#iso:std:iso:13485:ed-3:v1:en)
- §8.2.1 Feedback, §8.2.2 Complaint handling — [13485quality.com](http://13485quality.com/iso-134852016-standard-8-2-1-feedback/), [Advisera](https://advisera.com/13485academy/blog/2017/03/21/how-to-comply-with-iso-134852016-requirements-for-handling-complaints/)
- §3.4 complaint definition — [Elsmar Cove](https://elsmar.com/elsmarqualityforum/threads/iso-13485-2016-complaint-definition-clarity.80094/)
- §8.4 Analysis of data — [13485store.com](https://13485store.com/iso-13485-requirements/8-measurement-analysis-and-improvement/)
- §8.2.3 Reporting to regulatory authorities, §8.5.2 Corrective action, §8.5.3 Preventive action — clause numbers and titles from the official listing above; requirement text paraphrased in §1, §3.1 and §3.2 and not quoted. Nothing in this product implements §8.2.3.
- ISO 9000:2015 §3.12.2 correction / §3.12.3 corrective action — [Quality Gurus](https://www.qualitygurus.com/correction-corrective-action-and-preventive-action/)

**European Union**

- MDR Art. 88 trend reporting, baseline in the technical documentation — [Medical Device Regulation](https://www.medical-device-regulation.eu/2019/07/16/mdr-article-88-trend-reporting/), [TÜV SÜD](https://de-mdr-ivdr.tuvsud.com/Article-88-Trend-reporting.html)
- MDR Art. 83–86 PMS framework, Annex III contents, Art. 86(1) denominator, and Art. 83(2)'s requirement that the system suit "actively and systematically gathering, recording and analysing" the data — [Zechmeister Solutions](https://zechmeister-solutions.com/en/blog/mdr-articles-83-86-pms-framework), [Emergo by UL](https://www.emergobyul.com/sites/default/files/2024-04/PMS-and-PSUR-Requirements-Under-European-MDR.pdf)

**Context**

- FDA QMSR, effective 2 February 2026, incorporates ISO 13485:2016 by reference — [FDA](https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr). Worth one line in a pitch: ISO 13485 is now the single correct backbone. Nothing in this product depends on it.

Deeper research on registers this product no longer implements is preserved in [`reference/`](reference/); [`REGISTERS.md` §7](REGISTERS.md#7-out-of-scope) says which parts are now out of scope.
