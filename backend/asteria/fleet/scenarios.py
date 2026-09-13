"""The troubleshooting taxonomy, run forwards.

`triage/estate.py` ran it backwards: an episode had already happened, and a
weighted draw seeded on that episode decided, after the fact, what had caused
it. That was a good scaffold and a fair scorer, but there was no world — only a
label applied to a row in a frozen file.

Here the cause is chosen *first*. A scenario picks a target, mutates the estate
over simulated time, and the telemetry is what that mutated estate emits. When
the agent later SSHes the data box, the queue is 21,060 deep because a collector
has been stopped for forty minutes, not because a dict said so.

Three tiers, and the second two are the interesting ones:

    clean          one cause, one SOP outcome. OPS-SOP-004 reaches it.
    masked         two causes at once, stacked so the procedure stops at the
                   upper one and never reaches the lower. The diagnosis is
                   correct and incomplete, which is a different failure from
                   being wrong and is worth being able to see.
    off-taxonomy   a cause OPS-SOP-004 has no branch for. Every check passes,
                   nothing matches, and the run lands on `unknown-escalate` by
                   construction. These are not bugs in the agent or noise in the
                   simulator — they are the procedure's coverage gaps, and
                   surfacing them is the point (TRIAGE.md §6, C4).

Each scenario declares `expected_outcome`: what OPS-SOP-004 *should* conclude
given what it can see. The runner never reads it. The scorer does.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import ClassVar

from asteria.fleet.world import HubState, SiteState, World

# -- causes ----------------------------------------------------------------
# The first seven are triage/estate.py's, unchanged and deliberately so: a
# scenario's cause is the key the SOP outcome is compared against, and the two
# vocabularies have to be one vocabulary.

EXPECTED_REMOVAL = "expected-removal"
POWER_LOSS = "power-loss"
SITE_NETWORK = "site-network"
DATA_BOX_BACKLOG = "data-box-backlog"
DEVICE_FAULT = "device-fault"
CONSUMABLE_PATCH = "consumable-patch"
NOTHING_FOUND = "nothing-found"

# And these are new. No branch of OPS-SOP-004 rev 3.0 reaches any of them.
CLOCK_SKEW = "clock-skew"
UNAUTHORISED_FIRMWARE = "unauthorised-firmware"
PAIRING_STORM = "pairing-storm"
LOT_LINK_COLLAPSE = "lot-link-collapse"

OFF_TAXONOMY = {CLOCK_SKEW, UNAUTHORISED_FIRMWARE, PAIRING_STORM, LOT_LINK_COLLAPSE}

CLEAN = "clean"
MASKED = "masked"
OFF = "off-taxonomy"


@dataclass
class Scenario:
    """One hidden cause, unfolding. Subclasses say how.

    A scenario owns the state it changed and puts it back on `end`, because a
    fleet where every fault is permanent stops being a fleet after an hour.
    """

    scenario_id: str
    cause: str
    tier: str
    label: str
    hub_ids: list[str]
    customer_id: str | None
    started_at: datetime
    duration: timedelta
    rng: random.Random
    detail: dict = field(default_factory=dict)
    ended_at: datetime | None = None
    masked_cause: str | None = None
    began: bool = False

    #: What OPS-SOP-004 should conclude on the evidence it can gather.
    expected_outcome: str = ""

    @property
    def active(self) -> bool:
        return self.ended_at is None

    def ends_at(self) -> datetime:
        return self.started_at + self.duration

    def begin(self, world: World, now: datetime) -> None:  # pragma: no cover - overridden
        ...

    def tick(self, world: World, now: datetime) -> None: ...

    def end(self, world: World, now: datetime) -> None: ...

    # -- helpers ----------------------------------------------------------

    def hubs(self, world: World) -> list[HubState]:
        return [world.hubs[h] for h in self.hub_ids if h in world.hubs]

    def site(self, world: World) -> SiteState | None:
        return world.sites.get(self.customer_id) if self.customer_id else None

    def describe(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "cause": self.cause,
            "tier": self.tier,
            "label": self.label,
            "hub_ids": self.hub_ids,
            "customer_id": self.customer_id,
            "started_at": self.started_at.isoformat(),
            "ends_at": self.ends_at().isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "expected_outcome": self.expected_outcome,
            "masked_cause": self.masked_cause,
            "detail": self.detail,
        }


# -- tier 1: clean ---------------------------------------------------------


class ExpectedRemoval(Scenario):
    """Somebody meant for this to stop.

    §5.2 runs before any technical check for exactly this reason: the commonest
    cause of a hub going quiet is a discharge, and an incident row written for a
    discharge is a false signal that ends up in a rate and then in front of a
    regulator.
    """

    REASONS: ClassVar[list[tuple[str, str]]] = [
        ("discharge", "Session ended at discharge; unit unplugged by ward staff."),
        ("planned_works", "Customer notified a planned electrical shutdown on this ward."),
        ("bereavement", "Patient deceased. Unit removed by ward staff, session closed."),
        ("ward_move", "Bed reallocated; unit moved and not re-docked."),
    ]

    def begin(self, world: World, now: datetime) -> None:
        reason, narrative = self.rng.choice(self.REASONS)
        self.detail = {"basis": "ward", "reason": reason, "narrative": narrative}
        self.expected_outcome = EXPECTED_REMOVAL
        for hub in self.hubs(world):
            hub.bed_occupied = False
            hub.session_closed_cleanly = True
            hub.removal_reason = reason
            hub.socket_live = False
            hub.socket_state = "unplugged by ward"
            hub.on_dock = False
            if reason == "planned_works":
                site = self.site(world)
                if site:
                    site.planned_works_note = (
                        f"Planned electrical shutdown, {hub.ward_id}, covering this window."
                    )

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.bed_occupied = True
            hub.session_closed_cleanly = False
            hub.removal_reason = None
            hub.socket_live = True
            hub.socket_state = "live"
            hub.on_dock = True
            hub.battery_pct = 88.0
            hub.last_raised.clear()
        site = self.site(world)
        if site:
            site.planned_works_note = None


class PowerLoss(Scenario):
    """The socket, not the hub. The check everybody skips and shouldn't."""

    def begin(self, world: World, now: datetime) -> None:
        state = self.rng.choice(["unswitched", "no supply", "PoE port down"])
        self.expected_outcome = POWER_LOSS
        for hub in self.hubs(world):
            hub.socket_live = False
            hub.socket_state = state
            hub.on_dock = self.rng.random() < 0.3
            self.detail = {
                "socket_state": state,
                "pdu_port": hub.pdu_port,
                "on_dock": hub.on_dock,
                "battery_at_onset": hub.battery_pct,
            }

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.socket_live = True
            hub.socket_state = "live"
            hub.on_dock = True
            hub.battery_pct = 88.0
            hub.last_raised.clear()


