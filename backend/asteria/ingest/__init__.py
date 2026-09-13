"""mock-company/ -> Postgres. Run once before anything else: `make ingest`.

    registers.py    the 7 human .xlsx registers, as versioned snapshots
    telemetry.py    sources/telemetry/{events,heartbeats}.ndjson
    mail.py         sources/mail/THREADS.json + the message bodies
    meetings.py     sources/meetings/ transcripts + attendees.json
    service.py      sources/service/ work orders
    ward_rounds.py  sources/ward-rounds/rounds.ndjson
    ground_truth.py mock-company/ground-truth/ — scoring only. Never readable
                    by a capture bot; that would be cheating the scorecard.
"""


def main() -> None:
    """`python -m asteria.ingest` — full load, in dependency order."""
    raise NotImplementedError


if __name__ == "__main__":
    main()
