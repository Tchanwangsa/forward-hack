# Asteria evaluation set — the answer key

> **Private. Never ingested by the product. Never copied into `mock-company/`.**
> Everything here states what is true about the fictional world. A run that can read this directory
> is not being measured.

**What this is.** The scored answer key that turns the Asteria mock dataset from a pile of plausible
files into a metric. Five JSON files say what is true; [`SCORING.md`](SCORING.md) says how a product
run is graded against them.

---

## Why this lives outside `mock-company/`

[`MOCK-DATA.md`](../../../MOCK-DATA.md) is explicit: *evaluation is derived after source generation
and kept separate from product inputs.*
[`GENERATION-CONTRACT-V0.md` §9](../GENERATION-CONTRACT-V0.md) makes it a build rule — the freeze
step greps `mock-company/` for private identifiers (`EMP-`, `ORG-`, `CON-`, `SITE-`, `UNIT-`,
`EVENT-`, `LOT-0`) and for evaluation vocabulary, and a hit fails the build.

The reason is simple and it is not tidiness. If the answer key sits inside the tree the product
ingests, then entity resolution is a `grep`, the cohort is a lookup, and the metric measures nothing.
Every file here would fail that scan on purpose: `entity-truth.json` alone contains 900 serial →
`UNIT-…` mappings.

The same rule applies downstream. Do not paste an excerpt into a ticket that a product run can read,
do not mount this directory into an agent's workspace, and do not let a "helpful" context loader pick
up `plan/` alongside `mock-company/`.

---

## The files

| File | What it holds | Rows |
|---|---|---|
| [`entity-truth.json`](entity-truth.json) | every source identifier → private entity id, in 14 classes: email addresses, shared mailboxes, Slack user ids, support user ids, CRM account and contact ids, ERP customer numbers, organisation and site name forms, device serials and the mangled ways they are written, patch lots, component lots, technician name forms. Plus the merge traps, the split traps, the attribution traps, and the cases whose correct answer is **ambiguous**. | 1,325 identifiers |
| [`event-truth.json`](event-truth.json) | source records → world events. 2,500 source keys; the 28 multi-channel merges that must happen; the 18 near-duplicate pairs that must **not**; the two demo journeys with every arrival, every awareness event and the serial as each system wrote it. | 2,500 + 28 + 18 |
| [`field-truth.json`](field-truth.json) | per complaint, the defensible value of each mandated field, and for every empty one whether the honest state is `explicitly_unknown` or `not_yet_investigated`. The two demo complaints are broken out field by field with verified locators. | 68 complaints |
| [`clock-truth.json`](clock-truth.json) | per (event × device × jurisdiction): the governing awareness event, the computed due date or the reason there is none, the rule version, and how much the answer moves with the timezone it is read in. Plus four findings that are in the data by accident. | 21 obligations |
| [`trend-truth.json`](trend-truth.json) | the affected cohort, its true hazard, monthly exposure, every plausible cohort cut ranked per denominator basis, and **eight** labelled negatives — the seven designed confounders plus the denominator reversal that was discovered rather than designed. | 8 negatives, 7 rankings |
| [`SCORING.md`](SCORING.md) | the metric: eight measure groups worth 1,000 points, the fabrication penalties, and three reference profiles. | — |

Every file carries a `_provenance` block naming the world version it was derived from, the repo
commit at build time, and the warning above.

---

## How to use it

**To grade a run.** Read [`SCORING.md`](SCORING.md). Confirm first that the run had no access to
`plan/`; then export the run to the shape in §2 of that document and score the eight groups. Report
the group scores and the penalty list, never the bare total — the whole point is which half of the
ledger the score came from.

**To answer one question.** Each file is keyed the way you would ask it:

```bash
# who is this address?
jq '.classes.person_email_address[] | select(.identifier=="f.marsh@northbridgehealth.org.au")' entity-truth.json

# does this pair merge?
jq '.near_duplicates_that_must_not_merge[] | select(.pair[0]=="FB-2025-0033")' event-truth.json

# what is the honest state of this field?
jq '.complaints[] | select(.complaint_no=="CMP-2026-0034") | {explicitly_unknown, not_yet_investigated}' field-truth.json

# what is the deadline, and is there one at all?
jq '.obligations[] | {vig_no, jurisdiction, due: .computed.due_date, why: .correct_answer.must_state}' clock-truth.json

# where should the true cohort have ranked?
jq '.cohort_ranking | to_entries[] | {basis: .key, rank: .value.true_cohort_rank_among_rivals}' trend-truth.json
```

**To rebuild.** Deterministic, from `world.json` plus the frozen sources:

```bash
python3 tools/eval/build_eval.py      # rewrites the five JSON files
python3 tools/eval/spotcheck.py       # 12 claims re-checked against the files they name
uv run --directory tools/clock pytest # the clock implementation the deadlines came from
```

The builder reads `mock-company/` and never writes to it. Rebuild whenever `world.json` or the
sources change: **a stale answer key scores a correct product as failing**, which is worse than
having no answer key at all.

---

## How the truth was established

