"""Eight read-only diagnostic tools over the estate. The agent's hands.

Each tool returns the two things a triage step needs and a demo needs:

    metrics     structured, which the procedure's conditions read
    transcript  what the analyst would have seen on their screen

The transcript is not decoration. It is the provenance for the diagnosis in
exactly the way a telemetry event ID is the provenance for a drafted row — if
the agent says the upload queue was 12,000 deep, the queue must be able to show
the line it read that from (DASHBOARD.md §The artifact pane).

Every tool is a read. There is no ninth tool that restarts anything, and adding
one would break OPS-SOP-004 §3 C1 and TELEMETRY-API.md §7 in the same stroke:
remote access to a customer's estate is granted for diagnosis, and a product
that quietly widens it to remediation has changed what the customer agreed to.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from asteria.capture.episodes import Episode
from asteria.models.capture_fed import Incident
from asteria.resolve.entities import HubFacts
from asteria.triage import estate
from asteria.triage.estate import Situation


@dataclass
class ToolResult:
    """One check, its reading, and the screen it came off."""

    tool: str
    target: str
    summary: str
    metrics: dict = field(default_factory=dict)
    transcript: list[str] = field(default_factory=list)

    @property
    def ref(self) -> str:
        """Provenance, in the same shape as tel: and inv: refs elsewhere."""
        return f"probe:{self.tool}@{self.target}"


@dataclass
class Probe:
    """What every tool is given. One per triage run.

    `readings` is one round of live probes off the fleet service, taken together
    so that every tool in a run describes the same instant. When it is absent —
    no simulator running, or a triage over the frozen twenty months of backfill
    — the tools fall back to `situation`, which is the derived estate this
    module was originally written against. Same transcripts either way; the only
    difference is whether the numbers in them came from a world or from a
    weighted draw.
    """

    episode: Episode
    hub: HubFacts | None
    situation: Situation
    thresholds: dict
    session: Session | None = None
    readings: dict | None = None

    def live(self, *path: str) -> dict:
        """A section of the live reading, or an empty dict when there is none.

        Empty rather than None on purpose: a tool that reads `{}` falls through
        to its derived branch, and a metric that is absent is not a condition
        that is true (conditions.py, opening).
        """
        node = self.readings or {}
        for key in path:
            node = (node or {}).get(key) or {}
        return node if isinstance(node, dict) else {}

    @property
    def is_live(self) -> bool:
        return bool(self.readings)

    @property
    def hub_id(self) -> str:
        return self.episode.hub_id

    @property
    def host(self) -> str:
        return f"{self.hub_id.lower()}.pulseone.local"

    @property
    def site(self) -> str:
        return (self.hub.customer_id if self.hub else None) or "SITE-UNKNOWN"

    @property
    def databox(self) -> str:
        return f"databox-{self.site.lower().replace('cust-', '')}.pulseone.local"


# -- fleet -----------------------------------------------------------------


def hub_status(p: Probe) -> ToolResult:
    """Fleet state for one hub. The first thing anybody looks at."""
    ep = p.episode
    cluster = ep.cluster
    peers = len(cluster.hub_ids) if cluster else 1
    metrics = {
        "hub_id": p.hub_id,
        "unit_status": p.hub.unit_status if p.hub else None,
        "unit_accrues": bool(p.hub and p.hub.accrues),
        "sw_version": ep.primary.sw_version,
        "hw_revision": ep.primary.hw_revision,
        "last_event": ep.closed_at.isoformat(),
        "events_in_episode": len(ep.events),
        "peers_affected": peers,
        "site_wide": peers >= p.thresholds["site_wide_min_hubs"],
        "ward_wide_flag": bool(ep.payload_value("ward_wide")),
    }
    lines = [
        f"$ asteria fleet status {p.hub_id}",
        f"  hub          {p.hub_id}  ({p.hub.serial_number if p.hub else '?'})",
        (
            f"  site         {p.site}  ward {p.hub.ward_id if p.hub else '?'}"
            f"  bed {p.hub.bed_id if p.hub else '?'}"
        ),
        (
            f"  inventory    {p.hub.unit_status if p.hub else 'unknown'}"
            f"  hw {ep.primary.hw_revision}  sw {ep.primary.sw_version}"
        ),
        (
            f"  episode      {ep.code} x{len(ep.events)} over {ep.span_hours:.1f}h,"
            f" opened {ep.opened_at:%Y-%m-%d %H:%M}"
        ),
    ]
    if cluster:
        lines.append(
            f"  site-wide    {len(cluster.hub_ids)} hubs raised {cluster.code} "
            f"within {cluster.span_days}d: {', '.join(cluster.hub_ids[:6])}"
            + (" ..." if len(cluster.hub_ids) > 6 else "")
        )
    else:
        lines.append("  site-wide    no — no other hub at this site raised this code")
    return ToolResult(
        "fleet.hub_status",
        p.hub_id,
        f"{peers} hub(s) affected at {p.site}" + (" — site-wide" if metrics["site_wide"] else ""),
        metrics,
        lines,
    )


def heartbeat_gaps(p: Probe) -> ToolResult:
    """Where the silence starts and whether it ended. The shape of an outage."""
    ep = p.episode
    gap_h = ep.payload_value("offline_duration_h") or round(ep.span_hours, 1)
    returned = p.situation.cause != estate.DEVICE_FAULT or ep.repeats > 0
    metrics = {
        "gap_h": float(gap_h),
        "silence_started": ep.opened_at.isoformat(),
        "returned": returned,
        "flaps": ep.repeats,
        "abrupt": p.situation.cause in (estate.POWER_LOSS, estate.SITE_NETWORK),
    }
    lines = [
        f"$ asteria fleet heartbeats {p.hub_id} --around {ep.opened_at:%Y-%m-%dT%H:%M}",
        (
            f"  {(ep.opened_at - timedelta(minutes=10)):%H:%M:%S}  ok    battery"
            f" {ep.payload_value('battery_pct') or 94}%  sw {ep.primary.sw_version}"
        ),
        (
            f"  {(ep.opened_at - timedelta(minutes=5)):%H:%M:%S}  ok    battery"
            f" {ep.payload_value('battery_pct') or 94}%  sw {ep.primary.sw_version}"
        ),
        f"  {ep.opened_at:%H:%M:%S}  ---   last contact",
        f"  gap of {gap_h}h"
        + (f", {ep.repeats} further drop(s) after it returned" if ep.repeats else ""),
        "  " + ("service resumed" if returned else "no heartbeat since"),
    ]
    return ToolResult(
        "fleet.heartbeat_gaps",
        p.hub_id,
        f"{gap_h}h of silence from {ep.opened_at:%H:%M}",
        metrics,
        lines,
    )


# -- context ---------------------------------------------------------------


def registers_context(p: Probe) -> ToolResult:
    """What the company already knows about this hub. Read before touching it.

    A hub with three device faults in a month is a different conversation from
    one with none, and a planned electrical shutdown the customer told us about
    in writing is the whole answer to why a ward went quiet at 02:00.
    """
    prior = _prior_incidents(p)
    site = p.live("site")
    if site:
        planned = bool(site.get("planned_works_note"))
        change_window = (site.get("net_path") or {}).get("change_window")
    else:
        d = p.situation.detail
        planned = (
            p.situation.cause == estate.EXPECTED_REMOVAL and d.get("reason") == "planned_works"
        )
        change_window = d.get("change_window") if p.situation.cause == estate.SITE_NETWORK else None
    metrics = {
        "prior_incidents_30d": len(prior),
        "prior_device_faults_30d": sum(1 for i in prior if i.event_code in ("DISPLAY", "BATT")),
        "planned_works_covers_unit": planned,
        "site_change_window": change_window,
        "decommission_pending": bool(p.hub and p.hub.unit_status == "Decommissioned"),
    }
    lines = [f"$ asteria registers context {p.hub_id} --window 30d"]
    lines += (
        [
            f"  {i.incident_id}  {i.reported_date}  {i.event_code or '(uncoded)'}  {i.status}"
            for i in prior[:4]
        ]
        if prior
        else ["  no incident rows on this hub in the preceding 30 days"]
    )
    if planned:
        lines += [
            "  comms log   customer notice: planned electrical shutdown,",
            f"              {p.hub.ward_id if p.hub else 'this ward'}, covering the outage window",
        ]
    elif change_window:
        lines += [
            f"  comms log   customer notice: {change_window} at this site",
            "              (site-scope, does not by itself explain a single unit)",
        ]
    else:
        lines.append("  comms log   no planned-works notice covering this window")
    return ToolResult(
        "registers.context",
        p.hub_id,
        f"{len(prior)} prior incident(s) in 30d"
        + ("; planned works notice covers this unit" if planned else ""),
        metrics,
        lines,
    )


def ward_occupancy(p: Probe) -> ToolResult:
    """Was there a patient on it? Yes or no, and nothing else.

    OPS-SOP-004 §3 C2. The dashboard is allowed to know that a bed was empty;
    it is never allowed to know who was in it (TELEMETRY-API.md §7).
    """
    ward = p.live("ward")
    if ward:
        occupied = bool(ward.get("bed_occupied"))
        removal = bool(ward.get("session_closed_cleanly"))
        reason = ward.get("removal_reason")
    else:
        d = p.situation.detail
        removal = p.situation.cause == estate.EXPECTED_REMOVAL and d.get("basis") != "inventory"
        occupied = not removal
        reason = d.get("reason") if removal else None
    metrics = {
        "bed_occupied_at_onset": occupied,
        "session_closed_cleanly": removal,
        "removal_reason": reason,
    }
    lines = [
        (
            f"$ asteria ward occupancy --ward {p.hub.ward_id if p.hub else '?'}"
            f" --bed {p.hub.bed_id if p.hub else '?'}"
            f" --at {p.episode.opened_at:%Y-%m-%dT%H:%M}"
        ),
        "  (occupancy only — no patient identifier is returned by this endpoint)",
        f"  bed occupied at onset   {'yes' if occupied else 'no'}",
        f"  session at onset        {'active' if occupied else 'closed by ward, ended normally'}",
    ]
    if removal and reason:
        lines.append(f"  ward note               session closed by ward — {reason}")
    return ToolResult(
        "ward.occupancy",
        f"{p.hub.ward_id if p.hub else '?'}/{p.hub.bed_id if p.hub else '?'}",
        "bed occupied at onset" if occupied else "bed was empty — session already closed",
        metrics,
        lines,
    )


# -- estate probes ---------------------------------------------------------


def socket_check(p: Probe) -> ToolResult:
    """Mains and PoE at the wall. The check everybody skips and shouldn't."""
    power = p.live("hub", "power")
    if power:
        metrics = {
            "socket_live": bool(power.get("socket_live")),
            "socket_state": power.get("socket_state"),
            "pdu_port": power.get("pdu_port"),
            # The live reading is where the discharge curve actually got to,
            # not a number chosen to look plausible next to a dead socket.
            "battery_pct_at_silence": power.get("battery_pct"),
            "on_dock": bool(power.get("on_dock")),
            "last_draw_w": power.get("last_draw_w"),
        }
        dead = not metrics["socket_live"]
    else:
        dead = p.situation.cause == estate.POWER_LOSS
        d = p.situation.detail
        metrics = {
            "socket_live": not dead,
            "socket_state": d.get("socket_state") if dead else "live",
            "pdu_port": d.get("pdu_port", "A07"),
            "battery_pct_at_silence": d.get("battery_pct_at_silence", 91) if dead else 88,
            "on_dock": bool(d.get("on_dock", True)) if dead else True,
        }
    lines = [
        f"$ asteria estate power --hub {p.hub_id}",
        f"  pdu          {p.site}-PDU-01 port {metrics['pdu_port']}",
        f"  port state   {'DOWN — ' + str(metrics['socket_state']) if dead else 'UP'}",
        (
            f"  last draw    {metrics.get('last_draw_w', 0.0 if dead else 11.4)} W"
            f" at {p.episode.opened_at:%Y-%m-%d %H:%M}"
        ),
        f"  dock         {'not docked' if dead and not metrics['on_dock'] else 'docked'}",
        f"  battery at last report   {metrics['battery_pct_at_silence']}%",
    ]
    return ToolResult(
        "power.socket_check",
        p.hub_id,
        "socket dead at the wall" if dead else "power present, unit drawing normally",
        metrics,
        lines,
    )


