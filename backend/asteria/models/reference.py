"""Registers 1 and 7 — reference only. See REGISTERS.md §3.1 and §3.7.

**No capture agent writes to a reference register.** Both denominators and the
entire rule set come from these tables; an agent that can edit them can move
every number in the product.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from asteria.models.base import Base, TimestampMixin, enum_col
from asteria.models.enums import DenominatorKind, ThresholdKind, UnitStatus


class CustomerOrganisation(Base, TimestampMixin):
    """Organisations sheet — 16 rows, AU/NZ/UK/NO.

    The PulseOne unit counts here are a stale human summary and will disagree
    with a count of the hub inventory. The inventory is authoritative.
    """

    __tablename__ = "customer_organisation"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    organisation_name: Mapped[str] = mapped_column(String(200))
    legal_entity_name: Mapped[str | None] = mapped_column(String(200))
    location: Mapped[str | None] = mapped_column(String(120))
    state: Mapped[str | None] = mapped_column(String(80))
    country_region: Mapped[str | None] = mapped_column(String(80))
    status: Mapped[str | None] = mapped_column(String(40))  # Active, Evaluation, ...
    timezone: Mapped[str | None] = mapped_column(String(60))
    record_id: Mapped[str | None] = mapped_column(String(40))
    customer_since: Mapped[date | None] = mapped_column(Date)
    units_total_stated: Mapped[int | None] = mapped_column(Integer)
    units_in_service_stated: Mapped[int | None] = mapped_column(Integer)
    wards: Mapped[str | None] = mapped_column(Text)
    primary_contact: Mapped[str | None] = mapped_column(String(120))
    primary_contact_email: Mapped[str | None] = mapped_column(String(200))
    sales_channel: Mapped[str | None] = mapped_column(String(60))  # NOT the comms Channel
    account_owner: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)

    hubs: Mapped[list["Hub"]] = relationship(back_populates="organisation")


class Hub(Base, TimestampMixin):
    """PulseOne Hub Inventory — 250 rows. The most important sheet in the product.

    sw_version_last_observed is a last-observed value with a date, not a fact.
    Some observed-on dates are months stale and one or two are a year in the
    future because somebody typed the wrong year. Telemetry heartbeats turn this
    column into a timeline.
    """

    __tablename__ = "hub"

    id: Mapped[int] = mapped_column(primary_key=True)
    hub_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(60), index=True)
    customer_id: Mapped[str | None] = mapped_column(
        ForeignKey("customer_organisation.customer_id"), index=True
    )
    organisation_name_as_written: Mapped[str | None] = mapped_column(String(200))
    ward_id: Mapped[str | None] = mapped_column(String(40), index=True)
    bed_id: Mapped[str | None] = mapped_column(String(40))
    hw_revision: Mapped[str | None] = mapped_column(String(20), index=True)  # H1, H2, H2.1
    sw_version_last_observed: Mapped[str | None] = mapped_column(String(20), index=True)
    sw_version_observed_on: Mapped[date | None] = mapped_column(Date)
    install_date: Mapped[date | None] = mapped_column(Date)
    unit_status: Mapped[UnitStatus | None] = enum_col(UnitStatus, index=True)
    pairing_id: Mapped[str | None] = mapped_column(String(60), index=True)
    pairing_status: Mapped[str | None] = mapped_column(String(40))
    last_online_local: Mapped[datetime | None] = mapped_column(DateTime)
    notes: Mapped[str | None] = mapped_column(Text)
    decommission_date: Mapped[date | None] = mapped_column(Date)  # accrual_end when set
    depot_date: Mapped[date | None] = mapped_column(Date)  # accrual_end when At depot

    organisation: Mapped["CustomerOrganisation | None"] = relationship(back_populates="hubs")


class PatchLotAllocation(Base, TimestampMixin):
    """PulsePatch Stock Allocation — 275 rows. The IND-05/IND-06 denominator."""

    __tablename__ = "patch_lot_allocation"

    id: Mapped[int] = mapped_column(primary_key=True)
    lot_code: Mapped[str] = mapped_column(String(40), index=True)
    product_code: Mapped[str | None] = mapped_column(String(40))
    manufactured: Mapped[date | None] = mapped_column(Date)
    expiry: Mapped[date | None] = mapped_column(Date)
    customer_id: Mapped[str | None] = mapped_column(
        ForeignKey("customer_organisation.customer_id"), index=True
    )
    organisation_name_as_written: Mapped[str | None] = mapped_column(String(200))
    patches_allocated: Mapped[int | None] = mapped_column(Integer)
    boxes: Mapped[int | None] = mapped_column(Integer)
    shipped_date: Mapped[date | None] = mapped_column(Date, index=True)
    notes: Mapped[str | None] = mapped_column(Text)


class Indicator(Base, TimestampMixin):
    """Indicators & Thresholds sheet — 7 rows. Approved in advance, in a controlled
    document. The engine reads these; it never hardcodes the numbers.

    Escalation is written as '2.0x baseline' or 'Any increase - clinical review';
    threshold_kind + threshold_multiplier is that parsed. See REGISTERS.md §1.
    """

    __tablename__ = "indicator"

    id: Mapped[int] = mapped_column(primary_key=True)
    indicator_id: Mapped[str] = mapped_column(String(16), unique=True, index=True)  # IND-01
    product: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    internal_code: Mapped[str] = mapped_column(String(40), unique=True, index=True)  # ALERT-FALSE
    denominator_kind: Mapped[DenominatorKind] = enum_col(DenominatorKind)
    baseline: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    threshold_kind: Mapped[ThresholdKind] = enum_col(ThresholdKind)
    threshold_multiplier: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    escalation_as_written: Mapped[str] = mapped_column(String(80))
    review_function: Mapped[str] = mapped_column(String(40))  # Quality / Clinical / Service
    source_document: Mapped[str] = mapped_column(String(60))  # PMS-PLAN-001 v3.0


class ControlledDocument(Base, TimestampMixin):
    """PMS Documents sheet — 24 rows.

    Includes the monthly trend working files. One is Overdue, noted 'Data pending
    from service team' — the business case sitting in the customer's own spreadsheet.
    """

    __tablename__ = "controlled_document"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    title: Mapped[str] = mapped_column(Text)
    doc_type: Mapped[str | None] = mapped_column(String(60))
    version: Mapped[str | None] = mapped_column(String(20))
    status: Mapped[str | None] = mapped_column(String(40), index=True)
    approved_date: Mapped[date | None] = mapped_column(Date)
    next_review_due: Mapped[date | None] = mapped_column(Date)
    owner: Mapped[str | None] = mapped_column(String(120))
    frequency: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)


class PMSReviewMeeting(Base, TimestampMixin):
    """PMS Review Meetings sheet — 22 rows. Where a signal goes to be discussed.

    Tier 3 reads the minutes for its recurrence argument.
    """

    __tablename__ = "pms_review_meeting"

    id: Mapped[int] = mapped_column(primary_key=True)
    meeting_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    meeting_date: Mapped[date | None] = mapped_column(Date, index=True)
    meeting_type: Mapped[str | None] = mapped_column(String(60))
    attendees: Mapped[str | None] = mapped_column(Text)
    chair: Mapped[str | None] = mapped_column(String(120))
    minutes_status: Mapped[str | None] = mapped_column(String(40))
    items_reviewed: Mapped[str | None] = mapped_column(Text)
    actions_raised: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
