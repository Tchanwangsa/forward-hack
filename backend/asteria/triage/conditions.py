"""One predicate per `when:` in OPS-SOP-004. The reading of the findings.

Split from the YAML deliberately. The procedure owns *what* is checked and at
what threshold — those are the document's numbers and change when it is
revised. This module owns *how a reading is read*, which is code, has edge cases
and gets tested.

Every predicate takes the findings accumulated so far (every metric every tool
has returned this run, merged) and the procedure's thresholds. None of them
guess: a metric that is absent is not a condition that is true.
"""

from __future__ import annotations

from collections.abc import Callable

Findings = dict
Predicate = Callable[[Findings, dict], bool]

CONDITIONS: dict[str, Predicate] = {}


def condition(name: str) -> Callable[[Predicate], Predicate]:
    def register(fn: Predicate) -> Predicate:
        CONDITIONS[name] = fn
        return fn

    return register


def evaluate(name: str, findings: Findings, thresholds: dict) -> bool:
    try:
        return bool(CONDITIONS[name](findings, thresholds))
    except KeyError:
        raise UnknownCondition(
            f"OPS-SOP-004 names a condition `{name}` with no predicate behind it"
        ) from None


# -- T1 scope --------------------------------------------------------------


@condition("site_wide")
def site_wide(f: Findings, t: dict) -> bool:
    """Three or more hubs at one site, or the platform's ward-wide flag with at
    least one other hub behind it.

    The flag is good evidence — `ward_wide` is raised cloud-side and is a fact
    the platform knows and the spreadsheet never records — but it is a claim
    about a site, and a claim about a site that no second unit joins is not
    corroborated. This branch skips the unit-level checks at §5.2 and §5.3, so
    a lone hub that trips it is a hub whose socket nobody ever looks at.
    """
    peers = f.get("peers_affected", 1)
    return peers >= t["site_wide_min_hubs"] or (bool(f.get("ward_wide_flag")) and peers > 1)


# -- T2 expected absence ---------------------------------------------------


@condition("unit_not_accruing")
def unit_not_accruing(f: Findings, t: dict) -> bool:
    return f.get("unit_accrues") is False


@condition("planned_works_notice")
def planned_works_notice(f: Findings, t: dict) -> bool:
    """Only a notice that covers *this unit*. A site-scope change window is
    corroboration for a site-wide event, not a reason to close one hub.
    """
    return bool(f.get("planned_works_covers_unit"))


@condition("discharged_bed")
def discharged_bed(f: Findings, t: dict) -> bool:
    """Empty bed *and* an orderly session close. An empty bed on its own is
    not enough — a hub that died mid-session and was unplugged afterwards
    presents the same way, and that one is an incident.
    """
    return f.get("bed_occupied_at_onset") is False and bool(f.get("session_closed_cleanly"))


# -- T3 power --------------------------------------------------------------


@condition("socket_dead")
def socket_dead(f: Findings, t: dict) -> bool:
    return f.get("socket_live") is False


@condition("battery_exhausted_off_dock")
def battery_exhausted_off_dock(f: Findings, t: dict) -> bool:
    pct = f.get("battery_pct_at_silence")
    return pct is not None and pct <= 2 and f.get("on_dock") is False


# -- T4 site network -------------------------------------------------------


@condition("tunnel_down")
def tunnel_down(f: Findings, t: dict) -> bool:
    return f.get("tunnel_up") is False or f.get("dns_ok") is False


@condition("path_degraded")
def path_degraded(f: Findings, t: dict) -> bool:
    return f.get("loss_pct", 0) >= t["packet_loss_pct"] or f.get("rtt_ms", 0) >= t["rtt_ms"]


# -- T5 data box -----------------------------------------------------------


@condition("collector_not_running")
def collector_not_running(f: Findings, t: dict) -> bool:
    return f.get("collector_active") is False


@condition("upload_backlog")
def upload_backlog(f: Findings, t: dict) -> bool:
    return f.get("queue_depth", 0) >= t["upload_queue_depth"]


@condition("disk_pressure")
def disk_pressure(f: Findings, t: dict) -> bool:
    return f.get("disk_used_pct", 0) >= t["disk_used_pct"]


@condition("certificate_expired")
def certificate_expired(f: Findings, t: dict) -> bool:
    days = f.get("cert_days_remaining")
    return days is not None and days < 0


# -- T6 device -------------------------------------------------------------


@condition("service_crash_loop")
def service_crash_loop(f: Findings, t: dict) -> bool:
    return f.get("restarts_24h", 0) >= t["service_restarts_24h"]


@condition("post_fault")
def post_fault(f: Findings, t: dict) -> bool:
    return f.get("post_pass") is False


# -- T7 patch link ---------------------------------------------------------


@condition("link_margin_poor")
def link_margin_poor(f: Findings, t: dict) -> bool:
    """A weak link is the last thing checked, not the first.

    Everything below it in the stack can produce the same reading, which is why
    the procedure puts it after power, path, box and device — and why its
    outcome is asked rather than asserted.
    """
    rssi = f.get("rssi_dbm")
    return rssi is not None and rssi <= t["rssi_dbm"] and f.get("reachable") is not False


class UnknownCondition(KeyError):
    """The procedure names a branch this code cannot evaluate."""