class SiteNetwork(Scenario):
    """The hub never lost itself. The site lost us.

    Site-scope on purpose: every accruing hub at the customer goes quiet inside
    the same window, which is the co-occurrence §5.1 sends straight to §5.4 and
    the reason ten rows get one explanation instead of ten.
    """

    def begin(self, world: World, now: datetime) -> None:
        fault = self.rng.choice(["tunnel down", "packet loss", "dns failure"])
        window = self.rng.choice(
            ["scheduled firewall change", "core switch replacement", "VLAN re-addressing"]
        )
        self.expected_outcome = SITE_NETWORK
        self.detail = {"fault": fault, "change_window": window}
        site = self.site(world)
        if site is None:
            return
        site.change_window = window
        if fault == "tunnel down":
            site.tunnel_up = False
        elif fault == "dns failure":
            site.dns_ok = False
        else:
            site.loss_pct = round(self.rng.uniform(18, 64), 1)
            site.rtt_ms = self.rng.randint(900, 2400)
            self.detail["loss_pct"] = site.loss_pct
            self.detail["rtt_ms"] = site.rtt_ms

    def end(self, world: World, now: datetime) -> None:
        site = self.site(world)
        if site is None:
            return
        site.tunnel_up = True
        site.dns_ok = True
        site.loss_pct = 0.0
        site.rtt_ms = 31
        site.change_window = None


