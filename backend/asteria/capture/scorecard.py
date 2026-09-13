"""The capture scorecard — the metric the product is judged on.

Reads the ground_truth schema. Capture bots do not, and must not: if a bot can
see the answers, none of these numbers mean anything.

`baseline()` is the "before" half of the demo, computed from the database rather
than quoted from a slide. `coverage()` is the "after" half, and moves as the
capture tier accepts drafts.
"""

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class Baseline:
    """What the human register achieves on its own, before any capture runs."""

    events_happened: int
    events_logged: int
    correctly_coded: int
    blank_code: int
    wrong_code: int

    @property
    def never_written_up(self) -> int:
        return self.events_happened - self.events_logged

    @property
    def identified_pct(self) -> float:
        """The 53%. The number the product attacks."""
        return 100.0 * self.correctly_coded / self.events_happened

    def __str__(self) -> str:
        return (
            f"{self.events_happened} indicator events happened, "
            f"{self.events_logged} reached the incident log "
            f"({self.never_written_up} never written up at all), "
            f"and {self.correctly_coded} of those carry a correct event code. "
            f"The register correctly identifies {self.identified_pct:.0f}% of what happened."
        )


BASELINE_SQL = """
SELECT
  (SELECT count(*) FROM ground_truth.events)                                AS events_happened,
  count(*)                                                                  AS events_logged,
  count(*) FILTER (WHERE i.event_code = l.true_code)                        AS correctly_coded,
  count(*) FILTER (WHERE i.event_code IS NULL)                              AS blank_code,
  count(*) FILTER (WHERE i.event_code IS NOT NULL
                     AND i.event_code <> l.true_code)                       AS wrong_code
FROM incident i
JOIN ground_truth.incident_links l ON l.incident_id = i.incident_id
WHERE l.true_code IS NOT NULL AND l.true_code <> ''
"""


def baseline(session: Session) -> Baseline:
    row = session.execute(text(BASELINE_SQL)).one()
    return Baseline(*row)


def field_completeness(session: Session) -> list[dict]:
    """Per-column blank rates on the rows that do exist — the second half of the
    gap table in ARCHITECTURE.md. Each of these is a completion suggestion
    waiting to be made, and most are a join rather than a transcription.
    """
    columns = [
        ("incident", "sw_version_at_time", "the telemetry event carries it"),
        ("incident", "event_code", "telemetry codes ARE indicator codes"),
        ("incident", "serial_number_as_written", "resolvable from pairing ID, ward and bed"),
        ("product_return", "sw_version", "hub inventory as at the RMA date"),
        ("data_check", "patch_lot", "lot allocation for that ward in that window"),
        ("data_check", "action_taken", "often stated in the ward round it came from"),
        ("communication", "contact_role", "in the email signature block"),
    ]
    out = []
    for table, column, why in columns:
        pct = session.execute(
            text(
                f"SELECT round(100.0 * count(*) FILTER (WHERE {column} IS NULL) / count(*), 0) "
                f"FROM {table}"
            )
        ).scalar()
        out.append({"table": table, "column": column, "blank_pct": float(pct), "capture_knows": why})
    return out


def coverage(session: Session) -> dict:
    """The "after" number. Moves as drafts are accepted — it is not a constant.

    TODO: once outage watch runs, count accepted drafts and accepted completions
    against ground_truth.capture_targets and report the same three figures.
    """
    raise NotImplementedError("implement alongside outage watch")
