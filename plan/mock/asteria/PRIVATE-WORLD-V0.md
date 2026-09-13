# Asteria Private World — V0

> **Private generator state — never ingested by the product. Never rendered into a source record.**
> This file contains the physical truth behind the fictional company: what actually broke, why,
> and what else was going on that looks similar but is not. The product must reach its own
> conclusions from `mock-company/` alone.

**Who may read this.** The world simulator, to generate events at the right rate against the right
units. The evaluation task, after the freeze. **No source renderer.** A renderer that knows the root
cause writes records that are plausible only because the answer is known — which
[`MOCK-DATA.md`](../../MOCK-DATA.md) forbids and which produces a demo that proves nothing.

---

## 1. What actually happened

### The physical cause

PulseOne hardware revision **H2.1** was introduced in December 2025 as a minor manufacturing
revision — a second-source communications module after the original supplier extended lead times.
The replacement module is electrically equivalent on paper. Its antenna-matching network is
marginally out of tolerance at the warm end of its operating range.

On its own this produces nothing. It becomes observable only in combination:

```text
  H2.1 comms module          marginal antenna match at elevated temperature
            +
  software ≥ 1.2.0           more aggressive radio power-save duty cycle
            +                (released 2026-01-20 for battery life)
  warm ward / patch at
  the far side of the bay    link budget already thin
            ↓
  intermittent loss of the patch link, typically 20–90 seconds,
  self-recovering, sometimes raising a "signal lost" alert and
  sometimes simply showing stale readings until it reconnects
```

The self-recovery is what makes it hard. By the time a nurse looks, the unit is working. By the time
a technician tests it on a bench at 21 °C, it passes. **Most service records for affected units say
"no fault found", and that is a truthful technician observation, not a cover-up.**

### The population

| | |
|---|---|
| Affected units | H2.1 units built with comms module lot `CM-4412` — roughly **185 of 460** H2.1 units |
| Becomes possible | 2026-01-20, when software 1.2.0 begins rolling out |
| First observable | mid-February 2026 |
| Rate | on affected units on 1.2.0+, roughly **1 reportable-ish occurrence per unit per 9 months** — most are never reported at all |
| Unaffected | all H1, all H2, H2.1 units built with the original module lot, and any unit still on 1.1.x |

### Why it is genuinely ambiguous

The device is explicitly not intended to be the sole way staff detect deterioration
([`products.md`](products.md)); it sits between routine nurse observations. A 40-second dropout on a
general post-surgical ward is, in most cases, clinically nothing. In one case in the window a patient
deteriorated during a window that included a dropout, and **nobody can establish whether the dropout
contributed** — the nurse observation round was also late that evening.

That ambiguity is the point. It is what makes reportability a judgement call rather than a lookup,
what makes `reportable = uncertain_reporting_anyway` (MDR Art. 87(7)) the *correct* state rather than
a fudge, and what lets the same facts land differently under 21 CFR 803 and MDR Art. 87 with two
defensible written rationales.

### What the company does *not* know at freeze

As at 2026-09-01 Asteria has **not** connected the dots. Internally the position is:

- Support believes there is a wireless-range problem in some wards and has been advising customers to
  move the bedside unit closer.
- Service believes it is a patch-application issue, because the units test clean.
- Engineering opened a firmware ticket about power-save aggressiveness in June and it is unresourced.
- Quality has 9 separate complaints that nobody has compared against hardware revision.
- Nobody has joined comms module lot to serial to software version to ward temperature, because that
  join spans four systems and no one person can see all four.

**This is the value proposition, and it must be true of the data rather than asserted by it.** The
join is available in the sources. It has simply never been made.

---

## 2. Confounders — mandatory, not decoration

If the planted cause is the only cluster, the product finds it by accident and the metric is
meaningless. The world must contain other things that look like signals and are not, and one thing
that looks like noise and is real.

