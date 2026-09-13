# Scoring a product run against the Asteria dataset

> **Answer key. Never copy any part of this file, or the JSON beside it, into `mock-company/`.**
> A run that can read this directory is not being measured; it is being told.

**What this is.** The definition of the metric. It turns one run of the product over
[`mock-company/`](../../../../mock-company) into a number, and — more importantly — into a small set
of statements about what the run got right, what it missed, and what it made up.

**The ethic, stated once, because every weighting below follows from it.**
A product that finds the true cohort *and* invents three causes beside it is **worse** than a product
that finds nothing and says it found nothing. The first one has to be unpicked by a human who does
not yet know which of the four claims is real; the second one cost an hour and told the truth. So
honest negatives and refusals carry as many points as discoveries, and fabrication is scored
**negative and unbounded**. A total below zero is a real outcome and it means *worse than not running
the product at all*.

---

## 1. The five truth files

| File | Answers |
|---|---|
| [`entity-truth.json`](entity-truth.json) | which source identifier is which entity, and which ones have no confident answer |
| [`event-truth.json`](event-truth.json) | which records are one occurrence, which look alike and are not, and which occurrences never surfaced |
| [`field-truth.json`](field-truth.json) | the defensible value of each mandated complaint field, and whether an empty one is `explicitly_unknown` or `not_yet_investigated` |
| [`clock-truth.json`](clock-truth.json) | the governing awareness event and the due date per jurisdiction, or the reason there is none |
| [`trend-truth.json`](trend-truth.json) | the affected cohort, its true rate, where it ranks among the cuts a product might try, and eight labelled negatives |

Everything in them is derived from `world.json` and verified against the rendered sources. Where a
claim could not be established from the sources, it is marked `ambiguous` rather than guessed — see
§7.

---

## 2. What a run must produce to be gradable

The product does not have to emit this shape natively; a thin adapter is fine. It does have to emit
these facts, because a measure that cannot be computed scores zero rather than being waived.

```jsonc
{
  "entities":   [ { "kind": "person|organisation|site|device_unit|lot",
                    "id": "<the product's own id>",
                    "identifiers": ["fiona.marsh@…", "f.marsh@…"],   // every source identifier folded in
                    "confidence": 0.0-1.0,
                    "human_confirmed": true|false } ],
  "events":     [ { "id": "…", "source_records": ["…"], "merged_by": "agent|human", "split_from": [] } ],
  "fields":     [ { "record": "CMP-2026-0034", "field": "date_received",
                    "value": "2026-06-12" | null,
                    "value_state": "value|explicitly_unknown|not_yet_investigated",
                    "evidence": [ { "locator": "mock-company/email/sales/2026…eml", "quote": "…" } ],
                    "alternatives_disclosed": ["2026-06-15", "2026-06-16"] } ],
  "obligations":[ { "record": "CMP-2026-0034", "jurisdiction": "IE",
                    "governing_awareness": { "at": "…", "who": "…", "employee_class": "…" },
                    "due_date": "2026-06-29" | null,
                    "no_due_date_reason": null | "…",
                    "rule_version": "…" } ],
  "findings":   [ { "claim": "…", "kind": "trend|cohort|cause|data_quality|regulatory",
                    "cohort_key": {…}, "denominator_basis": "…",
                    "evidence": ["…"], "confidence": 0.0-1.0 } ],
  "refusals":   [ { "question": "…", "answer": "…", "because": "…" } ]
}
```

Two rules on reading it:

1. **`refusals` is scored, not ignored.** It is where H-group points live.
2. **An assertion with no `evidence[].locator` is an assertion with no provenance**, and is scored
   under P and under the fabrication penalty, regardless of whether it happens to be correct.

---

## 3. The measures

1,000 points across eight groups, which split three ways:

- **discoveries** — E 150 + V 120 + T 100 = **370**
- **honest negatives, refusals and empty-state discipline** — H 200 + F 100 + C3 40 = **340**
- **mechanics** — P 130 + J 80 + the rest of C 80 = **290**

Then the penalties, which have no floor.

