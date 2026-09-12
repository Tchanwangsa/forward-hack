# Asteria Product Portfolio

## Purpose

Define Asteria's fictional product portfolio before generating customers, device units, lots, shipments, service activity, support records, or quality workflows.

This document establishes stable product facts and lifecycle rules. It must not prescribe complaint patterns, safety signals, investigation outcomes, or CAPAs. Those must emerge from the simulated business history.

## What the product is

Asteria sells a wireless hospital-ward monitoring system for adult patients recovering after surgery.

- **PulsePatch** is an adhesive electronic patch placed on the patient's upper chest. It measures heart rate, respiratory rate, skin temperature, and movement.
- **PulseOne** is the reusable bedside receiver and display paired with that patient's patch. It shows the measurements and alerts ward staff when a configured threshold is crossed or the patch stops communicating.
- A small **clinical dashboard** lets staff at the nurses' station see the same status for multiple PulseOne units.

The product is used between routine nurse observations on a general ward. It is not an ICU monitor, does not diagnose a condition, and is not intended to be the sole way staff detect an emergency.

The two commercial product families are deliberately different:

- PulseOne is reused, cleaned, serviced, updated, and tracked by serial number.
- PulsePatch is used on one patient for up to 72 hours, discarded after use, and tracked by manufacturing lot and expiry date.

## What happens during use

1. A nurse applies a new PulsePatch to a post-operative patient.
2. The nurse pairs the patch to a PulseOne unit assigned to that bed.
3. PulsePatch sends heart rate, respiratory rate, skin temperature, and movement readings to PulseOne.
4. PulseOne displays current readings and recent trends.
5. PulseOne displays and sounds an alert when a configured limit is crossed, the signal is lost, or the patch needs attention.
6. PulseOne forwards status information to the nurses' station dashboard when the hospital network is available.
7. At discharge or after 72 hours, the patch is discarded. PulseOne is cleaned and returned for reuse.

## Intended setting and users

The initial use setting is an adult general hospital ward caring for patients during the first few days after surgery.

Typical users include:

- Nurses and clinical support staff who set up and monitor patients
- Biomedical engineering teams that receive, configure, inspect, and maintain reusable units
- Hospital procurement and stores teams that manage disposable stock
- Distributor support and service personnel in markets served through a local distributor
- Asteria support, service, quality, regulatory, product, and engineering employees

The purchaser is normally a hospital or hospital network. Biomedical engineering manages the reusable units, procurement manages PulsePatch stock, nurses use the system, and Asteria or its distributor provides support and service.

Exact regulatory classifications and jurisdiction-specific registrations remain out of scope until the regulatory scenario is deliberately defined.

## System relationship

```text
PulsePatch on patient's chest
  heart rate | breathing rate | skin temperature | movement
                    |
              wireless link
                    |
                    v
PulseOne at the bedside
  shows readings | sounds alerts | stores short device logs
                    |
              hospital network
                    |
                    v
Nurses' station dashboard
  shows the status of multiple beds
```

The clinical dashboard is supporting software, not a third commercial product family in V0.

## What the mock dataset tracks

The quality platform is not a patient-monitoring application. The mock dataset tracks the product and business evidence needed for post-market quality work.

### PulseOne tracking

- Serial number and product code
- Hardware revision and installed software version
- Customer, hospital site, and last known ward or location
- Shipment, installation, transfer, loan, and replacement history
- Configuration and software-update observations
- Cleaning, inspection, service, repair, RMA, and decommissioning records
- Short diagnostic logs attached to selected support or service cases
- Customer-reported problems and technician findings

### PulsePatch tracking

- Product code and product revision
- Manufacturing lot and expiry date
- Box and shipment quantities
- Contract manufacturer and relevant supplier-component lots
- Customers and distributors that received each lot
- Returned samples, label photographs, and customer-reported problems

### Use-session tracking

Where necessary to connect evidence, a use session may record:

- A synthetic encounter ID
- PulseOne serial number
- PulsePatch lot number
- Hospital site
- Start and end timestamps
- Software version observed during use

