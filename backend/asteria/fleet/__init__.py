"""The simulated PulseOne fleet: a live device cloud, run as its own service.

    make fleet    uvicorn asteria.fleet.api:app --port 8100

See plan/TELEMETRY-API.md for the contract and plan/TRIAGE.md §6 for why the
cause is generated before the telemetry rather than derived from it.
"""
