"""Screen 1 — capture queue. Ship this one if you ship one screen.

    GET  /api/capture/drafts            the queue: pending drafts + completions
    GET  /api/capture/drafts/{id}       the draft, its fields, and the raw artifact
    POST /api/capture/drafts/{id}/accept
    POST /api/capture/drafts/{id}/edit
    POST /api/capture/drafts/{id}/reject    rationale required
    GET  /api/capture/scorecard         coverage, field completeness, accept rate

Three kinds of item, reviewed differently (DASHBOARD.md §Screen 1): a new row, a
completion against a cell a human left blank, and a question the bot is not
confident enough to draft. The kind is derived from confidence rather than
stored, so lowering a bot's confidence can never quietly turn a question into an
assertion.

Nothing here commits without a named reviewer, and there is no bulk accept
across new rows. The friction is the feature.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pydantic import Field as PField
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from asteria.agent.action_log import log_action
from asteria.agent.autonomy import Autonomy
from asteria.capture import scorecard as sc
from asteria.capture.field_triage import FIELD_COLUMNS as DATA_CHECK_COLUMNS
from asteria.capture.field_triage import FieldTriage
from asteria.capture.outage_watch import FIELD_COLUMNS, OutageWatch
from asteria.db import get_session
from asteria.models.capture import CaptureDraft, CompletionSuggestion, ReviewVerdict
from asteria.models.capture_fed import DataCheck, Incident
from asteria.models.enums import DraftStatus, HumanVerdict, RowOrigin
from asteria.models.sources import TelemetryEvent
from asteria.models.triage import TriageRun

router = APIRouter()

SessionDep = Annotated[Session, Depends(get_session)]

# Below this, the bot is asking rather than asserting. ADHESIVE off the wire is
# the only thing that lands here today: a hub inferring a piece of tape came
# loose from a radio signal is a question for someone who can look at the ward.
QUESTION_THRESHOLD = Decimal("0.5")


@dataclass(frozen=True)
class Target:
    """Where an accepted draft lands. One entry per register a bot drafts into.

    The commit path is generic on purpose: a second bot drafting into a second
    register must not need a second copy of the accept/edit/reject machinery,
    because the machinery is where the gate lives.
    """

    model: type
    columns: dict[str, str]
    id_attr: str
    id_prefix: str


TARGETS = {
    "incident": Target(Incident, FIELD_COLUMNS, "incident_id", "INC"),
    "data_check": Target(DataCheck, DATA_CHECK_COLUMNS, "check_id", "CHK"),
}

_HUMAN_VERDICT = {
    DraftStatus.ACCEPTED: HumanVerdict.ACCEPTED,
    DraftStatus.EDITED: HumanVerdict.EDITED,
    DraftStatus.REJECTED: HumanVerdict.REJECTED,
}


class Verdict(BaseModel):
    reviewed_by: str = PField(min_length=1)
    rationale: str | None = None
    edits: dict[str, str] | None = None


def _kind(confidence: Decimal | None, has_code: bool) -> str:
    if confidence is not None and confidence < QUESTION_THRESHOLD:
        return "question"
    return "new_row" if has_code else "question"


@router.get("/drafts")
def list_drafts(
    session: SessionDep,
    bot: str | None = None,
    kind: str | None = Query(None, pattern="^(new_row|question|completion)$"),
    status: DraftStatus = DraftStatus.PENDING,
    limit: int = Query(50, le=500),
) -> dict:
    """The queue, grouped by bot — the reviewer for a drafted incident row is
    not the reviewer for a drafted comms row, and the edit rate that matters is
    per bot.
    """
    drafts = session.execute(
        select(CaptureDraft)
        .where(CaptureDraft.status == status, *([CaptureDraft.bot == bot] if bot else []))
        .order_by(CaptureDraft.id)
    ).scalars()
    items = [_draft_summary(d) for d in drafts]
    if kind in ("new_row", "question"):
        items = [i for i in items if i["kind"] == kind]

    completions: list[dict] = []
    if kind in (None, "completion"):
        rows = session.execute(
            select(CompletionSuggestion)
            .where(
                CompletionSuggestion.status == status,
                *([CompletionSuggestion.bot == bot] if bot else []),
            )
            .order_by(CompletionSuggestion.field_name, CompletionSuggestion.target_row_key)
        ).scalars()
        completions = [_completion_summary(c) for c in rows]

    return {
        "rail": _rail(session, status),
        "drafts": items[:limit] if kind != "completion" else [],
        "completions": completions[:limit],
        "counts": {"drafts": len(items), "completions": len(completions)},
    }


@router.get("/drafts/{draft_id}")
def get_draft(draft_id: int, session: SessionDep) -> dict:
    """The drafted row, field by field with what each field came from, and the
    artifact beside it — every event in the episode, not just the one that
    opened it. The artifact is never behind a click (DASHBOARD.md).
    """
    draft = session.get(CaptureDraft, draft_id)
    if draft is None:
        raise HTTPException(404, "no such draft")
    return {
        **_draft_summary(draft),
        "fields": [
            {
                "field": f.field_name,
                "proposed": f.proposed_value,
                "evidence": f.evidence,
                "confidence": float(f.confidence) if f.confidence is not None else None,
            }
            for f in draft.fields
        ],
        "blank_by_design": draft.payload.get("blank_by_design", {}),
        "artifact": _artifact(session, draft),
        # The procedure walk behind a diagnosis, where there is one. The checks
        # that found nothing are part of it — a reviewer judging a root cause is
        # judging what was ruled out (OPS-SOP-004 §3 C3).
        "triage": _triage(session, draft),
    }


@router.get("/completions/{completion_id}")
def get_completion(completion_id: int, session: SessionDep) -> dict:
    """The completion, the artifact behind it, and the human row as written.

    The artifact is never behind a click here either: a reviewer deciding
    `Event Code  blank -> ALERT-FALSE` is deciding about an event, and needs to
    see it. The row as written comes back so the cell being completed can be
    shown in its own row rather than as a value floating on its own.
    """
    completion = session.get(CompletionSuggestion, completion_id)
    if completion is None:
        raise HTTPException(404, "no such completion")
    ref = (completion.artifact_ref or "").removeprefix("tel:")
    return {
        **_completion_summary(completion),
        "artifact": _episode(session, [ref] if ref else []),
        "target_row": _row_as_written(session, completion),
    }


@router.post("/drafts/{draft_id}/accept")
def accept_draft(draft_id: int, verdict: Verdict, session: SessionDep) -> dict:
    """Commit the drafted row. The only place a capture row becomes a register row."""
    return _commit(session, draft_id, verdict, edits=None)


@router.post("/drafts/{draft_id}/edit")
def edit_draft(draft_id: int, verdict: Verdict, session: SessionDep) -> dict:
    """Accept with changes. Which field the human changed is the signal we want:
    it says the bot was close and names how it was wrong.
    """
    if not verdict.edits:
        raise HTTPException(422, "an edit with no edited fields is an accept")
    return _commit(session, draft_id, verdict, edits=verdict.edits)


@router.post("/drafts/{draft_id}/reject")
def reject_draft(draft_id: int, verdict: Verdict, session: SessionDep) -> dict:
    """A rejection is a permanent record with a named reviewer and a rationale.
    Never a deletion.
    """
    if not (verdict.rationale or "").strip():
        raise HTTPException(422, "a rejection needs a rationale")
    draft = _pending(session, draft_id)
    draft.status = DraftStatus.REJECTED
    session.add(
        ReviewVerdict(
            draft_id=draft.id,
            verdict=DraftStatus.REJECTED,
            reviewed_by=verdict.reviewed_by,
            rationale=verdict.rationale,
        )
    )
    log_action(
        session,
        tier=1,
        workflow=draft.bot,
        autonomy=Autonomy.DRAFT,
        inputs={"artifact_ref": draft.artifact_ref, "draft_id": draft.id},
        output={"committed": False},
        human_verdict=HumanVerdict.REJECTED,
        reviewed_by=verdict.reviewed_by,
        notes=verdict.rationale,
    )
    session.commit()
    return {"draft_id": draft.id, "status": draft.status, "committed_row": None}


@router.post("/completions/{completion_id}/accept")
def accept_completion(completion_id: int, verdict: Verdict, session: SessionDep) -> dict:
    """Accepting a completion does NOT touch the customer's row.

    The value is recorded here with its evidence and the analysis tier reads the
    completed view. The screen says so in plain words next to the button, or
    reviewers believe they are editing the spreadsheet (REGISTERS.md §6).
    """
    return _settle_completion(session, completion_id, verdict, DraftStatus.ACCEPTED)


@router.post("/completions/{completion_id}/edit")
def edit_completion(completion_id: int, verdict: Verdict, session: SessionDep) -> dict:
    """Accept a completion with a correction.

    The corrected value is the human's, and it is what the completed view reads.
    The customer's row is still not touched — this is the capture layer either
    way. `edits` carries {field_name: value} for the one field in play.
    """
    completion = session.get(CompletionSuggestion, completion_id)
    if completion is None:
        raise HTTPException(404, "no such completion")
    value = (verdict.edits or {}).get(completion.field_name)
    if value is None or value == completion.proposed_value:
        raise HTTPException(422, "an edit with no changed value is an accept")
    return _settle_completion(session, completion_id, verdict, DraftStatus.EDITED, value=value)


@router.post("/completions/{completion_id}/reject")
def reject_completion(completion_id: int, verdict: Verdict, session: SessionDep) -> dict:
    if not (verdict.rationale or "").strip():
        raise HTTPException(422, "a rejection needs a rationale")
    return _settle_completion(session, completion_id, verdict, DraftStatus.REJECTED)


@router.get("/scorecard")
def get_scorecard(session: SessionDep) -> dict:
    """The panel pinned across the top of the queue. Scored against ground
    truth, never against the verdict the reviewer is generating on this screen.
    """
    return sc.scorecard(session)


@router.post("/run/field-triage")
def run_field_triage(session: SessionDep) -> dict:
    """Run OPS-SOP-004 over the episodes in its scope. Read-only against the
    estate, drafts only against the register.
    """
    bot = FieldTriage(session)
    return {**bot.run().summary(), **bot.score()}


@router.post("/run/outage-watch")
def run_outage_watch(session: SessionDep) -> dict:
    """Run bot 1 over the telemetry stream. Idempotent — a re-run adds what is
    new and re-proposes nothing already reviewed. Drafts only, always.
    """
    return OutageWatch(session).run().summary()


# -- internals ------------------------------------------------------------


def _rail(session: Session, status: DraftStatus) -> list[dict]:
    """The left rail's per-bot counts."""
    drafts = session.execute(
        select(CaptureDraft.bot, CaptureDraft.confidence, func.count())
        .where(CaptureDraft.status == status)
        .group_by(CaptureDraft.bot, CaptureDraft.confidence)
    ).all()
    completions = dict(
        session.execute(
            select(CompletionSuggestion.bot, func.count())
            .where(CompletionSuggestion.status == status)
            .group_by(CompletionSuggestion.bot)
        ).all()
    )
    rail: dict[str, dict] = {}
    for bot, confidence, n in drafts:
        entry = rail.setdefault(bot, {"bot": bot, "new_rows": 0, "questions": 0, "completions": 0})
        key = (
            "questions"
            if confidence is not None and confidence < QUESTION_THRESHOLD
            else "new_rows"
        )
        entry[key] += n
    for bot, n in completions.items():
        rail.setdefault(bot, {"bot": bot, "new_rows": 0, "questions": 0, "completions": 0})
        rail[bot]["completions"] = n
    return list(rail.values())


