# `world.json` — schema

> **Private generator state.** Nothing in this file is ingested by the product.
> Renderers read `entities` and `events`. **`eval` is the answer key and no renderer may read it.**

This documents the frozen world produced by `tools/generators/world/`. It follows the sketch in
[`GENERATION-CONTRACT-V0.md` §5](../GENERATION-CONTRACT-V0.md) exactly where that sketch is
specified, and every extension beyond it is listed below with the reason it exists.

Top level is four keys and only four: `meta`, `entities`, `events`, `eval`.

---

## 0. Shape changes since the first freeze

Read this first if you wrote a renderer against the earlier file. Counts changed everywhere; these
are the changes to **shape**, which is what breaks silently.

| Change | Kind | What a renderer must do |
|---|---|---|
| `entities.employees[].absences[]` | **new field** — `{from, to, kind}` | Out-of-office and cover behaviour now has a source. Nobody authors anything inside their own absence, so sending gaps and leave agree. |
| `entities.device_units[]` unchanged, but `unit_state` now tracks a registration date | — | Surfaces as `registered` in the installed-base export; only ~58% of dispatched units are ever registered, and the fraction falls over time. |
| `meta.as_at` | **new field** — `2026-09-10` | The dataset's as-at, now *after* the last event rather than on top of it. |
| `meta.source_cutoffs` | **new field** — one date per system | **A renderer must not emit a record dated after its own cut-off.** |
| New event type `production_batch_released` | **new type**, 52 events | Carries the only serial↔module-lot path. See §4. |
| New event type `unit_decommissioned` | **new type**, 12 events | The end of the unit lifecycle; the unit leaves the installed-base denominator. |
| New event type `partner_correspondence` | **new type**, 16 events | Traffic with the US importer and the EU authorised representative. |
| `installed_base_sync` rows gained `manufactured` | **new field in a nested row** | The device master now carries a manufacture date — the first hop of the module-lot join. |
| `unit_shipped.build_dates` | **new field** — serial → build date | Same hop, on the dispatch row. |
| `customer_contact.ticket_comment_count` / `.ticket_status_changes` | **new fields** | How many comments and status changes the ticket accumulated. |
| `awareness_recorded.feedback_no` + `links.feedback` | **now always populated** | Previously null on the demo path. Every awareness event joins to its feedback record. |
| `vigilance_assessed.governing_awareness_at` / `_person_name` / `_employee_class` + `links.governing_awareness` | **new fields** | Exactly one governing awareness event per row, plus a `decision_recorded` of type `governing_awareness` that selected it. |
| `feedback_logged.duplicate_of_feedback_no`, `.void_reason` | **new fields**, nullable | Present only on `triage_state` `duplicate` / `void` rows. |
| `complaint_opened.date_received_basis` | **new field** | Which of the three candidate dates the register recorded. |
| Any fact whose value is a private id now ends in `_ref` | **renamed keys** | `owner` → `owner_ref`, `approved_by` → `approved_by_ref`, `lot_id` → `lot_id_ref`, `attendees` → `attendees_ref`, and so on. `observations[].knows` follows the rename. |
| `eval.trend_truth.denominator_sensitivity`, `.registration_coverage`, `.cohort_ranking` | **new eval blocks** | Answer key only. No renderer reads these. |

New enum values now present that were absent before: `complaint_opened.status` gains `open`,
`reopened`, `not_a_complaint`; `feedback_logged.triage_state` gains `duplicate`, `void`,
`unclassified`; `decision_recorded.decision_type` gains `reportability`, `capa_required`,
`closure`, `governing_awareness`; `vigilance_assessed.reportable` gains `pending` and
`clock_class` gains `5_work_day`; `device_serviced.disposition` gains `returned_as_is`,
`scrapped`, `replaced`. Values the world deliberately never contains are listed with a reason each
in `tools/generators/world/reachability.py:DELIBERATELY_ABSENT`, so an intentional gap cannot be
mistaken for a missing branch.

---

## 1. The one idea the whole file turns on

```text
event        what happened, with the complete truth in `facts`
observation  a source system noticing it: when, and which of those facts its users knew
```

A renderer writes a record **from an observation, never from the event**. So:

- If a field is missing from a rendered file, it is missing because the observing system's
  `knows` list did not contain it. Missingness is system behaviour, not a random null.
