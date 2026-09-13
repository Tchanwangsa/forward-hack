"""Take the simulated fleet back out of the database.

The live loop writes real rows to real tables — that is the point of it, and it
is what makes the queue fill on screen. But those rows are *simulated*, the
frozen twenty months of register history are not, and the two must not be left
mixed: a rate computed across both is meaningless, and the test suite reads the
same database.

Everything the simulator produced is identifiable by one prefix. `EVT-SIM-` on
the event, `tel:EVT-SIM-` on every artifact drafted from it. Nothing the
simulator made lacks it, and nothing real carries it — which is the only reason
a clean removal is possible at all.

    make reset-live
"""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from asteria.db import SessionLocal
from asteria.models.capture import CaptureDraft, CompletionSuggestion, DraftField
from asteria.models.sources import TelemetryEvent
from asteria.models.triage import TriageRun, TriageStep

SIM_EVENT_PREFIX = "EVT-SIM-"
SIM_ARTIFACT_PREFIX = "tel:EVT-SIM-"


def reset(session: Session) -> dict[str, int]:
    """Delete every simulated row. Children first, so no foreign key complains."""
    counts: dict[str, int] = {}

    draft_ids = list(
        session.execute(
            select(CaptureDraft.id).where(CaptureDraft.artifact_ref.like(f"{SIM_ARTIFACT_PREFIX}%"))
        ).scalars()
    )
    run_ids = list(
        session.execute(
            select(TriageRun.id).where(TriageRun.artifact_ref.like(f"{SIM_ARTIFACT_PREFIX}%"))
        ).scalars()
    )

    if draft_ids:
        counts["draft_field"] = _delete(
            session, delete(DraftField).where(DraftField.draft_id.in_(draft_ids))
        )
    if run_ids:
        counts["triage_step"] = _delete(
            session, delete(TriageStep).where(TriageStep.run_id.in_(run_ids))
        )
    counts["capture_draft"] = _delete(
        session,
        delete(CaptureDraft).where(CaptureDraft.artifact_ref.like(f"{SIM_ARTIFACT_PREFIX}%")),
    )
    counts["completion_suggestion"] = _delete(
        session,
        delete(CompletionSuggestion).where(
            CompletionSuggestion.artifact_ref.like(f"{SIM_ARTIFACT_PREFIX}%")
        ),
    )
    counts["triage_run"] = _delete(
        session, delete(TriageRun).where(TriageRun.artifact_ref.like(f"{SIM_ARTIFACT_PREFIX}%"))
    )
    counts["telemetry_event"] = _delete(
        session, delete(TelemetryEvent).where(TelemetryEvent.event_id.like(f"{SIM_EVENT_PREFIX}%"))
    )
    session.commit()
    return {k: v for k, v in counts.items() if v}


def _delete(session: Session, statement) -> int:
    return session.execute(statement).rowcount or 0


def main() -> None:
    with SessionLocal() as session:
        removed = reset(session)
    if not removed:
        print("nothing simulated in the database — it is already the frozen set")
        return
    for table, n in removed.items():
        print(f"  removed {n:>5} from {table}")


if __name__ == "__main__":
    main()
