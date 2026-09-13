# Asteria Seed Roster

> **Private generator state — never ingested by the product.**
> This file is our answer key, not the application's input. The product must derive
> every person, organisation, and device from source records alone. See
> [`plan/MOCK-DATA.md`](../../MOCK-DATA.md) dataset layers.


The fixed cast for the mock dataset. Every email, ticket, shipment, and spreadsheet row must reference an ID from this file. Nothing is generated freehand.

Email domain for Asteria: `asteriamedical.com.au`

## Asteria employees (12)

| ID | Name | Department | Role |
|---|---|---|---|
| EMP-01 | Priya Raghunathan | Quality | Quality Manager — approves complaint closure |
| EMP-02 | Daniel Okonkwo | Quality | PMS Specialist — **primary demo user** |
| EMP-03 | Sarah Whitcombe | Quality | Quality Engineer — investigations |
| EMP-04 | Mei-Ling Tan | Support | Support Team Lead |
| EMP-05 | Jarrah Nguyen | Support | Support Representative |
| EMP-06 | Tom Beckett | Support | Support Representative |
| EMP-07 | Vikram Shetty | Service | Service Technician (depot) |
| EMP-08 | Alina Kovač | Service | Field Service Technician |
| EMP-09 | Rebecca Fontaine | Sales | Account Manager — VIC/SA/WA |
| EMP-10 | Hamish Doyle | Sales | Account Manager — NSW/QLD/Europe |
| EMP-11 | Yuki Tanaka | Engineering | Firmware Engineer |
| EMP-12 | Marcus Ellery | Engineering | Product Engineer — patch hardware |

## Customer organisations (8) and sites (15)

| Org ID | Organisation | Market | Email domain |
|---|---|---|---|
| ORG-01 | Northbridge Health Network | AU — VIC | northbridgehealth.org.au |
| ORG-02 | Yarra Valley Health | AU — VIC | yarravalleyhealth.org.au |
| ORG-03 | Southern Cross Hospitals Group | AU — NSW | schg.com.au |
| ORG-04 | Brisbane Riverside Medical Centre | AU — QLD | brisbaneriverside.com.au |
| ORG-05 | Adelaide Metro Health | AU — SA | adelaidemetrohealth.org.au |
| ORG-06 | Perth Coastal Private | AU — WA | perthcoastal.com.au |
| ORG-07 | St Brendan's Hospital Group | IE | stbrendans.ie |
| ORG-08 | Randstad Zorggroep | NL | randstadzorg.nl |

| Site ID | Site | Org | Location |
|---|---|---|---|
| SITE-01 | Northbridge General Hospital | ORG-01 | Coburg, VIC |
| SITE-02 | Northbridge Sunshine Hospital | ORG-01 | Sunshine, VIC |
| SITE-03 | Northbridge Day Surgery | ORG-01 | Preston, VIC |
| SITE-04 | Yarra Valley Hospital | ORG-02 | Lilydale, VIC |
| SITE-05 | Healesville Community Hospital | ORG-02 | Healesville, VIC |
| SITE-06 | Southern Cross Randwick | ORG-03 | Randwick, NSW |
| SITE-07 | Southern Cross Parramatta | ORG-03 | Parramatta, NSW |
| SITE-08 | Southern Cross Newcastle | ORG-03 | Newcastle, NSW |
| SITE-09 | Brisbane Riverside Hospital | ORG-04 | South Brisbane, QLD |
| SITE-10 | Adelaide Metro North | ORG-05 | Elizabeth, SA |
| SITE-11 | Adelaide Metro Central | ORG-05 | Adelaide, SA |
| SITE-12 | Perth Coastal Private Hospital | ORG-06 | Cottesloe, WA |
| SITE-13 | St Brendan's Dublin | ORG-07 | Dublin, IE |
| SITE-14 | St Brendan's Cork | ORG-07 | Cork, IE |
| SITE-15 | Randstad Ziekenhuis Delft | ORG-08 | Delft, NL |

## Contacts (30)

Two per site: one clinical voice and one technical or procurement voice. They report the same fault in completely different language, which is the point.

