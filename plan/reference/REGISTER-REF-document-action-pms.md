# Register Shapes: Document, Training, Action, Risk, PMS

**Purpose.** The field-level shape of five QMS registers, with every field's status traced to a clause, a real template, or a named workflow in [`DIAGRAMS.md`](../DIAGRAMS.md). Companion to [`WORKFLOW.md`](../WORKFLOW.md), which owns the process topology; this file owns the table columns.

**Scope.** Document register, training register, action register, risk register / risk file index, PMS register(s). ISO 13485:2016 as the backbone, with FDA QMSR (21 CFR Part 820 as of 2 February 2026) and EU MDR 2017/745 obligations attached.

**Standing caveat.** ISO 13485:2016, ISO 9000:2015, ISO 14971:2019 and ISO/TR 20416:2020 are copyrighted standards. Clause numbers and titles are stated; requirement content is paraphrased and sub-item letters are cited, but requirement text is not reproduced. CFR and MDR text is public and is quoted directly. MDCG documents are public Commission-endorsed guidance and are quoted directly.

**Status vocabulary.** Exactly three values, used strictly:

- `Mandated` — a named regulation or standard clause requires this content. The clause is cited.
- `Convention` — not mandated; present in essentially every real register, commercial eQMS, or inspection-ready template. At least one real template or vendor/consultant source is cited, and labelled as such.
- `Product` — our own addition, needed by a numbered workflow in `DIAGRAMS.md`. The workflow number is cited.

**Deprioritisation declared up front.** Per the brief, depth went to the **document register (§2)** and the **PMS registers (§6)**. The **risk register (§5)** is the thinnest: I give the register shape and the index rows and stop at the boundary of the risk-management *process*, which is out of scope. The training register (§3) and action register (§4) are covered to full field level but with less commentary on edge cases. I did **not** cover: the audit-finding register as its own family, the change-control register, the supplier register, or the complaint/NC/CAPA registers (other families own those). I also did not resolve ISO/TR 20416:2020's internal clause numbering — it is paywalled and I had no second source.

---

## 0. The clause-numbering resolution

The brief asked me to resolve §4.2.3 vs §4.2.4 vs §4.2.5, noting that sources disagree and that `WORKFLOW.md` cites §4.2.4 for controlled-document approval and §4.2.5 for records.

**`WORKFLOW.md` is correct. The brief's framing is the legacy numbering.**

| Clause | Title (ISO 13485:2016) |
|---|---|
| 4.2.1 | General |
| 4.2.2 | Quality manual |
| **4.2.3** | **Medical device file** |
| **4.2.4** | **Control of documents** |
| **4.2.5** | **Control of records** |

Verified three independent ways:

1. **The standard's own table of contents**, inspected directly — 4.2.1 General, 4.2.2 Quality manual, 4.2.3 Medical device file, 4.2.4 Control of documents, 4.2.5 Control of records. The standard's Annex B correspondence table also maps 4.2.3 Medical device file to "No equivalent clause" in ISO 9001:2015, which is the tell: 4.2.3 is the *new* clause.
2. **21 CFR §820.35**, the QMSR control-of-records section, opens by building on **Clause 4.2.5 in ISO 13485** — a US federal regulation pointing at 4.2.5 as control of records is about as authoritative as a cross-reference gets.
3. **Independent secondary sources** describing 4.2.3 as the medical device file and 4.2.4–4.2.5 as document and record control.

**Why sources disagree.** ISO 13485:2003 and ISO 9001:2008 both numbered Control of documents as **4.2.3** and Control of records as **4.2.4**. ISO 13485:2016 inserted **Medical device file** as a new 4.2.3, pushing both down by one. Every pre-2016 template, consultant blog post, and internal procedure that was never renumbered still says 4.2.3/4.2.4. That is the entire source of the disagreement — it is a vintage problem, not a genuine ambiguity.

**Consequence for the mock data.** This is a realism gift rather than a problem. Asteria's own controlled procedures should contain the error: an older document-control SOP citing "ISO 13485 clause 4.2.3 (Control of Documents)" with a 2017 effective date, never corrected, while a newer PMS procedure cites 4.2.4 correctly. The product should be able to notice the divergence without treating either as authoritative.

**A second correction while I was in there.** §4.2.4 has **eight** sub-items, a) through h) — not the six that several secondary sources imply. They cover: review and approve prior to issue; review, update and re-approve; identification of current revision status and changes; availability of relevant versions at points of use; legibility and ready identifiability; identification and controlled distribution of external-origin documents; prevention of deterioration or loss; and prevention of unintended use of obsolete documents with suitable identification applied to them. Two further paragraphs then require that changes be reviewed and approved by the original approving function or another designated function with access to the pertinent background information, and that the organisation define the retention period for at least one copy of obsolete documents.

---

## 1. The shared provenance field set

I am the one looking across five registers, so this is the answer to the brief's cross-register question, stated once and referenced from each table as `[PROV]`.

**The design claim:** every register row is a *claim about the world asserted by someone at some time on some evidence*, and the evidence bundle (workflow 9) is only reconstructible if each row carries its own audit-grade biography. None of this is `Mandated` as register *content* — but §4.2.5's requirement that records remain legible, readily identifiable and retrievable, and that **changes to a record remain identifiable**, is the clause that makes an append-only provenance model the safe implementation rather than an indulgence.

All registers share these fields. Status is `Product` throughout unless noted.

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `row_id` | opaque stable id | `Product` | WF 9 | Platform identity. Never reused, never recycled on delete. |
| `tenant_id` | tenant ref | `Product` | [`MOCK-DATA.md`](../MOCK-DATA.md) multi-company expansion | Raw source ids collide across companies; resolution must happen inside the tenant boundary. |
| `record_class` | enum: `document` · `training_assignment` · `action` · `risk_item` · `pms_metric` · … | `Product` | WF 9 | Lets one evidence bundle span registers. |
| `source_system` | enum: `qms_repo` · `erp` · `crm` · `support` · `service` · `email` · `meetings` · `pms_working_files` · `product_db` · `platform` | `Product` | WF 1, WF 9 | `platform` means we created it; everything else means we observed it. |
| `source_record_id` | string, native | `Product` | WF 1 | The id *in that system*, unmodified. |
| `source_locator` | struct: file path · sheet name · cell range · row index · page · line · byte offset · message id · thread id | `Product` | WF 9 | "Cited the source location correctly" is an explicit extraction-evaluation criterion in `MOCK-DATA.md`. A sheet-and-cell locator is what makes a spreadsheet claim checkable. |
| `source_snapshot_id` | export/sync id | `Product` | WF 6, WF 9 | Which export this value came from. Without it, two disagreeing values look like a data bug instead of two honest observations of different snapshots. |
| `observed_as_of` | datetime + tz | `Product` | WF 6 | The source system's own notion of "as at". |
| `recorded_at` | datetime + tz | `Product` | WF 6 | When *we* learned it. These two axes must be separate — see the late-arriving-records policy in §6.4. |
| `extraction_method` | enum: `human_entry` · `connector_field` · `spreadsheet_cell` · `ocr` · `llm_extraction` · `deterministic_derivation` | `Product` | WF 1, WF 6 | WF 6's rule is that the agent "cites, it does not compute": any numeric field feeding a rate must be `deterministic_derivation` or a source cell, never `llm_extraction`. |
| `extraction_confidence` | 0–1, nullable | `Product` | WF 1 | Null for `connector_field` and `deterministic_derivation` — a confidence score on a directly-read field is noise. |
| `asserted_by` | struct: `actor_type` (`human` · `agent`) · person ref · agent id · model id · prompt/version hash | `Product` | WF 1–9 | `DIAGRAMS.md` requires every agent output to carry its autonomy level on its face; the model id and prompt version are what make a past agent output explainable a year later. |
| `authorship` | enum: `human_authored` · `agent_drafted` · `agent_drafted_human_accepted` · `agent_drafted_human_amended` | `Product` | WF 7 | The green-node rule: a draft accepted unchanged and a draft a human rewrote are different evidentiary objects. |
| `review_status` | enum: `unreviewed` · `accepted` · `amended` · `rejected` | `Product` | WF 1, WF 7 | `rejected` rows are retained, not deleted — a rejected agent proposal is evidence about the agent. |
| `reviewed_by` / `reviewed_at` | person ref / datetime | `Product` | WF 7 | |
| `evidence_refs[]` | list of (`source_record_id`, `source_locator`, `role`) where role ∈ `primary` · `corroborating` · `contradicting` | `Product` | WF 9 | The `contradicting` role is the one people forget and the one an auditor values. |
| `conflicts_with[]` | list of row_ids | `Product` | WF 1, WF 6 | Disagreement is modelled, not resolved silently. |
| `decision_id` | ref to a decision row, nullable | `Product` | WF 9 | Null until a human signs. This is the field that enforces "a green node never creates an approved record". |
| `decision_outcome` | enum: `approved` · `rejected` · `declined_with_rationale` · `deferred` · `no_action_required` | `Product` | WF 9 | **Negative decisions are first-class.** §8.2.2 permits declining to investigate with documented justification; §8.5.2's proportionality permits declining a CAPA. A register that can only represent "yes" cannot evidence either. |
| `decided_by` / `decided_at` / `decision_rationale` | person ref / datetime / text | `Product` | WF 9 | |
| `decision_authority_basis` | ref to approval-authority-matrix row | `Product` | WF 9 | `MOCK-DATA.md` lists an approval authority matrix as required V0 QMS content. "Who decided" is only half an answer; "and were they allowed to" is the other half. |
| `valid_from` / `valid_to` | datetime / datetime-or-null | `Product` | WF 9 | Bitemporal. Combined with `observed_as_of` / `recorded_at` this answers "what did the register say on the day the decision was made", which is the actual audit question. |
| `supersedes` / `superseded_by` | row_id refs | `Product` | WF 9 | Append-only chain. Mirrors §4.2.5's requirement that changes to a record remain identifiable. |

**The one-line version to socialise with the other register families:** every row carries *where it came from* (`source_*`, `source_locator`, `source_snapshot_id`), *when* on two clocks (`observed_as_of` / `recorded_at`), *who said so and how* (`asserted_by`, `extraction_method`, `authorship`), *what it rests on* (`evidence_refs[]` including contradicting evidence), *who signed and on what authority* (`decision_*`), and *what it replaced* (`supersedes`). Six groups. If another family's register is missing one of the six, workflow 9 breaks for that register only — and the bundle is only as good as its weakest register.

---

## 2. Document register

### 2.1 Is the register itself mandated? No — and this matters

**ISO 13485:2016 does not require a master document list.** §4.2.4 requires a documented procedure defining controls for the eight items above, including ensuring that "the current revision status of and changes to documents are identified" (sub-item c). A register is the normal way to satisfy (c), and it is what every auditor expects to be handed — but the *artefact* is convention, the *capability* is the requirement. Practitioners state this directly: one notes that ISO 13485 does not require it, while **Brazil's RDC 665/2022 does**, requiring that "A list of current documents shall be maintained to identify the documents' status and to ensure that only updated and approved documents are in use."

So: `Mandated` in Brazil, `Convention` under ISO 13485 and the QMSR. If Asteria ever registers in Brazil, the register becomes a regulated artefact. Flagging because it changes which fields are negotiable.

A second practitioner observation worth carrying into the mock data: maintaining a *live* list is described as impractical once records are in scope — "It would have been crazy to try to maintain a live list, as every new inspection record etc. would have to be added to it." This is the mechanism behind the register-lags-reality problem, not a sign of a sloppy company.

### 2.2 Grain

**One logical document × one revision.** Revision-grain, not document-grain.

This is the single most consequential grain decision in this note, and it deliberately differs from what real exports look like.

- **Real exports are document-grain**: one row per document, showing the *current* revision only. That is exactly why they lag — a new revision overwrites a cell rather than adding a row, so the register carries no memory.
- **Our register must be revision-grain**, because workflow 9 has to answer: *which revision of SOP-QA-007 was effective on 14 March, the day the reportability decision was made?* Document-grain cannot answer that at all. Revision-grain answers it with a `valid_from`/`valid_to` range lookup.
- A `current_revision` materialised view over the revision-grain table reproduces the document-grain export for people who want it.

Two sub-grains are also needed and should be separate tables, not crammed in:

- **Document-level row** (one per logical document): owner, retention class, periodic review interval, numbering, training-required flag. Things that are properties of the document, not of a revision.
- **Approval-signature row** (one per revision × signatory): §4.2.4 requires review and approval prior to issue and re-approval on change, by the original approving function or a designated function with access to the pertinent background information. Multiple signatories with different roles is the norm, so this is a child table.

### 2.3 Identity and numbering

Real schemes, all observed in the wild:

| Pattern | Example | Comment |
|---|---|---|
| Type prefix + sequence | `SOP-012`, `WI-204`, `FRM-031`, `POL-002`, `TMP-008` | Simplest; runs out of structure fast. |
| Type + function + sequence | `SOP-QA-012`, `WI-MFG-204`, `SPEC-ENG-0031` | Most common in 50–250-person manufacturers. |
| Clause-derived | `QOP-42-01` for Control of Documents, revision shown as a letter `(A)` | Real pattern — the `42` is ISO clause 4.2. Elegant until the standard renumbers, which is exactly what happened in 2016 (see §0). |
| Parent-child | `FRM-QA-012-01` as form 01 belonging to `SOP-QA-012` | Couples a form's identity to its parent procedure. Breaks when the form outlives the procedure. |
| Opaque sequential | `D-1047` | Used by companies that gave up on meaning. Actually the most robust. |

Revision schemes, equally varied: numeric (`1`, `2`, `3`), letter (`A`, `B`, `C`), zero-padded (`Rev 00` for first issue), or two-part (`1.0` released / `1.1` minor / `2.0` major) where the draft/released distinction is encoded in the number itself. A register that assumes one scheme will mis-sort another. **Store the revision as a string plus a monotonic integer `revision_ordinal` we derive** — sorting "10" before "9" is a real and embarrassing failure mode.

**What the row must carry to be findable:** `document_number` + `revision` is the citation key, but it is not sufficient. Findability in practice needs, in addition: the **title as written at that revision** (titles drift and people search the old one), **former document numbers** after a renumbering exercise, the **filename(s) as they appear in the repository** (which routinely disagree with the title), and the **storage locator** including dead ones. WORKFLOW.md's vocabulary table already warns about "references to renamed procedures"; former-number and former-title fields are the cheap fix.

### 2.4 Lifecycle / status values

`draft` → `in_review` → `approved` → `effective` → `superseded` → `obsolete` / `withdrawn`

The distinctions that earn their keep:

- **`approved` vs `effective`** — approval is a signature event; effectiveness is a date, usually later, and usually set to allow training to complete first. Collapsing them is common in real registers and destroys the training-gate logic in §3.
- **`superseded` vs `obsolete`** — superseded means a later revision took over; obsolete means the document is gone with no successor. Both are retained, both need "suitable identification" applied under §4.2.4 h).
- **`withdrawn`** — approved but pulled before or without ever becoming effective. Rare, and almost never representable in real registers, which is itself a realism detail.

§4.2.4 h) requires prevention of unintended use of obsolete documents *and* application of suitable identification to them, so `obsolete_marking_applied` is a real field, not decoration.

### 2.5 Retention periods — the actual rules

Three separate clocks, routinely conflated:

| Source | What it governs | The rule |
|---|---|---|
| ISO 13485 §4.2.5 | **Records** | Retain for at least the lifetime of the device as defined by the organisation, or as specified by applicable regulatory requirements, but **not less than two years from the medical device release by the organisation**. |
| ISO 13485 §4.2.4 (final paragraph) | **Obsolete documents** | The organisation defines the period for at least one retained copy. It must ensure documents to which devices were manufactured and tested are available for at least the device lifetime as defined by the organisation, but **not less than the retention period of any resulting record**, or as specified by regulation. So the document clock is bounded below by the record clock. |
| MDR Art. 10(8) | **Technical documentation + EU DoC + certificates** | "for a period of at least 10 years after the last device covered by the EU declaration of conformity has been placed on the market. In the case of implantable devices, the period shall be at least 15 years after the last device has been placed on the market." |

**21 CFR §820.35 specifies no retention period at all.** Confirmed by reading the section: it mandates record *content* for complaints (a), servicing (b), UDI (c), and a confidentiality marking provision (d), and nothing about duration. Under the QMSR the duration comes from ISO 13485 §4.2.5 by incorporation. The old §820.180(b) "not less than 2 years from the date of release for commercial distribution" language is no longer in Part 820's own text. Worth noting because a lot of internal procedures still quote it.

**The register implication:** retention cannot be a single number. It needs `retention_class` (a named rule, e.g. `device_lifetime_plus`, `mdr_td_10y`, `record_2y_floor`), `retention_basis_clause`, and a *derived* `retention_until` that is computed from an event that may not have happened yet — "10 years after the last device is placed on the market" is not a date you can store in 2026.

### 2.6 Field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `document_number` | string | `Convention` | OpenRegulatory QMS document list template (doc ID field); real procedure `QOP-42-01` | §4.2.4 c) requires revision status to be identified, which implies identity, but no clause names a "document number". |
| `revision` | string as written | `Mandated` | ISO 13485 §4.2.4 c) | Current revision status of and changes to documents shall be identified. |
| `revision_ordinal` | integer, derived | `Product` | WF 9 | Sort-safe. `Rev 10` must not sort before `Rev 9`. |
| `title` | string | `Convention` | OpenRegulatory template (title field) | |
| `title_at_revision` | string | `Product` | WF 9 | Titles drift between revisions; citations must resolve against the title as it read then. |
| `former_document_numbers[]` | list of strings | `Product` | WF 9 | Renumbering exercises orphan every prior citation. |
| `document_type` | enum: `manual` · `policy` · `procedure` · `work_instruction` · `form` · `template` · `specification` · `drawing` · `plan` · `report` · `record` · `external` | `Convention` | OpenRegulatory template (type field) | The `external` value carries §4.2.4 f). |
| `is_external_origin` | boolean | `Mandated` | ISO 13485 §4.2.4 f) | External-origin documents determined necessary for QMS planning and operation shall be identified and their distribution controlled. Standards, supplier specs, regulator guidance. Routinely missing from real registers. |
| `external_distribution_control` | text / controlled-copy list | `Mandated` | ISO 13485 §4.2.4 f) | |
| `status` | enum: `draft` · `in_review` · `approved` · `effective` · `superseded` · `obsolete` · `withdrawn` | `Convention` | OpenRegulatory template (version status); eQMS vendors tracking "document ID, title, owner, effective date, revision, and version status" | §4.2.4 implies the distinctions without naming the vocabulary. |
| `approved_date` | date | `Mandated` | ISO 13485 §4.2.4 a), b) | Review and approval for adequacy prior to issue; re-approval on change. |
| `effective_date` | date | `Convention` | eQMS practice: training "auto-launched when a new or revised controlled document becomes effective" | Distinct from approval. The gate for §3. |
| `obsoleted_date` | date, nullable | `Mandated` | ISO 13485 §4.2.4 h) | |
| `superseded_by_revision` | ref | `Mandated` | ISO 13485 §4.2.4 c) | |
| `obsolete_marking_applied` | boolean + method | `Mandated` | ISO 13485 §4.2.4 h) | Suitable identification applied to retained obsolete documents. |
| `approver(s)` | child table: person ref · role · signature method · date | `Mandated` | ISO 13485 §4.2.4 a), b) and the change-approval paragraph | Changes reviewed and approved by the original approving function or another designated function with access to the pertinent background information. The "designated function" wording is why `role` and a link to the approval-authority matrix matter, not just a name. |
| `author` / `originator` | person ref | `Convention` | OpenRegulatory template (owner field) | |
| `document_owner` | person ref / role | `Convention` | OpenRegulatory template (owner field); vendor guidance on assigning document owners with annual attestations | Should be a **role**, not a person — see §9 on owners who left. |
| `retention_class` | enum naming a rule | `Mandated` | ISO 13485 §4.2.4 final para, §4.2.5; MDR Art. 10(8) | The *period* is mandated; expressing it as a reusable class is ours. |
| `retention_basis_clause` | string | `Product` | WF 9 | So a retention claim is auditable rather than folklore. |
| `retention_until` | date, derived, nullable | `Product` | WF 9 | Null is legitimate and common — "10 years after the last device is placed on the market" has no value yet. |
| `periodic_review_interval` | duration, nullable | `Convention` | OpenRegulatory template (review date field) | §4.2.4 b) requires review and update *as necessary*; it does not mandate a fixed interval. Nearly every company invents one anyway. |
| `next_review_due` | date | `Convention` | OpenRegulatory template (review date field) | |
| `training_required` | boolean | `Convention` | eQMS practice of auto-generating training tasks on approval of a new or revised document | The join key to §3. |
| `training_population` | role list / group expression | `Convention` | eQMS training-population practice | |
| `storage_locator` | URI / UNC path / repository id | `Convention` | OpenRegulatory template; §4.2.4 d) availability requirement | §4.2.4 d) requires relevant versions available at points of use, which a locator serves; the column itself is convention. |
| `repository_filename` | string as it actually appears | `Product` | WF 9 | `MOCK-DATA.md` names "mismatched filenames and register metadata" as a document-variation behaviour. Storing both is how we detect it rather than paper over it. |
| `file_checksum` | hash | `Product` | WF 9 | The only deterministic way to answer "is the register's revision the file's revision". Directly attacks the register-lags-reality problem. |
| `repository_observed_revision` | string, nullable | `Product` | WF 9 | The revision the *file* claims, as distinct from the revision the *register* claims. When these differ, that is the finding. |
| `register_vs_repository_state` | enum: `agree` · `register_stale` · `repository_stale` · `file_missing` · `unknown` | `Product` | WF 9 | A first-class modelled disagreement, not an exception log line. |
| `medical_device_file_refs[]` | refs | `Mandated` | ISO 13485 §4.2.3 | Which documents belong to a device's medical device file. The clause requires the file; the register is where you find out what is in it. |
| `udi_relevance` | boolean / ref | `Mandated` | 21 CFR §820.35(c) | "The UDI must be recorded for each medical device or batch of medical devices." Affects which documents and records carry UDI. |
| `[PROV]` | see §1 | `Product` | WF 1, 7, 9 | |

### 2.7 Links out

- `document.revision` → **training assignment** (§3): one-to-many, keyed on `(document_number, revision)`, **not** on document alone. The whole point is that training is against a revision.
- `document.revision` → **change record / change control**: the authorisation for the revision to exist. Out of my scope but the foreign key is mine to declare.
- `document.revision` → **action** (§4): a CAPA action of the form "revise SOP-QA-012" closes against a specific revision becoming effective.
- `document.revision` → **risk file index** (§5): which risk-management documents are controlled, at which revision.
- `document.revision` → **PMS plan** (§6): the PMS plan is a controlled document *and* part of the technical documentation. The threshold-predated-the-signal argument in §6.4 is won or lost on this link.

---

## 3. Training register

### 3.1 What is mandated

ISO 13485:2016 **§6.2 Human resources** requires personnel performing work affecting product quality to be competent on the basis of appropriate education, training, skills and experience, requires the organisation to document the process(es) for establishing competence, providing needed training and ensuring awareness, and then lists five obligations a) through e): determine necessary competence; provide training or take other actions to achieve or maintain it; **evaluate the effectiveness of the actions taken**; ensure personnel are aware of the relevance and importance of their activities and how they contribute to the quality objectives; and maintain appropriate records of education, training, skills and experience. A note adds that the methodology for checking effectiveness is proportionate to the risk of the work concerned.

Three things follow that real registers get wrong:

1. **Effectiveness evaluation is mandated (c)**, not optional. A register with only "assigned / completed" cannot evidence (c).
2. **Awareness (d) is a separate obligation from training (b).** Nothing in a typical training matrix evidences awareness of the quality objectives.
3. **"Or take other actions" (b)** means training is not the only compliant response — reassignment, supervision, or a tooling change can satisfy competence. A register that can only record courses misrepresents the company.

Auditors request training matrices and competence/authorisation evidence for quality-impact roles, and the common finding is that "training records show completion dates but lack evidence that personnel are competent on *current* procedure revisions."

### 3.2 Grain

**One assignment = one (person × training requirement × document revision or competence element).**

Not one person, not one course, not one document. The revision is in the grain because the mandated failure mode is being trained on a superseded revision. A person retrained on `SOP-QA-012` Rev 4 after having completed Rev 3 has **two** rows, not an updated one.

