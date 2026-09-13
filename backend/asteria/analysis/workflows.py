"""The five workflows. Specified in full in plan/DIAGRAMS.md §Tier 2.

    1. Watch        classify new events against the indicators
    2. Measure      rate = numerator / denominator, per cohort per window
    3. Raise        threshold breached -> a Signal
    4. Investigate  cohort isolation, confounders, the near-miss test
    5. Record       a drafted Product NC                        <- human gate

Trigger: nightly, and on every new classified event.

Must land once, convincingly, on ALERT-FALSE / SW 1.1.0 — and must correctly
close the network-maintenance near-miss as `no action`, which is a permanent
record with a named reviewer, not a deletion.
"""
