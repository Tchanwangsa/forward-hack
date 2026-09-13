"""What the triage agent did, step by step. The audit trail for a diagnosis.

The Agent Action Log records that triage ran and what it concluded. This pair of
tables records *how* — which clause of OPS-SOP-004 each check belongs to, what
the check returned, and which one ended it. Two reasons it is a table and not a
blob in the action log:

    A reviewer deciding whether to accept the drafted row is deciding whether
    the diagnosis is sound, and cannot do that without the checks that found
    nothing. OPS-SOP-004 §3 C3 requires them recorded.

    `procedure_revision` on every run means a triage from last quarter still
    says which revision of the procedure it was made under. When the SOP moves
    to 4.0, nothing retroactively reinterprets a decision made under 3.0.

`actual_cause` is the estate's hidden truth, stored for scoring and never shown
to a reviewer as a finding — the agent did not know it when it decided.
"""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from asteria.models.base import Base, TimestampMixin


class TriageRun(Base, TimestampMixin):
    """One episode, one walk of the procedure, one conclusion."""

    __tablename__ = "triage_run"

    id: Mapped[int] = mapped_column(primary_key=True)
    bot: Mapped[str] = mapped_column(String(40), index=True)
    artifact_ref: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    hub_id: Mapped[str | None] = mapped_column(String(32), index=True)
    event_code: Mapped[str | None] = mapped_column(String(40), index=True)

    procedure_id: Mapped[str] = mapped_column(String(40))  # OPS-SOP-004
    procedure_revision: Mapped[str] = mapped_column(String(20))
    procedure_verification: Mapped[str | None] = mapped_column(Text)

    outcome: Mapped[str] = mapped_column(String(40), index=True)
    disposition: Mapped[str] = mapped_column(String(40), index=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    deciding_step: Mapped[str | None] = mapped_column(String(20))
    citation: Mapped[str | None] = mapped_column(String(80))
    narrative: Mapped[str | None] = mapped_column(Text)
    escalate_to: Mapped[str | None] = mapped_column(String(80))
    checks_run: Mapped[int] = mapped_column(Integer, default=0)
    findings: Mapped[dict | None] = mapped_column(JSON)

    # Scoring only. Never rendered as a finding, never drafted into a register.
    actual_cause: Mapped[str | None] = mapped_column(String(40), index=True)
    correct: Mapped[bool | None] = mapped_column(Boolean, index=True)

    # What the run produced, where it produced anything.
    draft_id: Mapped[int | None] = mapped_column(ForeignKey("capture_draft.id"), index=True)

    steps: Mapped[list[TriageStep]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="TriageStep.ordinal"
    )


class TriageStep(Base):
    """One clause, executed. Including the ones that found nothing."""

    __tablename__ = "triage_step"

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("triage_run.id"), index=True)
    ordinal: Mapped[int] = mapped_column(Integer)

    step_id: Mapped[str] = mapped_column(String(20))  # T1 ... T8
    section: Mapped[str | None] = mapped_column(String(20))  # 5.1 ...
    title: Mapped[str] = mapped_column(String(120))
    question: Mapped[str | None] = mapped_column(Text)

    satisfied: Mapped[str | None] = mapped_column(String(60))  # the condition that fired
    outcome: Mapped[str | None] = mapped_column(String(40))
    goto: Mapped[str | None] = mapped_column(String(20))
    note: Mapped[str | None] = mapped_column(Text)

    # [{tool, target, summary, metrics, transcript}] — the screen the analyst
    # would have seen, kept as the provenance for anything drafted off it.
    probes: Mapped[list | None] = mapped_column(JSON)

    run: Mapped[TriageRun] = relationship(back_populates="steps")