def _draft_summary(draft: CaptureDraft) -> dict:
    return {
        "id": draft.id,
        "kind": _kind(draft.confidence, draft.proposed_event_code is not None),
        "bot": draft.bot,
        "target_register": draft.target_register,
        "artifact_ref": draft.artifact_ref,
        "event_code": draft.proposed_event_code,
        "confidence": float(draft.confidence) if draft.confidence is not None else None,
        "rationale": draft.rationale,
        "status": draft.status,
        "row": draft.payload.get("fields", {}),
        "events": draft.payload.get("events", []),
        "committed_row_id": draft.committed_row_id,
    }


def _completion_summary(c: CompletionSuggestion) -> dict:
    return {
        "id": c.id,
        "kind": "question"
        if c.confidence is not None and c.confidence < QUESTION_THRESHOLD
        else "completion",
        "bot": c.bot,
        "target_register": c.target_register,
        "row": c.target_row_key,
        "field": c.field_name,
        "existing": c.existing_value,
        "proposed": c.proposed_value,
        "contradiction": c.existing_value is not None,
        "artifact_ref": c.artifact_ref,
        "evidence": c.evidence,
        "confidence": float(c.confidence) if c.confidence is not None else None,
        "rationale": c.rationale,
        "accepted": c.accepted_value,
        "status": c.status,
        "writes_to_source_row": False,
    }


