"""The loop. Scenarios arrive, the world moves, telemetry falls out of it.

Two rules hold this together and both are worth stating before the code:

    Nothing is emitted by a scenario. A scenario changes the estate; the engine
    looks at the estate and emits what that estate implies. `DISPLAY` is raised
    because a POST code is set, `HUB-OFFLINE` because a heartbeat did not arrive
    through a stack that is genuinely broken somewhere. So the telemetry and the
    diagnostic readings cannot drift apart — they are two views of one variable.

    Arrivals are stochastic, targets are not uniform. Poisson arrivals on a
    diurnal curve, and the hazard per hub is weighted by cohort, so the stories
    already planted in this dataset keep emerging from a live fleet instead of
    being re-seeded into it: SW 1.1.0 carries more `ALERT-FALSE`, and network
    work happens when hospitals do it, which is at night.
"""

from __future__ import annotations

import random
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from asteria.fleet.clock import Clock
from asteria.fleet.scenarios import (
    CATALOGUE,
    CLEAN,
    SITE_NETWORK,
    Scenario,
    Spec,
)
from asteria.fleet.world import HEARTBEAT_INTERVAL, OFFLINE_THRESHOLD, HubState, World

# Scenarios per simulated hour across the whole fleet, on a fleet behaving the
# way PMS-PLAN-001 says a fleet behaves. Derived, not chosen: the plan's seven
# baselines sum to 5.22 events per 100 unit-months, which over 202 accruing
# hubs is about ten events a month, and a scenario produces roughly three. A
# real fleet has an outage every week or so, which is unwatchable and correct.
REAL_ARRIVAL_RATE = 0.006

# A fault raises its code, then holds. Simulated time.
CODE_COOLDOWN = timedelta(minutes=45)

HOURS_PER_MONTH = 730.5

# PMS-PLAN-001 v3.0's baseline for IND-04, per unit-month. Nuisance alarms are
# not outages and get no scenario — they are a rate, and this is the plan's
# number for it rather than one the simulator made up.
ALERT_FALSE_PER_UNIT_MONTH = 0.011

# A demo that waits a week for an outage is not a demo. `intensity` is the one
# knob, and it is one knob on purpose: it scales scenario arrivals and per-hub
# hazards *by the same factor*, so every rate the metrics endpoint computes is
# uniformly inflated and can be compared against a baseline scaled the same way.
# Two independent knobs would inflate outage codes and alarm codes differently,
# and no single correction could put either back.
#
# At 40x and 60x clock speed a scenario lands every four minutes or so —
# TRIAGE.md §6's "watchable". Set it to 1.0 and the fleet behaves like the plan
# says a fleet behaves, which is almost entirely silence.
DEMO_INTENSITY = 40.0

# Hour-of-day multiplier, UTC. Ward activity through the day, and the small hours
# where hospital IT does its cutovers and nobody is on site to notice.
DIURNAL = [
    1.30,
    1.35,
    1.25,
    1.10,
    0.80,
    0.60,
    0.55,
    0.70,
    0.95,
    1.05,
    1.10,
    1.05,
    1.00,
    1.05,
    1.10,
    1.15,
    1.10,
    1.00,
    0.90,
    0.85,
    0.90,
    1.00,
    1.15,
    1.25,
]

# The cohort the dataset already has a story about. A live fleet should keep
# telling it rather than have it re-planted.
# 1.1.0 ships a threshold profile that fails to apply the ward's own settings.
# The multiplier is chosen to land IND-04 near the ratio TELEMETRY-API.md §1
# already uses as its worked example, so the planted story emerges from a live
# fleet at the size the plan says it is.
COHORT_HAZARD = {"1.1.0": 12.0, "1.0.9": 1.2}


