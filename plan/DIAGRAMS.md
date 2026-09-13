# Agent workflow diagrams

Companion to [`WORKFLOW.md`](WORKFLOW.md). One diagram per agent workflow, in the order they appear in [§9 Where the agent intervenes](WORKFLOW.md#9-where-the-agent-intervenes). Each diagram starts at its own trigger, so no diagram depends on reading another.

| Colour | Meaning |
|---|---|
| ⬜ **grey** | Trigger — an event in the customer's existing tools, or human work the agent does not touch |
| 🟩 **green** | Agent work — Observe, Recommend, or Draft |
| 🟧 **amber** | Human decision — never automated, regardless of confidence |
| 🟦 **blue** | Output — review material, a draft record, or a deliverable |

**The rule the colours encode:** a green node never creates an approved record. It produces evidence, a recommendation, or a draft that a named human accepts, amends, or rejects. The record exists only when a human signs it. The amber gates are the [hard human gates](WORKFLOW.md#hard-human-gates--never-agent-regardless-of-confidence) — they are not candidates for confidence-based automation later.

| # | Workflow | Autonomy | Clause |
|---|---|---|---|
| [1](#1-ingest-and-resolve) | Ingest and resolve | Draft | §8.2.1 |
| [2](#2-complaint-triage-recommendation) | Complaint triage recommendation | Recommend | §8.2.2 |
| [3](#3-reportability-evidence-assembly) | Reportability evidence assembly | Draft | §8.2.3 · Part 803 · Art. 87 |
| [4](#4-precedent-lookup) | Precedent lookup | Recommend | §8.2.2 |
| [5](#5-scope-expansion) | Scope expansion | Draft | §8.3.2 / §8.3.3 |
| [6](#6-trend-detection) | Trend detection | Draft | §8.4 · Art. 88 |
| [7](#7-record-drafting) | Record drafting | Draft | §8.2.2 · §8.3.1 · §8.5.2 |
| [8](#8-coordination) | Coordination | Execute with approval | all lanes |
| [9](#9-evidence-bundle-assembly) | Evidence bundle assembly | Observe | all lanes |

---

## 1. Ingest and resolve

**Trigger:** anything inbound lands in a connected source — no human has to file it first.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>email · support ticket<br/>distributor or rep mail<br/>service job · return"]
  A1["Extract the event facts<br/><small>free-text serial · lot · UDI<br/>software version · date</small>"]
  A2["Match to a canonical unit<br/><small>installed base · shipment · DHR</small>"]
  A3["Propose duplicate links<br/><small>one real event arriving<br/>through three channels</small>"]
  G{"Confirm or reject the link<br/><small>human · official record merges<br/>are never automatic</small>"}
  O["Resolved event in the quality inbox<br/><small>every fact keeps source, extraction<br/>method, timestamp, confidence</small>"]
  T --> A1 --> A2 --> A3 --> G --> O
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2,A3 agent
  class G gate
  class O out
```

Everything downstream reads from the resolved event, so this is the workflow the rest depend on. It is also the hardest: entity resolution across fragmented sources at volume is what a human cannot do reliably. §8.2.1 is the intake net — *all* feedback, not only the subset that turns out to be a complaint.

---

## 2. Complaint triage recommendation

**Trigger:** a resolved event appears in the inbox that has not yet been classified.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>unclassified resolved event"]
  A1["Apply the §3.4 definition<br/><small>alleged deficiency in a device<br/>released from the organisation's control</small>"]
  A2["Assemble the reasoning<br/><small>quoted evidence · cited clause<br/>precedent classifications</small>"]
  G{"Is it a complaint?<br/><small>§8.2.2 · named human decider<br/>this gate starts regulatory obligations</small>"}
  O1["Complaint — open the record<br/><small>goes to workflows 3, 4 and 7</small>"]
  O2["Feedback only<br/><small>still recorded · still feeds §8.4</small>"]
  T --> A1 --> A2 --> G
  G -->|yes| O1
  G -->|no| O2
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2 agent
  class G gate
  class O1,O2 out
```

The agent buys consistency: the same judgement made the same way every time, with the rationale recorded. The classification itself stays human because it is what starts the regulatory obligations. "Shipment arrived late" is not a complaint; "reading drifted mid-procedure" is.

---

## 3. Reportability evidence assembly

**Trigger:** awareness. Not the end of an investigation — the moment the organisation first holds the information.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>awareness of a potentially<br/>reportable event"]
  A1["Pin the start of the clock<br/><small>first receipt timestamp<br/>and where it landed</small>"]
  A2["Assemble the decision facts<br/><small>harm · malfunction · recurrence<br/>device identification · patient outcome</small>"]
  A3["Surface the applicable clocks<br/><small>US 30 calendar / 5 work days<br/>EU 15 / 10 / 2 days · flag divergence</small>"]
  G{"Reportability determination<br/><small>§8.2.3 · human only, always</small>"}
  O["Submission pack, or a recorded<br/>not-reportable rationale"]
  T --> A1 --> A2 --> A3 --> G --> O
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2,A3 agent
  class G gate
  class O out
```

This workflow runs on its own statutory clock, in parallel with any investigation — it is never a downstream step, and waiting for the investigation is the single most common place a real QMS takes a finding. The clocks start on awareness, and awareness is scattered across inboxes, so surfacing the start of the clock is the highest-value thing the agent does anywhere.

---

## 4. Precedent lookup

**Trigger:** a complaint record is open and someone has to decide whether to investigate.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>open complaint awaiting<br/>the investigation decision"]
  A1["Retrieve materially similar priors<br/><small>same failure mode · model · lot<br/>software version</small>"]
  A2["Attach their outcomes<br/><small>investigation findings · dispositions<br/>linked CAPAs · effectiveness verdicts</small>"]
  G{"Investigation required?<br/><small>§8.2.2 · decline only with<br/>documented justification</small>"}
  O1["Investigate<br/><small>recover device · pull DHR<br/>check lot · attempt reproduction</small>"]
  O2["Declined, citing the prior investigation<br/><small>the negative decision is a record</small>"]
  T --> A1 --> A2 --> G
  G -->|yes| O1
  G -->|no| O2
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2 agent
  class G gate
  class O1,O2 out
```

§8.2.2 explicitly permits not investigating where a materially similar complaint was already investigated — but only if you can find it and cite it. Retrieval over the full history is exactly what a human cannot do reliably, which is why the justification is usually thin in practice.

---

## 5. Scope expansion

**Trigger:** a nonconformity is detected, or a complaint investigation confirms product is nonconforming.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>NC detected at incoming, in-process,<br/>release or returns · or confirmed<br/>by a complaint investigation"]
  A1["Expand the population<br/><small>same lot · adjacent lots · same tool<br/>same supplier · same software version</small>"]
  A2["Answer the fork question<br/><small>did any of it ship?<br/>joins ERP, shipment, installed base</small>"]
  G1{"§8.3.2 or §8.3.3?<br/><small>pre-delivery or post-delivery<br/>human · getting this wrong<br/>is a serious finding</small>"}
  G2{"MRB disposition<br/><small>§8.3.2 · use-as-is under concession<br/>rework · repair · regrade · scrap</small>"}
  G3{"Advisory notice or FSCA?<br/><small>§8.3.3 · MDR Art. 87.1.b<br/>feeds workflow 3</small>"}
  O["Scoped NC record<br/><small>affected population with<br/>its evidence trail</small>"]
  T --> A1 --> A2 --> G1
  G1 -->|nothing delivered| G2
  G1 -->|units delivered| G3
  G2 --> O
  G3 --> O
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2 agent
  class G1,G2,G3 gate
  class O out
```

Containment and segregation happen before any of this — they are physical, immediate, and human. The agent's job starts once the record exists: work out how far the problem reaches. A complaint that confirms a product nonconformity creates a *linked* NC record; it does not merge into the complaint or get absorbed by it.

---

## 6. Trend detection

**Trigger:** continuous. This is a planned aggregation layer above the registers, not a reaction to any single event.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>scheduled run over<br/>the connected evidence"]
  A1["Aggregate and normalise<br/><small>complaints · service jobs · returns<br/>literature · one event, many records</small>"]
  A2["Compute the denominator<br/><small>shipped units · installed base<br/>usage cycles — deterministic</small>"]
  A3["Compare and explain<br/><small>rate by period and cohort<br/>agent cites, it does not compute</small>"]
  G1{"Signal review<br/><small>human · benefit-risk impact</small>"}
  G2{"Art. 88 trend report?<br/><small>human · threshold pre-set in<br/>the technical documentation</small>"}
  O["PMS and PSUR sections<br/><small>§8.4 · MDR Art. 83–86</small>"]
  T --> A1 --> A2 --> A3 --> G1 --> G2 --> O
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2,A3 agent
  class G1,G2 gate
  class O out
```

The denominator is the product. Without shipped-unit and installed-base data a trend is only a raw count, and a raw count is not defensible under Art. 88 — where the threshold is a legal commitment made in advance. The calculation is deterministic and reproducible; the model explains and cites it rather than performing it.

---

## 7. Record drafting

**Trigger:** a human decision has just created the need for a record — a complaint confirmed, an NC raised, a CAPA warranted.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>complaint confirmed · NC raised<br/>CAPA evaluation says warranted"]
  A1["Prefill the mandated fields<br/><small>QMSR §820.35.a · spec, quantity,<br/>lot or serial, detector · problem, risk, scope</small>"]
  A2["Cite every field<br/><small>each value links back to<br/>the evidence it came from</small>"]
  A3["Flag the gaps<br/><small>what is missing, what conflicts<br/>between sources</small>"]
  G{"Human review and sign-off<br/><small>§8.2.2 · §8.3.1 · §8.5.2<br/>opening a CAPA is a human act</small>"}
  O["Approved record<br/><small>complaint · NC · CAPA · PMS section</small>"]
  T --> A1 --> A2 --> A3 --> G --> O
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2,A3 agent
  class G gate
  class O out
```

This removes transcription, not judgement. The value is not the speed of the draft — it is that every prefilled field carries provenance back to the original evidence, so the reviewer checks a citation instead of hunting for a source. Root cause, effectiveness verdict, and closure all stay human gates inside the CAPA that follows.

---

## 8. Coordination

**Trigger:** an open item needs something from a named person — a reply, an attachment, a decision, a deadline met.

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>open action needing input<br/>or an approaching due date"]
  A1["Identify the responsible owner<br/><small>process · site · supplier · role</small>"]
  A2["Draft the information request<br/><small>what is needed, why, by when</small>"]
  G{"Approve before sending<br/><small>human · external requests always<br/>routine reminders automatic</small>"}
  A3["Match replies back<br/><small>attachments and answers land on<br/>the open request, not an inbox</small>"]
  O["Action register with live status"]
  T --> A1 --> A2 --> G --> A3 --> O
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef gate fill:#fdecd2,stroke:#b8761f,stroke-width:1.5px,color:#4a2f07
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2,A3 agent
  class G gate
  class O out
```

Lowest regulatory risk, highest time saving. This is where quality teams actually lose their days: chasing people, then re-finding the reply three weeks later in a thread. Routine reminders go out automatically; anything leaving the organisation is approved first.

---

## 9. Evidence bundle assembly

**Trigger:** an audit, an inspection, a notified-body request — or any time someone asks "show me the trail".

```mermaid
flowchart LR
  T["<b>Trigger</b><br/>audit · inspection<br/>notified body request"]
  A1["Walk the chain backwards<br/><small>approved decision → record →<br/>investigation → source message</small>"]
  A2["Assemble with provenance<br/><small>who decided, when, on what evidence<br/>including the negative decisions</small>"]
  O["Audit evidence pack<br/><small>source record through<br/>approved decision</small>"]
  T --> A1 --> A2 --> O
  classDef trigger fill:#eceae5,stroke:#8a8578,stroke-width:1.5px,color:#2e2c27
  classDef agent fill:#d9f0e3,stroke:#2f7d5d,stroke-width:1.5px,color:#12351f
  classDef out fill:#e3ecf7,stroke:#3f6ea8,stroke-width:1.5px,color:#12253d
  class T trigger
  class A1,A2 agent
  class O out
```

No gate, because nothing is being decided — this workflow only retrieves. It is Observe-level autonomy, and it works only if the eight workflows above kept their provenance as they went. Audit preparation is recurring, expensive, and purely retrieval-shaped.

---

## Source dependency matrix

Every workflow above reads from the same shared quality context, in which each fact retains its source, extraction method, timestamp, confidence, and review status. Source systems never write directly into a regulated record. This matrix is which source families each workflow actually needs.

| Agent workflow | Comms | Commercial + ops | Product data | Service + returns | QMS of record | External |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 · Ingest and resolve | ● | ● | ● | ● | | |
| 2 · Triage recommendation | ● | | ● | | ● | |
| 3 · Reportability evidence | ● | | ● | ● | ● | |
| 4 · Precedent lookup | | | | ● | ● | |
| 5 · Scope expansion | | ● | ● | | ● | |
| 6 · Trend detection | ● | ● | ● | ● | ● | ● |
| 7 · Record drafting | | | | | ● | |
| 8 · Coordination | ● | ● | | | ● | |
| 9 · Evidence bundle | | | | | ● | |

The source families, as they exist in the customer's tools today: **comms** — email, support, chat, distributor and rep mail. **Commercial and operations** — CRM, ERP, orders, shipments, installed base. **Product data** — model, lot, serial, UDI, software version, DHR. **Service and returns** — service jobs, repairs, RMAs, replacements. **QMS of record** — complaint, NC and CAPA registers, audit findings, PMS plan, risk file. **External** — literature, regulator notices, similar-device data.

The integration is the moat: the individual workflows are straightforward, but those six families sit across different systems and teams. Trend detection is the only workflow that needs all six, and commercial data is what turns event counts into rates. The human boundary is explicit throughout: no agent path reaches an approved record without a named human decision.
