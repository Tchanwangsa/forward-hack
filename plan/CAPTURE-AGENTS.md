# Tier 1 — the capture agents

**What this is.** Five agents, one primitive, five sources. Each watches the natural upstream source of one register and drafts the rows a human would otherwise type in late, badly, or never.

Companions: [`ARCHITECTURE.md`](ARCHITECTURE.md) (why capture is the product), [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md) (the raw material each one reads), [`REGISTERS.md`](REGISTERS.md) (the tables they write into).

---

## The primitive

```text
observe ──► resolve ──► classify ──► draft ──► confirm ──► committed
```

| Step | What happens | Autonomy |
|---|---|---|
| **observe** | An artifact appears in a watched source: an email lands, a transcript finishes, a telemetry event arrives, a work order is raised, a ward round is filed. | Automatic |
| **resolve** | Which customer, hub, serial, ward, bed, lot. `RNH` → `Royal North Hospital`, `4111` → `PO-P1-004111`, a bed number and a pairing ID → one hub. Plumbing, never a screen. | Automatic |
| **classify** | One of the seven indicator codes, or none. Telemetry arrives pre-classified; everything else is the actual work. | Automatic, with a confidence |
| **draft** | Fill every field this source evidences. Leave every field it does not. Attach the artifact reference. | **Draft (level 3)** |
| **confirm** | A human accepts, edits, or rejects. Verdict and diff go to the Agent Action Log. | **Human gate** |

The five rules that hold for every bot:

1. **Never commits a row.** Level 3 forever — see [`ARCHITECTURE.md`](ARCHITECTURE.md) §Autonomy.
2. **Fills only what its source evidences.** A blank is a correct answer. Guessing `Assigned To` to make a row look complete is the failure mode that discredits the whole tier.
3. **Carries its artifact reference.** `Captured From` on every drafted row, resolvable to the exact email, transcript span, event, or work order.
4. **Never edits a human row.** A wrong or incomplete human row gets a *completion proposal* — a separate reviewable object — and the original stays as written.
5. **Declares a confidence, and low confidence routes to a human as a question, not a draft.** "I think this ward check describes an adhesive failure but the text is `patch edge lift observed` under `Hardware Issues`" is a question worth asking.

### Two kinds of output

Capture produces two things and they are reviewed differently:

| | **New row** | **Completion** |
|---|---|---|
| When | the artifact records something no register row covers | a register row exists but a field the artifact evidences is blank or contradicted |
| Reviewed as | accept the row as drafted, edit it, or reject it | accept the field value, edit it, or reject it |
| Writes | a new register row, `Row Origin = Agent` | **nothing to the source row.** The proposed value lives in the capture layer with its evidence; downstream analysis reads the completed view |
| The measure | rows recovered that did not exist | blanks filled, and contradictions surfaced |

Rule 4 and the second column are the same rule. The customer's spreadsheet stays theirs; the completed view is ours. See [`REGISTERS.md`](REGISTERS.md) §Provenance.

---

## The five