class DataBoxBacklog(Scenario):
    """The hub is fine. The box in the comms room has stopped shipping.

    From the cloud this is indistinguishable from a dead hub, which is the
    entire reason §5.5 exists. The queue depth the agent reads is a real
    integral: frames per hub per minute, accumulating since the collector died.
    """

    def begin(self, world: World, now: datetime) -> None:
        mode = self.rng.choice(["collector stopped", "disk full", "cert expired"])
        self.expected_outcome = DATA_BOX_BACKLOG
        self.detail = {"mode": mode}
        site = self.site(world)
        if site is None:
            return
        if mode == "collector stopped":
            site.collector_active = False
        elif mode == "cert expired":
            site.cert_days_remaining = -self.rng.randint(1, 9)
        else:
            site.disk_used_pct = 97

    def tick(self, world: World, now: datetime) -> None:
        site = self.site(world)
        if site is None:
            return
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        hubs = len([h for h in world.hubs_at(site.customer_id) if h.accrues])
        # ~12 frames per hub per minute, which is what a 5s sample rate buys.
        site.queue_depth = int(3 + minutes * hubs * 12)
        if self.detail.get("mode") == "disk full":
            site.disk_used_pct = min(100, 97 + int(minutes / 120))

    def end(self, world: World, now: datetime) -> None:
        site = self.site(world)
        if site is None:
            return
        site.collector_active = True
        site.queue_depth = 3
        site.disk_used_pct = 41
        site.cert_days_remaining = 121
        site.last_upload = now


class DeviceFault(Scenario):
    """The unit answered, and then failed on itself."""

    def begin(self, world: World, now: datetime) -> None:
        mode = self.rng.choice(["crash loop", "post fault", "crash loop"])
        self.expected_outcome = DEVICE_FAULT
        self.detail = {"mode": mode, "fault": "watchdog reset"}
        for hub in self.hubs(world):
            if mode == "post fault":
                # The unit answers and reports its own self-test failure. It is
                # broken, not absent — which is the distinction §5.6 turns on.
                hub.post_code = f"E-{self.rng.randint(200, 260)}"
                self.detail["post_code"] = hub.post_code
            else:
                hub.restarts_24h = 1

    def tick(self, world: World, now: datetime) -> None:
        """A crash loop is a loop. The restart count is what the loop has done
        so far, and it is climbing while the agent is looking at it."""
        if self.detail.get("mode") != "crash loop":
            return
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        for hub in self.hubs(world):
            hub.restarts_24h = min(40, 1 + int(minutes / 4))
            # Down for half an hour, up for half an hour. Longer than the
            # cloud's offline threshold on purpose: this is the flap that
            # episodes.py has to collapse into one incident rather than eleven,
            # and a loop that never stays down long enough to be noticed is not
            # the failure mode §5.6 is about.
            hub.agent_up = int(minutes / 30) % 2 == 1

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.restarts_24h = 0
            hub.post_code = None
            hub.agent_up = True


