"""Run the capture tier: `python -m asteria.capture` (or `make capture`).

Drafts only. The queue is where it stops, every time — nothing in here can
commit a register row, whatever it is run with.
"""

import json

from asteria.capture.outage_watch import OutageWatch
from asteria.capture.scorecard import baseline, coverage
from asteria.db import SessionLocal


def main() -> None:
    with SessionLocal() as session:
        print(baseline(session), "\n")

        summary = OutageWatch(session).run().summary()
        print("outage-watch:", json.dumps(summary))

        now = coverage(session)
        projected = coverage(session, projected=True)
        print(
            f"\ncoverage {now['pct_after']}% accepted "
            f"(projected {projected['pct_after']}% if the queue is worked as drafted) — "
            f"{projected['rows_recovered']} rows recovered, "
            f"{projected['codes_corrected']} codes corrected."
        )
        print("Nothing is committed until a human accepts it.")


if __name__ == "__main__":
    main()