A second table at **(role × requirement)** grain holds the training matrix / requirement definition — which roles need what. The assignment table is the instantiation.

### 3.3 Lifecycle / status values

`required` → `assigned` → `in_progress` → `acknowledged` → `assessed` → `completed` / `overdue` / `waived` / `superseded_before_completion` / `cancelled`

- **`acknowledged` vs `completed`** is the distinction that matters. Read-and-understand acknowledgement is a signature; completion may additionally require an assessment. eQMS practice is "read-and-understand training plus a short assessment to all people with a due date before the effective date", with "a secure electronic signature to acknowledge they have read and understood".
- **`waived`** needs a rationale and an approver, and maps to §6.2 b)'s "or take other actions".
- **`superseded_before_completion`** is the honest state for an assignment on Rev 3 that was still open when Rev 4 went effective. Real systems usually just close it silently.

### 3.4 The document-release → training-assignment link

This is the part the brief specifically asked for, and it is `Convention` with a strong evidence base rather than `Mandated`. No ISO 13485 clause says "a document release shall create a training assignment". What the clauses give you is: §4.2.4 a)/b) approval and re-approval, §4.2.4 d) availability at points of use, and §6.2 b)/c)/e) training and competence records. Companies join them because an auditor reading those three together will ask the question.

eQMS vendors implement it as a hard trigger: "The system automatically generates training tasks whenever a new or revised document is approved", with training "auto-launched when a new or revised controlled document becomes effective". Note the two different triggers in those two descriptions — **on approval** vs **on effectiveness** — which is precisely why §2.6 keeps `approved_date` and `effective_date` as separate fields. The defensible design is: assignment created on approval, due date set **before** effective date, so that the population is trained when the document takes force. `MOCK-DATA.md` already lists "Document releases cause training assignments" as a world-event dependency.

### 3.5 Field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `assignment_id` | id | `Convention` | eQMS training-management practice | |
| `person_ref` | person id | `Mandated` | ISO 13485 §6.2 e) | Records of education, training, skills and experience are per person. |
| `role_at_assignment` | string | `Product` | WF 8 | Roles change; the assignment was made against the role held then. Also the anchor for the departed-owner problem in §9. |
| `requirement_ref` | ref to (role × requirement) row | `Mandated` | ISO 13485 §6.2 a) | Necessary competence shall be determined. |
| `competence_element` | enum: `document_read_understand` · `practical_assessment` · `supervised_signoff` · `external_qualification` · `awareness_briefing` · `other_action` | `Mandated` | ISO 13485 §6.2 b) | "Training **or other actions**" is why `other_action` and `supervised_signoff` exist as values. |
| `document_number` / `document_revision` | refs | `Convention` | eQMS practice: acknowledgement "tied to the exact revision assigned" | The join key to §2. Nullable for non-document competences. |
| `trigger` | enum: `document_release` · `onboarding` · `role_change` · `periodic_requalification` · `capa_action` · `audit_finding` · `regulatory_change` · `manual` | `Product` | WF 8 | `capa_action` and `audit_finding` make §4's links out work. |
| `trigger_ref` | row_id in another register | `Product` | WF 8, WF 9 | |
| `assigned_date` | date | `Convention` | eQMS practice | |
| `due_date` | date | `Convention` | eQMS practice of a due date before the effective date | |
| `document_effective_date` | date, denormalised | `Product` | WF 9 | Carried on the row so "was the population trained before it took force" is answerable without a join at query time. |
| `status` | enum per §3.3 | `Convention` | eQMS training-status practice | |
| `acknowledged_at` | datetime, nullable | `Convention` | eQMS read-and-understand e-signature practice | |
| `acknowledgement_method` | enum: `e_signature` · `wet_signature_scanned` · `lms_click` · `attendance_sheet` · `email_reply` | `Product` | WF 9 | Evidential weight differs enormously across these. An attendance sheet photo and a Part 11-style e-signature are not the same evidence. |
| `assessment_result` | enum/score, nullable | `Mandated` | ISO 13485 §6.2 c) | Effectiveness of the actions taken shall be evaluated. |
| `effectiveness_method` | text / enum | `Mandated` | ISO 13485 §6.2 c) + its NOTE | The NOTE makes the method risk-proportionate, so the method must be recorded to show the proportionality judgement. |
| `effectiveness_evaluated_by` / `_at` | person ref / datetime | `Mandated` | ISO 13485 §6.2 c) | |
| `awareness_evidence` | ref / text | `Mandated` | ISO 13485 §6.2 d) | Separate from training. Almost always absent in real registers. |
| `trainer_ref` | person ref, nullable | `Convention` | training-matrix practice with a `Trainer` competence level | |
| `waiver_rationale` / `waiver_approver` | text / person ref | `Product` | WF 9 | A waiver is a negative decision and needs the same treatment as any other. |
| `prior_assignment_ref` | assignment id, nullable | `Product` | WF 9 | Chains Rev 3 → Rev 4 retraining so "has this person ever been trained on this document" is answerable. |
| `[PROV]` | see §1 | `Product` | WF 1, 9 | |

### 3.6 Links out

- **document revision → assignment**: the trigger link, §3.4.
- **assignment → action** (§4): an overdue assignment is an action. In practice companies track them in two places and they diverge.
- **assignment → CAPA**: "retrain the affected population" is a standard corrective action, and its effectiveness check is the assignment's `assessment_result`.
- **assignment → approval authority**: competence is frequently the precondition for signing authority. A signed approval by someone whose competence record does not cover that document is a finding, and it is a join our register can actually perform.

---

## 4. Action register

### 4.1 Mandate status — mostly convention, with two real anchors

The brief is right that this register is mostly convention. Being precise about *where* it is not:

**Anchor 1 — §5.6 Management review.** §5.6.1 requires documented procedures for management review and maintained records. §5.6.2 lists twelve mandated inputs a) through l), and **(i) is "follow-up actions from previous management reviews"**. §5.6.3 requires the output to be recorded and to include **the input reviewed** and any decisions and actions related to a) improvement to maintain QMS suitability, adequacy and effectiveness; b) improvement of product related to customer requirements; c) changes needed to respond to applicable new or revised regulatory requirements; d) resource needs.

So: actions with their status, carried forward from review to review, are mandated *content* of the management-review record. The register is the mechanism. §5.6.3's demand that the record include the **input reviewed** as well as the decisions is unusual among management-system standards and has a direct field consequ— an action must carry *what evidence was in front of the meeting*, not just what was decided.

**Anchor 2 — §8.2.4 Internal audit.** Audit criteria, scope, interval and methods shall be defined and recorded. Records of the audits and their results, including identification of the processes and areas audited and the conclusions, shall be maintained. Management responsible for the area audited shall ensure necessary **corrections and corrective actions** are taken **without undue delay**. Follow-up activities shall include **verification of the actions taken and the reporting of verification results**.

That yields four mandated fields outright: an owner defined as the management responsible for the audited area; a timeliness obligation ("without undue delay" — deliberately not a number); a verification-of-action step distinct from completion; and a **reporting of the verification result**, which is a fifth state most registers lack.

Note the clause says "corrections **and** corrective actions" — the ISO 9000:2015 3.12.2 / 3.12.3 distinction `WORKFLOW.md` is built on shows up here as a mandated field on audit actions specifically.

Everything else — due dates, priority, escalation, overdue flags, percent-complete — is `Convention`. Management review and CAPA are among the most commonly cited clauses in ISO 13485 audits and FDA inspections, with findings that reviews are "deferred or informally conducted without structured documentation" and required inputs missing, which is the inspection pressure that produced the convention.

### 4.2 Grain

**One action.** One row per discrete committed action with one accountable owner.

Rejected alternatives and why:

- *One row per action-occurrence-per-meeting* — which is what minutes-derived registers naturally produce, and why `MOCK-DATA.md` notes "actions described differently in minutes and trackers". The same action restated in three sets of minutes is one action with three mentions, not three actions.
- *One row per owner* — an action with a changed owner is the same action. Ownership changes go in a child table, because workflow 8 needs the assignment history to chase the right person, and §9's departed-owner problem is unanswerable without it.

Child tables at: `(action × owner assignment)`, `(action × status transition)`, `(action × mention in a source record)`.

### 4.3 Identity and numbering

Real patterns: `MR-2025-03-04` (management review, meeting date, item index); `IA-2025-07-012` (internal audit, year, finding); `CAPA-0043-A2` (action 2 within CAPA 43); and the depressingly common `Item 7` with no prefix at all, unique only within one minutes document. The last one is the realism case: an action whose only identifier is a row position in a Word table is exactly what workflow 8 has to cope with, and exactly why `source_locator` in §1 is load-bearing.

To be findable a row needs: a stable `action_id` we mint, the `source_reference_text` as the humans wrote it ("Action 7, QMR minutes 2025-03-04"), and the `source_record_ref` + locator. Without the middle one, a person searching for what they remember finds nothing.

### 4.4 Lifecycle / status values

`proposed` → `open` → `in_progress` → `blocked` → `awaiting_verification` → `verified` → `closed`, plus `overdue`, `cancelled`, `superseded`, `transferred`.

- **`overdue` is not a status, it is a derived predicate** (`due_date < today AND status NOT IN (verified, closed, cancelled)`). Storing it as a status is the single most common action-register modelling error and it guarantees the register goes stale between refreshes. Compute it; never store it.
- **`awaiting_verification` → `verified`** is the §8.2.4 follow-up requirement made explicit: verification of the actions taken, and reporting of the verification result. Most registers jump straight to closed.
- **`cancelled` needs a rationale and an approver.** An action cancelled without a recorded reason is a finding waiting to happen, and under §5.6.2 i) it will be asked about at the next review.
- **`transferred`** — the action survives, the owner changes. Distinct from cancelled-and-reopened, which is what people actually do and which destroys the age metric.

### 4.5 Field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `action_id` | id | `Convention` | action-register practice; `MOCK-DATA.md` lists an action register as a required V0 template | |
| `source_reference_text` | string as humans wrote it | `Product` | WF 8, WF 9 | "Action 7, QMR minutes 2025-03-04". The searchable handle. |
| `source_type` | enum: `management_review` · `internal_audit` · `external_audit` · `notified_body_audit` · `capa` · `complaint` · `nonconformity` · `pms_review` · `risk_review` · `meeting` · `regulatory_commitment` · `other` | `Mandated` (partially) | ISO 13485 §5.6.2 a)–l); §8.2.4 | The twelve §5.6.2 input categories are mandated; the enum is our union of them with the other lanes. |
| `source_record_ref` | row_id in the originating register | `Mandated` (for audit and MR) | ISO 13485 §5.6.3 (output includes the input reviewed); §8.2.4 (records of audits and results) | The link out that makes workflow 9 possible. |
| `action_class` | enum: `correction` · `corrective_action` · `preventive_action` · `improvement` · `administrative` | `Mandated` | ISO 13485 §8.2.4 ("corrections and corrective actions"); ISO 9000:2015 3.12.2 / 3.12.3 | `WORKFLOW.md` §11 item 5 already requires this distinction to be enforced in the data model. This is where it lands for actions. |
| `description` | text | `Convention` | action-register practice | |
| `owner_ref` | person ref | `Mandated` (for audit actions) | ISO 13485 §8.2.4 | "The management responsible for the area being audited shall ensure…" — the owner is defined by the clause, not chosen. |
| `owner_role` | role / function | `Product` | WF 8 | Survives the person leaving. See §9. |
| `owner_assignment_history[]` | child table: person · role · from · to · reassigned_by · reason | `Product` | WF 8 | Workflow 8 must route a chase to the *current* owner while evidencing who held it when. |
| `due_date` | date | `Convention` | action-register practice | Not mandated. §8.2.4 says "without undue delay" and §8.5.2 is similar — both deliberately refuse a number. |
| `due_date_history[]` | child table: date · changed_by · changed_at · reason | `Product` | WF 8, WF 9 | `MOCK-DATA.md` lists "changed owners and due dates" as expected meeting-record behaviour. Silent extension is the thing an auditor looks for. |
| `timeliness_basis` | text | `Mandated` | ISO 13485 §8.2.4; §8.5.2 proportionality | How "without undue delay" was judged for this action. Rarely recorded; directly answers the obvious audit question. |
| `status` | enum per §4.4 | `Convention` | action-register practice | |
| `is_overdue` | boolean, **derived at query time** | `Product` | WF 8 | Never stored. |
| `completion_evidence_refs[]` | refs | `Convention` | inspection-ready practice | |
| `verification_required` | boolean | `Mandated` (for audit actions) | ISO 13485 §8.2.4 | Follow-up shall include verification of the actions taken. |
| `verified_by` / `verified_at` / `verification_result` | person ref / datetime / enum `effective` · `not_effective` · `inconclusive` | `Mandated` (for audit actions) | ISO 13485 §8.2.4 | |
| `verification_reported_to` / `_at` | person/forum ref / datetime | `Mandated` (for audit actions) | ISO 13485 §8.2.4 | The *reporting of verification results* is a separate mandated step. Almost never a field in real registers. |
| `mr_output_category` | enum: `qms_improvement` · `product_improvement` · `regulatory_response` · `resource_need` | `Mandated` (for MR actions) | ISO 13485 §5.6.3 a)–d) | The four categories the output must cover. Lets us show a review addressed all four. |
| `carried_forward_from[]` | action_id refs | `Mandated` (for MR actions) | ISO 13485 §5.6.2 i) | "Follow-up actions from previous management reviews" is a mandated review input. This field *is* that input. |
| `inputs_reviewed_refs[]` | refs | `Mandated` (for MR actions) | ISO 13485 §5.6.3 | The output must include the input reviewed — evidence that was in front of the meeting, not just the conclusion. |
| `cancellation_rationale` / `cancelled_by` | text / person ref | `Product` | WF 9 | Negative-decision discipline from §1. |
| `mentions[]` | child table: source_record_ref · locator · verbatim_text · observed_as_of | `Product` | WF 8, WF 9 | One action, many retellings. `MOCK-DATA.md`: "Actions described differently in minutes and trackers." This table is how we hold both without picking a winner. |
| `[PROV]` | see §1 | `Product` | WF 1, 8, 9 | |

