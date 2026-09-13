"""Append-only writes to the Agent Action Log. The only way anything gets logged.

A rejected draft, a declined complaint, a signal closed as no action, a CAPA
judged unnecessary — each is a permanent record with a named reviewer and a
rationale. Never a deletion.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from asteria.agent.autonomy import Autonomy
from asteria.config import settings
from asteria.models.enums import Autonomy as AutonomyValue
from asteria.models.enums import HumanVerdict
from asteria.models.system import AgentAction


def log_action(
    session: Session,
    *,
    tier: int,
    workflow: str,
    autonomy: Autonomy,
    inputs: dict | None = None,
    output: dict | None = None,
    human_verdict: HumanVerdict | None = None,
    reviewed_by: str | None = None,
    notes: str | None = None,
    rule_model_version: str | None = None,
) -> AgentAction:
    """One row. Never updated, never deleted — a correction is another row."""
    action = AgentAction(
        action_id=_next_action_id(session),
        tier=tier,
        workflow=workflow,
        autonomy_level=AutonomyValue(str(int(autonomy))),
        inputs=inputs,
        output=output,
        human_verdict=human_verdict,
        reviewed_by=reviewed_by,
        notes=notes,
        rule_model_version=rule_model_version or settings.anthropic_model,
    )
    session.add(action)
    session.flush()
    return action


def _next_action_id(session: Session) -> str:
    n = session.execute(select(func.count(AgentAction.id))).scalar() or 0
    return f"ACT-{n + 1:06d}"