| ID | Name | Site | Role |
|---|---|---|---|
| CON-01 | Fiona Marsh | SITE-01 | Nurse Unit Manager |
| CON-02 | Ravi Chandra | SITE-01 | Biomedical Engineer |
| CON-03 | Amanda Sze | SITE-02 | Nurse Unit Manager |
| CON-04 | Peter Kowalski | SITE-02 | Biomedical Engineer |
| CON-05 | Grace Liu | SITE-03 | Clinical Educator |
| CON-06 | Dean Whitfield | SITE-03 | Procurement Officer |
| CON-07 | Kate Brennan | SITE-04 | Nurse Unit Manager |
| CON-08 | Sam Adeyemi | SITE-04 | Biomedical Engineer |
| CON-09 | Louise Pham | SITE-05 | Nurse Unit Manager |
| CON-10 | Craig Sutton | SITE-05 | Procurement Officer |
| CON-11 | Nadia Haddad | SITE-06 | Nurse Unit Manager |
| CON-12 | Elliot Zhang | SITE-06 | Biomedical Engineer |
| CON-13 | Bianca Rossi | SITE-07 | Clinical Educator |
| CON-14 | Josh Tui'one | SITE-07 | Biomedical Engineer |
| CON-15 | Helen Byrne | SITE-08 | Nurse Unit Manager |
| CON-16 | Mark Delaney | SITE-08 | Procurement Officer |
| CON-17 | Tanya Robinson | SITE-09 | Nurse Unit Manager |
| CON-18 | Ash Mehta | SITE-09 | Biomedical Engineer |
| CON-19 | Cheryl Novak | SITE-10 | Nurse Unit Manager |
| CON-20 | Devan Patil | SITE-10 | Biomedical Engineer |
| CON-21 | Ingrid Solberg | SITE-11 | Clinical Educator |
| CON-22 | Wayne Fletcher | SITE-11 | Procurement Officer |
| CON-23 | Megan Ashcroft | SITE-12 | Nurse Unit Manager |
| CON-24 | Trent Baker | SITE-12 | Biomedical Engineer |
| CON-25 | Aoife Gallagher | SITE-13 | Nurse Unit Manager |
| CON-26 | Cormac Byrne | SITE-13 | Biomedical Engineer |
| CON-27 | Niamh Cassidy | SITE-14 | Clinical Educator |
| CON-28 | Declan Moore | SITE-14 | Procurement Officer |
| CON-29 | Sanne de Vries | SITE-15 | Nurse Unit Manager |
| CON-30 | Joost Bakker | SITE-15 | Biomedical Engineer |

## Deliberate traps

These are planted so entity resolution has something real to solve. Without them the demo is trivial and unimpressive.

| Trap | Where | What the agent must handle |
|---|---|---|
| Same person, two addresses | CON-01 appears as `fiona.marsh@` and `f.marsh@` | One person, not two |
| Shared surname, different orgs | CON-15 Helen Byrne (ORG-03) and CON-26 Cormac Byrne (ORG-07) | Do not merge |
| Contact moves site | CON-04 transfers SITE-02 → SITE-01 mid-timeline | Records before and after belong to different sites |
| Shared mailbox | `biomed@schg.com.au` sends on behalf of CON-12 and CON-14 | Attribute to the right person from the signature |
| Org named loosely | ORG-03 written as "Southern Cross", "SCHG", "Sth Cross Hospitals" | Same organisation |
| Timezone lag | ORG-07 and ORG-08 reply overnight AEST | Thread ordering must not imply delay in response |
| Site vs ship-to mismatch | ORG-01 orders centrally, delivers to SITE-01/02/03 | Buyer is not the user |

## Resolved elsewhere

The cast above is 12 employees, 8 organisations, 15 sites and 30 contacts. The US market decision
([`REGISTER-SHAPES-V0.md` §10.1](../../REGISTER-SHAPES-V0.md)) adds one employee, three organisations,
two sites and eight contacts — they are specified in
[`GENERATION-CONTRACT-V0.md` §4](GENERATION-CONTRACT-V0.md), which also adds three traps that only
exist once there is a second regulatory party. **Totals at freeze: 13 · 11 · 17 · 38.**

The lot codes, serial number ranges, and date windows this file deferred are now fixed in
[`GENERATION-CONTRACT-V0.md` §2–3](GENERATION-CONTRACT-V0.md), following the choice of a PulseOne
signal. Note in particular that `SN-4471` and `SN-4417` are **both real, shipped, distinct units at
different sites** — that is what makes the transcription conflict dangerous rather than cosmetic.

## Generation rules this roster implies

The product never sees this file. That puts three hard constraints on generation.

**No ID leakage.** `EMP-02`, `ORG-03`, `CON-14` must never appear in a single email, ticket, or spreadsheet cell. Each source system invents its own keys — the CRM has `A-1042`, the support tool has `TKT-8891`, email has only a display name and address. If the agent can grep an ID, entity resolution is free and the demo proves nothing.

**No orphans.** An entity that appears in zero source records does not exist for the demo. Every one of the 12 employees, 8 organisations, 15 sites, and 30 contacts needs enough footprint across sources to be inferable — a signature block, a ticket assignment, a ship-to line, a calendar attendee. Coverage is a generation checklist item, not an accident.

**Attributes must be inferable, not asserted.** The product cannot know CON-02 is a Biomedical Engineer because this table says so. It must read it off an email signature, a ticket queue, or who gets CC'd on service reports. Any attribute we want the agent to derive has to be observable somewhere.

## What this roster is for

Two things, and only two:

1. **Input to the generator**, so 18 months of source data stays internally coherent.
2. **The answer key**, so we can score what the agent derived against what is true.

The second is where the metric comes from. Held-out, the roster turns into scored test cases:

| Measure | Question it answers |
|---|---:|
| Entity-resolution recall | Of 30 real contacts, how many did the agent find? |
| Entity-resolution precision | How many agent-created people are duplicates or fictions? |
| Trap handling | Did it merge the two Byrnes? Did it split Fiona Marsh in two? |
| Attribution | Did shared-mailbox traffic land on the right person? |

The answer key must live outside whatever directory the product ingests, so it cannot be read by accident.
