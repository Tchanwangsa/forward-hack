# Quality Context and Action Platform

## One-line concept

**A shared quality context and action platform, with post-market surveillance (PMS) as the first module and entry point.**

The product is an intelligent coordination layer across a customer's existing quality management system (QMS), email, CRM, document storage, support platform, and operational databases.

It brings fragmented information together, identifies work that may need attention, assembles the supporting evidence, and helps authorised employees carry quality workflows through to completion.

## Product position

The product does not certify a company, guarantee compliance, or replace the judgement of quality and regulatory professionals. It also does not initially replace the customer's established QMS or systems of record.

It sits above those systems and helps people answer:

- What has happened?
- Which records and documents are related?
- What information is missing?
- Who needs to respond?
- What decision is due?
- Which controlled records may need to be created or updated?
- Can we retrieve the complete evidence trail later?

The initial medtech context is a company operating a quality system based on ISO 13485 and performing medical-device PMS. The broader architecture should support other regulated quality workflows without hard-coding the product around a single standard or jurisdiction.

## The problem

Quality work is distributed across tools that were designed for different teams:

- Complaints arrive through email, support systems, distributors, salespeople, and service teams.
- Product, shipment, software-version, lot, and installed-base information lives in operational databases.
- Investigations and quality records live in a QMS, spreadsheets, shared drives, or document repositories.
- Decisions are made in meetings and explained across email threads.
- Tasks and deadlines are chased manually.
- Evidence must later be reconstructed for reviews and audits.

The expensive part is often not creating another form. It is joining the context, finding the responsible people, requesting missing information, maintaining traceability, and keeping work moving without losing the evidence behind decisions.

## Initial users

### Primary user

Quality or post-market surveillance specialist at a small or medium medical-device company.

### Supporting users

- Quality manager
- Regulatory affairs specialist
- Customer-support representative
- Clinical or safety specialist
- Service technician
- Product or engineering lead
- Manufacturing representative
- Document-control administrator
- Executive participating in management review

## First module: post-market surveillance

PMS is the first module because it naturally depends on information from many parts of the business and can lead into several other quality workflows.

### PMS inputs

- Complaint and support records
- Customer and distributor emails
- CRM notes and cases
- Service, repair, return, and replacement records
- Product, model, lot, serial-number, UDI, and software-version data
- Sales, shipment, and installed-base data
- Existing PMS plans and reports
- Previous investigations and quality actions
- Risk-management information
- Meeting minutes and approved decisions
- Regulatory, safety-notice, literature, or comparable-device sources added later

### PMS capabilities

- Find potential post-market information across connected sources
- Extract relevant facts while preserving source provenance
- Reconcile products, customers, device identifiers, and related records
- Identify likely duplicates without silently merging official records
- Detect missing or conflicting information
- Draft and manage requests for additional information
- Calculate configured rates and trends using appropriate denominators
- Group related observations for human review
- Prepare source-linked signal review material
- Coordinate investigations, actions, meetings, and deadlines
- Draft downstream records such as an investigation or CAPA proposal
- Assemble evidence for PMS reporting and audit preparation

### PMS outputs

- Unified view of post-market events
- Data-quality and missing-information queue
- Trend tables and visualisations
- Source-linked review packet
- Draft investigation record
- Draft CAPA consideration record
- Information-request emails and reminders
- Action register
- Reviewed meeting minutes
- Draft PMS report or PSUR sections where applicable
- Traceable evidence bundle

## Product architecture

```text
Existing customer systems
  Email | CRM | Support | QMS | Documents | ERP | Service | Product database
                              |
                              v
Source and evidence layer
  Read original records | preserve provenance | monitor changes
                              |
                              v
Shared quality context
  Products | devices | people | organisations | documents | events
  risks | issues | investigations | actions | decisions | evidence
                              |
                              v
Reusable intelligence and action layer
  Extract | reconcile | search | analyse | draft | request | remind
  route | review | approve | publish | export | write back
                              |
                              v
Quality workflow modules
  PMS first, followed by CAPA, document change, training, audit, and others
                              |
                              v
Human decision and approved system-of-record update
```

