# Asteria Mock Data — Generation Contract V0

> **Private generator state — never ingested by the product.**
> Everything in `plan/mock/` is the answer key. The product-facing dataset is `mock-company/`.

**What this is.** The single shared contract every generator task builds against. It closes the four open decisions in [`REGISTER-SHAPES-V0.md` §10](../../REGISTER-SHAPES-V0.md), fixes the identifiers and date windows [`roster.md`](roster.md) deferred, and defines the interface — `plan/mock/asteria/world/world.json` — that separates the world simulator from the source renderers.

Read this before touching anything. It is normative; where it disagrees with an earlier draft, this file wins.

```text
  plan/mock/asteria/          PRIVATE. answer key, root causes, world state.
    GENERATION-CONTRACT-V0.md   ← this file: decisions, IDs, dates, volumes
    PRIVATE-WORLD-V0.md         ← root cause, confounders, evaluation labels
    roster.md · entities.md · products.md
    world/world.json            ← the frozen simulated world (generated)
                    │
                    │  source renderers read world.json, write source-native files
                    ▼
  mock-company/              PRODUCT-FACING. immutable once frozen. no answer key, ever.
```

---

## 1. The four decisions, closed

### D1 · Asteria gets a small US presence — **yes**

[`REGISTER-SHAPES-V0.md` §10.1](../../REGISTER-SHAPES-V0.md) recommends it, and it is one line in the company model in exchange for the §803.3(b)(2) awareness asymmetry — the sharpest beat in the demo and the only one backed by 1,145 lines of already-verified research.

**The addition.** Asteria entered the US market in **February 2026** through a single initial importer, selling directly to one hospital network in Illinois. Roughly 90 PulseOne units and PulsePatch stock, two sites, seven months of history as at the freeze date. It is small, recent, and commercially marginal — which is exactly why the US regulatory obligations are *underserved* inside the fictional company, and why an RA specialist hired in March 2026 is still catching up.

This also earns two entities the register shapes need and could not otherwise justify:

| Entity | Why the schema needs it |
|---|---|
| US initial importer / US agent | `vig_external_id.scheme = fda_report_number`, and a second party who becomes aware of events |
| EU authorised representative | `awareness_event.employee_class = authorised_representative` — MDCG 2023-3 Q15 includes them with no seniority carve-out |

Markets at freeze: **AU** (primary), **IE**, **NL**, **US** (since Feb 2026).

### D2 · The planted signal is **PulseOne**

[`REGISTER-SHAPES-V0.md` §7.1](../../REGISTER-SHAPES-V0.md) argues it: PulseOne is reusable, so its denominator is `active_installed_base` or `episodes_of_use`, where cumulative data *is* acceptable — against PulsePatch's `units_distributed_in_period`, where it explicitly is not. One product family, two denominator bases, two aggregation rules, same register. That contrast is free only if the signal sits on the reusable side.

The root cause, its natural rate, its confounders, and the reason it is *not* trivially visible live in [`PRIVATE-WORLD-V0.md`](PRIVATE-WORLD-V0.md). **No source renderer may read the root cause.** Renderers read events; they do not read explanations.

**The governing constraint, restated because it is the easiest thing to lose.** [`MOCK-DATA.md`](../../MOCK-DATA.md) forbids deciding what the AI should find and then manufacturing confirming records. What we are allowed to do — and what §11 of the register shapes *requires* — is give the fictional world a plausible physical cause, let it produce events at an ordinary rate, and let each source observe those events imperfectly. The test is simple: **if a source record is only plausible because we know the answer, it is wrong.** Confounders are not decoration. A dataset where the signal is the only cluster is a dataset that proves nothing.

### D3 · Identifiers and date windows — fixed below (§3, §4)

### D4 · Holiday calendars — IE, NL, US federal, AU/VIC for 2025–2026

These are **product runtime reference data**, not mock company data. They ship at `reference-data/holidays/` and are a hard dependency of [`REGISTER-SHAPES-V0.md` §5.3](../../REGISTER-SHAPES-V0.md). They are the only files in this build that are allowed to state real-world facts.

---

## 2. Time