def _artifact(session: Session, draft: CaptureDraft) -> dict:
    """Whatever the bot read, rendered beside what it wrote.

    Where a burst was grouped into one episode, every event in the episode comes
    back — ten HUB-OFFLINE events at one site must arrive as one queue item
    showing ten events, not as ten items.
    """
    event_ids = draft.payload.get("events") or [draft.artifact_ref.removeprefix("tel:")]
    return _episode(session, event_ids)


def _episode(session: Session, event_ids: list[str]) -> dict:
    """The telemetry events themselves, oldest first, exactly as they arrived."""
    events = session.execute(
        select(TelemetryEvent).where(TelemetryEvent.event_id.in_(event_ids))
    ).scalars()
    return {
        "kind": "telemetry_episode",
        "events": [
            {
                "event_id": e.event_id,
                "hub_id": e.hub_id,
                "code": e.code,
                "severity": e.severity,
                "sw_version": e.sw_version,
                "ts_device": e.ts_device,
                "ts_received": e.ts_received,
                "payload": e.payload,
                "source": e.source,
            }
            for e in sorted(events, key=lambda e: e.ts_received or e.ts_device)
        ],
    }


def _triage(session: Session, draft: CaptureDraft) -> dict | None:
    """The triage run behind this draft, step by step, transcripts and all."""
    run = session.execute(
        select(TriageRun).where(TriageRun.artifact_ref == draft.artifact_ref)
    ).scalar_one_or_none()
    if run is None:
        return None
    return {
        "procedure": f"{run.procedure_id} rev {run.procedure_revision}",
        "verification": run.procedure_verification,
        "outcome": run.outcome,
        "label": run.outcome.replace("-", " "),
        "disposition": run.disposition,
        "citation": run.citation,
        "narrative": run.narrative,
        "escalate_to": run.escalate_to,
        "checks_run": run.checks_run,
        "confidence": float(run.confidence) if run.confidence is not None else None,
        "steps": [
            {
                "step_id": s.step_id,
                "section": s.section,
                "title": s.title,
                "question": s.question,
                "satisfied": s.satisfied,
                "outcome": s.outcome,
                "goto": s.goto,
                "note": s.note,
                "probes": s.probes or [],
            }
            for s in run.steps
        ],
    }


