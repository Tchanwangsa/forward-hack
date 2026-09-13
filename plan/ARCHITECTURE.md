# Architecture — three tiers

**What this is.** The spine of the product. Read it before anything else in `plan/`.

Companions: [`CAPTURE-AGENTS.md`](CAPTURE-AGENTS.md) (tier 1 in detail), [`DIAGRAMS.md`](DIAGRAMS.md) (tier 2's five workflows), [`CAPA.md`](CAPA.md) (tier 3), [`REGISTERS.md`](REGISTERS.md) (the eleven tables), [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md) (the raw material tier 1 watches).

---

## The one line

**The registers are not the input. They are the output.**

Every register a PMS team keeps is a human transcription of something that happened somewhere else — a phone call, an email thread, a ward round, a hub going quiet at 03:40. The transcription is late, partial, or never made. Then the analysis runs on it and inherits every gap.

So the product has two halves, and the first one is the one nobody builds:

- **Tier 1 · Capture** — an agent per register, each watching that register's natural upstream source, drafting the rows a human would otherwise type in late, badly, or never.
- **Tier 2 · Analysis** — the indicator engine reading across the now-complete registers, recommending a Product NC.
- **Tier 3 · CAPA** — reading across tiers and across time, recommending a CAPA.

The analysis only becomes trustworthy because the capture layer closed the gaps. That is the whole argument.

---

## Runtime and storage

The application runs on **Postgres**, not on a folder of mutable workbooks. Postgres is authoritative for workflow state, review queues, accepted completions, system-maintained registers, approvals and the append-only action log. Agents interact through constrained application operations with validation and permission checks; they do not receive unrestricted database credentials.

The customer's reference and capture-fed spreadsheets remain source inputs during the pilot. Each import is retained as a versioned snapshot, source rows are never overwritten, and accepted additions or completions live in the database capture layer. Controlled `.xlsx` files can be generated from a named database snapshot for review, hand-off or audit evidence.

---

## The three tiers

```text
TIER 1 · CAPTURE            each bot watches one source, drafts into one register
────────────────
 client meeting  ──► Meeting scribe    ──► Client Feedback & Comms Log
 mailboxes       ──► Inbox triage      ──► Comms Log  +  complaint recommendation
 telemetry feed  ──► Outage watch      ──► Incident & Outage Log (incl. missed rows)
 service system  ──► RMA capture       ──► Returns & Replacements
 ward rounds     ──► Field-check nudge ──► Data Check & Troubleshooting
                              │
                              ▼  registers now actually complete
TIER 2 · ANALYSIS → NC
 read across complaints · returns · incidents · checks · comms
 against the approved indicators and thresholds
                              │
                              ▼  recommend: file a Product NC?          ◄── human gate
TIER 3 · CAPA
 overlap across registers · recurrence · same failure mode in
 three different logs · prior NCs that didn't hold
                              │
                              ▼  recommend: open a CAPA?                ◄── human gate
```

Every tier-1 bot is the same primitive pointed at a different source. That consistency is what makes it demo well and build fast.

---

## The capture primitive

One shape, five instances:

```text
observe ──► resolve ──► classify ──► draft the row ──► human confirms ──► committed
   │           │            │              │                 │
 the raw    which hub,   which of the   every field the   accept · edit ·
 artifact   which org,   seven          bot is allowed    reject — logged
 in its     which lot,   indicators     to fill, and no   in the Agent
 own system which ward   (or none)      field it isn't    Action Log
```

Four rules hold for all five:

1. **A capture bot never commits a row.** It drafts. A human accepts, edits, or rejects, and the verdict is logged. The draft queue is a real screen, not a background job.
2. **A capture bot fills only the fields its source actually evidences.** Outage watch knows the SW version at the moment of the event because the hub reported it; it does not know who the ward will assign the incident to, and leaves `Assigned To` blank rather than guessing.
3. **The raw artifact is the provenance.** Every drafted row carries a pointer to the email message-ID, the transcript timestamp range, the telemetry event ID, or the work-order number it came from. A drafted row you cannot walk back to its source is a bug.
4. **Capture never edits an existing human row.** If a human row is wrong or incomplete, the bot proposes a *completion* — a separate, reviewable suggestion — and the original stays as it was written. See [`REGISTERS.md`](REGISTERS.md) §Provenance.

---

## Why the gaps are the product

This is not a hypothesis about real PMS teams. It is measured in the dataset the product is built against ([`MOCK-DATA.md`](MOCK-DATA.md), `mock-company-v2/ground-truth/`):

| The world | The register | Gap |
|---|---|---|
| 369 indicator events actually happened | 307 reached the incident log | **62 events — 17% — were never written up at all** |
| 307 logged rows | 197 carry the correct event code | 27% blank, 9% wrong |
| — | — | **The register correctly identifies 53% of what happened** |

And per column, on the rows that do exist:

| Column | Blank | What capture knows that the human didn't |
|---|---:|---|
| Incident · `SW Version at Time` | 35% | The telemetry event carries it. The hub reported it at the moment of the fault. |
| Incident · `Event Code` | 27% | Telemetry codes *are* indicator codes. Ward staff never fill this in. |
| Incident · `Serial Number` | 11% | Resolvable from pairing ID, ward and bed. |
| RMA · `SW Version` | 48% | Resolvable from the hub inventory as at the RMA date. |
| Troubleshooting · `Patch Lot` | 51% | Resolvable from the lot allocation for that ward in that window. |
| Troubleshooting · `Action Taken` | 66% | Often stated in the ward round it came from, and lost on the way to the spreadsheet. |
| Comms · `Contact Role` | 46% | In the email signature block. |

The single sharpest instance sits inside the primary planted story: of the fifteen `ALERT-FALSE` events on SW 1.1.0 in the live window, **two carry a correct `SW Version at Time`**. The cohort that is the entire finding is not recoverable from the register as a human left it. Tier 2 cannot find that story without tier 1 having fixed the rows first.

One register literally says so out loud. The August 2026 trend working file is `Overdue`, noted *"Data pending from service team"*. A troubleshooting row reads *"Ward busy, check incomplete."* The business case is sitting in the customer's own spreadsheet.

---

## Tier boundaries — who owns what

| | Tier 1 · Capture | Tier 2 · Analysis | Tier 3 · CAPA |
|---|---|---|---|
| **Unit of work** | one artifact → one or more drafted rows | one indicator × cohort × window | one failure mode across registers and time |
| **Trigger** | an artifact appears in a watched source | nightly, and on every new classified event | a new NC, and a weekly sweep |
| **Question it answers** | "what happened, and which row records it?" | "is this rate higher than we said we'd tolerate?" | "have we seen this before, and did our fix hold?" |
| **Output** | a drafted register row + a completion suggestion | a Signal, then a drafted Product NC | a CAPA recommendation |
| **Human gate** | confirm each drafted row | promote signal → NC; approve/close NC | the CAPA-considered decision |
| **Writes to** | the five capture-fed registers | Signal Register · Product NC Register | CAPA Register |
| **Reads** | its own source + Hubs/Lots for resolution | all eleven registers | Signals, NCs, CAPAs, and the registers beneath them |

Tier 2 is what the five workflows — Watch, Measure, Raise, Investigate, Record — always were. They are the NC path, not the whole product. [`DIAGRAMS.md`](DIAGRAMS.md) specifies them unchanged, one tier down.

---

## Autonomy levels

Every action carries an explicit level, visible in the UI, logged in the Agent Action Log.

1. **Observe** — read and organise.
2. **Recommend** — suggest a classification, a next step, a complaint, a CAPA.
3. **Draft** — prepare a register row, a record, or a message for review.
4. **Execute with approval** — act after a named user confirms.
5. **Automatic** — low-risk, pre-authorised: normalisation, entity resolution, rate calculation, the nightly run.

**Capture is level 3, always.** No capture bot is ever promoted to level 5, however good its accept rate gets. A register row committed without a human is a record the company cannot defend, and the accept rate is itself the metric we want to keep measuring.

### Gates no confidence level may bypass

- Committing any drafted register row (tier 1)
- Classifying an inbound communication as a **complaint** (tier 1 recommends, a human decides)
- Promoting a Signal to a Product NC (tier 2)
- Approving or closing a Product NC (tier 2)
- The CAPA-considered decision, and opening a CAPA (tier 3)
- Any outbound customer communication (any tier)

A signal closed as *no action*, a complaint declined, a CAPA judged unnecessary — each is a permanent record with a named reviewer and a rationale. Never a deletion.

---

## What the tiers buy each other

The tiers are not three products stapled together. Each one is only as good as the one above it, and that dependency is the pitch:

- **Tier 1 → tier 2.** Coverage. 53% → near-total. The SW-version cohort becomes recoverable, so the primary story becomes findable. Without tier 1, tier 2 is running the same incomplete six-way join the specialist already runs, just faster.
- **Tier 2 → tier 3.** Structure. A CAPA argument needs *NCs with resolved scope and evidence links*, not a pile of emails. Tier 3 can reason about recurrence only because tier 2 left behind comparable records.
- **Tier 3 → tier 1.** Feedback. A CAPA that failed because the evidence was thin is a capture problem, and it names the register that was empty. "We could not tell whether this recurred, because nobody recorded the check" is a tier-1 requirement discovered by tier 3.

---

## Build order

Tier 1 is the part judges can actually see working, and it is the part that is new. Build it first and build it properly.

| | Build | Notes |
|---|---|---|
| 1 | **Outage watch** (telemetry → Incident log) | The strongest single demo. It creates rows that do not exist and fills `SW Version at Time` on rows that do. Everything downstream depends on it. |
| 2 | **Inbox triage** (mailboxes → Comms log + complaint recommendation) | The complaint recommendation is the first place a human gate is genuinely interesting. |
| 3 | **Meeting scribe** (transcript → Comms log, `Channel = Meeting`) | Demos live and needs no integration story. |
| 4 | **Tier 2**, all five workflows | Already specified. Lands the `ALERT-FALSE` / SW 1.1.0 finding and correctly closes the network-maintenance near-miss. |
| 5 | **Tier 3**, one convincing CAPA recommendation | Cross-register overlap on the `BATT` / H1 thread, plus a prior NC that did not hold. |
| 6 | **RMA capture** and **field-check nudge** | Stubbed: the same primitive, wired to a thinner source, enough to show the pattern generalises. |
| — | **Dashboard** | Design only. Five screens specified in [`DASHBOARD.md`](DASHBOARD.md); ship the capture queue if you ship one screen. |

### The honest scope risk

Five capture bots plus two analysis tiers is a lot for a hackathon. Three built properly beats five half-wired, and the two stubs must still be visibly the same primitive — a stub that looks like a different product costs more than it saves. Tier 2 and tier 3 each need to land **once, convincingly**, on a planted story: the NC path on `ALERT-FALSE` / SW 1.1.0, the CAPA path on `BATT` / H1. Anything past that is a bonus.

---

## Out of scope

Unchanged from before, and worth restating because the tier-1 reframe widens the surface and the scope has to hold anyway:

Vigilance, reportability and regulatory clocks. Production and manufacturing NCs. MRB and disposition of nonconforming stock. Advisory notices and FSCA. **Full CAPA execution** — tier 3 recommends opening a CAPA and drafts its problem statement; it does not run the investigation, verify effectiveness, or close it. Audit, training, change control, supplier quality, management review. `reference-data/clock-rules/` stays on disk; nothing reads it.

Also parked, deliberately: outage escalation logic, troubleshooting nudges beyond the stub, and a Slack assistant.

Entity resolution is plumbing. It has to work perfectly and it is never a screen.
