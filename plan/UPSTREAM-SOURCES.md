# Upstream sources — the raw material

**What this is.** The spec for the artifacts tier 1 watches. These do not exist yet: `mock-company/` generated the registers, and the capture agents need the material *upstream* of them.

Companions: [`CAPTURE-AGENTS.md`](CAPTURE-AGENTS.md) (who reads what), [`MOCK-DATA.md`](MOCK-DATA.md) (how the register set is generated), [`TELEMETRY-API.md`](TELEMETRY-API.md) (the stream's shape as an API).

---

## The governing idea

**Generate the artifact as complete truth. Render the register row as a lossy human transcription of it. Leave some rows untranscribed.**

The existing generator goes:

```text
world ──► events ──► register rows (messy)
```

The new layer sits between:

```text
world ──► events ──► ARTIFACTS (complete, faithful) ──► register rows (lossy, sometimes absent)
                         │                                      │
                         └──────── the gap between them ────────┘
                                           =
                                  what tier 1 is worth
```

Three properties this must have, and they are the acceptance criteria:

1. **The artifact is strictly more informative than the row.** Every blank in a register cell is either present in the artifact or genuinely unknowable from it. A blank the artifact also cannot fill is fine and should exist — it keeps the capture agents honest and stops "100% completion" being the target.
2. **The 62 unlogged events have artifacts.** They happened; somebody noticed; it just never reached the incident log. Their artifact is the proof, and recovering their rows is the clearest thing the product does.
3. **The register data does not change.** Row counts, row order, every existing cell value, all seven indicator rates and all four planted-story strengths stay exactly as verified. The only permitted movement is *additive*: the capture columns appended per [`REGISTERS.md`](REGISTERS.md) §3.0, and the two new workbooks. `CHECKSUMS.sha256` will move for that reason and no other — diff the verification run, not the hashes.

That third one matters practically: the register pack is already verified, already has ground truth, and already carries four planted stories at measured strengths. Re-deriving it would put all of that at risk to gain nothing.

---

## Layout

```text
mock-company/
  registers/            seed only — the shapes and fixtures pushed once into
                        the live Google Sheets, never written to again
  ground-truth/         extended — artifact ↔ row ↔ event links
  sources/              NEW — the raw upstream material
    telemetry/
      events.ndjson           the append-only event stream
      heartbeats.ndjson       thinned; enough to establish sw_version over time
      MANIFEST.json           windows, counts, codes, dedupe keys
    mail/
      support/  service/  quality/      .eml files, one per message
      THREADS.json            thread_id → ordered message-IDs, participants
    meetings/
      transcripts/            one .txt per meeting, timestamped speaker turns
      attendees.json          meeting_id → attendee list with roles
    service/
      work-orders.csv         one row per return raised
      technician-notes.csv    free text, one or more per work order
      parts-replaced.csv      part lines against a work order
    ward-rounds/
      rounds.ndjson           one record per round, free-text observations
```

`sources/` gets its own `CHECKSUMS.sha256`. Ground truth for artifacts goes in `ground-truth/` alongside the rest — it is answer key, not dataset.

---

## 1. Telemetry stream

**Read by:** outage watch. **Renders into:** the incident log.

One NDJSON line per event, append-only, ordered by `ts_received`. Shape follows [`TELEMETRY-API.md`](TELEMETRY-API.md) §3 exactly — this file is what `POST /v1/telemetry/events` would have written.

```json
{"event_id":"TEL-2026-0084210","hub_id":"HUB-0163","ts_device":"2026-07-08T03:41:22+10:00",
 "ts_received":"2026-07-08T03:41:29Z","code":"ALERT-FALSE","severity":"warning",
 "sw_version":"1.1.0","source":"device","dedupe_key":"HUB-0163:ALERT-FALSE:2026-07-08T03:41",
 "payload":{"alert_type":"RR_HIGH","threshold_profile":"default","dismissed_by_role":"RN",
            "ward_profile_applied":false,"dismiss_latency_s":4}}
```

**What must hold:**

| Rule | Why |
|---|---|
| Every indicator event in `ground-truth/events.csv` with a telemetry path appears here — **including the 62 that never reached the incident log** | This is the recovery set |
| Zero `SKIN` events | A patch cannot detect a rash |
| `ADHESIVE` events carry the signal-loss payload, not a detachment claim | It is an inference; the payload must let a human see that |
| `sw_version` is the version **at the moment of the event**, always present | This is the single most valuable field in the whole source set — 35% blank in the register, and blank on 13 of the 15 rows in the primary story |
| `HUB-OFFLINE` carries `ward_wide` and is generated cloud-side | A unit that is offline cannot report that it is offline |
| The near-miss burst arrives as **eleven-ish raw events over six days at one site**, with `ward_wide: true` | Outage watch must de-duplicate into episodes; the raw stream is where the flapping is visible |
| `dedupe_key` present on every event | So episode grouping is checkable, not magic |
| Timestamps in the hub's local timezone for `ts_device`, UTC for `ts_received`, and they must sometimes disagree across a date boundary | A real fleet in AU/NZ/UK/NO does this, and an off-by-one-day join bug is exactly what the register set is for |
| Heartbeats thinned to ~1/day/hub, carrying `sw_version` | Establishes the version timeline so `SW Version Observed On` can be checked and so a version change mid-window is visible |

**Also generate, deliberately:** a small number of events for hubs whose `Unit Status` is `Spare` or `Shipped - not installed`. They do not accrue unit-months, so an event from one of them must not enter a numerator. A capture agent that files an incident for a hub in a cupboard has created a denominator bug, and this is the trap that catches it.

---

## 2. Mailboxes

**Read by:** inbox triage. **Renders into:** the comms log, and complaint recommendations.

One `.eml` per message, RFC 5322, real headers — `Message-ID`, `In-Reply-To`, `References`, `Date`, `From`, `To`, `Cc`, `Subject`. Threads are formed by the header chain, not by filename. `THREADS.json` is ground truth for threading, not an input.

**What must hold:**

| Rule | Why |
|---|---|
| Every comms-log row with `Channel = Email` has a thread behind it | The row is the human's summary of the thread |
| Some threads have **no** comms-log row | Nobody got round to logging it. Recovery set for inbox triage. |
| Every thread carries a **signature block with the sender's role** | `Contact Role` is blank on 46% of comms rows and this is where it lives |
| The sender's organisation is inferable from the domain, but the display name is messy | `Sr. NUM 3B`, `Jo (nights)`, `J. Whitcombe` — the address is the key, the name is not |
| Thread `Type` is often *not* what the human typed in the register | The register's `Type` is unreliable by construction; the email is the evidence |
| A handful of threads are **genuinely ambiguous** between complaint and technical query | The complaint gate has to be worth having. If every recommendation is obvious, the human gate is theatre. |
| Attachments referenced by filename, with a few real small files | `device-log-20260527.txt`, a photo, a scanned form. The comms log's `Attachments` column already expects these. |
| Quoted-reply chains, top-posting, and one thread where the subject drifts off-topic | Extracting the substance from a 6-deep quoted chain is the actual job |
| Mail lands in the right mailbox, and ~7% in the wrong one | `com.mailbox` is blank on 7% of register rows for a reason |

**Volume:** enough to cover the 117 events that surface in `comm`, plus the threads behind the 566 comms rows that carry no indicator, plus unlogged threads. Not every email needs to be interesting — a realistic mailbox is mostly order confirmations and dispatch notices, and a triage bot that cannot ignore those is useless.

**The near-miss needs its 17 emails.** Seventeen client emails saying "our network team did a cutover on Monday" is what lets tier 2 close that signal as no-action with evidence. They must read like seventeen different people wrote them.

---

## 3. Meeting transcripts

**Read by:** meeting scribe. **Renders into:** the comms log with `Channel = Meeting`.

One `.txt` per meeting. Timestamped speaker turns, so a drafted row can cite a span:

```text
[00:14:02] Priya Raghunathan (Asteria, Clinical Support): ...and how have the overnight
           alerts been since the last visit?
[00:14:11] Jo Whitcombe (Cathedral Hill, NUM Ward 3B): Honestly, worse. We had three
           nights last week where the RR alarm went off and the patient was fine. Night
           staff have started ignoring it, which is the bit that worries me.
[00:14:28] Priya Raghunathan (Asteria, Clinical Support): Which beds?
```

**What must hold:**

| Rule | Why |
|---|---|
| Most of the transcript is **not** register-worthy | A scribe that files nine rows from a meeting containing three gets switched off. Precision is the measure, so the haystack has to be real. |
| Each meeting contains 0–4 items that genuinely belong in a register | Ground truth marks which, with the timestamp span |
| Some items are ambiguous or conditional | *"We might have seen it on 12 as well, I'd have to check"* is not a filable item, and a scribe that files it is wrong |
| Items are attributable | The speaker's organisation, and where possible the ward, bed or unit. Sometimes only the ward — that is a real limit, not a generation failure. |
| Speech is speech | Interruptions, half-sentences, someone joining late, a minute of talk about the parking. Clean prose is not a transcript. |
| Both **client meetings** and **internal PMS review meetings** | The 22 rows in the `PMS Review Meetings` sheet need transcripts too — that is where signals get discussed and where tier 3's recurrence argument gets its minuted precedent |
| The precedent conversations exist verbatim | `SIG-2026-0018` was closed no-action with a minuted note that three reporting sites are on the newest software. That sentence must be findable in a transcript. |

**The primary story wants a meeting.** A site visit to one of the three 1.1.0 organisations, where a nurse unit manager describes night-time false alerts in plain clinical language and never mentions a software version — because she does not know it. The scribe files the item; the version comes from tier 1's other half.

---

## 4. Service system

**Read by:** RMA capture. **Renders into:** the returns register.

Three CSVs, joined on `work_order_id`:

- `work-orders.csv` — `work_order_id · rma_number · raised_date · serial_as_written · organisation_as_written · reported_fault_verbatim · received_date · technician · closed_date · disposition`
- `technician-notes.csv` — `note_id · work_order_id · ts · technician · note` — free text, one or more per order, and the interesting ones are diagnostic narrative rather than a conclusion
- `parts-replaced.csv` — `line_id · work_order_id · part_number · part_description · qty`

**What must hold:**

| Rule | Why |
|---|---|
| `SW Version` is **absent here too**, but recoverable from the hub inventory as at `raised_date` | This is a *completion* from a different register, not a transcription. It shows capture doing a join, not just reading. |
| The 17 `Battery module replaced, capacity 61% of nominal` findings appear as notes with the measured figure | The `BATT` / H1 cohort's strongest evidence, and tier 3's CAPA argument |
| Technician notes sometimes contradict the customer's reported fault | *"Unit alarming for no reason"* → *"Configuration reset to ward profile, no hardware fault"*. The gap between the two columns is the register's whole value. |
| Parts lines exist without a matching note, and notes without parts | Real service systems are like this |
| `serial_as_written` keeps the messy renderings | Same variant mix as the registers |

---

## 5. Ward rounds

**Read by:** field-check nudge. **Renders into:** the troubleshooting log.

One NDJSON record per round: who, when, which ward, which beds walked, and free-text observations per bed.

**What must hold:**

| Rule | Why |
|---|---|
| The round knows the **patch lot** — it was read off the pouch | `Patch Lot` is blank on 51% of check rows; this is where it was lost |
| The round knows **bed and pairing**, so the serial is resolvable | `Serial Number` blank on 26% |
| The round often records what was done | `Action Taken` blank on 66% |
| Some rounds are genuinely **incomplete** and say so | *"Ward busy, check incomplete"* — and the nudge is the product |
| Observations are written the way the four free-text columns are | `patch edge lift observed`, `E-207 / E-211 pair`, `Charge state reporting wrong` — and they map *imperfectly* onto the indicators, on purpose |

---

## Ground truth for artifacts

Extends `mock-company/ground-truth/`. Answer key, never handed to anything being evaluated.

| File | What it is |
|---|---|
| `artifact-index.csv` | every artifact: id, kind, path, timestamp, the event(s) it evidences, the register row it was transcribed into (or blank if it never was) |
| `capture-targets.csv` | **the scorecard's answer key.** One row per (register, row_id_or_new, field): the true value, the value the human wrote, and whether a capture agent should be able to fill it from which artifact |
| `meeting-items.csv` | transcript id, timestamp span, whether it is filable, the item it becomes, its attribution |
| `complaint-truth.csv` | which threads are genuinely complaints, which are ambiguous, and the reasoning |
| `episodes.csv` | raw telemetry events → the episode they belong to, so de-duplication is scorable |

`capture-targets.csv` is the important one. Without it, "the bot filled 340 blanks" is unscorable — it has to be *the bot filled 340 blanks and 328 of them match the world*.

---

## Acceptance criteria

Verification runs the same way the register pack's does — re-read the emitted artifacts and check, don't trust the generator.

1. `verify.py`'s output is unchanged line-for-line on everything it checked before: referential integrity, entity resolution, all seven indicator rates, each planted story's strength, the single-source invisibility of the primary story, and every messiness rate. New checks are added, none are lost.
2. Every one of the 369 indicator events either appears in an artifact or is documented as unobservable, with a count per code.
3. All 62 unlogged events have at least one artifact, and the split is 44 telemetry / 15 adhesive-inferential / 3 human-only.
4. Every blank register cell listed in `capture-targets.csv` as fillable is genuinely derivable from the named artifact. Spot-check by hand on at least twenty.
5. Every `.eml` parses with `email.parser` and every thread chain resolves with no orphan `In-Reply-To`.
6. Every transcript's cited spans in `meeting-items.csv` land on real speaker turns.
7. Two runs are byte-identical. Same seed discipline as the register pack: no clock reads, named RNG streams, normalised archives.
8. The four planted stories are still at their stated strengths, and the primary story's artifacts contain the SW version the register rows are missing.
9. No real people, hospitals, or health bodies. Same rule as the register pack — the two real names already caught stay renamed.