V0 does not contain patient names, medical-record numbers, full clinical histories, or a warehouse of raw physiological readings. Selected fictional log excerpts may contain timestamps, connection status, alert codes, and summary values only when they are evidence attached to a support, service, or quality record.

## PulseOne

### Product definition

PulseOne is a reusable bedside receiver and display assigned to one patient at a time. It receives measurements from that patient's PulsePatch, shows them to ward staff, produces local alerts, and relays status to the nurses' station dashboard.

The unit has:

- A display showing heart rate, respiratory rate, skin temperature, movement status, connection state, and battery state
- A speaker and visual alert indicator
- Short-range communication with PulsePatch
- Network connectivity for synchronisation with the clinical dashboard
- An internal rechargeable battery
- Embedded software with an independently recorded version
- Configuration settings established during installation or service
- A device label carrying customer-visible identifiers

### Commercial configuration

Initial commercial model: **PulseOne P1-100**.

A shipment may contain:

- One PulseOne unit
- One docking and charging station
- One external power supply
- A quick-start guide
- Region-specific labelling
- Optional spare field-replaceable modules

Accessories and replacement modules are orderable items but are not separate product families in V0.

### Unit-level identity

Each PulseOne unit has:

- A unique serial number
- A product code
- A hardware revision
- A manufacturing completion date
- An initial embedded-software version
- A market configuration
- A shipment and ownership history
- Zero or more registration, installation, service, transfer, return, and decommissioning observations

Serial numbers are stable product identifiers. Their formatting may vary when copied into other systems, emails, spreadsheets, or handwritten evidence.

### Hardware revision model

Use a small, controlled revision sequence rather than many arbitrary variants:

| Revision | Lifecycle role | Compatibility intent |
|---|---|---|
| H1 | Initial released configuration | Supports the original field-replaceable modules |
| H2 | Later released configuration | Maintains PulsePatch compatibility while allowing updated internal modules |
| H2.1 | Minor manufacturing revision | Does not create a new customer-facing model |

Revision effective dates and production ranges will be established on the Asteria timeline. A revision must not be treated as evidence of a quality problem merely because it is newer.

### Field-replaceable components

The initial serviceable component catalogue includes:

- Battery module
- Communications module
- Docking connector assembly
- External power supply
- Protective rear cover

Each component has its own part number and revision. Service records may name a component using a formal part number, technician shorthand, or only a description.

### Embedded software

PulseOne software uses semantic customer-visible versions such as `1.0.0`, `1.1.0`, and `1.1.1`. Internal build identifiers may also exist but should not appear consistently across every source.

A software release records:

- Customer-visible version
- Internal build identifier
- Release date
- Compatible hardware revisions
- Release notes
- Approval status and effective date
- Installation method

A released version does not imply that every installed unit was upgraded. Version observations are time-bound and may become stale.

### Lifecycle

A typical PulseOne lifecycle is:

```text
manufactured → released → shipped → received → registered or installed
             → configured → used → serviced or transferred → decommissioned
```

Not every source observes every stage. Shipment does not prove installation, registration does not prove current location, and a service record may provide the most recent trustworthy configuration observation.

### Service model

PulseOne may receive:

- Remote configuration support
- Preventive inspection
- Software update
- Field-replaceable module replacement
- Depot repair under an RMA
- No-fault-found inspection
- Replacement by another serialised unit
- Decommissioning

Service work must preserve the distinction between the customer's reported symptom, the technician's observations, work performed, test results, and final disposition.

## PulsePatch

### Product definition

PulsePatch is a sterile, battery-powered adhesive sensor placed on the upper chest of one adult patient. It measures heart rate, respiratory rate, skin temperature, and movement, then sends those measurements to PulseOne over a short-range wireless connection. It is not individually serialised and is discarded after use.

Each pouch carries:

- Product code
- Manufacturing lot
- Expiry date
- Storage information
- Customer-facing device identifier where applicable to the fictional market configuration

### Commercial configuration

Initial commercial model: **PulsePatch PP-72**, intended for up to 72 hours of use.

Packaging hierarchy:

```text
individual sterile pouch → box of 10 → shipping carton
```

The individual pouch and box identify the manufactured lot. Orders and shipments generally track boxes or cartons, while customer correspondence may refer to individual patches.

