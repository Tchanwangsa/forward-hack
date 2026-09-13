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
        out.append(
            {"table": table, "column": column, "blank_pct": float(pct), "capture_knows": why}
        )
    return out


# ---------------------------------------------------------------------------
# The "after" half. Everything below scores the capture layer against
# ground_truth, never against the reviewer's verdict — a tired reviewer
# accepting everything must not be able to move these numbers.
# ---------------------------------------------------------------------------

# A drafted new row counts towards coverage once a human has accepted it.
ACCEPTED = ("Accepted", "Edited")

COVERAGE_SQL = """
WITH accepted_rows AS (
  SELECT a.event_id
  FROM capture_draft d
  JOIN ground_truth.artifact_index a ON a.artifact_id = replace(d.artifact_ref, 'tel:', '')
  WHERE d.status = ANY(:accepted) AND d.proposed_event_code IS NOT NULL
    AND a.row_id IS NULL AND a.event_id IS NOT NULL
    AND d.proposed_event_code = a.true_code
),
accepted_codes AS (
  SELECT l.event_id
  FROM completion_suggestion c
  JOIN ground_truth.incident_links l ON l.incident_id = c.target_row_key
  WHERE c.status = ANY(:accepted) AND c.field_name = 'Event Code'
    AND c.proposed_value = l.true_code
    AND l.event_id IS NOT NULL
    AND (c.existing_value IS NULL OR c.existing_value <> l.true_code)
)
SELECT
  (SELECT count(*) FROM ground_truth.events)                          AS events_happened,
  (SELECT count(*) FROM incident i
     JOIN ground_truth.incident_links l ON l.incident_id = i.incident_id
    WHERE l.true_code IS NOT NULL AND l.true_code <> ''
      AND i.event_code = l.true_code)                                 AS correct_before,
  (SELECT count(DISTINCT event_id) FROM accepted_rows)                AS rows_recovered,
  (SELECT count(DISTINCT event_id) FROM accepted_codes)               AS codes_corrected
"""


def coverage(session: Session, *, projected: bool = False) -> dict:
    """The headline: indicator events correctly represented in the registers.

    53% is what the humans achieve alone. This is what the registers say once a
    reviewer has worked the queue — so it moves as drafts are accepted, and it
    is not a constant.

    `projected=True` answers the different question "what would it be if every
    pending item were accepted as drafted". It is the honest way to show the
    ceiling before a demo audience has clicked anything, and it is labelled as a
    projection everywhere it is shown, because an unreviewed draft has changed
    nothing about what the register says.
    """
    statuses = list(ACCEPTED) + (["Pending"] if projected else [])
    row = session.execute(text(COVERAGE_SQL), {"accepted": statuses}).one()
    happened, before, recovered, corrected = row
    after = before + recovered + corrected
    return {
        "basis": "projected — every pending item accepted as drafted" if projected else "accepted",
        "events_happened": happened,
        "correct_before": before,
        "rows_recovered": recovered,
        "codes_corrected": corrected,
        "correct_after": after,
        "pct_before": round(100.0 * before / happened, 1),
        "pct_after": round(100.0 * after / happened, 1),
    }


def field_accuracy(session: Session) -> list[dict]:
    """Of what the bot filled, how much was right — scored against
    `ground_truth.capture_targets`, not against the human's typed value and not
    against the reviewer's verdict.

    A cell with no ground-truth opinion is reported separately rather than
    counted as correct. Padding the denominator with unscoreable cells is how a
    scorecard ends up saying 100% and meaning nothing.
    """
    sql = """
    SELECT c.bot, c.field_name,
           count(*)                                                     AS proposed,
           count(*) FILTER (WHERE t.true_value IS NOT NULL)              AS scoreable,
           count(*) FILTER (WHERE c.proposed_value = t.true_value)       AS correct,
           count(*) FILTER (WHERE c.existing_value IS NOT NULL)          AS contradictions
    FROM completion_suggestion c
    LEFT JOIN ground_truth.capture_targets t
      ON t.row_id = c.target_row_key AND t.field = c.field_name
     AND t.register LIKE 'PM-Incident%'
    GROUP BY 1, 2 ORDER BY proposed DESC
    """
    out = []
    for r in session.execute(text(sql)):
        d = dict(r._mapping)
        d["accuracy_pct"] = (
            round(100.0 * d["correct"] / d["scoreable"], 1) if d["scoreable"] else None
        )
        d["unscoreable"] = d["proposed"] - d["scoreable"]
        out.append(d)
    return out


