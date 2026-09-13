"""Registers 8-11 — system-maintained. See REGISTERS.md §4.

Written by tiers 2 and 3. Every terminal status needs a named human and a
rationale, and nothing is ever deleted.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Integer, JSON, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from asteria.models.base import Base, CaptureColumnsMixin, TimestampMixin, enum_col
from asteria.models.enums import (
    Autonomy,
    CAPADecision,
    CAPAStatus,
    CAPATrigger,
    CohortKind,
    HumanVerdict,
    SignalStatus,
)


class Signal(Base, TimestampMixin):
    """Register 8 — Signal Register. Written by WF 3, updated by WF 4.

    Every number is stored with its inputs (event_count, denominator_value,
    window) so the rate can be recomputed, not just believed — REGISTERS.md §6.4.

    capture_dependent is the most persuasive single cell in the product: whether
    this signal is visible at all without tier 1's drafted rows and completions.
    On the primary story it is True.

    'Closed - no action' is a permanent row with a rationale, never a deletion.
    A signal the team correctly dismissed is evidence the surveillance is working.
    """

    __tablename__ = "signal"

    id: Mapped[int] = mapped_column(primary_key=True)
    signal_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    raised: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    indicator_id: Mapped[str] = mapped_column(String(16), index=True)
    product: Mapped[str | None] = mapped_column(String(40))
    cohort: Mapped[CohortKind] = enum_col(CohortKind, index=True)
    cohort_value: Mapped[str | None] = mapped_column(String(80), index=True)

    observed_rate: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    baseline: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    threshold: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    ratio: Mapped[Decimal | None] = mapped_column(Numeric(12, 4))
    window_start: Mapped[date | None] = mapped_column(Date)
    window_end: Mapped[date | None] = mapped_column(Date)
    event_count: Mapped[int | None] = mapped_column(Integer)
    denominator_value: Mapped[Decimal | None] = mapped_column(Numeric(14, 4))

    # Every incident / RMA / check / comm / complaint ID that contributed.
    linked_events: Mapped[list | None] = mapped_column(JSON)

    capture_dependent: Mapped[bool | None] = mapped_column(Boolean, index=True)
    # What it thinks, including the innocent explanation it considered.
    agent_rationale: Mapped[str | None] = mapped_column(Text)

    status: Mapped[SignalStatus] = enum_col(SignalStatus, index=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(120))
    review_date: Mapped[date | None] = mapped_column(Date)
    outcome_rationale: Mapped[str | None] = mapped_column(Text)  # mandatory on terminal
    linked_nc: Mapped[str | None] = mapped_column(String(40), index=True)
    raised_at_pms_meeting: Mapped[str | None] = mapped_column(String(40))


class ProductNC(Base, TimestampMixin):
    """Register 9 — Product NC Register. Drafted by WF 5, signed by a human.

    An NC always has a signal behind it. affected_scope is serials and lots
    resolved from Hub Inventory + Lot Allocation — not a version string.

    capa_considered = False requires a rationale. A no-CAPA decision is a record.
    """

    __tablename__ = "product_nc"

    id: Mapped[int] = mapped_column(primary_key=True)
    nc_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    raised_from_signal: Mapped[str | None] = mapped_column(String(40), index=True)
    date_raised: Mapped[date | None] = mapped_column(Date, index=True)
    product: Mapped[str | None] = mapped_column(String(40))
    affected_scope: Mapped[dict | None] = mapped_column(JSON)  # {serials: [], lots: []}
    units_in_field: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    indicator_id: Mapped[str | None] = mapped_column(String(16), index=True)
    evidence_links: Mapped[list | None] = mapped_column(JSON)  # source row IDs, every one
    containment: Mapped[str | None] = mapped_column(Text)  # or the decision that nothing was
    investigation_owner: Mapped[str | None] = mapped_column(String(120))
    root_cause: Mapped[str | None] = mapped_column(Text)  # human-written
    disposition: Mapped[str | None] = mapped_column(Text)  # agent proposes, human decides
    capa_considered: Mapped[bool | None] = mapped_column(Boolean)
    capa_rationale: Mapped[str | None] = mapped_column(Text)  # mandatory when False
    linked_capa: Mapped[str | None] = mapped_column(String(40), index=True)
    status: Mapped[str | None] = mapped_column(String(40), index=True)
    approved_by: Mapped[str | None] = mapped_column(String(120))
    date_closed: Mapped[date | None] = mapped_column(Date)


class CAPA(Base, CaptureColumnsMixin, TimestampMixin):
    """Register 10 — CAPA Register. NEW. Recommended by tier 3, OPENED BY A HUMAN.

    Scope discipline: tier 3 drafts the problem statement, the evidence and the
    recurrence argument. It does NOT run the investigation, implement the action,
    verify effectiveness, or close it. The execution fields below exist so the
    register is a real register, and the agent leaves them alone.

    why_prior_action_did_not_hold is the sharpest field here: a CAPA system whose
    history does not record why the last fix failed will recommend the same fix
    again. Declined and Deferred both require a rationale and both stay forever.
    """

    __tablename__ = "capa"

    id: Mapped[int] = mapped_column(primary_key=True)
    capa_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    date_recommended: Mapped[date | None] = mapped_column(Date, index=True)
    date_opened: Mapped[date | None] = mapped_column(Date)  # the gap is a metric
    trigger: Mapped[CAPATrigger | None] = enum_col(CAPATrigger)
    raised_from: Mapped[list | None] = mapped_column(JSON)  # usually several NCs/signals

    # --- agent drafts ---
    problem_statement: Mapped[str | None] = mapped_column(Text)
    recurrence_evidence: Mapped[str | None] = mapped_column(Text)
    prior_action: Mapped[str | None] = mapped_column(Text)
    why_prior_action_did_not_hold: Mapped[str | None] = mapped_column(Text)
    product: Mapped[str | None] = mapped_column(String(40))
    affected_scope: Mapped[dict | None] = mapped_column(JSON)
    indicator_ids: Mapped[list | None] = mapped_column(JSON)  # a CAPA may span more than one

    # --- human only ---
    decision: Mapped[CAPADecision | None] = enum_col(CAPADecision)
    decision_rationale: Mapped[str | None] = mapped_column(Text)  # mandatory either way
    owner: Mapped[str | None] = mapped_column(String(120))
    target_date: Mapped[date | None] = mapped_column(Date)
    root_cause: Mapped[str | None] = mapped_column(Text)
    corrective_action: Mapped[str | None] = mapped_column(Text)
    preventive_action: Mapped[str | None] = mapped_column(Text)
    effectiveness_check: Mapped[str | None] = mapped_column(Text)
    effectiveness_verified: Mapped[bool | None] = mapped_column(Boolean)
    date_closed: Mapped[date | None] = mapped_column(Date)
    status: Mapped[CAPAStatus | None] = enum_col(CAPAStatus, index=True)


class AgentAction(Base):
    """Register 11 — Agent Action Log. Append-only. Empty at demo start.

    The log IS the provenance layer — there is no separate claim/binding layer.
    Any agent-written value traces back by following `inputs`.

    human_verdict = 'edited' on a capture draft is the honest measure of whether
    a bot is any good, and it names how it was wrong. rule_model_version means a
    rate computed in March stays explainable in September.

    Never updated, never deleted. Corrections are new rows.
    """

    __tablename__ = "agent_action"

    id: Mapped[int] = mapped_column(primary_key=True)
    action_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
    tier: Mapped[int] = mapped_column(Integer, index=True)  # 1-3
    workflow: Mapped[str] = mapped_column(String(60), index=True)  # bot name | WF 1-5 | sweep
    autonomy_level: Mapped[Autonomy] = enum_col(Autonomy)
    inputs: Mapped[dict | None] = mapped_column(JSON)  # artifact + source record IDs
    rule_model_version: Mapped[str | None] = mapped_column(String(80))
    output: Mapped[dict | None] = mapped_column(JSON)
    human_verdict: Mapped[HumanVerdict | None] = enum_col(HumanVerdict, index=True)
    reviewed_by: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
