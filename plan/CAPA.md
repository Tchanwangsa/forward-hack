# Tier 3 — the CAPA recommendation

**What this is.** The third tier. It reads across registers and across time and answers one question: *have we seen this before, and did our fix hold?*

Companions: [`ARCHITECTURE.md`](ARCHITECTURE.md) (the three tiers), [`REGISTERS.md`](REGISTERS.md) §4.3 (the CAPA Register), [`DIAGRAMS.md`](DIAGRAMS.md) (tier 2, which produces what tier 3 reasons over), [`WORKFLOW.md`](WORKFLOW.md) (the regulatory grounding).

---

## The distinction that makes this a tier and not a bigger NC

A Product NC says *this is wrong*. A CAPA says *our system let this happen twice*.

That is not a difference of severity. Ten units failing at once is one nonconformity, however bad. One unit failing for the third time — after a containment, after a closed NC, after a firmware release that was supposed to have fixed it — is a CAPA, however small the count. **The trigger for a CAPA is not magnitude. It is the failure of a prior action.**

Which gives tier 3 a test it can actually apply:

> Did this failure mode reappear **after** something we did was supposed to address it?

If nothing intervened, three occurrences are one cluster and tier 2 owns them. If something intervened and the mode came back, that is recurrence and the question is why the intervention did not hold. An agent that recommends a CAPA because a number is large has not understood the difference and will recommend one every quarter.

---

## The five triggers

`Trigger` on the CAPA Register is one of five. Each demands a different argument, and the agent has to state which it is making.

| Trigger | The claim | What makes it defensible | Where it goes wrong |
|---|---|---|---|
| **Prior NC ineffective** | We closed an NC on this and it came back | The prior NC, its corrective action, its effectiveness check, and the post-closure occurrences with dates | Calling the *same open problem* a recurrence because it was logged twice |
| **Recurrence** | The same failure mode has arisen in separate episodes over time | Distinct episodes, separated by an intervention or by enough time that they are not one cluster; the same mode by the structural test below | Counting one flapping unit's eleven telemetry events as eleven occurrences |
| **Cross-register convergence** | The same mode appears independently in registers that do not talk to each other | Rows from three or more registers, each independently attributable, agreeing on component or configuration | Circular evidence: an RMA raised *from* an email is not two sources |
| **Single severe NC** | One NC is serious enough that systemic action is warranted regardless of recurrence | The scope resolved to named units in the field, and why containment is insufficient | Severity is a human judgement; the agent presents the scope and does not score it |
| **External** | A regulator, distributor, notified body or supplier raised it | The external document | Out of scope for the agent to originate — it records one |

**On `Single severe NC`:** it exists because a real CAPA register needs it, and the agent's role is narrower here than anywhere else — resolve the affected scope, count the units still in the field, surface what containment did and did not cover, and stop. It does not rate severity. Nothing in the indicator set encodes harm, and a product that infers clinical severity from a false-alert rate is making a claim it cannot support.

---

## The hard problem: what makes two things the same failure mode

This is where tier 3 could quietly become nonsense. Free-text similarity will happily agree that "battery below spec on load test" and "charge state reporting wrong" are the same thing, and they might be — or one is a cell degradation and the other a firmware reporting bug with an identical symptom and an entirely different fix.

**The rule: structural agreement, stated field by field. Semantic similarity starts the comparison and never concludes it.**

Two records are proposed as the same failure mode when they agree on all three:

1. **Indicator** — the same one of the seven. Not "both battery-ish"; the same code.
2. **Component or configuration** — a named part from `Component Replaced` or a parts line, or a named configuration from a technician finding or software-issue text. `Battery module`, `comms module`, `ward alert profile`, `SW 1.1.0 alert logic`.
3. **A shared cohort axis** — both inside one HW revision, one SW version, one lot, or one site, with a denominator large enough that the shared axis is not a coincidence of two.

