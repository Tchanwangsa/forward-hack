"""Declarative base, shared columns, and the two capture columns.

Naming: the workbooks' column names are messy and stay messy on export
(REGISTERS.md §3 — "tidying it deletes the product"). In the database the
attributes are snake_case; the original header for each is held in the ingest
layer's header maps, so a generated .xlsx reproduces the customer's file exactly.
"""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from asteria.models.enums import RowOrigin


class Base(DeclarativeBase):
    pass


def enum_col(py_enum: type[StrEnum], **kw):
    """VARCHAR + CHECK rather than a native PG enum. See models/enums.py."""
    return mapped_column(
        Enum(py_enum, native_enum=False, values_callable=lambda e: [m.value for m in e]), **kw
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class CaptureColumnsMixin:
    """REGISTERS.md §3.0 — appended to every capture-fed register.

    row_origin is never 'Agent (pending)'. A pending draft lives in CaptureDraft,
    not here. captured_from is blank on human rows and resolvable on agent rows,
    or it is a bug.
    """

    row_origin: Mapped[RowOrigin] = enum_col(RowOrigin, default=RowOrigin.HUMAN, index=True)
    captured_from: Mapped[str | None] = mapped_column(String(200), index=True)