- If a field is *wrong* in a rendered file — a mangled serial, a loose organisation name, a
  contact's second address — the wrong surface form is in `as_written`. Renderers never invent
  a corruption.
- `at: null` means that system never saw the event at all. Its `knows` is then always `[]`,
  and the generator asserts that.

**Renderer contract:** for each event you care about, take *your* observation (`system == "erp"`,
`"support"`, …). Skip the event entirely if your observation is absent or `at` is null. Render only
the fact keys in `knows`, taking the value from `as_written[key]` if present, otherwise from
`facts[key]`.

---

## 2. `meta`

| Field | Notes |
|---|---|
| `dataset_version` | `0.1.0` |
| `seed` | `20260901`. Fixed in `tools/generators/world/config.py` and nowhere else. |
| `window` | `["2025-03-01", "2026-08-31"]` |
| `generated_at` | **Extension.** A fixed string, not the wall clock — byte-identical output is an acceptance criterion, and a real timestamp would break it. |
| `as_at` | **Extension.** `2026-09-10`. The simulation window ends 2026-08-31, but operational tails — a delivery booked in, a decision minuted, a Slack thread — run a few days past it. The as-at sits after the last event rather than on top of it. |
| `source_cutoffs` | **Extension.** The day each source system was exported, spread across 2026-09-02 … 2026-09-09. **A renderer must not emit a record dated after its own cut-off.** This is the "different export cut-off dates" imperfection `MOCK-DATA.md` asks for: two sources disagreeing about the latest record is a fact about when somebody ran the export, not a defect. Derived as the later of a declared export order and that system's own last record, so a source can never be exported before its own data. |
| `tz` | `Australia/Melbourne` |
| `generator` | **Extension.** Name and version of the producing generator, so a renderer can refuse a world it was not written against. |
| `notes` | **Extension.** Three sentences a renderer author should read before writing any code. |
| `counts` | **Extension.** Event totals by type plus derived counts. Lets a renderer sanity-check its input without walking 4,699 events. |

---

## 3. `entities`

Nine collections. The first four are the fixed cast and their sizes are asserted at build time:
**13 employees · 11 organisations · 17 sites · 38 contacts.**

### `employees[]`

Contract fields: `id` `name` `email` `dept` `role` `joined` `left` `employee_class`
`signature_block` `slack_handle`.

| Extension | Why |
|---|---|
| `display_name` | The form a person uses in their own signature, diacritics included, where the CRM and ERP exports flatten it. An entity-resolution surface, not a typo. |
| `alt_emails[]` | The "one person, two addresses" trap needs somewhere to live. |
| `title_as_written[]` | Roster titles are the answer key. The product must read a title off a signature — so each person needs two or three ways they actually write it. |
| `phone` | Signature blocks and CRM contact rows need one. |
| `tz` | Every timestamp needs a zone, including internal ones. |
| `absences[]` | `{from, to, kind}`. When somebody was not at work. An entity fact rather than only a pair of events, because every generator that picks an actor consults it and because the email renderer needs it to produce out-of-office replies that agree with the sending gaps. Parental leave also has `employee_leave_started` / `_ended` events, because it triggers an ownership handover; two-week annual leave does not. |

### `organisations[]`

Contract fields: `id` `legal_name` `trading_names[]` `market` `domain` `kind`.

| Extension | Why |
|---|---|
| `country` | ISO country, separate from `market` (`AU-VIC` is a market, `AU` is a country). Jurisdiction selection needs the country, not the sales region. |

`trading_names` carries the four written forms of ORG-03 that the roster's trap table requires.

### `sites[]`

Contract fields: `id` `org_id` `name` `city` `country` `tz` `ship_to_address`.

| Extension | Why |
|---|---|
| `region` | State or province. Appears in addresses and in market segmentation. |
| `name_variants[]` | A site is written loosely too, not just an organisation. |

### `contacts[]`

Contract fields: `id` `site_id` `org_id` `name` `emails[]` `role` `title_as_written[]`
`active_from` `active_to`.

| Extension | Why |
|---|---|
| `primary_email` | `emails[0]` is the address most systems hold; making it explicit stops five renderers picking differently. |
| `display_name`, `signature_block` | Attributes must be inferable from a signature, not asserted by the roster. |
| `tz`, `country` | Overnight replies from IE/NL/US must be a timezone fact, not a delay. |
| `site_history[]` | CON-04 moves SITE-02 → SITE-01 on 2025-11-15. Records either side belong to different sites; a single `site_id` cannot say that. |
| `shared_mailbox` | `biomed@schg.com.au` sends for CON-12 and CON-14. |

