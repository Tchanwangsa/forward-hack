# Asteria Entity Model

## Purpose

Define the stable things that exist in Asteria's simulated business world before generating operational activity, documents, or quality workflows.

This file contains only Asteria's custom ontology. Platform tenancy, ingestion state, access control, and cross-customer data isolation are outside its scope and must not appear in Asteria's private world or source data.

This model distinguishes four concepts:

```text
Entity
  A stable thing with identity: organisation, person, product, unit, lot

Event
  Something that happens: shipment, installation, service, complaint report

Source record
  A system's evidence that something exists or happened: CRM row, email, ticket

Quality object
  A controlled record created to manage quality work: complaint, investigation, CAPA
```

A source record is not automatically the entity or event it describes. Several source records may refer to the same real-world entity or event, and they may disagree.

## Scope boundary

Asteria's ontology includes:

- Asteria itself, its legal identity, internal sites, departments, and people
- External organisations and people that Asteria interacts with
- Asteria's products and traceable product instances
- Commercial, operational, service, communication, and quality objects belonging to Asteria's business history

Hospitals, distributors, suppliers, and the contract manufacturer are external organisations. They participate in Asteria's business history, but they are not organisational units inside Asteria.

Use `customer_organisation`, `distributor`, `supplier`, and `site` for specific relationships. Avoid the generic word `client`.

## Layer 1: Asteria internal organisation

These entities define who Asteria is and who can own or approve work.

| Entity | What it represents | Example relationship |
|---|---|---|
| Company | The root identity for the simulated business | Asteria Medical Systems |
| Legal entity | Asteria's registered corporate identity | Asteria Medical Systems Pty Ltd |
| Internal site | Asteria office, warehouse, or service location | Melbourne headquarters |
| Department | Organisational function | Quality, support, service, engineering |
| Person | A fictional individual | Employed by Asteria or an external organisation |
| Employment | A person's time-bounded relationship with Asteria | Has start date, end date, manager |
| Role | A reusable job or responsibility definition | Quality Manager, Service Technician |
| Role assignment | A person's time-bounded role | Person changes from engineer to team lead |
| Approval authority | Authority held for a scope and period | May approve complaint closure |

Do not store a person's current department, manager, and authority as timeless facts. These relationships can change during the 18-month simulation.

## Layer 2: external organisation network

These entities define the parties around Asteria.

| Entity | What it represents | Important distinctions |
|---|---|---|
| Organisation | Stable identity for an external legal or trading organisation | May have several names in source systems |
| Organisation relationship | Time-bounded relationship to Asteria | Customer, distributor, supplier, contract manufacturer |
| Customer account | Commercial representation of an organisation | Not necessarily identical to a legal entity |
| Hospital network | Parent grouping for hospitals | May buy centrally for several sites |
| Customer site | Physical hospital, clinic, warehouse, or office | Separate bill-to, ship-to, and use locations |
| Ward or care area | Operational location inside a hospital | Last-known device location, not a legal organisation |
| Distributor | Organisation that buys, holds, resells, and may support products | Can obscure the final user and delay reporting |
| Supplier | Organisation providing a component or service | May have approved and trading statuses |
| Contract manufacturer | Supplier that manufactures or packages product | Holds its own production references |
| Contact point | Email address, phone number, or shared mailbox | Belongs to a person or organisation for a period |

Organisation identity, commercial account identity, and physical site identity must remain separate.

## Layer 3: product master

These entities come from the [Asteria product portfolio](products.md).

| Entity | What it represents | Tracking level |
|---|---|---|
| Product family | PulseOne or PulsePatch | Portfolio |
| Commercial model | P1-100 or PP-72 | Customer-facing model |
| Sellable item | Orderable SKU, accessory, or replacement module | ERP catalogue |
| Product revision | Controlled design or manufacturing revision | Product configuration |
| Hardware revision | PulseOne hardware configuration | Device unit |
| Software release | Released PulseOne or dashboard software | Versioned software |
| Component part | Battery, communications module, adhesive, label stock | Part number and revision |
| Packaging configuration | Pouch, box, or shipping carton configuration | PulsePatch distribution |
| Artwork version | Approved label or packaging artwork | Document-controlled version |
| Compatibility rule | Supported combination over an effective period | Hardware, software, patch revision, market |

These are stable master entities. Releases and effective-date changes are events applied to them.

## Layer 4: traceable product instances

These entities represent physical product that can move through the world.

| Entity | What it represents | Identity |
|---|---|---|
| Device unit | One physical PulseOne | Serial number |
| Manufactured lot | A quantity of PulsePatch made together | Lot code |
| Component lot | Supplier or manufacturing lot used in product | Supplier/internal lot code |
| Inventory item | Quantity of a lot or SKU at a stock location | Item, location, status |
| Stock location | Asteria, distributor, or customer storage location | Location identifier |
| Returned sample | A returned PulsePatch or other evidence sample | Return/sample identifier |

PulsePatch units are not individually serialised. Do not invent one entity per patch unless a particular returned sample needs its own evidence identity.

## Layer 5: commercial and distribution objects

These objects connect products to customers. Some behave like business records as well as lifecycle objects.

| Object | What it represents | Key relationships |
|---|---|---|
| Order | Customer's commercial request | Account, bill-to, order lines |
| Order line | Quantity of a sellable item | Product/SKU |
| Shipment | Physical dispatch | Ship-from, ship-to, shipment lines |
| Shipment line | Quantity and allocations shipped | SKU, device serials, PulsePatch lots |
| Distributor allocation | Distributor-reported onward supply | Distributor, downstream customer, lots/units |
| Registration | Customer-submitted claim about a unit | Device, organisation, site |
| Installation | Observed placement and configuration | Device, customer site, software version |
| Transfer | Movement between sites or owners | Device, from/to party or site |
| Replacement | One device supplied in place of another | Original unit, replacement unit, reason |

