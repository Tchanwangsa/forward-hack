# Mock Data Layer Instructions

## Purpose

Define the reusable rules for creating fictional, internally consistent company datasets across several independent source systems.

The resulting data should look like ordinary company data created by different teams for different purposes. It must not be generated to produce a predetermined product insight, signal, CAPA, or demonstration outcome.

The product will ingest the frozen source data only after the company history and source records have been generated.

Company-specific scenarios, products, timelines, populations, and volume targets belong in separate files under [`plan/mock/`](mock/). The initial scenario is [Asteria Medical Systems](mock/asteria.md).

## Governing principle

**Simulate the business first. Let product use cases emerge from the resulting data.**

Do not:

- Decide what the AI should find and then manufacture confirming records.
- Put clean canonical identifiers into every source.
- Make every record complete and mutually consistent.
- Create messiness as a collection of arbitrary errors.
- Give the application access to private generation state.
- Modify the source dataset after seeing product results in order to improve the demo.

Instead:

- Model ordinary company operations over time.
- Give each source system a distinct purpose, schema, owner, and update behaviour.
- Let each system observe only the information available to its users.
- Produce natural omissions, delays, duplication, shorthand, and disagreement.
- Freeze and version the source dataset before product evaluation.
- Evaluate discoveries independently after generation.

## Dataset layers

```text
Private simulated world
  What actually happened inside the fictional company
                         |
                         v
Independent source systems
  Partial and imperfect records created by different teams
                         |
                         v
Frozen product input
  Files, tables, messages, documents, and attachments
                         |
                         v
Product-created context
  Entities, links, calculations, suggestions, and workflows
                         |
                         v
Independent evaluation
  Review product results against the private world and source evidence
```

The private simulated world exists to keep the synthetic company coherent. It is not an input to the application and contains no desired product conclusions.

## Source-format principle

The product-facing dataset must be heterogeneous. A collection of Markdown files is useful while drafting content, but it is not sufficient evidence that the ingestion layer can handle real company sources.

Render each record in the format people would naturally create or export from its source system. The dataset should exercise:

- Tabular data with types, formulas, multiple sheets, hidden rows, and inconsistent headers
- Structured API records with pagination, nested objects, update histories, and deleted or archived records
- Email and calendar records with headers, threads, recipients, attachments, and time zones
- Office documents with tables, headers, footers, tracked versions, comments, and approval blocks
- PDFs containing both selectable text and scanned pages
- Images such as device photographs, labels, screenshots, and scanned handwritten notes
- Chat messages with threads, reactions, mentions, edits, files, and links
- Binary attachments whose useful context exists in the parent record rather than the filename

Markdown may be used for repository documentation, generation templates, and sources that are genuinely Markdown-native. It should not be the default rendering format for business records.

For API-backed sources, maintain two related test surfaces:

1. A seeded live test account or workspace used to exercise authentication, discovery, pagination, incremental sync, and permissions.
2. A frozen raw snapshot used for deterministic development and evaluation.

The frozen snapshot should preserve source IDs, timestamps, MIME types, parent-child relationships, and the unmodified API response or export. Human-readable renditions may be included alongside it, but must not replace the raw source representation.

## Private world model

The private model represents the fictional reality behind the records.

### Core world entities

- Company and legal entities
- Sites and departments
- Employees, roles, managers, and approval authorities
- Customers, healthcare organisations, distributors, and suppliers
- Products, revisions, software versions, lots, components, and device units
- Shipments, installations, transfers, returns, and replacements
- Communications
- Support interactions
- Service activities
- Quality activities
- Documents and document versions
- Meetings, decisions, and actions

### World events

Examples of event types include:

- `employee_joined`
- `employee_role_changed`
- `customer_created`
- `order_placed`
- `unit_shipped`
- `unit_installed`
- `software_released`
- `supplier_delivery_received`
- `customer_contacted_sales`
- `support_ticket_opened`
- `device_serviced`
- `product_returned`
- `complaint_assessed`
- `meeting_held`
- `document_revised`
- `training_assigned`
- `training_completed`
- `audit_performed`
- `nonconformity_recorded`
- `quality_action_opened`