Contacts anchored to an organisation rather than a site (CON-31/32 at the importer, CON-37/38 at
the authorised representative) have `site_id: null`.

### `suppliers[]` — **whole collection is an extension**

`GENERATION-CONTRACT-V0.md` §4 forbids inventing an organisation, but `products.md` requires
supplier component lots and `PRIVATE-WORLD-V0.md` C3 requires a supplier CAPA. Three suppliers
therefore exist as a **separate collection with a `SUP-` prefix**, deliberately outside the eleven
organisations so they can never be counted as part of the entity-resolution cast:

| Id | Supplies |
|---|---|
| SUP-01 | PulseOne communications module, original source |
| SUP-02 | PulseOne communications module, second source |
| SUP-03 | PulsePatch assembly and sterile pouch (contract manufacturer) |

### `product_models[]`

`code` `family` `name` `kind` `udi_di` `denominator_basis` `nicknames[]`
`hardware_revisions[]` `serviceable_components[]`.

`denominator_basis` is an extension carrying the regulator's enum value per
[`REGISTER-SHAPES-V0.md` §7.1](../../../REGISTER-SHAPES-V0.md) — `active_installed_base` for
PulseOne, `units_distributed_in_period` for PulsePatch. It is a product fact, not a finding.

`nicknames[]` are the names customers use in free text.

### `device_units[]` — 900

Contract fields: `id` `serial` `hw_rev` `built` `sw_at_ship` `comms_module_lot` `market`.

| Extension | Why |
|---|---|
| `model`, `udi_di` | A renderer writing an installed-base row needs both without a second lookup. |
| `sw_at_build` | The version on the line, which is not always the version that ships. |

`market` and `sw_at_ship` are `null` for units never shipped (stock, scrap).

**Serial order is not build order.** Labels come off a pre-printed tray, so the generator shuffles
the serial pool within each revision before assigning build dates. That is what lets `SN-4471`
(H2.1, second-source module lot `CM-4412`, SITE-13 Dublin) and `SN-4417` (H2.1, original lot
`CM-4390`, SITE-06 Randwick) both be ordinary units without either being special-cased.

### `patch_lots[]` — 24

`id` `lot_code` `model` `product_revision` `packaging_revision` `artwork_revision` `mfg`
`released` `expiry` `qty_manufactured` `qty_released` `qty_scrapped` `contract_manufacturer`
`cm_production_ref` `supplier_component_lots{}` `udi_di`.

Product, packaging and artwork revisions are separate fields because `products.md` requires that a
change to one does not silently imply a change to the others.

### `sw_releases[]` — 6

`version` `released` `build` `compatible_hw[]` `note_kernel` `install_method` `approval_status`.

`note_kernel` is a short key, not prose — the QMS renderer writes the release note.

---

## 4. `events[]`

```jsonc
{
  "event_id": "EVENT-003795",
  "type": "device_occurrence",
  "at": "2026-06-12T16:20:00+01:00",   // always with a true UTC offset
  "tz": "Europe/Dublin",               // extension: the named zone, so a renderer can
                                       // write TZID=... in an ICS or an AEST-rendered export
  "actors":  { "employee": "EMP-10", "contact": "CON-25" },
  "subjects":{ "org": "ORG-07", "site": "SITE-13", "units": ["UNIT-000857"], "lots": [] },
  "facts":   { … the complete truth … },
  "source_keys": { "support_ticket": "TKT-7404" },   // extension, see below
  "links":   { "occurrence": "EVENT-003795", "same_occurrence_as": "EVENT-003802" },
  "observations": [ … ]
}
```

Events are sorted chronologically and `event_id` is issued in that order, so the id sequence reads
as a timeline.

### `source_keys` — extension

**The world issues every source-system key, not the renderers.** An email that quotes `TKT-7404`
and the support export that contains it have to agree, and only one writer can guarantee that.
Schemes follow [`GENERATION-CONTRACT-V0.md` §3.2](../GENERATION-CONTRACT-V0.md) exactly.

Numbers are assigned in a final pass (`numbering.py`) **in world time**, not in generator call
order, for two reasons:

1. Allocating at call time leaks the generator's execution order into the data — every complaint
   from one code path would carry a contiguous block of numbers. The demo journey's complaint
   number has to sit in the middle of the ordinary ones or a renderer could spot it.
2. Complaint numbers are issued when the record is *opened* while `date_received` is backdated to
   when the information arrived, so the register is legitimately **not** in date-received order —
   which §11 of the register shapes requires.

### `links` — extension

Named pointers to other `EVENT-` ids: `order`, `shipment`, `occurrence`, `contacts[]`, `feedback`,
`complaint`, `subject`, `about`, `same_occurrence_as`, `governing_awareness`.
`same_occurrence_as` is how three channels reporting one occurrence stay connected without any of
them owning it.

**Every `awareness_recorded` event carries `facts.feedback_no` and `links.feedback`.** Awareness
happens before anybody opens a feedback record — that is the point of the table — so the link is
written back once the record exists, and the answer key never has to re-derive it.

**Every `vigilance_assessed` event carries `links.governing_awareness`** plus
`facts.governing_awareness_at`, `governing_person_name` and `governing_employee_class`
([`REGISTER-SHAPES-V0.md` §4.7](../../../REGISTER-SHAPES-V0.md) requires exactly one per row, and
§5.5 asserts it as a grain invariant). Selecting it is a human act, so each row is accompanied by a
`decision_recorded` of `decision_type: "governing_awareness"` carrying the rationale, the selected
person, the selected instant and the named decider.

Different jurisdictions legitimately choose different events:

| Jurisdiction | Eligible classes | Why |
|---|---|---|
| US | `any_employee` · `mgmt_over_reg_sci_tech` · `ae_collection_duties` | 21 CFR 803.3(b)(2) — the 30-day period runs from awareness by **any** employee |
| EU | the three above **plus** `authorised_representative` · `outsourced_handler` | MDCG 2023-3 Q15 is broader on a different axis, with no seniority carve-out |

On the Dublin event that asymmetry is the whole beat: the US row runs from Hamish Doyle
(`any_employee`, Fri 18:40 +01:00) and the IE row from Lotte Janssen at the authorised
representative (`authorised_representative`, Fri 18:38 +01:00) — **before Asteria itself knew.**

### `facts` and the `_ref` convention — extension

A fact whose value is a private entity id has a key ending in **`_ref`** (`owner_ref`,
`decided_by_ref`, `attendees_ref`). The emitter renames these automatically and asserts the rule.
A `_ref` is a pointer a renderer must resolve to a name, an address or a source-system key —
**never something to print**. `observations[].knows` follows the rename.

Private ids also appear in `actors`, `subjects` and `links`. They appear **nowhere** in an
`as_written` value; that is asserted at build time.

### Two guarantees renderers can rely on

**1. Timestamps are internally consistent, always.** For every event and every
nested message, the offset in `at` is the offset its declared `tz` actually had at that
instant, across all three Australian DST transitions and the EU and US ones. `World.add()`
re-expresses the instant in the declared zone on the way in, and a check asserts it across the
whole file.

**There is no deliberate offset/timezone mismatch anywhere in `world.json`.** A record whose
offset disagrees with its own `tz` would be indistinguishable from a timezone bug, and
[`REGISTER-SHAPES-V0.md` §5.3](../../../REGISTER-SHAPES-V0.md) turns forty minutes into a
different regulatory deadline — a wrong offset does not read as a defect, it reads as a wrong due
date. Source-level timezone sloppiness is expressed instead by **how a system records time**, which
the renderer applies: ERP, installed base and service write naive local dates with no offset at
all; the support platform stores UTC and renders AEST; Gmail keeps the sender's true offset; Slack
uses epoch floats. Dropping an offset is the renderer's job. Lying about one is nobody's.

**2. A reply never predates what it answers, as an instant.** Within an email thread, message
instants are non-decreasing. Their *rendered local times* frequently are not — an Irish reply at
09:12 IST follows a Melbourne message sent at 17:40 AEST — and that is the overnight-reply trap
working as intended, not an ordering bug.

**3. Nobody signs anything before they joined or while they were away.** Every `actors.employee`,
every `*_ref` fact naming an employee, every meeting attendee and every message `from_ref` belongs
to somebody who had joined, had not left, and was not on leave that day. Work that would have
fallen to an absent person moves to a colleague in the same department. This is load-bearing:
contract §4 leans on EMP-13's March 2026 start to explain why US vigilance is underserved before
then, and a record she approved in January would destroy that explanation.

