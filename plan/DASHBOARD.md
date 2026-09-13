# Dashboard — design

**Status: design only. Not built.** Five React screens for an internal tool used by one PMS specialist, the two or three people who review with them, and — new with tier 1 — the support, service and clinical-support staff who confirm drafted rows.

**The capture queue is the primary screen**, because tier 1 is what gets built first and because it is the only screen where a human does work the agent cannot do. Fleet and Indicators exist so that a signal can be trusted; the signal queue is where the specialist lives; NC drafts exists so that acting on a signal is not a retyping exercise. If only one screen gets built, build the capture queue.

```text
CAPTURE QUEUE  ──▶  FLEET  ──▶  INDICATORS  ──▶  SIGNAL QUEUE  ──▶  NC DRAFTS
what the agent      what is     is anything    what needs me      what I'm
drafted for me      out there   moving         today               signing
```

Screens 2–5 read [`TELEMETRY-API.md`](TELEMETRY-API.md); the capture queue reads the drafted rows plus the artifacts behind them ([`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md)). No screen computes a rate.

---

## Screen 1 — Capture queue

**The primary screen.** Question: what has the agent drafted, and is it right?

Three panes. A bot rail on the left, the queue in the middle, and — the whole point of the screen — **the artifact beside the drafted row** on the right.

```text
┌───────────────┬────────────────────────────┬──────────────────────────────────┐
│ Outage watch  │  ▸ new row   INC-…         │  THE ARTIFACT                    │
│   32 new      │    ALERT-FALSE · 1.1.0     │  the telemetry event, the email  │
│   13 compl.   │    Cathedral Hill W3B      │  thread, the transcript span     │
│ Inbox triage  │  ▸ completion  INC-0412    │                                  │
│   18 new      │    SW Version at Time      │  THE DRAFTED ROW                 │
│   6 questions │    blank → 1.1.0           │  field by field, with what each  │
│ Meeting scribe│  ▸ question   round RD-…   │  field came from, and the blanks │
│   4 new       │    adhesive or hardware?   │  shown as deliberate blanks      │
│ RMA capture   │                            │                                  │
│ Field-check   │                            │  Accept · Edit · Reject · Ask    │
└───────────────┴────────────────────────────┴──────────────────────────────────┘
```

**Grouped by bot**, because the reviewer for a drafted incident row is not the reviewer for a drafted comms row, and because the edit rate that matters is per bot. The rail shows pending counts by kind.

**Three item kinds, reviewed differently:**

| Kind | What the reviewer is deciding | Actions |
|---|---|---|
| **New row** | is this a real event, and is the row right? | Accept · Edit · Reject (reason required) |
| **Completion** | is this the right value for a cell a human left blank? | Accept the field · Edit · Reject |
| **Question** | the bot is not confident enough to draft — it is asking | Answer · Dismiss |

A completion never touches the human's row. Accepting one writes the value into the capture layer with its evidence, and the analysis tier reads the completed view — [`REGISTERS.md`](REGISTERS.md) §6. The screen must say so in plain words next to the button, or reviewers will believe they are editing the spreadsheet.

### The artifact pane

This is the screen's one real idea and the reason it can be reviewed fast. Whatever the bot read is rendered beside what it wrote:

- **Telemetry** — the raw event, its payload, the hub's state at that moment, and, where the bot grouped a burst into one episode, **all of the events in the episode**. The near-miss is the test: ten `HUB-OFFLINE` events at one site over six days must arrive as one queue item showing ten events, not as ten items.
- **Email** — the thread, quoted chains collapsed, with the sentences the bot relied on highlighted. The signature block that supplied `Contact Role` is highlighted too, because that is the field the reviewer will not otherwise check.
- **Transcript** — scrolled to the cited timestamp span, with the turns either side visible. The reviewer needs the surrounding conversation to judge whether an item is filable or whether it was someone saying *"we might have seen it on 12 as well, I'd have to check"*.
- **Work order / ward round** — the note verbatim, with the parts lines or the beds walked.

Design rules for this pane, all of them about the same failure:

- **The artifact is never behind a click.** A reviewer who has to open something in another tab is a reviewer who starts accepting without looking, and a rubber-stamped queue is worth less than no queue.
- **The evidence for each field is attributable to a place in the artifact.** Hovering a drafted field highlights what it came from. A field the bot cannot point at should not have been filled.
- **Blanks render as deliberate blanks.** `Assigned To — not evidenced by this source` is the correct output and must look correct. An empty cell that reads as an omission trains reviewers to fill it in themselves, which is the behaviour the product exists to remove.
- **Nothing is pre-selected, and there is no select-all accept.** Bulk accept per *field type* across a completion set is defensible — thirteen `SW Version at Time` completions from the same telemetry window are one decision — and bulk accept across new rows is not. The friction is the feature.
- **Keyboard first.** Accept, next, edit, reject. A queue of fifty drafts is a five-minute job or it does not get done.

### The capture scorecard — a panel on this screen

**Decision: the scorecard is a panel here, not a sixth screen.** A pinned band across the top of the queue, three numbers wide, expanding to the full per-bot table from [`CAPTURE-AGENTS.md`](CAPTURE-AGENTS.md) §The capture scorecard.

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ Coverage  53% ──▶ 91%      Rows recovered  44        Field accuracy  96.2%   │
│ indicator events correctly  incident rows that       of fields filled, vs    │
│ represented in the registers did not exist            ground truth ▾ expand  │
└──────────────────────────────────────────────────────────────────────────────┘
```

*(The 91% is an illustration of the shape, not a claim. Coverage lift, field accuracy and every other scorecard number are to-be-measured against `mock-company-v2/ground-truth/capture-targets.csv` once the capture run is scored. 53% and 44 are measured.)*

Two reasons for the panel rather than the screen. First, the scorecard's job is to **discount the accept rate the reviewer is generating on this very screen** — a tired reviewer accepting everything scores identically to a perfect bot, which is why field accuracy is scored against ground truth and not against the verdict. Putting that caveat one navigation step away from the person clicking accept hides it from the only person it is about. Second, a standalone metrics screen in an internal tool is the screen nobody opens.

This still satisfies the requirement that the scorecard is a real screen and not a footnote: it is full width, always visible, and expands in place to the whole table — rows recovered, blanks filled by column, field accuracy, classification accuracy by source, contradictions surfaced, accept/edit/reject per bot, latency, coverage lift. It is not a tooltip and not a link.

Two things stay on the expanded panel rather than in a footnote, because they are the honest limits:

- **Accept rate is not accuracy.** Shown next to the accept rate, every time.
- **Recall on the free-text sources has no clean ceiling.** There is no ground truth for "items a human would have wanted filed from this meeting" beyond the ones we planted, so precision leads for the meeting scribe and the field-check nudge, and the panel says which metric is which.

**Do not build:** an inbox-shaped mail client, a transcript editor, in-place editing of the customer's workbook, a bot configuration UI.

---

## Screen 2 — Fleet

**Question:** what is out there right now, and is it healthy?

A dense table, one row per hub, 250 rows. `GET /v1/fleet/hubs`.

| Column | Notes |
|---|---|
| Online | Dot. Green online, grey offline, amber offline > 24h. |
| Serial | Canonical `PO-P1-004111`; hover shows the variants seen in the registers. |
| Organisation · Ward · Bed | |
| HW rev · SW version | Three HW revisions — H1, H2, H2.1. The plan says two; the data wins. |
| Last seen | Relative. "4 min ago" / "3 days ago". |
| Battery | Bar. |
| Unit status | `In service`, `Installed`, `Spare`, `At depot (RMA)`, `Shipped - not installed`, `Decommissioned`. |
| Accrues? | Whether this unit is in the denominator. `Spare` and `Shipped - not installed` are not, and a reviewer should be able to see that without reading the formula. |
| Open events (90d) | Count, linking into a filtered event list. |

**Header strip:** units in service · units online now · units offline > 24h · **SW version spread as a stacked bar** (1.0.0 · 1.0.2 · 1.1.0 · 1.1.1).

That stacked bar is the screen's one real idea. It is the first place a viewer sees that the fleet is not on one version, which is what makes the eventual "it is only 1.1.0" finding land. Clicking a segment filters the table.

**Filters:** organisation, SW version, HW rev, ward, unit status, online state.

**Do not build:** a map, a floorplan, per-hub live vitals.

---

## Screen 3 — Indicators

**Question:** is anything moving?

Seven cards, one per indicator, in a grid. `GET /v1/metrics/indicators`.

Each card:

```text
┌──────────────────────────────────────────────────┐
│ IND-04 · ALERT-FALSE                   ⚠ BREACH  │
│ False or inappropriate alert          PulseOne   │
│                                                  │
│                              ╱‾‾‾               │
│   ───────────────────── threshold 2.2 ──── ╱──── │
│                                        ╱         │
│   ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ baseline 1.1 ┄┄╱┄┄┄┄┄┄┄┄ │
│   ______________________________╱                │
│                                                  │
│   3.08 per 100 unit-months        ratio 2.80x    │
│   20 events / 6.50 unit-month blocks · 90d       │
│   PMS-PLAN-001 v3.0                              │
└──────────────────────────────────────────────────┘
```

- **Solid horizontal line** = escalation threshold. **Dashed** = baseline. **Shaded region** above the threshold, so a breach is visible without reading a number.
- The rate line is the rolling 90-day rate, plotted over the trailing 12 months.
- **Numerator and denominator are always on the card.** A rate without them is a number nobody can check.
- IND-06 (`SKIN`, "any increase — clinical review") has **no threshold line** — only a baseline and a clinical-review flag. Rendering a fake threshold line on it would misrepresent the rule. It also has no telemetry path at all, and the card should say so rather than look like a quiet indicator.
- The source document is on the card, because "who said 2.0x?" is the first question anyone senior asks.

**Cohort control** at the top: `Fleet · by SW version · by HW rev · by organisation · by ward · by lot`. Switching to *by SW version* splits each card into one line per version, and this is where the demo turns — the fleet line is unremarkable, the 1.1.0 line is not.

Cohorts below the minimum denominator render greyed with "insufficient exposure", never as a rate.

Clicking a card → the events behind it, and any signal raised from it.

---

## Screen 4 — Signal queue

**Question:** what needs me today?

Two panes: a list on the left, the open signal on the right.

**List** — grouped `Open` / `Monitoring` / recently closed. Each item: indicator code, cohort value, ratio as a chip (`2.80x`), age, review function (Quality / Clinical / Service), a one-line agent summary, and a **capture-dependent badge** where the signal needs tier 1 to be visible at all.

**Detail pane**, in this order:

1. **The breach, in one line.** "IND-04 on SW 1.1.0 — 14.28 per 100 unit-months against a baseline of 1.1. Threshold 2.0x."
2. **The chart**, same rendering as Screen 3, with the cohort line against the fleet line so the contrast is visible.
3. **Cohort breakdown.** A small table: every SW version's rate side by side, so the reader can see 1.1.0 is the outlier and 1.0.2 is not.
4. **Contributing events.** Every one, by source register, each row linking to its source: incidents, RMAs, troubleshooting checks, client comms, complaints. Each row carries its **`Row Origin`** chip, so it is visible at a glance how much of this signal's evidence a human typed and how much a bot drafted.
5. **Capture dependency.** A toggle — *without tier 1* — that recomputes the cohort from human-origin rows only. On the primary story the cohort collapses from fifteen rows to the two that carry a correct SW version, and the signal disappears. This is the single most persuasive control in the product and it belongs on the signal, not in a slide.
6. **Agent rationale.** Prose, clearly labelled as the agent's reading, with an **autonomy badge** (`Draft`). Includes the innocent explanation it considered and why it did not settle for it.
7. **Precedent** — prior signals, NCs, complaints and RMAs the agent found (WF 4).
8. **Missing data** — what is *still* incomplete after capture, with a **Draft an information request** button. After tier 1 this list is shorter and more honest: fields no artifact evidences, and checks that were never done.
9. **The gate.** Three buttons, equal weight: **Promote to NC** · **Monitor** · **Close — no action**. A free-text rationale is required for all three, and the reviewer's name is stamped automatically.

Design rules for this screen:

- **`Close — no action` is not a destructive-looking button.** It is a correct, common, valuable outcome, and it must not be styled as a rejection.
- **Nothing is pre-selected.** No default verdict, no "recommended action" highlighted as a primary button. The agent's opinion is in the rationale, not in the button styling.
- **Every number on this screen is clickable down to source rows, and from a source row to its artifact.** If a reviewer cannot get from "14.28" to the telemetry event or the email behind it in two clicks, the screen has failed.
- **The agent's rationale is always visually distinct** from the computed facts above it. Facts and opinion do not share a background colour.

---

## Screen 5 — NC drafts

**Question:** what am I about to sign?

A left rail of Product NC drafts by status (`Draft` / `In review` / `Approved` / `Closed`), and a document-shaped editor on the right.

Every prefilled field shows its provenance inline — a small source chip that expands to the rows behind it, and from a drafted row to its artifact:

| Section | Prefilled from |
|---|---|
| Description · Indicator | The signal |
| **Affected scope** | Hub Inventory + Lot Allocation — resolved to **named serials and lots**, listed, with a count of units still in service |
| Evidence links | Every contributing source row, with its `Row Origin` |
| Containment | What the RMAs actually did |
| Proposed disposition | The agent's read of the RMA dispositions, editable |
| CAPA considered | A Y/N control with a **mandatory** rationale either way. `Y` hands off to tier 3; it is not the same as opening a CAPA. |
| Root cause · Investigation owner | Empty. Human-written. The agent does not guess root cause. |

Affected scope is the section worth designing carefully: "SW 1.1.0" expanding into named serials at named organisations, with in-service counts, is the single clearest picture of what the product does that a spreadsheet cannot.

**Footer:** Approve and sign (named approver, timestamped) · Return to signal · Discard with a reason.

**Tier 3 is not a sixth screen.** A CAPA recommendation arrives as a panel on the NC that triggered it — the recurrence argument, the prior action, why it did not hold — with `Open · Decline · Defer` and a mandatory rationale. If tier 3 grows past one panel it earns its own screen; it has not yet.

---

## Cross-cutting

**Row Origin, everywhere a register row is shown.** A chip: `Human` · `Agent (accepted)` · `Agent (edited)`, and on agent rows the chip expands to `Captured From` — the telemetry event, the message-ID, the transcript span, the work order. Two rules: the chip is never the loudest thing in the row, and **every table that lists register rows carries a human-origin-only filter**, so anyone can see what the register looked like before the product touched it. That filter is how the coverage claim gets checked rather than believed.

**`Capture-dependent (Y/N)` on signals.** Rendered as a badge in the signal list and as the *without tier 1* toggle in the detail pane (Screen 4, §5). A signal marked `Y` is not weaker than one marked `N` — it is a signal the customer could not previously have seen at all, and the badge should read as information, not as a warning.

**Autonomy badges.** Every agent-produced block carries one: `Observe` / `Recommend` / `Draft` / `Execute with approval` / `Automatic`. Every capture draft carries `Draft`, always, on every bot, and the badge never changes value — capture does not get promoted. Computed numbers carry none; they are not agent output.

**The Agent Action Log** is not a sixth screen. It is a drawer, openable from any drafted row, signal or NC, showing what the agent did to produce what you are looking at — with its tier — and how previous humans ruled on it.

**Tone.** Dense, quiet, closer to an internal admin tool than a consumer dashboard. One accent colour for breach, one for the human gate. Numbers in a tabular figure font. No gauges, no sparkline confetti, no celebratory empty states — an empty signal queue is the normal, good, uneventful case, and an empty capture queue means the reviewers are keeping up.

**Stack.** React + TypeScript, one chart library, a component set the team already knows. Read-only against the API except the write actions: confirm a capture draft, accept a completion, answer a capture question, triage a signal, approve an information request, save an NC draft, sign an NC, and record a CAPA decision.

**Do not build:** a settings screen, user management, indicator editing (the indicator table is a controlled document and is edited in the controlled document), export, or a second theme.
