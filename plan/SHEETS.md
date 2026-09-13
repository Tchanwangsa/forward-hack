# Google Sheets — the live register surface

**What this is.** The customer's registers now live as seven Google Sheets rather than
seven `.xlsx` files on someone's laptop. This is the integration contract: what exists,
how an agent authenticates, and what it is allowed to write.

Companions: [`REGISTERS.md`](REGISTERS.md) (the eleven registers and the provenance
rules), [`ARCHITECTURE.md`](ARCHITECTURE.md) (tier boundaries and human gates).

---

## The topology — seven workbooks, eleven registers

One Google Sheet per workbook, mirroring what the customer actually keeps. Three of
them hold more than one tab, which is how seven workbooks carry eleven registers.

| Workbook | Tabs | Capture-fed? |
|---|---|---|
| Complaint Register | Complaints | yes |
| PM Client Communications Log | Client Communications | yes |
| PM Customer Organisations and Hubs Record | Organisations · PulseOne Hub Inventory · PulsePatch Stock Allocation | **no — reference** |
| PM Data Check and Troubleshooting Log | Data Check & Troubleshooting | yes |
| PM Incident and Outage Log | Incidents & Outages | yes |
| PMS Plan and Report Register | PMS Documents · Indicators & Thresholds · PMS Review Meetings | **no — reference** |
| Product Return and Replacement Register | Returns & Replacements | yes |

Seven rather than one is not only realism. Access is granted per spreadsheet, so the
agent can hold the Incident log without holding the Complaint register — which is the
answer when someone asks what stops it touching complaints.

### Naming a register

A register is named by its **workbook and tab** — *PM Incident and Outage Log →
`Incidents & Outages`* — because three workbooks hold more than one. Where the other
plan documents name a register, they mean the live sheet.

### The `.xlsx` files are seed, not the register

`mock-company/registers/*.xlsx` define the column shapes and carry the verified demo
fixtures — 737 incident rows, the planted stories, the deliberate mess. They are pushed
**once** into the live sheets and are never written to again. Nothing reads them at
runtime and no agent writes to them.

After the push, the Google Sheet is the register. A row that exists only in the `.xlsx`
does not exist as far as the product is concerned, and re-pushing overwrites whatever
the sheet holds — including rows an agent has committed since.

---

## Authentication

A **service account**, because capture bots run headless and there is no browser for
an OAuth consent screen.

- GCP project `pms-agent-508511`, **Google Sheets API** enabled (not the Drive API —
  the agent never browses Drive)
- Identity: `capture-agent@pms-agent-508511.iam.gserviceaccount.com`
- Scope: `spreadsheets` only
- Access is granted by a human **sharing a spreadsheet they own** with that address as
  Editor. Revoking is unsharing the file.

The key is a JSON file that lives outside the repository and is never committed. Each
developer places it wherever they like and points `REGISTER_SHEETS_CREDENTIALS` at it.

**Never create the register spreadsheets from the service account.** A file it creates
lives in its own Drive, which no human can browse, and is orphaned if the account is
deleted. A person creates the sheet; the agent is invited to it.

---

## Configuration contract

Eight environment variables. No secret material beyond the path to the key — the sheet
ids are not secrets, the sharing is what grants access. A pasted spreadsheet URL is
accepted anywhere an id is.

```
REGISTER_SHEETS_CREDENTIALS                     path to the service-account JSON key
SHEET_COMPLAINT_REGISTER                        one per workbook, URL or bare id
SHEET_CLIENT_COMMUNICATIONS_LOG
SHEET_CUSTOMER_ORGANISATIONS_AND_HUBS
SHEET_DATA_CHECK_AND_TROUBLESHOOTING_LOG
SHEET_INCIDENT_AND_OUTAGE_LOG
SHEET_PMS_PLAN_AND_REPORT_REGISTER
SHEET_PRODUCT_RETURN_AND_REPLACEMENT_REGISTER
```

---

## What an agent may write

The provenance rules in [`REGISTERS.md`](REGISTERS.md) §6 are the specification. In a
Sheets implementation they come out as:

| Rule | In practice |
|---|---|
| No capture agent writes to a reference register (§7) | The two reference workbooks are a deny-list, checked before any API call |
| A bot never commits a row | A bot writes to the draft queue only; a human moves it into the register |
| A commit needs a named human | The reviewer's name is required and recorded |
| Source rows are never edited (§6.1) | Every write is an append. No cell of an existing row is updated |
| A completion never lands in the source row (§6.2) | Completions stay in the capture layer with their evidence |
| A drafted row names its artifact (§6.3) | `Captured From` is mandatory — a telemetry event id, a message-id, a transcript range |
| A rejection is a record, not a deletion (§6.5) | The verdict is stamped with a reviewer and a rationale; nothing is removed |

Committed rows carry `Row Origin = agent` and `Captured From = <artifact pointer>`,
columns that already exist in all five capture-fed registers.

---

## Practical constraints

- **An `.xlsx` uploaded to Drive is not a Google Sheet.** Drive keeps it as an Excel
  blob and the Sheets API refuses it — *"the document must not be an Office file"*.
  Registers must be native sheets. Native ids are 44 characters; a 33-character id is
  an upload.
- **Write values as `RAW`.** With `USER_ENTERED`, Sheets reinterprets `1.1.0`,
  `SN-0042` and the date columns. The dirty variance in this dataset — `SN 4730`
  beside `PO-P1-004507` — is deliberate and must survive the round trip.
- **Read quota is 60 requests/min/user** (300 writes/min/project). A full sweep across
  eleven tabs exceeds it. Resolve a draft against the one workbook that holds it
  rather than scanning all of them.

---

## Where this sits relative to Postgres

[`ARCHITECTURE.md`](ARCHITECTURE.md) makes Postgres authoritative for workflow state,
review queues and the action log, and that does not change. Sheets is the **customer-
facing register surface**, downstream of the database: drafts and verdicts belong in
Postgres, and a row reaches a spreadsheet only once a human has approved it.

Any draft queue implemented inside a spreadsheet is demo scaffolding and should be read
as temporary.
