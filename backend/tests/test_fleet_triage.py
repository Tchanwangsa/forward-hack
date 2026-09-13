"""The claim, tested: one hidden cause drives both sides.

A scenario mutates the estate. The telemetry the world emits and the readings
the eight diagnostic tools take are two views of that same state — so when the
agent reports a 21,060-deep upload queue, a collector really has been stopped
for forty minutes. Before the simulator, those two sides were generated
separately from one label and could not disagree because neither was real.

This file runs the whole path with no HTTP and no database: world -> events ->
episodes -> OPS-SOP-004 -> outcome, and then scores the outcome against a cause
the runner never saw.
"""

from __future__ import annotations

import inspect
from datetime import UTC, datetime, timedelta

import pytest

from asteria.capture.episodes import find_clusters, to_episodes
from asteria.fleet import api, scenarios
from asteria.fleet.clock import Clock
from asteria.fleet.engine import Engine
from asteria.fleet.world import World
from asteria.models.sources import TelemetryEvent
from asteria.resolve.entities import HubFacts
from asteria.triage import sop
from asteria.triage.runner import triage

NOW = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)


@pytest.fixture
def engine() -> Engine:
    world = World.from_inventory(api.INVENTORY, now=NOW)
    e = Engine(world=world, clock=Clock(origin=NOW, speed=0))
    e.rate = 0.0  # nothing arrives but what a test injects
    e.intensity = 0.0
    e.tick()
    api.Hub.engine = e
    return e


