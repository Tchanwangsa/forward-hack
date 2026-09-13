# Register Shape Reference — NC, CAPA, Audit Findings, Change Control

**Purpose.** The field-level shape of four QMS registers, with every `Status` claim sourced. Companion to [`WORKFLOW.md`](../WORKFLOW.md) (the domain reference) and [`DIAGRAMS.md`](../DIAGRAMS.md) (the nine agent workflows that read and write these registers). This is a research note, not a schema migration — but it is written so a schema can be derived from it without re-reading the sources.

**Scope.** (1) Nonconformity register — ISO 13485:2016 §8.3.1–§8.3.4. (2) CAPA register — §8.5.2/§8.5.3 plus the ISO 9000:2015 §3.12.2/§3.12.3 correction-vs-corrective-action split. (3) Audit findings register — §8.2.4, extended to external findings. (4) Change control register — §7.3.9 plus the QMS change records that CAPA implementation depends on.

**Standing caveat.** ISO 13485:2016 and ISO 9000:2015 are copyrighted standards. Clause numbers and titles are stated; requirement content is paraphrased, never reproduced. Anyone implementing against this must read the purchased standard. CFR, MDR, FDA guidance, FDA warning letters, MDSAP documents and GHTF/IMDRF guidance are public and are quoted directly.

**Depth note.** As instructed, registers 1 and 2 are treated at full depth. Register 3 is treated at full depth for the field table but with less on export realism. Register 4 is the thinnest: it is scoped to what CAPA implementation and workflow 5 actually need (design-change significance, affected-item linkage, implementation evidence), not to a complete §7.3 design-control model. **Explicitly deprioritised and not covered:** supplier corrective action (SCAR) register, risk register / risk file rows, document-control and training registers, management-review register, PMS/PSUR register, the complaint register itself (another family owns it), and servicing records under §820.35(b).

---

## 0. Conventions used by all four tables

### 0.1 Status values

| Status | Meaning | Evidence bar applied here |
|---|---|---|
| `Mandated` | A named regulation or standard clause requires this **content**. | A cited clause. Where the clause requires an outcome and the field is the only practical way to record it, the row says so explicitly rather than pretending the field name is in the text. |
| `Convention` | Not mandated, but present in essentially every real register, commercial eQMS, or inspection-ready template. | At least one real template, vendor, or consultant source, labelled as such. |
| `Product` | Our own addition, needed by a DIAGRAMS.md workflow. | A named workflow number and the specific thing that workflow cannot do without it. |

Two honesty rules applied throughout: no field is marked `Mandated` on inference alone without the inference being stated in the Notes column, and where sources genuinely disagree the row says so instead of picking one.

### 0.2 A word on the QMSR transition, because it changes the citation pattern