Three layers, in this order:

1. **The world.** `world.json`'s private `eval` block is the generator's own record of what it built.
   It is the starting point, not the finish line.
2. **Recomputation.** Anything the world asserts as a number is recomputed here from the events, and
   several sets are widened. The near-duplicate set is recomputed at the feedback-event level over a
   30-day window rather than taken from the world's shorter list; registration coverage is
   recomputed from `installed-base/*.csv` alone and lands on 70.3% → 58.4%, against the world's
   70% → 58%.
3. **Verification against the rendered sources.** Every identifier claim carries an occurrence count
   and up to three locators, produced by extracting the text of all 1,677 readable files in
   `mock-company/` — including inside `.docx` and `.xlsx` containers and through `pdftotext`. A claim
   that the sources do not support is marked, not asserted.

That third step changed several answers. See "what could not be established" below.

---

## Two things this set records that the plan did not predict

**The denominator reversal (`trend-truth.json → denominator_reversal`, labelled negative C8).**
The aggregate PulseOne complaint rate is flat on `active_installed_base` and on
`units_distributed_in_period`, and trends upward on registered units — because registration coverage
falls from about 70% to about 58% across the window while shipments accelerate. The trend is in the
denominator, not in the device. It was **discovered during generation, not designed**: the PMS
renderer measured complaints per registered unit and refused to reproduce the flatness the brief
asserted. The brief was wrong. It is scored as a labelled negative — a product that reports a rising
trend without naming its denominator basis loses marks, and one that notices the coverage decline
gains them.

**The wrong regulatory citation (`clock-truth.json → findings_the_product_should_surface`,
FIND-01).** Four Australian TGA vigilance determinations cite **EU MDR Article 87(7)** in their
rationale, four carry the EU clock class *Serious incident, 15 days (MDR Art. 87(3))* on a TGA row,
and all seven AU records cite MDCG 2023-3 Q15 to justify the governing awareness event.

**This was not planted.** It emerged from generation and was found while diagnosing the
cross-jurisdiction divergence check; it is kept because it is realistic, and because
[`REGISTER-SHAPES-V0.md` §4.7](../../../REGISTER-SHAPES-V0.md) records FDA citing a manufacturer
under 21 CFR §803.17(a)(2) for a procedure that *"combined language from the requirements of other
regulatory or competent authorities with the requirements in 21 CFR Part 803 in a manner that will
result in incomplete, inadequate, or even non-reporting."* This is that defect in the other
direction. No later reader should believe we designed it. Three smaller findings sit beside it
(FIND-02 to FIND-04) and were all found while building this set.

---

## What could not be established from the sources

These are recorded as ambiguous or excluded rather than guessed, and they are as much a part of the
answer key as the things that resolved cleanly.

| | What | Treatment |
|---|---|---|
| AMB-01 | `biomed@schg.com.au` is used by two biomedical engineers at two sites | The address resolves to **ambiguous**. Per message it is decidable from the signature, and all 7 outbound messages are resolved in `attribution_traps[].per_message_truth`. |
| AMB-02 | `SN-4417` in the St Anne's Ward thread | **Ambiguous, resolve only at a human gate.** The ward, the site and the software version all point at `SN-4471`; the digits point at a real unit at another hospital in another country. The true referent is `SN-4471`; a product that adopts either silently is wrong. |
| AMB-03 | Peter Kowalski's site | **Context-dependent**: SITE-02 before 2025-11-15, SITE-01 after. A single current-site answer is wrong for half the records. |
| AMB-04 | `date_received` for `CMP-2026-0034` | Four arrivals, three defensible. `2026-06-12` with the alternatives disclosed; any single date with no disclosure scores zero whichever it is. |
| AMB-05 | `mei-ling.tan@asteriamedical.com.au` | The full address is **nowhere in the sources**. It survives only as the clipped string `mei-ling.tan@asteriamedical.co` in one PDF table cell, so the roster's two-address trap for EMP-04 is degraded and is excluded from scoring. |
| — | 19 site name forms and 1 organisation form | In the world's alias table; **no renderer used them**. Flagged `present_in_sources: false` and excluded. |
| — | 116 device units | Manufactured, never dispatched, so they appear in no customer-facing source. Not findable, excluded from recall. |

---

## Related

- [`../PRIVATE-WORLD-V0.md`](../PRIVATE-WORLD-V0.md) §4 — the specification this set implements
- [`../roster.md`](../roster.md) — the traps and the scored questions
- [`../GENERATION-CONTRACT-V0.md`](../GENERATION-CONTRACT-V0.md) — identifier schemes and the no-leakage rule
- [`../../../REGISTER-SHAPES-V0.md`](../../../REGISTER-SHAPES-V0.md) §5.5 grain invariants, §11 required imperfections
- [`../../../MOCK-DATA.md`](../../../MOCK-DATA.md) — the evaluation plan this set answers to
- [`../world/SCHEMA.md`](../world/SCHEMA.md) — the world file these truths were derived from
- [`../../../../tools/eval/`](../../../../tools/eval) — the builder, the source index, and the spot-check