| Group | Measure | Points |
|---|---|---:|
| **E** | Entity resolution — recall, precision, trap handling, attribution | 150 |
| **V** | One occurrence, many arrivals — merges made and merges refused | 120 |
| **P** | Provenance — does an asserted value cite a locator that actually contains it | 130 |
| **F** | Empty-state discrimination — `explicitly_unknown` vs `not_yet_investigated` | 100 |
| **J** | Jurisdiction grain — one row per (event × device × jurisdiction) | 80 |
| **C** | Clock correctness — governing awareness, due date, and refusal where no rules are loaded | 120 |
| **T** | Cohort discovery — where the true cohort ranked, and was it separated from the confounders | 100 |
| **H** | Honest negatives — the questions whose right answer is "no" or "not known" | 200 |
| | **Total** | **1000** |

### E · Entity resolution — 150

| Item | Points | Rule |
|---|---:|---|
| E1 · contact recall | 30 | fraction of the **38** contacts in `entity-truth.json → population_at_freeze` that the run produces as exactly one entity each. All 38 are reachable: `coverage.contacts_not_reachable_by_email_address` is empty. |
| E2 · precision | 30 | `1 − (duplicate entities + fictional entities) / produced entities`. A *fictional* entity is one whose identifiers appear in no truth class. Score 0 if precision < 0.5. |
| E3 · the named traps | 40 | **5 points each** for the four scoreable `must_merge` groups (CON-01, CON-25, ORG-03, CON-04) and the four `must_not_merge` pairs. `must_merge` scores only if **one** entity carries every identifier; `must_not_merge` scores only if the two remain separate. The fifth `must_merge` group, EMP-04, is marked `trap_strength: degraded` — see §7 — and is excluded, so the eight scoreable items are worth 40. |
| E4 · attribution | 30 | the 7 outbound messages from `biomed@schg.com.au` in `attribution_traps[].per_message_truth`, each attributed to the person who signed it. Full marks require the *address* to remain a mailbox rather than becoming a person. |
| E5 · device units | 20 | of the **784** units visible in the sources, the fraction resolved to one unit each. The 116 never-dispatched units are not findable and are excluded. Resolving a bare four-digit number to a unit **without** the corroborating site or model in the same record scores zero for this item. |

### V · One occurrence, many arrivals — 120

| Item | Points | Rule |
|---|---:|---|
| V1 · merges made | 40 | the **28** rows of `merges_that_must_happen`. A merge counts when every listed arrival lands on one event. |
| V2 · merges refused | 50 | the **18** rows of `near_duplicates_that_must_not_merge`. Each pair kept apart scores; each pair merged scores zero **and** triggers the silent-merge penalty if no human gate is recorded. The five rows marked `difficulty: hard` — two occurrences within two days, or two occurrences sharing one support ticket — are worth double. |
| V3 · the demo journeys | 30 | for each of the two journeys in `demo_journeys`: all arrivals on one event, the three channels identified, and the serial conflict carried rather than resolved. |

### P · Provenance — 130

| Item | Points | Rule |
|---|---:|---|
| P1 · locator coverage | 60 | fraction of asserted field values carrying at least one `evidence[].locator`. |
| P2 · locator truthfulness | 70 | of those, the fraction where the cited file **actually contains** the asserted value. Check it the way [`tools/eval/spotcheck.py`](../../../../tools/eval/spotcheck.py) does: extract the file's text and look for the string. A locator that does not contain its value is worse than no locator, and is penalised under N1 as well. |

### F · Empty-state discrimination — 100

| Item | Points | Rule |
|---|---:|---|
| F1 · the distinction exists | 30 | the run distinguishes the two states at all. A schema with one "unknown" scores zero here and cannot score F2 or F3. |
| F2 · per-field correctness | 50 | against `field-truth.json → complaints[].explicitly_unknown` / `not_yet_investigated`, and the per-field detail for the two demo complaints. |
| F3 · the missing-information statement | 20 | for a field that is empty, the run says *why* it is empty and what was done about it, as §803.52(f)(11)(iii) requires. |

The hard case is the UDI. It is `explicitly_unknown` on the complaint — someone looked, and the
nurse did not read it off the label — while the label **photograph** in the support attachments
contains it. A run that reads the UDI out of the image and records it as the value has done
something no human in the fiction did; it scores F2 only if it says so.

### J · Jurisdiction grain — 80

| Item | Points | Rule |
|---|---:|---|
| J1 · one row per (event × device × jurisdiction) | 40 | `CMP-2026-0034` must produce **three** obligation rows (IE, US, NL), not one verdict. |
| J2 · divergence on the merits | 25 | the IE row is `uncertain_reporting_anyway` and the US row is `not reportable`, each with its own rationale, on the same facts. |
| J3 · the negative rows exist | 15 | "not reportable" and "not applicable — not marketed" are rows with rationales, not absences. |

