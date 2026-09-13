"""The seven approved indicators. Approved in advance in a controlled document.

    IND-01 CONN-LINK-LOSS   PulseOne    unit-months    1.3    2.0x    Quality
    IND-02 HUB-OFFLINE      PulseOne    unit-months    0.9    2.5x    Quality
    IND-03 BATT             PulseOne    unit-months    0.6    2.0x    Quality
    IND-04 ALERT-FALSE      PulseOne    unit-months    1.1    2.0x    Clinical
    IND-05 ADHESIVE         PulsePatch  patches        0.4    2.0x    Quality
    IND-06 SKIN             PulsePatch  patches        0.12   any increase  Clinical
    IND-07 DISPLAY          PulseOne    unit-months    0.8    3.0x    Service

Baselines are trailing 12 months. Threshold kinds (REGISTERS.md §Threshold evaluation):
    ratio         observed_90d_rate >= multiplier * baseline
    any_increase  observed_90d_rate > baseline, routed to Clinical regardless of magnitude

These live in the database (models.reference.Indicator), loaded from the PMS plan.
This module is the rule engine over them, not a second copy of the numbers.
"""
