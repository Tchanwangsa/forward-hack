"""Run the capture tier: `python -m asteria.capture` (or `make capture`).

Drafts only. The queue is where it stops, every time — nothing in here can
commit a register row, whatever it is run with.
"""

import json

from asteria.capture.field_triage import FieldTriage
from asteria.capture.outage_watch import OutageWatch
from asteria.capture.scorecard import baseline, coverage
from asteria.db import SessionLocal


def main() -> None:
    with SessionLocal() as session:
        print(baseline(session), "\n")

        summary = OutageWatch(session).run().summary()
        print("outage-watch:", json.dumps(summary))

        # Then why. Outage watch establishes the event; triage runs the ops
        # team's own procedure over it and writes the diagnosis where the ops
        # team writes it — the troubleshooting log.
        triage_bot = FieldTriage(session)
        triage_summary = triage_bot.run().summary()
        score = triage_bot.score()
        print("field-triage:", json.dumps({**triage_summary, **score}))
        print(
            f"  {score['correct']}/{score['diagnosed']} diagnoses match what was actually "
            f"wrong, {score['escalated']} escalated as inconclusive, "
            f"{score['closed_benign']} closed as not an incident — "
            f"{score['checks_run']} read-only checks, no device touched."
        )

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
