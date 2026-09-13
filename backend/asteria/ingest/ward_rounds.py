"""sources/ward-rounds/rounds.ndjson -> ward_round + round_bed.

Field-check nudge's source. `complete=false` with beds_walked < beds_planned is
the nudge itself: checks that were planned and never happened, which the
troubleshooting log has no row for.
"""

import json

from sqlalchemy.orm import Session

from asteria.config import settings
from asteria.ingest.common import as_date, as_dt, as_int, clean, record_snapshot
from asteria.models.sources import RoundBed, WardRound

ROUNDS_PATH = settings.mock_company_path / "sources" / "ward-rounds" / "rounds.ndjson"


def load_all(session: Session) -> int:
    n = 0
    with ROUNDS_PATH.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            round_id = r["round_id"]
            session.add(
                WardRound(
                    round_id=round_id,
                    round_date=as_date(r.get("date")),
                    customer_id=clean(r.get("customer_id")),
                    organisation_as_written=clean(r.get("organisation")),
                    ward_id=clean(r.get("ward_id")),
                    walked_by=clean(r.get("walked_by")),
                    started=as_dt(r.get("started")),
                    beds_planned=as_int(r.get("beds_planned")),
                    beds_walked=as_int(r.get("beds_walked")),
                    complete=r.get("complete"),
                    incomplete_reason=clean(r.get("incomplete_reason")),
                )
            )
            for b in r.get("beds", []):
                session.add(
                    RoundBed(
                        round_id=round_id,
                        bed_id=clean(b.get("bed_id")),
                        pairing_id=clean(b.get("pairing_id")),
                        serial_read=clean(b.get("serial_read")),
                        patch_lot_read=clean(b.get("patch_lot_read")),
                        observation=clean(b.get("observation")),
                        action=clean(b.get("action")),
                        walked=b.get("walked"),
                        check_id=clean(b.get("check_id")),
                    )
                )
            n += 1
    record_snapshot(session, ROUNDS_PATH, n)
    return n