def path_check(p: Probe) -> ToolResult:
    """Site to cloud. The tunnel, the resolver, the loss."""
    path = p.live("site", "net_path")
    if path:
        metrics = {
            "tunnel_up": bool(path.get("tunnel_up")),
            "dns_ok": bool(path.get("dns_ok")),
            "loss_pct": float(path.get("loss_pct", 0.0)),
            "rtt_ms": int(path.get("rtt_ms", 31)),
            "peers_reachable": bool(path.get("healthy")),
            "change_window": path.get("change_window"),
        }
        broken = not path.get("healthy")
    else:
        broken = p.situation.cause == estate.SITE_NETWORK
        d = p.situation.detail if broken else {}
        fault = d.get("fault")
        metrics = {
            "tunnel_up": not (broken and fault == "tunnel down"),
            "dns_ok": not (broken and fault == "dns failure"),
            "loss_pct": float(d.get("loss_pct", 0.0)) if broken else 0.0,
            "rtt_ms": int(d.get("rtt_ms", 0)) if broken and d.get("rtt_ms") else 31,
            "peers_reachable": not broken,
            "change_window": d.get("change_window"),
        }
    lines = [
        f"$ asteria estate netpath --site {p.site}",
        f"  vpn tunnel   {'DOWN' if not metrics['tunnel_up'] else 'up (ike established)'}",
        f"  dns          {'SERVFAIL on ingest.asteria.io' if not metrics['dns_ok'] else 'ok'}",
        f"  egress 443   loss {metrics['loss_pct']}%  rtt {metrics['rtt_ms']}ms",
        f"  local segment  {'unreachable from bastion' if broken else 'all hubs answer arp'}",
    ]
    if metrics["change_window"]:
        lines.append(f"  customer change window: {metrics['change_window']}")
    return ToolResult(
        "net.path_check",
        p.site,
        "site path broken" if broken else "site path healthy end to end",
        metrics,
        lines,
    )


