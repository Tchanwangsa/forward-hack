"""Tier 1.5 — the ops team's triage procedure, executed.

Outage watch establishes *what* happened and that nobody wrote it down. This
package establishes *why*, by running OPS-SOP-004 the way the duty analyst runs
it: same steps, same order, same thresholds, same read-only access to the estate.

    sop.py          the procedure, loaded from reference-data/sop/ and checked
                    against the controlled PDF it is a twin of
    estate.py       the estate as the tools find it — one situation per episode
    tools.py        eight read-only diagnostic tools over that estate
    conditions.py   one predicate per `when:` in the procedure
    runner.py       walks the tree, records every step, reaches an outcome

The boundary this package does not cross, from OPS-SOP-004 §3 and
TELEMETRY-API.md §7: nothing here writes to a device. No restart, no
reconfiguration, no firmware. It reads, it records, it recommends, and a human
with a change ticket does the acting.
"""