| Anchor | Value |
|---|---|
| Simulation window | **2025-03-01 → 2026-08-31** (18 months) |
| Manufacturing history before the window | from 2024-09 (units exist before they ship) |
| US market entry | 2026-02-09 |
| Freeze / dataset "as at" | **2026-09-10** |
| Per-source export cut-off | varies 2026-09-01 … 2026-09-09 — sources do *not* agree on what the latest record is |
| Company timezone | `Australia/Melbourne` (AEST/AEDT — **the DST shift is in scope**, see below) |

Every timestamp in every source is stored **with an offset**. Sources disagree about timezone the way real systems do:

| Source | Timezone behaviour |
|---|---|
| ERP, installed base, service | naive local dates, `Australia/Melbourne`, no offset recorded |
| Support platform | UTC in the API payload, rendered AEST in exports |
| Gmail | true `Date:` headers with the sender's real offset — IE/NL/US senders write in their own time |
| Sheets / XLSX | whatever the person typed, often a date with no time at all |
| Slack | Unix epoch floats |
| Calendar / ICS | `TZID=Australia/Melbourne` with `VTIMEZONE`, plus two events in `Europe/Dublin` |

Australian DST transitions inside the window: **2025-04-06**, **2025-10-05**, **2026-04-05**. At least one demo-relevant timestamp must land near one. [`REGISTER-SHAPES-V0.md` §5.3](../../REGISTER-SHAPES-V0.md) is explicit that a timestamp 40 minutes either side of midnight moves an EU deadline by a day; a DST shift is the same failure with a better excuse.

---

## 3. Identifier schemes

**The rule that governs all of them:** no private ID (`EMP-02`, `ORG-03`, `CON-14`, `UNIT-…`) may appear anywhere in `mock-company/`. Each source system invents its own keys. If the agent can grep a shared ID, entity resolution is free and the demo proves nothing.

### 3.1 Product identifiers

| Thing | Scheme | Range |
|---|---|---|
| PulseOne model | `P1-100` | — |
| PulseOne serial | `SN-####` | H1 `SN-1001`–`SN-1180` · H2 `SN-2001`–`SN-2260` · H2.1 `SN-4001`–`SN-4520` |
| PulsePatch model | `PP-72` | — |
| PulsePatch lot | `PP72-YYWWx` | `PP72-2503A` … `PP72-2634B`, 24 lots |
| Software version | semver | `1.0.0` `1.1.0` `1.1.1` `1.2.0` `1.2.1` `1.3.0` |
| Hardware revision | `H1` `H2` `H2.1` | |
| UDI-DI (PulseOne) | `09361234500017` | one per model, GS1-style, fictional |
| UDI-DI (PulsePatch) | `09361234500024` | |

**`SN-4471` and `SN-4417` must both be real, shipped, distinct units at different sites.** That is what makes the transcription conflict in §11 dangerous rather than cosmetic — a resolver that picks the "valid-looking" one is wrong 50% of the time, and only a human gate saves it.

Serials appear mangled in free text, by source and by author, **not randomly**:

```text
SN-4471      formal  — service work orders, RMA, installed-base exports
4471         nurses  — support tickets, clinical emails
P1-100 #4471 biomed  — biomedical engineering emails, asset tags
SN 04471     ERP     — leading-zero pad in one export only
s/n 4471     Slack   — lowercase, inline
SN-4417      the transcription error — appears twice, from one author, in one thread
```

### 3.2 Source-system keys (each system invents its own)

| System | Key format | Example |
|---|---|---|
| CRM | `A-####` accounts, `C-#####` contacts, `ACT-#####` activities | `A-1042` |
| Support | `TKT-####` | `TKT-8891` |
| ERP customer | `CUST-#####` | `CUST-10233` |
| ERP order / shipment | `SO-######` / `DN-######` | `SO-204471` |
| Installed base | `IB-######` | `IB-003318` |
| Service | `WO-#####` work order, `RMA-####` | `WO-21884` |
| QMS complaint | `CMP-YYYY-####` | `CMP-2026-0147` |
| QMS feedback | `FB-YYYY-####` | `FB-2026-0188` |
| QMS vigilance | `VIG-YYYY-####` | `VIG-2026-0042` |
| QMS NC / CAPA | `NCR-YYYY-###` / `CAPA-YYYY-###` | `CAPA-2026-004` |
| Controlled doc | `QMS-<TYPE>-###` | `QMS-SOP-014` |
| Action register | `ACT-YYYY-###` | `ACT-2026-117` |

