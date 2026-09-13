"""The sweep — the five triggers. Runs on every new NC, and weekly.

Reads Signals, NCs, CAPAs and the registers beneath them. Asks: have we seen
this before, and did our fix hold? Outputs a CAPA recommendation and a drafted
problem statement. It does not run the investigation, verify effectiveness, or
close anything — that is explicitly out of scope.

Demo case: BATT / H1 — cross-register overlap plus a prior NC that did not hold.
"""