As of **2 February 2026**, 21 CFR Part 820 is the Quality Management System Regulation and incorporates ISO 13485:2016 by reference. Only six sections of substantive US text remain: **§820.1** scope, **§820.3** definitions, **§820.7** incorporation by reference, **§820.10** QMS requirements, **§820.35** control of records, **§820.45** control of device labeling and packaging. Subparts C–O are reserved ([Cornell LII, Part 820](https://www.law.cornell.edu/cfr/text/21/part-820); [Greenlight Guru, *What's left of the QSR*](https://www.greenlight.guru/blog/qmsr-your-guide-to-part-820)).

This means the old **§820.90 Nonconforming product**, **§820.100 Corrective and preventive action**, **§820.22 Quality audit** and **§820.198 Complaint files** no longer exist as US text. Their requirement content now arrives via ISO 13485 §8.3, §8.5.2/§8.5.3, §8.2.4 and §8.2.2.

**Why this note still quotes §820.90 heavily anyway.** Three reasons, and they matter for how we cite:

1. The repealed CFR text is **public and quotable**, where the ISO clause that replaced it is not. For fields like "justification for use of nonconforming product and the signature of the individual authorizing the use", the old CFR gives us a verbatim sentence for a requirement that ISO 13485 §8.3.2 also imposes but which we may only paraphrase.
2. FDA determined these sections were **substantively similar** to ISO 13485 — that is the stated legal basis for removing them. So the old text is the best available public gloss on the surviving ISO requirement.
3. Inspections of conduct before February 2026, and every warning letter in the corpus we can actually read, use the old citations. The most recent letter in this research — **Medline Industries, 25 March 2026** — still cites `21 CFR 820.100(a)` and `820.30(f)`, because the inspection ran 1–12 December 2025 ([FDA warning letter, Medline Industries](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/medline-industries-lp-723866-03252026)). **Mock-data implication:** an Asteria dataset covering an 18-month history that straddles early 2026 should contain registers whose clause-reference columns are internally inconsistent — older rows citing `820.90`, newer rows citing `ISO 13485 8.3.2`, and at least one row citing both. That inconsistency is realistic, not an error.

`FDA-era` in a Source cell below means: repealed CFR text, quoted because it is public, for a requirement ISO 13485 still imposes.

### 0.3 The provenance block — defined once, applied to all four registers

Every register below carries the same eight-field provenance block. It is `Product` in all four cases, justified once here rather than eight times per table.

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `source_system` | enum: `qms_repository`, `email`, `support`, `erp`, `service`, `crm`, `product_db`, `agent` | `Product` | DIAGRAMS.md workflow 1, source dependency matrix | The matrix says source systems never write directly into a regulated record. Without this field there is no way to assert that. |
| `source_record_id` | string, opaque, per-system | `Product` | Workflow 1, 9 | MOCK-DATA.md requires each source to invent its own keys (`A-1042`, `TKT-8891`). The register row must hold the foreign key it was derived from without adopting it as identity. |
| `field_provenance` | JSON map: field name → `{evidence_ref, extraction_method, extracted_at, confidence}` | `Product` | Workflow 7 step A2 ("cite every field"), workflow 9 | This is the single most load-bearing product field in the whole note. Workflow 7's stated value is *not* draft speed, it is that "every prefilled field carries provenance back to the original evidence". That is a per-field property, so it cannot live in a per-row `notes` column. |
| `review_status` | enum: `agent_draft`, `human_reviewed`, `human_signed`, `superseded` | `Product` | DIAGRAMS.md colour rule: "a green node never creates an approved record… The record exists only when a human signs it" | Must be per-field as well as per-row for partially-reviewed drafts. |
| `authorship` | enum: `human`, `agent_drafted_human_signed`, `agent_observed` + `agent_version` | `Product` | DIAGRAMS.md autonomy levels; WORKFLOW.md §9 hard gates | An auditor will ask which records a machine touched. If we cannot answer per record, the hard-gate claim is unfalsifiable. |
| `gap_flags` / `conflict_flags` | array of `{field, kind: missing｜conflicting, sources[]}` | `Product` | Workflow 7 step A3 ("flag the gaps… what conflicts between sources") | MOCK-DATA.md guarantees sources disagree. Suppressing that in the register destroys the evidence trail. |
| `evidence_bundle_ref` | string | `Product` | Workflow 9 | Workflow 9 "works only if the eight workflows above kept their provenance as they went". |
| `awareness_timestamp` | timestamp + `awareness_source` | `Product` (but see note) | Workflow 3; 21 CFR §803.50, §803.53; MDR Art. 87(3)(4)(5) | The statutory clock starts on awareness. Awareness is a *fact about the organisation*, not about the register row, so it is `Product` in the NC/CAPA registers while being `Mandated` in the complaint/vigilance registers. Carry it anyway: workflow 5 can discover post-delivery exposure, which is the moment a §8.3.3 NC becomes vigilance-relevant. |

---

## 1. Nonconformity (NC) register

### 1.1 Grain — the decision the rest of the design hangs on

**One row = one nonconformity.** Defined as: *one failure of one identified requirement, detected at one point in the process, on a defined population.* Not one unit. Not one lot. Not one disposition.

Two child tables carry the detail:

```text
nc_register  (one row per nonconformity)
  ├── nc_affected_population   one row per (lot | serial range | shipment | supplier lot | sw version)
  │                            + qty, ship status, evidence ref, expansion basis
  └── nc_disposition           one row per disposition decision
                               + sub-population ref, justification, authoriser, authority basis
```

**Why the register row cannot be the unit or the lot.** A single detected nonconformity routinely spans thousands of units across several lots. If the row were the unit, the "nature of the nonconformity" text and the investigation would be duplicated thousands of times and would drift — and drift in the problem statement is exactly what GHTF/SG3/N18 warns against when it requires the problem statement be "reviewed and refined as appropriate" as one artefact ([GHTF/SG3/N18:2010 §6.1](https://www.imdrf.org/sites/default/files/docs/ghtf/final/sg3/technical-docs/ghtf-sg3-n18-2010-qms-guidance-on-corrective-preventative-action-101104.pdf)).

**Why the register row cannot be the disposition.** Because a single NC lawfully carries several. Consider an Asteria PulsePatch lot failing an adhesive peel specification: 400 units in stock reworked, 120 in a damaged carton scrapped, 30 already delivered to SITE-13 left in the field under a documented use-as-is rationale. Three dispositions, three justifications, three authorisers, one nonconformity. ISO 13485 §8.3.2 requires records of the concession **and the identity of the person(s) authorising it**; the repealed-but-public US text is blunter: *"Disposition of nonconforming product shall be documented. Documentation shall include the justification for use of nonconforming product and the signature of the individual authorizing the use."* (21 CFR §820.90(b)(1), quoted in [FDA CDRH, *Nonconforming Product*, slide 32](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf)). A single `authorised_by` column on the register row cannot represent three authorisers, and flattening them loses the one piece of data an inspector will check.

**Why the affected-population detail must not be crammed into the register row either.** GHTF's own worked example in Annex D shows the grain: one problem statement, two serial numbers, **different measured values per serial** (67 µinch and "up to 38 µinch"). Per-unit measurement detail belongs under the row, not in it.

**Where the population lives relative to the row.** The register row carries *rollups only*, and they are derived, not entered: `qty_affected_total`, `qty_delivered`, `lots_affected_count`, `disposition_summary`, `delivery_fork` (§8.3.2 / §8.3.3 / mixed). The authoritative detail is in `nc_affected_population`. This matters because the rollup is what an export shows and what a reviewer trusts, and it is precisely where real registers stop reconciling with ERP (see §1.8).

**Consequence for workflow 5.** Workflow 5 does not edit the register row. It writes rows into `nc_affected_population` with an expansion basis and an evidence reference, then the rollups change, then a human makes the §8.3.2/§8.3.3 call. That keeps the amber gate in DIAGRAMS.md workflow 5 (`G1`) meaningful: the agent supplies a population, a human signs the fork.

### 1.2 Identity and numbering

Real practice, with the realism notes the mock layer needs:

- **Format.** `NCR-####` or `NC-YYYY-###`, per-site or per-year sequential. The FDA warning letter corpus shows bare sequential integers with no year: `NC 1797`, `NC 1804`, `NC 1786`, `NC 1787`, `NC 1790`, `NC 1796` — and note they are **not** in date order (NC 1804 is dated 28 Dec 2022, NC 1786 is dated 8 Nov 2023) ([FDA warning letter, Criticare Technologies](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/criticare-technologies-inc-686915-07122024)). Sequence number does not imply chronology. Our mock data should reproduce that.
- **Auto-numbering is a template feature, not a requirement.** Free NCR log templates ship with "Auto-numbered IDs (NCR-0001, NCR-0002…)" ([NominalQC NCR log template](https://www.nominalqc.com/templates/ncr-log-template)) — `Convention`.
- **What the row must carry to be findable.** Findability in practice is by: product code / model, lot or serial, date detected, detecting area or work centre, defect category, disposition, status, owner, and linked CAPA. Every one of those appears as a dropdown column in commodity NCR log templates (NominalQC, above) and as a field in consultant-described NCR structure ([SimplerQMS, *Nonconformance Report*](https://simplerqms.com/non-conformance-report/)). For a serialised reusable device like PulseOne, serial is the join key; for PulsePatch it is lot + expiry. The register must support both without a nullable mess — hence `population_key_type` on the child rows.
- **Retention.** ISO 13485 requires QMS records be retained for at least the lifetime of the device and not less than two years — so the identifier must survive longer than any source-system id it was derived from (secondary source: [SimplerQMS](https://simplerqms.com/non-conformance-report/), via [NominalQC](https://www.nominalqc.com/templates/ncr-log-template)).

### 1.3 Lifecycle / status values

The real state set, including the negative and awkward states:

| State | Meaning | Why it exists |
|---|---|---|
| `detected` | Raised, not yet contained | Detection and containment are distinct; containment is physical and immediate |
| `contained` | Identified and segregated | §8.3.1 identification and segregation is the point of the clause |
| `under_evaluation` | Extent being determined | The §8.3.2/§8.3.3 fork is decided here |
| `awaiting_mrb` | Queued for disposition authority | Real registers stall here; it is the commonest aging bucket |
| `disposition_approved` | MRB decided; execution pending | |
| `in_rework` | §8.3.4 execution | |
| `awaiting_reverification` | Reworked, not yet re-inspected | §8.3.4 re-verification is a separate event from rework |
| `closed_scrapped` | | |
| `closed_reworked_verified` | | |
| `closed_returned_to_supplier` | | |
| `closed_regraded` / `closed_downgraded` | "Downgrade — reverting back to a safe and effective older version when there is a problem with an upgrade" ([FDA NC slides, slide 30](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf)) | Directly relevant to Asteria: a PulseOne firmware rollback is a downgrade disposition, not a rework |
| **`closed_use_as_is_concession`** | Closed with authorised release of nonconforming product | The negative-ish terminal state the brief asks for. It is **not** a routine close: FDA's position, from QSR preamble comment #156, is that *"the justification should be based on scientific evidence, which a manufacturer should be prepared to provide upon request. Concessions should be closely monitored and not become accepted practice"* ([FDA NC slides, slide 33](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf)) |
| `closed_no_capa` | Closed with a recorded rationale that no corrective action is warranted | MDSAP auditors sample exactly this: "confirming that the medical device organization's decision not to take corrective action has been made using appropriate risk based decision making" ([MDSAP Measurement, Analysis and Improvement, Task 5](https://www.fda.gov/media/147373/download)). QSIT objective 6 instructs the investigator to "review records regarding nonconforming product where the firm concluded corrective or preventive action was not necessary" ([FDA QSIT](https://www.fda.gov/files/Guide-to-Inspections-of-Quality-Systems.pdf)) |
| `reopened` | | Needed because recurrence invalidates a prior close |
| `voided` / `duplicate_of` | | MOCK-DATA.md guarantees duplicates; merges are a hard human gate |

**Mixed-disposition closure.** Because dispositions are child rows, the register row's terminal state is a *derived* summary (`closed_mixed` with a breakdown). Do not force a single disposition enum onto the row — that is how real spreadsheets lose the concession.

### 1.4 NC register — field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `nc_id` | string, unique | `Convention` | [NominalQC NCR log](https://www.nominalqc.com/templates/ncr-log-template); [SimplerQMS](https://simplerqms.com/non-conformance-report/) ("NCR Number/ID — unique, system-generated identifier") | No clause mandates an identifier scheme. Every template has one. |
| `date_detected` | date | `Convention` | SimplerQMS "Date of Issue"; NominalQC "Date" | Distinguish from `date_raised`: real registers record the day somebody filed the form, not the day the failure happened, and the gap is evidence. |
| `date_raised` | timestamp | `Convention` | as above | |
| `nature_of_nonconformity` | long text | `Mandated` | ISO 13485 §8.3.1 (records of the nature of nonconformities); FDA-era 21 CFR §820.90(a): *"The procedures shall address the identification, documentation, evaluation, segregation, and disposition of nonconforming product"* ([FDA NC slides, slides 7–8](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf)) | The one field nobody disputes. |
| `requirement_not_met` | reference: spec doc + revision + clause/limit | `Mandated` *by inference, stated* | ISO 13485 §8.3.1 + the definition of nonconformity as non-fulfilment of a requirement (21 CFR §820.3(q) pre-QMSR: "the nonfulfillment of a specified requirement"; §820.3(y) "specification": "any requirement with which a product, process, service, or other activity must conform") | **Inference, declared:** the clause mandates the *nature* of the nonconformity; you cannot state a nature without naming the unmet requirement. GHTF's model problem statement does exactly this: *"nonconforming per Design Document 123456, revision A. Note 2.1… requires that the surface finish be 32 µinch maximum"* ([GHTF/SG3/N18 Annex D](https://www.imdrf.org/sites/default/files/docs/ghtf/final/sg3/technical-docs/ghtf-sg3-n18-2010-qms-guidance-on-corrective-preventative-action-101104.pdf)). If you want to be conservative, demote to `Convention` — do not demote the *content*. |
| `measured_value` / `specification_limit` | number + unit, nullable | `Convention` | GHTF Annex D (per-serial measured values) | Belongs on `nc_affected_population` when it varies per unit. |
| `product_identification` | model / product code + name | `Mandated` | 21 CFR §820.35(c) (current QMSR text): *"The UDI must be recorded for each medical device or batch of medical devices."*; ISO 13485 §8.3.1 | §820.35(c) mandates UDI at device-or-batch level, which drags model identity with it. |
| `udi` / `lot` / `serial` | string(s); at least one required | `Mandated` | 21 CFR §820.35(c) ([Cornell LII §820.35](https://www.law.cornell.edu/cfr/text/21/820.35)) | For PulsePatch this is lot; for PulseOne, serial. Enforce "at least one populated" rather than making all nullable. |
| `hardware_revision` / `software_version` | string, nullable | `Product` | Workflow 5 (same software version is an expansion axis); DIAGRAMS.md workflow 5 node A1 | Not mandated as an NC field, but the §8.3.2/§8.3.3 fork for a firmware defect is *defined* by version, not lot. |
| `detected_at_stage` | enum: `incoming`, `in_process`, `final_release`, `batch_record_review`, `returns_inspection`, `field` | `Mandated` *as content* / `Convention` *as enum* | FDA NC slides, "Sources of Nonconforming Product" (slides 15–17): incoming inspection, in-process test, returned product; ISO 13485 §8.2.6 | The enum shape is ours; the distinction is FDA's. |
| `detected_by` | person ref | `Convention` | SimplerQMS "Responsible Party/Department"; NominalQC "Owner" | |
| `detecting_area` / `work_centre` | string | `Convention` | NominalQC ("Department", "Work center" dropdowns) | |
| `extent_determination` | long text + link to population rows | `Mandated` | FDA QSIT objective 5: *"The full extent of a problem must be captured before the probability of occurrence, risk analysis and the proper course of corrective or preventive action can be determined."* ([QSIT](https://www.fda.gov/files/Guide-to-Inspections-of-Quality-Systems.pdf)); MDSAP advisory-notice task: "assessing whether the organization appropriately determined the scope of the quality issue" ([MDSAP MAI](https://www.fda.gov/media/147373/download)) | The *determination* is mandated. The numeric quantity column below is the conventional way of recording it. |
| `qty_affected_total` | integer, derived rollup | `Convention` | NominalQC ("Quantity", "Lot affected"); SimplerQMS ("lot/batch number") | Universal in every log; not named in any clause. |
| `qty_delivered` | integer, derived rollup | `Mandated` *as content* | ISO 13485 §8.3.2 vs §8.3.3 split; MDR Art. 10(12): *"Manufacturers who consider or have reason to believe that a device which they have placed on the market or put into service is not in conformity with this Regulation shall immediately take the necessary corrective action to bring that device into conformity, to withdraw it or to recall it, as appropriate."* | The fork is a legal fork. The number that decides it has to be in the record. |
| `delivery_fork` | enum: `pre_delivery_8_3_2`, `post_delivery_8_3_3`, `mixed`, `undetermined` | `Mandated` *as content* | ISO 13485 §8.3.2 / §8.3.3 titles; MDSAP Task 8 (in stock or returned) and Task 9 (detected after delivery or use) are **separate audit tasks** ([MDSAP MAI](https://www.fda.gov/media/147373/download)) | `undetermined` must be a legal value. Real registers sit there for weeks, and hiding it is worse than showing it. |
| `containment_action` | text | `Mandated` | FDA-era §820.90(a) "segregation"; ISO 13485 §8.3.1; GHTF §6.3 lists correction examples: "Containment, Stop of shipment/supply, Issuance of advisory notice" | Containment is a **correction**, not a corrective action. Keep it on this row, never in the CAPA register (see §2.1). |
| `segregation_location` | string | `Convention` | FDA NC slides, slide 25: "Locked Cages / Digital Controls / Separate Area" | |
| `investigation_required` | boolean + rationale | `Mandated` | FDA-era §820.90(a), quoted in [FDA NC slides, slide 22](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf): *"The evaluation of nonconformance shall include a determination of the need for an investigation and notification of the persons or organizations responsible for the nonconformance. The evaluation and any investigation shall be documented."* | The *negative* case is explicitly allowed: "Investigations are Not Always required – when an investigation has already been performed on a similar issue" (slide 23). That is workflow 4's entire justification, applied to NCs rather than complaints. |
| `responsible_party_notified` | person/org ref + date | `Mandated` | FDA-era §820.90(a) (sentence above); MDSAP Task 8: *"Confirm that an appropriate disposition was made, justified, and documented; and that any external party responsible for the nonconformity was notified."* | For Asteria, this is the contract manufacturer or component supplier for PulsePatch. |
| `investigation_findings` | long text + method | `Mandated` | FDA-era §820.90(a) "any investigation shall be documented"; ISO 13485 §8.3.1 | Root cause is **not** required at NC level — it is required at CAPA level. Do not make this field mandatory; see §2.8. |
| `risk_assessment_ref` | link to risk file row | `Mandated` *as content* | QSIT objective 6: investigation depth must be "commensurate with the significance and risk of the nonconformity"; MDSAP Task 8 (risk-based decision making for concession) | The *link* is our shape; the risk-proportionality judgement is mandated. |
| `severity` | enum: `critical`, `major`, `minor` | `Convention` | SimplerQMS ("Critical," "Major," or "Minor"); NominalQC ("Severity" dropdown) | **Not** an ISO classification. Firms disagree on the boundaries; our mock data should show two Asteria NCs with the same failure graded differently by different people. |
| `defect_category` | controlled vocabulary | `Convention` | NominalQC ("Defect category" dropdown, editable on a CONFIG sheet) | The "editable CONFIG sheet" detail is the realism: categories drift over time, exactly as MOCK-DATA.md's classification-variation model predicts. |
| `bracketing_assessment` | text + population rows | `Convention` | SimplerQMS: *"Bracketing Assessment — evaluation of potentially affected adjacent lots or batches"* | **Adopt this vocabulary.** It is the real-world name for workflow 5's job, and using it makes our UI legible to a quality professional on sight. |
| `status` | enum per §1.3 | `Convention` | NominalQC ("Status" dropdown) | |
| `target_close_date` / `days_open` / `overdue` | date / int / bool | `Convention` | NominalQC: "Days Open counter", "OVERDUE flag against each NCR's target close date" | Derived, but present in the export because the spreadsheet computes it. |
| `estimated_cost` | currency, nullable | `Convention` | NominalQC: "Estimated cost column feeding a total nonconformance cost KPI" | Useless to us regulatorily; include it because it is in real exports and because its presence tells you which register the data came from. |
| `linked_capa_id` | ref, nullable | `Mandated` *as content* | ISO 13485 §8.5.2 (corrective action evaluated from nonconformities); QSIT objective 4 names 820.90 as a CAPA data-source linkage | Nullable is correct: most NCs never reach CAPA (see §2.1). |
| `linked_complaint_ids` | array of refs | `Mandated` *as content, with a caveat* | ISO 13485 §8.2.2 → §8.3.3 hand-off; MDR Art. 10(9)(l) | See §1.6 — this is where WORKFLOW.md §1.1 needs a nuance, not a retraction. |
| `linked_change_control_ids` | array of refs | `Convention` | eQMS practice: nonconformances are "automatically linked… to related quality events (complaints, CAPAs, audits, change controls)" ([Rimsys](https://www.rimsys.io/blog/nonconformance-reporting-medical-device-manufacturers)) | |
| `advisory_notice_ref` / `field_action_ref` | ref, nullable | `Mandated` | ISO 13485 §8.3.3 (advisory notices, records of issue and receipt); MDR Art. 87(1)(b) | |
| `advisory_notice_decision` | enum: `issued`, `considered_not_issued`, `n/a` + rationale | `Mandated` | MDSAP: *"Select records for review of quality problems that were evaluated for potential issuance of advisory notices (include records where a decision was made not to issue an advisory notice as well as records of decision to issue advisory notices) and assess whether the organization has taken actions appropriately based on risk and documented the rationale."* ([MDSAP MAI](https://www.fda.gov/media/147373/download)) | A second negative-decision-as-record, independent of the CAPA one. Most products miss this. |
| **provenance block** | see §0.3 | `Product` | §0.3 | |
| `population_expansion_run_id` | ref to an expansion run | `Product` | Workflow 5 | See §1.7. |
| `shipped_determination` | `{answer, as_of, sources[], confidence}` | `Product` | Workflow 5 node A2 ("did any of it ship? joins ERP, shipment, installed base") | See §1.7. Separate from `delivery_fork` on purpose: the fork is a human decision, this is the agent's evidence for it. |
| `erp_qty_reconciliation` | `{erp_qty, register_qty, variance, reconciled_at, reconciled_by}` | `Product` | Workflow 5; §1.8 | The realism field. Real registers do not reconcile; making the failure to reconcile explicit is a product feature. |

#### `nc_disposition` (child)

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `disposition` | enum: `scrap`, `return_to_supplier`, `downgrade`/`regrade`, `use_as_is`, `rework`, `repair` | `Mandated` *as content* | ISO 13485 §8.3.2 (eliminate the nonconformity / authorise use, release or acceptance under concession / preclude original intended use); FDA NC slides, slides 28–35 name **Scrap, Return to Supplier, Downgrade, Use as Is, Rework** | ISO gives three *categories*; the five-to-six named dispositions are FDA-named and universal. `repair` is in ISO 9000's correction examples but is often folded into `rework` in practice — a genuine naming inconsistency to reproduce. |
| `sub_population_ref` | ref to `nc_affected_population` rows | `Product` | Workflow 5 | The field that makes mixed dispositions representable at all. |
| `justification` | long text | `Mandated` | FDA-era §820.90(b)(1): *"Documentation shall include the justification for use of nonconforming product and the signature of the individual authorizing the use."*; ISO 13485 §8.3.2 (justification for concession) | |
| `authorised_by` | person ref | `Mandated` | ISO 13485 §8.3.2 requires records of the concession **and the identity of the person(s) authorising** it; FDA-era §820.90(b)(1) "signature of the individual authorizing the use" | |
| `authority_basis` | ref to approval-authority matrix row + version | `Product` | Workflow 7; MOCK-DATA.md lists "Approval authority matrix" as required QMS content | Not mandated as a field. It is the only way to *check* the mandated signature was from someone with authority — see §1.8. |
| `mrb_meeting_ref` | ref, nullable | `Convention` | FDA NC slides, slide 18: *"One practice is through Material Review Board (MRB) or Material Review Committee (MRC). Not ad hoc, but in an approved procedure"*; SimplerQMS ("Quality Manager approves dispositions") | FDA calls MRB an **industry practice example**, not a requirement. The *responsibility and authority* for review and disposition is what is mandated (FDA-era §820.90(b)(1): "procedures that define the responsibility for review and the authority for the disposition"). Do not label an MRB field `Mandated`. |
| `regulatory_requirements_met` | boolean + basis | `Mandated` | ISO 13485 §8.3.2 (concession permitted only where applicable regulatory requirements are met) | |
| `rework_instruction_ref` | ref, nullable | `Mandated` | ISO 13485 §8.3.4 (rework instructions subject to the same authorisation and approval as the original instruction) — paraphrased; corroborated by [i3C Global](https://www.i3cglobal.com/iso-13485-rework/) and [qmsWrapper lesson 18](https://qmswrapper.com/control-of-nonconforming-products-in-iso-13485-lesson-18/) | |
| `reverification_result` | `{result, acceptance_criteria_ref, data_ref, date, by}` | `Mandated` | ISO 13485 §8.3.4; FDA-era §820.90(b)(2): *"procedures for rework, to include retesting and reevaluation of the nonconforming product after rework, to ensure that the product meets its current approved specifications"* | Re-verification is against the **original/current approved** specification, not a relaxed one. FDA's worked example: "Balloon burst strength of re-sterilized product needs to meet the original specification". |
| `adverse_effect_determination` | text + verdict | `Mandated` | ISO 13485 §8.3.4; FDA-era §820.90(b)(2): *"Rework and reevaluation activities, including a determination of any adverse effect from the rework upon the product, shall be documented in the DHR"* | Note the US text puts this in the **Device History Record**, not the NC register. Our register should hold the determination *and* a `dhr_ref`. |
| `dhr_ref` | ref | `Mandated` *US-specific* | FDA-era §820.90(b)(2) (sentence above) | Under QMSR this content routes through ISO 13485 §7.5.1/§8.3.4 records. Flagged as a jurisdictional delta. |

#### `nc_affected_population` (child)

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `population_key_type` | enum: `lot`, `serial`, `serial_range`, `shipment`, `supplier_lot`, `tool_or_mould`, `software_version`, `production_line` | `Product` | Workflow 5 node A1 ("same lot · adjacent lots · same tool · same supplier · same software version") | These five axes are named in DIAGRAMS.md. GHTF independently names the same axes: "range of affected devices, patient outcome, process, production lines, operator" (§6.6). |
| `population_key` | string | `Product` | as above | |
| `qty` | integer | `Convention` | NominalQC | |
| `ship_status` | enum: `in_stock`, `in_transit`, `delivered`, `installed`, `returned`, `consumed_discarded`, `unknown` | `Product` | Workflow 5 | `consumed_discarded` exists because PulsePatch is single-use for ≤72 h — for a patch lot shipped four months ago, "did any of it ship?" has a different answer from "is any of it recoverable?". That distinction changes what §8.3.3 action is even possible, and no generic register models it. |
| `ship_evidence_ref` | ref (ERP shipment line, installed-base record) | `Product` | Workflow 5 | |
| `expansion_basis` | enum: `same_lot`, `adjacent_lot`, `same_tool`, `same_supplier_lot`, `same_sw_version`, `same_line`, `manual` + query text | `Product` | Workflow 5, workflow 9 | The auditable reason this sub-population is in scope. |
| `expansion_as_of` | timestamp (data snapshot) | `Product` | Workflow 6's denominator discipline, applied to scope | The population changes as shipments continue. Without a snapshot time the rollup is unreproducible. |
| `inspection_result` | text, nullable | `Convention` | GHTF Annex D: *"All additional available lots of this component were inspected with a 95/95 inspection plan and no additional lots were confirmed to have the issue."* | The *negative* expansion result is evidence and must be storable. A population row that was checked and cleared is not the same as one never checked. |

### 1.5 What a real NC export looks like

Three shapes, all of which our mock data should contain for the same company:

1. **Spreadsheet with tabs** — the dominant reality for a company Asteria's size. A commodity NCR tracker ships as: a `LOG` sheet, a `CONFIG` sheet holding every dropdown's allowed values, a `DASHBOARD` sheet with "Total / Open / Closed / Overdue cards, average days-to-close, estimated NC cost", and a separate "Printable one-page NCR report form" with its own root-cause and "CAPA reference" fields ([NominalQC](https://www.nominalqc.com/templates/ncr-log-template)). **The form and the log disagree**, because someone retypes between them. That is the single most realistic thing about it.
2. **eQMS table export** — one flat CSV per record type, with separate exports for NCR, CAPA, SCAR, complaints and audit findings, because the eQMS models them as separate linked modules ([1factory](https://www.1factory.com/ncr-capa-scar-complaint.html)). Child rows arrive as either repeated parent columns or a second file; both are realistic.
3. **PDF log** — the approved, signed rendition filed per quarter, which is the version with signatures and the version whose numbers no longer match the live system. MOCK-DATA.md already calls for "Register values that occasionally lag behind repository state"; this is where that shows up.

**Real column-header wording, including bad ones.** Cited, real: `NCR No`, `Date`, `Lot affected`, `Quantity`, `Defect category`, `Severity`, `Disposition`, `Owner`, `Status`, `Department`, `Source`, `Work center`, `Days Open`, `OVERDUE`, `Bracketing Assessment`, `Reference Standard or Requirement`, `Approval/Sign-off` (NominalQC, SimplerQMS). `RTV` appears as a disposition value with no legend — it means *return to vendor*, and a reader who does not already know that cannot decode the column.

Header pathologies worth reproducing (these are my own characterisation of ordinary spreadsheet decay, **not** cited — treat as realism guidance, not findings): abbreviations that shadow real fields (`Disp.`, `Qty`, `Resp.`, `Eff Chk Due`); two columns that mean the same thing (`Closed?` and `Date Closed`, disagreeing); a `Status` column whose values are `Open`, `open`, `OPEN`, `In Progress`, `WIP`, `Closed`, `Closed - verified`; merged two-row headers that break every CSV parser; an `Owner` column containing initials (`PR`, `SW`) resolvable only against the roster; `Notes`, `Notes2`, and `Comments (old)`; and a trailing column added by one person in one quarter and never populated again. For a precedent that even *official* documents carry typos, note FDA's own nonconforming-product deck prints the CAPA regulation as **"829.100"** instead of 820.100 ([FDA NC slides, slide 4](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf)).

### 1.6 Links out — and the complaint ↔ NC question

**Direction of every link:**

| From → To | Cardinality | Direction of authority | Source |
|---|---|---|---|
| NC → complaint | many-to-many | Complaint is upstream; the NC points at it. Do **not** make the complaint point at the NC as its only link — the complaint closes on its own criteria. | ISO 13485 §8.2.2 → §8.3.3 hand-off |
| NC → CAPA | many-to-one (many NCs can feed one CAPA) | NC points at CAPA; CAPA also lists its inputs. Bidirectional, because trending needs the reverse direction. | ISO 13485 §8.5.2; QSIT objective 4 linkage list |
| NC → change control | many-to-many, nullable | NC points at the change that caused it *or* the change that fixed it — these are different relationships and need a `relation` qualifier (`caused_by` / `remediated_by`). | [Rimsys](https://www.rimsys.io/blog/nonconformance-reporting-medical-device-manufacturers) |
| NC → advisory notice / field action | one-to-many | NC points out. | ISO 13485 §8.3.3 |
| NC → supplier / SCAR | many-to-one | Outward, to a register this note does not cover. | MDSAP Task 8 (external party notified) |
| NC → audit finding | many-to-one, nullable | An audit finding can *be the detection event* for an NC. Link points from NC back to the finding. | ISO 13485 §8.2.4 → §8.5.2; [OpenRegulatory SOP CAPA](https://github.com/openregulatory/templates) lists "Audit findings" as a CAPA input |
| NC → DHR / batch record | one-to-one per lot | Outward. | FDA-era §820.90(b)(2) |

**Does WORKFLOW.md §1.1 need softening? Yes — a little, and in one specific place.**

The position to defend: *complaint and NC are two linked records in two registers, never one merged record.* Evidence **for** it is strong:

- The clauses are structurally separate, and so are the audit tasks. MDSAP audits nonconforming product in stock or returned under **Task 8**, nonconforming product detected after delivery under **Task 9**, and complaint handling under **Task 12** — three tasks, three record samples, three sets of conformity criteria ([MDSAP MAI](https://www.fda.gov/media/147373/download)).
- Commercial eQMS platforms model them as distinct-but-linked record types, not one table ([1factory](https://www.1factory.com/ncr-capa-scar-complaint.html)).
- US record-content requirements attach to the complaint record specifically (§820.35(a): device name, date received, UDI/UPC, complainant name/address/phone, nature and details, correction or corrective action taken, reply to complainant) and have no NC-register counterpart ([Cornell LII §820.35](https://www.law.cornell.edu/cfr/text/21/820.35)). A merged record would have to carry complainant contact details on a manufacturing nonconformity, which is nonsense.

Evidence that the claim is **slightly too strong**, and the softening I'd make:

1. **FDA's own training deck routes returned defective product into the complaint system, not the NC system.** Slide 17: a returned product with defects is *"Handled within the complaint system"* with the footnote *"not within the scope of this talk"* — in a presentation whose subject is nonconforming product. Yet the same deck, four slides earlier, quotes §820.3(r) defining "product" as *"components, manufacturing materials, in-process devices, finished devices, and returned devices"* ([FDA NC slides, slides 5 and 17](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf)). **Returned devices are simultaneously in scope of NC control by definition and routed away from it by FDA's own teaching.** This is a genuine disagreement inside one FDA document, not a misreading.
2. **Practitioner templates put complaint origin *on the NC row*.** Cognidox's guide says an NCR should capture "the day, date, description of the defect, and whether it is of internal origin **or a customer complaint**" ([Cognidox](https://www.cognidox.com/blog/a-guide-to-non-conformance-reports)). So a material slice of real industry does open an NC per complaint and distinguishes them with an origin field — which is one record, not two, for that firm.

**Revised position for our data model, which I believe survives an auditor:**

> Complaint and NC remain **two registers with two lifecycles and two closure criteria**. The NC register carries an `origin` field whose allowed values include `customer_complaint`, and a `linked_complaint_ids` array. A complaint does not auto-create an NC; an NC is created when investigation confirms product nonconformity. **But** the model must tolerate the common real-world state where an organisation has recorded only one of the two — because Asteria's own source data will contain complaint records with confirmed product nonconformity and no NC record, and that gap is a finding our product should surface rather than a schema violation it should prevent.

The one sentence in WORKFLOW.md §1.1 I would change is "Two linked records, two registers, two closure criteria. **Not one merged record.**" → add: *"Some organisations do record a single NC per complaint with an origin field; that is defensible but makes the §820.35(a) complaint-record content and the §8.3 disposition content share one row, and it is the weaker design. Our model keeps them separate and treats a missing counterpart record as a gap to flag, not as an invalid state."*

### 1.7 The affected-population problem

Workflow 5 expands the population and answers "did any of it ship?". Here is the minimum field set for that to be recorded with an evidence trail, and a note on why each exists.

**On the register row:**

| Field | Why |
|---|---|
| `extent_determination` (text) | The mandated content (QSIT objective 5). |
| `qty_affected_total`, `qty_delivered`, `lots_affected_count` (derived) | The rollups a human reads before signing the fork. **Derived, never typed** — typed rollups are how registers stop reconciling. |
| `delivery_fork` + `fork_decided_by` + `fork_decided_at` | The amber gate. DIAGRAMS.md workflow 5 `G1` is explicitly human: "getting this wrong is a serious finding". The decider's identity must be on the record, separately from whoever raised the NC. |
| `population_expansion_run_id` | Points at an immutable expansion run, so re-running later produces a new run rather than mutating history. |
| `shipped_determination` = `{answer, as_of, sources[], confidence}` | The agent's answer, held separately from the human's `delivery_fork`. If they ever differ, that difference is the most interesting row in the database. |

**On each expansion run (`nc_population_expansion_run`):**

| Field | Why |
|---|---|
| `run_id`, `run_at`, `run_by` (agent version or human) | |
| `axes_queried` (array of the five axes) | Proves which axes were *considered*, including those that returned nothing. An axis never queried and an axis queried-and-clear are different evidentiary positions, and only the register can tell them apart. |
| `source_snapshots` = array of `{system, export_or_query, as_of, row_count}` | Workflow 5 joins ERP, shipment and installed-base data. Without snapshot times the join is unreproducible and the §8.3.3 conclusion is unfalsifiable. Precedent: FDA cited Hologic because a risk assessment computed an occurrence rate over units sold 2016–2024 against complaints from 2021–2024 — a denominator/numerator period mismatch ([FDA warning letter, Hologic](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/hologic-inc-698214-12182024)). The same failure mode applies to population scoping, not only to trending. |
| `unresolved_identifiers` | Workflow 1's free-text serials that could not be matched. A population with 40 matched and 6 unmatched serials is not a complete population, and the record must say so. |
| `conclusion` + `conclusion_confidence` + `reviewed_by` | |
| `superseded_by_run_id` | Populations grow. The §8.3.2 decision taken on run 1 must remain readable after run 2 turns it into a §8.3.3. |

**On each population row:** `inspection_result` (GHTF's 95/95-plan example, above) is the field most registers lack and most need — it is the difference between "we expanded" and "we expanded and cleared".

**What GHTF's worked example tells us the output should read like.** *"Initial extent of the issue is restricted to supplier lot #678. All unused components and product built with components from this lot were controlled on [date]. No product built with this lot had been distributed."* ([GHTF/SG3/N18 Annex D](https://www.imdrf.org/sites/default/files/docs/ghtf/final/sg3/technical-docs/ghtf-sg3-n18-2010-qms-guidance-on-corrective-preventative-action-101104.pdf)). Three sentences: scope, containment with a date, ship answer. That is the target output of workflow 5, and it is three fields, not a paragraph.

### 1.8 Fields routinely incomplete or disagreed-on in reality

Each of these is a product opportunity, and each should appear in the Asteria mock data at a realistic rate.

| Pathology | Evidence | What the register needs |
|---|---|---|
| **NC records with no documented investigation or disposition at all** | *"six out of six nonconformance reports reviewed during the inspection did not include documented investigations or dispositions"* — named records NC 1797, 1804, 1786, 1787, 1790, 1796; two of them "Missing documentation and undated records" ([Criticare warning letter](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/criticare-technologies-inc-686915-07122024)) | Completeness as a first-class derived field, not a validation that blocks saving. Also: **undated records** — `date_raised` must be nullable with a flag, because the real data has blanks. |
| **Disposition authorised by someone without the authority** | Mandated content is the authoriser's identity (§8.3.2 / FDA-era §820.90(b)(1)); the *authority* to authorise comes from a separate approval-authority matrix, which MOCK-DATA.md lists as required QMS content. Nothing in the record links the two. | `authority_basis` → approval-matrix row + version, evaluated **as at the disposition date**, not as at today. Role changes (MOCK-DATA.md: `employee_role_changed`) silently invalidate historic approvals otherwise. |
| **Concession creeping into routine** | FDA QSR preamble comment #156: concessions *"should be closely monitored and not become accepted practice"*; QSIT objective 6 instructs reviewing concessions "to verify that the concessions have been made appropriate to product risk, within the requirements of the quality system and **not solely to fulfill marketing needs**" | A concession *rate* per product and per period, and a repeat-concession flag keyed on `requirement_not_met`. The third use-as-is on the same spec in a quarter is the signal. |
| **Quantities that do not reconcile with ERP** | No single clause; the mechanism is well evidenced — a separate printable NCR form alongside a log sheet with manual retyping ([NominalQC](https://www.nominalqc.com/templates/ncr-log-template)), plus MOCK-DATA.md's stated rule that ERP holds "corrections and cancelled transactions" and that "shipment history does not prove current installation or usage" | `erp_qty_reconciliation` with a variance and a `reconciled_at`, and an explicit `unreconciled` state. Do not auto-correct the register to match ERP: the divergence is the evidence. |
| **Severity graded inconsistently** | Severity is `Convention`, not standardised (§1.4) | Record `graded_by` and keep the grading history. Two graders disagreeing is data. |
| **`delivery_fork` left `undetermined` past close** | §8.3.2 vs §8.3.3 is a legal fork | Block *closure*, not *saving*. And surface aging in the `undetermined` state as its own metric. |
| **Rework re-verification against a relaxed spec** | FDA-era §820.90(b)(2) requires conformance to *current approved* specifications; FDA's example insists on "the original specification" | `reverification_result.acceptance_criteria_ref` must resolve to the original spec document + revision, and a mismatch between that revision and the `requirement_not_met` revision should flag. |
| **"No fault found" returns closed without an NC** | MOCK-DATA.md lists "'No fault found' conclusions" as a natural characteristic of the service/RMA system | Nothing to add to the schema — but the product should notice a returned-unit population with NFF conclusions and no corresponding NC, which is §8.3.3 exposure hiding in the service system. |

---

## 2. CAPA register

### 2.1 Grain — and the correction firewall

**One row = one corrective-action case or one preventive-action case.** Child tables for action items and for effectiveness checks:

```text
capa_register  (one row per case, including cases that decided "no action")
  ├── capa_input          one row per contributing record (NC, complaint, audit finding, trend, PMS signal)
  ├── capa_action         one row per action item: type, owner, due, done, evidence
  └── capa_effectiveness  one row per effectiveness check: criteria, window, result
```

**The correction firewall — the thing the brief says must be enforced in the data model.** ISO 9000:2015 §3.12.2 defines **correction** as action to eliminate a detected nonconformity; §3.12.3 defines **corrective action** as action to eliminate the cause and prevent recurrence. GHTF/SG3/N18 restates both and adds the note that *"There is a distinction between correction… and corrective action"*, and that corrections "can be, for example, rework… or re-grade" ([GHTF §2.1, §2.2](https://www.imdrf.org/sites/default/files/docs/ghtf/final/sg3/technical-docs/ghtf-sg3-n18-2010-qms-guidance-on-corrective-preventative-action-101104.pdf)).

Enforcement rule: **a correction is never a row in the CAPA register.** Containment, stop-shipment, rework, regrade, scrap, advisory notice — all of these are `nc_disposition` rows or NC-row fields. The CAPA register's `capa_action` child table has `action_type ∈ {corrective, preventive}` with **no `correction` value**. Where a CAPA's narrative needs to reference the correction that was already taken, it does so by pointing at the NC row (`capa_input` → NC), not by creating an action.

This is stricter than GHTF, which lists "Correction" as one of four possible documented outcomes at its §6.3 *Identify Actions* step. The reconciliation: GHTF is describing one improvement process that spans both; we are describing two registers. Our rule is that the *decision* to take a correction is recorded in the CAPA evaluation (as an outcome), while the *correction itself* is executed and recorded in the NC register. That keeps "closing a CAPA on the correction alone" — WORKFLOW.md §10's named common error — structurally impossible rather than merely discouraged.

**Why not one row per action item?** Because root cause, verification, and the effectiveness verdict are properties of the case, not of each action. ISO 13485 §8.5.2's documented procedure requires reviewing nonconformities, determining causes, evaluating the need for action, determining and implementing action, recording the results of any investigation and of action taken, and reviewing effectiveness — a single lifecycle over a set of actions, corroborated by [13485quality.com](http://13485quality.com/iso-13485-standard2016-8-5-2-corrective-action/) (fetched indirectly; see Confidence notes) and [i3C Global](https://www.i3cglobal.com/iso-13485-corrective-and-preventive-action/).

**Corrective and preventive in one register or two?** One register, one `capa_type ∈ {corrective, preventive, both}` discriminator, with a hard rule that a preventive action can never be the sole response to a *detected* nonconformity. GHTF is explicit: *"By its very nature preventive action can not follow a nonconformity"* (§6.3) — and GHTF deliberately avoids the acronym "CAPA" because *"the concept of corrective action and preventive action has been incorrectly interpreted to assume that a preventive action is required for every corrective action."* Our register must therefore permit, and our UI must not nag about, a corrective-only case with `preventive_action: not applicable` — which is exactly what GHTF's own worked example records ("Preventive action: Not applicable.", Annex D).

### 2.2 Identity and numbering

- `CAPA-####` or `CAPA-YYYY-###`. The warning-letter corpus again shows bare sequentials: `CAPA 1098`, `CAPA 1033`, `CAPA 1059`, `CAPA 1054`, `CAPA 1046`, `CAPA 1050`, `CAPA 1086/1088/1090/1091/1094` ([Criticare](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/criticare-technologies-inc-686915-07122024)). Note that CAPAs 1033 and 1059 were opened in **December 2017 and July 2018** and were still open, unfinished, at a 2024 inspection. Age is not a rounding error in this domain; our mock data should contain at least one multi-year-open CAPA.
- OpenRegulatory's free template numbers CAPAs with a plain integer (`1`) in a column literally named `CAPA ID` ([openregulatory/templates `list-capa.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/capa/list-capa.md)). Small companies really do this.
- **Findability requires:** input category, product/model, owner, date opened, status, due date, effectiveness-check due date, and the linked NC/complaint/audit IDs. The first of these is a real template column (`Input Category`, OpenRegulatory) and is worth adopting verbatim — it is how a quality manager answers "where do our CAPAs come from?" at management review.

### 2.3 Lifecycle / status values

| State | Meaning | Source / note |
|---|---|---|
| `evaluation_open` | A potential CAPA is being assessed | WORKFLOW.md §7 step 1 |
| **`evaluated_no_action`** | Assessed, declined, rationale recorded | The negative decision as a record. MDSAP Task 5: assessing conformity includes *"confirming that the medical device organization's decision not to take corrective action has been made using appropriate risk based decision making including a determination that the finished device meets risk acceptability criteria and looking for product or quality problems or trends that continued or began after the actions were implemented"* ([MDSAP MAI](https://www.fda.gov/media/147373/download)). QSIT objective 6 samples the same records. **This state is mandatory-by-audit-expectation and most commercial registers cannot represent it** — see §2.8. |
| `evaluated_correction_only` | Assessed; a correction was taken in the NC register and no corrective action is warranted | GHTF §6.3 outcome "No further action necessary… with continuous monitoring / Acceptance under concession and continuance of monitoring" |
| `open_investigating` | | GHTF Phase III §6.1 |
| `root_cause_identified` | | GHTF §6.2 |
| `actions_defined` | Action plan documented, **including effectiveness criteria** | GHTF §6.3 — this is where criteria are locked; see §2.7 |
| `actions_verified` | Actions verified/approved **before** implementation | GHTF §6.4: *"Before the implementation of action(s), a manufacturer should verify the identified action(s) and approve their implementation."* FDA QSIT objective 8: *"Determine if corrective and preventive actions were effective and verified or validated prior to implementation."* |
| `implementing` | | GHTF §6.5 |
| `awaiting_effectiveness` | Implemented; monitoring window running | |
| `effectiveness_verified` | | |
| `effectiveness_failed` → `reopened` / `superseded` | Actions were not effective | GHTF §6.6: *"If the manufacturer finds the actions are not effective, the manufacturer should re-initiate Phase III activities."* If new issues were created: re-enter Phase II. |
| `closed` | | |
| `closed_overdue_effectiveness` | Closed administratively with the check outstanding — an **anti-state we must be able to represent** | Criticare: CAPAs *"closed despite not having an adequate root cause investigation and no effectiveness check plan"* |
| `cancelled` / `duplicate_of` / `merged_into` | | Merges are a hard human gate (WORKFLOW.md §9) |

### 2.4 CAPA register — field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `capa_id` | string, unique | `Convention` | [OpenRegulatory `list-capa.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/capa/list-capa.md) (`CAPA ID`) | |
| `capa_type` | enum: `corrective`, `preventive`, `both` | `Mandated` | ISO 13485 §8.5.2 vs §8.5.3 are separate clauses; ISO 9000 §3.12.3 vs preventive action | Mislabelling corrective as preventive is WORKFLOW.md §10's named error. Make the type a required discriminator, not a tag. |
| `input_category` | enum: `nonconformity`, `complaint`, `audit_finding`, `pms_trend`, `management_review`, `internal_bug`, `supplier`, `service`, `returned_product`, `concession_trend`, `regulatory` | `Mandated` *as content* / `Convention` *as enum* | ISO 13485 §8.5.2 (corrective action arises from nonconformities including complaints); QSIT objective 2 requires the firm to have identified "appropriate sources of product and quality problems" and names them: *"data and information from all acceptance activities, complaints, service, and returned product records… information relating to concessions (quality and nonconforming products), quality records… quality audits, installation reports, lawsuits"*; column header `Input Category` from [OpenRegulatory](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/capa/list-capa.md) | The `concession_trend` value is worth calling out: QSIT explicitly names concessions as a CAPA data source, which closes the loop from §1.8's concession-creep pathology. |
| `capa_input[]` | child rows: `{record_type, record_id, contribution_note}` | `Mandated` *as content* | ISO 13485 §8.5.2; QSIT objective 5: *"The analysis of product and quality problems should also include the comparison of problems and trends across different data sources to establish a global, and not an isolated view, of a problem."* | One CAPA, many inputs, from **different registers**. A single `source_record_id` column cannot hold this and is the commonest schema mistake. GHTF reinforces it: "Is the nonconformity from a single data source? Does the current nonconformity correlate with nonconformities from other data sources? Are multiple data sources identifying the same nonconformity?" (§6.1). |
| `date_created` | date | `Convention` | OpenRegulatory `Date Created` | |
| `problem_statement` | long text | `Mandated` *as content* | ISO 13485 §8.5.2 (reviewing nonconformities); GHTF §6.1 requires a documented investigation plan whose first element is "Description of the nonconformity expressed as a problem statement", and Annex D gives the model wording | GHTF also requires it be "reviewed and refined as appropriate" → keep a revision history, do not overwrite. |
| `description` | long text | `Convention` | OpenRegulatory `CAPA Description` | |
| `evaluation_rationale` | long text | `Mandated` | ISO 13485 §8.5.2 (evaluating the need for action, proportionate to effects); MDSAP Task 5 (decision not to act must be risk-based) | **Required even when the answer is "no CAPA".** This is the field that makes `evaluated_no_action` a record rather than an absence. |
| `risk_acceptability_determination` | text + verdict + risk-file ref | `Mandated` | MDSAP Task 5: the no-action decision must include *"a determination that the finished device meets risk acceptability criteria"* | Specifically tied to the negative decision. Most registers have nowhere to put it. |
| `proportionality_basis` | text | `Mandated` *as content* | ISO 13485 §8.5.2 (action proportionate to the effects of the nonconformities encountered) and §8.5.3 (proportionate to potential impact); MDSAP Task 5 ("appropriate to the risk") | FDA's own heuristic for the handle-vs-escalate boundary is quotable and should be the UI's prompt: handle under nonconforming-product control when the issue is *"Easy/specific correction · Isolated · Minor · Not a Design issue · Not a Manufacturing issue"*; escalate to CAPA when *"No easy/specific correction · Recurring (based on valid analytical method) · Severe · Design issue · Manufacturing issue"* — and *"Too many nonconformances handled under 21 CFR 820.90 may fail to address systemic issues… Too many nonconformances referred to CAPA will overwhelm the system"* ([FDA NC slides, slides 40–42](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf)). |
| `decision` | enum: `open_capa`, `no_action`, `correction_only`, `defer` + `decided_by` + `decided_at` | `Mandated` *as content* | as above; WORKFLOW.md §7 step 2 | `decided_by` must be a named human: "Opening, approving, and closing a CAPA" is a hard gate (WORKFLOW.md §9). |
| `investigation_plan_ref` | ref | `Convention` | GHTF §6.1: *"Good practice shows that a documented plan should be in place prior to conducting the investigation"* — with seven named elements: problem statement, scope, team and responsibilities, activities, resources, methods and tools, timeframe | GHTF says "good practice", so `Convention`, but from the strongest possible convention source. |
| `investigation_scope` | text | `Mandated` *as content* | GHTF §6.1 ("Determine the extent of the nonconformity or potential nonconformity"); QSIT objective 5 (full extent before risk analysis) | |
| `root_cause` | long text | `Mandated` | ISO 13485 §8.5.2 (determining the causes); QSIT objective 6: *"Determine if failure investigations are conducted to determine root cause (where possible)"* and *"Select one significant failure investigation that resulted in a corrective action and determine if the root cause had been identified so that verification or validation of the corrective action could be accomplished"*; MDSAP Task 3 | "Where possible" is in the source. A CAPA with no determinable root cause is legal; a CAPA with no *record of the attempt* is not. |
| `root_cause_method` | enum: `five_whys`, `fishbone_ishikawa`, `cause_effect_diagram`, `pareto`, `change_analysis`, `is_is_not`, `risk_analysis`, `fault_tree`, `other` | `Convention` | GHTF §6.2 names exactly: *"Cause and effect diagrams · 5 Why's analysis · Pareto charting · Fishbone/Ishikawa cause and effect diagrams · Change analysis · Risk analysis techniques · Is/Is Not"*; OpenRegulatory's SOP names Five Whys as its preferred method | The *method* is not mandated; recording it is near-universal. Note GHTF lists "Cause and effect diagrams" and "Fishbone/Ishikawa" as separate bullets although they are the same technique — a real-world taxonomy inconsistency to preserve. |
| `root_cause_is_symptom_check` | boolean + note | `Product` | Workflow 7 gap-flagging; GHTF §6.2 *"Ensure that causes are identified, not the symptoms"*; §6.1 *"Require that symptoms be distinguished from root causes"* | See §2.8 on "operator error". The field exists so the agent can flag without deciding — root cause conclusion is a hard gate. |
| `contributing_factors[]` | array of text | `Mandated` *as content* | GHTF §6.2: *"Check for more than one root cause"*; §6.1 *"Acknowledge that there are likely to be several causes of an event; hence, the investigation should not cease prematurely"* | A single `root_cause` text field structurally encourages the single-cause error. Make it an array or add this sibling. |
| `actions[]` | child rows, see below | `Mandated` | ISO 13485 §8.5.2 (determining and implementing the action needed) | |
| `adverse_implications_assessment` | text + verdict | `Mandated` | ISO 13485 §8.5.2 (verifying the action does not adversely affect the ability to meet applicable regulatory requirements or the safety and performance of the device) — paraphrased; corroborated by [i3C Global](https://www.i3cglobal.com/iso-13485-corrective-and-preventive-action/) and [Registrar Corp](https://www.registrarcorp.com/blog/medical-devices/iso-13485/measurement-analysis-improvement-in-medical-devices/); QSIT objective 8: *"Confirm that corrective and preventive actions do not adversely affect the finished device."* | Real column header: `Potentially Adverse Implications` (OpenRegulatory) — and in the shipped template's worked example **that cell is blank**. That is the realistic default state. |
| `verification_of_actions` | `{protocol_ref, acceptance_criteria, result, date, by}` | `Mandated` | GHTF §6.4 (verify and approve before implementation); QSIT objective 8 (*"verified or validated prior to implementation"*); MDR Art. 10(9)(l): *"management of corrective and preventive actions and verification of their effectiveness"* | QSIT adds the engineering expectations: *"establishing a verification or validation protocol; verification of product output against documented product requirements and specifications; ensuring test instruments are maintained and calibrated; and that test results are maintained, available and readable."* |
| `validation_required` | boolean + ref | `Mandated` *conditional* | GHTF §6.4 (validation where process re-validation is needed, or user needs / intended use change → design validation); QSIT objective 8: *"Corrective actions must include the application of design controls if appropriate"* | For Asteria, a PulseOne firmware corrective action crosses into §7.3 design controls and the change control register. |
| `effectiveness[]` | child rows, see §2.7 | `Mandated` | ISO 13485 §8.5.2 (reviewing the effectiveness of the corrective action taken); MDR Art. 10(9)(l) | |
| `implementation_change_control_ids` | array of refs | `Mandated` *as content* | WORKFLOW.md §7 step 5; MDR Art. 10(9)(a): the QMS must address *"a strategy for regulatory compliance, including… procedures for management of modifications to the devices covered by the system"*; MDSAP Task 7 links CAPA to production-process change and re-validation | The join between this register and register 4. If a CAPA changed a document, a process, a supplier or a spec, the change record is the implementation evidence. |
| `training_ids` | array of refs | `Convention` | WORKFLOW.md §7 step 5; GHTF §6.5 lists "Training" among implementation items | GHTF warns against training as a sufficient corrective action: *"changing the procedure and training of personnel to the revised procedure may not, by itself, be appropriate or sufficient to address the systemic cause(s)"* (§6.3). Worth a UI warning. |
| `management_review_ref` | ref | `Mandated` | QSIT objective 10 (dissemination including for management review); MDSAP Task 11: *"Determine if relevant information regarding nonconforming product, quality management system nonconformities, corrections, corrective actions, and preventive actions has been supplied to management for management review."*; GHTF §7.2 | GHTF also says counting open/closed CAPAs is **not** sufficient management-review input: *"Merely providing the number of improvement actions or the number of how many improvement actions are opened or closed to the management review process are not sufficient in assessing the effectiveness of the processes."* Relevant to what we put on a dashboard. |
| `dissemination_record` | array of `{role, person, date, what}` | `Mandated` | QSIT objective 10; MDSAP Task 11 | Almost never implemented in commercial registers; cheap for us because workflow 8 already tracks who was told what. |
| `regulatory_reportability_considered` | enum: `yes_reported`, `yes_not_reportable`, `not_applicable` + ref | `Mandated` *as content* | MDSAP Task 14: *"confirming that reportable events were evaluated for corrective action when necessary"* (and the inverse); MDR Art. 10(9)(k) | Points at the vigilance register; never decided here (hard gate). |
| `field_action_required` | boolean + ref | `Mandated` *as content* | MDR Art. 10(12) (quoted in §1.4); ISO 13485 §8.3.3; MDSAP Task 9 and Task 15 | |
| `owner` | person ref | `Convention` | Universal; OpenRegulatory assigns the QMO as process owner | |
| `status`, `date_closed` | enum per §2.3 / date | `Convention` | OpenRegulatory `Date Closed` | Blank in the shipped template's example row. |
| `due_date`, `effectiveness_due_date` | dates | `Convention` | Ubiquitous in eQMS CAPA logs | These two being separate is the whole point of §2.7. |
| `without_undue_delay_basis` | text / elapsed-time derivation | `Mandated` *as content* | ISO 13485 §8.5.2 (action taken without undue delay); OpenRegulatory SOP step 2 cites it explicitly; GHTF §5: *"There may be predefined events that due to the significance of the risk will be escalated to Phase III without any delay that can not be justified"* | "Without undue delay" is a requirement with no number attached. The register needs the elapsed time *and* a place for the justification, because an auditor will compute the former and ask for the latter. |
| **provenance block** | see §0.3 | `Product` | §0.3 | |
| `precedent_ids` | array of refs + similarity basis | `Product` | Workflow 4 | Workflow 4's output has to land somewhere citable. Also serves GHTF §6.1's "Previous investigations should be reviewed in order to determine if the event is a new problem or the recurrence of a previous problem where, for example, an ineffective solution was implemented." |
| `recurrence_of_capa_id` | ref, nullable | `Product` | GHTF §6.1 (above); Criticare (repeat deficiency from a 2017 warning letter) | A CAPA that is a recurrence of a closed CAPA is the single highest-value flag in the register. |
| `denominator_snapshot_ref` | ref | `Product` | Workflow 6; Hologic (occurrence rate computed over a mismatched period) | Any CAPA whose trigger was a rate needs the rate's inputs frozen. |
| `autonomy_level` | enum: `observe`, `recommend`, `draft`, `execute_with_approval` | `Product` | DIAGRAMS.md §colour rule and WORKFLOW.md §9; "Every agent output carries its autonomy level on its face" (§11.4) | |

#### `capa_action` (child)

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `action_type` | enum: `corrective`, `preventive` — **no `correction` value** | `Mandated` | ISO 9000:2015 §3.12.2 / §3.12.3; GHTF §2.1/§2.2 | The firewall from §2.1, implemented as an enum constraint. |
| `description` | text | `Mandated` | GHTF §6.3: *"a list of action items should be documented… A detailed description of the implementation"* | |
| `owner`, `due_date`, `completed_date` | | `Mandated` *as content* | GHTF §6.3: *"Roles and responsibilities for execution of action items"*, *"Implementation schedule, including timelines"*; Annex D "Planned actions — Specify: What the action is / Who will do it / When it should be done" | |
| `resources_required` | text | `Convention` | GHTF §6.3 ("Identification of the necessary resources (e.g. IT, infrastructure, work environment)") | |
| `regulatory_review` | text | `Mandated` *as content* | GHTF §6.3: *"Review regulatory requirements (e.g. submissions, licensing, certifications)"* | For Asteria this is the MDR significant-change question → register 4. |
| `verification_protocol_ref` + `acceptance_criteria` | | `Mandated` | GHTF §6.3: *"Verification and/or validation protocols of the action(s) with acceptance criteria"*; QSIT objective 8 | Per action, not per case: a four-action CAPA has four verifications. |
| `implementation_evidence_ref` | ref | `Mandated` | QSIT objective 9: verify CAPAs "were implemented and documented" — *"it may be necessary to view actual processes, equipment, facilities or documentation"*; GHTF §6.5 "Verify that the implementation has been completed." | |
| `extension_log[]` | array of `{old_due, new_due, reason, approved_by, at}` | `Convention` | MOCK-DATA.md: "Changed owners and due dates" | Overdue-action management is where real CAPA systems visibly fail; without the log the register shows only the final, always-on-time due date. |

### 2.5 Links out

| From → To | Direction | Note |
|---|---|---|
| CAPA → NC | many-to-many via `capa_input`; NC also carries `linked_capa_id` | Bidirectional on purpose. Trending needs NC→CAPA; investigation needs CAPA→NC. |
| CAPA → complaint | many-to-many via `capa_input` | ISO 13485 §8.5.2 reviews nonconformities **including complaints** — so a complaint can feed CAPA *without* an NC in between. This is the clearest argument that complaint and NC are siblings, not parent and child. |
| CAPA → audit finding | many-to-many via `capa_input`, and audit finding carries `capa_id` | §8.2.4 requires correction and corrective action without undue delay; MDSAP Task 10 confirms internal audit includes "corrections, corrective actions, follow-up activities, and the verification of corrective actions". |
| CAPA → change control | one-to-many, outward | The implementation evidence. §2.4 `implementation_change_control_ids`. |
| CAPA → risk file | outward | ISO 13485 §8.5.3 (risk-assessment methods); MDSAP Task 5 (risk acceptability). |
| CAPA → vigilance / field action | outward, nullable | Never decided in this register. |
| CAPA → management review | outward | QSIT objective 10; MDSAP Task 11. |
| CAPA → supplier/SCAR | outward | Out of scope here; GHTF's entire worked example is a supplier CAPA, so this link will matter more than its absence from this note suggests. |
| CAPA → CAPA | `recurrence_of_capa_id`, `merged_into`, `superseded_by` | GHTF §6.1; §6.6 re-initiation. |

### 2.6 Grain note on the negative decision

The brief asks where "CAPA evaluated and declined with rationale" lives. Two designs; I recommend the first:

1. **Same register, `decision = no_action`, status `evaluated_no_action`.** The CAPA register becomes the register of *CAPA decisions*, not of *open CAPAs*. Pros: MDSAP and QSIT both sample the declined population, so it needs to be queryable alongside the opened population with the same filters; the rationale, the risk-acceptability determination and the proportionality basis are the same fields in both branches; the ratio of opened to declined is itself the metric FDA's balance guidance points at ("too many… too few").
2. Separate `capa_evaluation` register feeding a narrower CAPA register. Pros: keeps "CAPA count" clean for management review. Cons: the declined population becomes second-class, which is precisely how it ends up undocumented.

**Consequence to state loudly:** under design 1, "number of open CAPAs" is a filtered count, not a row count, and any dashboard that says "CAPAs: 14" must say which filter. Given GHTF §7.2's warning that open/closed counts are not sufficient management-review input anyway, this is a feature.

### 2.7 The effectiveness-check problem

**The requirement.** ISO 13485 §8.5.2 requires reviewing the effectiveness of the corrective action taken. MDR Art. 10(9)(l) requires the QMS to address *"management of corrective and preventive actions and verification of their effectiveness."*

**The proof that criteria come first.** GHTF/SG3/N18 places the definition of effectiveness criteria at **§6.3 Identify Actions** — two steps *before* §6.5 Implement Actions. The documented action list must include *"Method or data for the determination of effectiveness with acceptance criteria"*, and Annex D expands that into four elements:

> *"Method or data for the determination of effectiveness with acceptance criteria. The improvement goal · The evidence (data sources) that will be used to support effectiveness (e.g., a data source could be where the problem was initially found) · The time frame that effectiveness will be monitored (e.g., upon completion of actions or three months, six months as appropriate) OR Sample size required to demonstrate effectiveness"*
> — [GHTF/SG3/N18:2010 Annex D](https://www.imdrf.org/sites/default/files/docs/ghtf/final/sg3/technical-docs/ghtf-sg3-n18-2010-qms-guidance-on-corrective-preventative-action-101104.pdf)

Annex A's ordered activity list settles the sequence beyond argument: *13. Identify actions → 14. Verify proposed actions before implementation → 15. Implement proposed actions → 16. Determine effectiveness of actions.*

**The fields that prove criteria were set before implementation, rather than written to match the outcome.** This is an *ordering* claim, so the proof is temporal and must be tamper-evident at the row level.

| Field | Type | Status | Source | Notes |
|---|---|---|---|---|
| `improvement_goal` | text | `Mandated` | GHTF Annex D ("The improvement goal") | |
| `acceptance_criteria` | structured: metric, operator, threshold, unit | `Mandated` | GHTF §6.3, Annex D ("with acceptance criteria") | **Structured, not free text.** Free text is what lets criteria be quietly reinterpreted. "Zero surface finish rejects at final inspection" is GHTF's own example and is expressible as metric/operator/threshold. |
| `evidence_sources[]` | array of data-source refs | `Mandated` | GHTF Annex D ("The evidence (data sources) that will be used… e.g., a data source could be where the problem was initially found") | Named **in advance**. Choosing the data source afterwards is the subtlest way to manufacture a pass. |
| `monitoring_window` | `{start_rule, duration}` e.g. `on_implementation_complete + 3 months` | `Mandated` | GHTF Annex D ("The time frame that effectiveness will be monitored") | A *rule*, not a date, because the start depends on implementation completing. |
| `sample_size_required` | integer, nullable | `Mandated` *alternative* | GHTF Annex D ("OR Sample size required to demonstrate effectiveness") | Either a window or a sample size. One of the two must be present — an XOR constraint, not two nullable columns. |
| **`criteria_locked_at`** | timestamp, immutable | `Product` | The ordering proof | Set when `status` enters `actions_defined`; **must precede** the earliest `capa_action.completed_date`. |
| **`criteria_locked_by`** | person ref | `Product` | Hard gate: the effectiveness verdict is human (WORKFLOW.md §9) | |
| **`criteria_hash`** | content hash of the structured criteria at lock time | `Product` | The ordering proof | Cheap, decisive, and checkable by an auditor who does not trust our audit log. The hash is what turns "we say we didn't change it" into "here is the hash, recompute it". |
| **`criteria_amendments[]`** | array of `{old_criteria, new_criteria, reason, approved_by, at, pre_or_post_implementation}` | `Product` | The ordering proof | Criteria legitimately change. The product's job is not to forbid it but to make the *timing* of each change visible. An amendment after `implementation_complete_at` is the exact pathology the brief is describing, and it should be impossible to hide. |
| `implementation_complete_at` | timestamp, derived from action rows | `Mandated` *as content* | GHTF §6.5 ("Verify that the implementation has been completed") | The pivot the whole comparison hangs on. |
| `check_due_at` | derived: `implementation_complete_at + monitoring_window.duration` | `Convention` | Ubiquitous | Derived, so it cannot be quietly deferred without an amendment row. |
| `check_performed_at`, `check_performed_by`, `check_data_ref`, `check_result` | | `Mandated` | ISO 13485 §8.5.2; MDR Art. 10(9)(l); QSIT objective 8 | `check_result ∈ {effective, not_effective, inconclusive}`. `inconclusive` must exist — see the MDSAP "left open" status in §3.3. |
| `verdict_rationale` | text | `Mandated` *as content* | GHTF §6.6's four review questions: *"Has the problem been comprehensively identified? Has the extent of the problem been identified (e.g. range of affected devices, patient outcome, process, production lines, operator)? Have the root cause/contributing factors of the problem been identified and addressed? Has the improvement action(s) been defined, planned, documented, verified and implemented?"* | Note question two: GHTF requires the **extent** question be re-asked at the effectiveness review. That means the effectiveness check must be able to reach back into `nc_affected_population`, and that a population expansion discovered *after* implementation should invalidate an effectiveness verdict. |
| `new_issues_introduced` | boolean + refs | `Mandated` | GHTF §6.6: *"If the manufacturer finds the actions create a new issue or a new nonconformity then the manufacturer needs to initiate Phase II"*; QSIT objective 8 (do not adversely affect the finished device) | |

**The integrity constraints, stated as rules rather than fields** — these are the actual deliverable of this subsection:

1. `criteria_locked_at` < `min(capa_action.completed_date)`. Violation ⇒ the criteria were not pre-set; flag it, do not block it, and record the violation as a property of the row.
2. `criteria_hash` at lock time must be reproducible from `acceptance_criteria` + `criteria_amendments` applied in order.
3. Any amendment with `at` > `implementation_complete_at` forces `criteria_amended_post_implementation = true` on the row, permanently, and that flag must appear on every export and every dashboard tile that counts the CAPA as effective.
4. `check_performed_at` ≥ `check_due_at` is fine; `check_performed_at` < `check_due_at` means the monitoring window did not complete, and a `effective` verdict on a truncated window is a finding.
5. Closure requires a terminal `check_result`. MDSAP's rule is unambiguous and we should adopt it verbatim as our own: *"any nonconformity for which the remediation action effectiveness has not been verified is an open nonconformity"* ([MDSAP Audit Report Form Guidelines, §14](https://www.fda.gov/media/117101/download)).

**What real templates do instead, and why this matters.** OpenRegulatory's free, widely used ISO 13485 CAPA SOP defines effectiveness only at step 5 — *"Verification and Check of Effectiveness… Effectiveness: Review of the effectiveness of actions taken"* — with **no criteria defined anywhere earlier in the process**, and its CAPA list has a single `Effectiveness Evaluation` column and no criteria column at all ([openregulatory/templates `sop-capa.md`, `list-capa.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/capa/sop-capa.md)). A company running that SOP literally cannot produce the evidence, because its register has nowhere to hold a pre-set criterion. And FDA has cited exactly this: Criticare's CAPAs were *"closed despite not having an adequate root cause investigation and **no effectiveness check plan**"* ([Criticare warning letter](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/criticare-technologies-inc-686915-07122024)).

**So the three-field gap between a compliant and a non-compliant CAPA register is: `acceptance_criteria` (structured), `criteria_locked_at`, and `monitoring_window`.** That is a small, demonstrable, defensible product claim.

### 2.8 Fields routinely incomplete or disagreed-on in reality

| Pathology | Evidence | What the register needs |
|---|---|---|
| **Root cause recorded as "operator error"** | GHTF §6.2 requires that *"causes are identified, not the symptoms"* and lists legitimate cause categories that reframe human error as system failure: *"Inadequate or non-existent procedures and documentation · Non-compliance with procedures · Inadequate process control · Lack of training · Inadequate working conditions · Inadequate resources"*. GHTF also gives the decisive test: *"A failure to act is only considered a cause if there was a pre-existing requirement to act."* Secondary: consultant consensus that *"'Human error' is not a root cause — it is a symptom"* ([MedDeviceGuide](https://meddeviceguide.com/blog/capa-medical-devices-guide)) — label as consultant opinion, not regulation | A `root_cause_category` from GHTF's list, which has no "operator error" value, forcing the author to pick a system cause. Plus `root_cause_is_symptom_check` as an agent-raised flag. Note GHTF's own worked example lands on *"inadequate line clearance procedures established at the supplier"* — a procedure cause reached through an operator event. |
| **Overdue effectiveness checks** | Criticare: CAPAs closed with no effectiveness check plan; CAPAs 1033 and 1059 opened in 2017/2018 still open at a 2024 inspection. Medline (2026): *"the firm did not escalate ineffective corrective actions despite complaint trending data exceeding established thresholds"* | `check_due_at` derived and non-editable; an `overdue_effectiveness` state distinct from `open`; and an escalation trigger on `threshold exceeded + no escalation`, which is literally what Medline was cited for. |
| **CAPA opened, never investigated** | Criticare: *"CAPA 1098 did not include any investigation and was still open at the time of the inspection"*; *"CAPA 1033 did not include any investigation and the investigation in CAPA 1059 was not completed"*; *"CAPA 1054 did not include any investigation"* — against backdrops of 21, 276 and 68 related complaints | An `investigation_started_at` that is separate from `date_created`, and aging on the gap. The mock data must include an Asteria CAPA open for 14 months with an empty `root_cause`. |
| **Severity-gated CAPA opening that suppresses real signals** | Hologic: the firm opened CAPAs only for "critical" or "catastrophic" severity, so a September 2023 complaint spike went unaddressed until May 2024 | Record the *gate* as well as the decision: `capa_threshold_rule_ref` + `rule_version`. Otherwise a declined CAPA looks like a judgement when it was a policy. |
| **Denominator and period mismatch in the trigger** | Hologic: occurrence rate computed from units sold 2016–2024 against complaints 2021–2024, contrary to the firm's own procedure | `denominator_snapshot_ref` with explicit numerator and denominator periods, and a validation that they match. |
| **Preventive action recorded as "N/A" everywhere, or invented to fill the box** | GHTF: *"By its very nature preventive action can not follow a nonconformity"*, and the guidance deliberately avoids "CAPA" to stop the assumption that every corrective action needs a preventive twin | Make `preventive_action: not_applicable` a first-class value with a rationale, and *never* require it on a corrective case. Also: a register where 100% of cases have a preventive action is as suspicious as one with none. |
| **Blank adverse-implications and verification cells** | OpenRegulatory's shipped example row leaves `Potentially Adverse Implications`, `Date of Verification` and `Date Closed` blank | Treat blank as a tracked state, not an empty string. |
| **Correction logged as corrective action** | WORKFLOW.md §10's named error; ISO 9000 §3.12.2/§3.12.3; GHTF §6.3's warning that procedure-change-plus-training "may not, by itself, be appropriate or sufficient" | The enum firewall in §2.1, plus a detector: a CAPA whose only actions are document revision + training, on a recurring input, is the signature of a correction wearing a CAPA's clothes. |

---

## 3. Audit findings register

### 3.1 Grain

**One row = one finding.** Defined as: *one nonconformity statement raised against one requirement, in one audit.* The audit is a separate parent row.

```text
audit_register     (one row per audit event: internal, NB, MDSAP, FDA, customer, supplier)
  └── audit_finding  (one row per finding, graded, against one clause)
        └── finding_response  one row per response cycle (plan, implementation, verification)
```

**Why not one row per audit?** Because the lifecycle belongs to the finding, not the audit. MDSAP's follow-up model tracks the *status of each nonconformity* across subsequent audits, with per-finding statuses and per-finding superseding references ([MDSAP Audit Report Form Guidelines, §14](https://www.fda.gov/media/117101/download)). A finding routinely outlives the audit that raised it by years.

**Why not one row per clause?** Because one finding can legitimately cite a primary clause plus related ones, and MDSAP's own form records a single `ISO 13485` clause per NC Ref ("The clause of ISO13485 against which the nonconformity is raised", §12). One primary clause per row, with an array of secondary clauses.

**Scope decision: internal and external findings in one register.** §8.2.4 covers internal audit only. But the response lifecycle, the CAPA linkage, and the overdue mechanics are identical for a notified-body NC, an MDSAP grade-4, an FDA 483 observation, a customer audit finding and a supplier audit finding — and the register's consumer (workflow 9, evidence bundle assembly) needs them together. Discriminate with `audit_type` and `issuing_body`, and accept that `grading_scheme` then has to be polymorphic (see §3.4).

### 3.2 Identity and numbering

- Internal: `IA-YYYY-##` for the audit, findings numbered within it (`IA-2025-03 / MNC-1`). OpenRegulatory's free audit report template numbers findings *within severity class* — separate `MNC No.`, `mNC No.` and `OFI No.` sequences, each starting at 1 ([openregulatory/templates `audit-report.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/internal-audit/audit-report.md)). So "finding 1" is ambiguous without the class. Reproduce that.
- External: the issuing body's own reference. MDSAP's guidance on what the reference must be is worth quoting because it tells you what a register must tolerate: *"This may be either the full nonconformity record identifier, or the order number of the nonconformity, or a combination of both. The nonconformity reference # should be unambiguous."* And for findings with no formal reference: *"create a reference using the Audit Report number + report page where the audit finding was described"* ([MDSAP AU G0019, §12 and §14](https://www.fda.gov/media/117101/download)).
- FDA 483: `OBSERVATION n` within a 483, which has no document number at all on its face — only firm name, FEI number and inspection dates ([FDA Form 483, SeaStar Medical, Feb 2025](https://www.fda.gov/media/188590/download)). So the register's external identity must be composite: `{issuing_body, audit_ref_or_fei, date_range, observation_number}`.
- **Findability requires:** clause, process audited, grade, status, due date, owner, linked CAPA, and the audit's parent reference.

### 3.3 Lifecycle / status values

Adopt MDSAP's status model, which is public, precise, and better than most commercial ones:

| State | Meaning | Source |
|---|---|---|
| `open` | Raised; remediation not yet effectiveness-verified | MDSAP §14: *"any nonconformity for which the remediation action effectiveness has not been verified is an open nonconformity"* ([MDSAP AU G0019](https://www.fda.gov/media/117101/download)) |
| `response_submitted` | Plan submitted to the issuing body, not yet accepted | Convention; NB practice |
| `response_accepted` | | Convention |
| `implemented_awaiting_effectiveness` | | GHTF §6.6 |
| **`left_open`** | *"the correction and corrective actions have been implemented as planned but the effectiveness of these actions could not be verified for a legitimate reason, provided no new occurrences of the same nonconformity have been experienced"* | MDSAP §14 — verbatim |
| `closed` | *"the effectiveness of the remediation plan was verified"* | MDSAP §14 |
| **`superseded_by_new_nc`** | *"Superseded by a new Nonconformity Report, in all other situations"*; and specifically where a manufacturer-identified NC was not recorded in the grading form and is still present at the next audit | MDSAP §14 |
| `rejected` / `disputed` | Finding contested | Convention. FDA's 483 form itself records the firm's stance — the SeaStar 483 carries an "Annotations to Observations" section reading *"Observation 1: Promised to correct"* ([FDA 483](https://www.fda.gov/media/188590/download)). That annotation is a real field we should model. |
| `withdrawn` | | Convention |

The `left_open` state is the important one. It is the honest middle ground between open and closed, it is defined by a regulator-hosted document, and almost no commercial register has it — which is why real registers show findings flipping to `closed` at the administrative deadline.

### 3.4 Audit findings register — field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `finding_id` | string, unique | `Convention` | [OpenRegulatory audit report](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/internal-audit/audit-report.md) (`MNC No.`, `mNC No.`, `OFI No.`) | |
| `external_ref` | composite, nullable | `Mandated` *for external* | MDSAP §12 ("should be unambiguous"), §14 (synthesise from report number + page) | |
| `audit_id` | ref to parent audit | `Mandated` *as content* | ISO 13485 §8.2.4 (records of audits and their results) | |
| `audit_type` | enum: `internal`, `notified_body`, `mdsap`, `fda_inspection`, `customer`, `supplier`, `unannounced` | `Convention` | MDSAP §14 names "next surveillance, recertification, special or unannounced audit"; MDSAP audit-type list includes Initial/Certification and Unannounced | |
| `issuing_body` | org ref | `Convention` | | |
| `requirement_cited` | `{standard, clause}` primary | `Mandated` | ISO 13485 §8.2.4 (audit criteria); MDSAP §12: *"ISO 13485 — The clause of ISO13485 against which the nonconformity is raised"* | |
| `secondary_clauses[]` | array | `Convention` | MDSAP NC Grading and Exchange Form exists precisely to *"assist the auditor to identify all regulatory requirements related to a particular audit task"* ([MDSAP AU G0019, preamble](https://www.fda.gov/media/117101/download)) | One finding, many jurisdictions' requirements — the reason MDSAP needs a separate form for it. |
| `jurisdictions_affected[]` | enum array: `us`, `eu`, `ca`, `au`, `br`, `jp` | `Convention` | MDSAP's five-country model; the Exchange Form's purpose is *"to provide detailed information to the Regulatory Authorities on the nonconformities in a standard and aggregate way"* | Relevant to Asteria: AU manufacturer, EU market (IE, NL). |
| `process_audited` | enum per MDSAP process model: `management`, `device_marketing_authorization`, `measurement_analysis_improvement`, `design_and_development`, `production_and_service_controls`, `purchasing` | `Convention` | MDSAP audit model process names, visible throughout [MDSAP AU G0019](https://www.fda.gov/media/117101/download) and [MDSAP MAI](https://www.fda.gov/media/147373/download) | Adopting MDSAP's process taxonomy makes findings comparable across internal and external audits. |
| `audit_task_ref` | string, nullable | `Convention` | MDSAP audit tasks are numbered (Task 1–15 in Measurement, Analysis and Improvement) | Lets an internal audit programme mirror the external one. |
| `statement_of_nonconformity` | long text | `Mandated` | ISO 13485 §8.2.4 (results recorded and reported); MDSAP §12 *"Statement of Nonconformity/Supporting Evidence"* | |
| `objective_evidence` | text + refs | `Mandated` | ISO 13485 §8.2.4; OpenRegulatory: *"Only verifiable information constituted audit evidence. Audit evidence leading to audit findings was recorded."* and an `Audit Proof` column | The FDA 483 pattern is the model: a one-line observation, then "Specifically," then named documents with revision and approval dates ([SeaStar 483](https://www.fda.gov/media/188590/download)). |
| `classification` | enum: `major`, `minor`, `observation`/`OFI` | `Convention` | **Not in ISO 13485.** OpenRegulatory's template defines the three classes and their meanings; [i3C Global](https://www.i3cglobal.com/iso-13485-internal-audit/) shows an Observation/Minor/Major/Satisfactory scheme without stating its source | Important not to mark this `Mandated`. ISO 13485 §8.2.4 requires results be recorded; the major/minor split is certification-body practice. |
| `grade` | integer 1–5 | `Convention` *external* | MDSAP nonconformity grading: a 4-point matrix over ISO 13485 clauses split into indirect QMS impact (clauses 4.1–6) and direct QMS impact (clauses 6.4–8.5), then **escalation rules adding +1 for absence of a documented process or procedure related to the nonconformity, and +1 for a nonconforming medical device released to market as a result**; grade ≥5 triggers intervention ([Qualio](https://www.qualio.com/blog/complete-guide-mdsaps-nonconformity-grading-system); [The FDA Group](https://www.thefdagroup.com/blog/a-quick-guide-to-mdsaps-new-nonconformity-grading-system)); form reference MDSAP AU F0019.2 per [MDSAP AU G0019 §12](https://www.fda.gov/media/117101/download) | **The escalation rules are the interesting part for us:** "nonconforming medical device released to market as a result" is the same fact workflow 5 computes. A grading input and an NC register field are the same data. |
| `grading_scheme` | enum: `mdsap_1_5`, `major_minor_ofi`, `fda_483_observation`, `custom` | `Product` | Polymorphic grading across audit types | Without this, `grade: 4` is meaningless. |
| `grade_inputs` | `{base_matrix_cell, escalations[]}` | `Convention` | MDSAP grading matrix + escalation rules (above) | Recording the derivation, not just the number, is what lets a grade be challenged. |
| `repeat_of_finding_id` | ref, nullable | `Mandated` *as content* | ISO 13485 §8.2.4 (audit programme takes account of results of previous audits); MDSAP §14 follow-up of past nonconformities; Criticare: *"a repeat deficiency from our 2017 Warning Letter"* | |
| `superseded_by_finding_id` | ref, nullable | `Convention` | MDSAP §14 "Superseded by a new Nonconformity Report" | |
| `status` | enum per §3.3 | `Convention` (`left_open` from MDSAP) | MDSAP §14 | |
| `status_rationale` | text | `Convention` | MDSAP §14: *"Additional Comments — May include a rationale for the status of past nonconformities."* | Mandatory in practice for `left_open`. |
| `response_due_date`, `response_submitted_at` | dates | `Convention` | NB/MDSAP practice | |
| `firm_annotation` | text, nullable | `Convention` | FDA 483 "Annotations to Observations" — e.g. *"Promised to correct"* ([SeaStar 483](https://www.fda.gov/media/188590/download)) | Real, tiny, and almost never modelled. |
| `correction[]` / `corrective_action_capa_id` | refs | `Mandated` | ISO 13485 §8.2.4 (correction and corrective action without undue delay); MDSAP Task 10: internal audits must include provisions for *"auditor independence over the areas being audited, corrections, corrective actions, follow-up activities, and the verification of corrective actions"* | Note §8.2.4 names **both** correction and corrective action — so the firewall from §2.1 applies here too: the correction is a finding-level field, the corrective action is a CAPA. |
| `without_undue_delay_basis` | text + elapsed | `Mandated` *as content* | ISO 13485 §8.2.4 | |
| `effectiveness_verified_at` / `verified_by` | | `Mandated` | MDSAP Task 10 ("the verification of corrective actions"); MDSAP §14 (closure = effectiveness verified) | Closure gate, as in §2.7 rule 5. |
| `owner` | person ref | `Convention` | | |
| **provenance block** | §0.3 | `Product` | | |
| `auditor` / `lead_auditor` | person refs | `Mandated` *as content* | ISO 13485 §8.2.4 (auditor selection for objectivity and impartiality; auditors shall not audit their own work) — paraphrased; corroborated by [i3C Global](https://www.i3cglobal.com/iso-13485-internal-audit/) and [SimplerQMS](https://simplerqms.com/iso-13485-audit/) | Lives on the audit row; duplicated onto the finding for independence checking. |
| `independence_assertion` | `{auditor, areas_audited, own_work_conflict: bool, basis}` | `Product` | ISO 13485 §8.2.4 independence requirement + MDSAP Task 10 | `Product` because the *assertion as a checkable field* is ours; the requirement is mandated. For a 12-person company like Asteria, independence is the constraint that actually bites — EMP-03 cannot audit her own investigations, and with three people in Quality the options run out fast. This field makes that visible. |

#### `audit_register` (parent) — abbreviated

Mandated or near-mandated content: `audit_criteria`, `scope`, `interval/date`, `methods`, `processes_and_areas_audited`, `conclusions`, `report_ref` (ISO 13485 §8.2.4 — audit criteria, scope, interval and methods shall be defined; records of audits and their results maintained; paraphrased, corroborated by [i3C Global](https://www.i3cglobal.com/iso-13485-internal-audit/) and [SimplerQMS](https://simplerqms.com/iso-13485-audit/)). Plus `audit_programme_ref` — and the programme itself is a real artefact with a real shape: OpenRegulatory's template is a clause-coverage matrix, one row per clause group and one column per planned audit, with `x` and `n/a` cells, noting that *"an audit program most commonly covers all ISO 13485 requirements in the course of three years at minimum"* ([openregulatory/templates `audit-program.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/internal-audit/audit-program.md)).

Convention fields worth carrying because MDSAP records them and they are genuinely diagnostic: `duration_planned` vs `duration_actual` in auditor-days, `significant_deviations_from_plan`, and **`obstacles`** — *"Record all situations encountered that have the potential to impact the validity of the audit conclusions. Such as, instances where the audited organization refused to provide auditor-requested information, or the audited organization refused to grant the auditor(s) access to premises"* ([MDSAP AU G0019 §13](https://www.fda.gov/media/117101/download)).

Also from MDSAP §9, two fields most registers lack: `exclusions` (ISO 13485 requirements excluded) and `non_applications` — with the rule that *"By definition, regulatory requirements may not be excluded."*

### 3.5 Links out

| From → To | Direction | Note |
|---|---|---|
| finding → CAPA | many-to-one | Outward. Audit findings are an explicit CAPA input ([OpenRegulatory SOP CAPA](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/capa/sop-capa.md)). |
| finding → NC | nullable, many-to-many | An audit can *discover* a product nonconformity. QSIT objective 2 lists quality audits as a CAPA data source; MDSAP MAI notes the audit team "may encounter data involving product nonconformities" during this process audit. |
| finding → change control | nullable | When the remediation is a documented process or document change. |
| finding → management review | outward, mandated-as-content | MDSAP Task 10 linkage: *"During the audit of the Management process, the audit team should confirm that the output of internal audits is an input to management review."* |
| finding → finding | `repeat_of`, `superseded_by` | MDSAP §14. |
| finding → audit programme clause coverage | outward | Drives next year's programme (§8.2.4 takes account of previous results). |

**A US-specific constraint the other register families must know about.** FDA investigators **do not** review internal audit results. QSIT states it as policy: *"In accordance with Agency policy (CPG 7151.02), do not request records regarding the results of internal quality audits, management reviews, third party audits (including ISO audits), or supplier audits. However, you will be reviewing raw data that is used by the firm when conducting their quality audits, management reviews, etc. … Information or data utilized in internal audits and management reviews are considered raw data and should be available for routine review."* ([FDA QSIT](https://www.fda.gov/files/Guide-to-Inspections-of-Quality-Systems.pdf))

Two product consequences, and they are not small:

1. **The audit findings register has a different audience from the other three.** It is for notified bodies, MDSAP auditing organisations and management — not FDA. Anything we build that auto-assembles an FDA evidence bundle (workflow 9) must be able to *exclude* internal audit results while *including* the raw data underlying them. A naive "show me the trail" that pulls internal audit conclusions into an FDA pack is actively harmful to the customer.
2. **Conversely, the raw data is fair game.** So the provenance chain from a finding back to the NC rows and complaint rows it was based on must be traversable in the direction "give me the raw data without the audit conclusion" — which is a real query, not a theoretical one.

### 3.6 Export shape and routinely-incomplete fields

**Export shape.** Internal: a DOCX or PDF audit report with numbered findings in per-severity tables, plus an XLSX findings log that is maintained separately and drifts from the report. External: the issuing body's PDF (MDSAP audit report package = audit report + NC Grading and Exchange Form + NC reports, per [MDSAP AU G0019 preamble](https://www.fda.gov/media/117101/download); FDA Form 483 as a signed PDF with an annotations page). Internal tracking: an XLSX "CAR log" with columns like `NC#`, `Clause`, `Maj/Min`, `Due`, `Closed`, `CAPA#`, `Comments`. MDSAP's own form guidance carries the footer *"Uncontrolled copy, when printed"* — which is itself a realism detail worth reproducing in Asteria's documents.

**Routinely incomplete or disagreed-on:** `objective_evidence` reduced to a document number with no revision; `classification` disputed between the auditor and the auditee (the firm argues minor, the NB says major) with no field to hold the disagreement; findings closed on `response_accepted` with `effectiveness_verified_at` empty — the exact pattern MDSAP's `left_open` state exists to prevent; `repeat_of_finding_id` left null because nobody searched; `independence_assertion` absent in small companies where it is most needed; and the audit programme's clause-coverage matrix showing `x` for a clause that the report never actually mentions.

---

## 4. Change control register

### 4.1 Grain

**One row = one change control record** (one change request, through to implementation closure). Two child tables:

```text
change_register
  ├── change_affected_item   one row per document, drawing, spec, software version, process, tool, supplier, labelling item
  └── change_impact          one row per impact assessment: risk, V&V, regulatory/significance, labelling, training, delivered product
```

**Why one row per change and not per affected document?** Because ISO 13485 §7.3.9 requires the change to be identified, reviewed, verified and validated as appropriate, and approved **before implementation** — one approval over a set of affected items. Splitting per document would multiply the approval. Paraphrased from §7.3.9; corroborated independently by [Starfish Medical](https://www.starfishmedical.com/resource/iso-134852016-section-7/) and [mdregulatory.com](https://mdregulatory.com/iso-13485-design-controls/) on the 7.3 subclause structure (7.3.8 design transfer, **7.3.9 design and development changes**, 7.3.10 design and development files).

**Product vs QMS changes: one register or two?** One register, `change_domain ∈ {product_design, software, labelling, process, supplier, document_only, organisational}`. The evidence for keeping them together is that real templates do — OpenRegulatory's change evaluation list runs product change requests (`#PCR01`) and organisational change requests (`#OCR1`) through two different question sets in **one document** ([openregulatory/templates `change-evaluation-list.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/techdoc/62304/change-evaluation-list.md)). The evidence against is that the template itself warns: *"You may want to separate your lists for product and organizational changes, as you should release a new list for every product version."* Flag as a genuine design fork; my recommendation is one register with a domain discriminator plus a per-product-version *view*, because CAPA implementation needs to point at both kinds from one field.

### 4.2 Identity and numbering

`ECR`/`ECO` (engineering change request/order), `CR-YYYY-###`, `DCR` (document change request), or the template's `#PCR01`/`#OCR1` ([OpenRegulatory](https://raw.githubusercontent.com/openregulatory/templates/master/templates/techdoc/62304/change-evaluation-list.md)). For Asteria, a firmware release (`PulseOne fw 2.4.1`) will be referenced as a version string in the product database and as a change number in the QMS, and nothing will join them — that is the realistic gap and exactly what workflow 1 is for.

Findability requires: affected product/model, affected document IDs and revisions, effective date, significance verdict, status, requester, approver, and the originating CAPA/NC/finding.

### 4.3 Lifecycle / status values

`requested` → `impact_assessment` → `significance_determined` → `approved` / **`rejected_with_rationale`** / `withdrawn` → `nb_notification_required` → `awaiting_nb_approval` → `implementation_in_progress` → `implemented` → `effectiveness/verification_complete` → `closed`. Plus `implemented_without_approval` as a detectable anti-state, and `superseded_by`.

The negative state that matters: **`rejected_with_rationale`**, and separately `assessed_not_significant` — because the *not significant* verdict is the one a notified body will ask to see the reasoning for, and it is a decision record in its own right. MDR Annex IX Chapter II §4.10 makes the stakes explicit: changes to the approved device require notified-body approval where they could affect the safety and performance of the device or the conditions prescribed for use; the NB assesses, notifies its decision, and where approved issues a supplement to the certificate.

### 4.4 Change control register — field table

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `change_id` | string, unique | `Convention` | OpenRegulatory `Change Request ID` | |
| `change_domain` | enum per §4.1 | `Convention` | OpenRegulatory PCR/OCR split | |
| `description` | text | `Mandated` *as content* | ISO 13485 §7.3.9 (changes identified); OpenRegulatory `Change Request Description` | |
| `reason_for_change` | enum: `capa_implementation`, `nc_remediation`, `audit_finding`, `design_improvement`, `supplier_change`, `regulatory`, `cost`, `obsolescence` + text | `Convention` | | The `capa_implementation` value is the join that makes register 2's `implementation_change_control_ids` meaningful. |
| `originating_record_ids` | array of refs (CAPA / NC / finding / complaint) | `Mandated` *as content* | WORKFLOW.md §7 step 5 ("Implement under change control"); MDSAP Task 7 links CAPA-driven process change to re-validation | |
| `affected_items[]` | child rows: `{item_type, item_id, from_revision, to_revision}` | `Mandated` | ISO 13485 §7.3.9 (review of changes includes the effect on constituent parts); §4.2.4 document control | `from_revision` is the field most logs omit and every reviewer wants. |
| `effect_on_product_already_delivered` | text + population refs | `Mandated` | ISO 13485 §7.3.9 explicitly requires the review of changes to include the effect on **product already delivered** — paraphrased; corroborated by [Starfish Medical](https://www.starfishmedical.com/resource/iso-134852016-section-7/) and [mdregulatory.com](https://mdregulatory.com/iso-13485-design-controls/) | **This is the same question as workflow 5's.** §7.3.9 and §8.3.3 converge on "what is already in the field and what does this mean for it". The change register should reuse `nc_affected_population`'s shape rather than inventing a second one. |
| `risk_management_impact` | `{risk_file_ref, inputs_changed, outputs_changed, new_hazards}` | `Mandated` | ISO 13485 §7.3.9 requires the review to cover the inputs and outputs of risk management — paraphrased; corroborated as above; MDR Art. 10(9)(e) (risk management per Annex I §3) | |
| `significance_determination` | enum: `significant`, `not_significant` + per-question answers + verdict | `Mandated` *EU* | ISO 13485 §7.3.9 (determine the significance of the change to function, performance, usability, safety and applicable regulatory requirements — paraphrased); MDR Annex IX Ch. II §4.10; MDCG 2020-3 | The real shape is a question battery, not a field. OpenRegulatory's list has 13 product questions and 6 organisational questions, each mapped to a named MDCG 2020-3 chart (A/B/C/D), with the rule that *"YES in the first two categories (intended use / essential requirements / GSPR) always leads to a significant change"* and a special rule that a change made to correct a safety-relevant error or as part of an FSCA must be discussed with the notified body — or treated as significant if no NB was involved. |
| `significance_answers[]` | child rows: `{question_id, chart_ref, answer, rationale}` | `Convention` | OpenRegulatory change evaluation list (question text and chart references above) | Store per-question with rationale. The template's own worked example shows why: an answer of *"No, but internal validation showed that performance on same metrics improved"* — a "No" that carries a caveat. A boolean column destroys that. |
| `nb_notification` | `{required, notified_at, decision, certificate_supplement_ref}` | `Mandated` *EU* | MDR Annex IX Ch. II §4.10 (NB approval required where the change could affect safety/performance or prescribed conditions of use; NB assesses, notifies its decision, issues a certificate supplement) | |
| `us_regulatory_impact` | `{new_510k_required: bool, basis}` | `Convention` | Out of the four clauses in scope; the determination is real and belongs here | Marked `Convention` deliberately — the governing FDA guidance on when a change requires a new 510(k) was not verified in this research. Do not mark it `Mandated` without that citation. |
| `verification_plan` / `verification_result` | refs + result | `Mandated` | ISO 13485 §7.3.9 (changes verified and validated as appropriate before implementation) | |
| `validation_required` / `revalidation_required` | boolean + ref | `Mandated` *as content* | ISO 13485 §7.3.9; MDSAP Task 7: *"reviewing the medical device organization's evaluation of the process change to determine if revalidation is needed"*, and for supplier-performed validated processes, *"confirm the results show the process meets the planned result"* ([MDSAP MAI](https://www.fda.gov/media/147373/download)) | For Asteria: a change to a PulsePatch adhesive coating process at the contract manufacturer. |
| `approved_by` / `approved_at` | person ref + timestamp | `Mandated` | ISO 13485 §7.3.9 (approved before implementation); §4.2.4 (document approval) — and WORKFLOW.md §9 lists controlled-document approval as a hard human gate | |
| `implementation_date` / `effective_date` | dates | `Mandated` *as content* | ISO 13485 §7.3.9 (before implementation implies a recorded implementation point) | Keep both: the approval date and the effective date differ, and the gap is where unapproved-in-practice changes hide. |
| `training_required` / `training_ids` | boolean + refs | `Convention` | MOCK-DATA.md ("Document releases cause training assignments"); GHTF §6.5 | |
| `labelling_impact` | boolean + refs | `Mandated` *as content* | 21 CFR §820.45 (control of device labeling and packaging — one of the six surviving QMSR sections); MDCG 2020-3 labelling examples in the OpenRegulatory list | Worth noting that §820.45 survived the QMSR cut, which means FDA considered labelling control *not* adequately covered by ISO 13485. |
| `design_file_updated` | boolean + ref | `Mandated` *as content* | ISO 13485 §7.3.10 design and development files; §7.3.9 records of changes | |
| `status`, `closed_at` | enum per §4.3 | `Convention` | | |
| **provenance block** | §0.3 | `Product` | | |
| `post_implementation_monitoring` | `{metric, window, result}` | `Product` | Workflow 6; closes the loop with register 2's effectiveness check | A change made to implement a CAPA and the CAPA's effectiveness check are monitoring the same thing. Link them rather than duplicating. |

### 4.5 Links out

| From → To | Direction | Note |
|---|---|---|
| change → CAPA | many-to-one, inward-originated | CAPA is upstream when `reason_for_change = capa_implementation`. The CAPA's `implementation_change_control_ids` is the mirror. |
| change → NC | both directions, qualified | `caused_by` (the change broke something) and `remediated_by`. The `caused_by` direction is the one nobody builds and the one that matters: GHTF lists "Change analysis" as a root-cause technique (§6.2), which is only possible if changes are queryable by date against NC detection dates. |
| change → audit finding | many-to-one | When remediation is a process or document change. |
| change → document register / training | outward | Out of scope here. |
| change → risk file | outward, mandated-as-content | §7.3.9's risk-management review. |
| change → notified body / certificate | outward | MDR Annex IX §4.10. |
| change → delivered population | outward | §7.3.9's "product already delivered" — shares shape with `nc_affected_population`. |
| change → change | `superseded_by`, `depends_on` | Firmware chains. |

### 4.6 Export shape and routinely-incomplete fields

**Export shape.** An ECR/ECO PDF with an approval block and wet-or-electronic signatures; an XLSX change log with one row per change and a wide block of `Y/N` impact columns; the significance evaluation as a **transposed** table — OpenRegulatory's change evaluation list puts *questions as rows and change requests as columns*, which means the export is a matrix that no naive CSV reader will parse into records. Reproduce that: it is a genuine and common ingestion hazard.

**Routinely incomplete or disagreed-on:** `effect_on_product_already_delivered` left blank on "minor" changes; `from_revision` omitted; `significance_determination` recorded as a bare verdict with the question battery filled in afterwards (the same temporal pathology as §2.7, and it needs the same `determined_at` discipline); `nb_notification.required = false` with no rationale; `implementation_date` earlier than `approved_at`; and software changes that exist as a version string in the product database with no change record at all — which for a firmware-bearing product like PulseOne is the single most likely §7.3.9 finding in Asteria's history.

---

## 5. What the other register families need to agree with us on

1. **The provenance block in §0.3 is shared, not per-register.** If the complaint register invents a different provenance shape, workflow 9 cannot walk a chain across registers and the whole evidence-bundle claim collapses.
2. **`nc_affected_population` is a shared shape, used by at least three registers.** NC (§8.3.2/§8.3.3), change control (§7.3.9 "product already delivered"), and trending (workflow 6's denominators). One table or one reusable type — not three.
3. **The correction firewall is a cross-register constraint.** Corrections live on NC rows and audit-finding rows. Corrective actions live in the CAPA register. §8.2.4 names both for audit findings, so the findings register needs a correction field too, and it must not be a CAPA.
4. **`awareness_timestamp` belongs to the event, not the register row.** The vigilance clock starts on awareness; if the complaint register and the NC register each compute awareness independently, they will disagree, and the disagreement will be on the record. One event-level awareness fact, referenced by both.
5. **Negative decisions need a home in every register, and they must be queryable alongside positive ones.** No CAPA (MDSAP Task 5). No advisory notice (MDSAP Task 15). No investigation (FDA-era §820.90(a); ISO 13485 §8.2.2 for complaints). Not significant (MDR Annex IX §4.10). Same pattern four times: `decision` + `rationale` + `decided_by` + `decided_at` + `risk_basis`. Standardise it once.
6. **Closure is gated on effectiveness verification, everywhere.** MDSAP's rule — unverified effectiveness means the nonconformity is open — should be the platform's rule, not one register's.
7. **Identifiers: every register row needs composite external identity**, because external bodies number things badly or not at all (MDSAP's "synthesise from report number + page"; FDA 483's bare `OBSERVATION 1`). Do not assume a single opaque string.
8. **Clause-reference columns must be version-aware.** The QMSR transition means the same requirement is cited as `820.90` before February 2026 and `ISO 13485 8.3.2` after. Store `{framework, version, clause}`, not a string.

---

## Citations

Primary sources verified September 2026. Where a source is a vendor, consultant, or free-template publisher, it is labelled as such and is used only to support `Convention`.

**Standards (clause numbers stated; requirement content paraphrased — ISO 13485:2016 and ISO 9000:2015 are copyrighted)**

- §8.3.1–§8.3.4 subclause structure, concession records and identity of authoriser, rework re-verification and adverse-effect determination — [qmsWrapper lesson 18](https://qmswrapper.com/control-of-nonconforming-products-in-iso-13485-lesson-18/), [i3C Global — rework](https://www.i3cglobal.com/iso-13485-rework/), [Advisera — post-delivery actions](https://advisera.com/13485academy/blog/2017/04/11/iso-134852016-nonconforming-product-how-to-approach-the-post-delivery-actions/) *(all consultant sources)*
- §8.5.2 / §8.5.3 documented-procedure content and records — [13485quality.com — 8.5.2](http://13485quality.com/iso-13485-standard2016-8-5-2-corrective-action/), [i3C Global — CAPA](https://www.i3cglobal.com/iso-13485-corrective-and-preventive-action/), [Registrar Corp — measurement, analysis and improvement](https://www.registrarcorp.com/blog/medical-devices/iso-13485/measurement-analysis-improvement-in-medical-devices/) *(consultant sources)*
- §8.2.4 internal audit: criteria, scope, interval, methods, auditor independence, correction and corrective action without undue delay, records — [i3C Global — internal audit](https://www.i3cglobal.com/iso-13485-internal-audit/), [SimplerQMS — ISO 13485 audits](https://simplerqms.com/iso-13485-audit/) *(consultant sources)*
- §7.3.8 / §7.3.9 / §7.3.10 subclause numbering and titles; §7.3.9 significance determination, effect on constituent parts and product already delivered, risk-management inputs and outputs, records — [Starfish Medical](https://www.starfishmedical.com/resource/iso-134852016-section-7/), [mdregulatory.com — design controls](https://mdregulatory.com/iso-13485-design-controls/), [Ideagen](https://www.ideagen.com/thought-leadership/blog/iso-134852016-73-medical-device-design-controls-and-why-they-re-important) *(consultant sources; numbering corroborated across all three)*
- ISO 9000 §3.12.2 correction / §3.12.3 corrective action — restated with the explicit distinction note in [GHTF/SG3/N18:2010 §2.1–2.2](https://www.imdrf.org/sites/default/files/docs/ghtf/final/sg3/technical-docs/ghtf-sg3-n18-2010-qms-guidance-on-corrective-preventative-action-101104.pdf) *(GHTF cites the ISO 9000:2005 numbering 3.6.6 / 3.6.5; see Confidence notes)*

**International guidance (public, quotable)**

- GHTF/SG3/N18:2010 *Quality management system — Medical Devices — Guidance on corrective action and preventive action and related QMS processes*, 4 November 2010 — [IMDRF PDF](https://www.imdrf.org/sites/default/files/docs/ghtf/final/sg3/technical-docs/ghtf-sg3-n18-2010-qms-guidance-on-corrective-preventative-action-101104.pdf). Used for: data sources and escalation criteria (§4.1–4.2), the four documented outcomes including no-action-with-monitoring and concession (§6.3), investigation plan elements (§6.1), root-cause tools and cause categories (§6.2), verify-before-implement (§6.4), effectiveness criteria set at action-definition time (§6.3 and Annex D), the four effectiveness-criteria elements (Annex D), the effectiveness review questions including extent (§6.6), and management-review sufficiency (§7.2).
- MDSAP *Measurement, Analysis and Improvement Process* (FDA-hosted) — [fda.gov/media/147373](https://www.fda.gov/media/147373/download). Tasks 1–15, including Task 5 (decision not to take corrective action must be risk-based), Task 8 (disposition made, justified, documented; external party notified; concession risk-based), Task 9 (post-delivery nonconforming product), Task 10 (internal audit independence and verification of corrective actions), Task 11 (management review input), Task 15 (advisory-notice decisions including decisions not to issue; scope of the quality issue).
- MDSAP AU G0019.3.006 *Medical Device Regulatory Audit Report Form Guidelines* (FDA-hosted) — [fda.gov/media/117101](https://www.fda.gov/media/117101/download). Audit report package composition; §9 exclusions and non-applications; §12 NC Ref #, statement of nonconformity, ISO 13485 clause, grade; §13 duration planned vs actual, significant deviations, obstacles; §14 follow-up of past nonconformities, the Closed / Left open / Superseded status set, and the rule that unverified effectiveness means the nonconformity is open.
- MDSAP nonconformity grading matrix (indirect vs direct QMS impact; escalation rules for absence of a documented process and for release of a nonconforming device; grade ≥5 triggers intervention) — [Qualio](https://www.qualio.com/blog/complete-guide-mdsaps-nonconformity-grading-system), [The FDA Group](https://www.thefdagroup.com/blog/a-quick-guide-to-mdsaps-new-nonconformity-grading-system) *(vendor/consultant sources describing a public MDSAP scheme)*

**United States**

- 21 CFR §820.35 Control of records, current QMSR text, including (a) complaint record content, (b) servicing records, (c) UDI recorded for each device or batch — [Cornell LII](https://www.law.cornell.edu/cfr/text/21/820.35)
- 21 CFR Part 820 current structure: Subpart A §§820.1–820.10, Subpart B §§820.20–820.45, Subparts C–O reserved — [Cornell LII, Part 820](https://www.law.cornell.edu/cfr/text/21/part-820); surviving-section list corroborated by [Greenlight Guru](https://www.greenlight.guru/blog/qmsr-your-guide-to-part-820) *(vendor)*
- FDA CDRH, *Nonconforming Product* (Vidya Gopal, DICE) — [printable slides PDF](https://www.fda.gov/files/about%20fda/published/Nonconforming-Product---Printable-Slides.pdf). Quotes of repealed 21 CFR §820.90(a) and (b)(1)–(b)(2); §820.3(q) nonconformity, (r) product, (y) specification; the five named dispositions; MRB/MRC as industry practice; QSR preamble comment #156 on concessions; the handle-under-820.90 vs refer-to-CAPA criteria and the "balance is key" framing; the "returned product handled within the complaint system" routing.
- FDA, *Guide to Inspections of Quality Systems* (QSIT) — [fda.gov PDF](https://www.fda.gov/files/Guide-to-Inspections-of-Quality-Systems.pdf). CAPA subsystem objectives 1–10 verbatim, including objective 5 ("The full extent of a problem must be captured before…"), objective 6 (commensurate with risk; review records where the firm concluded no action was necessary; concessions not solely to fulfil marketing needs), objective 8 ("effective and verified or validated prior to implementation"), objective 10 (dissemination), and the CPG 7151.02 policy on not requesting internal audit results.
- FDA warning letter, Criticare Technologies, Inc., 12 July 2024 — [FDA](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/criticare-technologies-inc-686915-07122024). CAPAs open for years with no investigation; CAPAs "closed despite not having an adequate root cause investigation and no effectiveness check plan"; six of six nonconformance reports with no documented investigation or disposition; repeat deficiency from a 2017 letter.
- FDA warning letter, Hologic, Inc., 18 December 2024 — [FDA](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/hologic-inc-698214-12182024). Severity-gated CAPA opening delaying action on a complaint spike; occurrence rate computed over a mismatched period (units sold 2016–2024 vs complaints 2021–2024).
- FDA warning letter, Medline Industries, LP, 25 March 2026 — [FDA](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/medline-industries-lp-723866-03252026). Cites 21 CFR 820.100(a), 820.70(g)(1), 820.30(f) for a December 2025 inspection; failure to escalate ineffective corrective actions despite trending data exceeding thresholds.
- FDA Form 483, SeaStar Medical, Inc., 25–27 February 2025 — [fda.gov/media/188590](https://www.fda.gov/media/188590/download). Real 483 form structure: observation text, "Specifically," narrative naming the procedure and its approval date, FEI number, investigator signatures, and an "Annotations to Observations" page.

**European Union**

- MDR 2017/745 Art. 10(9), full lettered list, including (a) strategy for regulatory compliance including procedures for management of modifications to devices, (e) risk management, (i) PMS per Art. 83, (k) serious incident and FSCA reporting, (l) *"management of corrective and preventive actions and verification of their effectiveness"*, (m) monitoring and measurement of output, data analysis and product improvement — [EUR-Lex CELEX:32017R0745](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32017R0745)
- MDR Art. 10(12), corrective action / withdrawal / recall on a device not in conformity, and informing distributors, authorised representative and importers — [Medical Device HQ, Art. 10](https://medicaldevicehq.com/documentation/mdr-article-10-general-obligations-of-manufacturers/), [Medical Device Regulation, Art. 10](https://www.medical-device-regulation.eu/mdr-article-10-general-obligations-of-manufacturers/)
- MDR Annex IX Chapter II §4.10, changes to the approved device requiring notified-body approval and a certificate supplement — [TÜV SÜD, Annex IX](https://de-mdr-ivdr.tuvsud.com/Annex-IX-Conformity-assessment.html), [Johner Institute, design change](https://blog.johner-institute.com/regulatory-affairs/design-change/) *(paraphrase; see Confidence notes)*
- MDCG 2020-3 significant-change charts A–D, as operationalised in a published template — [openregulatory/templates `change-evaluation-list.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/techdoc/62304/change-evaluation-list.md)

**Templates, registers and vendor sources (used only for `Convention`)**

- OpenRegulatory free ISO 13485 templates, GitHub source of truth — [openregulatory/templates](https://github.com/openregulatory/templates): [`list-capa.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/capa/list-capa.md) (13 column headers verbatim), [`sop-capa.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/capa/sop-capa.md) (process steps; inputs; Five Whys; effectiveness defined only at closure), [`audit-report.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/internal-audit/audit-report.md) (MNC/mNC/OFI definitions and per-class numbering; Audit Proof column), [`audit-program.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/qms/internal-audit/audit-program.md) (three-year clause-coverage matrix), [`change-evaluation-list.md`](https://raw.githubusercontent.com/openregulatory/templates/master/templates/techdoc/62304/change-evaluation-list.md) (PCR/OCR question batteries, transposed layout)
- [NominalQC NCR log template](https://www.nominalqc.com/templates/ncr-log-template) — column set, CONFIG-sheet dropdowns, Days Open, OVERDUE flag, estimated cost KPI, separate printable NCR form
- [SimplerQMS — Nonconformance Report](https://simplerqms.com/non-conformance-report/) — 13 named fields including "Bracketing Assessment"; Critical/Major/Minor severity; Quality Manager approves dispositions
- [1factory — NCR, CAPA, SCAR, Complaint, Audit Findings](https://www.1factory.com/ncr-capa-scar-complaint.html) — separate-but-linked record types; Pareto by Part Number, Customer, Supplier, Defect Code, Root Cause
- [Cognidox — guide to non-conformance reports](https://www.cognidox.com/blog/a-guide-to-non-conformance-reports) — "whether it is of internal origin or a customer complaint"; not every NCR warrants a CAPA
- [Rimsys — nonconformance reporting](https://www.rimsys.io/blog/nonconformance-reporting-medical-device-manufacturers) — eQMS auto-linking of nonconformances to complaints, CAPAs, audits and change controls
- [Greenlight Guru — nonconformance vs CAPA](https://www.greenlight.guru/blog/nonconformance-capa-processes) — isolated vs systemic; warning against being "CAPA happy"
- [MedDeviceGuide — CAPA guide](https://meddeviceguide.com/blog/capa-medical-devices-guide) — "'Human error' is not a root cause — it is a symptom" *(consultant opinion, not regulation)*

### Confidence notes

**High confidence — quoted from primary or regulator-hosted sources**

- All CFR text quoted here, current (§820.35, Part 820 structure) and repealed (§820.90(a), (b)(1), (b)(2); §820.3(q), (r), (y)), and the QSR preamble comment #156 language on concessions — quoted from Cornell LII and from FDA's own published slide deck.
- All FDA QSIT text — extracted directly from the FDA-hosted PDF, including CAPA objectives 1–10 and the CPG 7151.02 internal-audit policy note.
- All GHTF/SG3/N18:2010 text, including the Annex D effectiveness-criteria elements and the Annex A activity ordering — extracted directly from the IMDRF-hosted PDF.
- All MDSAP text — extracted directly from the two FDA-hosted PDFs (Measurement Analysis and Improvement task descriptions; AU G0019 audit report form guidelines including the Closed / Left open / Superseded status set and the unverified-effectiveness rule).
- MDR Art. 10(9)(a)–(m) — quoted from EUR-Lex.
- The three FDA warning letters and the SeaStar Form 483 — quoted from FDA-hosted pages and PDF.
- Part 820's surviving six sections and the 2 February 2026 effective date — corroborated across Cornell LII and two independent commentaries.
- Medline (March 2026) still citing 21 CFR 820.100(a) for a December 2025 inspection — read directly from the letter.

**Paraphrased, not verified verbatim**

- Every ISO 13485:2016 and ISO 9000:2015 requirement in this note. The standards are paywalled. Clause *numbers and titles* were corroborated across at least two independent sources in every case (§8.3.1–§8.3.4, §8.2.4, §8.5.2–§8.5.3, §7.3.8–§7.3.10). Clause *content* is paraphrase and, in several places, paraphrase of a consultant's paraphrase. Before any of this appears in a customer-facing compliance claim it must be checked against a purchased copy. Specifically unverified against the standard text: whether §8.3.1 or §8.3.2 is the clause that carries the concession-record-and-authoriser requirement (sources split — see below); the exact lettered structure of §8.5.2; and whether §7.3.9's "product already delivered" wording is as broad as I have treated it.
- MDR Annex IX Chapter II §4.10 — paraphrased from TÜV SÜD and Johner Institute rather than quoted from EUR-Lex. The substance (NB approval for changes affecting safety, performance or prescribed conditions of use; certificate supplement) is consistent across both, but this is the one MDR provision in this note I did not read in the regulation itself.
- MDSAP grading matrix mechanics (clause ranges 4.1–6 "indirect" and 6.4–8.5 "direct", 4-point base matrix, +1 escalations, grade ≥5 threshold) — taken from two vendor summaries, not from MDSAP AU F0019.2 itself. Note the clause ranges as reported **overlap** at clause 6–6.4, which is probably a reporting artefact in the secondary sources rather than the scheme's actual design. Treat the grading *fields* as solid and the *matrix boundaries* as unverified.
- `us_regulatory_impact` in the change control register is marked `Convention` specifically because I did not verify the FDA guidance on when a device modification requires a new 510(k). Do not promote it.

**Corrected or sharpened during research**

- **The QMSR citation trap.** I initially assumed a 2026 register would cite ISO 13485 clauses. The most recent warning letter in the corpus (Medline, 25 March 2026) cites `21 CFR 820.100(a)`, because inspections are cited against the regulation in force at the time of inspection. Registers and findings spanning early 2026 will therefore carry *both* citation styles, and our clause-reference storage must be `{framework, version, clause}` rather than a string. This changed a cross-register recommendation (§5.8).
- **A genuine internal contradiction in FDA's own material on returned product.** §820.3(r) defines "product" to include returned devices, putting them squarely in nonconforming-product scope; FDA's nonconforming-product training deck routes returned defective product to the complaint system instead. Both are FDA. I have not resolved it and have flagged it as a real disagreement rather than picking a side (§1.6).
- **Which subclause carries the concession record requirement.** Two sources place it differently — [qmsWrapper](https://qmswrapper.com/control-of-nonconforming-products-in-iso-13485-lesson-18/) attributes the "record the concession and who authorised it" content to §8.3.3 and the disposition options to §8.3.2, which contradicts the more common reading that §8.3.2 (pre-delivery) carries both, with §8.3.3 covering post-delivery actions and advisory notices. I have followed the common reading (concession records in §8.3.2), and flag it as unverified against the standard. The *content* is not in dispute; only which subclause number to cite.
- **"MRB" is not a requirement.** I expected to find Material Review Board mandated somewhere. It is not. FDA explicitly frames MRB/MRC as an *industry practice example* ("One practice is through…"); what is mandated is defined responsibility for review and defined authority for disposition. I demoted the MRB field from `Mandated` to `Convention` and added `authority_basis` as a `Product` field to carry the part that actually matters.
- **GHTF cites the ISO 9000:2005 numbering, not 2015.** GHTF/SG3/N18 references correction at 3.6.6 and corrective action at 3.6.5 (ISO 9000:2005), whereas WORKFLOW.md §7 correctly uses the ISO 9000:2015 numbering 3.12.2 and 3.12.3. Both are right for their respective editions. Anyone cross-reading the two documents will think one of them is wrong; it is worth a footnote wherever we cite both. WORKFLOW.md's own Confidence note already flags that 3.12.2/3.12.3 are commonly stated in reverse — that remains correct.
- **The effectiveness-criteria-before-implementation requirement is better sourced than expected.** I expected to have to argue it from inference. GHTF Annex D states it outright ("Method or data for the determination of effectiveness with acceptance criteria") at the action-definition step, and Annex A fixes the ordering. That upgraded several `acceptance_criteria` sub-fields from `Convention` to `Mandated`, and it means the three-field gap in §2.7 is a defensible claim rather than a design preference.
- **WORKFLOW.md §1.1 needs a one-sentence softening, not a retraction.** See §1.6 for the proposed wording. The two-register position is the better design and is well supported by the separation of MDSAP audit tasks and of §820.35(a) record content; it is "never one merged record" that overstates, because a material slice of industry does run one NC per complaint with an origin field.

**Not covered here, deliberately**

Supplier corrective action (SCAR), risk register rows, document and training registers, management review register, PMS/PSUR register, the complaint register itself, §820.35(b) servicing records, IVDR, Health Canada, TGA and PMDA specifics beyond their presence in the MDSAP model, and FDA's when-to-submit-a-new-510(k) guidance.