**Complaint numbers are assigned at record creation, not at receipt.** So `CMP-2026-0147` may have an earlier `date_received` than `CMP-2026-0151`. [`REGISTER-SHAPES-V0.md` §11](../../REGISTER-SHAPES-V0.md) requires this; it falls out naturally if numbers are issued in creation order and receipt is backdated.

### 3.2b Regulatory classification — fixed, do not contradict

The QMS document set states these, so every downstream record must agree. They were undecided in
[`products.md`](products.md) and had to be settled because PSUR cadence (Art. 86) and PMS scoping
depend on them.

| Market | Classification | Consequence |
|---|---|---|
| EU | **Class IIa** (MDR Annex VIII, Rule 10) | PSUR required, updated at least every 2 years |
| AU | **Class IIa** | TGA — no clock rules loaded, see §1 D4 |
| US | **Class II** | 21 CFR 803 applies from the Feb 2026 market entry |

### 3.2c The effective vigilance procedure is AU/EU only

`QMS-SOP-004 Vigilance and Regulatory Reporting Rev 2` is the **effective** procedure and contains no
21 CFR Part 803 content at all. Rev 3, which adds it, is a draft still in review with the RA
specialist's edits on it.

This is not an oversight to be tidied up. US entry was February 2026, the RA specialist started in
March, and the procedure has not caught up — ordinary understaffing, exactly as §4 describes. Every
downstream record must be consistent with it: US reportability assessments in the window are being
made **without a procedure that covers them**, which is itself the kind of finding a real audit
produces. Do not generate records that imply a Part 803 procedure existed.

### 3.3 Email domains

| Party | Domain |
|---|---|
| Asteria | `asteriamedical.com.au` |
| Shared mailboxes | `support@` `quality@` `regulatory@` `service@` `sales@` |
| Customers | per [`roster.md`](roster.md) |

---

## 4. The extended cast

[`roster.md`](roster.md) fixes 12 employees, 8 organisations, 15 sites, 30 contacts. D1 adds the following and **nothing else**. No generator may invent a person, an organisation, or a site.

### New employee

| ID | Name | Department | Role | Joined |
|---|---|---|---|---|
| EMP-13 | Georgia Mbeki | Quality | Regulatory Affairs Specialist — vigilance submissions, US + EU | 2026-03-02 |

Her March 2026 start matters: events before it have **no** RA owner, which is why some awareness sits unactioned in a shared mailbox. That is ordinary understaffing, not a planted gap.

### New organisations

| Org ID | Organisation | Role | Market | Domain |
|---|---|---|---|---|
| ORG-09 | Meridian Medical Partners LLC | US initial importer & US agent | US — IL | meridianmedpartners.com |
| ORG-10 | Lakeshore Regional Health | Hospital network (customer) | US — IL | lakeshoreregional.org |
| ORG-11 | Bruggeman Regulatory Services B.V. | EU Authorised Representative | NL | bruggeman-ar.nl |

### New sites

| Site ID | Site | Org | Location |
|---|---|---|---|
| SITE-16 | Lakeshore Regional Medical Center | ORG-10 | Evanston, IL |
| SITE-17 | Lakeshore Northside Hospital | ORG-10 | Chicago, IL |

### New contacts

| ID | Name | Org / Site | Role |
|---|---|---|---|
| CON-31 | Brett Salazar | ORG-09 | Regulatory Manager, Meridian |
| CON-32 | Dana Whitlock | ORG-09 | Complaints Coordinator, Meridian |
| CON-33 | Renee Alcott | SITE-16 | Nurse Manager, Surgical Recovery |
| CON-34 | Miguel Ferraro | SITE-16 | Clinical Engineering |
| CON-35 | Terrence Oyelaran | SITE-17 | Nurse Manager |
| CON-36 | Paula Grady | SITE-17 | Materials Management |
| CON-37 | Wim Bruggeman | ORG-11 | Principal, EU AR |
| CON-38 | Lotte Janssen | ORG-11 | Vigilance Officer, EU AR |

**Totals at freeze: 13 employees · 11 organisations · 17 sites · 38 contacts.**

### Awareness classes — who starts which clock

