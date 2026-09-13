"""sources/service/*.csv -> work_order, technician_note, part_replaced.

RMA capture's source. The work order carries the customer's verbatim fault; the
technician notes carry the actual finding; parts-replaced is the hardest evidence
of all — a comms module swapped is better proof of CONN-LINK-LOSS than any prose.
"""

import csv

from sqlalchemy.orm import Session

from asteria.config import settings
from asteria.ingest.common import as_date, as_dt, as_int, clean, record_snapshot
from asteria.models.sources import PartReplaced, TechnicianNote, WorkOrder

SERVICE_DIR = settings.mock_company_path / "sources" / "service"


def _rows(path):
    with path.open(newline="") as fh:
        yield from csv.DictReader(fh)


def load_all(session: Session) -> int:
    wo_path = SERVICE_DIR / "work-orders.csv"
    n = 0
    for r in _rows(wo_path):
        session.add(
            WorkOrder(
                work_order_id=clean(r["work_order_id"]),
                rma_number=clean(r["rma_number"]),
                raised_date=as_date(r["raised_date"]),
                serial_as_written=clean(r["serial_as_written"]),
                organisation_as_written=clean(r["organisation_as_written"]),
                reported_fault_verbatim=clean(r["reported_fault_verbatim"]),
                received_date=as_date(r["received_date"]),
                technician=clean(r["technician"]),
                closed_date=as_date(r["closed_date"]),
                disposition=clean(r["disposition"]),
            )
        )
        n += 1
    record_snapshot(session, wo_path, n)

    for r in _rows(SERVICE_DIR / "technician-notes.csv"):
        session.add(
            TechnicianNote(
                note_id=clean(r["note_id"]),
                work_order_id=clean(r["work_order_id"]),
                ts=as_dt(r["ts"]),
                technician=clean(r["technician"]),
                note=clean(r["note"]),
            )
        )

    for r in _rows(SERVICE_DIR / "parts-replaced.csv"):
        session.add(
            PartReplaced(
                line_id=clean(r["line_id"]),
                work_order_id=clean(r["work_order_id"]),
                part_number=clean(r["part_number"]),
                part_description=clean(r["part_description"]),
                qty=as_int(r["qty"]),
            )
        )

    return n
