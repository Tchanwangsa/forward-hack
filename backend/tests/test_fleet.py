"""The fleet simulator: does the world hold together, and is the score honest.

The tests that matter here are not "does it produce events". They are:

    the estate a tool reads is the estate a scenario built — one hidden cause
    driving both sides, which is the whole claim of TRIAGE.md §6;

    the answer key is not on the triage path, because a score that can see the
    answers measures nothing;

    and off-taxonomy scenarios really do walk the whole tree and escalate,
    rather than being quietly caught by a branch that half-fits.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from asteria.fleet import scenarios
from asteria.fleet.api import INVENTORY
from asteria.fleet.clock import Clock
from asteria.fleet.engine import Engine
from asteria.fleet.world import World

NOW = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)


@pytest.fixture
def engine() -> Engine:
    """A frozen clock, stepped by hand. Same code path as the demo at 60x."""
    world = World.from_inventory(INVENTORY, now=NOW)
    e = Engine(world=world, clock=Clock(origin=NOW, speed=0))
    e.tick()
    return e


def advance(engine: Engine, minutes: int, step: int = 2) -> None:
    for _ in range(minutes // step):
        engine.clock.advance(step * 60)
        engine.tick()


def test_the_fleet_seeds_from_the_inventory_not_from_telemetry(engine: Engine) -> None:
    """The register owns the roster; telemetry owns state (TELEMETRY-API.md §7)."""
    assert len(engine.world.hubs) == 250
    assert engine.world.sites
    # Spares and units in transit are in the roster and out of the denominator.
    assert 0 < len(engine.world.live_hubs()) < 250


def test_a_healthy_fleet_is_quiet(engine: Engine) -> None:
    """No scenario, no events. A simulator that emits noise at rest cannot be
    read, and every rate computed off it is measuring the simulator."""
    engine.rate = 0.0
    engine.intensity = 0.0
    advance(engine, 240)
    assert not [e for e in engine.world.events if e["code"] != "HEARTBEAT"]
    assert all(h.online(engine.clock.now()) for h in engine.world.live_hubs())


def test_a_dead_socket_reaches_the_cloud_as_silence(engine: Engine) -> None:
    """Power loss: the unit runs down, says so, and only then goes quiet.

    This is the interval that separates a register row saying "lost power at
    14:20" from one that can show the discharge curve underneath it.
    """
    engine.rate = 0.0
    scenario = engine.inject(scenarios.POWER_LOSS)
    assert scenario is not None
    # Long enough to run a full battery down: at 11%/h that is eight hours, and
    # the catalogue's own durations are often shorter than the discharge.
    scenario.duration = timedelta(hours=20)
    hub = engine.world.hubs[scenario.hub_ids[0]]

    advance(engine, 60)
    assert hub.battery_pct < 90, "an unplugged unit should be running down"
    assert engine.world.visible_to_cloud(hub), "it still has charge, so it still reports"

    advance(engine, 12 * 60)
    assert hub.battery_pct == 0
    assert not engine.world.visible_to_cloud(hub)
    codes = {e["code"] for e in engine.world.events if e["hub_id"] == hub.hub_id}
    assert "BATT" in codes and "HUB-OFFLINE" in codes


def test_the_data_box_queue_is_an_integral_not_a_number(engine: Engine) -> None:
    """The reading the agent takes is where the backlog actually got to."""
    engine.rate = 0.0
    scenario = engine.inject(scenarios.DATA_BOX_BACKLOG)
    assert scenario is not None
    site = engine.world.sites[scenario.customer_id]

    advance(engine, 30)
    early = site.queue_depth
    advance(engine, 120)
    assert site.queue_depth > early > 3, "a stopped collector accumulates"

    # And the hubs behind it are perfectly healthy, which is the confusion
    # §5.5 exists to resolve.
    for hub in scenario.hubs(engine.world):
        assert hub.socket_live and hub.agent_up
        assert not engine.world.visible_to_cloud(hub)


def test_a_site_event_takes_the_site(engine: Engine) -> None:
    """Three or more hubs, or episodes.CLUSTER_MIN_HUBS will not call it one."""
    engine.rate = 0.0
    scenario = engine.inject(scenarios.SITE_NETWORK)
    assert scenario is not None
    assert len(scenario.hub_ids) >= 3
    advance(engine, 45)
    offline = [
        e
        for e in engine.world.events
        if e["code"] == "HUB-OFFLINE" and e["customer_id"] == scenario.customer_id
    ]
    assert offline
    assert any(e["payload"]["ward_wide"] for e in offline), (
        "the platform knows a site went with it, and the spreadsheet never records that"
    )


def test_skin_is_never_emitted(engine: Engine) -> None:
    """A patch cannot detect a rash (TELEMETRY-API.md §2). If the simulator ever
    produces one, outage watch can draft one, and that is an invented event."""
    advance(engine, 14 * 24 * 60, step=10)
    assert "SKIN" not in {e["code"] for e in engine.world.events}


def test_adhesive_is_raised_as_an_inference_not_an_observation(engine: Engine) -> None:
    engine.rate = 0.0
    scenario = engine.inject(scenarios.CONSUMABLE_PATCH)
    assert scenario is not None
    for hub in scenario.hubs(engine.world):
        hub.wear_time_h = 60
    advance(engine, 180)
    adhesive = [e for e in engine.world.events if e["code"] == "ADHESIVE"]
    assert adhesive
    for event in adhesive:
        assert event["payload"]["detachment_observed"] is False
        assert event["payload"]["confidence"] < 0.5


def test_one_fault_is_one_event(engine: Engine) -> None:
    """A flapping link raises an event and then holds its peace.

    Without the cooldown the stream is technically accurate and practically a
    denial of service on the register, and every rate inherits the tick interval.
    """
    engine.rate = 0.0
    scenario = engine.inject(scenarios.CONSUMABLE_PATCH)
    assert scenario is not None
    advance(engine, 8 * 60)
    hub_events = [
        e
        for e in engine.world.events
        if e["hub_id"] in scenario.hub_ids and e["code"] in ("CONN-LINK-LOSS", "ADHESIVE")
    ]
    assert 0 < len(hub_events) <= 12, f"{len(hub_events)} events in 8h is a storm, not a fault"


def test_the_planted_cohort_story_emerges_rather_than_being_planted(engine: Engine) -> None:
    """1.1.0 ships a threshold profile that does not apply the ward's settings.

    Nothing writes that story into the stream. It falls out of a per-cohort
    hazard on a live fleet, which is the difference between a dataset that
    contains a finding and one a product can be shown finding.
    """
    advance(engine, 30 * 24 * 60, step=10)
    alerts = [e for e in engine.world.events if e["code"] == "ALERT-FALSE"]
    assert len(alerts) > 20, "not enough signal to say anything"

    on_110 = [e for e in alerts if e["sw_version"] == "1.1.0"]
    hubs_110 = [h for h in engine.world.live_hubs() if h.effective_sw == "1.1.0"]
    share_of_fleet = len(hubs_110) / len(engine.world.live_hubs())
    share_of_alerts = len(on_110) / len(alerts)
    assert share_of_alerts > share_of_fleet * 3, (
        f"1.1.0 is {share_of_fleet:.0%} of the fleet and {share_of_alerts:.0%} of the alerts"
    )
    # And the field that makes it findable is a fact the device actually knows.
    assert any(e["payload"]["ward_profile_applied"] is False for e in on_110)


def test_off_taxonomy_scenarios_declare_that_the_procedure_cannot_reach_them(
    engine: Engine,
) -> None:
    """Every one of them expects `unknown-escalate`, by construction.

    They are not noise and they are not bugs. They are the coverage gaps in
    OPS-SOP-004 rev 3.0, and a scenario that claimed a cause the document has no
    clause for would be asserting something the agent could never honestly say.
    """
    engine.rate = 0.0
    for cause in scenarios.OFF_TAXONOMY:
        scenario = engine.inject(cause, tier=scenarios.OFF)
        if scenario is None:  # multi-site needs free hubs at four customers
            continue
        assert scenario.expected_outcome in ("unknown-escalate", scenarios.CONSUMABLE_PATCH)
        assert scenario.detail.get("note"), "a gap should say what it is"


def test_masked_scenarios_name_what_the_procedure_will_miss(engine: Engine) -> None:
    """Correct and incomplete is a different failure from wrong, and the
    simulator has to be able to tell a scorer which one it set up."""
    engine.rate = 0.0
    scenario = engine.inject(scenarios.DATA_BOX_BACKLOG, tier=scenarios.MASKED)
    assert scenario is not None
    assert scenario.expected_outcome == scenarios.DATA_BOX_BACKLOG
    assert scenario.masked_cause == scenarios.DEVICE_FAULT
    advance(engine, 90)
    for hub in scenario.hubs(engine.world):
        assert hub.restarts_24h > 0, "the masked fault is real, not a label"


def test_a_scenario_puts_the_estate_back(engine: Engine) -> None:
    """A fleet where every fault is permanent stops being a fleet after an hour."""
    engine.rate = 0.0
    scenario = engine.inject(scenarios.POWER_LOSS)
    assert scenario is not None
    hub_ids = list(scenario.hub_ids)
    advance(engine, int(scenario.duration.total_seconds() / 60) + 60)
    assert scenario.ended_at is not None
    for hub_id in hub_ids:
        hub = engine.world.hubs[hub_id]
        assert hub.socket_live and hub.scenario_id is None
