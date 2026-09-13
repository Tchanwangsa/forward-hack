# `reference-data/` — the one place real-world facts are allowed

Everything else in this repository is fictional. Asteria is not a real company,
its people are not real people, PulseOne and PulsePatch are not real devices, and
none of the incidents happened. [`GENERATION-CONTRACT-V0.md`](../plan/mock/asteria/GENERATION-CONTRACT-V0.md)
§9 rule 6 states it as a build rule: *"Real-world facts are banned except in
`reference-data/`."*

**This directory is that exception, and it is a narrow one.**

## Why the exception exists

[`REGISTER-SHAPES-V0.md` §5.3](../plan/REGISTER-SHAPES-V0.md) computes a
regulatory reporting deadline from an awareness event. That computation cannot be
faked, for two reasons.

1. **A fictional holiday calendar produces a fictional deadline.** MDCG 2023-3
   Rev.2 Q14 rolls a due date forward past *"a public holiday in the relevant
   Member State"*. If Ireland's public holidays are invented, the due date is
   invented, and the product's central claim — that it computes a defensible
   deadline — is false at the arithmetic level, not just at the demo level.
2. **The regulations are public text.** 21 CFR Part 803, MDR 2017/745 Art. 87 and
   the MDCG guidance are quotable primary sources. Paraphrasing them into
   plausible-sounding invented rules would be strictly worse than citing them.

So: the *world* is fictional; the *ruler we measure it with* is real.

## What is real here, and how real

| File | Real-world content | Verified against |
|---|---|---|
| `holidays/ie-2025-2026.json` | Republic of Ireland public holidays | Two independent listings per year, plus re-derivation from the statutory moveable-feast rules |
| `holidays/nl-2025-2026.json` | Netherlands public holidays | government.nl (which days count) + Easter arithmetic (when they fall) |
| `holidays/us-federal-2025-2026.json` | US federal holidays, observed | **OPM directly** — the official 2025 and 2026 tables |
| `holidays/au-vic-2025-2026.json` | Victoria, Australia public holidays | Secondary listings citing Business Victoria; one entry is `unverified` |
| `clock-rules/us-21cfr803.json` | 21 CFR §803.3, §803.50, §803.53, §803.56 | Quoted text, carried through [`REGISTER-REF-complaint-vigilance.md`](../plan/reference/REGISTER-REF-complaint-vigilance.md) §3.6 |
| `clock-rules/eu-mdr-art87.json` | MDR Art. 87, MDCG 2023-3 Rev.2 Q14/Q15, Reg. 1182/71 Art. 3(4) | Quoted text, same reference |
| `clock-rules/jurisdictions.json` | Which regimes V0 supports | Our own scoping decision, per §5.4 — *not* a real-world fact |

## What is **not** real here

- `jurisdictions.json`'s scope is a **product decision**, not a legal statement.
  `AU: clock_rules_available = false` does not mean Australia has no reporting
  deadlines. It means **we have not loaded them** and will therefore show none.
- `effective_from` on every rule file is the validity window of *this encoding*,
  and says so in its own `effective_from_basis` field. It is not a regulatory
  commencement date. 21 CFR Part 803 and MDR Art. 87 both long predate it.
- The `au-vic` calendar is Asteria's **own working calendar** — internal target
  dates, meeting scheduling, who was in the office. It computes no statutory
  deadline. A loaded calendar is a necessary but not sufficient condition for
  `clock_rules_available`.

## The honesty rules this directory follows

**1. Nothing is stated that a source did not verify.** Where the answer is an
absence, the absence is recorded as data with `confidence: "verified_as_absence"`
rather than left as a silent gap. Two examples:

- 21 CFR Part 803 provides **no** rule rolling a 30-calendar-day deadline off a
  weekend. The EU does. Importing the EU rule into the US clock would be a
  fabricated rule with a plausible shape, so `us-21cfr803.json` says
  `rollforward_rule.calendar_day_clocks.applies: false` and explains why.
- MDR Art. 88 sets **no** deadline for trend reports. `eu-mdr-art87.json`
  records `due_date_computable: false` rather than inventing one.

**2. Uncertainty is marked, not smoothed over.** Exactly one date in this
directory is `confidence: "unverified"`:

> `au-vic-2025-2026.json` → **2026-09-25**, "Friday before the AFL Grand Final".
> Both sources consulted on 2026-09-13 showed it as *date to be confirmed*,
> pending the AFL fixture and Victorian gazettal. The conventional
> last-Friday-in-September guess is recorded so the entry is not silently
> absent, and marked so it cannot be mistaken for a fact.

A test (`test_no_unverified_date_can_move_a_regulatory_deadline`) asserts that
`ie`, `nl` and `us-federal` — the three calendars a statutory clock is actually
computed against — contain **zero** unverified dates. AU computes nothing, so the
one unverified date cannot reach a deadline.

**3. No due date beats a wrong due date.** §5.4 again:

> *"A product that shows no due date and says why is telling the truth; one that
> invents a TGA deadline is not."*

Every unavailable jurisdiction carries an `unavailable_reason` written to be
shown to a user. `jurisdictions.json` includes **DE** specifically to make the
point visible: Germany has a fully loaded, fully verified MDR rule set and is
still unavailable, because Q14's roll-forward is national and no German
holiday calendar is loaded.

**4. Versions are first-class, never comments.** §5.3 requires that a due date
computed under one guidance revision stay explainable after the guidance is
revised. Every rule file carries a `rule_version` string and an `effective_from`
date, and every computed result carries the `rule_version` it was computed
under. Superseding a rule set means adding a new `rule_version` with a later
`effective_from` — never editing one in place.

**5. Everything is offline and deterministic.** No runtime network access. The
web was used once, on 2026-09-13, to verify the dates; the answers are checked
in. Sources are named per file, per entry.

## Where the dates go wrong, if they do

Two judgement calls are worth knowing about before trusting a computed date:

- **Dutch days that are official but worked.** Goede Vrijdag, Koningsdag and
  (outside lustrum years) Bevrijdingsdag are officially recognised public
  holidays that most Dutch employees still work. MDCG Q14's test is *"a public
  holiday in the relevant Member State"*, not *"a day our staff had off"*, so V0
  counts all three as non-working. Each entry carries `statutory_day_off: false`
  so a later revision can narrow this without re-researching.
- **Irish weekend holidays create no substitute weekday.** 2026-12-26 falls on a
  Saturday and Monday 2026-12-28 is an ordinary working day in Ireland — unlike
  in Victoria, which does substitute. Getting this backwards moves the
  Christmas-period roll-forward by a day.

## Consumers

[`tools/clock/`](../tools/clock/) is the reference implementation. It reads only
this directory, and its test suite re-derives every moveable feast from the rule
its own `basis` field states rather than trusting the typed-in date.

```
uv run --directory tools/clock pytest
```