An event records what occurred, when it occurred, the participating entities, and the information each participant could reasonably know at that time.

### Private identifiers

Private world IDs may be consistent, but they must not automatically appear in source systems.

```text
ORG-0001       organisation
PERSON-0001    person
PRODUCT-0001   product family
UNIT-000001    device unit
LOT-0001       manufactured lot
EVENT-000001   world event
DOC-0001       logical document
```

Each source system creates its own identifiers and may omit the private identifier entirely.

## Independent source systems

### CRM

Purpose: sales relationships, accounts, contacts, and commercial activity.

Owned by: sales and account management.

Suggested records:

- Accounts
- Contacts
- Opportunities
- Activities and notes
- Product interests
- Account ownership history

Natural characteristics:

- Common customer names rather than precise legal entities
- Stale contacts and account owners
- Informal product terminology
- Free-text customer feedback
- Limited device identifiers
- Sales notes that may contain quality-relevant information without being labelled as such

### Support platform

Purpose: respond to customer questions and problems.

Owned by: customer support.

Suggested records:

- Tickets
- Comments
- Ticket status history
- Tags and categories
- Attachments
- Customer satisfaction responses

Natural characteristics:

- Several issues inside one ticket
- Reopened tickets
- Duplicate contacts from different people
- Missing serial or lot numbers
- Inconsistent manual categorisation
- Informal symptom descriptions
- Links to other systems added only when employees remember

### Email

Purpose: communication across customers, distributors, suppliers, and internal teams.

Owned by: individual employees and shared mailboxes.

Suggested mailboxes:

- Support
- Quality
- Regulatory
- Sales
- Service
- Selected employee mailboxes

Natural characteristics:

- Forwarded and partially quoted threads
- Attachments with unclear filenames
- Discussions that predate formal records
- Abbreviations, spelling mistakes, and ambiguous references
- Different time zones
- Decisions described informally
- Missing recipients or unavailable historical messages

### ERP and commercial database

Purpose: products, orders, shipments, invoices, customers, and suppliers.

Owned by: operations and finance.

Suggested records:

- Product catalogue
- Customer master
- Supplier master
- Orders and order lines
- Shipments
- Returns and credits
- Lot allocations

Natural characteristics:

- Legal names that differ from CRM account names
- Separate bill-to and ship-to organisations
- Product codes that differ from customer-facing names
- Corrections and cancelled transactions
- Shipment history that does not prove current installation or usage

### Installed-base or product database

Purpose: identify shipped or registered device units and their configurations.

Owned by: operations or product engineering.

Suggested records:

- Serialised units
- Hardware revisions
- Software-version observations
- Installation or registration records
- Configuration changes
- Decommissioning records

Natural characteristics:

- Some customers never register devices
- Software-version information can be stale
- Replacement units create confusing histories
- Customer locations differ from shipment destinations

### Service and RMA system

Purpose: manage maintenance, repairs, returns, and technician work.

Owned by: service operations.

Suggested records:

- Work orders
- RMA records
- Technician notes
- Parts replaced
- Inspection and test results
- Return dispositions

Natural characteristics:

- Technician shorthand and specialised failure codes
- Serial numbers without customer-case identifiers
- Several work orders for one unit
- Delayed record creation
- “No fault found” conclusions
- Differences between customer symptoms and technician findings

### QMS repository

Purpose: hold controlled quality records and documents.

Owned by: quality assurance.

Suggested records:

- Document register
- Controlled procedures and templates
- Complaint records
- Investigation records
- CAPAs
- Nonconformities
- Change records
- Risk records
- Audit records
- Training records
- PMS plans and reports

Natural characteristics:

- Formal terminology that differs from operational systems
- Approved, draft, obsolete, and superseded versions
- Metadata copied manually from other sources
- Links to attachments and external records
- Pending approvals
- Register values that occasionally lag behind repository state
- Historical templates still present in folders