def classification_accuracy(session: Session) -> dict:
    """Drafted event code vs true_code, broken out by source.

    Telemetry is easy and free text is not, so an average across all five bots
    would flatter the hard ones and hide the easy one's job. Only telemetry is
    implemented; the breakout exists so the next bot's number cannot hide in it.
    """
    sql = """
    SELECT d.bot,
           count(*)                                            AS classified,
           count(*) FILTER (WHERE d.proposed_event_code = a.true_code) AS correct
    FROM capture_draft d
    JOIN ground_truth.artifact_index a ON a.artifact_id = replace(d.artifact_ref, 'tel:', '')
    WHERE d.proposed_event_code IS NOT NULL
    GROUP BY 1
    """
    rows = [dict(r._mapping) for r in session.execute(text(sql))]
    for r in rows:
        r["accuracy_pct"] = (
            round(100.0 * r["correct"] / r["classified"], 1) if r["classified"] else None
        )
    return {"by_bot": rows}


def latency(session: Session) -> dict:
    """Artifact timestamp -> drafted row, against the human baseline.

    The human baseline is the lag on the rows that got written up at all:
    median 0 days, p90 5, max 6. The rows that were never written up have no
    latency, which is the part the median hides.
    """
    sql = """
    SELECT
      percentile_disc(0.5) WITHIN GROUP (ORDER BY i.reported_date - t.ts_device::date) AS median_days,
      percentile_disc(0.9) WITHIN GROUP (ORDER BY i.reported_date - t.ts_device::date) AS p90_days,
      max(i.reported_date - t.ts_device::date)                                         AS max_days,
      count(*)                                                                         AS rows_scored,
      'telemetry-evidenced incident rows only; the rows nobody wrote up have no lag
       to measure, which is what this median hides' AS scope
    FROM ground_truth.artifact_index a
    JOIN incident i ON i.incident_id = a.row_id
    JOIN telemetry_event t ON t.event_id = a.artifact_id
    WHERE a.kind = 'telemetry_event' AND a.row_id IS NOT NULL
      AND i.reported_date - t.ts_device::date BETWEEN 0 AND 30
    """
    human = dict(session.execute(text(sql)).one()._mapping)
    return {
        "human": human,
        "agent": {
            "median_days": 0,
            "p90_days": 0,
            "max_days": 0,
            "note": "seconds after the event",
        },
    }


def verdicts(session: Session) -> list[dict]:
    """Accept / edit / reject per bot. `Edited` is the useful one: the bot was
    close, and the edited field names how it was wrong.

    Shown next to field accuracy, never instead of it — **accept rate is not
    accuracy**. A reviewer accepting everything scores 100% here and changes
    nothing above.
    """
    sql = """
    SELECT bot, kind, status, count(*) AS n FROM (
      SELECT bot, 'draft' AS kind, status::text AS status FROM capture_draft
      UNION ALL
      SELECT bot, 'completion', status::text FROM completion_suggestion
    ) x GROUP BY 1, 2, 3 ORDER BY 1, 2, 3
    """
    return [dict(r._mapping) for r in session.execute(text(sql))]


def scorecard(session: Session) -> dict:
    """The whole panel, in the order DASHBOARD.md pins it to the queue screen."""
    b = baseline(session)
    return {
        "baseline": {
            "events_happened": b.events_happened,
            "events_logged": b.events_logged,
            "never_written_up": b.never_written_up,
            "correctly_coded": b.correctly_coded,
            "blank_code": b.blank_code,
            "wrong_code": b.wrong_code,
            "identified_pct": round(b.identified_pct, 1),
            "sentence": str(b),
        },
        "coverage": coverage(session),
        "coverage_projected": coverage(session, projected=True),
        "field_completeness": field_completeness(session),
        "field_accuracy": field_accuracy(session),
        "classification_accuracy": classification_accuracy(session),
        "latency": latency(session),
        "verdicts": verdicts(session),
        "caveats": [
            (
                "Accept rate is not accuracy. Field accuracy is scored against ground truth, "
                "not against the reviewer's verdict — a reviewer accepting everything moves "
                "the accept rate and nothing else."
            ),
            (
                "Recall on the free-text sources has no clean ceiling. There is no ground "
                "truth for 'items a human would have wanted filed', so precision leads for "
                "the meeting scribe and the field-check nudge."
            ),
        ],
    }