### `observations[]`

| Field | Notes |
|---|---|
| `system` | one of `erp` `crm` `support` `email` `slack` `service` `installed_base` `qms` `meetings` `pms` |
| `at` | when that system recorded it, with a true offset — or `null` for "never saw it" |
| `knows[]` | the `facts` keys this system's users had at that moment |
| `as_written{}` | **extension made mandatory:** fact key → the surface form this system actually holds. `{"serial": "4471"}`, `{"org": "Sth Cross Hospitals"}`. Absent key means the value is written plainly. |
| `record_kind` | **extension:** what kind of record this becomes — `ticket`, `delivery_note`, `work_order`, `complaint_register_row`, … so the renderer does not have to infer it from the event type. |
| `note` | **extension:** a sentence for the renderer author where the honest reason for an oddity is not obvious from the data (`"serial obtained by telephone after the ticket was opened"`). Never a conclusion about the dataset. |

A small set of `knows` keys are source-local rather than event facts and are allowed by the
validator: `ticket_ref`, `complaint_no`, `epoch`, `thread_ts`, `channel`, `author_handle`,
`text_kernel`, `messages`, `subject_kernel`, `actions`, `context`.

### Surface forms for serials

Chosen by *who is writing in which system*, never at random:

| Style | Who |
|---|---|
| `SN-4471` | service work orders, RMAs, installed-base exports |
| `4471` | nurses, in tickets and clinical email |
| `P1-100 #4471` | biomedical engineering, asset tags |
| `SN 04471` | one ERP export only |
| `s/n 4471` | Slack |
| `SN-4417` | the transcription error — one author, one thread, twice |

### Communications are events — extension to the sketch

`GENERATION-CONTRACT-V0.md` §5 keeps the top level at three keys, so communications are event
types rather than a fourth section.

**`email_thread`** — `facts.messages[]` each carrying `seq`, `from_kind`, `from_ref`,
`from_address`, `to[]`, `cc[]`, `at`, `tz`, `utc_offset`, `knows[]`, `as_written{}`, `intent`,
`in_reply_to`, `attachments[]`, and sometimes `note`. `facts.context` holds the values those
`knows` keys resolve to, so the email renderer never has to walk back to the linked event. A
message's `knows` is filtered to keys `context` can supply — a message cannot claim to know
something the world cannot give it.

**`slack_message`** — one event per message. `facts.epoch` is the Unix float Slack exports use;
`facts.thread_ts` points at the root message's epoch; `facts.context` again holds what the author
knew.

**`meeting_held`** — attendees, external attendees, duration, named timezone, `agenda_kernel[]`,
whether minutes were taken, and `actions[]` with action numbers, owners, due dates and statuses.
Two series run in `Europe/Dublin`.

The world decides *that* a communication happened and what its author knew. It does not write the
prose. `subject_kernel`, `text_kernel`, `narrative_kernel`, `agenda_kernel`,
`description_kernel`, `rationale_kernel` are all short keys for a renderer to expand.

### Event types

| Group | Types |
|---|---|
| People | `employee_joined` `employee_role_changed` `employee_leave_started` `employee_leave_ended` |
| Commercial | `customer_created` `partner_appointed` `partner_correspondence` `order_placed` `order_cancelled` `order_line_corrected` `unit_shipped` `patch_shipped` `accessory_shipped` `sales_activity` |
| Field | `unit_registered` `unit_installed` `unit_transferred` `unit_loaned` `unit_loan_returned` `product_returned` `device_serviced` |
| Product | `software_released` `software_upgrade_campaign` `installed_base_sync` `supplier_delivery_received` `production_batch_released` |
| Quality | `device_occurrence` `customer_contact` `service_request` `feedback_logged` `complaint_opened` `awareness_recorded` `decision_recorded` `vigilance_assessed` `nonconformity_recorded` `quality_action_opened` `audit_performed` `document_revised` |
| Communications | `email_thread` `slack_message` `meeting_held` |

**`device_occurrence` usually has an empty `observations` array.** That is the point: 633 of 695
physical occurrences in the world were never reported to anyone. They are invisible to every
renderer and they are the honest denominator the `eval` block uses.

### The module-lot join — `production_batch_released`

