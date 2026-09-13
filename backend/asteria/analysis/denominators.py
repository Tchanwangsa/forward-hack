"""The two denominators. Getting these wrong is the quietest way to be wrong.

Unit-months in service (IND-01, 02, 03, 04, 07) — accrual per hub over the window:

    In service               202   accrues to window end
    Installed                 19   accrues to window end — same state, different
                                   data-entry habit. Two states here is a bug.
    At depot (RMA)             6   accrues to the day it went to the depot
    Decommissioned             8   accrues to its decommission date
    Spare                      9   does not accrue
    Shipped - not installed    6   does not accrue

Patches distributed (IND-05, IND-06) — from the lot allocation.

Cohorts (REGISTERS.md §2.3): fleet, SW version, HW revision (H1/H2/H2.1 — the
plan says H1/H2, the data also has H2.1, the data wins), organisation, ward, lot.
"""