And the recommendation must **state every disagreement it found**, not just the agreements. "These seventeen findings agree on the indicator and the component and the HW revision, and disagree on site — which is what you would expect if the cause is the hardware and not a ward practice" is an argument. The same sentence with the disagreement deleted is a sales pitch.

Where the three tests do not all pass, the honest output is a *question*: "these two look related and I cannot show that they are — here is what would settle it." That is a useful thing for an agent to say and a bad thing to hide.

---

## What tier 3 reads

Tier 3 is the only part of the product that reads the other two tiers' outputs as its primary input.

| Source | What it takes from it |
|---|---|
| **Product NC Register** | the prior NCs, their corrective actions, their `CAPA considered` decisions and rationales, their closures |
| **CAPA Register** | prior CAPAs and — the load-bearing field — `Why prior action did not hold` on any that already failed |
| **Signal Register** | signals closed *no action* and left on *monitoring*; a mode that was dismissed twice and is now back is exactly the pattern |
| **Complaint Register** | complaints on the same mode, including `Declined` ones, and the customer's own words |
| **The five capture-fed registers** | the occurrences themselves, and — after tier 1 — the ones a human never logged |
| **PMS Review Meetings + transcripts** | what the team said at the time. A minuted *"worth a look next cycle"* that nobody looked at is recurrence evidence about the process, not just the product. |
| **Agent Action Log** | whether the evidence was there and got rejected, or was never surfaced. A different failure and a different fix. |

**The dependency runs upward, and it is the argument for the tiers.** Tier 3 can compare NCs only because tier 2 left behind records with resolved scope and evidence links rather than a pile of emails. And it can count occurrences only because tier 1 put the unlogged ones in the register. A recurrence argument built on a register that is missing 17% of events is an argument that will be wrong in the one direction that matters — it will say *no recurrence* and be believed.

---

## The sweep

**Triggers:** on every NC reaching a terminal status, on every signal closed or set to monitoring, and weekly regardless.

The weekly sweep exists because the interesting case has no trigger. A mode that recurs with no new NC — because each occurrence was individually closed as too small — will never fire an event-driven check. That is precisely the pattern a CAPA is for, and it is invisible to anything that only wakes up when something is filed.

```text
for each candidate failure mode in the trailing 24 months:
    gather occurrences across all capture-fed registers
    group into episodes                       (not raw rows — see the de-dup rule)
    find every prior action that touched it    (NC, containment, CAPA, SW release)
    for each prior action:
        occurrences strictly after its effectiveness check?
    if yes -> draft a recommendation, trigger = Prior NC ineffective
    else if separate episodes across >=3 registers with structural agreement
         -> draft, trigger = Cross-register convergence
    else if separate episodes over time with an intervening action
         -> draft, trigger = Recurrence
    else -> no recommendation, and log that the sweep ran
```

**The last line is not a formality.** A sweep that produces nothing has still produced a record that somebody looked. The Agent Action Log carries the negative result, so "we did not notice" and "we looked and there was nothing" stay distinguishable a year later — which is the difference between a gap and a judgement when an auditor asks.

**24 months is a choice, not a principle.** It is the span of the register set, so it is the longest window the data supports. On a real deployment the window should be the product's lifecycle, and a mode that recurs every three years is exactly the one a human will not remember and an agent should.

---

## The human gate

Tier 3 **recommends**. It never opens a CAPA.

| | |
|---|---|
| **Agent drafts** | the problem statement, the recurrence evidence, the prior action, the proposed reading of why it did not hold, the resolved scope, the indicators |
| **Human decides** | `Opened` · `Declined` · `Deferred` — with a rationale, mandatory on all three |
| **Human owns** | root cause, corrective action, preventive action, effectiveness check, closure |

`Declined` and `Deferred` are permanent rows. A CAPA register with no declined recommendations is a register nobody is exercising judgement in, and a declined recommendation with a good rationale is the record that the question was asked and answered.

**CAPA execution stays out of scope** ([`ARCHITECTURE.md`](ARCHITECTURE.md) §Out of scope). The agent drafts the argument for opening one and then stops. Root-cause analysis, action design, implementation and effectiveness verification are the company's work, and a product that drafts an effectiveness check has started writing the evidence that its own recommendation worked.

