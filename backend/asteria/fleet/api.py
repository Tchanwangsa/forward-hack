"""The PulseOne fleet service. A separate process, on purpose.

This is not part of Asteria. It is the device cloud the hubs already report to,
and Asteria is a *second consumer* of a stream that exists whether or not the
surveillance product does (TELEMETRY-API.md, opening). Running it on its own
port is what keeps that boundary honest: the backend polls it over HTTP, the
same way it would poll a real one, and nothing in the product can reach into the
simulator's state except through an endpoint a real device cloud would also have.

Three groups of route, and the third one is fenced:

    /v1/telemetry, /v1/fleet, /v1/metrics   the spec's endpoints, live
    /v1/estate, /v1/ward                    the read-only diagnostic surface the
                                            eight triage tools read. Diagnosis
                                            only — there is nothing here that
                                            restarts, reconfigures or flashes
                                            anything (OPS-SOP-004 §3 C1).
    /v1/sim                                 the simulator's own controls, and
                                            the hidden cause. THE AGENT MUST
                                            NEVER READ /v1/sim/scenarios — it is
                                            the answer key, and it exists so the
                                            scorer can mark the paper.
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import ClassVar

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from asteria.fleet.clock import Clock
from asteria.fleet.engine import Engine
from asteria.fleet.world import OFFLINE_THRESHOLD, World

REPO_ROOT = Path(__file__).resolve().parents[3]
INVENTORY = (
    REPO_ROOT / "mock-company" / "registers" / "PM-Customer-Organisations-and-Hubs-Record.xlsx"
)

# Real seconds between ticks. The simulated step is this times clock speed.
TICK_SECONDS = 1.0

# PMS-PLAN-001 v3.0, per 100 unit-months. The plan's numbers, not ours — the
# simulator does not get to decide what normal is.
BASELINES = {
    "CONN-LINK-LOSS": 1.3,
    "HUB-OFFLINE": 0.9,
    "BATT": 0.6,
    "ALERT-FALSE": 1.1,
    "ADHESIVE": 0.4,
    "SKIN": 0.12,
    "DISPLAY": 0.8,
}
# Below this much time in service, a rate is arithmetic and not evidence. Two
# events on half a unit-month is a 400x ratio and means nothing, and a
# surveillance product that raises a signal off it has taught its users to
# ignore signals. The real plan carries the same guard for the same reason —
# a denominator is not a formality.
MIN_UNIT_MONTHS = 12.0

INDICATOR_OF = {
    "CONN-LINK-LOSS": "IND-01",
    "HUB-OFFLINE": "IND-02",
    "BATT": "IND-03",
    "ALERT-FALSE": "IND-04",
    "ADHESIVE": "IND-05",
    "SKIN": "IND-06",
    "DISPLAY": "IND-07",
}


class Hub:
    """Module-level singletons, held on one object so tests can build their own."""

    engine: Engine | None = None
    subscribers: ClassVar[set[asyncio.Queue]] = set()


def build_engine(
    *,
    speed: float = 60.0,
    intensity: float = 40.0,
    rate: float | None = None,
    seed: int = 20260913,
) -> Engine:
    now = datetime.now(UTC)
    world = World.from_inventory(INVENTORY, now=now, seed=seed)
    return Engine(world=world, clock=Clock(origin=now, speed=speed), intensity=intensity, rate=rate)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    rate = os.getenv("FLEET_RATE")
    Hub.engine = build_engine(
        speed=float(os.getenv("FLEET_SPEED", "60")),
        intensity=float(os.getenv("FLEET_INTENSITY", "40")),
        rate=float(rate) if rate else None,
        seed=int(os.getenv("FLEET_SEED", "20260913")),
    )
    task = asyncio.create_task(_run(Hub.engine))
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


async def _run(engine: Engine) -> None:
    """Tick, and hand whatever came out to anybody listening."""
    while True:
        await asyncio.sleep(TICK_SECONDS)
        events = await asyncio.to_thread(engine.tick)
        if not events:
            continue
        for queue in list(Hub.subscribers):
            for event in events:
                with contextlib.suppress(asyncio.QueueFull):
                    queue.put_nowait(event)


app = FastAPI(title="PulseOne Fleet Service", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("FLEET_CORS", "http://localhost:5173,http://localhost:8000").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


def engine() -> Engine:
    if Hub.engine is None:  # pragma: no cover - only before lifespan
        raise HTTPException(503, "fleet service is still starting")
    return Hub.engine


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "pulseone-fleet"}


# -- the spec's endpoints --------------------------------------------------


@app.get("/v1/telemetry/events")
def telemetry_events(
    since: int = Query(0, description="cursor: the last event sequence you saw"),
    code: str | None = None,
    hub_id: str | None = None,
    customer: str | None = None,
    sw_version: str | None = None,
    limit: int = Query(500, le=5000),
) -> dict:
    """The query surface outage watch runs on. Cursor-paginated on `since`.

    The cursor is the whole reason the poller is simple: ask for what you have
    not seen, get it once. Idempotency on `(hub_id, ts, code)` is still the
    consumer's job — `dedupe_key` is on every row for exactly that, and a
    replayed buffer counted five times is a fabricated signal.
    """
    e = engine()
    events, cursor = e.world.since(since)
    if code:
        events = [x for x in events if x["code"] == code]
    if hub_id:
        events = [x for x in events if x["hub_id"] == hub_id]
    if customer:
        events = [x for x in events if x["customer_id"] == customer]
    if sw_version:
        events = [x for x in events if x["sw_version"] == sw_version]
    page = events[:limit]
    # The scenario is the answer key; it never leaves via this route.
    clean = [{k: v for k, v in x.items() if k != "scenario_id"} for x in page]
    return {
        "events": clean,
        "cursor": _seq(page[-1]) if page else cursor,
        "more": len(events) > limit,
        "as_at": e.clock.now().isoformat(),
    }


@app.post("/v1/telemetry/events", status_code=202)
async def ingest_event(request: Request) -> dict:
    """Ingest, for completeness and for the backfill job.

    A real hub posts here. Nothing in this repo does — the simulated fleet's
    events are produced inside the world — but the route exists because the
    contract is the contract, and because a demo that wants to hand-place one
    event should not have to reach into the simulator to do it.
    """
    e = engine()
    body = await request.json()
    hub = e.world.hubs.get(body.get("hub_id", ""))
    if hub is None:
        raise HTTPException(404, f"unknown hub {body.get('hub_id')!r}")
    event = e.world.emit(
        hub,
        body.get("code", "HEARTBEAT"),
        e.clock.now(),
        severity=body.get("severity", "info"),
        payload=body.get("payload") or {},
    )
    return {"event_id": event["event_id"], "accepted": True}


@app.get("/v1/fleet/hubs")
def fleet_hubs(
    customer: str | None = None,
    online: bool | None = None,
    accruing: bool | None = None,
) -> dict:
    """Current state, one row per hub. The Fleet screen's data.

    `online` is derived from `last_seen` against the offline threshold, never
    stored — and `unit_status`, `customer_id` and `ward_id` come from the
    inventory sheet, which telemetry does not get to overwrite. Telemetry owns
    state; the register owns the roster (TELEMETRY-API.md §7).
    """
    e = engine()
    now = e.clock.now()
    rows = [h.inventory_row(now) for h in e.world.hubs.values()]
    if customer:
        rows = [r for r in rows if r["customer_id"] == customer]
    if online is not None:
        rows = [r for r in rows if r["online"] is online]
    if accruing is not None:
        rows = [r for r in rows if r["accrues"] is accruing]
    return {"hubs": rows, "count": len(rows), "as_at": now.isoformat()}


@app.get("/v1/fleet/hubs/{hub_id}")
def fleet_hub(hub_id: str) -> dict:
    e = engine()
    hub = e.world.hubs.get(hub_id)
    if hub is None:
        raise HTTPException(404, f"unknown hub {hub_id!r}")
    now = e.clock.now()
    return {
        **hub.inventory_row(now),
        "heartbeats": list(hub.heartbeats)[-40:],
        "events": [
            {k: v for k, v in x.items() if k != "scenario_id"}
            for x in e.world.events
            if x["hub_id"] == hub_id
        ][-40:],
    }


@app.get("/v1/metrics/indicators")
def metrics_indicators(window_days: int = 90, cohort: str | None = None) -> dict:
    """Deterministic. No model runs behind this endpoint.

    One row per indicator × cohort, with the denominator shown and the event IDs
    behind the number listed. `event_ids` is not optional: a rate that cannot be
    opened up into the events behind it is a number nobody can check.
    """
    e = engine()
    now = e.clock.now()
    start = now - timedelta(days=window_days)

    kind, value = cohort.split(":", 1) if cohort and ":" in cohort else (None, None)
    hubs = [h for h in e.world.hubs.values() if h.accrues]
    if kind == "sw_version":
        hubs = [h for h in hubs if h.effective_sw == value]
    elif kind == "customer":
        hubs = [h for h in hubs if h.customer_id == value]
    in_cohort = {h.hub_id for h in hubs}

    # Unit-months in service over the window, which is the only denominator
    # that survives a fleet still being installed — clamped to when this service
    # started observing. A hub installed in 2025 has eighteen months in service
    # and no events here from any of it, and counting that time would divide a
    # real numerator by a denominator we have no numerator for. The honest
    # window is the intersection of "in service" and "watched".
    observed_from = max(start, e.clock.origin)
    unit_months = 0.0
    for hub in hubs:
        began = max(hub.install_date, observed_from) if hub.install_date else observed_from
        unit_months += max(0.0, (now - began).total_seconds()) / (86400 * 30.44)
    per_100 = unit_months / 100 if unit_months else 0.0

    events = [
        x
        for x in e.world.events
        if x["hub_id"] in in_cohort and datetime.fromisoformat(x["ts_received"]) >= start
    ]

    # The simulated fleet runs hot by `intensity` (engine.py). Comparing a rate
    # from a 40x fleet against the plan's baseline would mark every indicator
    # breached and mean nothing, so the baseline is scaled by the same factor —
    # which leaves a breach saying what it should say: this *cohort* is
    # anomalous against its own fleet, not that the demo is turned up.
    out = []
    for code, plan_baseline in BASELINES.items():
        baseline = plan_baseline * (e.intensity or 1.0)
        hits = [x for x in events if x["code"] == code]
        rate = (len(hits) / per_100) if per_100 else 0.0
        threshold = baseline * 2.0
        out.append(
            {
                "indicator_id": INDICATOR_OF[code],
                "internal_code": code,
                "cohort": {"kind": kind or "fleet", "value": value or "all"},
                "window": {
                    "start": start.isoformat(),
                    "observed_from": observed_from.isoformat(),
                    "end": now.isoformat(),
                    "days": window_days,
                },
                "event_count": len(hits),
                "denominator": {
                    "basis": "unit_months_in_service",
                    "value": round(unit_months, 2),
                    "unit": "per 100 unit-months",
                    "hubs_counted": len(hubs),
                    "is_estimate": False,
                    "minimum_for_signal": MIN_UNIT_MONTHS,
                },
                "observed_rate": round(rate, 2),
                "baseline": round(baseline, 3),
                "baseline_pms_plan": plan_baseline,
                "simulation_intensity": e.intensity,
                "threshold": {"kind": "ratio", "multiplier": 2.0, "value": threshold},
                "ratio": round(rate / baseline, 2) if baseline else None,
                "breached": rate > threshold and unit_months >= MIN_UNIT_MONTHS,
                "insufficient_denominator": unit_months < MIN_UNIT_MONTHS,
                "event_ids": [x["event_id"] for x in hits],
                "rule_version": "PMS-PLAN-001-v3.0",
                # Everything here is live. The trailing baseline the real
                # product computes also draws on twenty months of backfill,
                # which this service has not got and does not pretend to.
                "basis_note": (
                    "Live simulated window only — excludes the twenty months of "
                    "register backfill the real trailing baseline draws on. "
                    "`baseline` is PMS-PLAN-001's number scaled by the "
                    "simulation intensity; `baseline_pms_plan` is the plan's own."
                ),
            }
        )
    return {"indicators": out, "as_at": now.isoformat()}


# -- the diagnostic surface ------------------------------------------------
# Read-only. QMS-WI-011 grants remote access to a customer estate for
# diagnosis; a product that quietly widens that to remediation has changed what
# the customer agreed to. There is no route below that writes.


@app.get("/v1/estate/hubs/{hub_id}")
def estate_hub(hub_id: str) -> dict:
    """What an engineer sees on the unit: power at the wall, and the unit itself."""
    e = engine()
    hub = e.world.hubs.get(hub_id)
    if hub is None:
        raise HTTPException(404, f"unknown hub {hub_id!r}")
    now = e.clock.now()
    reachable = e.world.reachable(hub)
    return {
        "hub_id": hub_id,
        "as_at": now.isoformat(),
        "power": {
            "socket_live": hub.socket_live,
            "socket_state": hub.socket_state,
            "pdu_port": hub.pdu_port,
            "on_dock": hub.on_dock,
            "battery_pct": round(hub.battery_pct, 1),
            "last_draw_w": 0.0 if not hub.socket_live else 11.4,
        },
        "device": {
            "reachable": reachable,
            "agent_up": hub.agent_up,
            "restarts_24h": hub.restarts_24h,
            "post_code": hub.post_code,
            "post_pass": hub.post_code is None,
            "uptime_s": 240 if hub.restarts_24h else 1578120,
            "sw_version": hub.effective_sw,
            "sw_version_inventory": hub.sw_version,
            "clock_skew_s": hub.clock_skew_s,
        },
        "link": {
            "rssi_dbm": hub.rssi_dbm,
            "link_up": hub.link_up,
            "pairing_id": hub.pairing_id,
            "pairing_status": hub.pairing_status,
            "wear_time_h": round(hub.wear_time_h, 1),
            "patch_lot": hub.patch_lot,
        },
        "cloud": {
            "visible": e.world.visible_to_cloud(hub),
            "last_seen": hub.last_seen.isoformat() if hub.last_seen else None,
            "offline_threshold_min": OFFLINE_THRESHOLD.total_seconds() / 60,
        },
    }


@app.get("/v1/estate/sites/{customer_id}")
def estate_site(customer_id: str) -> dict:
    """The path to us, and the box in their comms room."""
    e = engine()
    site = e.world.sites.get(customer_id)
    if site is None:
        raise HTTPException(404, f"unknown customer {customer_id!r}")
    now = e.clock.now()
    hubs = [h for h in e.world.hubs_at(customer_id) if h.accrues]
    return {
        "customer_id": customer_id,
        "organisation": site.organisation,
        "as_at": now.isoformat(),
        "net_path": {
            "tunnel_up": site.tunnel_up,
            "dns_ok": site.dns_ok,
            "loss_pct": site.loss_pct,
            "rtt_ms": site.rtt_ms,
            "healthy": site.path_healthy,
            "change_window": site.change_window,
        },
        "data_box": {
            "host": site.host,
            "agent": site.databox_agent,
            "collector_active": site.collector_active,
            "queue_depth": site.queue_depth,
            "disk_used_pct": site.disk_used_pct,
            "cert_days_remaining": site.cert_days_remaining,
            "last_upload": site.last_upload.isoformat() if site.last_upload else None,
            "healthy": site.databox_healthy,
        },
        "fleet": {
            "hubs_accruing": len(hubs),
            "hubs_quiet": sum(1 for h in hubs if not e.world.visible_to_cloud(h)),
        },
        "planned_works_note": site.planned_works_note,
    }


@app.get("/v1/ward/occupancy")
def ward_occupancy(hub_id: str) -> dict:
    """Occupancy only. Yes or no, and nothing else.

    OPS-SOP-004 §3 C2 and TELEMETRY-API.md §7 are the same rule read from two
    directions: the product may know that a bed was empty and may never know who
    was in it. There is no patient identifier behind this route to return.
    """
    e = engine()
    hub = e.world.hubs.get(hub_id)
    if hub is None:
        raise HTTPException(404, f"unknown hub {hub_id!r}")
    return {
        "ward_id": hub.ward_id,
        "bed_id": hub.bed_id,
        "bed_occupied": hub.bed_occupied,
        "session_closed_cleanly": hub.session_closed_cleanly,
        "removal_reason": hub.removal_reason,
    }


# -- the simulator's own controls -----------------------------------------


@app.get("/v1/sim/status")
def sim_status() -> dict:
    return engine().status()


@app.get("/v1/sim/scenarios")
def sim_scenarios(limit: int = 50) -> dict:
    """THE ANSWER KEY. Scoring only.

    Every scenario in flight and recently retired, with the hidden cause, the
    tier, and what OPS-SOP-004 ought to conclude on the evidence available. The
    triage runner must never call this — if it did, `TriageResult.correct` would
    stop being a measurement and become a tautology, and the one honest number
    in the system would be worthless.
    """
    e = engine()
    return {
        "warning": "hidden causes — scoring only, never an input to triage",
        "active": [s.describe() for s in e.active],
        "completed": [s.describe() for s in e.history[-limit:]],
    }


@app.post("/v1/sim/inject")
def sim_inject(cause: str, tier: str = "clean") -> dict:
    """Force a scenario, for a demo that cannot wait on a Poisson draw."""
    scenario = engine().inject(cause, tier)
    if scenario is None:
        raise HTTPException(400, f"no scenario for cause={cause!r} tier={tier!r}, or no free hubs")
    return scenario.describe()


@app.get("/v1/sim/stream")
async def sim_stream(request: Request) -> StreamingResponse:
    """Server-sent events. The fleet moving, live, with no polling interval."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
    Hub.subscribers.add(queue)

    async def events() -> AsyncIterator[str]:
        try:
            yield f": connected to pulseone-fleet at {engine().clock.now().isoformat()}\n\n"
            while not await request.is_disconnected():
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=15)
                except TimeoutError:
                    yield ": keepalive\n\n"
                    continue
                payload = {k: v for k, v in event.items() if k != "scenario_id"}
                yield f"event: telemetry\ndata: {json.dumps(payload)}\n\n"
        finally:
            Hub.subscribers.discard(queue)

    return StreamingResponse(events(), media_type="text/event-stream")


def _seq(event: dict) -> int:
    return int(event["event_id"].rsplit("-", 1)[-1])
