"""The estate as the diagnostic tools find it.

One `Situation` per episode: what is *actually* wrong, which the tools reveal
and the agent has to work out. It is derived, not stored, and derived the same
way every time — seeded on the episode's own artifact reference — so a triage
re-run reaches the same place and a test can assert on it.

Two things this is and is not:

    It is not a script. The situation decides what the tools report; the
    procedure decides what the agent concludes. Those are separate, which is
    why the agent can and does land on `unknown-escalate` — and why comparing
    the conclusion to `situation.cause` is a real score rather than a tautology.

    It is not arbitrary. The weighting reads the evidence already in the stream:
    a site cluster is overwhelmingly a network event, a DISPLAY fault is a
    device, a hub the inventory has decommissioned was pulled on purpose. The
    randomness only chooses between causes the evidence leaves open.

When the fleet simulator lands, this module is where a scenario's hidden cause
is injected instead of derived. Nothing downstream changes.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field

from asteria.capture.episodes import Episode
from asteria.resolve.entities import HubFacts

EXPECTED_REMOVAL = "expected-removal"
POWER_LOSS = "power-loss"
SITE_NETWORK = "site-network"
DATA_BOX_BACKLOG = "data-box-backlog"
DEVICE_FAULT = "device-fault"
CONSUMABLE_PATCH = "consumable-patch"
NOTHING_FOUND = "nothing-found"

# What the evidence leaves open, per code. The first number in each pair is the
# weight; they are read in order so the transcript of a decision is reproducible.
WEIGHTS: dict[str, list[tuple[str, float]]] = {
    "ADHESIVE": [(CONSUMABLE_PATCH, 0.75), (DEVICE_FAULT, 0.10), (NOTHING_FOUND, 0.15)],
    "DISPLAY": [(DEVICE_FAULT, 0.85), (POWER_LOSS, 0.05), (NOTHING_FOUND, 0.10)],
    "BATT": [
        (POWER_LOSS, 0.45),
        (DEVICE_FAULT, 0.30),
        (EXPECTED_REMOVAL, 0.10),
        (NOTHING_FOUND, 0.15),
    ],
    "CONN-LINK-LOSS": [
        (CONSUMABLE_PATCH, 0.40),
        (SITE_NETWORK, 0.20),
        (DEVICE_FAULT, 0.20),
        (NOTHING_FOUND, 0.20),
    ],
    "HUB-OFFLINE": [
        (EXPECTED_REMOVAL, 0.22),
        (POWER_LOSS, 0.24),
        (DATA_BOX_BACKLOG, 0.20),
        (SITE_NETWORK, 0.12),
        (DEVICE_FAULT, 0.12),
        (NOTHING_FOUND, 0.10),
    ],
}

# A site cluster overrides the per-code weighting outright. Three hubs at one
# hospital going quiet in the same 72 hours is a network event; the alternative
# is three independent faults on the same afternoon, which is not a thing.
CLUSTER_WEIGHTS = [(SITE_NETWORK, 0.82), (DATA_BOX_BACKLOG, 0.13), (NOTHING_FOUND, 0.05)]

REMOVAL_REASONS = [
    ("discharge", "Session ended at discharge; unit unplugged by ward staff."),
    ("planned_works", "Customer notified a planned electrical shutdown on this ward."),
    ("bereavement", "Patient deceased. Unit removed by ward staff, session closed."),
    ("ward_move", "Bed reallocated; unit moved and not re-docked."),
]


@dataclass(frozen=True)
class Situation:
    """What is wrong, and the specifics the tools will surface."""

    episode_key: str
    cause: str
    detail: dict = field(default_factory=dict)

    @property
    def benign(self) -> bool:
        return self.cause in (EXPECTED_REMOVAL, NOTHING_FOUND)


def derive(episode: Episode, hub: HubFacts | None) -> Situation:
    """The situation behind one episode. Deterministic on the episode."""
    rng = random.Random(_seed(episode.artifact_ref))

    # Facts that settle it outright, before any weighting.
    if hub is not None and not hub.accrues and hub.unit_status != "Decommissioned":
        # A spare in a cupboard or a unit still in transit. It is not on a ward
        # and there is nothing to triage.
        return Situation(episode.artifact_ref, EXPECTED_REMOVAL, _removal(rng, hub, "inventory"))

    weights = CLUSTER_WEIGHTS if episode.cluster else WEIGHTS.get(episode.code, CLUSTER_WEIGHTS)
    cause = _weighted(rng, weights)
    return Situation(episode.artifact_ref, cause, _detail(rng, cause, episode, hub))


def _detail(rng: random.Random, cause: str, episode: Episode, hub: HubFacts | None) -> dict:
    match cause:
        case s if s == EXPECTED_REMOVAL:
            return _removal(rng, hub, "ward")
        case s if s == POWER_LOSS:
            return {
                "socket_state": rng.choice(["unswitched", "no supply", "PoE port down"]),
                "pdu_port": f"A{rng.randint(1, 24):02d}",
                "battery_pct_at_silence": rng.choice([0, 0, 1, 2]),
                "on_dock": False,
            }
        case s if s == SITE_NETWORK:
            fault = rng.choice(["tunnel down", "packet loss", "dns failure"])
            return {
                "fault": fault,
                "loss_pct": round(rng.uniform(18, 64), 1) if fault == "packet loss" else 0.0,
                "rtt_ms": rng.randint(900, 2400) if fault == "packet loss" else 0,
                "change_window": rng.choice(
                    ["scheduled firewall change", "core switch replacement", "VLAN re-addressing"]
                ),
            }
        case s if s == DATA_BOX_BACKLOG:
            mode = rng.choice(["collector stopped", "disk full", "cert expired"])
            return {
                "mode": mode,
                "collector_active": mode != "collector stopped",
                "queue_depth": rng.randint(1800, 24000),
                "disk_used_pct": 97 if mode == "disk full" else rng.randint(58, 81),
                "cert_days_remaining": -rng.randint(1, 9) if mode == "cert expired" else 121,
            }
        case s if s == DEVICE_FAULT:
            mode = rng.choice(["crash loop", "post fault", "crash loop"])
            return {
                "mode": mode,
                "restarts_24h": rng.randint(5, 31) if mode == "crash loop" else 0,
                "post_code": (episode.payload_value("post_code") or f"E-{rng.randint(200, 260)}")
                if mode == "post fault"
                else None,
                "fault": episode.payload_value("fault") or "watchdog reset",
            }
        case s if s == CONSUMABLE_PATCH:
            return {
                "rssi_dbm": episode.payload_value("rssi_at_loss") or -rng.randint(88, 97),
                "wear_time_h": episode.payload_value("wear_time_h") or rng.randint(38, 96),
                "patch_lot": episode.payload_value("patch_lot"),
            }
        case _:
            return {"note": "Every check passed. Nothing here explains the event."}


def _removal(rng: random.Random, hub: HubFacts | None, basis: str) -> dict:
    if basis == "inventory" and hub is not None:
        return {
            "basis": "inventory",
            "reason": "unit_status",
            "narrative": f"Inventory has this unit as {hub.unit_status}. It is not on a ward.",
        }
    reason, narrative = REMOVAL_REASONS[rng.randrange(len(REMOVAL_REASONS))]
    return {"basis": basis, "reason": reason, "narrative": narrative}


def _weighted(rng: random.Random, weights: list[tuple[str, float]]) -> str:
    total = sum(w for _, w in weights)
    point = rng.random() * total
    running = 0.0
    for cause, weight in weights:
        running += weight
        if point <= running:
            return cause
    return weights[-1][0]


def _seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")