---

## The demo case

The `BATT` thread, and it works because the precedent is already in the data.

**The prior action.** A 2025 CAPA on battery capacity, arising from an earlier NC, whose corrective action was a firmware change to charge-state reporting. Its effectiveness check passed. It was closed.

**The recurrence.** Fleet IND-03 over the rolling 90 days is 1.08 — **1.79x** the 0.6 baseline, *under* the 2.0x threshold. Nothing breaches. A fleet-level view sees nothing and tier 2 raises no signal.

But H1 units more than 18 months in service run **1.74 = 2.90x**, and the corroboration is not the rate — the in-window numerator is four events, which is thin and must be said so. The corroboration is **seventeen RMA rows whose technician findings read `Battery module replaced, capacity 61% of nominal`**: the same indicator, the same named component, the same HW revision, a measured figure repeated seventeen times, and disagreement on site — which is what you would expect if the cause is the hardware and not a ward practice.

**And there is a signal that stopped just short.** `SIG-2026-0013` is `BATT` on H1, left on *monitoring*, with the reviewer asking service to record measured capacity. Service then recorded it, seventeen times, in a different register. Nobody joined the two.

So the recommendation writes itself, and every clause of it is checkable:

> The 2025 battery CAPA's corrective action addressed charge-state *reporting*. Seventeen returns since its effectiveness check show measured capacity at 61% of nominal on H1 units past eighteen months — capacity, not reporting. The prior action fixed the symptom it was scoped to and the underlying mode is still present in the field on 125 H1 units. Trigger: prior NC ineffective. `SIG-2026-0013` asked for exactly this measurement and it was taken; it was taken into a register nobody reads against signals.

**Why this is the right demo case and the `ALERT-FALSE` story is not.** The 1.1.0 story is new — it has no prior action to have failed, so it is correctly an NC and not a CAPA. Running tier 3 on it would be the exact overreach this document is written to prevent. Two stories, two tiers, and the discipline is visible in which one goes where.

---

## What tier 3 must not do

| Not this | Because |
|---|---|
| Recommend on magnitude | That is a signal, and tier 2 owns it |
| Treat one cluster as recurrence | Ten offline events in six days at one site is one episode. The near-miss story is exactly this shape and is correctly *no action*. |
| Treat correlated sources as independent | An RMA raised from an email thread is one source. Convergence needs genuine independence and the agent must say how it established that. |
| Score clinical severity | Nothing in the indicator set encodes harm |
| Draft the root cause | It drafts the *problem statement*. A root cause the agent wrote is a root cause nobody investigated. |
| Draft the effectiveness check | See above — that is writing the evidence for its own recommendation |
| Recommend the same thing twice | A previously `Declined` recommendation may only be re-raised on **new** evidence, and must cite what is new and reference the declining rationale |

---

## Honest weaknesses

**The data gives tier 3 one good case, not five.** Two years of registers and five historical NCs is a thin base for a recurrence engine. The `BATT` case is real and checkable; a second convincing one would have to be planted, and planting it makes the engine look better than the evidence supports.

**The structural test is strict and will miss things.** Requiring agreement on indicator, component *and* a cohort axis means a real recurrence expressed differently in two registers — one calling it a comms module, the other an antenna seating fault — will not pass. That is the trade: a tier that misses a real recurrence is recoverable, and a tier that confidently invents one is not. The mitigation is the question output, not a looser test.

**Recurrence over a 24-month register is a shorter memory than the problem needs.** A three-year cycle is invisible here. Nothing in the design fixes that; more history does.

**"Why prior action did not hold" is the field most likely to be wrong and most likely to be believed.** It is a causal claim about the company's own past work, drafted by an agent, in a register an auditor may read. It is marked agent-drafted and human-confirmed for that reason, and it should be the field with the lowest accept-without-edit rate in the whole product. If it ever climbs above the others, something has gone wrong with the reviewing, not right with the drafting.