| # | Confounder | Why it matters |
|---|---|---|
| C1 | **Charging practice.** Three sites report "battery does not last a shift". Cause is wards not docking units between patients. Clusters by site, not by revision. | A site-clustered cluster that is a training issue, not a device issue |
| C2 | **Adhesive failures in summer.** PulsePatch lifting reports spike Dec–Feb across AU. Real, seasonal, lot-independent. | A seasonal pattern with a plausible-but-wrong lot hypothesis attached |
| C3 | **One genuinely bad patch lot.** `PP72-2541C` has a real sterile-pouch seal problem — 11 reports, one NC, one supplier CAPA, closed May 2026. | A *real* signal on the other product family, correctly handled, so the product must not claim credit for finding it |
| C4 | **Docking connector damage.** 14 service jobs, all mechanical, all one site, caused by a trolley design. | High service volume that is not a product defect |
| C5 | **A 1.1.1 display-freeze bug.** Real, fixed in 1.2.0. Complaints about it *decline* exactly when the planted issue starts rising. | The two curves cross. A naive trend on "PulseOne complaints, all causes" shows **flat**. |
| C6 | **Reporting-rate artefact.** Support hires EMP-06 in Nov 2025 and ticket volume rises 30% with no change in underlying events. | Denominator discipline: a rise in reports is not a rise in events |
| C7 | **Two sites never report anything.** SITE-08 and SITE-12 have units and silence. | Absence of complaints is not absence of problems |

**C5 is the sharpest.** It means the honest finding is only visible when the analysis is cut by
hardware revision and software version — the cohort key in
[`REGISTER-SHAPES-V0.md` §7.1](../../REGISTER-SHAPES-V0.md). An aggregate trend line hides it
completely. That is a real PMS failure mode and it is worth more than a cluster anyone could see.

---

## 3. The demo journey's raw material

[`REGISTER-SHAPES-V0.md` §9](../../REGISTER-SHAPES-V0.md) specifies the beat. These are the world
events that produce it. The world generates them; no renderer is told they matter.

| World event | When | Who knew | Becomes |
|---|---|---|---|
| Dropout during post-op monitoring, SITE-13 Dublin, `SN-4471`, sw 1.2.1 | Fri 2026-06-12 ~16:20 IST | Ward staff | the occurrence |
| CON-25 emails EMP-10 (sales, AU) directly | Fri 2026-06-12 18:40 AEST | EMP-10 — `any_employee` | **US 30-day clock starts. §803.53(a) 5-work-day does not.** |
| EMP-10 forwards to `support@`, no comment | Mon 2026-06-15 08:55 AEST | EMP-04 — `mgmt_over_reg_sci_tech` | the 5-work-day clock becomes possible |
| Support creates `TKT-####` | Mon 2026-06-15 09:10 AEST | EMP-05 | `date_received` candidate #2 |
| CON-26 (biomed, same site) emails `service@` about the same unit, writes `SN-4417` | Tue 2026-06-16 | EMP-07 | the transcription conflict, and channel #3 |
| CON-38 (EU AR) is copied by the site directly | Fri 2026-06-12 | `authorised_representative` | **EU awareness predates Asteria's** |
| EMP-02 opens the complaint record | Wed 2026-06-17 | `ae_collection_duties` | `date_received` candidate #3 |

Four awareness events, three candidate received-dates, two serials, one occurrence, two jurisdictions.
None of it is manufactured: each step is what that person would ordinarily do.

`SN-4417` is a real H2.1 unit at **SITE-06 Southern Cross Randwick** — a different country, a
different customer, no open issue. A resolver that silently picks it produces a complaint against the
wrong hospital's device. This is the single best argument in the product for a human gate.

---

## 4. Evaluation ground truth

Derived **after** the freeze, stored at `plan/mock/asteria/eval/`, never inside `mock-company/`.

| Set | Content |
|---|---|
| `entity-truth.json` | every source identifier → private entity ID, with the ambiguous ones flagged ambiguous rather than resolved |
| `event-truth.json` | source records → world events, including the three-channel merges and the near-duplicates that must **not** merge |
| `field-truth.json` | per demo complaint: the defensible value of each mandated field, plus the fields whose honest state is `explicitly_unknown` |
| `clock-truth.json` | governing awareness event and computed due date per jurisdiction, with the rule version |
| `trend-truth.json` | the affected cohort, its true rate, and the seven confounders as labelled negatives |

The scored questions are in [`roster.md`](roster.md): entity-resolution precision and recall, trap
handling, attribution. Plus, from the register shapes: did the product distinguish
`explicitly_unknown` from `not_yet_investigated`, did it produce two jurisdiction rows rather than
one verdict, and did it ever fill a field without evidence.

**The honest failure this dataset is designed to permit.** If the product cuts the trend by hardware
revision and software version, it finds something real. If it does not, it finds a flat line and
reports a flat line — which is also correct, and which we must be willing to show.