### Lot-level identity

Each manufactured lot has:

- A unique lot code
- Product code and revision
- Manufacturing and release dates
- Expiry date
- Quantity manufactured, released, scrapped, and distributed
- Contract-manufacturer production reference
- Relevant supplier-component lots
- Markets and customers supplied through shipment allocations

Lot allocation may be recorded at shipment-line level. A customer report may omit the lot, provide a partial code, or include a photograph of the pouch rather than structured text.

### Product revision model

PulsePatch uses controlled product revisions that may affect material, labelling, packaging, or manufacturing instructions while retaining the PP-72 commercial model.

Product revision, packaging revision, and artwork revision must be separate fields. A change to one must not silently imply a change to the others.

### Shelf-life and stock movement

Shelf-life is calculated from the manufacturing date according to the released product specification. Stock can move through:

```text
contract manufacturer → Asteria inventory → distributor or customer
                      → local stock location → used, expired, returned, or discarded
```

Shipment records establish distribution, not confirmed patient use. Distributor reporting may arrive in batches and may not provide full downstream allocation.

### Supplier dependencies

PulsePatch has a small fictional bill of materials with supplier-controlled inputs, such as:

- Sensor substrate
- Skin-contact adhesive
- Electronics assembly
- Sterile pouch material
- Printed label stock

Supplier lots are private manufacturing context and should surface in product-facing records only where an operational process would record them, such as receiving, manufacturing, nonconformity, or supplier documentation.

## Compatibility model

Compatibility must be explicitly represented rather than inferred only from dates.

The compatibility table should relate:

- PulseOne hardware revision
- PulseOne embedded-software version
- PulsePatch product revision
- Market configuration
- Effective period

Most released combinations should be ordinary and supported. Unsupported, unverified, or obsolete combinations may exist as lifecycle states, but must not be inserted merely to create a predetermined finding.

## Customer and client shape implied by the portfolio

The initial Asteria dataset should represent a small-to-medium regulated manufacturer whose quality work spans durable equipment and consumables.

Likely customer organisations include:

- Public and private hospitals operating several PulseOne units
- Day hospitals or recovery clinics operating a small fleet
- Hospital networks with central procurement and multiple ship-to sites
- European distributors holding stock and providing first-line support
- Evaluation sites using a limited number of units before purchase

This product model is especially useful for testing customers of the quality platform that have:

- Approximately 50–250 employees
- One or two principal product families
- A mixture of direct and distributor sales
- Serialised reusable devices, lot-controlled consumables, or both
- Embedded software and field configuration
- Outsourced manufacturing or critical suppliers
- Separate support, service, commercial, engineering, and QMS records
- Manual spreadsheets and email coordination between those systems

It does not initially optimise for pharmaceutical manufacturers, very large multi-site enterprises, pure software companies, or organisations whose product has no post-market service or distribution traceability.

## Required source-system footprint

Product facts should naturally appear across different sources:

| Product fact | Likely authoritative or useful sources |
|---|---|
| Product code and sellable configuration | ERP product catalogue, approved product documentation |
| Serial number and manufacturing configuration | Product database, manufacturing or release records |
| Lot and expiry | ERP lot allocation, manufacturing release record, label image |
| Shipment destination | ERP shipment |
| Current installation or ownership | Registration, installed-base observation, service visit |
| Software version | Product database observation, installation record, service record, support evidence |
| Customer-reported experience | Email, support ticket, CRM note, distributor report |
| Technician findings | Service work order, RMA inspection, photographs |
| Formal quality assessment | QMS complaint or investigation record |
| Approved product or process change | QMS change record and controlled document versions |

No single source should contain a perfectly current, complete view of every product fact.

## Decisions intentionally deferred

Define these only when their downstream simulation is ready:

- Exact regulatory classification by market
- Exact clinical performance claims and alarm behaviour
- Detailed risk and hazard analysis
- Manufacturing process parameters
- Sterilisation method and validation details
- Specific complaint rates or failure modes
- Recall, vigilance, or field-action scenarios
- Predetermined investigation or CAPA outcomes

Deferring these decisions prevents the entity seed from quietly encoding the product discoveries that the application is later expected to make.
