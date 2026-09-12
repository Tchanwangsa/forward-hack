# Asteria Medical Systems Mock Scenario

## Purpose

Define the company-specific scenario used to generate the initial mock dataset. This file supplies the fictional company, products, operating period, activities, and volume targets.

The reusable generation rules, source-system behaviours, dataset boundaries, and evaluation safeguards are defined in [`plan/MOCK-DATA.md`](../MOCK-DATA.md).

## Fictionality boundary

All names, products, devices, customers, suppliers, employees, records, and events must be fictional.

Product descriptions must remain high-level and fictional. Do not copy a real employer's device architecture, intended use, hazards, complaint patterns, internal terminology, or records.

## Company profile

Name: **Asteria Medical Systems Pty Ltd**

- Australian medical-device manufacturer
- Approximately 80 employees
- Headquarters and primary quality team in Melbourne
- One external contract manufacturer
- Sells in Australia and selected European markets
- Operates a quality management system based on ISO 13485
- Uses a mixture of SaaS tools, shared drives, spreadsheets, email, and internal databases
- Has enough organisational maturity to possess controlled procedures, but still relies on manual coordination

## Products

The detailed fictional portfolio is defined in [Asteria product portfolio](asteria/products.md).

- **PulseOne:** a reusable bedside receiver that displays heart rate, respiratory rate, skin temperature, and movement received from one patient's patch and alerts ward staff to configured limits or connection problems.
- **PulsePatch:** a disposable upper-chest sensor used for up to 72 hours and supplied in lot-controlled boxes.

Together, the products give Asteria both unit-level and lot-level post-market traceability without creating unrelated product families solely to increase dataset variety.

## Entity model

The proposed entities, boundaries, relationships, and seed order are defined in [Asteria entity model](asteria/entities.md).

## Simulation period

Generate 18 months of company activity.

The timeline should contain ordinary operational changes such as:

- Employee onboarding, leave, role changes, and departures
- Customer and distributor onboarding
- Product shipments and replacements
- Software and document releases
- Supplier deliveries
- Service and maintenance activity
- Customer questions and feedback
- Support tickets and complaints
- Meetings and action items
- Training assignment and completion
- Internal audits and routine findings
- Nonconformities and occasional quality actions
- Reporting and review cycles

These changes are world events, not planted product findings. Generate their downstream effects according to the source-system behaviours in the mock data layer instructions.

## Initial source and connector mix

Asteria should combine seeded live services with frozen source-native files. The first slice should be small enough to operate manually but varied enough to demonstrate authentication, synchronisation, parsing, provenance, and cross-source reconciliation.

### Live-backed sources

| Source | Sample Asteria content | Important behaviours to exercise |
|---|---|---|
| Gmail | Customer complaints, distributor correspondence, internal forwards, supplier replies | Threads, quoted text, labels, recipients, attachments, delayed replies |
| Google Drive | Shared quality folders, working documents, exported evidence, obsolete copies | Folder hierarchy, sharing, permissions, duplicate filenames, modified timestamps |
| Google Docs | Draft procedures, investigation notes, meeting minutes, review reports | Document structure, tables, comments, revisions, links |
| Google Sheets | Complaint tracker, action register, shipment reconciliation, PMS calculations | Multiple tabs, formulas, typed cells, hidden rows, filters, stale copies |
| Google Calendar | Review meetings, audit dates, training sessions, action deadlines | Attendees, recurrence, cancellations, time zones, changed times |
| Slack | Support escalation, quality triage, engineering discussion, meeting follow-up | Channels, threads, mentions, reactions, edits, files, informal decisions |

Use dedicated fictional accounts and workspaces only. Live services are test surfaces, not the private source of truth.

### Frozen and source-native files

The Asteria source pack should include a deliberate mix of:

- CSV exports from ERP, CRM, installed-base, and service systems
- XLSX registers and PMS working analyses with formulas and multiple tabs
- JSON or JSONL support tickets, Slack messages, and raw connector responses
- EML customer, distributor, supplier, and internal email threads
- ICS calendar events and recurring review meetings
- DOCX draft procedures, meeting minutes, investigations, and reports
- Text-based PDF approved records and supplier documentation
- Scanned PDF signed forms and historical records
- PNG or JPEG device photographs, screenshots, packaging labels, and damage evidence
- ZIP exports from chat, support, or document systems where archive structure matters

Some records should exist in more than one representation—for example, a Google Doc plus an approved PDF rendition—but each representation must retain its own source identity and timestamps. They are related evidence items, not automatic duplicates.

### Later connector candidates

After the Google Workspace and Slack path works end to end, add one source from each distinct operational category:

- CRM: HubSpot or Salesforce
- Customer support: Zendesk or Intercom
- Engineering work: Jira and Confluence, Linear, or GitHub Issues
- Microsoft document environment: SharePoint, OneDrive, Outlook, and Teams
- Lightweight operational database: Airtable
- File repository: Dropbox or Box

Choose additions for the new data behaviour they introduce, not merely to increase the connector count.

## Approximate V0 scale

Use enough history to produce realistic joins and routine noise.

| Data type | Initial target |
|---|---:|
| Employees | 50–80 |
| Customers, clinics, and distributors | 40–70 |
| Suppliers | 10–20 |
| Product families | 2 |
| Product or software versions | 5–8 |
| Serialised units | 1,000–3,000 |
| Disposable lots | 20–40 |
| Orders and shipments | 1,000–2,500 |
| CRM activities | 500–1,000 |
| Support tickets | 300–600 |
| Emails | 800–1,500 messages |
| Service work orders | 150–300 |
| Formal complaint records | 80–180 |
| Controlled documents | 30–50 |
| Document versions | 50–90 |
| Training assignments | 300–600 |
| Meetings | 40–80 |
| Audits and findings | 4–8 audits, 10–25 findings |
| CAPAs and nonconformities | Small, plausible operational totals |

For the first implementation slice, generate a representative subset of this scale. Preserve schemas and generation rules so volume can be increased without redesigning the dataset.