def advance(engine: Engine, minutes: int, step: int = 2) -> None:
    for _ in range(minutes // step):
        engine.clock.advance(step * 60)
        engine.tick()


def as_rows(engine: Engine) -> list[TelemetryEvent]:
    """The stream as the product stores it. No database needed to reduce it."""
    return [
        TelemetryEvent(
            event_id=e["event_id"],
            hub_id=e["hub_id"],
            serial=e["serial"],
            customer_id=e["customer_id"],
            ward_id=e["ward_id"],
            bed_id=e["bed_id"],
            ts_device=datetime.fromisoformat(e["ts_device"]),
            ts_received=datetime.fromisoformat(e["ts_received"]),
            code=e["code"],
            severity=e["severity"],
            sw_version=e["sw_version"],
            hw_revision=e["hw_revision"],
            source=e["source"],
            dedupe_key=e["dedupe_key"],
            payload=e["payload"],
        )
        for e in engine.world.events
    ]


def facts(engine: Engine, hub_id: str) -> HubFacts:
    hub = engine.world.hubs[hub_id]
    return HubFacts(
        hub_id=hub.hub_id,
        serial_number=hub.serial,
        customer_id=hub.customer_id,
        organisation=hub.organisation,
        ward_id=hub.ward_id,
        bed_id=hub.bed_id,
        pairing_id=hub.pairing_id,
        pairing_status=hub.pairing_status,
        hw_revision=hub.hw_revision,
        unit_status=hub.unit_status,
    )


def readings(engine: Engine, hub_id: str) -> dict:
    """The diagnostic surface, taken as one round — what FleetClient.readings
    fetches, without standing a server up to fetch it."""
    hub = engine.world.hubs[hub_id]
    return {
        "hub": api.estate_hub(hub_id),
        "site": api.estate_site(hub.customer_id) if hub.customer_id else None,
        "ward": api.ward_occupancy(hub_id),
    }


def run_one(engine: Engine, scenario, procedure=None):
    """Reduce the stream to this scenario's episode and walk the procedure."""
    episodes = to_episodes(as_rows(engine))
    find_clusters(episodes)
    mine = [e for e in episodes if e.hub_id in scenario.hub_ids]
    if not mine:
        return None
    episode = max(mine, key=lambda e: len(e.events))
    return triage(
        episode,
        facts(engine, episode.hub_id),
        procedure=procedure or sop.load(),
        readings=readings(engine, episode.hub_id),
    )


# -- the claim -------------------------------------------------------------


@pytest.mark.parametrize(
    "cause",
    [
        scenarios.POWER_LOSS,
        scenarios.SITE_NETWORK,
        scenarios.DATA_BOX_BACKLOG,
        scenarios.DEVICE_FAULT,
        scenarios.EXPECTED_REMOVAL,
    ],
)
def test_the_procedure_reaches_the_cause_the_world_actually_has(engine: Engine, cause: str) -> None:
    """The runner is handed live readings and no cause, and gets there anyway.

    `actual_cause` is attached after the outcome is already fixed, which is the
    only reason this is a measurement rather than a tautology.
    """
    scenario = engine.inject(cause)
    assert scenario is not None
    scenario.duration = timedelta(hours=20)
    advance(engine, 13 * 60, step=5)

    result = run_one(engine, scenario)
    assert result is not None, f"{cause} produced no episode in OPS-SOP-004 scope"
    result.actual_cause = scenario.cause
    assert result.correct, (
        f"{cause}: procedure concluded {result.outcome.key} at {result.citation}\n"
        + "\n".join(line for step in result.steps for t in step.tools for line in t.transcript)
    )


def test_the_transcript_shows_the_number_the_agent_reported(engine: Engine) -> None:
    """Provenance, not decoration. If the agent says the queue was N deep, the
    transcript has to contain the line it read N from."""
    scenario = engine.inject(scenarios.DATA_BOX_BACKLOG)
    assert scenario is not None
    scenario.duration = timedelta(hours=20)
    advance(engine, 6 * 60, step=5)

    result = run_one(engine, scenario)
    assert result is not None
    depth = result.findings["queue_depth"]
    assert depth > 500, "a stopped collector should have accumulated"
    assert depth == engine.world.sites[scenario.customer_id].queue_depth, (
        "the tool must report the estate's number, not one of its own"
    )
    databox = next(t for step in result.steps for t in step.tools if t.tool == "ssh.databox")
    assert any(str(depth) in line for line in databox.transcript)


def test_an_off_taxonomy_cause_walks_the_whole_tree_and_escalates(engine: Engine) -> None:
    """Every check passes, nothing matches, and the run ends at a field visit.

    This is §3 C4 working: a cause the procedure cannot reach is escalated,
    never invented. The value is not the escalation — it is that the run records
    eight clean checks, which is what makes the gap in the document legible.
    """
    scenario = engine.inject(scenarios.CLOCK_SKEW, tier=scenarios.OFF)
    assert scenario is not None
    scenario.duration = timedelta(hours=20)
    advance(engine, 10 * 60, step=5)

    result = run_one(engine, scenario)
    assert result is not None
    result.actual_cause = scenario.cause
    assert result.outcome.key == "unknown-escalate"
    assert result.off_taxonomy
    assert result.correct, "escalating is the correct answer when the document has no clause"
    assert result.checks_run >= 6, "it should have actually looked before escalating"


def test_a_masked_scenario_stops_at_the_upper_fault(engine: Engine) -> None:
    """Correct and incomplete. The box really has stopped; the crash-looping hub
    behind it is real and nobody is now going to look at it."""
    scenario = engine.inject(scenarios.DATA_BOX_BACKLOG, tier=scenarios.MASKED)
    assert scenario is not None
    scenario.duration = timedelta(hours=20)
    advance(engine, 6 * 60, step=5)

    result = run_one(engine, scenario)
    assert result is not None
    assert result.outcome.key == scenarios.DATA_BOX_BACKLOG
    assert "restarts_24h" not in result.findings, (
        "the procedure terminated at §5.5 and never reached the device step"
    )
    for hub in scenario.hubs(engine.world):
        assert hub.restarts_24h > 0, "the fault it missed is real"


# -- the fence -------------------------------------------------------------


def test_the_answer_key_is_not_on_the_triage_path() -> None:
    """Nothing that decides an outcome may read `/v1/sim/scenarios`.

    If this test ever has to be relaxed, `TriageResult.correct` stops being a
    measurement of anything and the one honest number in the system is worthless.
    """
    from asteria.capture import field_triage
    from asteria.fleet.client import SCENARIOS_PATH
    from asteria.triage import conditions, estate, runner, tools

    for module in (runner, tools, conditions, estate, field_triage):
        source = inspect.getsource(module)
        assert SCENARIOS_PATH not in source, f"{module.__name__} reads the answer key"
        assert ".scenarios()" not in source, f"{module.__name__} reads the answer key"


def test_the_tool_set_is_still_the_granted_one() -> None:
    """Read-only, eight of them. A ninth that restarts something would break
    OPS-SOP-004 §3 C1 and TELEMETRY-API.md §7 in one stroke — and the live
    estate makes that a bigger temptation, not a smaller one."""
    from asteria.triage.tools import TOOLS

    assert set(TOOLS) == {
        "fleet.hub_status",
        "fleet.heartbeat_gaps",
        "registers.context",
        "ward.occupancy",
        "power.socket_check",
        "net.path_check",
        "ssh.databox",
        "ssh.hub",
    }


def test_the_fleet_service_exposes_no_write_to_the_estate() -> None:
    """Diagnosis, not remediation. The only POSTs are telemetry ingest — which
    is a hub's route, not ours — and the simulator's own demo control."""
    writes = {
        route.path
        for route in api.app.routes
        if getattr(route, "methods", None) and route.methods & {"POST", "PUT", "PATCH", "DELETE"}
    }
    assert writes == {"/v1/telemetry/events", "/v1/sim/inject"}