def ssh_databox(p: Probe) -> ToolResult:
    """The site aggregator. Where data goes to sit when it is not going anywhere.

    A hub can be perfectly healthy, sending perfectly good data, into a box that
    has stopped shipping it. From the cloud that looks identical to a dead hub —
    which is the entire reason this step exists in the procedure.
    """
    box = p.live("site", "data_box")
    if box:
        metrics = {
            "collector_active": bool(box.get("collector_active")),
            # A real integral, not a plausible-looking number: frames per hub
            # per minute, accumulating since the collector stopped.
            "queue_depth": int(box.get("queue_depth", 0)),
            "disk_used_pct": int(box.get("disk_used_pct", 41)),
            "cert_days_remaining": int(box.get("cert_days_remaining", 121)),
            "hub_reporting_in": not box.get("healthy"),
        }
        broken = not box.get("healthy")
    else:
        broken = p.situation.cause == estate.DATA_BOX_BACKLOG
        d = p.situation.detail if broken else {}
        metrics = {
            "collector_active": bool(d.get("collector_active", True)) if broken else True,
            "queue_depth": int(d.get("queue_depth", 0)) if broken else 3,
            "disk_used_pct": int(d.get("disk_used_pct", 41)) if broken else 41,
            "cert_days_remaining": int(d.get("cert_days_remaining", 121)) if broken else 121,
            "hub_reporting_in": broken,
        }
    active = metrics["collector_active"]
    lines = [
        f"$ ssh -J bastion.asteria.internal ops@{p.databox}",
        f"PulseOne DataBox  {p.site}  agent 2.4.1",
        "ops@databox:~$ systemctl is-active pulseone-collector",
        f"{'active' if active else 'failed'}",
        "ops@databox:~$ pulseone-cli queue --stats",
        f"  pending     {metrics['queue_depth']}",
        f"  oldest      {p.episode.opened_at:%Y-%m-%d %H:%M}"
        if broken
        else "  oldest      00:00:04 ago",
        f"  last upload {'never since ' + f'{p.episode.opened_at:%H:%M}' if broken else 'ok (4s ago)'}",
        "ops@databox:~$ df -h /var/lib/pulseone | tail -1",
        f"/dev/sda2  200G  {metrics['disk_used_pct']}% /var/lib/pulseone",
        "ops@databox:~$ pulseone-cli cert --check",
        f"  client cert expires in {metrics['cert_days_remaining']} days"
        + ("  ** EXPIRED **" if metrics["cert_days_remaining"] < 0 else ""),
    ]
    if broken:
        lines.append(f"ops@databox:~$ grep {p.hub_id} /var/log/pulseone/ingest.log | tail -1")
        lines.append(
            f"  {p.episode.opened_at:%H:%M:%S} accepted frame from {p.hub_id} — buffered, not shipped"
        )
    return ToolResult(
        "ssh.databox",
        (p.live("site", "data_box") or {}).get("host") or p.databox,
        "data box holding data it cannot ship" if broken else "data box healthy and current",
        metrics,
        lines,
    )