### Meetings and action tracking

Purpose: coordinate reviews, decisions, and work.

Owned by: meeting organisers and functional teams.

Suggested records:

- Calendar entries
- Agendas
- Transcripts for selected meetings
- Draft and approved minutes
- Decisions
- Action register

Natural characteristics:

- Different attendees across related meetings
- Informal discussion omitted from approved minutes
- Actions described differently in minutes and trackers
- Changed owners and due dates
- Decisions made after the meeting by email

### PMS working files

Purpose: periodic aggregation and review of post-market information.

Owned by: PMS, quality, clinical, or regulatory personnel.

Suggested records:

- Monthly exports
- Manually maintained analysis spreadsheets
- Review notes
- Data requests
- Approved periodic reports

Natural characteristics:

- Snapshot dates differ between sources
- Manually normalised categories
- Repeated copying between periods
- Calculation logic embedded in spreadsheets
- Late-arriving complaints included in later reviews

## Proposed physical dataset

```text
mock-company/
├── README.md
├── source-manifest.yaml
├── connector-snapshots/
│   ├── google-workspace/
│   └── slack/
├── crm/
│   ├── accounts.csv
│   ├── contacts.csv
│   └── activities.csv
├── support/
│   ├── tickets.json
│   └── attachments/
├── email/
│   ├── support/
│   ├── quality/
│   ├── regulatory/
│   ├── sales/
│   └── service/
├── erp/
│   ├── customers.csv
│   ├── suppliers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── shipments.csv
├── product-database/
│   ├── device-units.csv
│   ├── registrations.csv
│   └── version-observations.csv
├── service/
│   ├── work-orders.csv
│   ├── returns.csv
│   └── technician-notes.csv
├── qms/
│   ├── document-register.xlsx
│   ├── controlled-documents/
│   ├── complaints/
│   ├── investigations/
│   ├── capas/
│   ├── nonconformities/
│   ├── change-control/
│   ├── risk/
│   ├── audits/
│   └── training/
├── meetings/
│   ├── calendars.ics
│   ├── transcripts/
│   ├── minutes/
│   └── action-register.xlsx
└── pms/
    ├── monthly-exports/
    ├── working-analysis/
    ├── review-minutes/
    └── approved-reports/
```

Private generation state and independent evaluation data must live outside `mock-company/` so the application cannot ingest them accidentally.

## Source manifest

The source manifest describes the dataset without resolving its contents:

- Source-system name
- System purpose
- Owning department
- Export timestamp
- File format and encoding
- Time-zone convention
- Schema version
- Included date range
- Known export limitations
- Whether records can be updated after creation
- Sensitivity classification

It must not include cross-source entity mappings or expected findings.

## Data-generation mechanics

### 1. Define stable company state

- Organisation structure
- Employee roster and responsibilities
- Product catalogue
- Customer, distributor, and supplier population
- Source-system ownership
- QMS document hierarchy
- Business calendar and working hours

### 2. Advance the world through time

Generate ordinary events using configured rates, dependencies, seasonality, and state transitions.

Examples:

- Orders cause shipments.
- Shipments may cause registrations or installations.
- Installed devices may later generate support contacts or service work.
- Employee role changes affect ownership and approval routing.
- Document releases cause training assignments.
- Meetings create decisions and actions with imperfect follow-through.

### 3. Let source systems observe events

Each source adapter decides:

- Whether the event is visible to that system
- When it becomes visible
- Which fields its users know
- How entities are named
- Whether a user creates or updates a record
- Whether information is copied from another source
- Which details are placed in structured fields versus free text

### 4. Render source-native records

