# Asteria Entity Model

> **Private generator state — never ingested by the product.**
> This file is our answer key, not the application's input. The product must derive
> every person, organisation, and device from source records alone. See
> [`plan/MOCK-DATA.md`](../../MOCK-DATA.md) dataset layers.


## Purpose

Define the smallest set of things that must exist before we can generate operational activity for Asteria.

This is deliberately minimal. Suppliers, contract manufacturers, distributors, component lots, controlled documents, training, audits, and risk records are **out of scope for now**. Add them only when something we actually want to simulate needs them.

## The one distinction that matters

```text
Entity   A stable thing with identity: a person, a hospital, a device unit
Event    Something that happens: a shipment, a support ticket, a complaint
```

Everything else is detail we can add later.

## Layer 1: Asteria (internal)

| Entity | What it represents |
|---|---|
| Employee | A fictional person who works at Asteria, with a name, department, and role |

One flat list of people. No legal entities, sites, employment records, role assignments, or approval authorities yet. Departments and roles are just string fields on the employee.

Departments in use: quality, support, service, sales, engineering.

## Layer 2: Customers (external)

| Entity | What it represents |
|---|---|
| Customer organisation | A hospital or hospital network that buys from Asteria |
| Customer site | A physical hospital or clinic belonging to that organisation |
| Contact | A named person at a customer site, with an email address |

An organisation has one or more sites. A site has one or more contacts. That is the whole external network.

All customers are direct — Asteria sells to them and supports them itself.

## Layer 3: Products

From the [Asteria product portfolio](products.md).

| Entity | What it represents | Tracked by |
|---|---|---|
| Product model | PulseOne (P1-100) or PulsePatch (PP-72) | Model code |
| Device unit | One physical PulseOne | Serial number |
| Patch lot | A batch of PulsePatch made together | Lot code, expiry date |

A device unit has a hardware revision and a current software version as plain fields.

## Layer 4: Activity

| Event | What it represents | Links |
|---|---|---|
| Shipment | Product sent to a customer site | Site, device serials and/or patch lots |
| Support ticket | A customer contacting Asteria about a problem | Contact, site, optionally a device or lot |
| Complaint | A ticket assessed as a quality complaint | Ticket |

No orders, order lines, registrations, installations, transfers, RMAs, work orders, inspections, or repairs yet. A shipment is enough to say who has what.

Not every ticket becomes a complaint. Complaint creation is a judgement made about a ticket, not an automatic consequence of one.

## Core shape

```text
Customer organisation
└── customer site
    ├── contact
    ├── shipment → device units / patch lots
    └── support ticket → optional complaint
```

## Seed order

1. Asteria employees
2. Customer organisations, sites, and contacts
3. Product models, device units, patch lots
4. Shipments allocating units and lots to sites
5. Support tickets raised by contacts
6. Complaints, for the subset of tickets that warrant one

## First concrete seed

- 12 Asteria employees across the five departments
- 8 customer organisations
- 15 customer sites
- 30 contacts
- 2 product models
- 40 PulseOne device units
- 6 PulsePatch lots
- ~25 shipments
- ~60 support tickets
- ~10 complaints

Small enough to read end to end by hand. Scale up only once the relationships look right.