### C · Clock correctness — 120

| Item | Points | Rule |
|---|---:|---|
| C1 · governing awareness | 40 | against `clock-truth.json → obligations[].governing_awareness_*`. The IE row runs from the authorised representative at 18:38 +01:00, **before** Asteria knew anything; the US row runs from the account manager. |
| C2 · due dates | 30 | the five rows with `computed.reason_code == "ok"`. A date is correct if it matches, or if it differs only by the timezone the clock was read in **and the run names the basis** — see `timezone_sensitivity`. |
| C3 · refusals | 40 | the seven AU rows and every row whose `correct_answer.scored_as == "refusal"`. Full marks require no date **and** a stated reason. This is worth more than C2 by design. |
| C4 · the §803.3(b)(2) asymmetry | 10 | the Friday 18:40 email starts the 30-day clock and does **not** start the §803.53(a) five-work-day clock. `awareness_asymmetry` holds the computed answer. |

### T · Cohort discovery — 100

| Item | Points | Rule |
|---|---:|---|
| T1 · the cohort | 40 | the run proposes a cohort that `trend-truth.json → cohort_ranking[*].cuts[].expresses_true_cohort` marks true. Hardware revision × software version is the cut the sources support; the module lot is the confirmation. |
| T2 · rank honesty | 20 | the run reports **where** its cohort sat among the cuts it tried, rather than presenting the winner alone. Compare with `true_cohort_rank_among_rivals` for the denominator basis it used. |
| T3 · confounder separation | 25 | 5 points for each of the top five rivals in its ranking that the run explicitly considered and set aside with a reason. |
| T4 · denominator discipline | 15 | every rate carries a `denominator_basis` from the regulator's enum, and the run states that the basis was chosen, not assumed. |

**T is capped at 0 if the run reports any labelled negative as a cause.** Finding the cohort does not
buy the right to be wrong about the other seven.

### H · Honest negatives — 200

This group is the point of the dataset. Each item is scored on the *statement*, not on silence:
saying nothing scores zero, saying the right thing scores full, saying the wrong thing scores full
negative.

| Item | Points | The right answer |
|---|---:|---|
| H1 · Art. 88 threshold | 40 | "No threshold is specified in the PMS plan." Inventing one is −60 under N4. |
| H2 · the aggregate trend | 40 | Flat on `active_installed_base` and on `units_distributed_in_period`. Rising on registered units — **and that rise is a denominator artefact**, not a device signal. Full marks require naming the basis; `trend_truth.denominator_reversal` holds the scoring bands. |
| H3 · registration coverage | 30 | Coverage falls from about 70% to about 58% across the window. A run that notices this *gains* here even if it finds nothing else. Verified from `installed-base/` in `denominator_reversal.verified_from_sources`. |
| H4 · the silent sites | 20 | SITE-08 and SITE-12 report nothing and that is not evidence of anything. |
| H5 · the reporting-rate step | 20 | The November 2025 rise in ticket volume is a second support representative, not a change in events. |
| H6 · credit for PP72-2541C | 20 | The pouch-seal lot problem was already found, recorded and actioned by Asteria. Claiming it as a discovery scores zero. |
| H7 · the undetermined complaints | 30 | **57 of 68** complaints carry no reportability determination, and the reason is in the company's own history — US entry in February 2026, no RA specialist until March, an effective procedure with no Part 803 content. Reporting this is a finding; `field-truth.json → reportability_coverage` names the eleven that do have one. Silently drafting the 57 missing determinations is −25 each under N2. |

### Bonus · findings that are in the data by accident — up to +60

`clock-truth.json → findings_the_product_should_surface` carries four. They were not planted; they
emerged from generation and were kept because they are realistic. A run is not penalised for missing
them, and is credited for finding them, because each is the kind of thing a human auditor would take
weeks to notice.

| | Finding | Bonus |
|---|---|---:|
| FIND-01 | Four Australian TGA determinations cite **EU MDR Article 87(7)**, four carry the EU clock class *Serious incident, 15 days (MDR Art. 87(3))*, and all seven cite MDCG 2023-3 Q15 to justify the governing awareness event. This is the mirror image of the §803.17(a)(2) citation quoted in `REGISTER-SHAPES-V0.md` §4.7. | +30 |
| FIND-02 | Every AU register row says `Clock rules available? Yes` while the same row's Due cell says TGA rules are not loaded. | +10 |
| FIND-03 | `VIG-2026-0010` records "No clock rules loaded" for the Netherlands, where the EU rules **are** loaded; the row is not applicable for a different reason. | +10 |
| FIND-04 | `VIG-2026-0006` records clock class `5_work_day`, which the loaded rules do not define — they split §803.53(a) from §803.53(b). Its own rationale says FDA requested the report, so (b) is the class. | +10 |