def ssh_hub(p: Probe) -> ToolResult:
    """The unit itself: service health, self-test, and the radio's own margin.

    Feeds two steps. T6 reads the service and POST lines; T7 reads the link
    margin. One session, because that is how an engineer does it.
    """
    device = p.live("hub", "device")
    link = p.live("hub", "link")
    if device:
        reachable = bool(device.get("reachable"))
        restarts = int(device.get("restarts_24h", 0))
        post = device.get("post_code")
        rssi = int(link.get("rssi_dbm", -61))
        faulty = bool(restarts or post)
        metrics = {
            "reachable": reachable,
            "restarts_24h": restarts,
            "post_code": post,
            "post_pass": post is None,
            "rssi_dbm": rssi,
            "wear_time_h": link.get("wear_time_h"),
            "patch_lot": link.get("patch_lot"),
            "sw_version": device.get("sw_version"),
            # Reported by the unit against what was shipped to it. No step of
            # OPS-SOP-004 rev 3.0 compares these, which is why an unreleased
            # build in the field walks straight through the whole tree — the
            # evidence is on the screen and the procedure never looks at it.
            "sw_version_inventory": device.get("sw_version_inventory"),
            "clock_skew_s": device.get("clock_skew_s", 0),
        }
        d = {"fault": "watchdog reset"}
        patchy = rssi <= p.thresholds["rssi_dbm"]
    else:
        cause = p.situation.cause
        d = p.situation.detail
        faulty = cause == estate.DEVICE_FAULT
        patchy = cause == estate.CONSUMABLE_PATCH
        reachable = cause not in (estate.POWER_LOSS, estate.SITE_NETWORK)
        restarts = int(d.get("restarts_24h", 0)) if faulty else 0
        post = d.get("post_code") if faulty else None
        rssi = int(d.get("rssi_dbm", -61)) if patchy else -61

        metrics = {
            "reachable": reachable,
            "restarts_24h": restarts,
            "post_code": post,
            "post_pass": post is None,
            "rssi_dbm": rssi,
            "wear_time_h": d.get("wear_time_h") if patchy else None,
            "patch_lot": d.get("patch_lot") if patchy else None,
            "sw_version": p.episode.primary.sw_version,
        }
    if not reachable:
        return ToolResult(
            "ssh.hub",
            p.host,
            "unit not reachable — consistent with the layer below it being down",
            metrics,
            [
                f"$ ssh -J bastion.asteria.internal ops@{p.host}",
                f"ssh: connect to host {p.host} port 22: No route to host",
                "  (the unit is not answering; this is a symptom, not a finding)",
            ],
        )

    lines = [
        f"$ ssh -J bastion.asteria.internal ops@{p.host}",
        (
            f"PulseOne Hub  {p.hub_id}  sw {metrics['sw_version']}"
            f"  hw {p.episode.primary.hw_revision}"
        ),
        "ops@hub:~$ uptime",
        (
            f"  up {'0 days, 00:04' if faulty and restarts else '18 days, 06:22'},"
            f" load 0.2{'9' if faulty else '1'}"
        ),
        "ops@hub:~$ systemctl show pulseone-agent -p NRestarts --value",
        f"  {restarts}",
        "ops@hub:~$ pulseone-selftest --post",
        f"  POST {'FAIL ' + str(post) if post else 'pass'}"
        + (f" — {d.get('fault')}" if faulty and post else ""),
        "ops@hub:~$ pulseone-cli link --stats",
        f"  rssi        {rssi} dBm",
        f"  pairing     {p.hub.pairing_status if p.hub else 'unknown'}",
    ]
    if patchy:
        lines.append(
            f"  wear time   {metrics['wear_time_h']}h"
            + (f"  lot {metrics['patch_lot']}" if metrics["patch_lot"] else "")
        )
    if faulty and restarts:
        lines += [
            "ops@hub:~$ journalctl -u pulseone-agent -n 3 --no-pager",
            f"  {p.episode.opened_at:%H:%M:%S} pulseone-agent[411]: {d.get('fault')}",
            "  watchdog: resetting service (restart loop)",
        ]
    return ToolResult(
        "ssh.hub",
        p.host,
        (
            f"agent restarted {restarts}x in 24h"
            if faulty and restarts
            else f"POST fail {post}"
            if post
            else f"link margin {rssi} dBm"
            if patchy
            else "unit healthy — nothing on the device explains it"
        ),
        metrics,
        lines,
    )


TOOLS = {
    "fleet.hub_status": hub_status,
    "fleet.heartbeat_gaps": heartbeat_gaps,
    "registers.context": registers_context,
    "ward.occupancy": ward_occupancy,
    "power.socket_check": socket_check,
    "net.path_check": path_check,
    "ssh.databox": ssh_databox,
    "ssh.hub": ssh_hub,
}


def _prior_incidents(p: Probe) -> list[Incident]:
    if p.session is None or not p.hub_id:
        return []
    since = (p.episode.opened_at - timedelta(days=30)).date()
    day = p.episode.opened_at.date()
    rows = p.session.execute(
        select(Incident)
        .where(
            Incident.hub_id == p.hub_id,
            Incident.reported_date.is_not(None),
            Incident.reported_date >= since,
            Incident.reported_date <= day,
        )
        .order_by(Incident.reported_date.desc())
    ).scalars()
    return list(rows)