### 4.6 Links out

- **action → source record**: mandated for audit (§8.2.4) and management review (§5.6.3). The single most important foreign key in this register.
- **action → document revision** (§2): "revise SOP-QA-012" closes when Rev 5 goes effective, not when someone ticks a box.
- **action → training assignment** (§3): "retrain the ward-support team" closes on the assignment's effectiveness evaluation.
- **action → risk item** (§5): a risk control measure is an action, and §5's `risk_control_verification` is its verification result.
- **action → PMS period** (§6): actions arising from a PMS review or PSUR. MDCG 2022-21 requires the PSUR executive summary to give "a brief description and status of actions taken by the manufacturer based on the previous PSUR" — so the action register is a mandated *input* to the PSUR, which makes this link regulatory rather than convenient.
- **action → CAPA**: a CAPA's plan is a set of actions; the CAPA's effectiveness check is a distinct action with its criteria defined before implementation.

---

## 5. Risk register / risk file index

Deprioritised per the brief. Register shape only.

### 5.1 Mandate status

**ISO 14971:2019 does not mandate a "risk register".** It requires a **risk management file**, and clause **4.5** requires that file to provide **traceability for each identified hazard** to the risk analysis, the risk evaluation, the implementation and verification of the risk control measures, and the results of the evaluation of residual risk. Traceability here means the manufacturer can locate the applicable records and documents, which may be scattered across PLM, DHF, test reports and a post-market database.

The familiar spreadsheet — hazard, sequence of events, hazardous situation, harm, severity, probability, risk, control, verification, residual risk — is **`Convention`**: the universal implementation of 4.5's traceability requirement, not a mandated artefact.

**ISO 13485:2016 §7.1 Planning of product realization** requires the organisation to document one or more processes for risk management in product realization and to maintain **records of risk management activities**, with a NOTE pointing at ISO 14971. So §7.1 mandates records, not a register. That is the correct relationship: §7.1 is the QMS hook, ISO 14971 is the method, the register is the company's choice of container.

**MDR** then adds the benefit-risk layer: Annex I Sections 1 and 5 are the benefit-risk provisions Article 88 points at, and Annex I Section 3 is the risk-management requirement that Annex III 1.1(b)'s indicators and thresholds must feed back into. MDCG 2025-10 states that the indicators and threshold values used in continuous benefit-risk reassessment "should be covered in the PMS plan and be linked to the risk management documentation (as referred to Annex I, section 3 MDR/IVDR)". **That sentence is the seam between this register and §6**, and it is the reason they cannot be designed independently.

### 5.2 Grain

**One hazardous situation.** Not one hazard.

ISO 14971's chain is hazard → foreseeable sequence of events → hazardous situation → harm. One hazard produces many hazardous situations, each with its own probability and severity. Hazard-grain registers are common and they systematically understate risk because they force one probability onto many situations.

For PulseOne/PulsePatch: "loss of wireless link" is one hazard; "loss of wireless link during the night shift while the nurse is in another bay, alert not heard" and "loss of wireless link at handover, unnoticed for 40 minutes" are two hazardous situations with different probabilities and plausibly different harms.

A second, coarser table — the **risk file index** — sits at **one controlled risk-management document per row**, and is what makes clause 4.5 traceability demonstrable. It is a specialised view of §2's document register, not a separate universe.

### 5.3 Lifecycle / status values

Risk item: `identified` → `analysed` → `evaluated` → `control_planned` → `control_implemented` → `control_verified` → `residual_risk_evaluated` → `accepted` / `not_acceptable_further_control_required`, plus `reopened_by_post_production_information` and `superseded`.

That last-but-one value is the ISO 14971:2019 point: clause 10 on production and post-production activities was extensively revised and aligned with ISO 13485 clause 8, and the file must be maintained while the device is on the market. A risk register without a "reopened by post-market information" state cannot represent the loop that workflow 6 exists to feed.

### 5.4 Field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `risk_item_id` | id | `Convention` | universal risk-table practice | |
| `hazard` | string / taxonomy ref | `Mandated` | ISO 14971:2019 cl. 5.4 | Identification of hazards and hazardous situations. |
| `foreseeable_sequence_of_events` | text | `Mandated` | ISO 14971:2019 cl. 5.4 | |
| `hazardous_situation` | text | `Mandated` | ISO 14971:2019 cl. 5.4 | The grain. |
| `harm` | string / taxonomy ref | `Mandated` | ISO 14971:2019 cl. 5.5 | |
| `severity` | ordinal scale ref + value | `Mandated` | ISO 14971:2019 cl. 5.5 | The *scale definition* must be a controlled document; store the scale ref, not a bare integer. |
| `probability` (or P1/P2 decomposition) | ordinal / quantitative | `Mandated` | ISO 14971:2019 cl. 5.5 | The P1 (hazardous situation occurs) × P2 (leads to harm) split is `Convention` from ISO/TR 24971 practice, not a 14971 requirement. |
| `risk_before_control` | derived | `Mandated` | ISO 14971:2019 cl. 5.5, cl. 6 | |
| `risk_acceptability_criterion_ref` | ref to risk management plan revision | `Mandated` | ISO 14971:2019 cl. 4.4, cl. 6 | Criteria come from the plan, and the plan is a controlled document — so this is a link into §2 at a specific revision. |
| `risk_control_measures[]` | child table: measure · type (`inherently_safe_design` · `protective_measure` · `information_for_safety`) · implementation ref · verification ref | `Mandated` | ISO 14971:2019 cl. 7 | The three-level hierarchy and its order are the standard's. |
| `control_implementation_verified` / `control_effectiveness_verified` | refs | `Mandated` | ISO 14971:2019 cl. 4.5, cl. 7 | 4.5 names verification of risk control measures specifically. Two distinct verifications, routinely merged. |
| `residual_risk` | derived | `Mandated` | ISO 14971:2019 cl. 7 | |
| `new_risks_introduced_by_control[]` | refs | `Mandated` | ISO 14971:2019 cl. 7 | A control that creates a new hazardous situation must be traced. |
| `overall_residual_risk_contribution` | ref | `Mandated` | ISO 14971:2019 cl. 8 | Evaluation of overall residual risk is a separate clause from per-item residual risk. |
| `benefit_risk_rationale_ref` | ref | `Mandated` | MDR Annex I §§1, 5; ISO 14971:2019 cl. 8 | MDR Art. 88 points at Annex I Sections 1 and 5 for the benefit-risk analysis a trend could significantly impact. |
| `expected_frequency_baseline` | rate + denominator definition + source | `Mandated` (via MDR) | MDR Art. 88(1); Annex III §1.1(b); MDCG 2025-10 | **The join to §6.** The baseline a trend is measured against lives here, and MDCG 2025-10 says thresholds "are to be established in the pre-market phase". If this field is empty, Art. 88 is unanswerable. |
| `expected_undesirable_side_effect` | boolean + IFU ref | `Mandated` | MDR Art. 88(1); Annex I §23 (information supplied by the manufacturer) | Art. 88 covers "expected undesirable side-effects"; "expected" means declared somewhere. The IFU reference is what makes it expected. |
| `post_production_information_refs[]` | refs to complaints, service records, PMS periods | `Mandated` | ISO 14971:2019 cl. 10; ISO 13485 §8.4 | The feedback loop. Workflow 6's output lands here. |
| `risk_file_document_refs[]` | refs into §2 at revision | `Mandated` | ISO 14971:2019 cl. 4.5 | The traceability requirement, made into a field. |
| `review_status` / `last_reviewed_at` / `reviewed_against_revision` | enum / datetime / ref | `Mandated` | ISO 14971:2019 cl. 9, cl. 10 | Risk management review before commercial distribution, then maintained. |
| `[PROV]` | see §1 | `Product` | WF 6, 9 | |

### 5.5 Links out

- **risk item → risk file document** (§2): clause 4.5 traceability.
- **risk item → PMS metric** (§6): via `expected_frequency_baseline`. Bidirectional: the baseline sets the threshold, the observed rate updates the baseline.
- **risk item → action** (§4): a risk control measure is an action with a verification result.
- **risk item → complaint / NC / CAPA**: post-production information under clause 10.

---

## 6. PMS register(s) — and the denominator problem

This is the deepest section, per the brief.

### 6.1 What is mandated, precisely

| Source | Requirement |
|---|---|
| **MDR Art. 83** | Plan, establish, document, implement, maintain and update a PMS system as part of the QMS, proportionate to risk class and device type, actively and systematically gathering data across device lifetime. |
| **MDR Art. 84** | Document it in a PMS plan addressing every element of Annex III Section 1.1; the plan is part of the technical documentation. |
| **MDR Art. 85** | Class I — PMS report, updated when necessary, available to the competent authority on request. |
| **MDR Art. 86(1)** | PSUR for Class IIa/IIb/III. Shall set out the results and conclusions of PMS data analyses, the rationale and description of any preventive and corrective actions, **"the volume of sales of the device and an estimate of the size and other characteristics of the population using the device and, where practicable, the usage frequency of the device"**. Class IIb/III annually; Class IIa at least every two years. |
| **MDR Art. 86(2)** | Class III and implantables — submitted electronically to the notified body via the electronic system. |
| **MDR Art. 88(1)** | "Manufacturers shall report, by means of the electronic system referred to in Article 92, any statistically significant increase in the frequency or severity of incidents that are not serious incidents or that are expected undesirable side-effects that could have a significant impact on the benefit-risk analysis referred to in Sections 1 and 5 of Annex I and which have led or may lead to risks to the health or safety of patients, users or other persons that are unacceptable when weighed against the intended benefits." The manufacturer must specify how such incidents are managed and **the methodology for determining a statistically significant increase, as well as the observation period, in the PMS plan referred to in Article 84**. |
| **MDR Annex III §1.1(b)** | The plan shall cover, among other things, "a proactive and systematic process to collect any information referred to in point (a)" that allows correct characterisation of device performance and comparison with similar products; "effective and appropriate methods and processes to assess the collected data"; "suitable indicators and threshold values that shall be used in the continuous reassessment of the benefit-risk analysis and of the risk management as referred to in section 3 of Annex I"; "effective and appropriate methods and tools to investigate complaints and analyze market-related experience collected in the field"; "methods and protocols to manage the incidents subject to the trend report as provided for in Article 88 MDR…, including the methods and protocols to be used to establish any statistically significant increase in the frequency or severity of incidents as well as the observation period"; communication protocols; procedures to fulfil Art. 83/84/86 obligations; systematic procedures to identify and initiate appropriate measures including corrective actions; and a PMCF plan or a justification for its absence. |
| **ISO 13485 §8.4** | Analysis of data — documented procedures to determine, collect and analyse data demonstrating QMS suitability and effectiveness, covering feedback, conformity to product requirements, characteristics and trends of processes and product including opportunities for preventive action, and suppliers. |