`PRIVATE-WORLD-V0.md` §1 says the join that would explain the field behaviour "is available in the
sources. It has simply never been made." This event type is what makes that true rather than
aspirational. One record per hardware revision per fortnight of manufacturing, and it is
deliberately awkward:

- **No serial list.** Serial labels come off a pre-printed tray, so a batch covers a build *date
  range*; `serial_block_hint` is a stores hint, not an allocation.
- **Two grammars for one lot.** The ERP production-consumption observation writes the component lot
  as `P1-COM-03 L4412`; goods receipt for the same lot, on `supplier_delivery_received`, writes
  `CM-4412`. Same lot, two documents, no string match.
- **The QMS device-history index carries the batch and its dates and no component lot at all.**

So the join costs three systems and a date range:

```text
serial  ──▶ manufacture date        installed-base device master
        ──▶ batch (built_from..to)  QMS device-history record index
        ──▶ component lot           ERP production order consumption
```

`comms_module_lot` appears in exactly one system's `knows` list — the ERP one — and the manufacture
date is exposed on the installed-base device master (`installed_base_sync` rows carry
`manufactured`) and on the dispatch row (`unit_shipped.build_dates`). Nothing else in the world
puts a serial next to a module lot.

**Difficulty is deliberately split.** Hardware revision plus software version is how the cohort is
*found* (a 2.9× elevation, available from the installed-base export alone). The module lot is how
the cause is *confirmed*, and nobody in the fictional company has ever had a reason to walk it.

**`service_request` is not feedback.** How-to questions, configuration help, RMA logistics and
portal access produce tickets but are not ISO 13485 §8.2.1 feedback. Only `feedback_logged` is the
net, and only some of that becomes `complaint_opened`.

---

## 5. `eval`

**No source renderer may read this block.** The freeze step strips it.

| Key | Content |
|---|---|
| `entity_truth` | every source identifier → private entity id; `ambiguous_addresses` for the shared mailbox; `must_merge` and `must_not_merge` pairs with the reason; `attribution_traps` including the site move |
| `event_truth` | which source records are one world event, near-duplicates that must **not** merge, how many occurrences were never reported, and both demo journeys resolved end to end |
| `field_truth` | per demo complaint: the defensible value of each mandated field, the candidate `date_received` values, which fields are honestly `explicitly_unknown` versus `not_yet_investigated`, and the conflicting serial claims |
| `clock_truth` | every awareness event with its `employee_class`, and per jurisdiction the governing awareness event, the rule, and the rule version |
| `trend_truth` | the affected cohort definition, its serials, monthly exposure and monthly link events, the true hazard, every complaint with a label, and the seven confounders as labelled negatives |

---

## 6. The denominator disagrees with itself, on purpose

The same numerator over three lawful-looking denominators does not give the same answer:

| Basis | Lawful for PulseOne? | Slope | Spearman | Verdict | C5 cancels? |
|---|---|---|---|---|---|
| `active_installed_base` | yes (§7.1: reusable) | +0.0018 | +0.28 | flat | **yes** |
| `units_distributed_in_period` | **no** — that basis is for consumables | +0.0025 | +0.29 | flat | yes |
| registered units | in practice, as a proxy | +0.0139 | +0.34 | **trending up** | **no** |

Registration coverage falls from 70% to 58% across the window (Spearman −0.93) because
registration is a customer act with a lag and the shipment rate accelerates. So complaints per
*registered* unit rise while complaints per *installed* unit stay flat. **The trend is in the
denominator, not in the device** — it is labelled `C8` in `eval`, and it was discovered rather than
designed.

Paired with a PMS plan that specifies no Art. 88 threshold, the honest product output is *"your
trend reverses depending on a denominator basis your plan does not specify"* — which is what §7.1
exists to express.

## 7. What the world deliberately does **not** say

No field named `is_signal`. No `root_cause` on an event. No event carries a cause at all.

The world records that a unit with hardware revision H2.1, communications module lot `CM-4412` and
software 1.2.1, in a ward flagged `ward_conditions: "warm"`, lost its patch connection for 55
seconds and recovered. Whether that is a pattern is an emergent property of 900 units, six software
releases and eighteen months of arithmetic — not an annotation.

The word "signal" does not appear anywhere outside `eval`, which is why device narratives say
*connection* and *link* rather than the product's own alert wording.
