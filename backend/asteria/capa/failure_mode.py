"""The hard problem: what makes two things the same failure mode.

Not string equality on the event code. Cross-register overlap means the same
underlying fault showing up as an incident, an RMA and a complaint — three rows
in three logs that are one thing. See plan/CAPA.md §The hard problem.
"""