def _row_as_written(session: Session, completion: CompletionSuggestion) -> dict | None:
    """The customer's row, untouched, as the reviewer would see it in the
    workbook. Accepting a completion does not change any of this — the value
    lands in the capture layer and analysis reads the completed view.
    """
    row = session.execute(
        select(Incident).where(Incident.incident_id == completion.target_row_key)
    ).scalar_one_or_none()
    if row is None:
        return None
    columns = {**FIELD_COLUMNS, "Reported By": "reported_by", "Assigned To": "assigned_to"}
    return {
        "row_key": row.incident_id,
        "register": completion.target_register,
        "fields": {
            column: (str(v) if (v := getattr(row, attr, None)) is not None else None)
            for column, attr in columns.items()
        },
    }


def _pending(session: Session, draft_id: int) -> CaptureDraft:
    draft = session.get(CaptureDraft, draft_id)
    if draft is None:
        raise HTTPException(404, "no such draft")
    if draft.status != DraftStatus.PENDING:
        raise HTTPException(409, f"already {draft.status.lower()} — verdicts are not revisited")
    return draft


def _commit(session: Session, draft_id: int, verdict: Verdict, edits: dict | None) -> dict:
    draft = _pending(session, draft_id)
    target = TARGETS.get(draft.target_register)
    if target is None:
        raise HTTPException(422, f"no commit path for register {draft.target_register}")
    values = dict(draft.payload.get("fields", {}))
    values.update(edits or {})

    row = target.model(
        row_origin=RowOrigin.AGENT_EDITED if edits else RowOrigin.AGENT_ACCEPTED,
        captured_from=draft.artifact_ref,
        resolved_hub_id=values.get("HubID") or _hub_of(session, draft),
    )
    setattr(row, target.id_attr, _next_id(session, target))
    for column, value in values.items():
        attr = target.columns.get(column)
        if attr:
            setattr(row, attr, _coerce(attr, value))
    session.add(row)
    session.flush()
    incident = row  # the committed row, whichever register it landed in

    draft.status = DraftStatus.EDITED if edits else DraftStatus.ACCEPTED
    draft.committed_row_id = incident.id
    for field in draft.fields:
        field.accepted_value = (
            str(values.get(field.field_name))
            if field.field_name in values
            else field.proposed_value
        )

    session.add(
        ReviewVerdict(
            draft_id=draft.id,
            verdict=draft.status,
            reviewed_by=verdict.reviewed_by,
            rationale=verdict.rationale,
            edited_fields=sorted(edits) if edits else None,
        )
    )
    log_action(
        session,
        tier=1,
        workflow=draft.bot,
        autonomy=Autonomy.DRAFT,
        inputs={"artifact_ref": draft.artifact_ref, "draft_id": draft.id},
        output={
            "committed": True,
            "register": draft.target_register,
            "row_id": getattr(incident, target.id_attr),
            "edits": edits,
        },
        human_verdict=HumanVerdict.EDITED if edits else HumanVerdict.ACCEPTED,
        reviewed_by=verdict.reviewed_by,
        notes=verdict.rationale,
    )
    session.commit()
    return {
        "draft_id": draft.id,
        "status": draft.status,
        "committed_row": getattr(incident, target.id_attr),
    }


