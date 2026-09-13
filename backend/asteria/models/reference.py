"""Registers 1 and 7 — reference only, human is the system of record.

1. PM-Customer-Organisations-and-Hubs-Record.xlsx — 3 sheets:
   Customer Organisations · Hub Inventory (250 units) · Patch Lot Allocation.
   Hub Inventory carries Unit Status, which drives the unit-months denominator
   (plan/REGISTERS.md §2.1 — `Spare` and `Shipped - not installed` do not accrue).
7. PMS-Plan-and-Report-Register.xlsx — controlled documents: PMS-PLAN-001 v3.0,
   PMS-PLAN-002 v2.0, and the trend working files (one of which is `Overdue`).

Also home to the seven approved indicators: internal code, denominator kind,
trailing-12-month baseline, escalation threshold, review function, source document.
"""

# TODO: CustomerOrganisation, Hub, PatchLotAllocation, ControlledDocument, Indicator
