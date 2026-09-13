"""The loop that closes on screen.

    events land -> outage watch drafts the row -> triage runs the procedure ->
    the diagnosis and the drafted troubleshooting row appear, with the
    transcripts behind them (TRIAGE.md §6)

One cycle: poll the fleet service for telemetry we have not seen, write it to
`telemetry_event`, reduce the new arrivals to episodes, draft, triage, score.
Nothing here commits a register row. Capture is autonomy level 3 at any speed,
and a queue that fills faster is still a queue.

Two things worth being precise about:

    **Scope.** A cycle only reduces events that arrived since the loop started.
    The frozen twenty months are already drafted, and re-reducing 35,000 rows
    every few seconds to reach the same answer is not a live system, it is a
    busy one.

    **Scoring.** The hidden causes come from `/v1/sim/scenarios`, and they are
    read *here*, after every triage in the cycle has already reached its
    outcome — never by the bot and never by a tool. If the answer key were
    available while the paper was being sat, the score would measure nothing.
"""

from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from asteria.capture.field_triage import FieldTriage
from asteria.capture.outage_watch import OutageWatch
from asteria.db import SessionLocal
from asteria.fleet.client import FleetClient
from asteria.ingest.common import as_dt
from asteria.models.sources import TelemetryEvent

POLL_SECONDS = 5.0


@dataclass
class Cycle:
    """What one turn of the loop did. The line the terminal prints."""

    at: datetime
    events_ingested: int = 0
    duplicates_dropped: int = 0
    episodes: int = 0
    rows_drafted: int = 0
    questions: int = 0
    completions: int = 0
    diagnoses: Counter = field(default_factory=Counter)
    correct: int = 0
    scored: int = 0
    off_taxonomy: int = 0

    def line(self) -> str:
        if not self.events_ingested and not self.episodes:
            return f"{self.at:%H:%M:%S}  quiet"
        causes = ", ".join(f"{k} x{v}" for k, v in self.diagnoses.most_common())
        score = f"{self.correct}/{self.scored} matched" if self.scored else "unscored"
        gaps = f", {self.off_taxonomy} outside the procedure" if self.off_taxonomy else ""
        return (
            f"{self.at:%H:%M:%S}  +{self.events_ingested} events"
            f" ({self.duplicates_dropped} replays dropped), {self.episodes} episodes,"
            f" {self.rows_drafted} rows + {self.questions} questions drafted"
            f" — {causes or 'no diagnosis'} [{score}{gaps}]"
        )


class LiveLoop:
    """Asteria, consuming a fleet it does not own."""

    def __init__(
        self,
        fleet: FleetClient | None = None,
        *,
        session_factory=SessionLocal,
        since: datetime | None = None,
    ) -> None:
        self.fleet = fleet or FleetClient()
        self.session_factory = session_factory
        self.cursor = 0
        # Everything before this instant is history somebody has already worked.
        self.started_at = since or datetime.now(UTC)

    # -- ingest ------------------------------------------------------------

    def ingest(self, session: Session) -> tuple[int, int]:
        """Pull what we have not seen and write it down.

        Idempotent on `event_id`, and the count of what was already there is
        reported rather than swallowed: a replayed buffer counted five times is
        a fabricated signal, and a loop that silently absorbs replays cannot
        show that it did not.
        """
        events, cursor = self.fleet.events_since(self.cursor)
        if not events:
            return 0, 0
        self.cursor = cursor

        known = {
            event_id
            for (event_id,) in session.execute(
                select(TelemetryEvent.event_id).where(
                    TelemetryEvent.event_id.in_([e["event_id"] for e in events])
                )
            )
        }
        written = 0
        for e in events:
            if e["event_id"] in known:
                continue
            session.add(
                TelemetryEvent(
                    event_id=e["event_id"],
                    hub_id=e.get("hub_id"),
                    serial=e.get("serial"),
                    customer_id=e.get("customer_id"),
                    ward_id=e.get("ward_id"),
                    bed_id=e.get("bed_id"),
                    ts_device=as_dt(e.get("ts_device")),
                    ts_received=as_dt(e.get("ts_received")),
                    code=e.get("code"),
                    severity=e.get("severity"),
                    sw_version=e.get("sw_version"),
                    hw_revision=e.get("hw_revision"),
                    source=e.get("source"),
                    dedupe_key=e.get("dedupe_key"),
                    payload=e.get("payload"),
                )
            )
            written += 1
        session.flush()
        return written, len(events) - written

    # -- one cycle ---------------------------------------------------------

    def cycle(self) -> Cycle:
        turn = Cycle(at=datetime.now(UTC))
        with self.session_factory() as session:
            turn.events_ingested, turn.duplicates_dropped = self.ingest(session)
            if not turn.events_ingested:
                session.commit()
                return turn

            watch = OutageWatch(session, since=self.started_at).run().summary()
            turn.rows_drafted = watch["new_rows"]
            turn.questions = watch["questions"]
            turn.completions = watch["completions"]

            bot = FieldTriage(session, since=self.started_at, fleet=self.fleet)
            output = bot.run()
            turn.episodes = output.episodes_seen
            for result in bot.runs.values():
                turn.diagnoses[result.outcome.key] += 1

            self._score(bot, turn)
            session.commit()
        return turn

    def _score(self, bot: FieldTriage, turn: Cycle) -> None:
        """Mark the paper, now that every answer is written.

        `actual_cause` is set on the result *after* the outcome is fixed. The
        runner's docstring promises this and this is the only place that does
        it, so the promise is checkable by reading one function.
        """
        answer_key = self.fleet.scenarios()
        if not answer_key:
            return
        by_hub: dict[str, dict] = {}
        for scenario in [*answer_key.get("active", []), *answer_key.get("completed", [])]:
            for hub_id in scenario["hub_ids"]:
                by_hub[hub_id] = scenario

        for result in bot.runs.values():
            scenario = by_hub.get(result.episode.hub_id)
            if scenario is None:
                continue
            result.actual_cause = scenario["cause"]
            turn.scored += 1
            turn.correct += int(result.correct)
            turn.off_taxonomy += int(result.off_taxonomy)

    # -- the loop ----------------------------------------------------------

    def run(self, *, cycles: int | None = None, interval: float = POLL_SECONDS) -> list[Cycle]:
        turns: list[Cycle] = []
        n = 0
        while cycles is None or n < cycles:
            turn = self.cycle()
            turns.append(turn)
            print(turn.line(), flush=True)
            n += 1
            if cycles is None or n < cycles:
                time.sleep(interval)
        return turns


def main() -> None:
    fleet = FleetClient()
    if not fleet.available:
        raise SystemExit(
            f"No fleet service at {fleet.base_url}. Start it with `make fleet`, "
            "or run `make capture` to work the frozen twenty months instead."
        )
    print(f"watching {fleet.base_url} — nothing is committed, at any speed\n")
    LiveLoop(fleet).run()


if __name__ == "__main__":
    main()