class ConsumablePatch(Scenario):
    """Link margin degrading. Asked, never asserted.

    A radio cannot see a piece of tape (TELEMETRY-API.md §2). The hub stays up
    and reachable throughout — it is the link to the patch that goes, so every
    check below §5.7 passes and the procedure arrives here having earned it.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = CONSUMABLE_PATCH
        for hub in self.hubs(world):
            hub.patch_lot = (
                hub.patch_lot
                or f"L-25{self.rng.randint(1, 12):02d}-{self.rng.choice('ABCDEF')}{self.rng.randint(10, 99)}"
            )
            self.detail = {"patch_lot": hub.patch_lot, "wear_time_h": hub.wear_time_h}

    def tick(self, world: World, now: datetime) -> None:
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        for hub in self.hubs(world):
            hub.rssi_dbm = max(-97, -61 - int(minutes / 3))
            hub.wear_time_h += minutes / 600
            hub.link_up = hub.rssi_dbm > -92
            self.detail["rssi_dbm"] = hub.rssi_dbm
            self.detail["wear_time_h"] = round(hub.wear_time_h, 1)

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.rssi_dbm = -61
            hub.link_up = True
            hub.wear_time_h = 4.0


class TransientBlip(Scenario):
    """Something happened and nothing is wrong.

    The honest case, and a real share of any fleet's traffic. Every check
    passes, which is `unknown-escalate` and a field visit rather than a guess —
    C4, and the run that lands there is the procedure working.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = "unknown-escalate"
        self.detail = {"note": "Every check passed. Nothing here explains the event."}
        for hub in self.hubs(world):
            hub.agent_up = False

    def tick(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.agent_up = True

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.agent_up = True


# -- tier 2: masked --------------------------------------------------------


class MaskedBacklog(Scenario):
    """A data box that stopped shipping, over a hub that is genuinely broken.

    OPS-SOP-004 works top down and stops at the first branch that fires, so it
    finds the box at §5.5 and never reaches the device at §5.6. The diagnosis is
    *correct* — the box really has stopped — and *incomplete*, because there is
    a crash-looping unit behind it that nobody is now going to look at.

    Being able to tell "incomplete" from "wrong" is the reason this tier exists.
    A procedure that terminates early is not a procedure that errs.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = DATA_BOX_BACKLOG
        self.masked_cause = DEVICE_FAULT
        self.detail = {
            "mode": "collector stopped",
            "masked": "crash-looping hub behind the backlog",
        }
        site = self.site(world)
        if site:
            site.collector_active = False
        for hub in self.hubs(world):
            hub.restarts_24h = 14

    def tick(self, world: World, now: datetime) -> None:
        site = self.site(world)
        if site is None:
            return
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        hubs = len([h for h in world.hubs_at(site.customer_id) if h.accrues])
        site.queue_depth = int(3 + minutes * hubs * 12)
        for hub in self.hubs(world):
            hub.restarts_24h = min(40, 14 + int(minutes / 5))

    def end(self, world: World, now: datetime) -> None:
        site = self.site(world)
        if site:
            site.collector_active = True
            site.queue_depth = 3
        for hub in self.hubs(world):
            hub.restarts_24h = 0


class MaskedPower(Scenario):
    """A dead socket over a patch that had already been failing.

    §5.3 fires and the triage stops. The link margin that had been degrading for
    two days is still degrading, and the row will say `power-loss` — which is
    true, and is not the whole truth.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = POWER_LOSS
        self.masked_cause = CONSUMABLE_PATCH
        for hub in self.hubs(world):
            hub.socket_live = False
            hub.socket_state = "unswitched"
            hub.on_dock = False
            hub.rssi_dbm = -91
            hub.link_up = False
            self.detail = {
                "socket_state": "unswitched",
                "pdu_port": hub.pdu_port,
                "on_dock": False,
                "masked": f"link margin already at {hub.rssi_dbm} dBm before the socket died",
            }

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.socket_live = True
            hub.socket_state = "live"
            hub.on_dock = True
            hub.rssi_dbm = -61
            hub.link_up = True


# -- tier 3: off-taxonomy --------------------------------------------------


class ClockSkew(Scenario):
    """The unit's clock has walked away from ours.

    NTP fails on the hub and `ts_device` drifts hours from `ts_received`. Power,
    path, box, device and link all read perfectly healthy, because they are. The
    fault is in a field OPS-SOP-004 rev 3.0 has no step that reads — the
    procedure's eight tools return eight clean results and the run escalates.

    This one is also quietly nasty in a way worth demoing: every rate in the
    product is windowed, and events that arrive stamped three hours ago land in
    the wrong window. The gap is real in the frozen dataset too; here it is
    large enough to see.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = "unknown-escalate"
        skew = self.rng.choice([-10800, -7200, 7200, 14400])
        self.detail = {
            "skew_s": skew,
            "note": (
                "Device clock has drifted from the ingest edge. No step of "
                "OPS-SOP-004 rev 3.0 reads a timestamp delta."
            ),
        }
        for hub in self.hubs(world):
            hub.clock_skew_s = skew

    def tick(self, world: World, now: datetime) -> None:
        """The symptom, which is not the fault.

        A device whose clock has walked off fails session validity against the
        collector, retries, and drops the link. So the stream carries
        CONN-LINK-LOSS and every estate check reads perfectly healthy — which is
        exactly the shape that walks the whole tree and escalates.
        """
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        for hub in self.hubs(world):
            hub.link_up = int(minutes / 20) % 2 == 1

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.clock_skew_s = 0
            hub.link_up = True


class UnauthorisedFirmware(Scenario):
    """A hub reporting a version that was never released to it.

    The unit is healthy on every check. It is running software the release
    manifest does not have against this serial — a field engineer's test build
    left on, or a rollback that did not roll back. The procedure has no step
    that compares reported firmware to what was shipped, so nothing fires.

    The story this plants is one the product should be able to find on its own:
    `sw_version` is authoritative on every event (TELEMETRY-API.md §5), so the
    evidence is right there in the stream and the SOP simply never looks at it.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = "unknown-escalate"
        for hub in self.hubs(world):
            rogue = self.rng.choice(["1.2.0-rc3", "1.1.9-eng", "0.9.14"])
            hub.reported_sw_version = rogue
            self.detail = {
                "reported": rogue,
                "inventory": hub.sw_version,
                "note": "Version not in the release manifest for this serial.",
            }
            # Two restarts a day against a threshold of three. The check at
            # §5.6 runs, reads a real number, and correctly does not fire —
            # which is a procedure working on evidence that does not reach it.
            hub.restarts_24h = 2

    def tick(self, world: World, now: datetime) -> None:
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        for hub in self.hubs(world):
            hub.link_up = int(minutes / 25) % 3 == 2

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.reported_sw_version = None
            hub.restarts_24h = 0
            hub.link_up = True


class PairingStorm(Scenario):
    """The pairing table churns while the radio is perfect.

    CONN-LINK-LOSS arrives in bursts, RSSI reads −58 dBm throughout, and the
    unit is up. §5.7 asks about link margin and the margin is fine, so the one
    branch that could have caught this does not fire. The cause is two hubs on
    one ward contending for the same pairing ID after a bed move — a
    configuration fact, and the procedure has no configuration step.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = "unknown-escalate"
        for hub in self.hubs(world):
            hub.pairing_status = "Contended"
            self.detail = {
                "pairing_id": hub.pairing_id,
                "note": (
                    "Two units claiming one pairing ID after a bed move. "
                    "Link margin is healthy; the fault is in configuration."
                ),
            }

    def tick(self, world: World, now: datetime) -> None:
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        for hub in self.hubs(world):
            hub.link_up = int(minutes) % 3 != 0
            hub.rssi_dbm = -58

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.pairing_status = "Paired"
            hub.link_up = True


class LotLinkCollapse(Scenario):
    """One patch lot failing across several customers at once.

    Per hub this presents exactly as `consumable-patch`, and the procedure will
    reach that conclusion and be locally right every time. But §5.1's scope
    question only asks about one *site*, and these hubs are at four different
    hospitals — so the thing that actually matters, that a single manufactured
    lot is bad, is invisible to a procedure that can only see one site at a time.

    The right output is not a diagnosis. It is a lot hold, and OPS-SOP-004 rev
    3.0 cannot ask for one.
    """

    def begin(self, world: World, now: datetime) -> None:
        self.expected_outcome = CONSUMABLE_PATCH
        lot = f"L-25{self.rng.randint(1, 12):02d}-R{self.rng.randint(10, 99)}"
        self.detail = {
            "patch_lot": lot,
            "sites": sorted({world.hubs[h].customer_id for h in self.hub_ids if h in world.hubs}),
            "note": (
                "One lot, several customers. Each hub triages to consumable-patch "
                "correctly; the lot-level pattern is above what §5.1 can see."
            ),
        }
        for hub in self.hubs(world):
            hub.patch_lot = lot

    def tick(self, world: World, now: datetime) -> None:
        minutes = max(0.0, (now - self.started_at).total_seconds() / 60)
        for hub in self.hubs(world):
            hub.rssi_dbm = max(-96, -63 - int(minutes / 2))
            hub.link_up = hub.rssi_dbm > -92

    def end(self, world: World, now: datetime) -> None:
        for hub in self.hubs(world):
            hub.rssi_dbm = -61
            hub.link_up = True


# -- the catalogue ---------------------------------------------------------


@dataclass(frozen=True)
class Spec:
    """One entry in the catalogue: how to build it and how often it happens."""

    cause: str
    tier: str
    label: str
    cls: type[Scenario]
    weight: float
    scope: str  # hub | site | multi-site
    minutes: tuple[int, int]
    codes: list[str]


CATALOGUE: list[Spec] = [
    Spec(
        EXPECTED_REMOVAL,
        CLEAN,
        "Expected removal",
        ExpectedRemoval,
        0.20,
        "hub",
        (40, 600),
        ["HUB-OFFLINE"],
    ),
    Spec(
        POWER_LOSS,
        CLEAN,
        "Power loss at the unit",
        PowerLoss,
        0.16,
        "hub",
        (30, 420),
        ["HUB-OFFLINE", "BATT"],
    ),
    Spec(
        SITE_NETWORK,
        CLEAN,
        "Site network interruption",
        SiteNetwork,
        0.10,
        "site",
        (25, 260),
        ["HUB-OFFLINE"],
    ),
    Spec(
        DATA_BOX_BACKLOG,
        CLEAN,
        "Data box not shipping",
        DataBoxBacklog,
        0.11,
        "site",
        (45, 400),
        ["HUB-OFFLINE"],
    ),
    Spec(
        DEVICE_FAULT,
        CLEAN,
        "Hub fault",
        DeviceFault,
        0.14,
        "hub",
        (35, 300),
        ["DISPLAY", "HUB-OFFLINE"],
    ),
    Spec(
        CONSUMABLE_PATCH,
        CLEAN,
        "Patch or link margin",
        ConsumablePatch,
        0.13,
        "hub",
        (30, 240),
        ["CONN-LINK-LOSS", "ADHESIVE"],
    ),
    Spec(
        NOTHING_FOUND,
        CLEAN,
        "Transient — nothing found",
        TransientBlip,
        0.05,
        "hub",
        (10, 45),
        ["HUB-OFFLINE"],
    ),
    Spec(
        DATA_BOX_BACKLOG,
        MASKED,
        "Backlog masking a hub fault",
        MaskedBacklog,
        0.04,
        "site",
        (60, 420),
        ["HUB-OFFLINE"],
    ),
    Spec(
        POWER_LOSS,
        MASKED,
        "Power loss masking a failing patch",
        MaskedPower,
        0.03,
        "hub",
        (40, 300),
        ["HUB-OFFLINE", "CONN-LINK-LOSS"],
    ),
    Spec(
        CLOCK_SKEW,
        OFF,
        "Device clock drift",
        ClockSkew,
        0.015,
        "hub",
        (90, 600),
        ["CONN-LINK-LOSS", "HUB-OFFLINE"],
    ),
    Spec(
        UNAUTHORISED_FIRMWARE,
        OFF,
        "Unreleased firmware in the field",
        UnauthorisedFirmware,
        0.015,
        "hub",
        (120, 900),
        ["ALERT-FALSE", "DISPLAY"],
    ),
    Spec(
        PAIRING_STORM,
        OFF,
        "Pairing ID contention",
        PairingStorm,
        0.015,
        "hub",
        (45, 240),
        ["CONN-LINK-LOSS"],
    ),
    Spec(
        LOT_LINK_COLLAPSE,
        OFF,
        "Patch lot failing across sites",
        LotLinkCollapse,
        0.01,
        "multi-site",
        (180, 900),
        ["ADHESIVE", "CONN-LINK-LOSS"],
    ),
]

BY_CAUSE = {(s.cause, s.tier): s for s in CATALOGUE}