This table is the reason `awareness_event.employee_class` exists. It is private; the product must derive it from signatures, titles, and who is CC'd.

| Person | `employee_class` | Starts §803.50 30-day | Starts §803.53(a) 5-work-day |
|---|---|---|---|
| EMP-09, EMP-10 (Sales) | `any_employee` | yes | **no** |
| EMP-05, EMP-06 (Support reps) | `any_employee` | yes | **no** |
| EMP-04 (Support Team Lead) | `mgmt_over_reg_sci_tech` | yes | yes |
| EMP-01 (Quality Manager) | `mgmt_over_reg_sci_tech` | yes | yes |
| EMP-02 (PMS Specialist) | `ae_collection_duties` | yes | yes |
| EMP-13 (RA Specialist) | `ae_collection_duties` | yes | yes |
| CON-37, CON-38 (EU AR) | `authorised_representative` | n/a | n/a — EU clock only |
| CON-31, CON-32 (Meridian) | `outsourced_handler` | see note | see note |

*Note:* Meridian is an initial importer with its own §803.40 obligations, not Asteria's complaint handler. Its awareness is recorded because the product must be able to show that it was — not because it starts Asteria's clock. That distinction is a `decision` row.

### The traps, extended

[`roster.md`](roster.md) fixes seven. D1 adds three that only exist once there is a second regulatory party:

| Trap | Where | What the agent must handle |
|---|---|---|
| Same fault, two reporters, two languages | CON-33 (nurse, US) and CON-34 (clinical engineering, US) report one event 6 days apart | One event, two channels — and the second arrival is not a new event |
| Forwarded chain loses the original sender | Meridian forwards a hospital email to `quality@` stripping headers; the `From:` is Meridian | The reporter is CON-33, not CON-32 |
| AR receives a copy the manufacturer does not | CON-38 is emailed directly by SITE-15; Asteria learns 4 days later | EU awareness starts at the AR, not at Asteria |

---

## 5. The world interface — `plan/mock/asteria/world/world.json`

The world simulator writes it. Every source renderer reads it and **nothing else**. It is the contract that lets five renderers run in parallel without editing each other's sources to force a cross-system result.

```jsonc
{
  "meta": { "dataset_version": "0.1.0", "seed": 20260901, "window": ["2025-03-01","2026-08-31"],
            "generated_at": "…", "tz": "Australia/Melbourne" },

  "entities": {
    "employees":     [{ "id":"EMP-02", "name":…, "email":…, "dept":…, "role":…, "joined":…, "left":null,
                        "employee_class":…, "signature_block":…, "slack_handle":… }],
    "organisations": [{ "id":"ORG-03", "legal_name":…, "trading_names":[…], "market":…, "domain":…, "kind":… }],
    "sites":         [{ "id":"SITE-06", "org_id":…, "name":…, "city":…, "country":…, "tz":…, "ship_to_address":… }],
    "contacts":      [{ "id":"CON-12", "site_id":…, "org_id":…, "name":…, "emails":[…], "role":…,
                        "title_as_written":[…], "active_from":…, "active_to":… }],
    "product_models":[{ "code":"P1-100", … }],
    "device_units":  [{ "id":"UNIT-000471", "serial":"SN-4471", "hw_rev":"H2.1", "built":…,
                        "sw_at_ship":"1.2.0", "comms_module_lot":…, "market":… }],
    "patch_lots":    [{ "id":"LOT-0014", "lot_code":"PP72-2603A", "mfg":…, "expiry":…, "qty_released":… }],
    "sw_releases":   [{ "version":"1.2.0", "released":…, "build":…, "compatible_hw":[…], "notes":… }]
  },

  "events": [
    { "event_id":"EVENT-000412", "type":"unit_shipped", "at":"2026-02-19T09:14:00+11:00",
      "actors":{…}, "subjects":{…}, "facts":{…},
      "observations":[                      // which systems saw it, when, and knowing what
        { "system":"erp",     "at":…, "knows":["order_no","ship_to","serials"] },
        { "system":"support", "at":null,  "knows":[] }
      ] }
  ],

  "eval": { /* NEVER rendered. cross-source ground truth, see PRIVATE-WORLD-V0.md */ }
}
```

Three rules on the interface:

1. **`observations` is how imperfection is generated.** A missing field is a system that did not know it, not a random null. Every omission in every rendered file must trace to an `observations[].knows` list.
2. **`eval` stays in `world.json` and is never copied into `mock-company/`.** The freeze step greps for it.
3. **Renderers never write back to `world.json`.** If a renderer needs a fact the world does not have, the world simulator adds it — otherwise two renderers invent two different versions of it.

---

## 6. Product-facing layout — `mock-company/`

```text
mock-company/
├── README.md                      what a new engineer reads first
├── source-manifest.yaml           per §7 — no cross-source mappings, no findings
├── CHECKSUMS.sha256
├── crm/            accounts.csv · contacts.csv · activities.csv · owner-history.csv
├── support/        tickets.jsonl · comments.jsonl · status-history.jsonl · attachments/
├── email/          support/ quality/ regulatory/ sales/ service/   (*.eml)
├── erp/            customers.csv · products.csv · orders.csv · order-lines.csv
│                   shipments.csv · shipment-lines.csv · lot-allocations.csv · returns.csv
├── installed-base/ device-units.csv · registrations.csv · version-observations.csv
├── service/        work-orders.csv · rma.csv · technician-notes.csv · attachments/
├── qms/            document-register.xlsx · controlled-documents/ · complaints/
│                   investigations/ · nonconformities/ · capa/ · audits/ · vigilance/
├── meetings/       calendar.ics · agendas/ · transcripts/ · minutes/ · action-register.xlsx
├── pms/            monthly-exports/ · working-analysis/ · review-minutes/ · approved-reports/
└── slack/          channels.json · users.json · <channel>/YYYY-MM-DD.json   (Slack export shape)

reference-data/
└── holidays/       ie-2025-2026.json · nl-2025-2026.json · us-federal-2025-2026.json · au-vic-2025-2026.json
```

---

## 7. Volume targets for V0

Bigger than [`entities.md`](entities.md)'s 60-ticket first seed — trend detection needs enough denominator to be honest — and smaller than [`asteria.md`](asteria.md)'s full scale, which no one will read. Sized so a human can audit any single thread end to end.

| Data | V0 target | Notes |
|---|---:|---|
| Employees | 13 | fixed cast |
| Organisations / sites / contacts | 11 / 17 / 38 | fixed cast |
| PulseOne units manufactured | ~900 | H1 180 · H2 260 · H2.1 460 |
| PulseOne units shipped | ~760 | rest in stock, loan pool, or scrapped |
| PulsePatch lots | 24 | ~3,000 boxes distributed |
| Orders / shipments | ~380 / ~420 | shipments ≠ orders; splits and partials exist |
| CRM activities | ~380 | |
| Support tickets | ~240 | ~700 comments |
| Email messages | ~600 | across ~220 threads |
| Slack messages | ~900 | 6 channels |
| Service work orders / RMAs | ~160 / ~70 | |
| Feedback events (QMS §8.2.1) | ~110 | the net |
| Complaints (QMS §8.2.2) | ~64 | the filter — and **not** every ticket |
| Vigilance obligations | ~24 | across US / IE / NL, incl. `90 not applicable` rows |
| NCs / CAPAs | 18 / 6 | stub detail only |
| Controlled documents / versions | 34 / ~60 | |
| Meetings / minutes | ~55 / ~30 | |
| Audits / findings | 5 / 14 | |

**The dataset must be mostly boring.** [`MOCK-DATA.md`](../../MOCK-DATA.md)'s acceptance criteria require routine, uninteresting operations alongside unusual activity. Target: **fewer than 1 in 8** feedback events relate to the planted cause. Shipping delays, training questions, adhesive complaints in hot weather, a docking connector that a biomed bent, three separate "the battery does not last a full shift" reports that are a charging-practice issue — these are the dataset, and the signal lives inside them.

---

## 8. The imperfections that are *required*, not optional

[`REGISTER-SHAPES-V0.md` §11](../../REGISTER-SHAPES-V0.md) makes six of these load-bearing. They are acceptance criteria, not flavour. Each one names the task that owns producing it.