- CSV for flat system exports and interchange files
- XLSX for working analyses, registers, formulas, and multi-sheet workbooks
- JSON or JSONL for API responses, chat exports, histories, and nested records
- EML for email, including realistic headers, quoted replies, and attachments
- ICS for calendar events and recurring meetings
- DOCX for editable procedures, minutes, reports, forms, and draft controlled documents
- PDF for approved records, supplier certificates, signed forms, and fixed renditions
- PNG, JPEG, or TIFF for screenshots, device photographs, labels, and scans
- TXT, HTML, or RTF only where the originating system would plausibly produce them
- ZIP for source-native bulk exports whose internal directory and metadata structure matter

Where a cloud-native document has no standalone native file format, retain its raw API metadata and content representation and optionally add a realistic export such as DOCX, XLSX, CSV, or PDF. Do not silently treat the export as identical to the live source object.

### 5. Freeze the dataset

- Assign a dataset version.
- Record generation configuration and random seed privately.
- Generate checksums for source files.
- Prevent product development from mutating the source pack.

### 6. Evaluate independently

Only after freezing should reviewers inspect the private world and source data to create an evaluation set.

## Realistic imperfection model

Messiness should be governed by source-specific behaviour rather than random corruption.

### Identity variation

- Legal name versus trading name
- Abbreviations
- Previous organisation names
- Parent and subsidiary confusion
- Duplicate contacts
- Product nicknames
- Serial numbers with punctuation or transcription differences

### Timing variation

- Reporting delays
- Batched distributor submissions
- Late data entry
- Backdated formal records
- Different export cut-off dates
- Time-zone differences

### Completeness variation

- Missing device identifiers
- Unknown product version
- Unavailable attachments
- Partial customer descriptions
- Actions without final evidence
- Service findings not copied into the complaint record

### Classification variation

- Different vocabularies across support, service, and quality
- Default or catch-all categories
- Categories that change over time
- Human misclassification
- Multiple symptoms recorded as one issue

### Document variation

- Draft and approved versions
- Obsolete copies in personal folders
- Mismatched filenames and register metadata
- Scanned evidence
- Missing signatures or approvals
- References to renamed procedures

## QMS content required for V0

The fictional QMS should be coherent enough to provide context without attempting to reproduce an entire certified system.

### Company-level context

- QMS scope
- Organisation chart
- Roles and responsibilities
- Approval authority matrix
- Product catalogue
- Site and market overview
- Quality policy and objectives
- Process map
- Document naming and retention conventions

### Core procedures

- Document and record control
- Complaint handling
- PMS
- Vigilance or regulatory assessment
- Investigation and CAPA
- Nonconformity management
- Risk management
- Change control
- Training and competency
- Internal audit
- Management review
- Supplier control

### Templates and registers

- Document register
- Complaint form
- Investigation form
- PMS review template
- CAPA form
- Change request
- Risk record
- Training acknowledgement
- Audit finding
- Meeting minutes
- Action register

Documents should describe how the fictional company operates. They should not be written to tell the product what conclusion to reach.

## Evaluation plan

Evaluation is derived after source generation and kept separate from product inputs.

### Extraction evaluation

- Does each extracted field match its source?
- Is the source location cited correctly?
- Does the system avoid filling unknown values without evidence?

### Entity-resolution evaluation

- Which records genuinely refer to the same person, organisation, product, unit, or event?
- Which matches are ambiguous?
- Does the system avoid destructive merges without approval?

### Analysis evaluation

- Are calculations reproducible?
- Are appropriate denominators used?
- Are missing periods or late records disclosed?
- Can reviewers distinguish an observed pattern from a causal conclusion?

### Workflow evaluation

- Are missing-information requests directed to plausible owners?
- Do replies and attachments return to the correct work item?
- Are approval boundaries respected?
- Is the complete evidence and decision history retrievable?

### Quality-expert review

A qualified reviewer may assess whether an output is useful for further review, but the dataset should not declare that a specific regulatory or CAPA decision is objectively required unless that decision is explicitly represented as an authorised event in the simulated company history.

## Multi-company expansion

Do not create several shallow companies initially. Complete and freeze one rich company first.

Additional companies should differ structurally:

- Software-focused medical-device manufacturer
- Physical-device manufacturer using a contract manufacturer
- Australian sponsor or distributor rather than the manufacturer
- Small single-product company
- Larger multi-site organisation

Every record must include tenant ownership at the platform layer. Raw source identifiers may collide across companies, so identity resolution must always occur inside a tenant boundary.

## Work packages for later delegation

Delegation should begin only after the company model, schemas, timeline rules, and identifier conventions are approved.

### Company modeller

- Organisation, employees, roles, products, customers, and suppliers
- Business rules and time-dependent state

### Operational-data generator

- ERP, CRM, installed base, shipments, service, and support exports

### Communications generator

- Email threads, attachments, meeting records, and action tracking

### QMS author

- Controlled procedures, templates, registers, revisions, training, audits, and quality records

### Evaluation owner

- Private world-to-source mappings
- Post-generation review labels
- Integrity checks and benchmark cases

Each owner must generate against the shared world model and source contract without editing another source to force a cross-system result.

## Build sequence

### Step 1: Approve the company model

- Company boundaries
- Products and markets
- Teams and responsibilities
- Systems in use
- Simulation period

### Step 2: Approve source contracts

- Schemas
- Identifiers
- Ownership
- Update behaviour
- Export formats
- Natural data-quality characteristics

### Step 3: Build the private simulator

- Entity state
- Event types
- Event dependencies
- Operational rates and timelines
- Source visibility rules

### Step 4: Generate foundational data

- People
- Organisations
- Products
- Suppliers
- Devices and lots
- Documents and versions

### Step 5: Generate longitudinal operations

- Sales and shipments
- Customer interactions
- Support and service
- Communications and meetings
- Quality activities
- Training, audits, and reviews

### Step 6: Render independent source exports

- Preserve each system's naming, timing, schema, and omissions.
- Do not add canonical mappings to the product-facing data.

### Step 7: Run integrity checks

- Validate referential integrity inside each source where expected.
- Confirm plausible date ordering and state transitions.
- Confirm that cross-source variation follows configured behaviour.
- Check that no real company information is present.

### Step 8: Freeze version 0.1

- Record the generation version and private seed.
- Checksum product-facing inputs.
- Treat the pack as immutable during initial development.

### Step 9: Create independent evaluation data

- Review private events and observable sources.
- Mark supported matches, ambiguities, and source-backed facts.
- Keep evaluation files inaccessible to normal ingestion.

### Step 10: Build and test the product

- Ingest raw systems.
- Construct context.
- Measure extraction and linking.
- Add PMS analysis and actions only after the underlying context is reliable.

## Acceptance criteria for the mock layer

- The company has a coherent 12–18 month history.
- Each source has a clear business purpose and owner.
- Source records can stand alone as plausible exports.
- Cross-source relationships exist without universal shared identifiers.
- Missingness and inconsistency arise from documented system behaviour.
- Raw inputs contain no desired product conclusions or evaluation labels.
- Product outputs can cite the exact source evidence used.
- The dataset includes routine, uninteresting operations as well as unusual activity.
- A product failure cannot be hidden by changing the dataset after evaluation.
- No real employer, patient, customer, product, or incident information is present.
- The generation rules support additional companies without assuming medtech-specific fields in the platform core.

## Immediate next deliverables

The registers these must be able to reconstruct are defined in [`REGISTER-SHAPES-V0.md`](REGISTER-SHAPES-V0.md), whose §11 lists the imperfections the generator is required to produce.

Before generating bulk records, create and review:

1. `company-model.yaml` describing the fictional organisation and products.
2. `source-contracts/` containing one schema and behaviour specification per source system.
3. `world-events.schema.json` defining private event types.
4. `generation-config.yaml` defining time range, volumes, rates, and source-observation behaviour.
5. `source-manifest.schema.json` defining product-facing export metadata.
6. A two-week miniature dataset used only to validate the generator architecture.

Once those are coherent, generate the full 18-month company history and freeze the first reusable mock-data release.