| # | Bot | Watches | Drafts into | Build |
|---|---|---|---|---|
| [1](#1-outage-watch) | **Outage watch** | telemetry event stream | Incident & Outage Log | **Full** |
| [2](#2-inbox-triage) | **Inbox triage** | `support@` `service@` `quality@` mailboxes | Comms Log + **complaint recommendation** | **Full** |
| [3](#3-meeting-scribe) | **Meeting scribe** | client + PMS review transcripts | Comms Log (`Channel = Meeting`) | **Full** |
| [4](#4-rma-capture) | **RMA capture** | service work orders + technician notes | Returns & Replacements | Stub |
| [5](#5-field-check-nudge) | **Field-check nudge** | ward round notes | Data Check & Troubleshooting | Stub |

---

## 1. Outage watch

**Watches** the telemetry event stream — see [`TELEMETRY-API.md`](TELEMETRY-API.md) and [`UPSTREAM-SOURCES.md`](UPSTREAM-SOURCES.md) §Telemetry stream.
**Drafts into** PM Incident and Outage Log → `Incidents & Outages`.

The strongest bot, because the gap it closes is the largest and the source is machine-truthful.

| Field | Drafts | From |
|---|---|---|
| `Incident/Outage ID` | ✓ | next in sequence |
| `Pairing ID` · `Pairing Status` | ✓ | hub inventory at the event date |
| `Organisation` | ✓ | resolved — written canonically, unlike the human rows |
| `HubID` · `Serial Number` | ✓ | the event's hub, canonical serial |
| `WardID` · `BedID` | ✓ | hub inventory |
| `Last Online` | ✓ | **the event's own last-online**, not the inventory snapshot the humans copy |
| `Offline Duration (hrs)` | ✓ | event-close minus event-open, where the stream carries both |
| `Reported Date` | ✓ | the event timestamp — same day, not a median-0-p90-5-day lag |
| `Incident Description` | ✓ | from the event code and its payload, in the register's own vocabulary |
| `Status` | ✓ | `Open` on draft |
| `Event Code` | ✓ | **the event code is the indicator code.** Never blank, never wrong. |
| `Source` | ✓ | `Telemetry` |
| `SW Version at Time` | ✓ | **the hub reported it at the moment of the fault** |
| `Notes` | ✓ | only where the payload says something a human would write |
| `Reported By` | — | a telemetry event has no reporter. Left blank. |
| `Assigned To` | — | triage is a human act |
| `Date of Last Email Sent` | — | not this bot's business |

**The gap it closes.** 369 indicator events happened; 307 reached the incident log. Of those 307, 197 carry the correct code. The register correctly identifies 53% of the world.

| Measure | Baseline | Target |
|---|---|---|
| Events present as a row | 307 / 369 = 83% | **+44 rows that do not exist** — the hub codes it owns outright |
| Correct event code on indicator rows | 64% (27% blank, 9% wrong) | ~100% on telemetry-sourced rows |
| `SW Version at Time` present | 65% | ~100% on telemetry-sourced rows |
| `Serial Number` present | 89% | 100% |
| World-event → register-row latency | median 0d, p90 5d, max 6d | seconds |

The `SW Version at Time` line is the one that matters most, and not because 35% is a big number. It is because of *which* rows are blank: of the fifteen `ALERT-FALSE` events on SW 1.1.0 inside the live window, **two** carry a correct version. The primary finding is invisible to tier 2 until this bot has run.

**What it must not do.** `SKIN` (IND-06) has no telemetry path — a patch cannot detect a rash. Zero `SKIN` rows may ever carry `Source = Telemetry`; if this bot emits one, it has invented an event.

`ADHESIVE` is the delicate one. The stream *does* carry it ([`TELEMETRY-API.md`](TELEMETRY-API.md) §2), but only as a signal-loss pattern *consistent with* detachment — an inference, not an observation. Outage watch drafts `CONN-LINK-LOSS`, `HUB-OFFLINE`, `BATT`, `ALERT-FALSE` and `DISPLAY` as confident rows; it raises `ADHESIVE` as a low-confidence question for a human to confirm against the ward, and never as a committed classification.

**The 62 split three ways, and that is the argument for building all five bots.** Of the events missing from the incident log entirely: **44** are hub codes outage watch owns outright, **15** are `ADHESIVE` it can only ask about, and **3** are `SKIN` it will never see. Those last 18 reach the company through a ward check, a client email or a returned sample — which is to say through bots 2, 4 and 5. No single capture source closes the gap; the five of them together do.

**Failure mode to design against.** Telemetry is chatty. A hub that flaps offline eleven times in six days at one site is *one* incident, and the near-miss story is exactly that shape — ten `HUB-OFFLINE` rows at Ashfield Private inside six days, all explained by a hospital network cutover. Outage watch must de-duplicate into episodes, and must carry the site-wide co-occurrence into `Notes` so tier 2 can close it as no-action honestly. A bot that turns a network maintenance window into ten separate incidents has made the register worse, not better.

---

## 2. Inbox triage

**Watches** the `support@`, `service@` and `quality@` mailboxes — threads, not messages.
**Drafts into** PM Client Communications Log → `Client Communications`, and separately **recommends a complaint**.

| Field | Drafts | From |
|---|---|---|
| `Comm ID` | ✓ | next in sequence |
| `Email Subject` | ✓ | thread subject, de-`Re:`'d |
| `Date of Initial Email` · `Date of Last Email Sent` | ✓ | first and last message in the thread |
| `Channel` | ✓ | `Email` |
| `Status` | ✓ | open if the last message is inbound and unanswered |
| `Type` | ✓ **with a confidence** | the thread's content — **not** the human's habit of typing `Technical query` for everything |
| `Organisation` · `Client Contact` · `Contact Email` | ✓ | resolved from the sender domain and address book |
| `Contact Role` | ✓ | **the signature block** — blank on 46% of human rows and almost always present in the email |
| `Handled By` · `Mailbox` | ✓ | the internal participant, the receiving mailbox |
| `Notes` | ✓ | the substance — what the customer actually said |
| `Attachments` | ✓ | filenames as attached |
| `Cross-reference` | ✓ **as a hint only** | mentions of an RMA, incident or lot in the body |
| `Indicator` / `Event Code` | ✓ **with a confidence** | classification of the underlying issue, where there is one |

**The complaint recommendation** is the interesting half. `Type = Complaint` in the comms log is a human's casual label. A **complaint** in the QMS sense is a formal record with a lifecycle, an owner, a closure rationale and a vigilance screen. Those are different objects and conflating them is how complaint registers end up both over- and under-populated.

So: inbox triage **recommends**, with its reasoning and the sentences it relied on. A human classifies. The decision — either way — is a record.

```text
thread ──► drafted Comms row  (level 3, confirm to commit)
       └─► complaint recommendation  (level 2, human decides)
              │
              ├── yes ──► Complaint Register row, drafted from the thread
              └── no  ──► logged decision, with a rationale. Not a deletion.
```

What makes a recommendation, stated in advance so it is not a vibe: dissatisfaction with product performance or safety, attributable to a specific product and ideally a specific unit or lot, from a customer rather than internally, about something that happened rather than something feared. Escalating tone is a weak signal; a named serial and a described failure is a strong one.

The register's own field `Vigilance screen required (Y/N)` is **human-only and the agent never fills it**. Vigilance is explicitly out of scope ([`ARCHITECTURE.md`](ARCHITECTURE.md) §Out of scope) and the field exists to mark that boundary rather than to hide it.

| Measure | Baseline | Target |
|---|---|---|
| `Contact Role` present | 54% | ~100% |
| `Type` agreeing with thread content | unreliable by construction | measured against ground truth |
| Threads with a comms row at all | — | 100% |
| Complaint recommendation precision / recall | — | against the ground-truth complaint set |
| Indicator classified from free text | — | the second-hardest classification job in the dataset |

---

## 3. Meeting scribe

**Watches** transcripts — client site visits, support queue reviews, and the PMS review meetings themselves.
**Drafts into** PM Client Communications Log → `Client Communications` with `Channel = Meeting`.

**Why the comms log and not its own register.** ISO 13485 §8.2.1 is one feedback net. A concern raised by a nurse unit manager in a Tuesday site visit and the same concern emailed on Wednesday are the same feedback, and splitting them into two registers means tier 2 has to re-join them to see it. One register, a `Channel` column, and the analysis reads across channels for free.

*(If a standalone Client Feedback Log is wanted instead, this is the decision to revisit — it is one column and one file, not a re-architecture.)*

| Field | Drafts | From |
|---|---|---|
| `Comm ID` | ✓ | next in sequence |
| `Email Subject` | ✓ | the meeting title — the column is misnamed for meetings and stays misnamed, because the real file is |
| `Date of Initial Email` | ✓ | meeting date |
| `Channel` | ✓ | `Meeting` |
| `Type` | ✓ with a confidence | what the item actually was |
| `Organisation` · `Client Contact` · `Contact Role` | ✓ | the attendee list |
| `Handled By` | ✓ | the Asteria attendee who owned the item |
| `Notes` | ✓ | **one row per raised item, not one row per meeting** |
| `Captured From` | ✓ | transcript ID plus the timestamp span of the passage |
| `Mailbox` · `Attachments` | — | not applicable to a meeting |

**The hard part** is that a transcript is not a list of items. It is forty minutes of people talking, most of it irrelevant, with three things in it that belong in a register. Finding those three, attributing each to the right organisation and unit, and *not* filing the other thirty-seven minutes is the whole job. Precision matters more than recall here: a scribe that files nine rows from a meeting that contained three will be turned off by its second week.

A raised item that also carries an indicator issue gets one classification, at a confidence, exactly as inbox triage does. A meeting item that is a complaint gets the same recommendation path.

| Measure | Target |
|---|---|
| Items filed vs items a human marked as worth filing | precision first, then recall |
| Attribution accuracy (org / hub / ward) | against ground truth |
| Passages cited per row | ≥1, always, resolvable to a timestamp span |

---

## 4. RMA capture — stub

**Watches** the service system: work orders, technician notes, parts-replaced lines.
**Drafts into** Product Return and Replacement Register → `Returns & Replacements`.

Stubbed for the hackathon: the same primitive, wired to a thinner source, enough to show the pattern generalises.

The gap is real and narrow enough to be shown in one screen. `SW Version` is blank on **48%** of RMA rows, and it is recoverable — the hub inventory knows what that serial was running as at the date the RMA was raised. `Linked Complaint` is blank on 83%, and the complaint register plus the comms log usually say which thread the return came out of.

The register's actual value is the gap between `Customer Reported Fault` and `Technician Findings` — *"Unit alarming for no reason"* against *"Configuration reset to ward profile, no hardware fault"* is an `ALERT-FALSE` event and its explanation in the same row. Capture's job is to make sure both halves are present and the serial is resolvable, so that seventeen technician notes reading `Battery module replaced, capacity 61% of nominal` are findable as a cohort rather than as seventeen separate afternoons.

| Field | Drafts | From |
|---|---|---|
| `SW Version` | ✓ | hub inventory as at `Date Raised` — a **completion**, not a new row |
| `HW Rev` | ✓ | hub inventory |
| `Serial Number` | ✓ canonical | the work order |
| `Technician Findings` · `Component Replaced` | ✓ | the technician note and the parts lines |
| `Customer Reported Fault` | ✓ | the originating thread where there is one |
| `Linked Complaint` | ✓ | the complaint register |
| `Disposition` · `Warranty Status` | — | commercial and engineering judgement |
| `Linked Signal` | — | written by tier 2, not tier 1 |

---

## 5. Field-check nudge — stub

**Watches** ward round notes.
**Drafts into** PM Data Check and Troubleshooting Log → `Data Check & Troubleshooting`.

Also stubbed. Its two jobs:

**Complete what the round recorded.** `Patch Lot` is blank on 51% of check rows and resolvable from the lot allocation for that ward in that window; `Serial Number` is blank on 26% and resolvable from ward, bed and pairing; `Action Taken` is blank on 66% and is often stated in the round note and lost on the way to the spreadsheet.

**Nudge the incomplete check.** A row reading *"Ward busy, check incomplete"* is the product's business case written by a nurse. The nudge is a level-2 recommendation — this check did not finish, this unit is in the cohort we are currently investigating, ask for it again — and every word of the outbound ask goes through a human.

The classification job here is the hardest in the dataset and the best demonstration of why capture is not transcription. Four free-text columns map *imperfectly* onto the seven indicators: an adhesive finding sits in `Hardware Issues`, a battery finding sometimes sits in `Software Issues` as *"Charge state reporting wrong"*, `E-207 / E-211 pair` is a link-loss event written as an error code, and one row can carry two indicators.

---

## The capture scorecard

One table, all five bots, and it is a real screen. Every number below is computable against `mock-company/ground-truth/`.

| Metric | Why it is the right measure |
|---|---|
| **Rows recovered** | Register rows that did not exist and should have. 62 for outage watch alone. The clearest number in the product. |
| **Blanks filled, by column** | Per-column, so the weak spots are visible rather than averaged away. |
| **Field accuracy** | Of what it filled, how much was right — scored against ground truth, not against the human's typed value. |
| **Classification accuracy** | Drafted event code vs `true_code`. Broken out by source, because telemetry is easy and free text is not. |
| **Contradictions surfaced** | Human rows the artifact disagrees with. A different and more delicate thing than a blank. |
| **Accept / edit / reject** | The human verdict, per bot. `Edited` is the useful one: it says the bot was close and names how it was wrong. |
| **Latency** | Artifact timestamp → drafted row. Against a human baseline of median 0, p90 5 days for the rows that got written at all. |
| **Coverage lift** | The headline: indicator events correctly represented in the registers. 53% → target. |

Two honest caveats to keep on this screen rather than in a footnote. **Accept rate is not accuracy** — a tired reviewer accepting everything scores the same as a perfect bot, which is why field accuracy is scored against ground truth and not against the verdict. And **recall on the free-text sources has no clean ceiling**: there is no ground truth for "items a human would have wanted filed from this meeting" beyond the ones we planted, so precision is the number to lead with for bots 3 and 5.
