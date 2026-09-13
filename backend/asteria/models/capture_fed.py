"""Registers 2-6 — human rows plus capture-bot rows. See REGISTERS.md §3.2-§3.6.

Column order and the mess are preserved: the abbreviation sloppiness, the blank
cells, the organisation-name variants. That mess is the problem the product
solves. Nullability here is deliberate — a blank cell must stay blank.

Every table carries row_origin + captured_from from CaptureColumnsMixin.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from asteria.models.base import Base, CaptureColumnsMixin, TimestampMixin, enum_col
from asteria.models.enums import Channel, ComplaintStatus, IncidentSource


class Incident(Base, CaptureColumnsMixin, TimestampMixin):
    """Register 2 — PM-Incident-and-Outage-Log. 737 rows, 20 + 2 cols.

    307 rows carry an indicator; 430 are logistics, site network, user error and
    duplicates. 62 indicator events that happened have no row here at all — that
    set is outage watch's headline.

    event_code is blank on 27% and wrong on 9% of human indicator rows.
    sw_version_at_time is blank on 35% — and on 13 of the 15 rows in the primary
    story. last_online is a snapshot copied from the inventory, not the time of
    the incident: a column that looks event-related and is not.
    """

    __tablename__ = "incident"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    pairing_id: Mapped[str | None] = mapped_column(String(60), index=True)
    pairing_status: Mapped[str | None] = mapped_column(String(40))
    organisation_as_written: Mapped[str | None] = mapped_column(String(200))
    hub_id: Mapped[str | None] = mapped_column(String(32), index=True)
    serial_number_as_written: Mapped[str | None] = mapped_column(String(60))
    ward_id: Mapped[str | None] = mapped_column(String(40), index=True)
    bed_id: Mapped[str | None] = mapped_column(String(40))
    last_online: Mapped[datetime | None] = mapped_column(DateTime)
    offline_duration_hrs: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    reported_date: Mapped[date | None] = mapped_column(Date, index=True)
    incident_description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(40))
    date_of_last_email_sent: Mapped[date | None] = mapped_column(Date)
    reported_by: Mapped[str | None] = mapped_column(String(120))
    assigned_to: Mapped[str | None] = mapped_column(String(120))
    sw_version_at_time: Mapped[str | None] = mapped_column(String(20), index=True)
    notes: Mapped[str | None] = mapped_column(Text)
    event_code: Mapped[str | None] = mapped_column(String(40), index=True)
    source: Mapped[IncidentSource | None] = enum_col(IncidentSource)

    # Resolved by asteria.resolve.entities — never overwrites the as-written columns.
    resolved_customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    resolved_hub_id: Mapped[str | None] = mapped_column(String(32), index=True)


class ProductReturn(Base, CaptureColumnsMixin, TimestampMixin):
    """Register 3 — Product-Return-and-Replacement-Register. 308 rows, 20 + 2 cols.

    The register's whole value is the gap between customer_reported_fault and
    technician_findings: "Unit alarming for no reason" against "Configuration
    reset to ward profile, no hardware fault" is an ALERT-FALSE event and its
    explanation in one row.

    serial_number arrives as 'PO-P1-004226', 'SN 4216', 'P1100-4563', and with
    trailing whitespace. sw_version is blank on 48% and recoverable from the hub
    inventory as at date_raised — a completion that is a join, not a transcription.
    linked_complaint is blank on 83%.
    """

    __tablename__ = "product_return"

    id: Mapped[int] = mapped_column(primary_key=True)
    rma_number: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    date_raised: Mapped[date | None] = mapped_column(Date, index=True)
    organisation_as_written: Mapped[str | None] = mapped_column(String(200))
    customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    product: Mapped[str | None] = mapped_column(String(40))
    serial_number_as_written: Mapped[str | None] = mapped_column(String(60))
    hw_rev: Mapped[str | None] = mapped_column(String(20))
    sw_version: Mapped[str | None] = mapped_column(String(20))
    customer_reported_fault: Mapped[str | None] = mapped_column(Text)
    date_received: Mapped[date | None] = mapped_column(Date)
    technician_findings: Mapped[str | None] = mapped_column(Text)
    component_replaced: Mapped[str | None] = mapped_column(String(120))
    linked_complaint: Mapped[str | None] = mapped_column(String(40), index=True)
    disposition: Mapped[str | None] = mapped_column(String(80))
    replacement_serial: Mapped[str | None] = mapped_column(String(60))
    date_closed: Mapped[date | None] = mapped_column(Date)
    technician: Mapped[str | None] = mapped_column(String(120))
    warranty_status: Mapped[str | None] = mapped_column(String(40))
    notes: Mapped[str | None] = mapped_column(Text)
    linked_signal: Mapped[str | None] = mapped_column(String(40), index=True)

    resolved_customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    resolved_hub_id: Mapped[str | None] = mapped_column(String(32), index=True)
    resolved_event_code: Mapped[str | None] = mapped_column(String(40), index=True)


class DataCheck(Base, CaptureColumnsMixin, TimestampMixin):
    """Register 4 — PM-Data-Check-and-Troubleshooting-Log. 712 rows, 15 + 2 cols.

    Four free-text issue columns, mostly blank, mapping *imperfectly* onto the
    seven indicators — the hardest classification job in the dataset. An adhesive
    finding sits in hardware_issues; a battery finding sometimes sits in
    software_issues as "Charge state reporting wrong"; one row can carry two
    indicators.

    serial_number blank on 26% and sometimes the bare '4111'. patch_lot blank on
    51%. action_taken blank on 66% — often stated in the ward round it came from
    and lost on the way to the spreadsheet.
    """

    __tablename__ = "data_check"

    id: Mapped[int] = mapped_column(primary_key=True)
    check_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    check_date: Mapped[date | None] = mapped_column(Date, index=True)
    organisation_as_written: Mapped[str | None] = mapped_column(String(200))
    ward: Mapped[str | None] = mapped_column(String(40), index=True)
    bed: Mapped[str | None] = mapped_column(String(40))
    pairing: Mapped[str | None] = mapped_column(String(80))
    serial_number_as_written: Mapped[str | None] = mapped_column(String(60))
    patch_lot: Mapped[str | None] = mapped_column(String(40), index=True)
    hardware_issues: Mapped[str | None] = mapped_column(Text)
    alert_misclassifications: Mapped[str | None] = mapped_column(Text)
    patient_and_alert_issues: Mapped[str | None] = mapped_column(Text)
    software_issues: Mapped[str | None] = mapped_column(Text)
    issue_found: Mapped[str | None] = mapped_column(Text)
    checked_by: Mapped[str | None] = mapped_column(String(120))
    action_taken: Mapped[str | None] = mapped_column(Text)

    resolved_customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    resolved_hub_id: Mapped[str | None] = mapped_column(String(32), index=True)
    # A row can carry two indicators — stored as a comma-separated code list.
    resolved_event_codes: Mapped[str | None] = mapped_column(String(200), index=True)


class Communication(Base, CaptureColumnsMixin, TimestampMixin):
    """Register 5 — PM-Client-Communications-Log. 566 rows, 15 + 3 cols.

    One register for ALL feedback channels, via `channel`. ISO 13485 §8.2.1 is one
    feedback net: a concern raised in a Tuesday site visit and the same concern
    emailed on Wednesday are the same feedback.

    email_subject stays named that on a Channel = Meeting row, holding the meeting
    title. Misnamed, and stays misnamed, because the real file is.

    comm_type is human-assigned and unreliable — 'Complaint' here is a casual
    label, NOT a complaint record. The formal object is Complaint.
    cross_reference is free text and an unreliable join: a hint, never a key.
    contact_role is blank on 46% and sits in the email signature block.
    """

    __tablename__ = "communication"

    id: Mapped[int] = mapped_column(primary_key=True)
    comm_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    email_subject: Mapped[str | None] = mapped_column(Text)
    date_of_initial_email: Mapped[date | None] = mapped_column(Date, index=True)
    date_of_last_email_sent: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str | None] = mapped_column(String(40))
    comm_type: Mapped[str | None] = mapped_column(String(60))
    organisation_as_written: Mapped[str | None] = mapped_column(String(200))
    client_contact: Mapped[str | None] = mapped_column(String(120))
    contact_role: Mapped[str | None] = mapped_column(String(120))
    contact_email: Mapped[str | None] = mapped_column(String(200))
    handled_by: Mapped[str | None] = mapped_column(String(120))
    mailbox: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)
    attachments: Mapped[str | None] = mapped_column(Text)
    cross_reference: Mapped[str | None] = mapped_column(Text)
    channel: Mapped[Channel | None] = enum_col(Channel, index=True)

    resolved_customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    resolved_event_code: Mapped[str | None] = mapped_column(String(40), index=True)


class Complaint(Base, CaptureColumnsMixin, TimestampMixin):
    """Register 6 — Complaint-Register. NEW. See REGISTERS.md §3.6.

    Recommended by inbox triage, CLASSIFIED BY A HUMAN. A complaint under ISO
    13485 §8.2.2 is a record with an owner, an investigation decision, a closure
    rationale and a vigilance screen — not a note about a conversation.

    'Declined' is a first-class status with a rationale. A complaint register with
    no declined rows is a register nobody is actually screening.
    """

    __tablename__ = "complaint"

    id: Mapped[int] = mapped_column(primary_key=True)
    complaint_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    date_received: Mapped[date | None] = mapped_column(Date, index=True)  # customer's clock
    date_opened: Mapped[date | None] = mapped_column(Date)  # ours; the gap is a metric
    channel: Mapped[Channel | None] = enum_col(Channel)
    organisation_as_written: Mapped[str | None] = mapped_column(String(200))
    customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    complainant: Mapped[str | None] = mapped_column(String(120))
    contact_role: Mapped[str | None] = mapped_column(String(120))
    contact_email: Mapped[str | None] = mapped_column(String(200))
    product: Mapped[str | None] = mapped_column(String(40))
    serial_number_as_written: Mapped[str | None] = mapped_column(String(60))
    patch_lot: Mapped[str | None] = mapped_column(String(40))

    # The customer's words. Never the agent's paraphrase.
    description_as_reported: Mapped[str | None] = mapped_column(Text)

    indicator_id: Mapped[str | None] = mapped_column(String(16), index=True)  # proposed
    event_code: Mapped[str | None] = mapped_column(String(40), index=True)  # proposed
    classification_confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))

    investigation_required: Mapped[bool | None] = mapped_column(Boolean)  # human
    investigation_summary: Mapped[str | None] = mapped_column(Text)  # human

    # HUMAN ONLY. The agent never fills this. Vigilance is out of scope; the field
    # exists to mark the boundary rather than hide it.
    vigilance_screen_required: Mapped[bool | None] = mapped_column(Boolean)

    linked_comm: Mapped[str | None] = mapped_column(String(40), index=True)
    linked_incident: Mapped[str | None] = mapped_column(String(40), index=True)
    linked_rma: Mapped[str | None] = mapped_column(String(40), index=True)
    linked_signal: Mapped[str | None] = mapped_column(String(40), index=True)
    linked_nc: Mapped[str | None] = mapped_column(String(40), index=True)

    status: Mapped[ComplaintStatus | None] = enum_col(ComplaintStatus, index=True)
    owner: Mapped[str | None] = mapped_column(String(120))
    date_closed: Mapped[date | None] = mapped_column(Date)
    closure_rationale: Mapped[str | None] = mapped_column(Text)  # mandatory on terminal
    customer_informed: Mapped[bool | None] = mapped_column(Boolean)
    date_informed: Mapped[date | None] = mapped_column(Date)