Shipment, registration, and installation are separate. None proves the other occurred.

## Layer 6: use and device observations

These objects provide enough context to relate product evidence without building a patient-record system.

| Object | What it represents | V0 privacy boundary |
|---|---|---|
| Use session | Period when one patch and one PulseOne were used together | Synthetic encounter ID only |
| Pairing observation | Evidence that a patch was paired with a device | No patient identity |
| Configuration observation | Software, hardware, and settings observed at a time | May become stale |
| Device log excerpt | Selected diagnostic evidence | Only attached to relevant cases |
| Alert summary | Summary of device-generated alerts for a session | No full physiological stream |

There is no patient entity in V0. Patient names, medical-record numbers, clinical histories, and complete physiological time series are excluded.

## Layer 7: support and service objects

| Object | What it represents | Important distinction |
|---|---|---|
| Support ticket | A request or conversation managed by support | May contain several reported issues |
| Reported issue | One customer's description of a concern | Not yet a formal complaint conclusion |
| Service case | Coordination of technical work | May connect several work orders |
| Work order | One service visit or depot task | Work performed by a technician |
| RMA | Authorisation and logistics for a return | Not the physical returned item itself |
| Inspection | Technician observations and test results | Separate from customer symptom |
| Repair | Work performed to restore a device | May replace components |
| Component replacement | Removal and installation of parts | Links device and component part/lot |
| Service disposition | Returned, replaced, no fault found, scrapped, etc. | Final technical disposition |

## Layer 8: communications and coordination

| Object | What it represents |
|---|---|
| Message | One email or chat message |
| Conversation or thread | Related messages in one source system |
| Attachment | File attached to a message, ticket, or record |
| Calendar event | Scheduled meeting or deadline |
| Meeting | Meeting that actually occurred |
| Decision | A decision with maker, time, scope, and evidence |
| Action | Assigned work with owner, due date, and status history |

A calendar event may be cancelled, and a scheduled event does not prove that a meeting occurred.

## Layer 9: quality and controlled content

These entities should be defined structurally now but populated only after ordinary operations are simulated.

| Entity | What it represents |
|---|---|
| Source record | Original system record retained as evidence |
| Evidence item | A citable piece of source content or attachment |
| Complaint | A formal quality record created after assessment |
| Investigation | Controlled work to establish facts and conclusions |
| Nonconformity | Failure to meet a specified requirement |
| CAPA | Controlled corrective or preventive action process |
| Risk item | Hazard, sequence, harm, control, or related risk record |
| Change request | Proposed controlled change |
| Controlled document | Logical procedure, form, plan, or report |
| Document version | One draft, approved, superseded, or obsolete version |
| Training assignment | Required training for a person and document version |
| Training completion | Evidence that assigned training was completed |
| Audit | Planned and performed audit activity |
| Audit finding | Observation or nonconformity produced by an audit |
| PMS review | Periodic review of post-market evidence |

Do not create a formal complaint for every support ticket. Complaint assessment is an event that may or may not create a complaint record.

## Core relationships

```text
Asteria Medical Systems
├── people, departments, roles, and approval authorities
├── product master
│   ├── PulseOne → hardware + software → device units
│   └── PulsePatch → revisions + packaging → manufactured lots
└── external organisation network
    ├── hospitals → sites → wards
    ├── distributors → downstream hospitals
    └── suppliers → component lots → product lots or serviced units

Customer order
  → shipment
    → PulseOne serial or PulsePatch lot allocation
      → registration / installation / use observation
        → support or service evidence
          → complaint assessment
            → optional controlled quality record
```

## Recommended seed order

1. **Internal organisation:** Asteria legal entity, sites, departments, roles, and a small initial employee roster.
2. **External network:** hospital networks, hospital sites, distributors, suppliers, and the contract manufacturer.
3. **Product master:** models, SKUs, revisions, software releases, components, packaging, and compatibility rules.
4. **Traceable inventory:** PulseOne units, PulsePatch lots, component lots, and initial stock positions.
5. **Commercial relationships:** customer accounts, contacts, contracts or territories, bill-to and ship-to relationships.
6. **Operational history:** orders, shipments, registrations, installations, transfers, and product use observations.
7. **Support and service history:** contacts, tickets, work orders, RMAs, inspections, repairs, and replacements.
8. **Source records:** render each system's partial view of the preceding entities and events.
9. **Quality workflows:** assess incoming information and create controlled records only when the simulated process calls for them.

Documents should not be generated as an isolated library before these entities exist. Controlled documents can be seeded early as company infrastructure, but transactional documents, emails, tickets, minutes, and quality records should be produced from entity relationships and events.

## First concrete seed

Start with a small foundation pack before generating the full target scale:

- 1 Asteria legal entity
- 3 internal sites: headquarters, warehouse, and service centre
- 8 departments
- 12 roles
- 20 named employees with time-bounded assignments
- 2 hospital networks containing 5 hospital sites
- 3 independent hospitals or clinics
- 1 European distributor with 3 downstream customer sites
- 1 contract manufacturer
- 6 component or service suppliers
- The PulseOne and PulsePatch product master
- 30 PulseOne units
- 3 PulsePatch lots

This is large enough to test identity, hierarchy, ownership, shipment, and traceability while remaining easy to inspect manually. Scale only after the relationships and source projections are correct.
