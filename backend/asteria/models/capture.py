"""The capture layer — what tier 1 writes before a human confirms anything.

REGISTERS.md §6, in five rules:
  1. Source rows are never edited. A wrong serial stays wrong in the source.
  2. A bot adds rows and proposes completions; it never rewrites history.
  3. Every agent-written field names its inputs.
  4. Every computed number carries its inputs.
  5. Every human verdict is recorded, including the negative ones.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from asteria.models.base import Base, TimestampMixin, enum_col
from asteria.models.enums import DraftStatus


class SourceSnapshot(Base):
    """One import of one customer workbook. Source rows are never overwritten —
    a re-import makes a new snapshot (ARCHITECTURE.md §Runtime and storage).

    A controlled .xlsx can be generated from a named snapshot for review or audit.
    """

    __tablename__ = "source_snapshot"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(200), index=True)
    sha256: Mapped[str | None] = mapped_column(String(64))
    row_count: Mapped[int | None] = mapped_column(Integer)
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    notes: Mapped[str | None] = mapped_column(Text)


class CaptureDraft(Base, TimestampMixin):
    """A proposed NEW register row. Never committed by a bot.

    It sits in the queue until a human accepts, edits or rejects it. On accept it
    becomes a real row with row_origin = 'Agent (accepted)' (or '(edited)'), and
    captured_from = this draft's artifact_ref.

    artifact_ref is the provenance: 'tel:TEL-2026-0084210', 'eml:<msgid>',
    'tx:TX-2026-0187@00:14:02-00:14:28', 'wo:WO-21412', 'round:RD-2026-0412'.
    Resolvable, or it is a bug.
    """

    __tablename__ = "capture_draft"

    id: Mapped[int] = mapped_column(primary_key=True)
    bot: Mapped[str] = mapped_column(String(40), index=True)  # outage-watch, inbox-triage, ...
    target_register: Mapped[str] = mapped_column(String(40), index=True)  # incident, communication
    artifact_ref: Mapped[str] = mapped_column(String(200), index=True)

    # The drafted row as field -> value. Only fields the source actually evidences;
    # a field the bot cannot know is absent, never guessed (capture rule 2).
    payload: Mapped[dict] = mapped_column(JSON)

    proposed_event_code: Mapped[str | None] = mapped_column(String(40), index=True)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    rationale: Mapped[str | None] = mapped_column(Text)

    status: Mapped[DraftStatus] = enum_col(DraftStatus, default=DraftStatus.PENDING, index=True)
    # Set on accept: the row this became.
    committed_row_id: Mapped[int | None] = mapped_column(Integer)

    fields: Mapped[list["DraftField"]] = relationship(
        back_populates="draft", cascade="all, delete-orphan"
    )
    verdicts: Mapped[list["ReviewVerdict"]] = relationship(back_populates="draft")

    __table_args__ = (UniqueConstraint("bot", "artifact_ref", name="uq_draft_bot_artifact"),)


class DraftField(Base):
    """Per-field provenance and per-field editing.

    The queue screen shows, for each field, what the bot proposed and what in the
    artifact evidences it. When a human edits one field, that is recorded here —
    which field was wrong is the signal we actually want.
    """

    __tablename__ = "draft_field"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int] = mapped_column(ForeignKey("capture_draft.id"), index=True)
    field_name: Mapped[str] = mapped_column(String(80))
    proposed_value: Mapped[str | None] = mapped_column(Text)
    accepted_value: Mapped[str | None] = mapped_column(Text)  # differs => a human edited it
    evidence: Mapped[str | None] = mapped_column(Text)  # the quote / event field behind it
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))

    draft: Mapped["CaptureDraft"] = relationship(back_populates="fields")


class CompletionSuggestion(Base, TimestampMixin):
    """A proposed value for a BLANK or contradicted cell on an EXISTING human row.

    The source row is not touched (capture rule 4). The proposal lives here with
    its evidence, and analysis reads the completed view.

    This is where the 35%-blank SW Version and the 51%-blank Patch Lot get fixed —
    often a join rather than a transcription.
    """

    __tablename__ = "completion_suggestion"

    id: Mapped[int] = mapped_column(primary_key=True)
    bot: Mapped[str] = mapped_column(String(40), index=True)
    target_register: Mapped[str] = mapped_column(String(40), index=True)
    target_row_key: Mapped[str] = mapped_column(String(40), index=True)  # INC-..., RMA-...
    field_name: Mapped[str] = mapped_column(String(80), index=True)

    existing_value: Mapped[str | None] = mapped_column(Text)  # usually blank
    proposed_value: Mapped[str] = mapped_column(Text)
    artifact_ref: Mapped[str | None] = mapped_column(String(200), index=True)
    evidence: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    rationale: Mapped[str | None] = mapped_column(Text)

    status: Mapped[DraftStatus] = enum_col(DraftStatus, default=DraftStatus.PENDING, index=True)

    __table_args__ = (
        UniqueConstraint(
            "target_register", "target_row_key", "field_name", name="uq_completion_target_field"
        ),
    )


class ReviewVerdict(Base):
    """The human gate, recorded. Rule 5: every verdict, including the negative ones.

    A rejection is a permanent record with a named reviewer and a rationale.
    Never a deletion.
    """

    __tablename__ = "review_verdict"

    id: Mapped[int] = mapped_column(primary_key=True)
    draft_id: Mapped[int | None] = mapped_column(ForeignKey("capture_draft.id"), index=True)
    completion_id: Mapped[int | None] = mapped_column(
        ForeignKey("completion_suggestion.id"), index=True
    )
    verdict: Mapped[DraftStatus] = enum_col(DraftStatus)
    reviewed_by: Mapped[str] = mapped_column(String(120))
    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    rationale: Mapped[str | None] = mapped_column(Text)  # mandatory on reject
    edited_fields: Mapped[list | None] = mapped_column(JSON)

    draft: Mapped["CaptureDraft | None"] = relationship(back_populates="verdicts")
