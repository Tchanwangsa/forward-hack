# plan/

**The product:** three tiers of agent working alongside a post-market surveillance specialist at a medical-device company. **Tier 1 captures** — five bots watch the natural upstream sources (a telemetry stream, the mailboxes, meeting transcripts, the service system, ward rounds) and draft the register rows a human would otherwise type in late, badly, or never. **Tier 2 analyses** — the indicator engine reads across the now-complete registers, computes the rates the company's own PMS plan already specifies, and recommends a Product NC. **Tier 3 recommends a CAPA** — recurrence, cross-register overlap, prior fixes that did not hold. Hackathon Track 1 — improve an existing business capability.

**The one line:** the registers are not the input, they are the output. Measured in the dataset the product is built against: 369 indicator events happened, 307 reached the incident log, and of those 307 only 197 carry a correct event code. The register correctly identifies **53%** of what happened. That is the number the product attacks, and it is why the analysis tier is only trustworthy once the capture tier has run.

**The company:** Asteria Medical Systems (fictional). Two products — PulseOne P1-100, a network-connected bedside hub, 250 units across 16 customer organisations in AU/NZ/UK/NO; PulsePatch PP-72, a lot-controlled disposable sensor patch.

**The engine:** seven indicators, each with an internal code, a computed denominator, a trailing-12-month baseline and an escalation threshold — all approved in advance in a controlled document.

## Start here

| Read | For |
|---|---|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | **The spine.** The three tiers, the capture primitive, tier boundaries, autonomy, build order, scope |
| [`IDEA.md`](IDEA.md) | The pitch — what it is, who it is for, the demo beat, the risks |
| [`CAPTURE-AGENTS.md`](CAPTURE-AGENTS.md) | Tier 1 — the five bots, field by field, and the capture scorecard |
| [`DIAGRAMS.md`](DIAGRAMS.md) | The tier overview, the capture primitive, tier 2's five workflows, tier 3's sweep |
| [`CAPA.md`](CAPA.md) | Tier 3 — how recurrence and cross-register overlap become a CAPA recommendation |
| [`REGISTERS.md`](REGISTERS.md) | The eleven registers, the indicator rule set, how both denominators are computed |
| [`SHEETS.md`](SHEETS.md) | The live Google Sheets surface — seven workbooks, service-account auth, what an agent may write |
| [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md) | The raw artifacts tier 1 watches, and the ground truth that scores it |
| [`TELEMETRY-API.md`](TELEMETRY-API.md) | The six endpoints, event codes, backfill, AWS mapping — and tier 1's primary source |
| [`DASHBOARD.md`](DASHBOARD.md) | The five React screens (design only, not built) |
| [`WORKFLOW.md`](WORKFLOW.md) | Why this shape is legitimate (ISO 13485 §8.2.1/§8.2.2/§8.4/§8.5, MDR Art. 83–88) |
| [`MOCK-DATA.md`](MOCK-DATA.md) | How the register set and the upstream artifacts are generated, and made realistically imperfect |
| [`mock/asteria.md`](mock/asteria.md) | The fictional company |
| [`reference/`](reference/) | Deep regulatory research. Correct, much wider than this product. Not implemented. |
| [`archive/`](archive/) | Superseded documents, kept for their techniques — including the nine-register v0 schema |

## Deliberately out of scope

Vigilance, reportability and regulatory clocks. Production and manufacturing NCs. MRB and disposition of nonconforming stock. Advisory notices and FSCA. **CAPA execution** — tier 3 recommends opening a CAPA and drafts its problem statement; it does not run the investigation, verify effectiveness, or close it. Audit, training, change control, supplier quality, management review. `reference-data/clock-rules/` stays on disk; nothing reads it. No claim that the product guarantees compliance.

Entity resolution is plumbing — it has to work, it is never a screen.

## Human gates

No confidence level bypasses any of these, and capture never rises above autonomy level 3 however good its accept rate gets:

- Committing any drafted register row (tier 1)
- Classifying an inbound communication as a **complaint** (tier 1 recommends, a human decides)
- Promoting a Signal to a Product NC (tier 2)
- Approving or closing a Product NC (tier 2)
- The CAPA-considered decision, and opening a CAPA (tier 3)
- Any outbound customer communication (any tier)

A capture draft rejected, a complaint declined, a signal closed as *no action*, a CAPA judged unnecessary — each is a permanent record with a named reviewer and a rationale. Never a deletion.