@dataclass
class Engine:
    """One fleet, one clock, one set of scenarios in flight."""

    world: World
    clock: Clock
    intensity: float = DEMO_INTENSITY
    #: Override only to pin an arrival rate directly; normally derived from
    #: `intensity` so the two cannot drift apart.
    rate: float | None = None
    rng: random.Random = field(default_factory=lambda: random.Random(20260913))

    active: list[Scenario] = field(default_factory=list)
    history: list[Scenario] = field(default_factory=list)
    _seq: int = 0
    _last_tick: datetime | None = None
    _last_heartbeat: datetime | None = None
    _last_tick_drain: datetime | None = None
    _lock: threading.Lock = field(default_factory=threading.Lock)

    @property
    def arrival_rate(self) -> float:
        return self.rate if self.rate is not None else REAL_ARRIVAL_RATE * self.intensity

    # -- the tick ----------------------------------------------------------

    def tick(self) -> list[dict]:
        """Advance the world to `clock.now()`. Returns the events it produced."""
        with self._lock:
            now = self.clock.now()
            if self._last_tick is None:
                self._last_tick = now
                self._last_heartbeat = now - HEARTBEAT_INTERVAL
                for hub in self.world.live_hubs():
                    self.world.heartbeat(hub, now)
                return []

            dt_hours = (now - self._last_tick).total_seconds() / 3600
            self._last_tick = now
            if dt_hours <= 0:
                return []

            before = len(self.world.events)
            self._retire(now)
            self._arrive(now, dt_hours)
            for scenario in self.active:
                scenario.tick(self.world, now)
            self._drain(now)
            self._heartbeats(now)
            self._raise_offline(now)
            self._raise_device_codes(now, dt_hours)
            return list(self.world.events)[before:]

    # -- scenario lifecycle ------------------------------------------------

    def _retire(self, now: datetime) -> None:
        still: list[Scenario] = []
        for s in self.active:
            if now >= s.ends_at():
                s.end(self.world, now)
                s.ended_at = now
                for hub_id in s.hub_ids:
                    hub = self.world.hubs.get(hub_id)
                    if hub is not None and hub.scenario_id == s.scenario_id:
                        hub.scenario_id = None
                self.history.append(s)
            else:
                still.append(s)
        self.active = still

    def _arrive(self, now: datetime, dt_hours: float) -> None:
        """Poisson. One draw per tick against λ·dt, curved by hour of day."""
        lam = self.arrival_rate * DIURNAL[now.hour] * dt_hours
        n = _poisson(self.rng, lam)
        for _ in range(n):
            scenario = self._spawn(now)
            if scenario is not None:
                self.active.append(scenario)

    def _spawn(self, now: datetime, spec: Spec | None = None) -> Scenario | None:
        spec = spec or self._pick_spec(now)
        hubs = self._pick_targets(spec)
        if not hubs:
            return None
        self._seq += 1
        minutes = self.rng.randint(*spec.minutes)
        scenario = spec.cls(
            scenario_id=f"SCN-{self._seq:05d}",
            cause=spec.cause,
            tier=spec.tier,
            label=spec.label,
            hub_ids=[h.hub_id for h in hubs],
            customer_id=hubs[0].customer_id,
            started_at=now,
            duration=timedelta(minutes=minutes),
            rng=random.Random(self.rng.randrange(2**32)),
        )
        scenario.begin(self.world, now)
        scenario.began = True
        for hub in hubs:
            hub.scenario_id = scenario.scenario_id
        return scenario

    def _pick_spec(self, now: datetime) -> Spec:
        """Weighted draw, with the one time-of-day nudge that is real.

        Hospital network changes happen in the maintenance window. Everything
        else the diurnal curve already handles at the arrival rate, and nudging
        it twice would be double-counting.
        """
        night = now.hour < 5 or now.hour >= 22
        weights = [
            s.weight * (3.0 if night and s.cause == SITE_NETWORK and s.tier == CLEAN else 1.0)
            for s in CATALOGUE
        ]
        total = sum(weights)
        point = self.rng.random() * total
        running = 0.0
        for spec, weight in zip(CATALOGUE, weights, strict=True):
            running += weight
            if point <= running:
                return spec
        return CATALOGUE[-1]

    def _pick_targets(self, spec: Spec) -> list[HubState]:
        """Who it happens to. Free hubs only — one cause per unit at a time.

        Two scenarios on one hub would make the hidden cause ambiguous and the
        score meaningless, and it is also not what `masked` means: a masked
        scenario is *one* scenario that carries two faults, declared as such.
        """
        free = [h for h in self.world.live_hubs() if h.scenario_id is None]
        if not free:
            return []

        if spec.scope == "site":
            sites = {h.customer_id for h in free if h.customer_id}
            if not sites:
                return []
            customer_id = self.rng.choice(sorted(sites))
            at_site = [h for h in free if h.customer_id == customer_id]
            # A site event takes the site. Anything less is a coincidence, and
            # episodes.CLUSTER_MIN_HUBS needs three before it will say so.
            return at_site if len(at_site) >= 3 else []

        if spec.scope == "multi-site":
            by_site: dict[str, list[HubState]] = {}
            for h in free:
                if h.customer_id:
                    by_site.setdefault(h.customer_id, []).append(h)
            chosen = self.rng.sample(sorted(by_site), min(4, len(by_site)))
            picked: list[HubState] = []
            for customer_id in chosen:
                picked.extend(
                    self.rng.sample(by_site[customer_id], min(2, len(by_site[customer_id])))
                )
            return picked

        return [self._weighted_hub(free)]

    def _weighted_hub(self, free: list[HubState]) -> HubState:
        weights = [COHORT_HAZARD.get(h.effective_sw or "", 1.0) for h in free]
        total = sum(weights)
        point = self.rng.random() * total
        running = 0.0
        for hub, weight in zip(free, weights, strict=True):
            running += weight
            if point <= running:
                return hub
        return free[-1]

    # -- physics -----------------------------------------------------------

    def _drain(self, now: datetime) -> None:
        """An unplugged unit runs down. This is not a scenario's business.

        A hub unplugged by a ward at a discharge and a hub whose socket failed
        behave identically on the way out, and they should: the difference
        between them is the ward note at §5.2, not the discharge curve. Keeping
        the drain here rather than in either scenario is what stops the two from
        quietly diverging.
        """
        dt_h = (now - (self._last_tick_drain or now)).total_seconds() / 3600
        self._last_tick_drain = now
        if dt_h <= 0:
            return
        for hub in self.world.live_hubs():
            if hub.socket_live:
                if hub.battery_pct < 88:
                    hub.battery_pct = min(88.0, hub.battery_pct + dt_h * 22)
            else:
                hub.battery_pct = max(0.0, hub.battery_pct - dt_h * 11)

    # -- emission, derived from state -------------------------------------

    def _heartbeats(self, now: datetime) -> None:
        """Every unit that can still reach us, says so. The rest say nothing,
        and their silence is the only thing the cloud has to go on."""
        if self._last_heartbeat and now - self._last_heartbeat < HEARTBEAT_INTERVAL:
            return
        self._last_heartbeat = now
        for hub in self.world.live_hubs():
            if self.world.visible_to_cloud(hub):
                self.world.heartbeat(hub, now)

    def _raise_offline(self, now: datetime) -> None:
        """`HUB-OFFLINE` is raised cloud-side. A unit that is offline cannot
        report that it is offline (TELEMETRY-API.md §2)."""
        for hub in self.world.live_hubs():
            if hub.last_seen is None or hub.offline_raised:
                continue
            gap = now - hub.last_seen
            if gap < OFFLINE_THRESHOLD:
                continue
            hub.offline_raised = True
            site = self.world.site_of(hub)
            peers = (
                [
                    h
                    for h in self.world.hubs_at(hub.customer_id)
                    if h.accrues and not self.world.visible_to_cloud(h)
                ]
                if hub.customer_id
                else []
            )
            self.world.emit(
                hub,
                "HUB-OFFLINE",
                now,
                severity="error",
                payload={
                    "last_seen": hub.last_seen.isoformat(),
                    "offline_duration_h": round(gap.total_seconds() / 3600, 2),
                    # The platform's own judgement, and a fact the spreadsheet
                    # never records. It is a claim about a site, so it needs a
                    # second unit behind it before conditions.site_wide trusts it.
                    "ward_wide": len(peers) >= 3,
                    "site_units_quiet": len(peers),
                    "databox_shipping": bool(site.databox_healthy) if site else None,
                },
                scenario_id=hub.scenario_id,
            )

    def _raise_device_codes(self, now: datetime, dt_hours: float) -> None:
        """The codes a hub raises about itself, each one read off its state."""
        for hub in self.world.live_hubs():
            if not self.world.visible_to_cloud(hub):
                continue

            if hub.post_code and self._may_raise(hub, "DISPLAY", now):
                self.world.emit(
                    hub,
                    "DISPLAY",
                    now,
                    severity="error",
                    payload={"fault": "power-on self test", "post_code": hub.post_code},
                    scenario_id=hub.scenario_id,
                )

            if not hub.link_up and self._may_raise(hub, "LINK", now):
                code = "ADHESIVE" if hub.wear_time_h >= 36 else "CONN-LINK-LOSS"
                payload = {
                    "pairing_id": hub.pairing_id,
                    "rssi_at_loss": hub.rssi_dbm,
                    "patch_lot": hub.patch_lot,
                }
                if code == "ADHESIVE":
                    # Inference, not observation. TELEMETRY-API.md §5: this may
                    # only ever be raised as a question for the ward.
                    payload |= {
                        "wear_time_h": round(hub.wear_time_h, 1),
                        "detachment_observed": False,
                        "confidence": 0.4,
                    }
                else:
                    payload |= {"duration_s": self.rng.randint(30, 900)}
                self.world.emit(hub, code, now, payload=payload, scenario_id=hub.scenario_id)

            if hub.battery_pct <= 12 and self._may_raise(hub, "BATT", now):
                self.world.emit(
                    hub,
                    "BATT",
                    now,
                    payload={
                        "capacity_pct_nominal": round(hub.battery_pct, 1),
                        "cycles": self.rng.randint(180, 700),
                        "on_dock": hub.on_dock,
                        "discharging_since": hub.last_seen.isoformat() if hub.last_seen else None,
                    },
                    scenario_id=hub.scenario_id,
                )

            self._alert_false(hub, now, dt_hours)

    def _may_raise(self, hub: HubState, key: str, now: datetime) -> bool:
        """One fault is one event, not one per tick.

        A hub whose link is flapping raises an event, and then holds its peace
        for half an hour. Without this the stream is technically accurate and
        practically a denial of service on the register — and every rate
        computed off it is inflated by the sampling interval, which is the least
        defensible kind of wrong number.
        """
        last = hub.last_raised.get(key)
        if last is not None and now - last < CODE_COOLDOWN:
            return False
        hub.last_raised[key] = now
        return True

    def _alert_false(self, hub: HubState, now: datetime, dt_hours: float) -> None:
        """A clinical alert raised and then dismissed as inappropriate.

        Not an outage and not a scenario — a nuisance-alarm rate, which is what
        IND-04 measures. It is here because it is the one indicator with a live
        cohort story in this dataset: 1.1.0 ships a threshold profile that fails
        to apply the ward's own settings, so the version carries a higher
        intensity and `ward_profile_applied` is the field that makes it findable.

        A hub can see that an alert was silenced in four seconds. It cannot see
        whether the alert was wrong (TELEMETRY-API.md §2), and the payload says
        only what the device actually knows.
        """
        hazard = COHORT_HAZARD.get(hub.effective_sw or "", 1.0)
        # Scaled by the tick, not per tick: a rate that depends on how often the
        # loop happens to run is not a rate, and every number computed off it
        # would change when the tick interval did.
        p = ALERT_FALSE_PER_UNIT_MONTH * hazard * self.intensity * (dt_hours / HOURS_PER_MONTH)
        if self.rng.random() > p:
            return
        applied = hub.effective_sw != "1.1.0" or self.rng.random() < 0.2
        self.world.emit(
            hub,
            "ALERT-FALSE",
            now,
            severity="info",
            payload={
                "alert_type": self.rng.choice(["hr_high", "hr_low", "spo2_low", "lead_off"]),
                "threshold_profile": "ward" if applied else "factory-default",
                "dismissed_by_role": self.rng.choice(["RN", "RN", "CNS"]),
                "ward_profile_applied": applied,
                "dismissed_after_s": self.rng.randint(2, 25),
            },
            scenario_id=hub.scenario_id,
        )

    # -- demo controls -----------------------------------------------------

    def inject(self, cause: str, tier: str = CLEAN) -> Scenario | None:
        """Force one, for a demo that cannot wait for a Poisson draw."""
        spec = next((s for s in CATALOGUE if s.cause == cause and s.tier == tier), None)
        if spec is None:
            return None
        with self._lock:
            scenario = self._spawn(self.clock.now(), spec)
            if scenario is not None:
                self.active.append(scenario)
            return scenario

    def status(self) -> dict:
        now = self.clock.now()
        return {
            "clock": self.clock.describe(),
            "hubs": len(self.world.hubs),
            "hubs_accruing": len(self.world.live_hubs()),
            "hubs_online": sum(1 for h in self.world.live_hubs() if h.online(now)),
            "sites": len(self.world.sites),
            "events_held": len(self.world.events),
            "arrival_rate_per_sim_hour": round(self.arrival_rate, 4),
            "intensity": self.intensity,
            "intensity_note": (
                "The one knob. Scenario arrivals and per-hub hazards are both "
                "scaled by it, so every rate here is uniformly inflated by the "
                "same factor. 1.0 is the rate PMS-PLAN-001 says a real fleet "
                "runs at; anything above it is a demo setting, and "
                "/v1/metrics/indicators scales its baselines to match."
            ),
            "scenarios_active": [s.describe() for s in self.active],
            "scenarios_completed": len(self.history),
        }


def _poisson(rng: random.Random, lam: float) -> int:
    """Knuth. λ is small here — a tick is seconds of simulated time."""
    if lam <= 0:
        return 0
    if lam > 30:  # pragma: no cover - only if someone sets a silly rate
        return max(0, int(rng.gauss(lam, lam**0.5)))
    target = 2.718281828459045**-lam
    k, p = 0, 1.0
    while True:
        p *= rng.random()
        if p <= target:
            return k
        k += 1