def _settle_completion(
    session: Session,
    completion_id: int,
    verdict: Verdict,
    status: DraftStatus,
    value: str | None = None,
) -> dict:
    completion = session.get(CompletionSuggestion, completion_id)
    if completion is None:
        raise HTTPException(404, "no such completion")
    if completion.status != DraftStatus.PENDING:
        raise HTTPException(409, f"already {completion.status.lower()}")
    completion.status = status
    if status in (DraftStatus.ACCEPTED, DraftStatus.EDITED):
        completion.accepted_value = value if value is not None else completion.proposed_value
    session.add(
        ReviewVerdict(
            completion_id=completion.id,
            verdict=status,
            reviewed_by=verdict.reviewed_by,
            rationale=verdict.rationale,
            edited_fields=[completion.field_name] if value is not None else None,
        )
    )
    log_action(
        session,
        tier=1,
        workflow=completion.bot,
        autonomy=Autonomy.DRAFT,
        inputs={
            "target_row": completion.target_row_key,
            "field": completion.field_name,
            "artifact_ref": completion.artifact_ref,
        },
        output={"value": completion.accepted_value, "source_row_edited": False},
        human_verdict=_HUMAN_VERDICT[status],
        reviewed_by=verdict.reviewed_by,
        notes=verdict.rationale,
    )
    session.commit()
    return {
        "completion_id": completion.id,
        "status": completion.status,
        "source_row_edited": False,
    }


def _next_id(session: Session, target: Target) -> str:
    """Next in sequence, allocated on accept rather than on draft — a rejected
    draft must not leave a hole in the customer's ID sequence.
    """
    column = getattr(target.model, target.id_attr)
    rows = session.execute(select(column).where(column.like(f"{target.id_prefix}-%"))).scalars()
    n = max((int(r.rsplit("-", 1)[1]) for r in rows if r.rsplit("-", 1)[1].isdigit()), default=0)
    return f"{target.id_prefix}-{n + 1}"


def _hub_of(session: Session, draft: CaptureDraft) -> str | None:
    """A data-check row has no HubID column; the episode behind it still knows."""
    event_id = (draft.payload.get("events") or [None])[0]
    if not event_id:
        return None
    return session.execute(
        select(TelemetryEvent.hub_id).where(TelemetryEvent.event_id == event_id)
    ).scalar()


def _coerce(attr: str, value):
    if value in (None, ""):
        return None
    if attr in ("reported_date", "date_of_last_email_sent", "check_date"):
        return date.fromisoformat(str(value)[:10])
    if attr == "last_online":
        return datetime.fromisoformat(str(value))
    if attr == "offline_duration_hrs":
        return Decimal(str(value))
    return value