| # | Requirement | Owner |
|---|---|---|
| 1 | `date_received` genuinely disputed — mailbox Fri 18:40, ticket Mon 09:10, complaint record Wed | email + support + qms |
| 2 | Serials arrive mangled; one true transcription conflict (`SN-4471`/`SN-4417`) survives to a human gate | all renderers |
| 3 | UDIs mostly blank — nurses do not read UDIs off labels, §820.35(a)(3) requires it anyway | support + qms |
| 4 | Complaint numbers not in `date_received` order | qms |
| 5 | At least one event reportable in one jurisdiction and not the other, two rationales | qms vigilance |
| 6 | PMS plan realistically **vague** about its Art. 88 threshold | qms documents |
| 7 | One person, two addresses; two Byrnes who are not the same person; a contact who moves site | all renderers |
| 8 | A shared mailbox (`biomed@schg.com.au`) sending for two different people | email |
| 9 | Org written four ways — "Southern Cross", "SCHG", "Sth Cross Hospitals", the legal name | crm + erp + email |
| 10 | Overnight replies from IE/NL that are *not* slow responses, only different timezones | email + slack |
| 11 | Register values that lag the repository — the document register says Rev 3, the folder holds Rev 4 | qms |
| 12 | "No fault found" outcomes, and technician findings that contradict the customer's symptom | service |
| 13 | A cancelled order and a corrected shipment line | erp |
| 14 | An obsolete controlled document still sitting in someone's personal Drive folder | qms |
| 15 | One spreadsheet with a formula error nobody noticed, and a hidden row | pms |

---

## 9. Rules every task obeys

1. **Write only into your own directory.** No task edits another task's output to make a join work. If a join is broken, the world is wrong — fix `world.json`, regenerate.
2. **No private IDs, no canonical cross-source keys, no evaluation labels in `mock-company/`.** The freeze step (`tools/freeze/leak_scan.py`) greps for `EMP-`, `ORG-`, `CON-`, `SITE-`, `UNIT-`, `EVENT-`, `LOT-0`, and evaluation vocabulary — *"answer key"*, *"ground truth"*, *"confounder"*, *"planted"*, *"private world"*. A hit fails the build.

   **The comms module lot code is explicitly allowed**, and an earlier draft of this rule that banned it was wrong. The three-hop join exists precisely so the lot *is* discoverable in a goods-receipt record. Banning the string forces every supplier lot into one grammar, which collapses the two-grammar design — ERP goods receipt writes `CM-4412`, ERP production consumption writes `P1-COM-03 L4412` — and turns a genuine cross-system join into a string match. The lot code is a fact a stores clerk types; it is not a conclusion.

   **The bare word `signal` is explicitly allowed.** An earlier draft of this rule banned it, which is a trap: PulseOne transmits a wireless signal, service notes say *signal strength*, and *safety signal* is ordinary PMS vocabulary. Banning the word makes honest records unwritable and pushes authors into stilted prose that itself reads as evasion. What must not appear is the *claim* — no record may assert that a group of events constitutes a signal, name a root cause, or otherwise state a conclusion the product is supposed to reach. The scanner checks for the claim, not the word.
3. **No source record may be plausible only because you know the answer.** If you cannot justify a record from what that system's users knew at that time, delete it.
4. **Deterministic.** Seed everything. `seed = 20260901`. Re-running a generator produces byte-identical output, or it is not finished.
5. **Source-native format or it does not count.** Markdown is for documentation and nothing else. A `.csv` that is really a Markdown table is a failed deliverable.
6. **Real-world facts are banned** except in `reference-data/holidays/`. No real hospitals, no real people, no real devices, no real incidents.
7. **Scripts are deliverables too.** Everything goes in `tools/generators/`, runnable, seeded, documented. The dataset must be reproducible from a clean checkout.

---

## 10. Build order

```text
  1  world simulator              plan/mock/asteria/world/world.json      ← blocks everything
     ├─ 2  ERP · CRM · installed base · support · service   (structured exports)
     ├─ 3  email · slack                                    (communications)
     ├─ 4  QMS documents · registers · quality records      (controlled content)
     ├─ 5  meetings · PMS working files                     (coordination + analysis)
     └─ 6  holiday reference data                           (independent, any time)
  7  freeze: manifest · checksums · leak scan · integrity checks
  8  evaluation set, derived after the freeze, stored outside mock-company/
```

Task 4's *company-level* content — quality manual, procedures, templates, org chart — depends only on this contract and can start immediately. Its *quality records* depend on the world.
