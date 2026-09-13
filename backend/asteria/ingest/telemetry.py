"""sources/telemetry/*.ndjson -> telemetry_event, telemetry_heartbeat.

Outage watch's primary source. `code` IS an indicator code; `sw_version` is what
the hub reported at the moment of the fault. See plan/TELEMETRY-API.md.
"""

import json

from sqlalchemy.orm import Session

from asteria.config import settings
from asteria.ingest.common import as_dt, clean, record_snapshot
from asteria.models.sources import TelemetryEvent, TelemetryHeartbeat

TELEMETRY_DIR = settings.mock_company_path / "sources" / "telemetry"


def _ndjson(path):
    with path.open() as fh:
        for line in fh:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_events(session: Session) -> int:
    path = TELEMETRY_DIR / "events.ndjson"
    n = 0
    for e in _ndjson(path):
        session.add(
            TelemetryEvent(
                event_id=e["event_id"],
                hub_id=clean(e.get("hub_id")),
                serial=clean(e.get("serial")),
                customer_id=clean(e.get("customer_id")),
                ward_id=clean(e.get("ward_id")),
                bed_id=clean(e.get("bed_id")),
                ts_device=as_dt(e.get("ts_device")),
                ts_received=as_dt(e.get("ts_received")),
                code=clean(e.get("code")),
                severity=clean(e.get("severity")),
                sw_version=clean(e.get("sw_version")),
                hw_revision=clean(e.get("hw_revision")),
                source=clean(e.get("source")),
                dedupe_key=clean(e.get("dedupe_key")),
                payload=e.get("payload"),
            )
        )
        n += 1
    record_snapshot(session, path, n)
    return n


def load_heartbeats(session: Session) -> int:
    """Heartbeats turn the inventory's stale SW version into a timeline, and
    their absence is how a hub going quiet is detected.
    """
    path = TELEMETRY_DIR / "heartbeats.ndjson"
    n = 0
    for e in _ndjson(path):
        session.add(
            TelemetryHeartbeat(
                event_id=e["event_id"],
                hub_id=clean(e.get("hub_id")),
                ts_device=as_dt(e.get("ts_device")),
                ts_received=as_dt(e.get("ts_received")),
                code=clean(e.get("code")),
                sw_version=clean(e.get("sw_version")),
                source=clean(e.get("source")),
                payload=e.get("payload"),
            )
        )
        n += 1
    record_snapshot(session, path, n)
    return n


def load_all(session: Session) -> None:
    load_events(session)
    load_heartbeats(session)