**Refinement to `WORKFLOW.md` §5.** `WORKFLOW.md` says the Art. 88 comparison baseline "must be specified in the technical documentation and product information". That is right in effect but imprecise about the locus, and the imprecision matters for field design. The operative requirements are: Art. 88(1) second subparagraph puts the **methodology and the observation period in the PMS plan**; Annex III §1.1(b) puts the **indicators and threshold values in the PMS plan** and links them to Annex I Section 3 risk management; and MDCG 2025-10 adds that thresholds "are to be established in the pre-market phase" and "should be covered in the PMS plan and be linked to the risk management documentation". The PMS plan is itself part of the technical documentation (Annex III's own title is "Technical documentation on post-market surveillance"), so `WORKFLOW.md` is not wrong — but the field we must be able to show is a **reference to a specific revision of the PMS plan with an effective date earlier than the signal**, plus its link into the risk file. "It's in the technical documentation somewhere" does not survive an Art. 88 challenge. The "product information" half of the claim maps to Annex I Section 23 — expected undesirable side-effects being declared in the IFU — which is a different field (§5.4 `expected_undesirable_side_effect`).

### 6.2 Grain — three registers, not one

This is where I differ most from how the source systems will look. `MOCK-DATA.md` describes PMS working files as "monthly exports" and "manually maintained analysis spreadsheets", which are period-grain workbooks. Our register cannot be.

**Register 6A — PMS period register. Grain: one (device grouping × region × observation period × snapshot).**

- *Device grouping*, not product: MDCG 2022-21 requires datasets "split by Basic UDI-DI or model of the device if the Basic UDI-DI does not exist", and reporting at device, device group (CMD) or device group/family level. PulseOne and PulsePatch are separate groupings; a PSUR may cover both under a leading device.
- *Region*: MDCG 2022-21's tables are split "EEA+TR+XI" and "Worldwide", with worldwide including EEA, TR and XI. Region is in the grain, not a filter, because the rates differ and the reporting obligations differ.
- *Observation period*: Art. 88(1) requires the observation period in the plan; MDCG 2022-21 structures data as "Reporting Day + preceding 12 months (N); N − 12 months (N2); N2 − 12 months (N3); N3 − 12 months (N4)" for Class III/IIb and 24-month windows for Class IIa.
- ***Snapshot*** — **this is the one nobody puts in the grain and it is the whole ballgame.** The same (grouping, region, period) recomputed in March and in September gives different numbers, because late records arrived. Both are correct as at their snapshot. If snapshot is not in the grain, you either overwrite history (and can never reproduce the PSUR you submitted) or you store two rows that look like a data-integrity bug.

**Register 6B — PMS metric register. Grain: one (metric definition × device grouping × region × period × snapshot).**

A period has many metrics: complaint rate, non-serious incident rate by IMDRF device-problem code, service-call rate, NFF rate, return rate, adhesion-failure rate. Each has its own numerator definition, its own denominator, and its own threshold. Flattening metrics into columns on the period row means every new metric is a schema change and no metric can carry its own denominator. **Metric-per-period, long-format.**

**Register 6C — PMS source-inclusion register. Grain: one (period × snapshot × contributing source record).**

The answer to the brief's "which complaints and service records it aggregated". Without this table, a rate is a number with no audit trail, and workflow 9 cannot walk backwards from a trend report to the complaints underneath it. This table is large and boring and it is the most valuable one here.

**So: one period per product per region per snapshot (6A); one metric per that (6B); one source record per that (6C).** Answering the brief's question directly: *not* one period, *not* one product, *not* one period-per-product — period × product-grouping × region × snapshot, with metrics one level below.

### 6.3 Identity and numbering

- `pms_period_id`: `PMS-{grouping}-{region}-{period_start}-{period_end}-S{snapshot_seq}`.
- `psur_reference_number`: **`Mandated`-adjacent.** MDCG 2022-21 requires the PSUR cover page to include at least the manufacturer information, devices covered, notified body name and organisation number, "PSUR reference number assigned by the manufacturer", version number of the PSUR, the data collection period covered, and a table of contents. It further requires the reference number to be attached to the "leading device" and to "remain unchanged for the PSUR updates, provided the 'leading device' within the grouped devices has remained the same". So the register must carry a `leading_device_ref` and detect when it changes.
- `basic_udi_di`: the canonical grouping key.
- Findability also needs the **PMS plan revision** in force for the period, since that is where the thresholds live.

### 6.4 The denominator problem — the fields that make a rate reproducible

A rate is reproducible if and only if a reader can recompute it from the row. That requires all of the following, and the register is defective if any is missing.

**(1) Numerator definition.**

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `numerator_definition_ref` | ref to a controlled metric definition at revision | `Mandated` | MDR Annex III §1.1(b) "methods and processes to assess the collected data" | Must be a *versioned reference*, not free text. Changing a definition mid-series is the most common way a trend is faked, intentionally or not. |
| `numerator_event_class` | enum: `complaint` · `non_serious_incident` · `serious_incident` · `expected_undesirable_side_effect` · `service_call` · `return` · `nff` | `Mandated` | MDR Art. 88(1) (non-serious incidents / expected undesirable side-effects); Annex III §1.1(a) | Art. 88 applies to a *specific* subset. A register that cannot distinguish non-serious incidents from complaints cannot compute the Art. 88 numerator at all. |
| `numerator_taxonomy_codes[]` | IMDRF AET codes | `Mandated` | MDCG 2022-21 | "The following IMDRF Adverse Event Terminologies, terms and codes should at least be utilized: Annex A: Medical Device Problem; Annex C: Cause Investigation - Investigation Findings; Annex D: Cause Investigation - Investigation Conclusion; Annex F: Health Effects - Health Impact", with Level 2 terms satisfactory and Level 1 acceptable when Level 2 is unavailable. Store the level used. |
| `numerator_count` | integer | `Mandated` | MDR Art. 86(1) | |
| `numerator_inclusion_rule` | text + executable predicate | `Product` | WF 6 | What was counted and what was excluded. The predicate is what makes the calculation deterministic, per WF 6's "agent cites, it does not compute". |
| `numerator_deduplication_rule` | text + ref | `Product` | WF 1, WF 6 | `MOCK-DATA.md`: one event arrives through three channels. Whether those are one or three is a numerator decision with a bigger effect than most threshold choices. |

**(2) Denominator definition and source.**

The `Mandated` core here is stronger than the brief assumed. **Art. 86(1) mandates the denominator**: "the volume of sales of the device and an estimate of the size and other characteristics of the population using the device and, where practicable, the usage frequency of the device". That is numerator-free — it exists so rates can be formed.

MDCG 2022-21 then gives the official menu. The manufacturer should consider all devices placed on the market: "This could be volumes of sales, units shipped, or units implanted or another suitable indicator. **Whichever method is used should be consistent throughout the PSUR in all areas to allow for a comparison of data.**" And it must "Indicate to what criteria the number of devices on the market is provided":

- Devices placed on the market or put into service
- Units distributed within each time period
- **Number of episodes of use (for reusable devices)**
- **Active installed base**
- Units distributed from the date of declaration of conformity or EC/EU mark approval to the end date of each time period
- Number of devices implanted
- Other — description/rationale should be provided

Its rate tables carry the footnote "The denominator is compatible to the number of devices in table 1 or based on manufacturer's reasoning e.g. reusable instruments".

MDCG 2025-10 independently lists, as examples of "the measurable values" a PMS plan should enumerate: "batch, batch quantity, hours/frequency of use, number of devices in use/sold, number of exposures, etc."

And MDCG 2022-21 is explicit that sales are not exposure: "Estimate the number of patients exposed, as the sales numbers alone do not necessarily reflect the number of uses of the device (usage frequency)."

**For Asteria this resolves cleanly and differently per product family, which is the point of the portfolio:**

- **PulsePatch PP-72** — single-use, lot-controlled, discarded after ≤72 hours. Denominator = **units distributed within the period** (boxes × 10, by lot, by ship-to region). Exposure ≈ units used ≈ units distributed with a lag and a wastage/expiry fraction. Needs a `denominator_adjustment` for stock-in-transit and expired-unused stock.
- **PulseOne P1-100** — reusable, serialised, multi-patient. Units shipped is the **wrong** denominator and would understate risk by a factor that grows every year the fleet ages. Correct choices are **active installed base** (device-months at risk) or **number of episodes of use**. `products.md` already defines a use-session object with a synthetic encounter ID, start/end timestamps, serial and lot — that is the episodes-of-use denominator, and it is the better one, but it is only available where sessions are observed.
- **The honest problem:** PulseOne's installed base is not knowable exactly. `products.md` states shipment does not prove installation, registration does not prove current location, "some customers never register devices", and a service record may be the most recent trustworthy configuration observation. So the denominator is an *estimate with a method*, which is exactly what Art. 86(1) says ("an estimate of the size and other characteristics of the population"). The register must carry the estimation method, not pretend to a count.

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `denominator_basis` | enum: `placed_on_market` · `units_distributed_in_period` · `episodes_of_use` · `active_installed_base` · `cumulative_units_since_doc` · `devices_implanted` · `other` | `Mandated` | MDCG 2022-21 ("Indicate to what criteria the number of devices on the market is provided") | The enum values are MDCG's own list. `other` requires `denominator_rationale`. |
| `denominator_value` | numeric | `Mandated` | MDR Art. 86(1) | |
| `denominator_unit` | enum: `units` · `device_months` · `episodes` · `patient_exposures` · `usage_hours` · `boxes` · `lots` | `Mandated` | MDCG 2025-10 measurable-values list ("batch, batch quantity, hours/frequency of use, number of devices in use/sold, number of exposures") | `device_months` is the one that makes a reusable-device rate comparable across periods of unequal length. |
| `denominator_is_estimate` | boolean | `Mandated` | MDR Art. 86(1) ("an estimate") | |
| `denominator_estimation_method_ref` | ref to a controlled method at revision | `Mandated` | MDR Art. 86(1); Annex III §1.1(b) | For PulseOne: shipped minus decommissioned minus known-replaced, with a registration-gap correction. The method must be a controlled document or the estimate is unauditable. |
| `denominator_source_systems[]` | list of (system, snapshot_id, as_of) | `Product` | WF 6, WF 9 | ERP shipments, product database registrations, service records. Each with its own snapshot — they will not agree. |
| `denominator_rationale` | text | `Mandated` | MDCG 2022-21 ("Other – description/rational should be provided") | |
| `denominator_consistency_key` | string | `Mandated` | MDCG 2022-21 ("consistent throughout the PSUR in all areas") | A checkable token asserting that every metric in a PSUR used the same basis. Makes a mandated consistency obligation machine-verifiable. |
| `denominator_adjustments[]` | child table: type (`in_transit` · `expired_unused` · `returned_unused` · `decommissioned` · `registration_gap`) · value · basis | `Product` | WF 6 | The difference between shipped and at-risk. Where most of the real argument lives. |
| `usage_frequency_estimate` | numeric + method, nullable | `Mandated` (conditional) | MDR Art. 86(1) "where practicable, the usage frequency of the device" | Nullable, but if null, the register must say **why not practicable** — that is the conditional mandate's evidence. |
| `population_characteristics` | struct | `Mandated` | MDR Art. 86(1); MDCG 2022-21 Table 3 | "Characteristics of the population using the device is defined by the manufacture based on the usage of device" — so the characteristic definition is itself a field. |

**(3) Observation period.**

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `observation_period_start` / `_end` | date / date | `Mandated` | MDR Art. 88(1) ("as well as the observation period, in the post-market surveillance plan") | |
| `observation_period_basis_ref` | ref to PMS plan revision | `Mandated` | MDR Art. 88(1); Annex III §1.1(b) | The period must have been *specified in the plan*, not chosen after the fact. |
| `period_sequence_key` | (N, N2, N3, N4) | `Convention` | MDCG 2022-21 year-on-year structure | |
| `period_contiguity_check` | enum: `contiguous` · `gap` · `overlap` | `Mandated` | MDCG 2022-21: "the end of data collection period for one PSUR marks the start date of the next PSUR's data collection period", to "avoid any gap or overlap of data" | A computable check on a mandated property. Cheap, and catches a real class of error. |
| `period_change_justification` | text, nullable | `Mandated` (conditional) | MDCG 2022-21: "In case the data collection period is changed by the manufacturer, a justification should be provided, and a statement should be provided whether the change affects the comparability of the results gained" | Two fields really — the justification and the comparability statement. |
| `comparability_statement` | text | `Mandated` (conditional) | MDCG 2022-21, as above | |
| `data_collection_period_anchor` | date + basis | `Mandated` | MDCG 2022-21: "The data collection period should start at the device MDR certification date. If the device is not MDR-certified, the data collection period starts at MDR Date of Application (26 May 2021)." | |

**(4) Snapshot / data-cut date.**

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `snapshot_at` | datetime + tz | `Convention` | MDCG 2022-21's "Reporting Day + preceding 12 months" framing implies a reporting day; `MOCK-DATA.md` lists "Snapshot dates differ between sources" as expected PMS-working-file behaviour | No clause names a field called "data cut date". The concept is unavoidable; the field is convention. |
| `snapshot_sequence` | integer | `Product` | WF 6, WF 9 | Which recomputation of this period this is. |
| `snapshot_reason` | enum: `scheduled` · `psur_preparation` · `recomputation_after_late_records` · `definition_change` · `correction` · `ad_hoc_query` | `Product` | WF 6 | `definition_change` is the dangerous one and must be visibly distinct from `recomputation_after_late_records`. |
| `per_source_as_of[]` | child table: system · snapshot_id · as_of · record_count | `Product` | WF 6, WF 9 | **The single most important field in this register.** `MOCK-DATA.md` says snapshot dates differ between sources as a matter of ordinary behaviour. A period-level snapshot date that hides six different source as-of dates is a lie of convenience. |
| `snapshot_frozen` | boolean | `Product` | WF 9 | Once a snapshot backs a submitted PSUR or trend report it is immutable. Corrections create a new snapshot. |
| `submitted_artefact_refs[]` | refs | `Product` | WF 9 | Which PSUR / PMS report / trend report this snapshot backs. |

**(5) Late-arriving records policy.**

`MOCK-DATA.md` names "Late data entry", "Backdated formal records", "Different export cut-off dates" and "Late-arriving complaints included in later reviews" as ordinary behaviours, not errors. The register must treat late arrival as normal.

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `late_record_policy_ref` | ref to controlled procedure at revision | `Product` | WF 6 | No clause mandates a policy, but the number is indefensible without one. Two legitimate policies: attribute by event date (restating prior periods) or by awareness date (never restating). Both are defensible; mixing them is not. |
| `attribution_basis` | enum: `event_date` · `awareness_date` · `record_creation_date` | `Product` | WF 6 | **This is the field that makes two honest analysts disagree by 30%.** `WORKFLOW.md` §5 already establishes that the vigilance clock runs on *awareness*; if PMS attributes by event date and vigilance by awareness date, the two will never reconcile — and that must be visible rather than surprising. |
| `late_arrivals_since_prior_snapshot` | integer + refs | `Product` | WF 6, WF 9 | |
| `restates_prior_snapshot` | boolean + ref | `Product` | WF 6 | |
| `restatement_delta` | numeric | `Product` | WF 6 | How much the prior published number moved. The honest disclosure. `MOCK-DATA.md`'s analysis-evaluation criteria ask explicitly whether missing periods or late records are disclosed. |

**(6) Baseline / threshold, and where it was pre-committed.**

The brief's sharpest requirement: the register must be able to show the threshold predated the signal.

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `baseline_rate` | numeric + unit | `Mandated` | MDR Art. 88(1); Annex III §1.1(b) "suitable indicators and threshold values" | |
| `baseline_source_ref` | ref to risk file item at revision | `Mandated` | MDCG 2025-10: indicators and thresholds "should be covered in the PMS plan and be linked to the risk management documentation (as referred to Annex I, section 3 MDR/IVDR)" | The link to §5's `expected_frequency_baseline`. |
| `threshold_value` | numeric / expression | `Mandated` | MDR Annex III §1.1(b) | MDCG 2025-10 glosses threshold values as "limits beyond which action should be taken". |
| `threshold_method_ref` | ref to PMS plan revision + statistical method | `Mandated` | MDR Art. 88(1) ("the methodology for determining any statistically significant increase") | The method, not just the number. |
| `threshold_committed_in_document` | ref to controlled document | `Mandated` | MDR Art. 88(1); Annex III §1.1(b) | |
| `threshold_committed_revision` | revision string | `Mandated` | as above | |
| `threshold_committed_effective_date` | date | `Mandated` | MDCG 2025-10: thresholds "are to be established in the pre-market phase" | |
| `threshold_predates_signal` | boolean, **derived**: `threshold_committed_effective_date < signal_first_detected_at` | `Product` | WF 6, WF 9 | **The field that answers the Art. 88 challenge in one cell.** Derived, never stored as an assertion, and it joins §2 (document register, at revision) to §6. This is the concrete reason the document register's revision-grain decision in §2.2 is not academic: document-grain cannot evaluate this predicate. |
| `threshold_change_history[]` | child table: old · new · changed_in_document_revision · effective_date · rationale | `Product` | WF 6, WF 9 | A threshold raised *after* a signal appeared is the finding. Modelling it is the only way to be able to show it did not happen. |
| `statistical_test` | enum + parameters | `Mandated` | MDR Art. 88(1) | Practitioner guidance stresses that use of statistics must be justified rather than automatic. |
| `signal_first_detected_at` | datetime | `Product` | WF 6 | |
| `threshold_breached` | boolean, derived | `Product` | WF 6 | |
| `signal_review_outcome` | enum: `no_action` · `monitor` · `investigate` · `trend_report_submitted` · `capa_opened` · `fsca` | `Mandated` (partly) | MDR Art. 88(1); Annex III §1.1(b) "systematic procedures to identify and initiate appropriate measures including corrective actions" | `no_action` must be recordable with a rationale — workflow 6's G1/G2 are human gates and `WORKFLOW.md` lists the Art. 88 submission decision as a hard human gate. |
| `benefit_risk_impact_statement` | text | `Mandated` | MDR Art. 88(1) ("significant impact on the benefit-risk analysis referred to in Sections 1 and 5 of Annex I"); MDCG 2022-21 requires a clear and bold benefit-risk statement in the PSUR | |

**(7) Source inclusion — register 6C.**

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `period_snapshot_ref` | ref | `Product` | WF 9 | |
| `source_record_ref` + `source_locator` | refs | `Product` | WF 9 | |
| `counted_in_numerator` | boolean | `Product` | WF 6 | |
| `exclusion_reason` | enum: `duplicate_of` · `out_of_period` · `out_of_region` · `different_product` · `not_an_incident` · `insufficient_information` | `Product` | WF 6 | **Exclusions are evidence.** A rate is only defensible if you can show what you threw away and why. |
| `duplicate_of_ref` | ref, nullable | `Product` | WF 1, WF 6 | |
| `event_date` / `awareness_date` / `record_created_date` | dates | `Product` | WF 6 | All three, always. `attribution_basis` picks which one drives the period assignment; keeping the other two is what lets a reviewer re-derive the number under a different policy. |
| `[PROV]` | see §1 | `Product` | WF 1, 6, 9 | |

### 6.5 Links out

- **PMS period → complaint records, service work orders, returns, support tickets**: via register 6C. The brief's "which complaints and service records it aggregated", answered by a table rather than a join guess.
- **PMS period → PMS plan revision** (§2): the thresholds, indicators and observation period. At revision.
- **PMS metric → risk item** (§5): baseline in, observed rate out. MDCG 2025-10's explicit PMS-to-risk-management interface.
- **PMS period → action** (§4): actions arising, and — mandated by MDCG 2022-21 — the status of actions from the *previous* PSUR.
- **PMS period → PSUR / PMS report artefact**: the submitted document, with its `psur_reference_number`, version number and leading device.
- **trend signal → vigilance**: Art. 88 reporting via the Art. 92 electronic system, which is a different clock from Art. 87. `WORKFLOW.md` §5 owns that.

---

## 7. The evidence-bundle problem (workflow 9), stated as a cross-register contract

Workflow 9 has no gate because nothing is decided — it only retrieves, and `DIAGRAMS.md` says plainly that it "works only if the eight workflows above kept their provenance as they went". The shared field set in §1 is the mechanism. Four properties it must deliver, and the field that delivers each:

1. **Walk backwards from an approved decision to a source message.** `decision_id` → `evidence_refs[]` → `source_record_id` + `source_locator`, recursively. Every hop must be a stored edge, never an inferred one.
2. **Reconstruct what was known at the time.** `observed_as_of` / `recorded_at` as two clocks, plus `valid_from` / `valid_to`. Without both pairs you can reconstruct *what the register says now*, which is the wrong answer to every audit question.
3. **Include negative decisions.** `decision_outcome` with `rejected`, `declined_with_rationale` and `no_action_required` as ordinary values, and `review_status = rejected` rows retained. The §8.2.2 decision not to investigate, the §8.5.2 decision not to open a CAPA, the Art. 88 decision not to report, the cancelled action, the waived training, the excluded complaint — all of these are the decisions an auditor asks about, and a register that can only record "yes" is silently lossy in exactly the expensive direction.
4. **Show authority.** `decided_by` + `decision_authority_basis` + the competence join into §3. "A named human signed" is necessary; "and was authorised and competent to" is what closes the question.

**One more thing all registers must agree on: `authorship`.** `DIAGRAMS.md`'s colour rule is that a green node never creates an approved record. That rule is only enforceable if every row can say whether it was human-authored, agent-drafted, or agent-drafted-and-then-accepted or amended. If one register family omits `authorship`, the rule becomes a UI convention rather than a data invariant, and the demo claim in `WORKFLOW.md` §11 item 4 stops being true of the database.

---

## 8. What a real export actually looks like

For mock-data realism. The document register is the worst offender and therefore the best example.

**It is a multi-sheet workbook, not a table.** Typical sheet names, verbatim-plausible: `Master List`, `Procedures`, `Work Instructions`, `Forms`, `Obsolete`, `Training Matrix`, `Sheet1`, `OLD - do not use`, `Pivot`, `CHANGE LOG`.

**Header wording, real and inconsistent — including bad ones.** Inconsistency *within one workbook* is the realism target, not just across companies:

| Concept | Headers actually seen |
|---|---|
| Identifier | `Doc No.` · `Doc #` · `Document No` · `DocID` · `Document Number` · `Ref` · `No.` |
| Revision | `Rev` · `Rev.` · `Revision` · `Ver` · `Version` · `Issue` · `Rev No` |
| Dates | `Date` (which date?) · `Eff. Date` · `Effective` · `Date Effective` · `DOE` · `Approval Date` · `Date Approved` · `Issued` |
| Ownership | `Owner` · `Process Owner` · `Author` · `Originator` · `Responsible` · `Resp.` |
| Approval | `Approved By` · `Approver` · `Signed` · `QA Approval` |
| Status | `Status` · `Active?` · `Current` · `In Force` |
| Review | `Next Review` · `Review Due` · `Periodic Review Date` · `Review` |
| Retention | `Retention` · `Record Retention` · `Retention (yrs)` |
| Obsolescence | `Obsolete?` (Y/N) · `Superseded By` · `Replaces` |
| Training | `Training Req'd?` · `Trg` · `Read & Understand?` |
| Location | `Location` · `Where Filed` · `Link` · `Path` |
| The junk drawer | `Notes` · `Comments` · `Remarks` — **where the actually useful information lives** |
| Artefacts | `Unnamed: 11` · `Column1` · blank headers on columns that contain data |

**Structural pathologies to reproduce:**

- A **title row above the header row**, so row 1 is "Asteria Medical Systems — Master Document List" and the headers are on row 3. Every naive parser breaks here.
- **Merged header cells** spanning `Approval` over `By` / `Date`.
- **Status encoded as formatting**: strikethrough for obsolete, yellow fill for in-revision, red text for overdue review — with a legend in a floating text box that no export preserves.
- **Hidden rows** for documents someone deleted but did not want to lose.
- **`TODAY()`-based formulas** in `Days Until Review`, so the file's numbers change every time it is opened and no two exports of the "same" register agree.
- **A `CHANGE LOG` sheet** holding the register's own revision history, because the register is itself a controlled document — which is the practitioner point that "that list itself needs to be under control".
- **Dead UNC paths** in `Location`: `\\asteria-fs01\QMS\Controlled\SOPs\SOP-QA-012 Rev3.docx` pointing at a server decommissioned last year, with the live copy now in a cloud folder.
- **Filename/register disagreement**: the register says Rev 4, the filename says `Rev3`, the document's own footer says `Rev 4 DRAFT`. `MOCK-DATA.md` lists "mismatched filenames and register metadata" as expected behaviour.
- **Rows lagging the repository**, which is the headline problem: document control is reported as the number-one area for audit findings in both ISO and FDA audits, with the classic finding being "outdated or uncontrolled documents in use… without current approval status". Practitioners note that spreadsheets' "fluid nature does not lend itself to the level of organization and accountability required", and that maintaining a live list is impractical once records are in scope.

**Action register exports**: one sheet per meeting series (`QMR Actions`, `Audit Actions`, `Mgmt Review 2025`), status as free text so `Closed` / `closed` / `CLOSED` / `Complete` / `Done` / `C` coexist in one column, due dates overwritten in place with no history, and owners as first names only (`Sam`, `S.T.`, `Sam T (left)`).

**Training register exports**: a matrix with people as columns and documents as rows, which transposes badly, has a legend row, uses `x` / `✓` / `C` / `1` / dates interchangeably in the same grid, and has no revision column at all — so the single most important field in §3 is absent from the source.

**PMS working-file exports**: one workbook per period with the prior period's sheet copied forward and edited, calculation logic embedded in cells rather than documented, manually normalised categories, a `Notes` cell reading "denominator from Jan ERP extract — Maria to confirm", and a different snapshot date on every sheet. `MOCK-DATA.md` already lists exactly these as PMS working-file characteristics; worth honouring them literally.

---

## 9. Fields routinely incomplete or disagreed-on

The product's value is largely in surfacing these, so they should be generated as ordinary behaviour, not as injected errors.

| Register | What goes wrong | Why it happens |
|---|---|---|
| Document | **Register revision ≠ file revision.** The canonical case. | The revision is approved in one place and transcribed into the register by hand, later. `MOCK-DATA.md`: "Register values that occasionally lag behind repository state." Mitigated by `file_checksum` + `repository_observed_revision` + `register_vs_repository_state` (§2.6). |
| Document | **Retention period blank.** | Nobody owns it; it is needed only when someone asks. Three different clocks (§2.5) make it genuinely hard, so the blank is honest. |
| Document | `effective_date` equals `approved_date` for every row. | The register has only one date column, so the distinction was never capturable — which silently breaks the training gate. |
| Document | Obsolete documents absent from the register entirely, surviving only as files in a personal folder. | `MOCK-DATA.md`: "Obsolete copies in personal folders"; "Historical templates still present in folders". |
| Document | External-origin documents (standards, supplier specs) not listed at all. | §4.2.4 f) is the most-forgotten sub-item in the clause. |
| Document | Clause citations frozen at the 2003 numbering — "4.2.3 Control of Documents". | See §0. A dating artefact, and a good one to plant. |
| Training | **Assigned but never acknowledged.** Assignment exists, `acknowledged_at` null, status still `assigned` two years later. | The effective date passed anyway; nobody blocked on it. |
| Training | Completion recorded against the document, not the revision. | The source matrix has no revision column (§8). Produces the classic finding: completion dates without evidence of competence on the *current* revision. |
| Training | `assessment_result` and `effectiveness_method` empty across the board. | §6.2 c) is the least-implemented sub-item in the clause; read-and-sign is treated as sufficient. |
| Training | Awareness (§6.2 d)) has no evidence anywhere. | Nobody has ever built a field for it. |
| Action | **Owner left the company.** `owner_ref` resolves to a deactivated account; nobody reassigned. | Why `owner_role` and `owner_assignment_history[]` exist (§4.5). Workflow 8's first job is identifying the responsible owner, and this is the case it must handle. |
| Action | Due date silently extended three times, no history. | The register is a spreadsheet; the cell was overwritten. |
| Action | Same action worded differently in minutes and tracker, with different owners. | `MOCK-DATA.md` names this. Handled by `mentions[]` rather than by picking a winner. |
| Action | `awaiting_verification` / verification-reporting states missing; actions jump to `Closed`. | §8.2.4's two-step follow-up is rarely modelled, so the evidence for it does not exist. |
| Action | Closed with no completion evidence attached. | `MOCK-DATA.md`: "Actions without final evidence." |
| Risk | Register at hazard grain, so one probability is stretched over several hazardous situations. | Template inertia. Understates risk systematically. |
| Risk | `expected_frequency_baseline` empty, or present as a qualitative FMEA occurrence rating with no denominator. | And then Art. 88 has nothing to compare against — the quiet failure that makes trend reporting undefensible. |
| Risk | Post-market information never fed back; file last reviewed at launch. | ISO 14971:2019 clause 10 is the newest and least-embedded part of the standard. |
| PMS | **Snapshot dates differ between sources**, and the period row carries only one of them. | `MOCK-DATA.md` lists this first among PMS characteristics. Handled by `per_source_as_of[]`. |
| PMS | Denominator basis changes between periods without anyone noticing. | The basis lived in a spreadsheet formula, not a field. MDCG 2022-21's consistency requirement is exactly about this; `denominator_consistency_key` makes it checkable. |
| PMS | Numerator attributed by event date in one period and awareness date in the next. | Two analysts, two habits, one spreadsheet. The biggest unexplained-variance source in the whole register. |
| PMS | Late complaints appear in a later review and the earlier published rate is never restated or flagged. | `MOCK-DATA.md`: "Late-arriving complaints included in later reviews." |
| PMS | PulseOne denominator taken as cumulative units shipped, so the rate falls every year while absolute events rise. | Shipped units is the easy number and the wrong one for a reusable device. The single most consequential error available in this dataset. |
| PMS | IMDRF coding absent or at Level 1 only, so numerators cannot be grouped consistently across periods. | MDCG 2022-21 accepts Level 1 when Level 2 is unavailable — so this is compliant *and* analytically awkward, which is the best kind of realism. |
| Cross | Management review minutes list twelve §5.6.2 inputs as headings with three of them empty. | A recurring finding: reviews conducted without the required inputs present. |