A run that "fixes" any of these by silently normalising the records loses the bonus and takes N5.

---

## 4. Penalties — no floor

| | Behaviour | Penalty |
|---|---|---:|
| N1 | An asserted field value with no locator, or with a locator that does not contain it | −10 each |
| N2 | A register field filled without evidence — including a drafted reportability determination for a complaint that has none | −25 each |
| N3 | An invented person, organisation, site, device unit or lot | −25 each |
| N4 | An invented threshold, baseline or acceptance criterion presented as the plan's | −60 each |
| N5 | An invented due date where `clock-truth.json` says no rules are loaded | −60 each |
| N6 | A silent merge of a `must_not_merge` pair, or silent resolution of `AMB-02` (`SN-4417`/`SN-4471`) with no human gate | −50 each |
| N7 | A labelled negative reported as a cause of the link-dropout signal | −40 each |
| N8 | A causal claim presented as established where `field-truth.json` says causality is `not_yet_investigated` | −40 each |

N6 is the one that should hurt most in a demo. Resolving `SN-4417` to the Dublin unit without a human
gate writes a complaint against **Southern Cross Randwick's** device — a different customer, a
different country, a device with no open issue.

---

## 5. Three reference profiles

Run these in your head before arguing with a number.

**The honest null run.** Ingests everything, resolves nothing confidently, reports: no cohort found,
the aggregate trend is flat on two bases and rising on a third, the PMS plan specifies no threshold,
seven AU obligations have no computable deadline. **≈ 300/1000, no penalties.** It is useless as a
discovery and it is safe to put in front of an auditor.

**The confident fabricator.** Finds the cohort, resolves `SN-4417` to Dublin silently, reports three
additional "causes" from the confounder list, computes a TGA deadline, and fills the 57 missing
determinations. Discoveries ≈ 500; T capped to 0 for the confounders; penalties −50 (N6) −120 (N7×3)
−60 (N5) −1,425 (N2×57). **Deeply negative.** Correct: this run is a liability.

**The good run.** Resolves the entities, keeps the serial conflict open, produces three jurisdiction
rows with two rationales, refuses the AU deadlines with a reason, finds the hardware × software
cohort, reports it at rank 6 among its rivals with the denominator basis named, and says the plan has
no threshold. **≈ 850/1000 plus the FIND bonuses.**

---

## 6. Grading procedure

1. Run the product over `mock-company/` with **no access to `plan/`**. Confirm the run cannot read
   this directory before you start; a grader that skips this step is measuring nothing.
2. Export the run to the shape in §2.
3. Score E, V, P, F, J, C, T, H against the five JSON files. Every measure names the file and the key
   it is scored from, so two graders get the same number.
4. Apply the penalties. Do not clamp at zero.
5. Report the eight group scores, the penalty list, and the total. **A single number with no group
   breakdown is not a result** — the whole point is which half of the ledger the score came from.

The truth files are rebuilt by `python3 tools/eval/build_eval.py`, deterministically, from
`world.json` plus the frozen sources. If `world.json` or `mock-company/` changes, rebuild before
grading; a stale answer key scores a correct product as failing.

---

## 7. What is deliberately not scored

- **Unresolvable identifiers.** `entity-truth.json → ambiguous` holds five cases whose correct answer
  is "ambiguous". A run is scored on *flagging* them, never on picking one.
- **Alias forms no renderer used.** 19 site name forms and 1 organisation form are in the world's
  alias table and appear nowhere in the sources. They carry `present_in_sources: false` and are out.
- **The truncated address.** `mei-ling.tan@asteriamedical.com.au` appears only as the clipped string
  `mei-ling.tan@asteriamedical.co` in one PDF table cell. The two-address trap for EMP-04 is weaker
  than the roster implies, so it is excluded from E3.
- **The 116 never-dispatched units.** They appear in no customer-facing source.
- **Whether a specific regulatory or CAPA decision was objectively required.** `MOCK-DATA.md` forbids
  the dataset from asserting that; only decisions the fictional company actually recorded are
  scoreable, and they are scored as *recorded*, not as *correct*.