## Shared context model

The platform should use tenant-scoped canonical objects so that modules can share context without sharing customer data.

### Organisation and people

- Company
- Legal entity
- Site
- Department
- Employee
- Role
- Approval authority
- Customer
- Distributor
- Supplier

### Product and operations

- Product or device family
- Product version
- Software version
- Lot, batch, serial number, or UDI
- Shipment
- Installation or installed-base observation
- Service activity
- Return or replacement

### Quality

- Source record
- Evidence item
- Post-market event
- Complaint
- Nonconformity
- Signal or review topic
- Risk or hazard
- Investigation
- CAPA
- Change request
- Controlled document and version
- Training requirement and completion
- Audit and finding
- Meeting and decision
- Action and deadline

Every canonical fact should retain its source, extraction method, timestamp, confidence, and review status.

## Reusable agent actions

### Read and understand

- Search connected sources
- Retrieve original evidence
- Compare document versions
- Find related records
- Summarise a case with citations
- Inspect owners, statuses, and deadlines

### Structure and reconcile

- Extract fields from structured and unstructured sources
- Classify information using customer-controlled taxonomies
- Match records to products, devices, organisations, and people
- Suggest duplicates
- Identify conflicts and missing information
- Link evidence to a canonical object

### Analyse

- Run deterministic calculations
- Normalise event counts against suitable denominators
- Compare periods, products, versions, lots, markets, and categories
- Identify unusual groupings or changes for review
- Explain results and limitations using source-linked evidence
- Generate tables and visualisations

### Coordinate

- Draft an information request
- Identify an appropriate owner from configured responsibilities
- Create and assign an action
- Monitor responses and deadlines
- Match replies and attachments to open requests
- Draft reminders and escalations
- Prepare a meeting agenda
- Draft meeting minutes, decisions, and follow-up actions

### Support controlled quality work

- Create a draft quality record
- Prefill an approved template
- Suggest related documents and records
- Route a record for review
- Capture an authorised decision
- Start an approved downstream workflow
- Prepare a controlled-document change
- Publish or write back only after the required approval
- Export a traceable evidence package

## Action permission model

Every action should have an explicit autonomy level:

1. **Observe:** read and organise information.
2. **Recommend:** suggest a classification, relationship, or next step.
3. **Draft:** prepare a record, communication, calculation, or document for review.
4. **Execute with approval:** perform the action after an authorised user confirms it.
5. **Automatic:** perform low-risk, pre-authorised actions such as routine reminders.

Human approval should remain mandatory for regulated or consequential decisions, including:

- Final complaint classification
- Official record merging
- Clinical or safety significance
- Regulatory reportability
- Opening, approving, or closing a CAPA
- Root-cause and effectiveness conclusions
- Controlled-document approval and publication
- External regulatory submissions

## Example cross-module flow

```text
Post-market information
  -> human PMS review
  -> investigation
  -> risk reassessment
  -> CAPA consideration
  -> approved change
  -> document revision
  -> employee training
  -> effectiveness review
  -> management-review and audit evidence
```

Information should be entered or extracted once and reused throughout this chain. Each later decision should remain traceable to its supporting evidence and authorised reviewer.

## Future modules

The same context and action layer could support:

- Complaint handling
- Investigations and CAPA
- Nonconformity management
- Risk management
- Document control
- Change control
- Supplier quality
- Training and competency
- Internal audits
- Management review
- Equipment, calibration, and maintenance records

Each module is primarily a configured set of triggers, required information, calculations, templates, roles, deadlines, approval gates, and outputs built on the shared platform.

## Hackathon product scope

The hackathon should demonstrate one complete and credible workflow rather than a broad but shallow eQMS.

### Demonstrate

1. Connect several fictional source systems.
2. Build a canonical, source-linked view of post-market information.
3. Resolve or surface identity conflicts and missing information.
4. Produce deterministic analysis and a clear visualisation.
5. Prepare a review packet with links to original evidence.
6. Let a quality user make and record a decision.
7. Draft a follow-on investigation or CAPA consideration record.
8. Create requests, actions, and reminders.
9. Show the traceable history from source to approved output.

