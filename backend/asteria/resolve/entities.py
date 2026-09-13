"""Which hub, which organisation, which lot, which ward.

The resolutions tier 1 depends on:
    pairing ID + ward + bed        -> serial number   (11% blank on incidents)
    hub inventory as at a date     -> SW version      (48% blank on RMAs)
    lot allocation for a ward+window -> patch lot     (51% blank on checks)
    email domain / signature block -> organisation, contact role

Organisation names arrive in variants — see ground-truth/organisation-variants.csv
for how many, but resolve them from the reference register, not from that file.

Nothing here guesses. Every function returns None when the join does not land,
and a None here becomes a blank on a drafted row (capture rule 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from asteria.models.enums import ACCRUING_STATUSES
from asteria.models.reference import CustomerOrganisation, Hub
from asteria.models.sources import TelemetryHeartbeat


@dataclass(frozen=True)
class HubFacts:
    """The inventory's view of one hub. Everything a telemetry event cannot say."""

    hub_id: str
    serial_number: str | None
    customer_id: str | None
    organisation: str | None
    ward_id: str | None
    bed_id: str | None
    pairing_id: str | None
    pairing_status: str | None
    hw_revision: str | None
    unit_status: str | None

    @property
    def accrues(self) -> bool:
        """Whether this unit is in the denominator — and so whether an event
        from it may enter a numerator. A Spare in a cupboard reporting itself
        offline is a true event about a box, not an incident on a ward.
        """
        return self.unit_status in ACCRUING_STATUSES


class Resolver:
    """Reference lookups, cached for the length of one capture run.

    A run touches the same 250 hubs a few hundred times; the inventory is small
    and static within a run, so it is loaded once rather than joined per event.
    """

    def __init__(self, session: Session) -> None:
        self.session = session
        self._hubs: dict[str, HubFacts] = {}
        self._serial_to_hub: dict[str, str] = {}
        self._sw_cache: dict[tuple[str, date], str | None] = {}
        self._load_hubs()

    def _load_hubs(self) -> None:
        orgs = {
            o.customer_id: o.organisation_name
            for o in self.session.execute(select(CustomerOrganisation)).scalars()
        }
        for h in self.session.execute(select(Hub)).scalars():
            facts = HubFacts(
                hub_id=h.hub_id,
                serial_number=h.serial_number,
                customer_id=h.customer_id,
                organisation=orgs.get(h.customer_id),
                ward_id=h.ward_id,
                bed_id=h.bed_id,
                pairing_id=h.pairing_id,
                pairing_status=h.pairing_status,
                hw_revision=h.hw_revision,
                unit_status=h.unit_status,
            )
            self._hubs[h.hub_id] = facts
            if h.serial_number:
                self._serial_to_hub[normalise_serial(h.serial_number)] = h.hub_id

    def hub(self, hub_id: str | None) -> HubFacts | None:
        return self._hubs.get(hub_id) if hub_id else None

    def hub_by_serial(self, serial: str | None) -> HubFacts | None:
        """'SN 4216', 'P1100-4563', 'PO-P1-004226 ' all name one hub."""
        if not serial:
            return None
        hub_id = self._serial_to_hub.get(normalise_serial(serial))
        return self._hubs.get(hub_id) if hub_id else None

    def canonical_serial(self, hub_id: str | None) -> str | None:
        facts = self.hub(hub_id)
        return facts.serial_number if facts else None

    def sw_version_at(self, hub_id: str | None, when: date | datetime | None) -> str | None:
        """What this hub was running on that date, from the heartbeat timeline.

        The inventory's `SW Version (last observed)` is a last-observed value
        with a stale date — sometimes months stale, occasionally a year in the
        future because somebody typed the wrong year. The heartbeat stream turns
        that column into a timeline, and this is the only honest way to answer
        "what was it running when this happened".

        The last heartbeat at or before the date; None if the hub had not yet
        reported by then. Never the inventory column as a fallback — a stale
        value dressed up as a timeline answer is worse than a blank.
        """
        if not hub_id or when is None:
            return None
        day = when.date() if isinstance(when, datetime) else when
        key = (hub_id, day)
        if key not in self._sw_cache:
            self._sw_cache[key] = self.session.execute(
                select(TelemetryHeartbeat.sw_version)
                .where(
                    TelemetryHeartbeat.hub_id == hub_id,
                    TelemetryHeartbeat.ts_received <= _end_of_day(day),
                )
                .order_by(TelemetryHeartbeat.ts_received.desc())
                .limit(1)
            ).scalar()
        return self._sw_cache[key]

    def heartbeat_ref(self, hub_id: str, when: date | datetime) -> str:
        """Provenance for a version taken off the timeline: hb:HUB-04165@2025-01-09."""
        day = when.date() if isinstance(when, datetime) else when
        return f"hb:{hub_id}@{day.isoformat()}"


def normalise_serial(serial: str) -> str:
    """'SN 4216' -> '4216'. Comparison only — the as-written value is never rewritten."""
    s = serial.strip().upper().replace(" ", "")
    for prefix in ("PO-P1-", "P1100-", "SN", "PO-P1", "P1-"):
        if s.startswith(prefix):
            s = s[len(prefix) :]
            break
    return s.lstrip("-0") or "0"


def _end_of_day(day: date) -> datetime:
    from datetime import time

    return datetime.combine(day, time.max, tzinfo=UTC)
