"""sources/telemetry/events.ndjson + heartbeats.ndjson -> the telemetry tables.

The primary source for tier 1. Telemetry event codes *are* indicator codes,
and the event carries the SW version at the moment of the fault — the column
that is 35% blank in the human incident log. See plan/TELEMETRY-API.md.
"""