---

## Citations

Primary sources verified September 2026.

**Standards (clause numbers and sub-item letters verified; requirement content paraphrased — ISO 13485, ISO 9000, ISO 14971 and ISO/TR 20416 are copyrighted)**

- ISO 13485:2016 official listing — [iso.org/obp](https://www.iso.org/obp/ui/#iso:std:iso:13485:ed-3:v1:en)
- §4.2 subclause structure (4.2.1 General · 4.2.2 Quality manual · **4.2.3 Medical device file** · **4.2.4 Control of documents** · **4.2.5 Control of records**), §4.2.4 a)–h) and the obsolete-document retention paragraph, §4.2.5 two-year floor, §5.6.1–5.6.3, §6.2 a)–e) and its NOTE, §7.1 risk-management records, §8.2.4 internal audit follow-up and verification reporting — verified against the standard's table of contents, Annex B correspondence table, and clause text
- §4.2.3 Medical device file as a new 2016 clause — [Elsmar Cove](https://elsmar.com/elsmarqualityforum/threads/iso-13485-2016-clause-4-2-3-medical-device-file.78543/), [HealthTech Activator](https://hta.nziat.co.nz/news/understanding-qms-requirements-under-iso13485-2016)
- §4.2.5 Control of records — [13485quality.com](http://13485quality.com/iso-13485-standard2016-4-2-5-control-records/)
- §4.2.4 obsolete-document retention and document-vs-record retention distinction — [Advisera](https://advisera.com/13485academy/blog/2018/03/14/common-mistakes-with-iso-134852016-documentation-control-and-how-to-avoid-them/), [i3C Global](https://www.i3cglobal.com/iso-13485-control-of-documents/)
- §5.6.2 twelve mandated inputs and §5.6.3 output including the input reviewed — [Advisera](https://advisera.com/13485academy/blog/2017/11/09/how-to-perform-management-review-according-to-iso-13485/), [Hardcore QMS](https://hardcoreqms.com/13485/management-review-iso-13485/)
- §6.2 competence, training, awareness, effectiveness evaluation; training matrices as the usual implementation — [Comply Guru](https://complyguru.com/training-and-competence-under-iso-13485/), [Greenlight Guru](https://www.greenlight.guru/blog/training-management-iso-13485-part-820), [Hardcore QMS](https://hardcoreqms.com/13485/iso-13485-training-requirements/)
- §8.2.4 internal audit records, corrections and corrective actions without undue delay, verification of actions and reporting of verification results — [ISO Cloud Consulting](https://isocloudconsulting.com/pages/iso-13485-internal-audit), [i3C Global](https://www.i3cglobal.com/iso-13485-internal-audit/)
- ISO 14971:2019 cl. 4.5 risk management file and traceability for each identified hazard; cl. 5.4 hazard identification; cl. 5.5 risk estimation; cl. 7 risk control; cl. 8 overall residual risk; cl. 9 risk management review; cl. 10 production and post-production activities (revised and aligned with ISO 13485 cl. 8) — [iso.org](https://www.iso.org/standard/72704.html), [Greenlight Guru](https://www.greenlight.guru/blog/risk-management-documentation-iso-14971), [SoftComply](https://softcomply.com/what-is-risk-management-file/), [Orcanos clause-by-clause](https://www.orcanos.com/compliance/2020/06/09/iso-149712019-medical-device-risk-management-detailed-explanation-clause-clause/), [BSI on production and post-production](https://compliancenavigatorppd.bsigroup.com/en/medicaldeviceblog/production-post-production-and-the-new-iso-14971/)
- ISO 13485 §7.1 risk management in product realization with a NOTE referring to ISO 14971 — [13485quality.com](http://13485quality.com/iso-134852016-standard-7-1-planning-documenting-risk-management-activities/), [Exeed](https://exeedqm.com/new-blog/understanding-risk-management-requirements-in-iso-134852016)
- ISO/TR 20416:2020 *Medical devices — Post-market surveillance for manufacturers*, cited by MDCG 2025-10 as the reference for PMS data-quality and method selection — [CEN catalogue](https://standards.cencenelec.eu/) (paywalled; not inspected)

**United States**

- 21 CFR §820.35 Control of records — builds on ISO 13485 Clause 4.2.5; (a) complaint record content, (b) servicing record content, (c) "The UDI must be recorded for each medical device or batch of medical devices", (d) confidentiality marking; **no retention period specified in the section itself** — [Cornell LII](https://www.law.cornell.edu/cfr/text/21/820.35)
- QMSR effective 2 February 2026 and the remaining Part 820 sections — [FDA](https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr), [Greenlight Guru](https://www.greenlight.guru/blog/qmsr-your-guide-to-part-820)

**European Union**

- MDR Art. 10(8) — technical documentation, EU declaration of conformity and certificates kept available "for a period of at least 10 years after the last device covered by the EU declaration of conformity has been placed on the market", 15 years for implantable devices — [Medical Device Regulation](https://www.medical-device-regulation.eu/mdr-article-10-general-obligations-of-manufacturers/), [Medical Device HQ](https://medicaldevicehq.com/documentation/mdr-article-10-general-obligations-of-manufacturers/)
- MDR Art. 83–86 PMS framework and PSUR frequencies — [Zechmeister Solutions](https://zechmeister-solutions.com/en/blog/mdr-articles-83-86-pms-framework), [Mantra Systems](https://mantrasystems.com/articles/psur-periodic-safety-update-report-requirements-under-eu-mdr)
- MDR Art. 86(1) — PSUR shall set out the conclusions of the benefit-risk determination, the main findings of the PMCF, and "the volume of sales of the device and an estimate of the size and other characteristics of the population using the device and, where practicable, the usage frequency of the device" — [Medical Device Regulation](https://www.medical-device-regulation.eu/2019/07/16/mdr-article-86-periodic-safety-update-report/), corroborated by [Mantra Systems](https://mantrasystems.com/articles/psur-periodic-safety-update-report-requirements-under-eu-mdr)
- MDR Art. 88(1) — trend reporting, quoted in full; methodology for determining a statistically significant increase and the observation period to be specified in the PMS plan referred to in Article 84 — [Medical Device Regulation](https://www.medical-device-regulation.eu/2019/07/16/mdr-article-88-trend-reporting/), [TÜV SÜD](https://de-mdr-ivdr.tuvsud.com/Article-88-Trend-reporting.html)
- MDR Annex III §1.1(a) and (b) — PMS plan contents including "suitable indicators and threshold values", "methods and protocols to manage the incidents subject to the trend report", and the PMCF plan or justification for its absence — [Medical Device Regulation](https://www.medical-device-regulation.eu/2019/07/25/annex-iii/); Annex III text also reproduced column-by-column in MDCG 2025-10 Table 2
- **MDCG 2025-10** *Guidance on post-market surveillance of medical devices and in vitro diagnostic medical devices*, December 2025 — PMS plan element table; thresholds "are to be established in the pre-market phase"; measurable values "batch, batch quantity, hours/frequency of use, number of devices in use/sold, number of exposures, etc."; indicators and thresholds "should be covered in the PMS plan and be linked to the risk management documentation (as referred to Annex I, section 3 MDR/IVDR)"; Art. 83(3)(h) trend detection — [European Commission](https://health.ec.europa.eu/document/download/a9ad86b7-1b8e-4bae-beb4-48b2b3ed2f05_en?filename=mdcg_2025-10_en.pdf)
- **MDCG 2022-21** *Guidance on Periodic Safety Update Report (PSUR)*, December 2022 — cover-page minimum content including the manufacturer-assigned PSUR reference number and the data collection period; leading-device rule for the reference number; volume-of-sales criteria menu (devices placed on the market or put into service · units distributed within each time period · number of episodes of use for reusable devices · active installed base · units distributed from the date of declaration of conformity to the end of each period · number of devices implanted · other with rationale); "Whichever method is used should be consistent throughout the PSUR in all areas"; "Estimate the number of patients exposed, as the sales numbers alone do not necessarily reflect the number of uses of the device (usage frequency)"; data collection period starting at MDR certification date or MDR Date of Application 26 May 2021; contiguity requirement avoiding "any gap or overlap of data"; change-of-period justification and comparability statement; Basic UDI-DI split and EEA+TR+XI / Worldwide regions; year-on-year N/N2/N3/N4 structure; IMDRF AET Annexes A, C, D, F at Level 2 where available; Annex II rate-table denominator footnotes — [European Commission](https://health.ec.europa.eu/system/files/2023-01/mdcg_2022-21_en.pdf)
- MDCG 2023-3 Rev.2 vigilance Q&A — incidents that are not serious incidents "must be documented and considered in the manufacturer's quality management system and reported in accordance with requirements outlined in Article 88 MDR/Article 83 IVDR"; trend reports to be reported to the competent authority of the Member State in which the incidents occurred — [European Commission](https://health.ec.europa.eu/document/download/af1433fd-ed64-4c53-abc7-612a7f16f976_en?filename=mdcg_2023-3_en.pdf)

**Other jurisdictions**

- Brazil ANVISA RDC 665/2022 — "A list of current documents shall be maintained to identify the documents' status and to ensure that only updated and approved documents are in use." The one jurisdiction found that mandates the register artefact itself — [ANVISA English version](https://www.gov.br/anvisa/en/regulation-of-companies/arquivos/rdc-665-2022-english-version.pdf), [CBDL copy](https://cbdl.org.br/wp-content/uploads/2022/05/RDC_665-2022-GMP_IvD.pdf), [Thema-Med overview](http://www.thema-med.com/en/2022/05/30/brazil-rdc-665-2022-brazilian-good-manufacturing-pratices-bgmp-application/)

**`Convention` sources — vendor, consultant and practitioner, labelled as such**

- **OpenRegulatory** free QMS document-list template: fields for title, doc ID, type, version, release and review dates, owner, comments — [openregulatory.com/document_templates/document-list-qms](https://openregulatory.com/document_templates/document-list-qms) (page returned 403 to direct fetch; field list via search result summary — see Confidence notes)
- **Elsmar Cove practitioner thread** on master control lists: ISO 13485 does not require a master list; "that list itself needs to be under control" with "reference number and version control, so that you can show what the revision status was at any time"; maintaining a live list including records is impractical; Brazil RDC 665/2022 does require it — [Elsmar Cove](https://elsmar.com/elsmarqualityforum/threads/master-control-lists-for-records-and-documents.91036/)
- **Elsmar Cove** on master document lists and obsolete documents — [Elsmar Cove](https://elsmar.com/elsmarqualityforum/threads/master-document-list-obsolete-documents.68461/page-2)
- **Real controlled procedure with clause-derived numbering** `QOP-42-01 (A) Control of Documents` — [imsxp.com](https://www.imsxp.com/PrdResources/aqaFiles/ISO%2013485%20Operational%20Procedure%20QOP-42-01%20(A)%20Control%20of%20Documents.pdf)
- **eQMS training-automation practice**: training tasks auto-generated when a new or revised document is approved; training auto-launched when a revised controlled document becomes effective; read-and-understand plus assessment with a due date before the effective date; secure e-signature acknowledgement tied to the exact revision assigned; systems tracking document ID, title, owner, effective date, revision and version status — [Dot Compliance](https://www.dotcompliance.com/solutions/training-management/), [Cognidox](https://www.cognidox.com/blog/training-management-medical-device-qms), [ApprovaDoc](https://www.approvadoc.com/sop-training-records-software), [Trackmedium](https://www.trackmedium.com/modules/training-management/)
- **Document control as the number-one audit-finding area**; spreadsheets' "fluid nature does not lend itself to the level of organization and accountability required"; manual binder/Excel/email methods prone to compliance risk — [SimplerQMS](https://simplerqms.com/medical-device-document-control/), [Arena Solutions](https://www.arenasolutions.com/resources/articles/device-master-record/), [QT9](https://qt9software.com/blog/medical-device-document-control)
- **Common ISO 13485 nonconformities by clause**: outdated or uncontrolled documents in active use without current approval status (4.2); training records with completion dates but no evidence of competence on *current* revisions (6.2); CAPA as the single most-cited area in both ISO 13485 audits and FDA inspections; management reviews deferred or informally conducted with required inputs missing (5.6) — [MedDeviceGuide](https://meddeviceguide.com/blog/iso-13485-audit-findings-common-nonconformities-clause-guide)
- **Art. 88 denominator practice**: the denominator defines the population at risk and should match the one used in the risk management file to establish expected frequency; non-serious incidents and expected undesirable side-effects should already carry a pre-defined occurrence rate and severity rating in the risk file; "use of statistics must be justified, not automatic" — [MedDeviceGuide](https://meddeviceguide.com/blog/mdr-article-88-trend-reporting-statistical-thresholds-guide), [Qserve](https://qservegroup.com/blog/en/how-to-incorporate-article-88-into-post-market-surveillance)
- **Record retention under MDR in practice** — [Zechmeister Solutions](https://zechmeister-solutions.com/en/blog/record-control-mdr), [Johner Institute on retention periods](https://blog.johner-institute.com/regulatory-affairs/retention-periods/)

**Internal**

- [`WORKFLOW.md`](../WORKFLOW.md) — process topology, vigilance clocks, the correction / corrective-action distinction, hard human gates
- [`DIAGRAMS.md`](../DIAGRAMS.md) — workflows 1–9 and the source dependency matrix
- [`MOCK-DATA.md`](../MOCK-DATA.md) — QMS content required for V0, templates and registers, realistic imperfection model, evaluation plan
- [`mock/asteria/entities.md`](../mock/asteria/entities.md), [`mock/asteria/products.md`](../mock/asteria/products.md) — PulseOne serialised/reusable vs PulsePatch lot-controlled/single-use, use-session object, installed-base unreliability

### Confidence notes

**High confidence**

- The §4.2.3 / §4.2.4 / §4.2.5 mapping. Verified three independent ways, including a US federal regulation cross-referencing Clause 4.2.5 as control of records. The numbering shift from ISO 13485:2003 fully explains the disagreement in secondary sources.
- §4.2.4 having eight sub-items a)–h), and the exact shape of the obsolete-document retention paragraph (bounded below by the resulting record's retention period).
- §4.2.5's "not less than two years from the medical device release by the organization" floor, as distinct from the device-lifetime rule.
- §5.6.2's twelve inputs with (i) being follow-up actions from previous management reviews, and §5.6.3 requiring the output to include the input reviewed.
- §6.2's five sub-items including (c) effectiveness evaluation and (d) awareness as separate obligations, and the risk-proportionality NOTE.
- §8.2.4's "corrections and corrective actions… without undue delay" plus follow-up verification **and** reporting of verification results.
- §7.1 mandating records of risk management activities with a NOTE pointing at ISO 14971 — and *not* mandating a register.
- All MDR text quoted: Art. 10(8), Art. 86(1), Art. 88(1), Annex III §1.1(b).
- All MDCG 2022-21 and MDCG 2025-10 material, read directly from the Commission-hosted PDFs. The denominator menu, the consistency requirement, the contiguity requirement, the change-of-period justification and comparability statement, the IMDRF AET annex list, and "thresholds are to be established in the pre-market phase" are all verbatim from those documents.
- 21 CFR §820.35 specifying no retention period — read directly.
- Brazil RDC 665/2022 mandating a list of current documents.

**Paraphrased, not verified verbatim**

- All ISO 13485, ISO 9000 and ISO 14971 requirement content. Clause numbers, titles and sub-item letters are reliable; wording is deliberately paraphrased for copyright reasons and should be checked against a purchased copy before appearing in any customer-facing compliance claim.
- ISO 14971:2019's internal clause numbering (4.5, 5.4, 5.5, 7, 8, 9, 10). Corroborated across three secondary sources but **not** verified against the standard itself. The 4.5 traceability requirement is the best-attested; clause 7's internal subclause numbering (7.1 vs 7.2 etc.) is the least certain and I avoided citing sub-numbers.
- ISO/TR 20416:2020 — known only as a reference cited inside MDCG 2025-10. Not inspected. No claim in this note depends on it.
- The OpenRegulatory document-list field set (title, doc ID, type, version, release and review dates, owner, comments). The page returned 403 to direct fetch; the field list comes from a search-result summary of it. Treat as indicative of the template's shape rather than as its exact column headers.
- The real-world header-wording tables in §8 are a synthesis of practitioner sources plus ordinary industry exposure. They are realistic, not sourced line-by-line, and are labelled `Convention`/observed rather than cited to a single template.

**Corrected during research**

- **The brief's premise was the legacy numbering.** It framed §4.2.3 as control of documents and §4.2.4 as control of records. That is ISO 13485:2003 / ISO 9001:2008. `WORKFLOW.md` was already right and needs no change.
- **§4.2.4 has eight sub-items, not six.** Several secondary sources imply six; I had initially drafted against that and corrected it after reading the clause.
- **The document register is not mandated by ISO 13485.** I began assuming it was the obvious `Mandated` anchor for this whole note. It is not: §4.2.4 c) requires revision status to be *identified*, and the register is the conventional implementation. Brazil RDC 665/2022 is the only mandate I found for the artefact. This changed the status of roughly half the document-register rows.
- **The denominator is more strongly mandated than I expected.** I expected to mark denominator fields `Convention`. MDR Art. 86(1) mandates volume of sales, an estimate of population size and characteristics, and where practicable usage frequency — as PSUR content in its own right. The denominator is `Mandated`; only the *choice among* the MDCG 2022-21 bases is the manufacturer's, and even that choice must be declared and kept consistent.
- **`WORKFLOW.md`'s Art. 88 baseline locus is imprecise, not wrong.** It says the baseline must be in "the technical documentation and product information". The operative loci are the **PMS plan** (Art. 88(1) second subparagraph for methodology and observation period; Annex III §1.1(b) for indicators and threshold values) linked to the **risk management documentation** (Annex I Section 3, per MDCG 2025-10) — with the PMS plan being part of the technical documentation, so the statement holds at one remove. The "product information" half maps to expected undesirable side-effects declared in the IFU under Annex I Section 23. Recommend tightening `WORKFLOW.md` §5 to name the PMS plan explicitly, since the register field we need is a *revision-dated reference to the PMS plan*, not a gesture at the technical file.
- **MDCG 2025-10 is a December 2025 document and post-dates `WORKFLOW.md`'s September 2026 citation sweep without being in it.** It is now the primary PMS guidance and should be added to `WORKFLOW.md`'s EU citations. One early fetch attempt returned MDCG 2023-3 Rev.2 content instead; both were eventually read from their own PDFs and are cited separately above.