### Do not attempt during the hackathon

- Full replacement of an established eQMS
- Automatic regulatory reportability decisions
- Automatic regulator submissions
- Autonomous CAPA opening or closure
- Every ISO 13485 workflow
- Production-ready validation for regulated use
- Broad integrations with every commercial system
- Claims that the product guarantees compliance

## Proposed demonstration interface

### Quality inbox

A queue of new information, missing fields, conflicts, due reviews, and overdue actions.

### Unified record view

A timeline showing related email, CRM, service, product, meeting, and QMS records with provenance.

### Analysis workspace

Filters, denominators, deterministic calculations, trend charts, and an explanation of limitations.

### Review packet

A source-linked summary that an authorised user can accept, reject, amend, or send for investigation.

### Action workspace

Owners, information requests, replies, reminders, approvals, deadlines, and downstream records.

### Evidence history

A readable audit trail showing what the system proposed, which evidence it used, what a human decided, and what was subsequently changed.

## Value and success measures

### Operational metrics

- Time required to prepare a PMS review
- Time spent finding and reconciling records
- Percentage of records missing important information
- Time spent drafting and chasing information requests
- Time from new information to human assessment
- Time required to assemble audit evidence
- Number of overdue quality actions

### Product-quality metrics

- Field-extraction accuracy
- Entity-resolution precision and recall
- Duplicate-suggestion precision
- Citation and provenance coverage
- Calculation reproducibility
- Rate of useful versus irrelevant review suggestions
- Human correction rate
- Percentage of actions completed without losing traceability

### Business value hypothesis

The platform reduces administrative coordination time, shortens the time required to assess potential quality issues, improves evidence completeness, and makes existing quality systems easier to operate without forcing an immediate system migration.

## Product risks and safeguards

### Incorrect AI conclusions

- Separate deterministic calculations from language-model explanations.
- Require source citations for material claims.
- Display uncertainty and missing evidence.
- Keep regulated decisions behind human approval.

### Poor or conflicting source data

- Preserve raw records.
- Surface conflicts instead of silently resolving them.
- Record field-level provenance and human corrections.

### Sensitive information

- Use role-based access and tenant isolation.
- Minimise ingestion of patient and personal information.
- Support redaction, retention, and deletion controls.
- Log access and changes.

### Becoming another eQMS

- Integrate with existing systems of record first.
- Own cross-system context, coordination, and traceability.
- Add record ownership only where it creates clear user value.

### Regulated use of the platform

- Define intended use precisely.
- Maintain versioned requirements, prompts, models, rules, and calculations.
- Make outputs reproducible where required.
- Design for customer validation and change control.

## Key product decisions still to make

- Which medtech company size and product type should be the first target?
- Which jurisdictions should the first PMS configuration support?
- Which existing QMS or document repository should remain the official system of record?
- Which two or three connectors are essential for the first pilot?
- What information may leave customer-controlled infrastructure?
- Which actions may be automatic and which always require approval?
- Is the first paid product a PMS review workspace, a quality inbox, or an investigation coordinator?

## Recommended build sequence

### Stage 1: Read-only context

- Ingest mock sources.
- Preserve raw evidence.
- Build canonical objects and relationships.
- Provide search, timelines, summaries, and citations.

### Stage 2: PMS analysis

- Add configured data-quality checks.
- Add deterministic trend calculations.
- Generate visualisations and review packets.

### Stage 3: Human-controlled actions

- Record review decisions.
- Draft investigations and CAPA considerations.
- Create information requests, actions, and reminders.

### Stage 4: Cross-module workflow

- Connect an approved investigation to CAPA, change control, document revision, and training.
- Preserve end-to-end traceability.

## Pitch

Quality teams do not need another place to copy information. They need a layer that understands where quality information lives, connects related evidence, coordinates the people involved, and helps authorised professionals move from fragmented observations to controlled action.

**The product is a shared quality context and action platform. PMS is the first module because it exposes the fragmentation problem clearly and creates a natural path into the rest of the quality system.**
