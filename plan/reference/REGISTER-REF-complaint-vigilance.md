# Register Shape Reference — Complaint Register and Vigilance / Regulatory Reporting Register

**Purpose.** The citation-backed, field-level shape of the two registers that carry the post-market core of the product. Companion to [`WORKFLOW.md`](../WORKFLOW.md) (the domain reference) and [`DIAGRAMS.md`](../DIAGRAMS.md) (the nine agent workflows that read and write these registers). This is a research note, not a schema — but it is intended to be precise enough that a schema can be written from it without further research.

**Scope.** Two registers:

1. **Complaint register** — ISO 13485:2016 §8.2.2 Complaint handling, with US record content mandated by 21 CFR §820.35(a) under the QMSR effective 2 February 2026, sitting on §4.2.5 Control of records.
2. **Vigilance / regulatory reporting register** — ISO 13485:2016 §8.2.3 Reporting to regulatory authorities; US 21 CFR Part 803 (§803.50 / §803.52 / §803.53 / §803.56 / §803.18) and the eMDR / Form FDA 3500A data elements; EU MDR 2017/745 Art. 87 and the MDCG **MIR v7.3.1** form fields; Art. 88 trend reports as entries.

**Standing caveat.** ISO 13485:2016 and ISO 9000:2015 are copyrighted standards. Clause numbers and titles are stated here; requirement content is paraphrased, never reproduced. Anyone implementing against this must read the actual standard. CFR, EU MDR, MDCG guidance, FDA guidance and FDA compliance-program text is public and is quoted directly.

One useful consequence of the QMSR: **21 CFR Part 820 now quotes ISO 13485 clause numbers and titles in public-domain regulatory text.** §820.35 names "Clause 4.2.5 in ISO 13485 … Control of Records", "Clause 8.2.2 in ISO 13485, Complaint Handling", and "Clause 7.5.4 in ISO 13485, Servicing Activities"; §820.10(b)(3) names "Clause 8.2.3 in ISO 13485, Reporting to regulatory authorities". Those clause numbers and titles are therefore verified against a primary public source, not only against consultants.

### How to read `Status`

| Status | Means |
|---|---|
| `Mandated` | A named regulation or standard clause requires this content. The clause is cited on the row. |
| `Convention` | Not mandated, but present in essentially every real register, commercial eQMS, or inspection-ready template. At least one real template, vendor, consultant or official-guidance source is cited, and labelled as such. |
| `Product` | Our own addition, required by a numbered workflow in `DIAGRAMS.md`. The workflow number is on the row. |

Where a field is mandated in one jurisdiction only, the row says which. Where sources genuinely disagree, the row says so and §5 collects the disagreements.

Counts, after removing the clock fields that deliberately appear in two tables:

| Register | `Mandated` | `Convention` | `Product` | Total |
|---|---:|---:|---:|---:|
| A — Complaint (§2.3, §2.6) | 20 | 25 | 15 | 60 |
| B — Vigilance (§3.3, §3.6.4) | 78 | 6 | 20 | 104 |

The asymmetry is the finding, not an artefact. The complaint register is *mostly convention*: ISO 13485 §8.2.2 describes a process and §820.35(a) mandates seven fields, so almost everything else is practice. The vigilance register is *mostly mandated*, because two regulators publish the form field-by-field — §803.52 enumerates the Form FDA 3500A blocks and the MIR v7.3.1 helptext enumerates roughly 150 labelled fields with their XML element names. **So the vigilance register is not where we get to design; it is where we get to be correct.** Our differentiation there is concentrated in 20 `Product` fields, and most of those exist to make the clock defensible.

---

## 1. What changed in 2026, and why it matters to these two registers

Four currency facts that move the shape of both registers, all verified:

1. **QMSR effective 2 February 2026.** 21 CFR Part 820 incorporates ISO 13485:2016 by reference. The old §820.198 "Complaint files" section is gone; complaint-handling requirements now come from ISO 13485 §8.2.2, and the US-specific *record content* lives in §820.35(a). ([FDA QMSR](https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr); [eCFR §820.35](https://www.ecfr.gov/current/title-21/part-820/section-820.35))
2. **QSIT is retired.** On 2 February 2026 FDA stopped using the Quality System Inspection Technique and moved to **Compliance Program 7382.850**, *Inspection of Medical Device Manufacturers*. CP 7382.850 treats **Complaint Handling** as an element of the *Measurement, Analysis, and Improvement* QMS area (mapped to "21 CFR 820.10(b)(3)(4), 21 CFR 820.35, and Clauses 8.2.2, 8.2.3") while **Medical Device Reporting** and **Reports of Corrections and Removals** are separate *Other Applicable FDA Requirements* (OAFRs). FDA's own inspection structure therefore treats these as two registers with a named hand-off — not one pipeline. ([CP 7382.850](https://www.fda.gov/media/80195/download))
3. **MIR v7.3.1 is mandatory from 1 May 2026.** The EU Manufacturer Incident Report form changed version, and the new version adds the second awareness date (field 1.2.d) that the whole clock design turns on. ([EC PMSV reporting forms](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance/pmsv-reporting-forms_en); [MIR v7.3.1 helptext](https://health.ec.europa.eu/document/download/dc6acc1b-f1ae-4512-b838-2fae869124c3_en?filename=md_new-reg_mir-help-v7.3.1_en.pdf))
4. **Eudamed's vigilance module is still not live.** Four Eudamed modules became mandatory 28 May 2026; the **Post-market surveillance and Vigilance (VGL) module** was not among them, is not available for voluntary use, and until it is declared functional manufacturers "must continue to use the national reporting processes as explained in MDCG 2021-1 Rev. 1 and MDCG 2022-12". So in 2026 a European vigilance register row carries a *national* submission channel and an **empty Eudamed reference number**, and open reports will later migrate mid-life into Eudamed. ([MDCG 2023-3 Rev.2 Q21](https://health.ec.europa.eu/document/download/af1433fd-ed64-4c53-abc7-612a7f16f976_en?filename=mdcg_2023-3_en.pdf); [EC Eudamed roll-out Q&A Q12–Q13](https://health.ec.europa.eu/document/download/0e7327c7-0e06-4fbd-90d3-8ab7bb30fe9f_en?filename=eudamed-qa_en.pdf))

Fact 4 is a gift for mock-data realism: two identifier columns that are *supposed* to be populated and in reality are blank or say `Unknown`.

---

## 2. Register A — Complaint register

### 2.1 Grain

**One row = one complaint record = one alleged deficiency, about one device (model, and where known one unit/lot), reported by one complainant, received once.**

This is genuinely contested in practice, and the contest is worth stating precisely.

**What pushes toward a coarser grain (one row per communication):** §820.35(a) requires "The name of the device" (singular) and "The date the complaint was received" (singular). A single phone call is a single receipt. Support tickets, which are where complaints actually arrive, routinely carry several issues at once — `MOCK-DATA.md` lists "Several issues inside one ticket" as a natural characteristic of the support platform.

**What pushes toward a finer grain (one row per device per event):** three things.

- §820.35(a)(3) requires "Any unique device identifier (UDI) or universal product code (UPC), and any other device identification(s)" — a per-unit identifier, and the 2026 compliance program tells investigators to "Verify complaint-handling procedures include provisions for capturing and documenting any UDI when performing assessment of the firm's complaint investigations. Refer to 21 CFR 820.35(a)(3)." A register row that aggregates five units cannot carry five UDIs in one identifier field.
- Reportability is assessed **per event per device**, not per communication, and the downstream vigilance row has to point at something.
- The EU form settles it for the adjacent register: MIR field 1.3.1(c) exists precisely because one incident involving multiple devices from the same manufacturer produces **multiple MIR forms** that cross-reference each other ("If this incident involves multiple devices from the same manufacturer, please list the respective reference numbers of the other MIR forms you have submitted"). If the report grain is per-device, a complaint grain coarser than per-device forces an unmappable join.

**What a real auditor would expect.** One complaint record per alleged deficiency per device. Where one communication yields several, the expectation is several linked complaint records — not one merged record, and not several unlinked records. Conversely, three channels reporting the *same* event must end as one complaint record with the duplicates linked, not three complaint records; that is exactly `DIAGRAMS.md` workflow 1, and the merge is a human act.

Two grain rules to implement, therefore:

- **Never merge two distinct alleged deficiencies into one row.** Split, and link with a `related_complaint_ids` / `parent_complaint_id` pair.
- **Never let one real-world event become several complaint rows without a recorded link and a recorded human decision.** This is why `duplicate_of_complaint_id` is a field and not a deletion.

A corollary the product must respect: **feedback that is *not* a complaint is not a row in this register.** §8.2.1 Feedback is the intake net and §8.2.2 is the filter (`WORKFLOW.md` §3). CP 7382.850 lists **Feedback** (Clause 8.2.1) and **Complaint Handling** as *separate elements*. The `Not a complaint` outcome therefore belongs in the feedback register with a pointer, or as a terminal state on a complaint row that was opened and then reclassified — and the two are not the same thing. Pick one and be consistent; see §4.

### 2.2 Identity and numbering

Nothing in ISO 13485 §8.2.2 or §820.35(a) mandates a complaint number. What §4.2.5 Control of records requires is that records be identifiable and retrievable — so a findable identifier is mandated in effect, and its *format* is entirely convention.

What the row must carry to be findable:

| Purpose | Field |
|---|---|
| Primary key visible to humans | `complaint_no` — the number people say out loud in a meeting |
| Findable by device | device model/product code, serial or lot, UDI/UPC |
| Findable by device name | §803.18(d)(1) requires *distributors* to "file these records by device name"; manufacturers conventionally do the same |
| Findable by customer | account, site, complainant |
| Findable by date | date received (the regulated date), plus date of awareness |
| Findable from outside | the source-system ids it came from (ticket id, message id, work order) — `Product`, workflow 1 |
| Findable from downstream | the NC, CAPA and vigilance-report ids that point back |

Conventional number formats in real registers are year-scoped sequences with a type prefix: `CMP-2026-0147`, `C-26-0147`, `CPL-000147`, sometimes with a site or product-family prefix. The prefix-plus-year-plus-sequence shape is near-universal; the exact string is a per-company decision and is exactly the kind of thing that should vary between Asteria and a second mock company. **See §6 for the verbatim header and numbering evidence.**

One structural warning for the mock data: because complaint numbers are assigned at the moment the complaint record opens, and the regulated `date_received` is earlier (the receipt of the original communication), **complaint numbers are not in date-received order.** A register sorted by number is not sorted by receipt. Real registers show exactly this, and it is a realistic inconsistency to generate.

### 2.3 Field table

#### Identity and intake

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `complaint_no` | string, company-specific pattern | `Convention` | §4.2.5 requires retrievable records; format is convention — see §6 | Not in receipt order. Never reuse a number, including for voided records. |
| `device_name` | string | `Mandated` | 21 CFR §820.35(a)(1) "The name of the device" | US. The *marketed* name, which in Asteria's data will disagree with the ERP product code and with what the nurse called it. |
| `date_received` | date | `Mandated` | §820.35(a)(2) "The date the complaint was received" | The single most disputed field in the register. See §2.6. |
| `device_identifiers` | UDI-DI + UDI-PI, UPC, model, catalogue, serial, lot, software version | `Mandated` | §820.35(a)(3) "Any unique device identifier (UDI) or universal product code (UPC), and any other device identification(s)"; CP 7382.850 §D(4)(g) tells investigators to verify this is captured | Must be multi-valued and must tolerate *absent*. Distinguish "not provided" from "not applicable". |
| `complainant_name` | string | `Mandated` | §820.35(a)(4) "The name, address, and phone number of the complainant" | |
| `complainant_address` | string | `Mandated` | §820.35(a)(4) | |
| `complainant_phone` | string | `Mandated` | §820.35(a)(4) | Email is *not* in the mandated list but is how complaints actually arrive — see next row. |
| `complainant_email` | string | `Convention` | Not in §820.35(a)(4); universal in real registers | Keep it, and keep it separate from the mandated three so an inspection export can show the mandated set. |
| `complainant_role` | enum: healthcare professional · patient/lay user · biomed engineer · distributor · internal (sales/service) · other | `Convention` | MIR 3.4(a) `initialReporterRole` has a regulated equivalent for the *vigilance* row; on the complaint row it is convention | Drives whether "patient" fields can ever be filled. |
| `complaint_text` | long free text | `Mandated` | §820.35(a)(5) "The nature and details of the complaint" | Preserve the complainant's own words verbatim as well as any normalised summary. Two fields, not one. |
| `intake_channel` | enum: email · phone · support ticket · service visit · distributor report · sales visit · chat · web form · literature · regulator | `Convention` | Universal in real registers; ISO 13485 §3.4 contemplates written, electronic and oral communications | An *oral* complaint must be documentable — real registers carry a "documented from verbal report by" field. |
| `received_by` | person | `Convention` | Brazil mandates the analogous decider name for the no-investigation decision (ANVISA RDC 665/2022 Art. 121, via [MDSAP AU P0002.010](https://www.mdsap.global/sites/default/files/2026-02/MDSAP%20AU%20P0002.10%20MDSAP%20Audit%20Approach.PDF)); receipt-by is convention | Load-bearing for the US awareness clock — see §3.6. |
| `customer_account` / `site` / `country_of_use` | refs | `Convention` | Universal; `country_of_use` is effectively forced because jurisdiction selection depends on it | `country_of_use` ≠ ship-to country. `MOCK-DATA.md` flags exactly this ERP/installed-base divergence. |

#### Classification

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `is_complaint` | enum: complaint · feedback only · pending assessment | `Mandated` | ISO 13485 §8.2.2 requires evaluating whether feedback constitutes a complaint (paraphrased); §3.4 supplies the test | The recorded decision that starts regulatory obligations. `DIAGRAMS.md` workflow 2 gate. |
| `classification_rationale` | free text | `Mandated` (in effect) | §8.2.2 requires records of complaint handling; Brazil explicitly requires the decision-maker's name for the analogous negative decision (ANVISA Art. 121 via MDSAP) | A negative classification with no rationale is the finding. |
| `classified_by` / `classified_on` | person / date | `Convention` → `Mandated` in BR | ANVISA Art. 121 requires "the name of the persons responsible for the decision" for a no-investigation decision (via MDSAP AU P0002.010) | Treat as mandated. **The US used to mandate it and no longer does** — old §820.198(b) required the name of the individual responsible for a no-investigation decision; §820.35(a) asks only for "records documenting justification". See §6.1. Carry the field anyway: Brazil requires it and auditors still expect it. |
| `complaint_category` / `failure_mode_code` | controlled vocabulary | `Convention` | MDSAP Task 12 directs auditors to "select one or more complaint failure modes" and sample within them — so a failure-mode taxonomy is an audit-sampling dependency | Will disagree with the support platform's tags and the service system's failure codes by design. |
| `imdrf_device_problem_codes` | IMDRF Annex A codes, 1–6 | `Convention` on the complaint row, `Mandated` on the vigilance row | MIR 3.2(a); IMDRF terminology is mandatory in the MIR | Coding early on the complaint row is what makes trend detection possible. Keep the code *and* the coder and date. |
| `severity` / `harm_alleged` | enum: death · serious injury/deterioration · non-serious harm · no harm · unknown | `Convention` on the complaint row | Derived from §803.3 and MDR Art. 2(65) definitions, which are mandated *for the report*, not for the complaint row | Must allow `unknown`. The complainant who will not say is the normal case. |
| `patient_involved` | yes · no · unknown | `Convention` | MIR 3.2(b) `numPatientsInvolved` is mandated on the vigilance row | |
| `risk_file_ref` | ref | `Convention` | ISO 14971 linkage; MIR 4.2(d) `riskAssReviewed` makes the risk-file review mandated on the *final* MIR | Complaint → risk file is the link teams forget. |

#### Investigation

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `investigation_required` | yes · no | `Mandated` | §820.35(a): "If an investigation has already been performed for a similar complaint, another investigation is not necessary, and the manufacturer shall maintain records documenting justification for not performing such investigation." Same permission in ISO 13485 §8.2.2 (paraphrased) | |
| `no_investigation_justification` | free text + ref to the prior complaint/investigation | `Mandated` | §820.35(a) (quoted above); ANVISA Art. 121 additionally requires "the reason that the investigation was not performed and the name of the persons responsible for the decision" | The ref to the prior investigation is what `DIAGRAMS.md` workflow 4 exists to produce. Free text alone is the thin justification auditors find. |
| `investigation_id` | ref | `Convention` | §8.2.2 requires the investigation be recorded; whether it is a separate record or fields on the complaint is the firm's choice | `WORKFLOW.md` A6. Separate record is the cleaner model and matches `MOCK-DATA.md`'s `qms/investigations/`. |
| `review_evaluation_investigation_record` | ref / text | `Mandated` | §820.35(a): "the manufacturer shall maintain records of the review, evaluation, and investigation for any complaints involving the possible failure of a device, labeling, or packaging to meet any of its specifications" | Three distinct activities — review, evaluation, investigation — and FDA names all three. |
| `investigation_results` / `investigation_dates` | text / dates | `Convention` (was `Mandated` pre-2026) | Old §820.198(e)(5) named "Results and dates of investigation" as record content ([FDA CDRH deck](https://www.fda.gov/files/about%20fda/published/Complaint-Files---Printable-Slides.pdf)); §820.35(a) no longer enumerates it | Keep the fields — every real register has them and FDA warning letters still cite their absence (§6.4) — but the status is honestly `Convention` under the QMSR. |
| `device_returned` | yes · no · pending · not requested | `Convention` on complaint row; `Mandated` on vigilance row | §803.52(c)(10) requires "Whether the device was available for evaluation, and whether the device was returned to the manufacturer, and if so, the date it was returned"; MIR 3.2(c) `currentDeviceLocation` | Asteria's PulsePatch is discarded after use, so "device not available" is the *default* for the consumable and the exception for PulseOne. |
| `device_evaluation_summary` | free text | `Mandated` (when returned) | §803.52(f)(3): "If the device was returned to you and evaluated by you, you must include a summary of the evaluation. If you did not perform an evaluation, you must explain why you did not perform an evaluation" | The "why not" is mandated content, not an omission. |
| `root_cause` / `root_cause_confirmed` | free text / yes · suspected · no | `Mandated` on the final vigilance row | MIR 4.2(a) `rootCauses`, 4.2(c) `rootCauseConfirmed` | On the complaint row, convention. |
| `dhr_lot_batch_reviewed` | refs | `Convention` | §8.2.2 practice; `WORKFLOW.md` A6 | |
| `nff_flag` | boolean | `Convention` | `MOCK-DATA.md` names "No fault found" as a natural service-system characteristic | A complaint closed NFF is not a complaint that never happened. Keep it. |

#### Outcome, response, closure

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `correction_or_corrective_action_taken` | free text + refs | `Mandated` | §820.35(a)(6) "Any correction or corrective action taken" | **The QMSR wording is "correction *or* corrective action", not "corrective action".** This is a change worth noticing: the public text of the regulation now carries the ISO 9000 §3.12.2 / §3.12.3 distinction that `WORKFLOW.md` §7 builds the data model on. Model them as two link types. |
| `reply_to_complainant` | free text / ref | `Mandated` | §820.35(a)(7) "Any reply to the complainant" | `WORKFLOW.md` A9. Also the field most often empty in real registers. |
| `reply_date` | date | `Convention` | Not in §820.35(a); universal | |
| `nc_record_ids` | refs, 0..n | `Convention` (named hand-off) | ISO 13485 §8.2.2 covers handling of complaint-related product and §8.3.3 covers post-delivery nonconforming product — the standard *names* the hand-off (`WORKFLOW.md` §1.1); the register *field* is convention | Linked, never merged. |
| `capa_ids` | refs, 0..n | `Convention` (named hand-off) | §8.2.2 → §8.5.2; CP 7382.850 lists Complaint Handling and Corrective Action as distinct elements | Most complaints never reach CAPA, and that is correct. |
| `capa_not_required_rationale` | free text | `Mandated` in effect | §8.5.2 proportionality (paraphrased); MDSAP Task 15 directs auditors to select records "where a decision was made not to issue an advisory notice as well as records of decision to issue" — the same negative-decision logic | The negative CAPA decision is a record. |
| `vigilance_assessment_ids` | refs, 1..n | `Mandated` (hand-off named) | 21 CFR §820.10(b)(3): "For Clause 8.2.3 in ISO 13485, Reporting to regulatory authorities, the manufacturer must notify FDA of complaints that meet the reporting criteria of part 803 of this chapter." | One per jurisdiction in scope. See §3.1. |
| `advisory_notice_id` / `fsca_id` | refs | `Convention` (named hand-off) | §820.10(b)(4): "For Clauses 7.2.3, 8.2.3, and 8.3.3, advisory notices shall be handled in accordance with the requirements of part 806"; MDR Art. 87(1)(b) | Part 806 and FSCA are a *third* register. See §3.5. |
| `status` | see §2.4 | `Convention` | Lifecycle states are not enumerated in any standard | |
| `closed_on` / `closed_by` | date / person | `Convention` | §8.2.2 requires records of complaint handling; closure metadata is convention | |
| `closure_rationale` | free text | `Mandated` in effect | §8.2.2; `WORKFLOW.md` A11 | |
| `retention_until` | date | `Mandated` in effect | §4.2.5 requires retention periods (paraphrased); for the *MDR event file* §803.18(c) sets "2 years from the date of the event or a period of time equivalent to the expected life of the device, whichever is greater" | For Asteria, PulseOne's expected life drives this, and §803.3(f) defines "expected life of a device". |

#### Product fields (ours, justified against `DIAGRAMS.md`)

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `source_system_refs[]` | `{system, record_id, record_url, observed_at}` | `Product` | Workflow 1 (ingest and resolve), workflow 9 (evidence bundle) | Without this, workflow 9's "walk the chain backwards" is impossible. `MOCK-DATA.md` forbids canonical cross-source ids in the source data, so the register is the *first* place the mapping can legally exist. |
| `field_provenance[]` | per field: `{source_ref, extraction_method, extracted_at, confidence, reviewed_by, reviewed_at}` | `Product` | Workflow 7 ("Cite every field — each value links back to the evidence it came from"); workflow 1 ("every fact keeps source, extraction method, timestamp, confidence") | This is the product. Per-field, not per-record. |
| `authorship` | enum: human · agent-drafted · agent-drafted-human-accepted · agent-drafted-human-amended | `Product` | `DIAGRAMS.md` colour rule: "a green node never creates an approved record" | Must be visible on the record, per `WORKFLOW.md` §11.4. |
| `autonomy_level_at_creation` | enum: observe · recommend · draft · execute-with-approval | `Product` | `DIAGRAMS.md` header table | Recorded so an audit can show which gate applied at the time. |
| `agent_confidence` | 0–1 + calibration note | `Product` | Workflow 1, workflow 2 | Never shown as a reason a human decision was skipped. |
| `duplicate_of_complaint_id` / `related_complaint_ids[]` | refs | `Product` (grain control) | Workflow 1 gate: "official record merges are never automatic" | A rejected merge proposal must also be recorded — see next row. |
| `proposed_links[]` | `{target, kind, proposed_by, confidence, decision, decided_by, decided_on}` | `Product` | Workflow 1 | The *rejected* proposals are evidence that the system was not silently merging. |
| `gaps[]` / `conflicts[]` | `{field, nature, sources_in_conflict[]}` | `Product` | Workflow 3 step A3 ("Flag the gaps — what is missing, what conflicts between sources") | The honest representation of §2.6's mess. Do not resolve conflicts by picking. |
| `precedent_refs[]` | `{complaint_id, similarity_basis, retrieved_at}` | `Product` | Workflow 4 | Feeds `no_investigation_justification`. The similarity *basis* must be stated, not just the match. |
| `denominator_cohort_keys` | model, hw revision, sw version, lot, market, period | `Product` | Workflow 6 ("Compute the denominator") | Must be on the complaint row, not computed later, or the numerator and denominator cohorts will not match. Align with the MIR's own denominator-basis vocabulary — see §3.3. |
| `open_actions[]` | refs to the action register | `Product` | Workflow 8 | `MOCK-DATA.md` has `meetings/action-register.xlsx`; the link direction matters. |
| `information_requests[]` | `{asked_of, asked_on, channel, what, reply_ref, reply_on, attempt_no}` | `Product` | Workflow 8 | Has a real-world template: a published medical-device SOP operationalises "reasonably known" (§803.50(b)) as "At least three attempts will be made to obtain required information. At least one of the attempts must be a written communication. All attempts to collect additional information will be documented." ([Argos Global SOP-0003](https://medicaldeviceacademy.com/wp-content/uploads/Argos-Global-Complaint-Processing-SOP-0003-RevAE.pdf), consultant). This field is what turns "we tried" into evidence. |

### 2.4 Lifecycle / status values

No standard enumerates complaint states. What the standards *do* require is that specific **negative decisions be representable as records**, and that is what constrains the state set. The mandated negatives:

- **Not a complaint** — ISO 13485 §8.2.2 requires the evaluation; the negative outcome is a recorded decision.
- **Investigation declined with documented justification** — §820.35(a), verbatim: "If an investigation has already been performed for a similar complaint, another investigation is not necessary, and the manufacturer shall maintain records documenting justification for not performing such investigation." Brazil additionally requires the decider's name (ANVISA RDC 665/2022 Art. 121, via MDSAP AU P0002.010).
- **Not reportable with rationale** — MDSAP Task 14, verbatim: "Confirm that decisions to not report complaints were made according to established procedures and a documented rationale." In the EU the negative is a *submitted form*: MIR report type `Final (Non-reportable incident)` with field 4.2(b) "For Final (Non-reportable incident) - Fill out rationale for why this is considered not reportable".
- **No CAPA required with rationale** — §8.5.2 proportionality; the same pattern FDA applies in §806.20(b)(4) for unreported corrections: "Justification for not reporting the correction or removal action to FDA, which shall contain conclusions and any followups, and be reviewed and evaluated by a designated person."

A defensible state set, with the negatives as first-class terminal states rather than flags:

```text
                 ┌─────────────────────┐
                 │ 00 Received         │  feedback captured, §8.2.1
                 └──────────┬──────────┘
                            │  §8.2.2 classification gate (human)
        ┌───────────────────┼────────────────────┐
        ▼                   ▼                    ▼
┌───────────────┐   ┌──────────────┐    ┌──────────────────┐
│ 90 Not a      │   │ 10 Open      │    │ 95 Duplicate of  │
│    complaint  │   │              │    │    CMP-xxxx      │
│  (terminal,   │   └──────┬───────┘    │  (terminal,      │
│   rationale)  │          │            │   linked)        │
└───────────────┘          │            └──────────────────┘
                           ▼  investigation decision (human)
            ┌──────────────┴───────────────┐
            ▼                              ▼
┌────────────────────────┐   ┌──────────────────────────────┐
│ 20 Under investigation │   │ 15 Investigation declined     │
└───────────┬────────────┘   │    (justification + prior ref)│
            │                └───────────────┬──────────────┘
            ▼                                │
┌────────────────────────┐                   │
│ 25 Awaiting information│◄──────────────────┘
│   (customer / service /│
│    distributor)        │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ 30 Investigation       │
│    complete            │
└───────────┬────────────┘
            ▼
┌────────────────────────┐
│ 40 Pending response    │   §820.35(a)(7) reply
│    to complainant      │
└───────────┬────────────┘
            ▼
┌────────────────────────┐     ┌────────────────────────┐
│ 50 Closed              │     │ 99 Void / entered in   │
└────────────────────────┘     │    error (terminal,    │
                               │    never deleted)      │
                               └────────────────────────┘
```

Three design rules that fall out:

1. **`90 Not a complaint` and `95 Duplicate` are terminal states, not deletions.** §4.2.5 record control and workflow 9 both require the trail to survive.
2. **`15 Investigation declined` is a normal closure path, not an error path.** It is explicitly permitted by §820.35(a) and §8.2.2, and it is the path that `DIAGRAMS.md` workflow 4 is built to support.
3. **`99 Void` must exist and must be distinguishable from `90 Not a complaint`.** One says "this was assessed and is not a complaint"; the other says "this record should never have been created". Auditors ask which.

A state the register must *not* have: "closed pending reportability". The vigilance clock is independent (`WORKFLOW.md` §5) and a complaint can legitimately close while a follow-up report obligation is still open, or close while a report is already submitted. Complaint status and report status are separate columns.

### 2.5 Links out

| From → to | Direction | Cardinality | Named in the standard? |
|---|---|---|---|
| Complaint → NC record (§8.3.3) | out | 0..n | **Partly.** §8.2.2 requires the procedure to cover handling of complaint-related product and §8.3.3 covers post-delivery nonconforming product, so the hand-off is named; the *linked-record* implementation is convention. `WORKFLOW.md` §1.1 is the precise statement. |
| NC record → complaint | back | 0..n | Convention. Needed because an NC found at incoming inspection can later be matched to open complaints (workflow 5). |
| Complaint → investigation record | out | 0..1 | §8.2.2 requires the investigation be recorded; separating it into its own record is convention. §820.35(a) names "review, evaluation, and investigation" as the recorded activities. |
| Complaint → CAPA | out | 0..n | Hand-off named (§8.2.2 → §8.5.2); link is convention. CP 7382.850 keeps Complaint Handling and Corrective Action as separate elements. |
| Complaint → vigilance assessment | out | 1..n (one per jurisdiction in scope) | **Yes, and uniquely explicit in the US.** 21 CFR §820.10(b)(3): "the manufacturer must notify FDA of complaints that meet the reporting criteria of part 803". This is the only one of these edges quoted in regulation as a complaint→report obligation. |
| Complaint → advisory notice / FSCA / Part 806 report | out | 0..n | Named: §820.10(b)(4) routes Clauses 7.2.3, 8.2.3 and 8.3.3 advisory notices to Part 806; MDR Art. 87(1)(b) makes FSCA reportable in its own right. |
| Complaint → risk file | out | 0..n | Convention on the complaint row, but MIR 4.2(d) makes "Has the risk assessment been reviewed?" mandatory content on a final MIR — so the link has to exist somewhere. |
| Complaint → PMS/PSUR period | out (aggregation) | n..1 | MDR Art. 83–86 / Annex III; the register is an input, not a step inside PMS (`WORKFLOW.md` §6). |
| Complaint → feedback record (§8.2.1) | back | 1 | Convention, but structurally required: CP 7382.850 treats Feedback and Complaint Handling as separate elements, so the complaint must point back at its feedback origin. |
| Complaint ↔ complaint (duplicate / related / precedent) | both | 0..n | Convention. `Product` in our implementation because the *proposal and decision* are recorded, not only the result. |

**Where the standard names the hand-off versus where it is convention** — the honest summary: only two edges are named in public regulatory text (complaint→FDA reporting via §820.10(b)(3); advisory notices→Part 806 via §820.10(b)(4)). Complaint→NC and complaint→CAPA are named *as process obligations* in ISO 13485 clauses but not as record links. Everything else is convention. Saying this out loud is worth more than pretending the links are all mandated.

### 2.6 Clock fields on the complaint register

The complaint register has no statutory clock of its own. ISO 13485 §8.2.2 requires timely handling (paraphrased) and firms set their own internal targets. What the complaint register *must* carry is the **clock-start evidence** that the vigilance register depends on — and this is where the product earns its keep.

| Field | Type | Status | Source | Notes |
|---|---|---|---|---|
| `date_received` | date | `Mandated` | §820.35(a)(2) | The regulated date. |
| `first_receipt_timestamp` | timestamp + tz | `Product` | Workflow 3 A1 ("Pin the start of the clock — first receipt timestamp and where it landed") | Not the same as `date_received`. Time zone is not optional: MDCG 2023-3 Q14 runs the EU period from 00:00:01 the day after, so a timestamp 40 minutes either side of midnight moves the deadline by a day. |
| `first_receipt_location` | system + mailbox/queue + recipient | `Product` | Workflow 3 A1 | This is the field that settles "who knew, and were they the kind of employee whose knowledge starts the 5-work-day clock". See §3.6. |
| `awareness_candidates[]` | `{timestamp, source_ref, recipient, role, basis, selected}` | `Product` | Workflow 3; `MOCK-DATA.md` "date-of-awareness disputed" | Model awareness as a *set of candidate dates with one selected and a recorded reason*, not a single value. This is the single highest-leverage schema decision in the note. |
| `internal_target_due` | date | `Convention` | Internal KPI, universal | Keep separate from any statutory due date so the two are never confused in a UI. |
| `days_open` | derived int | `Convention` | Universal register column | Derived, never stored. Real registers store it and it goes stale — a good mock-data imperfection. |

### 2.7 What a real export looks like

Covered with verbatim evidence in §6. The short version of what we must be able to ingest and emit:

- An **Excel workbook with a worksheet per year** (`2024`, `2025`, `2026`, often plus a stale `Sheet1` and a hidden `Lookups` tab), where the header row is not row 1, totals rows sit inside the data range, and date columns are a mix of real dates and text.
- An **eQMS table export** (CSV or XLSX) with system column names rather than human ones, a `Record ID` that is not the complaint number, and one row per complaint but a separate export for child objects (investigations, attachments).
- A **PDF "Complaint Log"** printout with a signature block — the rendition that actually gets handed to an auditor.
- Per-complaint **DOCX or PDF complaint forms** in a folder, whose filenames disagree with the register's metadata (`MOCK-DATA.md` "Mismatched filenames and register metadata").

`MOCK-DATA.md` already prescribes `qms/complaints/` plus a `document-register.xlsx`; the realistic addition is that the *register workbook* and the *per-complaint records* disagree, because `MOCK-DATA.md` itself notes "Register values that occasionally lag behind repository state".

### 2.8 Fields that are routinely incomplete or disagreed-on

For honest mock data. Each of these should appear in Asteria's data without being flagged as an error anywhere in the product-facing files.

| Field | How it fails in reality | Why |
|---|---|---|
| `device_identifiers` — serial | Missing, partial, transcribed wrong, or with punctuation variants | `MOCK-DATA.md`: support "Missing serial or lot numbers"; "Serial numbers with punctuation or transcription differences". Asteria's PulseOne serials will arrive as `P1-100 #4471`, `4471`, `SN 04471`. |
| `device_identifiers` — lot | Unknown for PulsePatch because the pouch is already in the clinical waste | Structural to the product: PP-72 is discarded after use. The photograph of the pouch is sometimes the only evidence — `MOCK-DATA.md` "label photographs". |
| `device_identifiers` — UDI | Blank, even though §820.35(a)(3) requires it and CP 7382.850 tells investigators to check | Nurses do not read UDIs off labels. This is a real and inspectable gap, and generating it honestly is more valuable than generating it clean. |
| `device_identifiers` — software version | Stale | `MOCK-DATA.md`: "Software-version information can be stale"; `products.md`: "A released version does not imply that every installed unit was upgraded." |
| `complainant_name` / patient identity | Complainant will not identify the patient; hospital privacy policy blocks it | §803.52(a)(1) asks for "Patient name **or other identifier**" precisely because the name is often unavailable. MIR 3.3 asks age/gender/weight/height — routinely `unknown`. §803.50(b)(3) then requires: "If you cannot submit complete information on a report, you must provide a statement explaining why this information was incomplete and the steps you took to obtain the information." **The explanation is the mandated substitute for the value.** |
| `date_received` | Genuinely disputed: the email hit the shared quality mailbox Friday 18:40, the support ticket was created Monday 09:10, the complaint record was opened Wednesday | This is the product's central problem. Three systems, three defensible answers, and the one you pick moves a statutory deadline. Generate all three and let them disagree. |
| `severity` / `harm_alleged` | `unknown` at intake and often never resolved | Patient outcome frequently never comes back from the hospital. |
| `device_returned` / `device_evaluation_summary` | Device never returned; evaluation therefore impossible | §803.52(f)(3) turns this into a mandated *explanation*. Real registers leave it blank instead. |
| `reply_to_complainant` | Empty, or "see email" with no attachment | Mandated by §820.35(a)(7) and one of the commonest gaps. |
| `root_cause` | "No fault found", or a root cause that contradicts the customer's description | `MOCK-DATA.md`: "'No fault found' conclusions"; "Differences between customer symptoms and technician findings". |
| `complaint_category` | Default or catch-all category; recategorised later | `MOCK-DATA.md` "Default or catch-all categories", "Categories that change over time". |
| `closed_on` | In the per-complaint record but not in the register workbook, or vice versa | `MOCK-DATA.md` "Register values that occasionally lag behind repository state". |

---

## 3. Register B — Vigilance / regulatory reporting register

This is the register where the product's claim lives, so it gets the more careful treatment.

### 3.1 Grain

**One row = one reportability obligation = (event × device × jurisdiction).** A row exists from the moment a jurisdiction is in scope, *before* and *independently of* whether anything is submitted. Submissions are child records (versions) of the row, not new rows.

The evidence, jurisdiction by jurisdiction:

**US — and the per-device split is mandated here too, not just in the EU.** Form FDA 3500A's General Instructions, verbatim: **"For medical device reporting, manufacturers, importers, and user facilities must prepare and submit a complete Form FDA 3500A for each suspect device. Each Form FDA 3500A will be given a separate Report Number."** FDA's MDR guidance adds the series case: "If more than one of your devices is involved in a single MDR reportable event, and it is not apparent which device may have caused or contributed to the event, then you must submit a separate report for each of your devices involved in the event. … if a series of MDR reportable events occurs, the regulation requires a separate report for each event." ([3500A instructions](https://www.fda.gov/media/133177/download); [FDA MDR guidance](https://www.fda.gov/media/86420/download))

§803.3(m) then defines the manufacturer report number as the thing that "uniquely identifies each individual adverse event report submitted by a manufacturer or importer", and §803.56 requires a supplemental or follow-up report to "Submit the appropriate identification numbers of the report that you are updating" and to "Include only the new, changed, or corrected information". The 3500A instructions make it explicit: **"For a follow-up report, the manufacturer report number must be identical to the number assigned to the initial report"**, with the follow-up sequence carried separately in `G6` ("first follow-up report = follow-up #1, second follow-up report = follow-up #2, and so on"). That settles follow-ups: versions, not rows — and it means the FDA report number is unique per *row*, never per submission.

**EU.** MIR field 1.3.1(b) is "Manufacturer's reference number for this incident" — per incident. Field 1.3.1(c) handles the multi-device case by pointing at *other MIR forms*: "If this incident involves multiple devices from the same manufacturer, please list the respective reference numbers of the other MIR forms you have submitted." So the EU grain is explicitly **one MIR per device per incident**. And Art. 87(11) directs the report to "the competent authority of the Member State in which that serious incident occurred" — one NCA per incident normally, several when a device is distributed widely and authorities coordinate.

**Therefore the row key is (event, device, jurisdiction/authority).** A single PulseOne failure in a Hamburg ward that also triggers a US malfunction obligation is **two rows**, with two different clocks, two different report numbers, two different decision records, and possibly two different outcomes.

Two independent confirmations that this is the right call rather than a tidy-minded one. First, **a merged cross-jurisdiction reportability verdict is FDA-citable**: a manufacturer was cited under §803.17(a)(2) because its procedure "combined language from the requirements of other regulatory or competent authorities with the requirements in 21 CFR Part 803 in a manner that will result in incomplete, inadequate, or even non-reporting" ([Exactech, 01/19/2024](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/exactech-inc-669904-01192024)). Second, a mainstream safety platform ships exactly this shape: a global Case carrying a `Global Due Date`, with per-locale records each carrying their own `Due Date` ([Veeva, vendor](https://safety.veevavault.help/en/lr/891324/)). See §6.7.

And the fan-out is real in enforcement, not just in theory: one firm's single complaint number `NCP 2022-14` carried five late-reported events across Texas, Pennsylvania and Spain ([Future Diagnostics Solutions B.V., 05/11/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/future-diagnostics-solutions-bv-653493-05112023)).

**Where the grain is genuinely contested, and what an auditor expects:**

| Contested question | The two defensible answers | What a real auditor expects |
|---|---|---|
| Is a **not-reportable** determination a row here, or a field on the complaint? | (a) field on the complaint; (b) row here with status `Not reportable` | Either is acceptable *if the rationale is a record*. §803.18(e) explicitly permits the US MDR event file to live inside the complaint file "if you prominently identify these records as MDR reportable events". But **multi-jurisdiction forces the row**: one event can be reportable in the EU and not in the US, and a single field on the complaint cannot hold two opposite determinations with two rationales. Put it here. |
| Are **follow-ups** rows or versions? | versions | Versions. §803.56(b) requires the follow-up to cite the original report number. MIR `reportType` (Initial / Follow-up / Combined initial & final / Final (Reportable incident) / Final (Non-reportable incident)) is a *property of a submission*, and MIR 1.2(f) carries "the expected date of next report" — i.e. a chain under one reference. |
| Are **trend reports (Art. 88)** rows in this register? | (a) yes, as a distinct row type; (b) separate register | Yes, as a distinct row type here, because they are submitted through the same electronic system (Art. 88(1) → Art. 92) and carry the same identifier shape (trend form: "Reference number assigned by the manufacturer", "Reference number assigned by NCA", type Initial/Follow up/Final). Their grain is **one row per (device or device group × trend × NCA × observation period)** — not per event. Their clock is not an awareness clock (see §3.6). |
| Are **periodic summary reports** rows? | yes | Yes, two flavours with different parents: EU PSR under Art. 87(9) (MIR field 1.3.1(e) `psrId` links individual incidents to the PSR), and US **VMSR** quarterly malfunction summary reports. Both are rows whose grain is a *bucket*, with many complaint rows pointing at them. |
| **US VMSR grain** | — | FDA is explicit: "separate summary malfunction reports must be submitted for each unique combination of brand name, device model, and MDR adverse event device problem code(s)". So a VMSR row's key is (brand, model, problem-code-set, quarter). This is a materially different grain from an individual MDR and the register must support both. |

The VMSR point is easy to miss and it changes the shape of the register: **in the US, most malfunction reports for eligible product codes are not individual reports at all.** Deaths and serious injuries stay individual (always), and a malfunction "associated with a 5-day report" is excluded from VMSR.

### 3.2 Identity and numbering

This register carries **at least four identifiers per row**, and three of them are assigned by somebody else.

| Identifier | Format | Status | Source |
|---|---|---|---|
| `internal_ref` | company pattern, e.g. `VIG-2026-0042`, `MDR-26-0042` | `Convention` | MIR 1.3.1(b) makes a manufacturer reference *mandatory on the form*, so the field is mandated even though the format is not. |
| `fda_manufacturer_report_number` | `{7-digit FDA registration number}-{YYYY}-{NNNNN}`, e.g. `1234567-2011-00001` | `Mandated` | §803.3(m), verbatim: "(1) The FDA registration number for the manufacturing site of the reported device … (2) The four-digit calendar year in which the report is submitted; and (3) The five-digit sequence number of the reports submitted during the year, starting with 00001. (For example, the complete number will appear as follows: 1234567-2011-00001.)" Also required on a VMSR summary report. |
| `nca_report_number` | assigned by the national competent authority | `Mandated` on follow-up/final MIRs | MIR 1.1(c): "This is a mandatory field when reference number is provided by the NCA. If no reference number is provided by the NCA, please add 'Unknown' in the follow-up and final reports." **The regulator's own form tells you to write the literal string `Unknown`.** Free realism. |
| `eudamed_reference` | assigned by Eudamed | `Mandated` "as soon as available in EUDAMED" | MIR 1.1(d). Today: blank, because the VGL module is not live (§1 fact 4). |
| `part_806_report_number` | `{7-digit registration}-{M/D/YY}-{NNN}-{C or R}`, e.g. `1234567-6/1/97-001-C` | `Mandated` for corrections/removals | §806.10(c)(1), verbatim example. A *third* numbering grammar, with slashes inside the identifier — and therefore a CSV-quoting hazard and a realistic mock-data trap. |
| `psr_id` / `vmsr_report_id` | bucket identifiers | `Mandated` where used | MIR 1.3.1(e) `psrId`; VMSR summary report carries an MDR Number of the same §803.3(m) shape. |
| `fsca_references` | three of them: `ncaRefFSCA`, `eudamedRefFSCA`, `mfrRefFSCA` | `Mandated` when applicable | MIR 1.3.1(d): "If this incident is covered under an FSCA, please provide the relevant numbers". |

Two observations worth carrying into the schema:

1. **Three numbering grammars, one of which contains slashes and one of which is literally the word `Unknown`.** An identifier column in this register cannot be a clean opaque key. Model every external identifier as `{value, assigned_by, assigned_on, status: assigned|pending|unknown|not-applicable}`.
2. **The FDA number embeds the submission year, not the event year.** A 2025 event reported in January 2026 gets a `…-2026-…` number. Sorting by report number is not sorting by event date, and a register that reconciles against MAUDE has to know this.

### 3.3 Field table

#### Row identity and scope

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `internal_ref` | string | `Mandated` (value), `Convention` (format) | MIR 1.3.1(b) `mfrRef` | |
| `jurisdiction` / `authority` | enum of authorities (FDA, per-MS NCA, MHRA, HC, TGA, ANVISA, PMDA…) | `Mandated` in effect | Art. 87(11) directs the report to the Member State where the incident occurred; §803.50 to FDA; `WORKFLOW.md` §5 | The column that makes the grain work. |
| `applicable_regulation` | enum: 21 CFR 803 · MDR Art. 87 · MDR Art. 88 · 21 CFR 806 · national | `Mandated` in effect | Each clock belongs to a named instrument | Determines which clock and which form. |
| `complaint_id` | ref, 1 | `Mandated` (hand-off) | §820.10(b)(3) | A vigilance row with no parent complaint is possible (a regulator-initiated report under Art. 87(11)) — allow 0 with a reason. |
| `event_id` | ref to the resolved event | `Product` | Workflow 1 | Lets two jurisdiction rows share one event without either owning it. |
| `device_ref` | ref to model + unit/lot | `Mandated` | §803.52(c); MIR 2.3 | |
| `report_required_by_form` | enum: 3500A/eMDR · MIR v7.3.1 · trend form · PSR form · 806 report · national form | `Convention` | EC PMSV forms page; §803.11(a) | Version matters: MIR 7.2.1 vs 7.3.1 changes the field set. Store the form version on the submission, not the row. |

#### Event and clock (see §3.6 for the full clock model)

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `date_of_incident` | date **or date range** | `Mandated` | MIR 1.2(b) `adverseEventDateFrom` / `adverseEventDateTo`: "if incident date is unknown, please enter a date range when you think the incident occurred"; §803.52(b)(3) "Date of event" | A **range**, not a date. This is a primary-source instruction to model uncertainty as a range, and it should be the pattern for every uncertain date in our system. |
| `awareness_date_incident` | date | `Mandated` | MIR 1.2(c) `mfrAwarenessDate`; MDCG 2023-3 Q15 | Defined below. |
| `awareness_date_reportability` | date | `Mandated` (EU) | MIR 1.2(d) `mfrAwarenessReportDate` | The second awareness date. New in v7.3.1. |
| `us_awareness_date_30day` | date | `Mandated` (US, derived from §803.3(b)(2)) | §803.50(a) + §803.3(b) | Different definition from the 5-day date. See §3.6. |
| `us_awareness_date_5day` | date | `Mandated` (US) | §803.53(a) + §803.3(b)(2) | Different definition. See §3.6. |
| `clock_class` | enum (EU): serious public health threat · death · unanticipated serious deterioration · all other reportable incidents | `Mandated` | MIR 1.2(g) `eventClassification`; MDR Art. 87(3)–(5) | The MIR's classification field *is* the clock selector: 2 / 10 / 10 / 15 days. |
| `clock_class_us` | enum: 30-calendar-day · 5-work-day · VMSR quarterly · not reportable | `Mandated` in effect | §803.50 / §803.53; VMSR guidance | |
| `due_date` | date | `Product` (computed) | No regulation states a due *date*; they state periods. Computation rules in §3.6 | Must be recomputed, versioned, and must carry the rule version that produced it. |
| `date_submitted` | date | `Mandated` in effect | MIR 1.2(a) `reportDate` "Date when you submit the report"; §803.12(a) requires electronic submission | |
| `next_report_expected_date` | date | `Mandated` (EU, initial/follow-up) | MIR 1.2(f) `reportNextDate` | A second, softer clock that real registers forget. |
| `days_late` | derived int | `Convention` | Universal register column | Compute; never store. |

#### Reportability decision

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `reportable` | enum: yes · no · uncertain-reporting-anyway · pending | `Mandated` in effect | Art. 87(7), verbatim: "If, after becoming aware of a potentially reportable incident, the manufacturer is uncertain about whether the incident is reportable, it shall nevertheless submit a report within the timeframe" | **`uncertain-reporting-anyway` is a mandated state, not a hedge.** The EU requires you to report while uncertain. A register that only has yes/no cannot represent compliance. |
| `not_reportable_rationale` | free text | `Mandated` | MIR 4.2(b) `manufacturersWhyNotReportable`; MDSAP Task 14 ("documented rationale"); Art. 87(11) requires an "explanatory statement" to the CA when the manufacturer considers an incident not serious | In the EU the negative decision can itself be a *submitted form* — report type `Final (Non-reportable incident)`. |
| `decided_by` / `decided_on` | person / date | `Convention` → effectively mandated | §806.20(b)(4) requires the analogous negative justification be "reviewed and evaluated by a designated person"; ANVISA Art. 121 requires the decider's name | Never an agent. `WORKFLOW.md` hard gate. |
| `reportability_criteria_applied` | structured: harm · malfunction · recurrence-likelihood · causality · seriousness | `Mandated` in effect | §803.50(a)(1)–(2); §803.3(o) MDR reportable event; MDR Art. 2(64)/(65) | The decision facts workflow 3 assembles. Store the *answers*, not just the conclusion. |
| `causality_assessment` | enum: established · reasonably possible · suspected · excluded · unknown | `Mandated` in effect (EU) | Art. 87(3) "immediately after they have established the causal relationship … or that such causal relationship is reasonably possible"; Art. 87(5) "has established or as soon as it suspects" | Three different causality thresholds across the three EU clocks. |
| `report_type` | enum: Initial · Follow-up · Combined initial & final · Final (Reportable incident) · Final (Non-reportable incident) | `Mandated` (EU) | MIR 1.2(e) `reportType` | Per *submission*, not per row. |
| `us_report_type` | enum: 30-day initial · 5-day · supplemental/follow-up · VMSR summary | `Mandated` (US) | §803.52(e)(6) "Type of report being submitted (e.g., 5-day, initial, followup)" | |

#### Device, event and clinical content (mandated form fields)

Rather than restate two long form field lists, the register should carry the union, keyed to its source. The load-bearing ones:

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `brand_name` | string | `Mandated` | §803.52(c)(1) "Brand name"; MIR 2.3(a) | |
| `product_code` (FDA) | 3-letter code | `Mandated` | §803.52(c)(2) "Product Code, if known, and Common Device Name" | Also determines VMSR eligibility. |
| `model` / `catalogue_no` / `serial_no` / `lot_no` | strings, multi-valued | `Mandated` | §803.52(c)(4); MIR 2.3(c)–(f) | §803.52(c)(4) is one compound field: "Model number, catalog number, serial number, lot number, or other identifying number; expiration date; and unique device identifier (UDI) that appears on the device label or on the device package". |
| `udi_di` + `udi_pi` + `basic_udi_di` + `unit_of_use_udi_di` | strings + issuing entity | `Mandated` | MIR 2.1(a)–(d) with an `issuing entity` for each; §803.52(c)(4) for UDI | The EU wants **four** UDI fields plus issuing agencies. The US wants one. |
| `software_version` / `firmware_version` | strings | `Mandated` (EU) | MIR 2.3(g) `deviceSoftwareVer`, 2.3(h) `deviceFirmwareVer` | Directly relevant to Asteria: PulseOne carries a customer-visible semantic version *and* an internal build id. |
| `emdn_code` / nomenclature | code + system | `Mandated` (EU) | MIR 2.2(a) `nomenclatureSystem`, 2.2(b) `nomenclatureCode` | EMDN in the EU, FDA product code in the US, GMDN historically. Three vocabularies. |
| `device_risk_class` | MDR/IVDR class + legacy MDD/AIMDD/IVDD class + device-type flags | `Mandated` (EU) | MIR 2.4(a)–(e), incl. `deviceClassMDRType` flags: implantable, active device, intended to administer, sterile conditions, measuring function, reusable, software, systems, procedure packs, custom-made, non-medical | Class **when placed on the market**, not current class. |
| `notified_body_id` / `nb_certificate_no` | strings (×2 each) | `Mandated` (EU, if applicable) | MIR 2.3(p) | |
| `market_distribution` | country set | `Mandated` (EU) | MIR 2.5a; trend/PSR forms have a country checkbox grid | |
| `event_description` | long free text, ≤4000 chars | `Mandated` | MIR 3.1(a) `eventDescription`; §803.52(b)(5) "Description of the event or problem, including a discussion of how the device was involved, nature of the problem, patient followup or required treatment, and any environmental conditions that may have influenced the event" | **The MIR helptext states: "Free text fields are limited to 4000 characters (approximately 1 A4)."** A hard character budget on the narrative — a real constraint our drafting workflow must respect. |
| `imdrf_device_problem_codes` | IMDRF Annex A, up to 6 | `Mandated` (EU) | MIR 3.2(a) `imdrfCodeChoice1-6`, plus `imdrfCodeMissing` | There is an explicit **"codes missing"** field. Model "we could not code this" as a value. |
| `imdrf_health_effect_codes` | IMDRF Annex E (clinical signs) + Annex F (health impact), up to 6 each | `Mandated` (EU) | MIR 3.3(a), plus `imdrfMissingCodeHealthEffect` | |
| `imdrf_cause_investigation_codes` | IMDRF Annex B (type of investigation, up to 8) + Annex C (findings) + Annex D (conclusions) | `Mandated` (EU, final) | MIR 4.2(e) | |
| `imdrf_component_codes` | IMDRF Annex G, up to 6 | `Mandated` (EU, final) | MIR 4.2(f), plus `imdrfMissingComponentCodes` | Maps onto Asteria's field-replaceable component catalogue. |
| `fda_evaluation_codes` | FDA event / method of evaluation / result / conclusion codes | `Mandated` (US) | §803.52(f)(6) "Evaluation codes (including event codes, method of evaluation, result, and conclusion codes) (refer to FDA MedWatch Medical Device Reporting Code Instructions)" | The US and EU code systems are **different vocabularies for the same judgement**. Store both; never derive one from the other silently. |
| `patient_outcome` | enum incl. death, serious injury (3 statutory sub-tests), malfunction only | `Mandated` (US) | §803.52(b)(2): serious injury is "(i) A life-threatening injury or illness; (ii) A disability resulting in permanent impairment of a body function or permanent damage to a body structure; or (iii) An injury or illness that requires intervention to prevent permanent impairment of a body structure or function" | |
| `patient_identifier` / `age` / `gender` / `weight` / `height` | mixed | `Mandated` | §803.52(a)(1)–(4); MIR 3.3(b)–(e) | §803.52(a)(1) is "Patient name **or other identifier**". Height is EU-only. |
| `num_patients_involved` | int | `Mandated` (EU) | MIR 3.2(b) `numPatientsInvolved` | |
| `device_operator_at_event` | enum: health professional · lay user/patient · other | `Mandated` | §803.52(c)(5); MIR 3.2(d) | |
| `current_device_location` | enum + other-text | `Mandated` (EU) | MIR 3.2(c) `currentDeviceLocation` | Stronger than the US "was it available for evaluation". |
| `single_use_reprocessed` + `reprocessor_name_address` | bool + strings | `Mandated` (US) | §803.52(c)(8)–(9) | |
| `concomitant_products` | text + therapy dates | `Mandated` (US) | §803.52(c)(11): "Concomitant medical products and therapy dates. (Do not report products that were used to treat the event.)" | |
| `initial_reporter_*` | name, address, phone, health-professional flag, occupation, whether they also reported to FDA | `Mandated` (US) | §803.52(d)(1)–(4) | MIR 3.4 asks instead for the *healthcare facility* block plus a facility report number. |
| `healthcare_facility_report_number` | string | `Mandated` (EU, if applicable) | MIR 3.4(c) `healthcareFacilityRepNum` | A fifth external identifier. |
| `report_sources` | enum set | `Mandated` (US) | §803.52(e)(3) "Your report sources" | |
| `pma_510k_number` + `is_combination_product` | strings / bool | `Mandated` (US) | §803.52(e)(5) | |
| `remedial_action_taken` + `type` | bool + enum | `Mandated` (US) | §803.52(f)(7) | |
| `reported_as_806_removal_correction` + `number` | bool + string | `Mandated` (US) | §803.52(f)(9): "Whether remedial action was reported as a removal or correction under section 519(f) … and if it was, provide the correction/removal report number" | The explicit 803↔806 cross-reference, in regulation. |
| `corrected_data` / `missing_information_explanation` | free text | `Mandated` (US) | §803.52(f)(11)(iii): "If your report omits any required information, you must explain why this information was not provided and the steps taken to obtain this information"; §803.50(b)(3) the same | **The register must have a field for "why this field is empty".** This is the single most product-relevant mandated field in Part 803. |
| `risk_assessment_reviewed` | enum + rationale-if-not + adequacy + results | `Mandated` (EU, final) | MIR 4.2(d) `riskAssReviewed`, `rationaleNoReview`, `riskAssAdequate`, `riskAssResults` | Forces the vigilance row to point at the risk file. |
| `corrective_action_description` + `schedule` | free text + dates | `Mandated` (EU, final) | MIR 4.2(g) "Description of remedial action/corrective action/preventive action/Field Safety Corrective Action", 4.2(h) "Time schedule for the implementation of the identified actions" | |
| `similar_incidents_basis` | free text | `Mandated` (EU, final) | MIR 4.3.3(a) `similarVariant`: "Specify medical device identification e.g. based on model, product platform, batches, serial number range etc." | The cohort definition, written down. |
| `denominator_basis` | enum (below) | `Mandated` (EU, final) | MIR 4.3.3(b) `numberBasedOn` | See §3.3.1 — this is the Art. 88 denominator, enumerated by the regulator. |
| `similar_incidents_counts` | matrix: 4 periods × {country of incident, EEA+CH+TR, World} × {similar incidents, devices on market} | `Mandated` (EU, final) | MIR 4.3.3(c) `timePeriodN` … `timePeriodN-3` with `countrySimInc`/`countrySimDev`/`eeaChTrSimInc`/`eeaChTrSimDev`/`worldSimInc`/`worldSimDev` | **24 numbers**, yearly by default. This is the single richest structured field in either register. |
| `how_determined` | free text | `Mandated` (EU, final) | MIR 4.3.3(d) `howWereDetermined` — "Comments on how similar (serious) incidents and associated number of devices on the market were determined" | A mandated *methodology* narrative. Workflow 6's output has a regulated home. |

##### 3.3.1 The denominator vocabulary, from the regulator

MIR field 4.3.3(b) enumerates the acceptable denominator bases, and the helptext splits them by whether cumulative data may be used across the horizontal time periods. Quoted from the MIR v7.3.1 helptext:

Cumulative across periods is acceptable for:

> - "Active installed base"
> - "Number of devices implanted"
> - "Units distributed from the date of declaration of conformity"
> - "Devices placed on the market or put into service"
> - "Other -describe"

Cumulative is **not** acceptable for — "competent authorities do not consider the following appropriate for the use of cumulative data":

> - "Units distributed within each time period"
> - "Number of tests performed"
> - "Number of episodes of use"

This is the most useful single find for `DIAGRAMS.md` workflow 6. It means:

- The denominator is not ours to invent. There is a **regulator-enumerated vocabulary**, and the product should speak it.
- For Asteria the choice is forced and interesting: PulseOne is a reusable device, so "Active installed base" or "Number of episodes of use" apply (and `products.md` already contemplates use sessions). PulsePatch is a consumable, so "Units distributed within each time period" — which is the category where cumulative data is **not** allowed.
- One product family therefore needs two denominator bases with different aggregation rules, in the same register. That is exactly the kind of thing a demo should show, and it is sourced, not invented.

#### Submission and acknowledgement

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `submission_channel` | enum: eMDR gateway · eMDR eSubmitter · national NCA portal · NCA email · Eudamed VGL · paper | `Mandated` in effect | §803.12(a): manufacturers "must submit initial and supplemental or followup reports to FDA in an electronic format that FDA can process, review, and archive"; MDCG 2023-3 Q21 for the EU national-process position | EU rows will change channel mid-life when the VGL module goes live: "for vigilance reports initiated in accordance with the national process in the absence of Eudamed and still open when the VGL module becomes mandatory to use, the subsequent actions should be done in Eudamed". So channel belongs on the *submission*, not the row. |
| `acknowledgement_refs[]` | per submission | `Mandated` in effect (US) | §803.18(b)(1)(iii) requires the MDR event file to contain "Copies of all electronic acknowledgments FDA sends you in response to electronic MDR submissions" | Acknowledgements are **mandated file content**. See §6 for the eMDR acknowledgement levels. |
| `submitted_by` | person | `Convention` | Universal | |
| `attachments[]` | refs | `Mandated` in effect | §803.18(b)(1) permits references to other information "in lieu of copying and maintaining duplicates in this file" | So the register may legitimately hold *pointers*, not copies. |
| `mdr_event_file_ref` | ref | `Mandated` (US) | §803.18(a): "you must establish and maintain MDR event files. You must clearly identify all MDR event files and maintain them to facilitate timely access." | If held inside the complaint file, §803.18(e) requires you to "prominently identify these records as MDR reportable events". A flag on the complaint record, in other words. |
| `deliberation_record` | refs + text | `Mandated` (US) | §803.18(b)(1)(i): the file must contain "all documentation of your deliberations and decision making processes used to determine if a device-related death, serious injury, or malfunction was or was not reportable under this part" | Verbatim: **"was or was not reportable"**. The negative decision's full deliberation trail is mandated US file content, not a nice-to-have. |
| `retention_until` | date | `Mandated` (US) | §803.18(c): "2 years from the date of the event or a period of time equivalent to the expected life of the device, whichever is greater. If the device is no longer distributed, you still must maintain MDR event files for the time periods described in this paragraph" | |

#### Product fields (ours)

| Field | Type / allowed values | Status | Source | Notes |
|---|---|---|---|---|
| `awareness_candidates[]` | `{timestamp, tz, source_ref, recipient, recipient_role, employee_class, basis, selected, selected_by, selected_reason}` | `Product` | Workflow 3 A1 | The core of the product. `employee_class` exists because the US 5-day clock depends on *which kind* of employee knew (§3.6). |
| `clock_instances[]` | `{clock_class, rule_version, awareness_ref, start_at, due_at, holiday_calendar, computed_at}` | `Product` | Workflow 3 A3 ("Surface the applicable clocks … flag divergence") | Several clocks per row. Each must state its own rule version so a recomputation is explainable. |
| `jurisdiction_divergence[]` | `{jurisdictions, differing_determination, reason}` | `Product` | Workflow 3 A3 "flag divergence" | Reportable in the EU, not in the US — with the reason, not just the flag. |
| `evidence_pack_ref` | ref | `Product` | Workflow 9 | |
| `field_provenance[]` | as complaint register | `Product` | Workflow 7 | Per-field citation is what makes a drafted 3500A reviewable. |
| `authorship` / `autonomy_level` | as complaint register | `Product` | `DIAGRAMS.md` hard gates | The reportability determination is a hard human gate. The record must prove a human made it. |
| `gaps[]` / `conflicts[]` | as complaint register | `Product` | Workflow 3, workflow 7 A3 | Has a mandated destination: §803.52(f)(11)(iii) and §803.50(b)(3). Our `gaps[]` drafts that statement. |
| `reasonably_known_checklist` | `{contacted_user_facility, information_in_possession, analysis_testing_evaluation}` + evidence | `Product` | Directly models §803.50(b)(1)(i)–(iii) | FDA defines "reasonably known" as three specific sources; a checklist against them is the defensible version of "we tried". |
| `trend_link` | ref to trend/Art. 88 row | `Product` | Workflow 6 | Art. 88 trends and individual reports are different rows that must see each other. The trend form asks: "Have any of the trended events been submitted individually as reportable events under vigilance? If yes, please list how many and to which Competent Authority". |
| `*_status` companions on every computed field — `{computed \| human-overridden}` + `override_reason` | enum + text | `Product` | `DIAGRAMS.md` hard gates; workflow 3 | **Borrowed from a shipping product rather than invented.** Veeva Vault Safety ships `Device Report Type (Status)` — "whether populated automatically or manually overridden" — and `Expected (status)` with an `Override Reason` ([vendor](https://safety.veevavault.help/en/lr/01287/)). Pair it with §803.18(b)(1)(i)'s requirement to retain "all documentation of your deliberations and decision making processes", which FDA has cited a firm for failing (§6.8). Any field our agents compute — `clock_class`, `due_at`, `reportable`, IMDRF codes — needs this companion. |
| `reportability_decision_date` + `decision_due_at` + `decision_age_days` | dates + derived int | `Product` | Workflow 3 | **There is a clock on the not-reportable path too, and FDA enforces it.** A firm was cited because "Complaints were not reviewed and recorded as **unreportable for over 200 days after receipt**" ([DeVilbiss Healthcare, 11/23/2021](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/devilbiss-healthcare-llc-619182-11232021)). No regulation sets this period, so `decision_due_at` is an internal target — but a register whose only deadline is a submission deadline is structurally blind to this failure mode. |
| `unknown_reason[]` | per field: `{field, state: value \| explicitly-unknown \| not-yet-investigated, reason, attempts_ref}` | `Product` | Workflow 3, workflow 7 A3 | FDA refuses to read a blank as "unknown": "**If the fields are left blank, we cannot determine what information was unknown to you or what information was simply overlooked.**" Its own sentinel is the literal string `UNK`. A two-state null cannot satisfy this; three states can. |

#### Trend-report rows (Art. 88) — additional fields

From the EC trend report form (note its provenance caveat in §5):

| Field | Status | Source |
|---|---|---|
| `date_trend_identified` | `Mandated` | Trend form §7 "Date the trend was identified" |
| `trend_description` | `Mandated` | §7 "Description narrative for identified trend" |
| `observation_period` | `Mandated` | §7 "Time period of trend analysis"; Art. 88(1) requires the observation period be specified in the PMS plan |
| `trigger_level` | `Mandated` | §7 "Established trigger level"; Art. 88(1): "The significant increase shall be established in comparison to the foreseeable frequency or severity … during a specific period as specified in the technical documentation and product information" |
| `individually_reported_events_count` + `authorities` | `Mandated` | §7 "Have any of the trended events been submitted individually as reportable events under vigilance? If yes, please list how many and to which Competent Authority" |
| `serious_public_health_threat` | `Mandated` | §1 "Do these incidents / trend represent a serious public health threat?" |
| `trend_analysis_results`, `remedial/corrective/preventive/FSCA`, `implementation_schedule` | `Mandated` (final) | §9 |
| `expected_date_of_next_report` | `Mandated` | §8 |
| `serial_number_range`, `lot_batch_number_range` | `Mandated` | §6 — note **ranges**, where the MIR wants individual numbers |

The `trigger_level` field is the one to dwell on. Art. 88(1) makes the threshold a **commitment made in advance in the technical documentation**, and the form asks you to state it. So workflow 6 cannot invent a threshold at analysis time; it must read one. If the mock Asteria PMS plan does not contain a numeric threshold, the product's honest output is "no threshold is specified in the PMS plan" — and that, not a computed p-value, is the finding.

#### Periodic-summary rows

| Field | Status | Source |
|---|---|---|
| `psr_type` (incidents described in an FSN · common and well documented incidents) | `Mandated` (EU) | PSR form §7 |
| `psr_basis` (observed failure mode · root cause) | `Mandated` (EU) | PSR form §7 "Stage of PSR reporting based on" |
| `psr_agreed_period` (monthly · 2 · 3 · 6 · 12 months) | `Mandated` (EU) | PSR form §7 "Summary period agreed"; Art. 87(9) requires the CA to have "agreed with the manufacturer on the format, content and frequency" |
| `psr_counts` (date of PSR · new incidents this period · total via PSR · total resolved · total in progress) | `Mandated` (EU) | PSR form §7 table |
| `psr_geography_scope` (EEA+CH+TR · all PSR recipient NCAs · single Member State) | `Mandated` (EU) | PSR form §7 |
| `vmsr_bucket_key` (brand name × device model × MDR adverse event device problem code set × quarter) | `Mandated` (US) | VMSR guidance §V.C.1 |
| `vmsr_counts` (total reportable malfunctions; devices returned; labelled single-use; reprocessed and reused) | `Mandated` (US) | VMSR guidance §V.C.1 |

### 3.4 Lifecycle / status values

Two interleaved lifecycles: the **obligation** (row) and the **submission** (child). Conflating them is the commonest modelling error, because "submitted" is a property of a document and "closed" is a property of an obligation.

**Obligation states (the row):**

```text
05 Awareness recorded            clock running, determination not yet made
10 Assessment in progress        workflow 3 assembling evidence
20 Not reportable                TERMINAL. rationale + decider + date mandatory
                                   (MDSAP Task 14; MIR 4.2.b; Art. 87.11 explanatory statement)
25 Not reportable — notified     EU only: a MIR was submitted and then closed as
                                   'Final (Non-reportable incident)' (MDCG 2023-3 Q16)
30 Reportable — uncertain        Art. 87(7): report anyway. NOT a pending state.
35 Reportable                    determination made
40 Initial submitted             awaiting acknowledgement
45 Acknowledged                  regulator ACK received (§803.18(b)(1)(iii))
50 Follow-up due                 MIR 1.2(f) next-report date, or §803.56 new information
55 Follow-up submitted
60 Final submitted               MIR 'Final (Reportable incident)'
70 Closed                        TERMINAL
80 Superseded by PSR/VMSR        rolled into a summary bucket; the individual row persists
85 Reopened                      new information changed the determination
                                   (MDCG 2023-3 Q14 exceptional case — the clock restarts)
90 Not applicable — jurisdiction TERMINAL. device not marketed there; recorded, not deleted
99 Void / entered in error       TERMINAL
```

**Submission states (the child):** rather than invent these, take a shipped set. Veeva Vault Safety's Transmission lifecycle, verbatim ([vendor](https://safety.veevavault.help/en/lr/01266/)):

```text
Pending   Ready · Pending · Validation Error · Ready for Submission
Sending   Sending ICSR · Sending Attachments · Error
Sent      MDN Received · MDN Failure · ACK Warning · ACK Rejected
Accepted  ACK Accepted
```

with `ACK Warning` = "destination gateway could not load the transmission" and `ACK Rejected` = "destination gateway loaded the transmission but rejected it" — a distinction worth keeping, because the first is a transport failure and the second is a content rejection. `Validation Error` and `MDN Failure` are not theoretical: FDA's published ACK3 rejection reasons include "eMDR has already accepted a report with this report number", an invalid report number, an invalid adverse-event code, and an invalid US state code (§6.6). A submission that fails is part of the MDR event file under §803.18(b)(1)(ii)–(iii), not a retry to be forgotten.

Four points an auditor will press on:

1. **`20 Not reportable` must carry a rationale, a named decider and a date.** MDSAP Task 14 asks exactly this; §806.20(b)(4) shows FDA's template for the analogous negative ("reviewed and evaluated by a designated person").
2. **`30 Reportable — uncertain` is a compliant state, not an unresolved one.** Art. 87(7) requires reporting while uncertain. A UI that shows it as "incomplete" teaches the wrong behaviour.
3. **`85 Reopened` restarts the clock from a different date.** MDCG 2023-3 Q14: "the period of reporting begins on the date the manufacturer received the information that determined that the incident is reportable." The row must therefore hold *two* start dates and know which one the live clock uses.
4. **`90 Not applicable — jurisdiction` should be a recorded state.** "We did not report to Health Canada because PulseOne is not sold in Canada" is an answer; an absent row is not.

### 3.5 Links out

| From → to | Direction | Cardinality | Named in the standard? |
|---|---|---|---|
| Vigilance row → complaint | back | 1 (0 allowed for regulator-initiated) | **Yes**: §820.10(b)(3) ties Clause 8.2.3 to "complaints that meet the reporting criteria of part 803". |
| Vigilance row → MDR event file | out | 1 | **Yes**: §803.18(a); §803.18(e) allows it to live inside the complaint file if "prominently identif[ied]". |
| Vigilance row → sibling rows for the same event in other jurisdictions | lateral | 0..n | Convention, but MIR 1.3.1(c) makes the *same-manufacturer multi-device* cross-reference a mandated form field, which is the same idea one axis over. |
| Vigilance row → FSCA / advisory notice | out | 0..n | **Yes**: MDR Art. 87(1)(b) makes FSCA separately reportable; MIR 1.3.1(d) requires the three FSCA reference numbers; §820.10(b)(4) routes advisory notices to Part 806. |
| Vigilance row → Part 806 correction/removal report | out | 0..1 | **Yes, bidirectionally.** §803.52(f)(9) asks for the correction/removal report number inside the MDR; §806.10(f): "No report of correction or removal is required under this part, if a report of the correction or removal is required and has been submitted under parts 803 or 1004." CP 7382.850 tells investigators to check exactly this overlap. |
| Vigilance row → PSR / VMSR bucket | out | 0..1 | **Yes**: MIR 1.3.1(e) `psrId`; Art. 87(9); VMSR guidance. |
| Vigilance row → trend (Art. 88) row | lateral | 0..n | **Yes, in the form**: the trend form asks how many trended events were reported individually and to which CA. Art. 87(1)(a) excludes from individual reporting those expected side-effects "subject to trend reporting pursuant to Article 88" — a mutual-exclusion rule between row types. |
| Vigilance row → CAPA | out | 0..n | Convention. MIR 4.2(g) requires the *action description*, which is not the same as a CAPA link. |
| Vigilance row → risk file | out | 0..n | Effectively mandated on a final MIR via 4.2(d). |
| Vigilance row → NC record | out | 0..n | Convention. Present in real registers because the returned unit becomes §8.3.3 product. |
| Vigilance row → PMCF/PMPF investigation | out | 0..1 | `Mandated` where applicable: MIR 1.3.1(f) `pmcfpmpfQuestion` / `pmcfpmpfId`. |

The mutual exclusion between Art. 87 individual reports and Art. 88 trend reports deserves a line of its own, because it is a *rule the register has to enforce*, not just a link: Art. 87(1)(a) carves out "expected side-effects which are clearly documented in the product information and quantified in the technical documentation and are subject to trend reporting pursuant to Article 88". So an event can be excluded from individual reporting **only if** the product information documents it *and* the technical documentation quantifies it. Two document references, per excluded event. That is a checkable claim and a good demo.

### 3.6 Clock fields — the precise model

This is the product's centre, so it is worth being exact. Three separate things are routinely conflated: **what starts the clock**, **how the days are counted**, and **what the deadline means**.

#### 3.6.1 What "awareness" is

**US — and the critical asymmetry.** 21 CFR §803.3(b) defines "Become aware" as "that an employee of the entity required to report has acquired information that reasonably suggests a reportable adverse event has occurred." §803.3(b)(2) then splits it for manufacturers:

> "If you are a manufacturer, you are considered to have become aware of an event when **any of your employees** becomes aware of a reportable event that is required to be reported within 30 calendar days or that is required to be reported within 5 work days because we had requested reports in accordance with § 803.53(b). You are also considered to have become aware of an event when **any of your employees with management or supervisory responsibilities over persons with regulatory, scientific, or technical responsibilities, or whose duties relate to the collection and reporting of adverse events**, becomes aware, from any information, including any trend analysis, that a reportable MDR event or events necessitates remedial action to prevent an unreasonable risk of substantial harm to the public health."

Read that carefully, because it is the most important sentence in this note:

| Clock | Whose knowledge starts it |
|---|---|
| 30-calendar-day (§803.50) | **Any** employee |
| 5-work-day because FDA requested it (§803.53(b)) | **Any** employee |
| 5-work-day because remedial action is necessitated (§803.53(a)) | **Only** an employee with management/supervisory responsibility over regulatory/scientific/technical staff, or whose duties relate to collecting and reporting adverse events |

So a sales rep reading a customer email starts the 30-day clock. The same email does **not** start the §803.53(a) 5-day clock until it reaches someone in the second category. And §803.53(a) explicitly includes trend analysis as a trigger: "You may become aware of the need for remedial action from any information, including any trend analysis" — which wires `DIAGRAMS.md` workflow 6 directly into a 5-work-day statutory clock.

**The product consequence:** awareness is not one date. It is a set of (timestamp, person, person-class) facts, and *which* fact starts *which* clock depends on the person's class. Our `awareness_candidates[].employee_class` field is not a nicety; it is how the §803.53(a) clock can be defended at all.

**EU.** MDCG 2023-3 Rev.2 Q15:

> "the 'manufacturer awareness date' of the incident is the date when the first employee or representative of the manufacturer's organisation (i.e. any natural or legal person acting on behalf of the manufacturer) receives information regarding the potentially serious incident. If the handling of this information is performed by the authorised representative or if the manufacturer has outsourced its complaint and incident handling activities to another natural or legal person (e.g. a subcontractor), then reference to 'manufacturer's organisation' in the context of the awareness date will also apply to that organisation."

Broader than the US on one axis (it includes representatives and outsourced handlers, not just employees) and with no seniority carve-out. Q14 adds the "not after investigation" point explicitly: "The awareness date (day=0) refers to the date when the manufacturer is first made aware or receives information of the occurrence of the (potentially) serious incident, and **not after it has conducted its investigation**."

And the **second EU awareness date**, new in MIR v7.3.1 — field 1.2(d) "Manufacturer awareness date of reportability", whose helptext reads: "In this field, the manufacturer should insert the date in which it received the information that determined that the incident is reportable and thus met the criteria of a incident." MDCG 2023-3 Q15 requires the difference between 1.2.c and 1.2.d to be explained in MIR section 5.

| Which EU date the clock runs from | When |
|---|---|
| `awareness_date_incident` (1.2.c) | Normal case |
| `awareness_date_reportability` (1.2.d) | **Only** the exceptional case where the manufacturer initially determined the incident was not reportable and later received new information changing that. MDCG Q14: "the period of reporting begins on the date the manufacturer received the information that determined that the incident is reportable." |

#### 3.6.2 The clocks themselves, quoted

**United States — 21 CFR Part 803** (Part 803 was *not* folded into the QMSR and remains a separate regulation).

| Clock | Text | Counting |
|---|---|---|
| 30-day | §803.50(a): report "no later than **30 calendar days** after the day that you receive or otherwise become aware of information, from any source, that reasonably suggests that a device that you market: (1) May have caused or contributed to a death or serious injury or (2) Has malfunctioned and this device or a similar device that you market would be likely to cause or contribute to a death or serious injury, if the malfunction were to recur." | Calendar days, counted **after the day** of awareness |
| 5-day | §803.53: "no later than **5 work days** after the day that you become aware that: (a) An MDR reportable event necessitates remedial action to prevent an unreasonable risk of substantial harm to the public health. You may become aware of the need for remedial action from any information, including any trend analysis or (b) We have made a written request for the submission of a 5-day report." | **Work days.** §803.3(y): "Work day means Monday through Friday, except Federal holidays." |
| Supplemental | §803.56: "you must submit the supplemental information to us within **30 calendar days** of the day that you receive this information." | Calendar days from receipt of the new information — a *new* clock per new fact |
| VMSR quarterly | Malfunctions you become aware of Jan 1–Mar 31 → due **Apr 30**; Apr 1–Jun 30 → **Jul 31**; Jul 1–Sep 30 → **Oct 31**; Oct 1–Dec 31 → **Jan 31** | Fixed calendar deadline, not an offset from awareness |
| Part 806 correction/removal | §806.10(b): "within **10-working days** of initiating such correction or removal" | Working days, and the trigger is **initiation of the action**, not awareness — a structurally different clock |

**European Union — MDR 2017/745 Art. 87**, quoted:

| Clock | Text |
|---|---|
| 15 days | Art. 87(3): "Manufacturers shall report any serious incident as referred to in point (a) of paragraph 1 immediately after they have established the causal relationship between that incident and their device or that such causal relationship is reasonably possible and not later than **15 days** after they become aware of the incident." |
| 2 days | Art. 87(4): "Notwithstanding paragraph 3, in the event of a serious public health threat the report referred to in paragraph 1 shall be provided immediately, and not later than **2 days** after the manufacturer becomes aware of that threat." |
| 10 days | Art. 87(5): "Notwithstanding paragraph 3, in the event of death or an unanticipated serious deterioration in a person's state of health the report shall be provided immediately after the manufacturer has established or as soon as it suspects a causal relationship between the device and the serious incident but not later than **10 days** after the date on which the manufacturer becomes aware of the serious incident." |
| FSCA | Art. 87(8): "Except in cases of urgency in which the manufacturer needs to undertake field safety corrective action immediately, the manufacturer shall, without undue delay, report the field safety corrective action referred to in point (b) of paragraph 1 **in advance of the field safety corrective action being undertaken**." — a deadline defined by a future event, not a date arithmetic |
| Trend (Art. 88) | **No deadline is stated.** Art. 88(1) requires reporting of a statistically significant increase but sets no period. The clock is the *observation period and methodology specified in the PMS plan*, which Art. 88(1) requires the manufacturer to define. This is a real asymmetry: our UI must not display an Art. 88 due date as if the regulation set one. |

#### 3.6.3 How EU days are counted — the part everybody gets wrong

MDCG 2023-3 Rev.2 Q14, with its footnoted basis in Regulation (EEC, Euratom) No 1182/71:

> "The timelines for reporting serious incidents must be considered as calendar days, meaning the reporting periods include weekdays, public holidays, Saturdays and Sundays."
>
> "As a general rule, the reporting period begins on the day after the awareness date of a potentially serious incident at 00:00:01 AM. The awareness date (day=0) refers to the date when the manufacturer is first made aware or receives information of the occurrence of the (potentially) serious incident, and not after it has conducted its investigation."
>
> "In both situations i.e., the general rule and the exceptional case, the period ends on the 15th, 2nd or 10th day thereafter (more specifically at 11:59:59 PM). However, if this (last) day is a public holiday, Saturday or Sunday the deadline is moved to the following working day automatically."

Plus, from the cited Regulation 1182/71 Art. 3(4): "Any period of two days or more shall include at least two working days" — which bites hardest on the 2-day public-health-threat clock.

And when several clocks apply, Q14's worked example ends: "In conclusion, it is the **earliest date of reporting** which should be considered."

**The computable rule, therefore:**

```text
EU due date:
  day 0        = awareness date (incident, or reportability in the exceptional case)
  period start = day 0 + 1, at 00:00:01 local
  nominal due  = day 0 + N (N = 2, 10 or 15), at 23:59:59 local
  if nominal due is Sat, Sun or a public holiday in the relevant Member State:
      roll forward to the next working day
  if N >= 2 and the period contains fewer than two working days:
      extend so that it contains at least two working days
  if more than one clock applies:
      due = MIN(all applicable due dates)
```

Four things this rule needs that a naive implementation will not have:

1. **A per-Member-State public-holiday calendar**, because the roll-forward is national. The due date for the same event differs between Germany and Ireland.
2. **A local time zone and a local date**, because the period starts at 00:00:01 and ends at 23:59:59 *local*.
3. **A rule version**, because MDCG guidance is revised (this is Rev.2) and a due date computed in 2024 under Rev.1 must remain explainable.
4. **Recomputation on new information**, because §803.56, MDCG Q14's exceptional case, and the Art. 87(5) escalation in MDCG's own variant example (the patient dies two days later and the 15-day clock becomes a 10-day clock ending *earlier*) all move the deadline after the fact.

That last one is worth stating plainly: **a deadline in this register can move earlier.** Any UI that treats a due date as fixed once computed is wrong.

#### 3.6.4 The clock fields, as a table

| Field | Type | Status | Source |
|---|---|---|---|
| `awareness_date_incident` | date | `Mandated` | MIR 1.2(c); MDCG Q15 |
| `awareness_date_reportability` | date | `Mandated` (EU) | MIR 1.2(d); MDCG Q14/Q15 |
| `awareness_timestamp` + `tz` | timestamp | `Product` (workflow 3) | Needed because EU periods start 00:00:01 local |
| `awareness_basis` | enum: complaint received · ticket created · regulator notification (Art. 87(11)) · literature · trend analysis (§803.53(a)) · distributor report · service finding | `Product` (workflow 3) | §803.53(a) names trend analysis; Art. 87(11) names CA notification |
| `awareness_person` + `employee_class` | person + enum (any employee · management/supervisory over reg/sci/tech · AE-collection duties · authorised representative · outsourced handler) | `Product` (workflow 3) | §803.3(b)(2) US asymmetry; MDCG Q15 EU breadth |
| `clock_class` | enum per jurisdiction | `Mandated` | MIR 1.2(g); §803.50/§803.53 |
| `jurisdiction` + `holiday_calendar` | enum + calendar id | `Product` | MDCG Q14 roll-forward is national |
| `period_start_at` / `due_at` | timestamps | `Product` (computed) | Derived from the quoted rules |
| `due_at_history[]` | `{value, computed_at, rule_version, reason_for_change}` | `Product` | Deadlines move; §803.56, MDCG Q14 |
| `date_submitted` | date | `Mandated` | MIR 1.2(a); §803.12(a) |
| `acknowledged_at` | date | `Mandated` in effect (US) | §803.18(b)(1)(iii) |
| `next_report_expected_date` | date | `Mandated` (EU) | MIR 1.2(f) |
| `observation_period_start` / `_end` | dates | `Mandated` (Art. 88 rows) | Trend form §7; Art. 88(1) |
| `reportability_decision_date` | date | `Convention`, enforced | Not named in any regulation, but a firm was cited for taking "over 200 days after receipt" to record complaints as unreportable ([DeVilbiss](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/devilbiss-healthcare-llc-619182-11232021)). Distinct from both awareness and submission; the only date that can evidence a timely *negative* decision. |
| `decision_due_at` / `decision_age_days` | date / derived int | `Product` | Internal target for the assessment itself, so the not-reportable path has a visible clock. |
| `event_type_history[]` | `{value, changed_at, basis}` | `Product`, with a mandated driver | FDA guidance: "If your initial report was submitted as a malfunction and you learn a patient died or suffered a serious injury, then your supplemental report should **change the event type** to death or serious injury." Changing the event type can change the clock class and move the deadline earlier. |
| `late_flag` + `late_explanation` | bool + text | `Convention`, with a mandated cousin | §803.50(b)(3) and §803.52(f)(11)(iii) require explaining incomplete information; lateness itself is a finding, not a form field. MDCG Q14: "A delay in submitting an initial report e.g. due to incomplete information provided by the healthcare facility, end user or other relevant parties, is **not deemed justified**." |

That last quotation is the single best line to put in front of a customer: the EU explicitly refuses "we were waiting for the hospital to reply" as an excuse, and Art. 87(6) gives the alternative — "the manufacturer may submit an initial report that is incomplete followed up by a complete report."

### 3.7 What a real export looks like

See §6 for verbatim evidence. The shapes to support:

- An **Excel tracker**, usually a single sheet per year with a wide right-hand side of per-jurisdiction columns, because the one-row-per-event habit dies hard. Expect merged header cells and a `Due Date` column that is a formula against `Awareness Date`, frozen at whatever the formula said when the row was typed.
- **Per-report artefacts**: a PDF of the submitted MIR (an XFA Adobe form — the official MIR is an XFA PDF, which does not yield text to ordinary extraction, a genuinely useful ingestion hazard to include in the mock data), the eMDR XML or the eSubmitter package, the FDA acknowledgement files.
- The **MAUDE public extract**, which is the register as the *regulator* publishes it and therefore the most citable set of real-world column names for this domain. `MOCK-DATA.md`'s "External" source family should include a MAUDE-shaped file for similar devices.
- A **Word or PDF "Vigilance Log"** for audit, typically with a column for "Rationale if not reported" that is three words wide and a paragraph long.

### 3.8 Fields that are routinely incomplete or disagreed-on

| Field | How it fails | Why / evidence |
|---|---|---|
| `awareness_date_*` | Disputed between the mailbox timestamp, the ticket creation time, and the complaint open date — and sometimes backdated to make a deadline work | The product's reason to exist. §803.3(b)(2) makes *any employee's* knowledge count for the 30-day clock, so the earliest defensible date is usually earlier than the one in the register. |
| `date_of_incident` | Unknown; the regulator's own form tells you to enter a **range** | MIR 1.2(b): "if incident date is unknown, please enter a date range when you think the incident occurred." |
| `patient_*` (name/identifier, age, gender, weight, height) | Withheld by the hospital or the complainant | §803.52(a)(1) says "Patient name **or other identifier**" for this reason; MIR 3.3 fields are routinely `unknown`. |
| `serial_no` / `lot_no` / `udi_*` | Missing or partial | For PulsePatch the pouch is discarded; for PulseOne the nurse reads the asset sticker, not the UDI. |
| `device_evaluation_summary` | Device never returned | §803.52(f)(3) converts this into a mandated explanation; real registers leave it blank. |
| `imdrf_*` codes | Uncoded | The MIR has explicit `imdrfCodeMissing`, `imdrfMissingCodeHealthEffect`, `imdrfMissingCodeCauseInvestigation`, `imdrfMissingComponentCodes` fields — **the regulator built a field for "we could not code this"**. |
| `nca_report_number` | Literally `Unknown` | MIR 1.1(c) instructs: "If no reference number is provided by the NCA, please add 'Unknown' in the follow-up and final reports." |
| `eudamed_reference` | Blank | VGL module not live (§1 fact 4). |
| `similar_incidents_counts` (the 24-cell matrix) | Partially filled, or filled with numbers that contradict the PMS spreadsheet | Needs shipment, installed-base and incident data joined across four periods and three geographies. `MOCK-DATA.md`: "Snapshot dates differ between sources", "Calculation logic embedded in spreadsheets". |
| `denominator_basis` | Chosen inconsistently between reports, or chosen in a cumulative-prohibited category and then used cumulatively | The MIR helptext's split list exists because this is done wrong. |
| `trigger_level` (Art. 88) | Not specified anywhere in the PMS plan | Art. 88(1) requires it in the technical documentation. Its absence is the finding, and the mock Asteria PMS plan should be realistically vague about it — not conveniently precise. |
| `causality_assessment` | The three EU thresholds (established / reasonably possible / suspected) get collapsed to one yes/no | Art. 87(3) and 87(5) use different thresholds for different clocks. |
| `reportable` | Two reviewers disagree; the determination changes after submission | Art. 87(7) (report while uncertain) and MDCG Q16 (`Final (Non-reportable incident)`) both exist because this is normal. |
| `late_flag` | Quietly absent from the register even when the dates show lateness | The `days_late` column computed from stored dates is the thing nobody wants to add. |
| `reportability_decision_date` | Absent, or months after receipt | FDA cited a firm because "Complaints were not reviewed and recorded as unreportable for **over 200 days after receipt**". The negative decision being *late* is independently citable (§6.8). |
| `clock_class` / `patient_outcome` | Correct at submission, wrong later | FDA expects the supplemental report to "change the event type to death or serious injury" when the outcome worsens. Registers store the original and never revisit. |
| jurisdiction coverage | Rows simply missing for markets nobody thought about | An absent row is indistinguishable from "assessed and not applicable" unless state `90` exists. |
| any field | **Blank, where FDA requires an explicit `UNK` plus a reason** | "If the fields are left blank, we cannot determine what information was unknown to you or what information was simply overlooked." Blanks are the normal real-world state and the mandated-against one simultaneously — ideal mock-data material. |

---

## 4. Four decisions the other register families must agree with us on

Stated as decisions so the other notes can accept or contest them explicitly.

1. **Negative decisions are rows, not absences, and they carry four fields: decision, rationale, named decider, date.** The pattern is consistent across every instrument we found — §820.35(a) (no-investigation justification), §806.20(b)(4) ("reviewed and evaluated by a designated person"), MDSAP Task 14 ("documented rationale") and Task 15 ("include records where a decision was made not to issue an advisory notice"), MIR 4.2(b), ANVISA Art. 121 ("the name of the persons responsible for the decision"). Every register in the system should use the same four-field negative-decision shape, the same terminal-state convention, and never a soft delete.

2. **Awareness is a set, not a date; and a date is sometimes a range.** `awareness_candidates[]` with one selected value and a recorded reason, plus `{from, to}` for uncertain dates because the regulator's own form asks for a range. If the NC, CAPA and audit registers model dates as single scalars, the complaint and vigilance registers cannot reconcile with them.

3. **Every field has three empty states, not one: *value*, *explicitly unknown with a reason*, and *not yet investigated*.** This is not a modelling preference — FDA refuses to read a blank as unknown: "If the fields are left blank, we cannot determine what information was unknown to you or what information was simply overlooked. By completing each requested data element, you assure us that all elements were considered and reviewed." FDA's own sentinel is the literal string `UNK`; the EU ships dedicated "codes missing" fields (`imdrfCodeMissing`, `imdrfMissingComponentCodes`) and instructs writing `Unknown` into the NCA reference field. If the NC, CAPA and audit registers use nullable scalars, every cross-register completeness report will be wrong in the same direction.

4. **Anything an agent computes carries a `{computed | human-overridden}` status and an override reason.** Taken from a shipping product — Veeva's `Device Report Type (Status)` and `Expected (status)` with `Override Reason` — and backed by §803.18(b)(1)(i), which FDA has cited a firm for failing. This is how `DIAGRAMS.md`'s colour rule ("a green node never creates an approved record") becomes a column rather than a convention.

Three more, lower-stakes but worth naming: **correction and corrective action are different link types** (the QMSR's own §820.35(a)(6) wording now says "Any correction or corrective action taken"); **every external identifier is `{value, assigned_by, assigned_on, status}`** because one of them is literally the string `Unknown`; and **the denominator vocabulary is the MIR's**, not ours.

---

## 5. Where sources genuinely disagree

| Disagreement | Sources | Our position |
|---|---|---|
| **5-day clock: work days or calendar days?** | 21 CFR §803.53: "5 **work** days", with §803.3(y) defining work day as "Monday through Friday, except Federal holidays". FDA's own VMSR guidance: "the 5-**work** day timeframe under 21 CFR 803.53". But **MDSAP AU P0002.010 Annex 3** says for the United States: "5 **calendar** days if FDA has issued a 5-day notice". | The CFR governs; MDSAP's Annex 3 is wrong or loosely worded. Implement work days. Flagging this matters because MDSAP is the document many manufacturers actually read. |
| **Is there a current MDR-era EU trend report form?** | The EC PMSV reporting-forms page offers a trend report form and a PSR form; both documents are headed "Medical Devices Vigilance System (MEDDEV 2.12/1 rev 7)" and carry MDD-era device classes (AIMD, MDD Class III…). The MIR was rewritten for MDR/IVDR; these two were not. | There is **no MDR-native trend or PSR form**. Art. 88 reporting today uses an MDD-era template. Model the trend row on the form's fields but do not claim the form is MDR-current, and expect it to change. |
| **Where does the reportability determination live?** | §803.18(e) permits the MDR event file inside the complaint file. MDSAP Task 14 and CP 7382.850 treat complaint handling and MDR as separate. CP 7382.850 maps Clause 8.2.3 *into* the Complaint Handling element, while MDR is a separate OAFR. | Separate rows in the vigilance register, with a mandatory link back to the complaint and a `prominently_identified_as_mdr` flag to satisfy §803.18(e) if a customer keeps them co-located. Multi-jurisdiction makes any single-field-on-the-complaint design untenable. |
| **Does the complaint register hold non-complaints?** | ISO 13485 separates §8.2.1 Feedback from §8.2.2 Complaint handling, and CP 7382.850 makes them separate inspection elements. Most commercial eQMS products, by contrast, put "not a complaint" as a closure reason on a complaint record. | Support both: a `90 Not a complaint` terminal state *and* a pointer to the feedback record. Do not silently discard the distinction, because an auditor sampling "complaints" should not be handed a pile of non-complaints. |
| **`date_received` vs awareness date** | §820.35(a)(2) mandates "The date the complaint was received". §803.3(b)(2) makes the 30-day clock run from when any employee became aware. These are frequently different dates and no source reconciles them. Veeva ships them as two fields (`Receipt Date`, `Manufacturer Reportable Awareness Date`); a real manufacturer protocol collapses them into one field labelled "Date the complaint was received/recorded in the EDC System (Date of Sponsor Awareness)". | Store both, never derive one from the other, and show the gap. The gap between them is a product feature. |
| **Which §803.3 paragraph defines the manufacturer report number?** | This note cites **§803.3(m)**. FDA's own published variance letter cites **§803.3(o)**. | **Resolved in favour of (m).** I checked the paragraph lettering directly in both the 2024 annual CFR XML and the current eCFR rendering: (m) is *Manufacturer or importer report number* and (o) is *MDR reportable event*. FDA's variance letter uses stale lettering from an earlier revision. Cite (m). |
| **How many eMDR acknowledgements does FDA send?** | FDA ESG NextGen documents ACK1, ACK2, and "**ACK3 & ACK4**" (Center-dependent). FDA's eMDR troubleshooting page refers to "ACK3 or ACK4". Every vendor source says three. | Model four slots, or a single `{ack_level, ack_status}` pair. Do not assert "three acknowledgements" as primary fact — it is industry shorthand. |
| **Can more than one `H1 Type of Reportable Event` box be checked?** | 3500A form instructions: "Check **all** the appropriate boxes that apply to this report." FDA MDR guidance §5.1.2(9) lists as a recurring defect: "No box is marked, or more than one box is marked, in Block H-1 … **only one of these boxes should be marked**." | A direct contradiction **inside FDA's own documentation**. Allow multi-select in the data model, single-select in the submission renderer, and record which interpretation was applied. Worth raising with a customer rather than silently picking. |
| **MAUDE field counts and column casing** | FDA's MDR Data Files page says the MDRFOI file has "82 fields" and then enumerates ~85. The same schema appears as `Title Case With Spaces` (FDA), `lower_snake_case` (openFDA) and `Mixed_Snake_Case` (community import scripts). No FDA source uses `SCREAMING_SNAKE_CASE`. | Treat the enumerated list as authoritative over the count, and test ingestion against all three casings. Do not assume uppercase column names exist. |
| **Merged vs per-jurisdiction reportability assessment** | Johner Institute: "Do not try to combine the requirements of different countries." FDA cited a firm under §803.17(a)(2) for exactly that combination. Much vendor marketing promotes unified multi-country decision trees. | The sharpest practice-versus-enforcement tension in this research. Per-jurisdiction rows (§3.1). A single cross-jurisdiction verdict column is a citable defect, not a simplification. |

---

## 6. The convention layer — real templates, real column headers, real export shapes

This section supplies the `Convention` citations and, more importantly for `MOCK-DATA.md`, **verbatim real-world field wording**. Everything quoted below is from a source we can cite; where a plausible header could not be verified, it says so rather than guessing.

### 6.1 Complaint register — verbatim field wording from real artefacts

**FDA's own pre-QMSR baseline.** CDRH's published *Complaint Files* training deck lists the §820.198(e) record content as, verbatim: "Device name", "Date complaint received", "Unique Device Identifier (UDI), Universal Product Code (UPC), and other device identification(s) (e.g., control/batch/lot number(s))", "Name, address, and phone number of complainant", "Nature/details of the complaint", "**Results and dates of investigation**", "Corrective action taken", "Reply/response to complainant". The same deck uses the in-house vocabulary "Other ('non complaints')", "Investigate ('investigable')", and splits outcomes into "Handle within Complaint Files System" vs "Refer to Corrective and Prevent Action Subsystem". ([FDA CDRH deck](https://www.fda.gov/files/about%20fda/published/Complaint-Files---Printable-Slides.pdf))

Two deltas between that deck and the QMSR text are worth recording, because they change what is `Mandated` today:

| Item | Old §820.198 | QMSR §820.35(a) |
|---|---|---|
| "Results **and dates** of investigation" | Explicit record-content item | **Gone as a named item.** §820.35(a) requires records of "the review, evaluation, and investigation" but no longer enumerates results-and-dates as a field. Keep the fields — every real register has them — but they are now `Convention`, not `Mandated`. |
| Name of the individual responsible for the decision **not** to investigate | §820.198(b) required it by name | §820.35(a) requires only "records documenting justification for not performing such investigation" — **the named individual is no longer US-mandated.** ([consultant commentary](https://redhenadmin.com/2026/03/22/your-complaint-files-just-got-a-new-address-and-a-udi-requirement/)) |
| MDR-reportable complaints held separately | §820.198(d): "maintained in a separate portion of the complaint files or otherwise clearly identified" | Moved to §803.18(e): maintain MDR event files inside the complaint file only "if you prominently identify these records as MDR reportable events". Same requirement, different home. |

The second delta is why `classified_by` is marked `Convention → Mandated in BR` in §2.3 rather than `Mandated`: the US dropped it, Brazil kept it (ANVISA RDC 665/2022 Art. 121 requires "the reason that the investigation was not performed and the name of the persons responsible for the decision"), so carry it.

**A real medical-device complaint SOP, with its numbered field list.** Argos Global *Complaint Processing, SOP-0003 Rev AE* enumerates 38 "Event Record Requirements" grouped as `Reporter Information` / `Patient Information` / `Event Information` / `Device Information` / `Other` / `Investigation Information`. The wording worth stealing:

> "1. Date of report by the reporter;" · "2. **Date reporter became aware of this event**;" · "3. The method through which the information from the reporter was communicated (e.g. telephone, email, survey, service report, etc);" · "8. Patient name **or other identifier**;" · "24. Any device identification(s) and control number(s) available (e.g. model number, part number, catalog number, serial number, lot number, batch number, or other identifying number);" · "26. Whether the use of the device was initial, reuse, or **unknown**;" · "27. Whether the device is available for evaluation;" · "36. A summary of the device evaluation, the person who performed the evaluation, and the date of the evaluation… If an evaluation was not performed, an explanation as to why an evaluation was not performed is required;"

Two structural lessons from this document. First, **its noun is "event record", not "complaint record"** — the record exists *before* the complaint / non-complaint decision, which is exactly the §8.2.1→§8.2.2 split and a good naming convention for our resolved-event layer. Second, it operationalises "reasonably known" as a documented **good-faith effort**: "At least three attempts will be made to obtain required information. At least one of the attempts must be a written communication. All attempts to collect additional information will be documented." That is a concrete, citable implementation of §803.50(b) and a strong candidate for a `Product` field (`information_requests[]`, workflow 8). ([Argos Global SOP-0003 Rev AE](https://medicaldeviceacademy.com/wp-content/uploads/Argos-Global-Complaint-Processing-SOP-0003-RevAE.pdf), consultant-hosted real SOP)

**A real manufacturer's intake field list.** J&J Vision Care protocol CR-5856 §4.11 requires, for each product quality complaint, verbatim: "Date the complaint was received/recorded in the EDC System (**Date of Sponsor Awareness**)", "Who received the complaint", "Lot number(s)", "Indication of who first observed complaint (site personnel or subject)", "Any related AE number if applicable", "Detailed complaint description", "**Confirmation of product availability for return (and tracking information, if available), or rationale if product is not available for return**". ([protocol PDF on clinicaltrials.gov](https://cdn.clinicaltrials.gov/large-docs/23/NCT02886923/Prot_SAP_000.pdf), company document on a .gov domain)

Note what that first field does: it **collapses date-received and date-of-awareness into one field and says so in the label**. That is the single most realistic bad-practice pattern we could put in Asteria's QMS — and §2.6 / §3.6 explain why it is a problem.

**A published complaint-control log with literal column headers.** Not a device register, but a genuine government complaint-register artefact whose column grammar is the convention we are modelling — California DSS form LIC 957, *COMPLAINT CONTROL LOG*:

> `CONTROL NUMBER` | `FACILITY NAME` | `FACILITY NUMBER` | `COMPLAINT CODE*` | `DATE RECEIVED` | `INVESTIGATOR /EVALUATOR NUMBER` | `DATE TO RIS/AS` | `DATE VISIT DUE` | `DATE VISIT MADE` | `RESOLUTION` (sub-columns `S` `I` `U`) | `REQUIRES FURTHER INVESTIGATION` | `DATE RESOLVED/ CLOSED`

with the instruction "The **Resolution Codes** are **(S) Substantiated, (I) Inconclusive** or **(U) Unfounded**". Three transferable patterns: a control number distinct from the intake report number; a one-letter resolution code set; and a boolean escape hatch (`REQUIRES FURTHER INVESTIGATION`) next to it. ([CDSS LIC 957](https://www.cdss.ca.gov/cdssweb/entres/forms/English/LIC957.PDF))

A device-adjacent one, from a Medicare contractor — *MEDICARE BENEFICIARY COMPLAINT LOG*: `Date of receipt of complaint:` / `Patient's name:` / `Patient's address:` / `Patient's telephone number:` / `Description of complaint:` / `Action taken to resolve the complaint:` / `Signature of representative` / `Date`. ([Palmetto GBA](https://dominoapps.palmettogba.com/palmetto/providers.nsf/files/Model%20Complaint%20Log%20Sheet.pdf/$File/Model%20Complaint%20Log%20Sheet.pdf))

**Commercial eQMS field names.** Veeva Vault QMS publishes its object fields, and they are a useful corrective to the idea that vendors use regulatory wording. Verbatim field labels and API names: **`Awareness Date` (`awareness_date__v`)** — note the vendor names it awareness, not date-received, and drives the reportability due date from it — plus `Contact Method`, `Latest Response Details`, `Followup Evaluation Type`, `Do Not Promote`, `Complaint Intake Follow-Ups`, `Send Email on Create?`, and on the reportability side `Is Reportable?`, `Type of Assessment` (values `Initial Assessment`, `Reassessment`), `Severity Outcome`, `Domestic Incidents`, `Foreign Incidents`, `Latest Info Available`, `Days for Initial Response`, `Days for Initial Report Due Date`. ([Veeva — Configuring Complaint Intake](https://quality.veevavault.help/en/lr/928400/), [Veeva — MedTech Complaint AE Reporting](https://quality.veevavault.help/en/gr/65833/), vendor)

`Days for Initial Report Due Date` is worth noting: a mainstream eQMS stores the clock as a **number of days on a configuration record** and derives the due date. That is the design our `clock_instances[].rule_version` is meant to improve on, because a stored integer cannot express "calendar days, day+1, roll forward off German public holidays, minimum two working days".

**Document numbering, as actually practised.** The register and the record are *separate controlled documents with adjacent numbers*, and the numbering is of the template, not the record: Medical Device Academy ships "**LST-011 v0.1, Complaint Register (i.e., Complaint Log in Excel format)**" and "**FRM-020 v0.3, Complaint Record (Protected Form in Word format)**" under "SYS-018 Customer Feedback and Complaint Handling Procedure" ([consultant](https://medicaldeviceacademy.com/complaint-handling-procedure/)); Advisera ships "Registry of Customer Complaints", document number **09.2_Appendix_2**, a 1-page MS Word table ([consultant](https://advisera.com/13485academy/documentation/registry-of-customer-complaints-iso-13485-2016/)); a practitioner posts `F-QA-008 Customer Complaint-Concern.docx` and `F-QA-009 Customer Complaint-Concern Log.docx` ([Elsmar](https://elsmar.com/elsmarqualityforum/threads/customer-complaint-form-or-log.3834/)). Asteria's `document-register.xlsx` should look like this: `SYS-0xx` procedures, `FRM-0xx` forms, `LST-0xx` registers.

**Complaint record numbering, verified formats.**

| Format | Source |
|---|---|
| `RDTC-XX-001` — "where RDTC = R&D Technical Complaint, XX = last two digits of the current year, 001 = sequential numbering starting with 001" | [J&J Vision Care protocol CR-5856](https://cdn.clinicaltrials.gov/large-docs/23/NCT02886923/Prot_SAP_000.pdf) (company doc) |
| `Sr. No. / Year`, e.g. `01/2011`, reset on 31 December | [Pharmaguideline market-complaint SOP](https://www.pharmaguideline.com/2011/08/sop-for-handling-of-market-complaints.html) (consultant, pharma-adjacent) |
| `NC12-001` / `OFI12-001` — two-digit year prefix, 3-digit sequence, new log each year | [Elsmar numbering thread](https://elsmar.com/elsmarqualityforum/threads/corrective-action-numbering-and-indexing-best-practice.52929/) (practitioner) |
| Anti-pattern explicitly argued against: `CARIA021512` (type + source + MMDDYY) — "the more data you try to encode in your 'smart' numbers, the more likely you'll run into a situation that doesn't fit" | same thread |

**Honest gap.** I could not verify a published source using `CMP-2025-001`, `C-25-0142` or `CPL-0001`, nor the abbreviated headers `Cmplt #`, `Date Rec'd`, `MDR Y/N`, `Investigation Req'd (Y/N)`, `Days Open`, `CAPA#`. They are plausible and consistent with every verified artefact above, but they are **unverified** and should be generated for Asteria as *our* invented company convention rather than cited as industry fact. The paid template bundles (Greenlight Guru, Rook QS, Medical Device Academy LST-011, Advisera 09.2_Appendix_2) all gate the actual sheet behind a download form and describe contents in prose only.

### 6.2 Complaint lifecycle values, as real systems name them

| Source | Verbatim states / values | Label |
|---|---|---|
| Veeva Vault QMS — Complaint Intake | `Pending Complaints`, `Follow-Up Received`; the intake is "promoted" into Complaint records via the **`Promote to Complaint`** action; a `Do Not Promote` Yes/No sits on the Reported Product | vendor |
| Veeva Vault QMS — Duplicate Check | the reviewer's verdict picklist is literally **`is a Duplicate of`** / **`is a Follow-up of`**, with a configurable "Destination Lifecycle State" such as `Duplicate` or `Follow-Up`, and an admin setting "Do not transition complaints in the following lifecycle states" | vendor |
| Veeva Vault QMS — Complaint / AE Report | `Initiated`, `Closed`, `Draft`, `Completed`, `Cancelled`, plus state types `Sending` and **`XML Generation Failed`** | vendor |
| Argos Global SOP-0003 | two orthogonal axes: events are "either **non-complaints** or **complaints**" (with a three-criteria test, failing any one → non-complaint), and complaints are "either **non-reportable complaints** or **reportable complaints**" | consultant |
| FDA CDRH deck | `Other ('non complaints')`, `Investigate ('investigable')`, `Other ('non complaints,' 'similar' complaint)` | primary |
| Oriel STAT A MATRIX / ELIQUENT | closure **levels** by investigation depth: `Level I` (initial investigation with documented closure rationale), `Level II` (probable cause), `Level III` (root cause analysis, potential CAPA link); and four feedback categories that are *not* complaints: "Product information inquiries", "Preventive maintenance service calls", "Cosmetic defects", "Shipping errors" | consultant |
| CDSS LIC 957 | `(S) Substantiated` / `(I) Inconclusive` / `(U) Unfounded` + `Requires Further Investigation` | primary |
| MDSAP QMS P0011 | the tracking instrument is a **"Concern Resolution Report (CRR) Log"**; complainant name and affiliation are required **"(if not confidential or anonymous)"**; complaints may be flagged `confidential` or `anonymous` | primary |

Three things this changes in §2.4. **(a)** Veeva's two-axis model (complaint / non-complaint, then reportable / non-reportable) is cleaner than one flat state machine and matches our two-register split — adopt it. **(b)** Veeva's duplicate verdict distinguishes `is a Duplicate of` from `is a Follow-up of`; our `duplicate_of_complaint_id` should be a typed link with at least those two values, because "the same person wrote again" and "a different person reported the same event" are different facts. **(c)** `XML Generation Failed` is a real, shipped state — submission failure is a first-class state, not an exception, confirming §3.4's submission lifecycle.

And one genuinely useful non-finding, from a consultant FAQ: **"there is no FDA regulation that defines when a complaint is considered 'closed'"** ([ComplianceOnline](https://www.complianceonline.com/resources/30-frequently-asked-questions-about-medical-device-complaint-and-reporting.html)). Closure criteria are entirely company convention, which is precisely why `closure_rationale` matters more than `status`. Also useful: ISO 13485 Expert's list of acceptable no-investigation rationales — "The complaint is a duplicate of an already-open investigation", "The complaint does not allege a deficiency in the device", "The complaint cannot be substantiated and no safety signal exists" — with the warning that a bare "not a complaint" closure "without documented evaluation criteria applied to specific facts" is insufficient ([consultant](https://iso13485expert.com/blog/complaint-handling-iso-13485-intake-to-regulatory-reporting/)).

### 6.3 What a real complaint export actually is

- **Excel is the default at Asteria's scale, and the industry ships it that way.** The mainstream consultant register is literally "Complaint Log in **Excel format**" paired with a Word protected form for the record ([Medical Device Academy](https://medicaldeviceacademy.com/complaint-handling-procedure/)). Advisera's equivalent is a **1-page MS Word table** ([Advisera](https://advisera.com/13485academy/documentation/registry-of-customer-complaints-iso-13485-2016/)). So the realistic Asteria artefact pair is `LST-011 Complaint Register.xlsx` + `qms/complaints/FRM-020-CMP-2026-0147.docx`.
- **The register is an index over files that live elsewhere.** FDA's inspection guide, verbatim: "Typically, manufacturers will keep complaints in a customer file, product returns/credit file, service file, warranty file, medical file, or legal file", with the completeness rule "**The complaint file(s) must contain all complaints including those open or still under investigation**" and the instruction "Determine if oral or telephone complaints are documented." ([FDA inspection guide](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-guides/page-4)) That sentence is the best available justification for our `source_system_refs[]` field: the complaint file is *already*, in FDA's own description, a set of pointers into six other systems.
- **Spreadsheet-as-register is a validation exposure**, and FDA has cited it: a warning letter found "Failure to validate use of an Excel spreadsheet used to calculate the Moisture Vapor Transmission Rate (MVTR) per test procedure" under 21 CFR 820.70(i) ([Ofni Systems, quoting FDA WL ucm256498](https://www.ofnisystems.com/warning-letter-ucm256498/)). Worth one line in a pitch: the spreadsheet register is both the status quo and a finding waiting to happen.
- **Honest gap:** I could not verify the "one worksheet per calendar year" convention as a *device-industry* norm. The verifiable adjacent facts are the annual numbering resets above ("new log each year"; "Sr. No./Year… reset 31 December"). Treat tab-per-year as a realistic generation choice for Asteria, not a cited industry practice.

### 6.4 FDA enforcement evidence for the routinely-incomplete fields

These are the best possible sources for §2.8 — FDA describing, in its own words, which columns are empty in real registers. All predate the QMSR and therefore cite §820.198; the requirements they enforce survive in §820.35(a), ISO 13485 §8.2.2 and §803.18.

| Failing field | FDA's words | Source |
|---|---|---|
| No register at all; missing device IDs | "Your firm is **missing a complaint log** as acknowledged by your management and **product IDs for all 5 complaint records**." Serial numbers absent from three named complaint records; no rationale or responsible person recorded for decisions not to investigate. | [Sea-Long Medical Systems, 04/04/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/sea-long-medical-systems-llc-647320-04042023) |
| Complainant identity, investigation dates/results, reply — missing from the procedure itself; and reportability unassessed | the procedure "does not include requirements that records of investigation include… any device identifications and control number used; the name, address, and phone number of the complainant; the dates and results of the investigation; and any reply to the complainant." And: "**Five of five complaint records reviewed did not contain documentation of MDR reportability assessments.**" | [X12 Co., LTD., 03/23/2017](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/x12-co-ltd-518581-03232017) |
| `no_investigation_justification` blank at scale | **forty-eight** customer complaints from 2019–2022 where no investigation was performed and the justification was not documented — against the firm's own procedure | [Medivance Instruments Ltd., 02/13/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/medivance-instruments-ltd-647562-02132023) |
| Reportability assessment blank | **eleven of thirteen** complaint records lacked MDR reportability evaluations and lacked an evaluation of whether investigation was necessary; oral complaints received outside the system | [Vitang Technology LLC, 06/12/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/vitang-technology-llc-653455-06122023) |
| Complaints never entering the register because they were filed as something else | "**not all complaints are entered into your firm's complaint handling system; instead many of these complaints (reviewed from 2022 to 2024) were logged and treated as repairs.**" | [Rolence Ent. Inc., 10/18/2024](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/rolence-ent-inc-695010-10182024) |
| Same leak via service reports | US service reports meeting the complaint definition stayed outside the complaint system; components were repaired/replaced without determining why they failed | [Boule Medical AB, 10/02/2018](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/boule-medical-ab-559614-10022018) |

The Rolence and Boule letters are the most important two for `MOCK-DATA.md`. They describe a **structural leak, not sloppiness**: complaints arrive as service jobs and repairs and are legitimately filed as service jobs and repairs, and nobody reclassifies them. Asteria's PulseOne service and RMA data should contain several cases that meet the §3.4 complaint definition and have no complaint record — generated because the service technician had no reason to think otherwise, not because we planted them. FDA's own deck anticipates the countermeasure ("Have Formally Designated Unit **review** all Servicing reports/records for complaints"), which makes this an honest, sourced, emergent finding rather than a manufactured one. This is also the single strongest argument for `DIAGRAMS.md` workflow 1 existing at all.

### 6.5 Vigilance register — the honest state of the convention evidence

One finding up front, because it shapes how the rest of this section should be read: **no commercial eQMS vendor publishes a vigilance register column list.** Of the vendors worth checking, only Veeva publishes field-level documentation publicly. Greenlight Guru, MasterControl, AssurX, ETQ, Sparta TrackWise, Qualio, Rimsys, Scilife, SimplerQMS and Intellect publish marketing copy only. Medical Device Academy sells the artefact (`LST-011 v0.1 Complaint Register`, bundled with `SYS-001` / `SYS-029` Medical Device Reporting Procedure) but the columns are behind the paywall.

Consequently **none** of the abbreviated headers one would expect — `MDR#`, `Rptbl?`, `Days to Due`, `MIR Sent?`, `Initial/FU`, `CA Ref #`, `5-day or 30-day` — could be verified from any public source. They are plausible, and they are what firms abbreviate *to*, but they should be generated for Asteria as our invented convention, not cited.

What *is* available is better evidence anyway: the regulator-authored labels that firms abbreviate *from*, a real filed MIR, FDA's own public MAUDE export layout, and one vendor's complete shipped status vocabulary.

**Two headers are confirmed primary, though.** Form FDA 3500A itself uses `Manufacturer report #`, abbreviated **by FDA** to **`Mfr report #`**; and FDA's legacy Alternative Summary Report export uses the literal column names **`Manufacturer Aware Date`** and **`Initial Report Flag`**. So "Mfr Report #" and "Awareness Date" as column wording are citable; the rest are not.

### 6.6 Verbatim vigilance field labels, from regulators

**Form FDA 3500A Section H** — the manufacturer-only block, and the vocabulary register columns get named after ([3500A instructions 09/2025](https://www.fda.gov/media/133177/download)):

> `H1: Type of Reportable Event` · `H2: If Follow-up, What Type?` · `H3: Device Evaluated by Manufacturer?` · `H4: Device Manufacture Date` · `H5: Labeled for Single Use` · `H6: Adverse Event Problem` · `H7: If Remedial Action Initiated, Check Type` · `H8: Usage of Device` · `H9: If action reported to FDA under 21 USC 360i(g), list correction/removal reporting number` · `H10: Related Report Number` · `H11: Additional Manufacturer Narrative` · `G8: Manufacturer Report Number (For all manufacturers)`

`H1` values verbatim: `Death` / `Serious injury` / `Malfunction` / **`Summary Report`** (the VMSR checkbox). `H2` values verbatim: `Correction: Changes to previously submitted information.` / `Additional information: Information concerning the event that was not provided in the initial report because it was not known/available when the report was originally submitted.` / `Response to FDA request: … e.g., FDA requests additional information when the report is submitted late (retrospective reporting), the report is a result of an internal audit or FDA inspection, etc.` / `Device evaluation: Evaluation/analysis of device.`

That `Response to FDA request` gloss is worth reading twice: **FDA's own form instructions name "the report is submitted late (retrospective reporting)" as a routine follow-up reason.** Late reports are a modelled-for case in the regulator's own vocabulary.

**A real filed MIR v7.3.1**, submitted June 2025 and published by the receiving authority — the best evidence of what the fields actually contain in practice ([gov.sm](https://www.gov.sm/pub1/GovSM/dam/jcr:915e806b-207d-4836-b295-30b5a74fdc26/R2025173_md_new-reg_mir-form-v7.3.1_FINAL%20Signed.pdf)):

| MIR field | Value in the real filing |
|---|---|
| `1.1 c Reference number assigned by NCA for this incident` | **`Unknown`** |
| `1.1 d Reference number assigned by EUDAMED for this incident` | **blank** |
| `1.2 b Date of incident` | **`2025-05-20 to 2025-05-20`** — rendered as a range even when the date is known |
| `1.3.1 b Manufacturer's reference number for this incident` | **`R2025/173`** — year-slash-sequence |
| `1.3.2 b Single registration number` | **`IT-MF-000029427`** — `{country}-{actor type}-{9 digits}` |

Four of those five are directly reusable as mock-data realism, and the `Date of incident` one is a correction to an assumption: the MIR renders a single known date as a degenerate range, so our date-range model should too.

EUDAMED's own MIR creation screen adds one more label worth knowing, because it constrains editing: **"The information provided in this step cannot be modified after you click Create form."** ([EUDAMED help](https://webgate.ec.europa.eu/eudamed-play-help/en/search-by-module/vigilance/manage/register-a-new-mir/create-initial-mir-dossier.html))

**Health Canada's CV-MD industry form** is the clearest public example of the cross-jurisdiction bookkeeping our register needs, with labels that map almost one-to-one onto the columns in §3.3 ([Health Canada form](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/dhp-mps/alt_formats/pdf/medeff/report-declaration/md-mm_form-eng.pdf)):

> `A3. Reporter File Number` — "Indicates the manufacturer's or importer's file number for the case. For final reports, the report number should be the same as the preliminary report."
> `A4. Health Canada File Number` — "A number provided in the acknowledgement letter for the preliminary report."
> `A5. Type of Report` — "preliminary, update, final, or a preliminary and final. It also includes the anticipated date for the submission of the final report."
> `B1. Classification of Incident` — "if the report is a **10 day or 30 day report**, based on the seriousness…"
> `B3. Reporter's Awareness Date`
> `C9. Availability of Device` — "Indicates if the device has been destroyed, or is available for the company/Health Canada for further evaluation"
> `E1. Investigative Actions and Timeline` — "**If no investigation is to be done, a rational needs to be provided here.**"
> `E3. Corrective actions taken as a result of the investigation` — "**If no corrective action is to be taken, a rationale needs to be provided here.**"

Three lessons. **`Reporter File Number` alongside `Health Canada File Number`** is primary-source proof of the our-ref/their-ref pair in one row. **`B1. Classification of Incident` explicitly doubling as the clock selector** ("10 day or 30 day report") confirms the `clock_class` design in §3.3 — the same pattern the MIR uses with 2/10/15. And Canada mandates the negative rationale *twice on the form*, for investigation and for corrective action, which is the §4 decision-1 pattern appearing in a third jurisdiction.

**Veeva Vault Safety** — the only commercial field list available, and it validates the clock model more precisely than expected ([Case Field Reference](https://safety.veevavault.help/en/lr/01287/), [Localized Case Field Reference](https://safety.veevavault.help/en/lr/891324/), vendor):

> `Manufacturer Reportable Awareness Date` — "date when the manufacturer became aware of the report" · `Receipt Date` — "date the event was first reported" · `Due Date` — calculated earliest reportable date to agencies/partners · `Device Report Type` · **`Device Report Type (Status)`** — "whether populated automatically or manually overridden" · `Device Follow-Up Type` · `Malfunction Only` · `Remedial Action` / `Remedial Action-Other` · `Transmission Reason` (Amendment or Nullification) · `Overall Case Seriousness` · `Suppress Submission`
> and per-locale: **`Global Due Date`** ("From global Case") alongside **`Due Date`** ("earliest regulatory due date for the *Localization*"), `Localized Assessment Result`, `Expected`, **`Expected (status)`** ("auto-calculated or manually overridden"), **`Override Reason`**

Three things to adopt from this:

1. **`Manufacturer Reportable Awareness Date` and `Receipt Date` are separate shipped fields.** A mainstream vendor already refuses to collapse them. §2.6's insistence on keeping `date_received` and awareness apart is industry practice, not our invention.
2. **`Global Due Date` coexisting with a per-localization `Due Date`** is independent validation of §3.1's grain and §3.6's per-jurisdiction clock computation.
3. **`Device Report Type (Status)` = "auto-calculated or manually overridden", plus `Override Reason`.** This is the field I did not have and should. Add to §3.3's product fields: wherever we compute reportability or a clock class, ship a companion `*_status` of `computed | human-overridden` plus `override_reason`. It pairs exactly with §803.18(b)(1)(i)'s requirement to retain "all documentation of your deliberations and decision making processes" — and with the Exactech citation for failing to do so (§6.8).

**Veeva's Transmission lifecycle** is a complete, shipped status set and a better starting point than anything I could reason out ([Veeva](https://safety.veevavault.help/en/lr/01266/), vendor):

> Pending stage: `Ready` · `Pending` · `Validation Error` · `Ready for Submission`
> Sending stage: `Sending ICSR` · `Sending Attachments` · `Error`
> Sent stage: `MDN Received` · `MDN Failure` · `ACK Warning` · `ACK Rejected`
> Accepted stage: `ACK Accepted`

with `ACK Warning` = "destination gateway could not load the transmission" and `ACK Rejected` = "destination gateway loaded the transmission but rejected it" — a distinction worth keeping. An older Veeva page shows a partly different set including `Withdrawn` and an `E2B ` prefix, so vendor vocabularies drift across releases; ours should be versioned too.

**eMDR acknowledgements.** §3.3 marks these as mandated file content under §803.18(b)(1)(iii), and they are, but the *levels* are a place sources disagree — see §5. FDA's current ESG NextGen documentation describes **ACK1** ("if the submission was uploaded into ESG NextGen"), **ACK2** ("if the submission was successfully transmitted to the Center") and **"ACK3 & ACK4"** ("the Center's response on the submission"), Center-dependent; every vendor source says "three ACKs". Model four slots or a single `{ack_level, ack_status}` pair, and do not assert "FDA sends three acknowledgements" as fact. ([FDA ESG NextGen](https://www.fda.gov/industry/getting-started-esg-nextgen/submission-acknowledgements))

Real ACK3 rejection reasons, verbatim from FDA's troubleshooting page, make a good rejection-reason enum — and the first one is a register-integrity check: "This error means that **eMDR has already accepted a report with this report number**." Others: "the report number you provided was not valid", "one of the codes you provided in the Adverse Event Code fields … was not valid", "the state code you entered in one of the address fields was not a valid U.S. state code". ([FDA eMDR troubleshooting](https://www.fda.gov/medical-devices/emdr-electronic-medical-device-reporting/emdr-troubleshooting-and-contact-information))

One currency note: "As of April 14, 2025, the ESG NextGen Unified Submission Portal (USP) replaced the legacy WebTrader user interface." Any design referencing WebTrader is stale.

### 6.7 What the grain evidence actually settled

The convention research resolved §3.1 more firmly than the primary reading alone did, and in our favour.

**FDA mandates more than one row per event, within a single jurisdiction.** 3500A General Instructions, verbatim: **"For medical device reporting, manufacturers, importers, and user facilities must prepare and submit a complete Form FDA 3500A for each suspect device. Each Form FDA 3500A will be given a separate Report Number."** And FDA's MDR guidance §5.1.2(2): "If more than one of your devices is involved in a single MDR reportable event, and it is not apparent which device may have caused or contributed to the event, then you must submit a separate report for each of your devices involved in the event. … if a series of MDR reportable events occurs, the regulation requires a separate report for each event." ([FDA MDR guidance](https://www.fda.gov/media/86420/download))

So the per-device split is **mandated in the US too**, not only implied by the EU's MIR cross-reference field. §3.1's grain is confirmed by primary sources on both sides.

**But the MDR number is not the row key.** Same instructions, verbatim: "For a follow-up report, the manufacturer report number must be identical to the number assigned to the initial report", with the follow-up sequence in `G6` — "first follow-up report = follow-up #1, second follow-up report = follow-up #2, and so on." Initial plus three follow-ups share one number. §3.1's "follow-ups are versions, not rows" is therefore correct, and `fda_manufacturer_report_number` must be unique per *row*, not per submission.

**And the mapping is many-to-many in both directions.** The per-device fan-out is one-event-to-N-rows; PSR (EU) and VMSR (US) are N-events-to-one-submission. Neither "one row per event with jurisdiction columns" nor "one row per submission" survives alone, which is why §3.1 separates the obligation row from its submissions and why §3.3 has bucket rows.

**FDA gives the cross-reference nowhere structured to live.** 3500A front page, verbatim: "Enter all numbers, if applicable, to cross-reference this report with a report from another source on the same event. For medical devices, the cross-reference report number should be left blank in the section and **instead entered in H11: Additional Manufacturer Narrative**." That is the best available justification for our `jurisdiction_divergence[]` and sibling-link fields: the regulator pushes the cross-reference into free text, so the structure has to exist in the firm's own register or not at all.

**Fan-out differs by row type.** MDCG 2023-3 Q20: a serious incident goes to "the competent authority of the Member State in which the serious incident occurred" — one authority. An FSCA goes to "the competent authority(ies) of the Member State(s) in which the FSCA is being or is to be undertaken", and "The competent authority in the Member State where the manufacturer or its authorised representative has its registered place of business **must always be informed** of the FSCA, even if it is not amongst the Member States in which the FSCA is being or is to be undertaken." And a `coordinating_authority` field gets populated *later, by them*: authorities may run a coordinated assessment and then "inform the manufacturer … that it has assumed this role".

**Do not merge jurisdictions into a single verdict** — and this is the sharpest practice-versus-enforcement tension in the whole body of evidence. Johner Institute, verbatim: "Do not try to combine the requirements of different countries … defining specific work instructions per country is advisable" ([consultant](https://blog.johner-institute.com/regulatory-affairs/vigilance-system/)). FDA cited a manufacturer for exactly this under §803.17(a)(2): the firm "combined language from the requirements of other regulatory or competent authorities with the requirements in 21 CFR Part 803 in a manner that will result in incomplete, inadequate, or even non-reporting" ([Exactech, 01/19/2024](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/exactech-inc-669904-01192024)). Meanwhile much vendor marketing promotes unified multi-country decision trees. A merged reportability column is an FDA-citable defect, which makes §3.1's jurisdiction-per-row grain a compliance argument and not just a modelling preference.

### 6.8 Vigilance register — real exports, and FDA's own enforcement evidence

**The MAUDE public extract** is the canonical real-world export, and the best source of citable column wording in this domain: pipe-delimited `.txt` files in monthly zips, normalised across four primary and two supplemental files joined on `MDR Report Key` ([FDA MDR Data Files](https://www.fda.gov/medical-devices/medical-device-reporting-mdr-how-report-medical-device-problems/mdr-data-files)).

Header wording to reuse, verbatim from FDA's published layout:

> **MDRFOI:** `MDR Report Key` · **`Empty field (not used)`** · `Report Number` · `Report Source Code` · `Manufacturer Link Flag` · `Number Devices in Event` · `Number Patient in Event` · `Date Received` · `Adverse Event Flag` · `Product Problem Flag` · `Date Report` · `Date of Event` · `Single Use Flag (Reprocessor Flag)` · `Reporter Occupation Code` · `Health Professional` · `Initial Report to FDA` · **`Date Facility Aware`** · `Report Date` · `Date Report to FDA` · `Event Location` · `Date Report to Manufacturer` · **`Date Manufacturer Received`** · `Device Date Of Manufacture` · `Remedial Action` · `Previous Use Code` · `Removal/Correction Number` · `Event type` · `Type of Report` · `Source Type` · **`Date Added`** · **`Date Changed`** · `PMA 510(K) Number` · `Exemption Number` · `Summary Report` · `NOE Summary` · `Suppl Dates FDA Received` · `Suppl Dates MFR Received`
> **DEVICE:** `Device Event key` · `Implant Flag` · `Date Removed Flag` · `Device Sequence No` · `Brand Name` · `Generic Name` · `Device Operator` · `Expiration Date of Device` · `Model Number` · `Catalog Number` · `Lot Number` · `Other ID Number` · **`Device Availability`** · **`Date Returned to Manufacturer`** · `Device Report Product Code` · `Device Age` · **`Device Evaluated by Manufacturer`** · `Combination Product Flag` · `UDI-DI` · `UDI-Public` · `Baseline …` (12 more)
> **PATIENT:** `Patient Sequence Number` · `Treatment` · `Outcome` · `Patient Age` · `Patient Sex` · `Patient Weight` · `Patient Ethnicity` · `Patient Race`
> **TEXT:** `MDR Text Key` · `Text Type Code` · `Patient Sequence Number` · `Text`

Five properties of this export are worth copying into Asteria's mock data verbatim-in-spirit:

- **`Empty field (not used)` is published as column 2.** Dead columns survive in real exports forever.
- **FDA's own layout contains a typo it has never fixed**: `Baseline 510(k exempt flag` and `Baseline date) first marketed` — the parenthesis is in the wrong field name. A misplaced bracket in a header is exactly the kind of realistic ugliness `MOCK-DATA.md` asks for, and here it is in a regulator's file.
- **`Date Added` and `Date Changed` are distinct from `Date Received`** — rows mutate after publication.
- **Files are year-sharded** (`mdrfoiThru2012.txt`, `mdrfoiThru2024.txt`, plus per-year increments). This is the public-database analogue of the tab-per-year Excel habit, and it is citable where the Excel habit is not.
- **Three incompatible casings for the same schema.** FDA's layout page uses `Title Case With Spaces`; openFDA uses `lower_snake_case` (`mdr_report_key`, `date_facility_aware`, `reprocessed_and_reused_flag`); community import scripts use a third (`Date_Rcvd`, `No_Pts_in_Event`, `Mfr_Link_Flag`). No FDA source uses `SCREAMING_SNAKE_CASE`. Our ingestion layer should be tested against all three, and `MOCK-DATA.md`'s "External" source family should carry a MAUDE-shaped file for similar devices in at least two of them.

Also: text fields carry FOIA redaction markers `(b)(4)` and `(b)(6)` inline. **Honest gap:** there is no machine-readable MAUDE README or data dictionary; the layout page *is* the spec, and it points at Form 3500A for field meanings. And no commercial eQMS publishes its vigilance export schema at all.

**FDA enforcement evidence for §3.8.** These are FDA describing, in its own words, which vigilance columns are empty or late in real registers.

| Failing field | FDA's words | Source |
|---|---|---|
| Awareness date → submission gap | for complaint `CASE-2022-00006275-1` the firm "became aware of the event on September 1, 2022. However, the corresponding MDR **1038671-2023-00008** was received by the FDA on January 4, 2023, which is beyond the required 30 calendar day timeframe." | [Exactech, 01/19/2024](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/exactech-inc-669904-01192024) |
| `deliberation_record` absent | cited under §803.18(b)(1)(i) for failing to document "the deliberations and decision-making processes used to determine if a device-related death, serious injury, or malfunction **was or was not** reportable" | Exactech |
| Merged jurisdictions | the procedure "combined language from the requirements of other regulatory or competent authorities with the requirements in 21 CFR Part 803 in a manner that will result in incomplete, inadequate, or even non-reporting" (§803.17(a)(2)) | Exactech |
| Definitions omitted from the procedure | "The exclusion of definitions from 21 CFR 803.3 for the terms '**become aware**', 'caused or contributed', 'malfunction', 'MDR reportable event', and 'serious injury'" | Exactech |
| Same, plus no standardised review | "The procedure omits definitions of the terms 'become aware' and 'caused or contributed' … The procedure does not establish internal systems that provide for a standardized review process to determine when an event meets the criteria for reporting." Six events late; awareness dates spanning three jurisdictions under **one** complaint number `NCP 2022-14` (Texas 11/17/2022; Pennsylvania ×2 11/21/2022; Spain ×2 12/1/2022) | [Future Diagnostics Solutions B.V., 05/11/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/future-diagnostics-solutions-bv-653493-05112023) |
| **`reportability_decision_date` late, not just submission late** | "Complaints were not reviewed and recorded as **unreportable for over 200 days after receipt**" — complaints `RO_0174581`, `RO_0171904`, `RO_0188624`, `RO_0198227` | [DeVilbiss Healthcare, 11/23/2021](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/devilbiss-healthcare-llc-619182-11232021) |
| Malfunction reports not submitted | complaints `CC-0094982` and `CC-0099632`, Medfusion syringe pump battery depletion; "Your firm initiated a recall Z-0610-2020 for the referenced malfunction." | [Smiths Medical ASD, 10/01/2021](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/smiths-medical-asd-inc-617147-10012021) |

Two of these change the note materially.

**The DeVilbiss citation is the one to build a feature on.** It is not about a late *submission* — it is about a late *negative decision*: 200+ days to record that a complaint was unreportable. That makes `reportability_decision_date` an independently citable field, distinct from awareness and from submission, and it means our register needs a **clock on the not-reportable path too**. §3.4's `10 Assessment in progress` state needs an age, and a register whose only deadline is a submission deadline cannot see this failure mode at all. Add `decision_due_at` (internal target) and `decision_age_days` to §3.6.

**The Future Diagnostics complaint `NCP 2022-14` is the grain argument in an enforcement document**: one complaint number carrying five events across Texas, Pennsylvania and Spain. Exactly the one-complaint-to-many-obligations fan-out §3.1 describes, found in the wild, with the outcome being a warning letter.

**Blank is not the same as unknown, and FDA says so.** MDR guidance §5.1.1, verbatim: **"If the fields are left blank, we cannot determine what information was unknown to you or what information was simply overlooked. By completing each requested data element, you assure us that all elements were considered and reviewed."** The guidance even shows the sentinel: "the OEM should enter **'UNK'** in Block D8 and in Block H11." So our schema needs a three-way distinction per field — *value* / *explicitly unknown with a reason* / *not yet looked at* — and `gaps[]` in §3.3 should populate the middle one rather than leaving a null.

**Device not returned is a mandated explanation, not a gap.** §803.52(f)(3) requires the why-not; the 3500A instruction adds "If an evaluation of a returned suspect or related medical device was not conducted, check the box marked No and provide a justification to explain why not in H11"; and `H6` insists **"Conclusion codes must be entered even if the device was not evaluated."** FDA guidance §4.9.1 is blunter: "although we cannot mandate that a user facility return a device to you for analysis … **The fact that you do not get the device back, however, does not mean you do not have to analyze the event.**" For Asteria's PulsePatch, where the pouch is always discarded, this is the default path and not the exception.

**"Good faith effort" is FDA's name for our `information_requests[]`.** Guidance §2.23: "A 'good faith effort' to obtain additional information should include **at least one written (including email) request** for information. Your MDR files should include a record of each attempt to obtain information, and the nature of the response by the reporter … You should make an effort to obtain correct and complete information about the patient outcome." And §4.9.1: "there is no specified number of attempts … However, you should demonstrate a good faith effort. For example, calling a user facility during hours when you know someone is unable to respond would not be considered a good faith effort." That last sentence is a gift: FDA judges the *quality* of the attempt, which is precisely what a logged request with channel, timestamp and recipient can evidence and a blank field cannot.

**Event type is mutable over a row's life.** Guidance, verbatim: "If your initial report was submitted as a malfunction and you learn a patient died or suffered a serious injury, then your supplemental report should change the event type to death or serious injury." So `clock_class` and `patient_outcome` are versioned fields, and the transition malfunction → serious injury → death is a first-class history our register must keep — which is the same mechanism that makes a due date move *earlier* (§3.6.3).

**Other FDA-listed recurring defects** (guidance §5.1.2), useful as mock-data failure modes: "Duplicate report sequence numbers … You should not use the same sequence number on more than one report in any given year"; Block B-2 outcome contradicting the H-block narrative ("if a reporter marks 'Death' in Block B-2 as the outcome, and after your investigation you determined that the patient did not die, you would provide this explanation in Block H-11"); "Block D (Suspect Medical Device) is left blank or specific items within Block D are left blank"; "A 5-day report is submitted for an event that does not meet the 5-day report criteria"; "A report is marked as a 'follow-up' report, but no follow-up sequence number is provided."

**On backdating awareness dates:** flagged but *not* substantiated. Consultant sources assert it happens; I found **no** FDA warning letter alleging falsification. The citable enforcement pattern is late reporting and late recording of the reportability decision, not backdating. Present it as an industry-discussed risk, not a documented finding — and note the structural argument instead: MDCG's two-date design and §803.18(b)(1)(i)'s deliberation requirement exist precisely because a single mutable awareness date is unprovable.

Two more reusable details: complainant identity can legitimately be absent — MDSAP's own procedure requires the complainant's name "(if not **confidential or anonymous**)" and supports both flags ([MDSAP QMS P0011](https://www.fda.gov/medical-devices/medical-device-single-audit-program-mdsap/mdsap-qms-p0011-complaints-andor-customer-feedback-procedure)) — though no FDA source blesses an "anonymous" value against §820.35(a)(4), so the honest model is a value *plus* a reason-absent code. And patient privacy is normally handled by a separate procedure reference rather than by omitting fields (Argos SOP-0003 points at "Protected Health Information, SOP-0011").

---

## Citations

Primary sources verified September 2026.

**Standards (clause numbers and titles verified; requirement content paraphrased — ISO 13485 and ISO 9000 are copyrighted)**

- ISO 13485:2016 clause numbers and titles **verified against public regulatory text**: 21 CFR §820.35 names Clause 4.2.5 *Control of Records*, Clause 8.2.2 *Complaint Handling*, Clause 7.5.4 *Servicing Activities*; §820.10(b)(3) names Clause 8.2.3 *Reporting to regulatory authorities* — [eCFR Part 820](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-820)
- ISO 13485:2016 clause-to-element mapping for inspection, incl. the §8.2 and §8.3 subclause sets — [FDA CP 7382.850, Attachment A](https://www.fda.gov/media/80195/download)
- §8.2 subclause structure (8.2.1 Feedback · 8.2.2 Complaint handling · 8.2.3 Reporting to regulatory authorities · 8.2.4 Internal audit · 8.2.5 / 8.2.6 Monitoring and measurement) — second and third independent confirmations: [ISO Cloud Consulting](https://isocloudconsulting.com/pages/iso-13485-clause-8-measurement-analysis-improvement), [Advisera 13485Academy](https://advisera.com/13485academy/blog/2018/09/20/how-to-comply-with-section-8-2-monitoring-and-measurement-in-iso-134852018/)
- §8.2.2 required procedure elements and the documented-justification-for-not-investigating permission (paraphrased) — [ISO 13485 Expert](https://iso13485expert.com/blog/complaint-handling-iso-13485-intake-to-regulatory-reporting/) (consultant), [Advisera](https://advisera.com/13485academy/blog/2017/03/21/how-to-comply-with-iso-134852016-requirements-for-handling-complaints/) (consultant)
- ISO 13485 §8.2.2 / §8.2.3 / §8.3.3 audit tasks and per-jurisdiction record content (Brazil ANVISA RDC 665/2022 Art. 121; Canada CMDR 57–61.6; Japan MHLW MO169; Australia TG(MD)R Sch3 P1 1.4(3)) — [MDSAP AU P0002.010 Audit Approach, Feb 2026](https://www.mdsap.global/sites/default/files/2026-02/MDSAP%20AU%20P0002.10%20MDSAP%20Audit%20Approach.PDF)

**United States**

- 21 CFR §820.3 Definitions, §820.10 Requirements for a quality management system, §820.35 Control of records, §820.45 Device labeling and packaging controls (QMSR text, effective 2 Feb 2026) — [eCFR Part 820](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part-820); mirror: [Cornell LII §820.35](https://www.law.cornell.edu/cfr/text/21/820.35)
- FDA QMSR overview and 2 February 2026 effective date — [FDA QMSR](https://www.fda.gov/medical-devices/postmarket-requirements-devices/quality-management-system-regulation-qmsr), [FDA QMSR FAQ](https://www.fda.gov/medical-devices/quality-management-system-regulation-qmsr/quality-management-system-regulation-frequently-asked-questions)
- FDA Compliance Program 7382.850, *Inspection of Medical Device Manufacturers* (supersedes QSIT from 2 Feb 2026; Complaint Handling element; MDR and Corrections-and-Removals as OAFRs; UDI-in-complaints verification at §D(4)(g); MDR violation examples) — [FDA](https://www.fda.gov/media/80195/download)
- 21 CFR §803.3 Definitions — *become aware* (incl. the 30-day vs 5-day asymmetry at (b)(2)), *caused or contributed*, *malfunction*, *MDR reportable event*, *manufacturer or importer report number* format, *serious injury*, *work day*, *UDI* — [govinfo CFR-2024-title21-vol8-sec803-3](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-3.xml)
- 21 CFR §803.11 forms · §803.12 electronic submission · §803.17 written MDR procedures · §803.18 MDR event files and retention — [govinfo §803.18](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-18.xml), [§803.12](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-12.xml), [§803.17](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-17.xml)
- 21 CFR §803.50 — 30 calendar days; "reasonably known" at (b)(1)(i)–(iii); incomplete-information statement at (b)(3) — [govinfo](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-50.xml), [Cornell LII](https://www.law.cornell.edu/cfr/text/21/803.50)
- 21 CFR §803.52 — the complete Form FDA 3500A Block A/B/D/E/G/H data-element list — [govinfo](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-52.xml), [Cornell LII](https://www.law.cornell.edu/cfr/text/21/803.52)
- 21 CFR §803.53 — 5 work days — [govinfo](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-53.xml), [Cornell LII](https://www.law.cornell.edu/cfr/text/21/803.53)
- 21 CFR §803.56 — supplemental and follow-up reports, 30 calendar days, cite-the-original-number rule — [govinfo](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec803-56.xml)
- 21 CFR §806.10 — corrections and removals, 10 working days, report-number format `1234567-6/1/97-001-C`, and the §806.10(f) overlap rule with Part 803 — [govinfo](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec806-10.xml)
- 21 CFR §806.20 — records of corrections and removals *not* required to be reported, incl. "Justification for not reporting … reviewed and evaluated by a designated person" — [govinfo](https://www.govinfo.gov/content/pkg/CFR-2024-title21-vol8/xml/CFR-2024-title21-vol8-sec806-20.xml)
- FDA *Voluntary Malfunction Summary Reporting (VMSR) Program for Manufacturers* guidance — summary-report grain (brand × model × problem code set), Table 1 quarterly schedule, exclusions (deaths, serious injuries, 5-day-associated malfunctions), MDR Number requirement — [FDA guidance PDF](https://www.fda.gov/media/163692/download), [FDA VMSR programme page](https://www.fda.gov/medical-devices/medical-device-reporting-mdr-how-report-medical-device-problems/voluntary-malfunction-summary-reporting-program); Federal Register basis 83 FR 40973 (17 Aug 2018) and 89 FR 70096 (29 Aug 2024)

**European Union**

- MDR 2017/745 consolidated text — Art. 2(62)–(69) definitions (incident, serious incident, serious public health threat, corrective action, FSCA, field safety notice), Art. 87 (incl. (3) 15 days, (4) 2 days, (5) 10 days, (6) incomplete initial report, (7) report-while-uncertain, (8) FSCA in advance, (9) periodic summary reports, (11) explanatory statement), Art. 88 trend reporting, Art. 89 analysis and FSN content, Art. 92 electronic system — [EUR-Lex CELEX:02017R0745-20240709](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:02017R0745-20240709)
- MDCG 2023-3 Rev.2, *Questions and Answers on vigilance terms and concepts* — Q14 reporting-timeline arithmetic (calendar days, day+1 at 00:00:01, end 23:59:59, weekend/holiday roll-forward, "earliest date of reporting", "A delay … is not deemed justified"), Q15 manufacturer awareness date and the two MIR date fields, Q16 `Final (Non-reportable incident)`, Q21 Eudamed VGL status, Q23–Q24 periodic summary reports — [European Commission](https://health.ec.europa.eu/document/download/af1433fd-ed64-4c53-abc7-612a7f16f976_en?filename=mdcg_2023-3_en.pdf)
- Regulation (EEC, Euratom) No 1182/71 Art. 3 — the day-counting rules MDCG 2023-3 relies on (period excludes the day of the event; ≥2-day periods include at least two working days; roll forward off weekends and public holidays) — cited in MDCG 2023-3 Rev.2 footnotes 25–29
- **MIR v7.3.1** — the full field list and XML element map, mandatory properties per report type, the 4000-character free-text limit, the denominator-basis vocabulary, and the "IMDRF codes missing" fields — [MIR v7.3.1 Helptext](https://health.ec.europa.eu/document/download/dc6acc1b-f1ae-4512-b838-2fae869124c3_en?filename=md_new-reg_mir-help-v7.3.1_en.pdf)
- EC PMSV reporting forms page — MIR v7.3.1 mandatory from 1 May 2026, the MIR PDF and XSD/XSL, FSCA report form, FSN template and reply forms, trend report form, periodic summary report form — [European Commission](https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance/pmsv-reporting-forms_en)
- Manufacturer's Trend Report form (headed MEDDEV 2.12/1 rev 7) — fields incl. "Date the trend was identified", "Time period of trend analysis", "Established trigger level" — [ec.europa.eu docsroom 32305 att. 6](https://ec.europa.eu/docsroom/documents/32305/attachments/6/translations)
- Manufacturer's Periodic Summary Report form (headed MEDDEV 2.12/1 rev 7) — PSR type, stage (observed failure mode / root cause), agreed summary period, the per-period counts table, geography scope — [ec.europa.eu docsroom 32305 att. 7](https://ec.europa.eu/docsroom/documents/32305/attachments/7/translations)
- EC *Q&A on practical aspects related to the implementation of the gradual roll-out of Eudamed* — Q12/Q13: VGL module not available for voluntary use, becomes applicable six months after the Commission notice, national processes continue meanwhile, and reports open at cut-over continue in Eudamed — [European Commission](https://health.ec.europa.eu/document/download/0e7327c7-0e06-4fbd-90d3-8ab7bb30fe9f_en?filename=eudamed-qa_en.pdf)
- Eudamed module mandatory dates (four modules from 28 May 2026; VGL not among them) — [Osborne Clarke](https://www.osborneclarke.com/insights/eu-triggers-mandatory-eudamed-use-diagnostics-and-medtech-may-2026) (law firm commentary), corroborated by the EC Q&A above

**Convention layer — complaint register** (labelled by kind; see §6)

- FDA CDRH, *Complaint Files* training slides — the pre-QMSR §820.198 record-content list verbatim, the "non complaints" / "investigable" vocabulary, and the servicing-records review countermeasure — [FDA](https://www.fda.gov/files/about%20fda/published/Complaint-Files---Printable-Slides.pdf) *(primary)*
- FDA *Guide to Inspections of Quality Systems* — complaint-handling page: complaints kept in "a customer file, product returns/credit file, service file, warranty file, medical file, or legal file"; the file must contain all complaints including those still open; oral complaints must be documented — [FDA](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/inspection-guides/page-4) *(primary)*
- MDSAP QMS P0011, *Complaints and/or Customer Feedback Procedure* — the "Concern Resolution Report (CRR) Log", and the `confidential` / `anonymous` complainant flags — [FDA](https://www.fda.gov/medical-devices/medical-device-single-audit-program-mdsap/mdsap-qms-p0011-complaints-andor-customer-feedback-procedure) *(primary)*
- FDA warning letters cited in §6.4 — [Sea-Long 04/04/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/sea-long-medical-systems-llc-647320-04042023), [X12 03/23/2017](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/x12-co-ltd-518581-03232017), [Medivance 02/13/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/medivance-instruments-ltd-647562-02132023), [Vitang 06/12/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/vitang-technology-llc-653455-06122023), [Rolence 10/18/2024](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/rolence-ent-inc-695010-10182024), [Boule Medical 10/02/2018](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/boule-medical-ab-559614-10022018) *(primary)* — all cite the pre-QMSR §820.198
- California DSS form LIC 957, *Complaint Control Log* — verbatim column headers and the S/I/U resolution-code set — [CDSS](https://www.cdss.ca.gov/cdssweb/entres/forms/English/LIC957.PDF) *(primary, non-device)*
- Palmetto GBA, *Medicare Beneficiary Complaint Log* — verbatim field labels — [Palmetto GBA](https://dominoapps.palmettogba.com/palmetto/providers.nsf/files/Model%20Complaint%20Log%20Sheet.pdf/$File/Model%20Complaint%20Log%20Sheet.pdf) *(primary, device-supplier domain)*
- Johnson & Johnson Vision Care protocol CR-5856 v2.0 §4.11 — product-quality-complaint field list, the `RDTC-XX-001` numbering rule, and the "Date the complaint was received/recorded in the EDC System (Date of Sponsor Awareness)" label — [clinicaltrials.gov](https://cdn.clinicaltrials.gov/large-docs/23/NCT02886923/Prot_SAP_000.pdf) *(company document published on a .gov domain)*
- Argos Global, *Complaint Processing, SOP-0003 Rev AE* — 38 numbered event-record requirements, the non-complaint / complaint and non-reportable / reportable two-axis classification, the three-attempt good-faith-effort rule — [hosted by Medical Device Academy](https://medicaldeviceacademy.com/wp-content/uploads/Argos-Global-Complaint-Processing-SOP-0003-RevAE.pdf) *(real SOP, consultant-hosted)*
- Veeva Vault QMS product documentation — `Awareness Date` (`awareness_date__v`), `Days for Initial Report Due Date`, `Is Reportable?`, `Type of Assessment`, `Promote to Complaint`, `is a Duplicate of` / `is a Follow-up of`, `XML Generation Failed` — [Configuring Complaint Intake](https://quality.veevavault.help/en/lr/928400/), [Using Complaint Intake](https://quality.veevavault.help/en/lr/28400/), [Duplicate Check](https://quality.veevavault.help/en/lr/52308303/), [MedTech Complaint AE Reporting](https://quality.veevavault.help/en/gr/65833/), [QMS overview](https://quality.veevavault.help/en/gr/34814/) *(vendor)*
- Medical Device Academy — `SYS-018` procedure, `LST-011` Complaint Register (Excel), `FRM-020` Complaint Record (Word) — [Medical Device Academy](https://medicaldeviceacademy.com/complaint-handling-procedure/) *(consultant/vendor)*
- Advisera 13485Academy — *Registry of Customer Complaints*, doc no. `09.2_Appendix_2`, 1-page MS Word — [Advisera](https://advisera.com/13485academy/documentation/registry-of-customer-complaints-iso-13485-2016/) *(consultant/vendor)*
- Oriel STAT A MATRIX / ELIQUENT — Level I/II/III closure depth, and the four feedback categories that are not complaints — [orielstat.com](https://www.orielstat.com/blog/medical-device-complaint-handling-understanding-basics/) *(consultant)*
- ISO 13485 Expert — acceptable no-investigation rationales and the insufficiency of a bare "not a complaint" closure — [iso13485expert.com](https://iso13485expert.com/blog/complaint-handling-iso-13485-intake-to-regulatory-reporting/) *(consultant)*
- ComplianceOnline — "there is no FDA regulation that defines when a complaint is considered 'closed'" — [complianceonline.com](https://www.complianceonline.com/resources/30-frequently-asked-questions-about-medical-device-complaint-and-reporting.html) *(consultant)*
- QMSR §820.35 commentary on the UDI addition and the dropped named-individual requirement — [redhenadmin.com](https://redhenadmin.com/2026/03/22/your-complaint-files-just-got-a-new-address-and-a-udi-requirement/) *(consultant)*
- Ofni Systems, quoting FDA warning letter ucm256498 — unvalidated Excel spreadsheet used for quality records cited under 21 CFR 820.70(i) — [ofnisystems.com](https://www.ofnisystems.com/warning-letter-ucm256498/) *(consultant aggregator of FDA text)*
- Practitioner numbering conventions (`NC12-001`, form/log document-number pairs, the argument against "smart numbers") — [Elsmar: complaint form or log](https://elsmar.com/elsmarqualityforum/threads/customer-complaint-form-or-log.3834/), [Elsmar: numbering best practice](https://elsmar.com/elsmarqualityforum/threads/corrective-action-numbering-and-indexing-best-practice.52929/) *(practitioner forum)*
- Pharmaguideline, market-complaint SOP — `Sr. No./Year` numbering with a 31 December reset — [pharmaguideline.com](https://www.pharmaguideline.com/2011/08/sop-for-handling-of-market-complaints.html) *(consultant, pharma-adjacent)*

**Convention layer — vigilance register** (labelled by kind; see §6.5–§6.8)

- Form FDA 3500A instructions (09/2025) — Section H labels `H1`–`H11`, the `H2` follow-up-type value set, the `Manufacturer report #` / `Mfr report #` wording, the manufacturer report number format with worked examples, the follow-up-number-must-match rule, the one-3500A-per-suspect-device rule, and the "cross-reference … instead entered in H11" instruction — [FDA](https://www.fda.gov/media/133177/download) *(primary)*
- FDA, *Medical Device Reporting for Manufacturers* guidance — "become aware" for 30-day vs 5-day reports, the corporate-awareness position, the good-faith-effort standard (§2.23, §4.9.1), "the fact that you do not get the device back … does not mean you do not have to analyze the event", the supplemental-report event-type change, "If the fields are left blank…" (§5.1.1), and the recurring-defect list (§5.1.2) — [FDA](https://www.fda.gov/media/86420/download) *(primary)*
- FDA MDR Data Files (MAUDE public export) — the verbatim MDRFOI / DEVICE / PATIENT / TEXT / problem-code file layouts, pipe-delimited, year-sharded — [FDA](https://www.fda.gov/medical-devices/medical-device-reporting-mdr-how-report-medical-device-problems/mdr-data-files); background: [About MAUDE](https://www.fda.gov/medical-devices/mandatory-reporting-requirements-manufacturers-importers-and-device-user-facilities/about-manufacturer-and-user-facility-device-experience-maude-database) *(primary)*
- openFDA device-event searchable fields — the `lower_snake_case` rendering of the same schema — [open.fda.gov](https://open.fda.gov/apis/device/event/searchable-fields/) *(primary)*
- FDA eMDR — electronic submission requirement and routes (eSubmitter, AS2 gateway with HL7 ICSR XML), ESG NextGen, and the April 2025 replacement of WebTrader by the Unified Submission Portal — [eMDR hub](https://www.fda.gov/medical-devices/mandatory-reporting-requirements-manufacturers-importers-and-device-user-facilities/emdr-electronic-medical-device-reporting), [eSubmitter](https://www.fda.gov/industry/fda-esubmitter/electronic-medical-device-reporting-emdr), [HL7 ICSR](https://www.fda.gov/medical-devices/emdr-electronic-medical-device-reporting/health-level-seven-hl7-individual-case-study-report-icsr), [ESG NextGen](https://www.fda.gov/medical-devices/emdr-electronic-medical-device-reporting/fda-electronic-submissions-gateway-next-generation-esg-nextgen), [final rule 79 FR (14 Feb 2014)](https://www.federalregister.gov/documents/2014/02/14/2014-03279/medical-device-reporting-electronic-submission-requirements) *(primary)*
- FDA ESG NextGen submission acknowledgements — ACK1 / ACK2 / "ACK3 & ACK4" definitions — [FDA](https://www.fda.gov/industry/getting-started-esg-nextgen/submission-acknowledgements); rejection reasons and helpdesk routing — [eMDR troubleshooting](https://www.fda.gov/medical-devices/emdr-electronic-medical-device-reporting/emdr-troubleshooting-and-contact-information) *(primary)*
- FDA, *Variance from Manufacturer Report Number Format* letter — the four granted variances, incl. arbitrary site assignment noted in `H10` — [FDA](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/variance-manufacturer-report-number-format-mdr-letter) *(primary; note its stale §803.3(o) cite — see §5)*
- FDA warning letters cited in §6.8 — [Exactech 01/19/2024](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/exactech-inc-669904-01192024), [Future Diagnostics Solutions B.V. 05/11/2023](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/future-diagnostics-solutions-bv-653493-05112023), [DeVilbiss Healthcare 11/23/2021](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/devilbiss-healthcare-llc-619182-11232021), [Smiths Medical ASD 10/01/2021](https://www.fda.gov/inspections-compliance-enforcement-and-criminal-investigations/warning-letters/smiths-medical-asd-inc-617147-10012021) *(primary)*
- A real filed MIR v7.3.1 (manufacturer ref `R2025/173`, SRN `IT-MF-000029427`, NCA ref `Unknown`, incident date as a range), published by the receiving authority — [gov.sm](https://www.gov.sm/pub1/GovSM/dam/jcr:915e806b-207d-4836-b295-30b5a74fdc26/R2025173_md_new-reg_mir-form-v7.3.1_FINAL%20Signed.pdf) *(primary — a real submitted form)*
- EUDAMED vigilance module help — MIR initial-dossier screen labels and the "cannot be modified after you click Create form" constraint — [European Commission](https://webgate.ec.europa.eu/eudamed-play-help/en/search-by-module/vigilance/manage/register-a-new-mir/create-initial-mir-dossier.html) *(primary)*
- Health Canada mandatory problem report form for industry — `A3. Reporter File Number` / `A4. Health Canada File Number`, `A5. Type of Report`, `B1. Classification of Incident` ("10 day or 30 day report"), `B3. Reporter's Awareness Date`, `C9. Availability of Device`, `E1`/`E3` negative-rationale requirements; forms `FRM-0237` / `FRM-0238` / `FRM-0255` — [Health Canada form](https://www.canada.ca/content/dam/hc-sc/migration/hc-sc/dhp-mps/alt_formats/pdf/medeff/report-declaration/md-mm_form-eng.pdf), [guidance](https://www.canada.ca/en/health-canada/services/drugs-health-products/reports-publications/medeffect-canada/guidance-document-mandatory-problem-reporting-medical-devices-health-canada-2011.html) *(primary)*
- TGA — Medical Device Incident Reporting (MDIR) system for "initial, follow-up and final reports" — [TGA](https://www.tga.gov.au/resources/guidance/reporting-adverse-events-medical-devices) *(primary; field labels not retrievable, see Confidence notes)*
- Veeva Vault Safety product documentation — `Manufacturer Reportable Awareness Date`, `Receipt Date`, `Due Date`, `Device Report Type (Status)` "auto-calculated or manually overridden", `Override Reason`, `Global Due Date` vs per-localization `Due Date`, and the complete Transmission lifecycle state set — [Case Field Reference](https://safety.veevavault.help/en/lr/01287/), [Transmission lifecycle](https://safety.veevavault.help/en/lr/01266/), [Localized Case Field Reference](https://safety.veevavault.help/en/lr/891324/), [Generate a regulatory report](https://safety.veevavault.help/en/lr/01224/), [Prepare a localized case](https://safety.veevavault.help/en/lr/01290/) *(vendor)*
- Johner Institute — "Do not try to combine the requirements of different countries", plus a per-jurisdiction deadline table — [blog.johner-institute.com](https://blog.johner-institute.com/regulatory-affairs/vigilance-system/) *(consultant)*
- Emergo by UL — vigilance reporting whitepaper; the three nested geographic counts on a final MIR — [Emergo](https://www.emergobyul.com/sites/default/files/2024-08/RLC24CS1445442-Vigilance_Reporting-Whitepaper.pdf) *(consultant)*
- Oriel STAT A MATRIX / ELIQUENT — EU MDR/IVDR vigilance reporting overview — [orielstat.com](https://www.orielstat.com/blog/eu-mdr-ivdr-vigilance-reporting-requirements/) *(consultant)*
- Medical Device Academy — `SYS-029` / `SYS-001` Medical Device Reporting Procedure bundled with `LST-011` Complaint Register — [Medical Device Academy](https://medicaldeviceacademy.com/medical-device-reporting/) *(consultant/vendor; register columns paywalled)*
- VMSR Federal Register modification notice (89 FR 70096, 29 Aug 2024) — [federalregister.gov](https://www.federalregister.gov/documents/2024/08/29/2024-19414/medical-devices-and-device-led-combination-products-voluntary-malfunction-summary-reporting-for) *(primary)*

**Internal references**

- [`WORKFLOW.md`](../WORKFLOW.md) — §1.1 complaint/NC relationship, §3 Lane A steps, §5 the vigilance clock, §7 correction vs corrective action, §8 QMSR deltas, §9 agent interventions and hard human gates
- [`DIAGRAMS.md`](../DIAGRAMS.md) — workflows 1–9 and the source dependency matrix
- [`MOCK-DATA.md`](../MOCK-DATA.md) — realistic imperfection model, source-system characteristics, physical dataset layout
- [`mock/asteria/entities.md`](../mock/asteria/entities.md), [`mock/asteria/products.md`](../mock/asteria/products.md) — PulseOne P1-100 serialised reusable device, PulsePatch PP-72 lot-controlled consumable, hardware revisions H1/H2/H2.1, semantic software versions

### Confidence notes

**High confidence — quoted from primary or official sources and cross-checked**

- All 21 CFR text in this note (§820.3, §820.10, §820.35, §820.45, §803.3, §803.11, §803.12, §803.17, §803.18, §803.50, §803.52, §803.53, §803.56, §806.10, §806.20) — pulled as structured XML from govinfo and the eCFR API, not from summaries. §820.35's QMSR text was taken from the eCFR current-as-of-2026 rendering.
- All MDR 2017/745 text — pulled from the EUR-Lex consolidated HTML (CELEX 02017R0745-20240709).
- All MDCG 2023-3 Rev.2 quotations, including the day-counting arithmetic and both awareness-date definitions — extracted from the Commission's own PDF.
- The complete MIR v7.3.1 field list and XML element names — extracted from the Commission's own helptext PDF, including the XML Element Field Map, so field names are exact rather than reconstructed.
- The VMSR quarterly schedule, summary-report grain, and exclusions — from FDA's own guidance PDF (Table 1 and §V.C.1).
- ISO 13485 clause numbers **and titles** for 4.2.5, 7.5.4, 8.2.2 and 8.2.3 — these are quoted inside public CFR text, which is an unusually strong confirmation for a paywalled standard. The §8.2 and §8.3 subclause sets are additionally confirmed by FDA CP 7382.850's Attachment A mapping table and by two independent consultant sources.
- CP 7382.850's treatment of Complaint Handling as a QMS element and MDR / Corrections-and-Removals as separate OAFRs — from FDA's own compliance program PDF.
- The §803.3 paragraph lettering: **(m)** is *Manufacturer or importer report number*, **(o)** is *MDR reportable event*. Verified twice, in the 2024 annual CFR XML and in the current eCFR rendering of Part 803.
- The MAUDE export file layouts, the 3500A Section H labels and value sets, the one-3500A-per-suspect-device rule, and every FDA warning-letter quotation in §6.4 and §6.8 — from FDA pages and PDFs.
- The grain conclusion. It rests on two independent mandates pointing the same way: the 3500A instructions ("a complete Form FDA 3500A for each suspect device. Each Form FDA 3500A will be given a separate Report Number") and MIR field 1.3.1(c)'s sibling cross-reference. This is the strongest-evidenced claim in the note.

**Paraphrased, not verified verbatim**

- Every statement of what ISO 13485 §8.2.2, §8.2.3, §8.3.3, §8.4, §8.5.2 or §4.2.5 *requires* in substance. The standard is paywalled; clause numbers and titles are reliable, and the §820.35(a) and §820.10(b)(3) text tells us what FDA believes those clauses say, but the exact requirement wording should be checked against a purchased copy before any of this appears in a customer-facing compliance claim.
- The specific list of §8.2.2 procedure elements in §2.3 is assembled from two consultant sources that broadly agree; treat the *set* as reliable and any individual item as paraphrase.
- ISO 14971 linkage for the risk-file fields is asserted from the MIR's own risk-assessment fields, not from 14971 text.

**Corrected during research**

- **§820.35(a)(6) says "Any correction or corrective action taken", not "corrective action taken".** `WORKFLOW.md` §3 step A3 and §8 both render the mandated field as "corrective action taken". The QMSR text carries both words, which *strengthens* `WORKFLOW.md` §7's correction-vs-corrective-action argument — the distinction is now in the regulation's own complaint-record field list. Worth a one-word fix in `WORKFLOW.md` and a two-link-type model in the schema.
- **§820.35(a) also mandates the no-investigation justification in the US**, not only ISO §8.2.2. `WORKFLOW.md` §3 step A5 attributes the documented-justification requirement to §8.2.2 alone; §820.35(a) states it directly and publicly: "If an investigation has already been performed for a similar complaint, another investigation is not necessary, and the manufacturer shall maintain records documenting justification for not performing such investigation."
- **§820.35(a)'s mandated seven fields are scoped, not universal.** They apply to "complaints that must be reported to FDA under part 803 …, complaints that a manufacturer determines must be investigated, and complaints that the manufacturer investigated regardless of those requirements". A complaint that is neither reportable nor investigated is arguably outside that specific field list (though still a record under §8.2.2 and §4.2.5). I have marked the seven as `Mandated` anyway because the scoping exception is narrow and no sensible register would vary its columns by row — but the scope sentence is real and an auditor may raise it.
- **I initially expected QSIT to be the inspection reference.** It was retired on 2 February 2026 and replaced by CP 7382.850. Any design note or pitch that cites QSIT is now dated.
- **MDSAP AU P0002.010 Annex 3 states "5 calendar days" for the US 5-day report.** 21 CFR §803.53 says "5 work days" and §803.3(y) defines work day; FDA's VMSR guidance also says "5-work day". MDSAP's quick-reference table is wrong on this point and I have implemented the CFR. See §5.
- **The EU trend and PSR forms are MEDDEV-era, not MDR-era.** I expected MDR-native forms to exist because the MIR was rewritten; they were not. Both forms on the current EC PMSV page are headed "Medical Devices Vigilance System (MEDDEV 2.12/1 rev 7)" and offer MDD/AIMD/IVD device classes. Art. 88 reporting therefore runs on a legacy template today.
- **Eudamed's vigilance module is still not live as of September 2026**, despite four other modules becoming mandatory on 28 May 2026. I had assumed Eudamed submission would be the 2026 default; it is not, and the register must model national channels plus a mid-life migration.
- **FDA's own variance letter cites §803.3(o) for the manufacturer report number format; the current and 2024 CFR both put it at §803.3(m).** I checked the paragraph lettering directly rather than trusting either. Cite (m).
- **I expected the per-device report split to be an EU-only implication of MIR field 1.3.1(c). It is mandated in the US too**, explicitly, in the 3500A General Instructions. This strengthened the grain decision from "defensible" to "required".
- **I expected a merged cross-jurisdiction reportability verdict to be merely inelegant. It is FDA-citable** — a manufacturer was cited under §803.17(a)(2) for combining other authorities' requirements with Part 803. This turned a modelling preference into a compliance argument, and it cuts against what a lot of vendor marketing promotes.
- **I expected the only vigilance clock to be the submission clock.** A warning letter citing a firm for taking "over 200 days" to record complaints as *unreportable* shows the negative-decision path has its own enforceable latency. `reportability_decision_date` and a decision-age clock were added after this.
- **I expected "field left blank" to be an acceptable representation of unknown.** FDA explicitly rejects it ("we cannot determine what information was unknown to you or what information was simply overlooked") and uses the sentinel `UNK`. The three-state empty model in §4 is a direct consequence.
- **The abbreviated register headers I went looking for do not exist in any citable source.** `MDR#`, `Rptbl?`, `Days to Due`, `MIR Sent?`, `Initial/FU`, `CA Ref #`, `Cmplt #`, `Date Rec'd`, `CAPA#`, `Days Open` — none verified. Two close cousins *are* primary: FDA abbreviates its own field to `Mfr report #`, and FDA's legacy summary-report export uses `Manufacturer Aware Date` and `Initial Report Flag`. Everything else of that shape must be generated as Asteria's invented convention, not cited as industry practice.
- **Backdating awareness dates is not a documented FDA finding.** Consultant sources assert it; I could find no warning letter alleging falsification. The citable patterns are late reporting and late recording of the decision. Do not put "firms backdate awareness dates" in a pitch as an FDA-evidenced claim.

**Not covered here**

- IVDR 2017/746 (the MIR and MDCG 2023-3 cover both, and IVDR Art. 82 mirrors MDR Art. 87 clause-for-clause, but IVDR-specific fields such as `imdrfClinicalCodeChoice` usage for erroneous results are not worked through).
- The FSCA / advisory-notice / Part 806 register as a register in its own right. It is referenced here as a link target, and the official EU FSCA report form is an XFA PDF whose fields I could not extract; that register needs its own note.
- UK (MHRA), Health Canada, TGA, ANVISA and PMDA field-level detail beyond the MDSAP clock table and the ANVISA Art. 121 record-content list.
- Retention-schedule arithmetic beyond §803.18(c) and §806.20(c).
- **Commercial eQMS register column lists other than Veeva's.** Greenlight Guru, MasterControl, AssurX, ETQ, Sparta TrackWise, Qualio, Rimsys, Scilife, SimplerQMS, Intellect and Matrix Requirements publish marketing copy only; several refuse automated fetches. Medical Device Academy's `LST-011` register is paywalled. If a customer-facing claim needs "this is what every eQMS carries", it cannot be sourced today beyond Veeva.
- **A machine-readable MAUDE data dictionary.** None appears to exist; the MDR Data Files page *is* the spec and it defers to Form 3500A for field meanings. The widely repeated "135 fields across six file types" is a third-party count I could not verify.
- **The `Device Evaluated by Manufacturer` value set** in MAUDE. One community source reports raw codes `R` / `N` / `Y`; the commonly quoted display string "Not Returned to Manufacturer" could not be confirmed against any FDA page. Do not assert the enumeration.
- **TGA MDIR field labels.** tga.gov.au timed out repeatedly; only the existence of the MDIR system and its initial/follow-up/final report types is confirmed.
- **The official EU FSCA report form's field list.** It is an XFA PDF and did not yield text to extraction. The FSCA / advisory-notice / Part 806 register needs its own note, and whoever writes it should expect the same obstacle.
- **Asteria's own chosen identifier formats and column wording.** Deliberately not decided here, because §6.1 and §6.5 establish that these are per-company conventions with no citable industry standard — so they are a mock-data design choice, and should be made once and applied consistently rather than inferred from this note.
