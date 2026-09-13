"""mock-company/ -> Postgres. Run once before anything else: `make ingest`.

Order matters only for the reference tables, which everything else resolves
against. The rest is independent.

This is a full reload, not an incremental sync: it truncates and re-imports.
That is the right shape for a demo dataset and the wrong shape for a pilot —
in a pilot each import is a new snapshot and nothing is ever truncated.
"""

import sys

from sqlalchemy import text

from asteria.db import SessionLocal, engine
from asteria.ingest import ground_truth, mail, meetings, registers, service, telemetry, ward_rounds
from asteria.models import Base

# Reverse dependency order; CASCADE handles the rest.
def _truncate_all() -> None:
    tables = ", ".join(f'"{t}"' for t in Base.metadata.tables)
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


def main() -> None:
    print("truncating...", flush=True)
    _truncate_all()

    with SessionLocal() as session:
        print("registers  ...", end=" ", flush=True)
        registers.load_all(session)
        session.commit()
        print("ok")

        print("telemetry  ...", end=" ", flush=True)
        telemetry.load_all(session)
        session.commit()
        print("ok")

        print("mail       ...", end=" ", flush=True)
        n = mail.load_all(session)
        session.commit()
        print(f"ok ({n} messages)")

        print("meetings   ...", end=" ", flush=True)
        n = meetings.load_all(session)
        session.commit()
        print(f"ok ({n} transcripts)")

        print("service    ...", end=" ", flush=True)
        n = service.load_all(session)
        session.commit()
        print(f"ok ({n} work orders)")

        print("rounds     ...", end=" ", flush=True)
        n = ward_rounds.load_all(session)
        session.commit()
        print(f"ok ({n} rounds)")

    print("ground truth (separate schema) ...", end=" ", flush=True)
    counts = ground_truth.load_all()
    print(f"ok ({len(counts)} tables)")

    _summary()


def _summary() -> None:
    with engine.connect() as conn:
        print("\nloaded:")
        for t in sorted(Base.metadata.tables):
            n = conn.execute(text(f'SELECT count(*) FROM "{t}"')).scalar()
            if n:
                print(f"  {n:>6}  {t}")


if __name__ == "__main__":
    sys.exit(main())
