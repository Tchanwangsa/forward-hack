"""The raw upstream artifacts tier 1 watches. See ../../plan/UPSTREAM-SOURCES.md.

These are not registers. They are the world as it actually happened, in the
systems it happened in — and every drafted row points back to one of them.

Provenance prefixes, which are the `captured_from` values on a committed row:

    tel:TEL-2026-0084210                        TelemetryEvent.event_id
    eml:<msgid>                                 EmailMessage.message_id
    tx:TX-2026-0187@00:14:02-00:14:28           MeetingTranscript + a time range
    wo:WO-21412                                 WorkOrder.work_order_id
    round:RD-2026-0412                          WardRound.round_id
"""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from asteria.models.base import Base


class TelemetryEvent(Base):
    """sources/telemetry/events.ndjson — outage watch's primary source.

    The two columns that make this the strongest bot: `code` IS an indicator
    code (the incident log's Event Code is blank on 27% of human rows), and
    `sw_version` is what the hub reported at the moment of the fault (blank on
    35% of human rows, and on 13 of the 15 rows in the primary story).

    ts_device is the hub's local clock with an offset; ts_received is UTC at the
    ingest edge. They disagree, and which one you window on changes the answer.
    """

    __tablename__ = "telemetry_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    hub_id: Mapped[str | None] = mapped_column(String(32), index=True)
    serial: Mapped[str | None] = mapped_column(String(60))
    customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    ward_id: Mapped[str | None] = mapped_column(String(40), index=True)
    bed_id: Mapped[str | None] = mapped_column(String(40))
    ts_device: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    ts_received: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    code: Mapped[str | None] = mapped_column(String(40), index=True)
    severity: Mapped[str | None] = mapped_column(String(20))
    sw_version: Mapped[str | None] = mapped_column(String(20), index=True)
    hw_revision: Mapped[str | None] = mapped_column(String(20), index=True)
    source: Mapped[str | None] = mapped_column(String(40))
    dedupe_key: Mapped[str | None] = mapped_column(String(120), index=True)
    payload: Mapped[dict | None] = mapped_column(JSON)

    # Set by outage watch once it has drafted or matched. Not a foreign key —
    # an event may legitimately have no incident row, which is the whole point.
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class TelemetryHeartbeat(Base):
    """sources/telemetry/heartbeats.ndjson.

    Turns Hub Inventory's `SW Version (last observed)` from a stale value with a
    date into an actual timeline — which is what makes the SW-version cohort
    honest. Also the evidence for a hub going quiet: absence of heartbeats.
    """

    __tablename__ = "telemetry_heartbeat"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    hub_id: Mapped[str | None] = mapped_column(String(32), index=True)
    ts_device: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    ts_received: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    code: Mapped[str | None] = mapped_column(String(40))
    sw_version: Mapped[str | None] = mapped_column(String(20), index=True)
    source: Mapped[str | None] = mapped_column(String(40))
    payload: Mapped[dict | None] = mapped_column(JSON)


class EmailMessage(Base):
    """sources/mail/{quality,sales,service,support}/*.eml — 1,938 messages.

    Threading is formed from the header chain (in_reply_to / references), NOT
    from THREADS.json — that file is ground truth for scoring and is never an
    input. The signature block is where Contact Role lives (46% blank in the
    comms log).

    message_id is NOT unique: 196 of the 1,941 messages are duplicate deliveries
    — the same Message-ID arriving twice, hours apart. The file on disk is the
    unique artifact. Inbox triage has to dedupe, and that is part of the job,
    not a data error to be cleaned away.
    """

    __tablename__ = "email_message"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[str] = mapped_column(String(200), index=True)
    mailbox: Mapped[str | None] = mapped_column(String(40), index=True)
    file_path: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    from_name: Mapped[str | None] = mapped_column(String(200))
    from_email: Mapped[str | None] = mapped_column(String(200), index=True)
    to_emails: Mapped[str | None] = mapped_column(Text)
    cc_emails: Mapped[str | None] = mapped_column(Text)
    subject: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    in_reply_to: Mapped[str | None] = mapped_column(String(200), index=True)
    references: Mapped[str | None] = mapped_column(Text)
    direction: Mapped[str | None] = mapped_column(String(20))  # inbound / outbound

    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class MeetingTranscript(Base):
    """sources/meetings/transcripts/TX-*.txt — 56 transcripts, plus attendees.json.

    Header gives the linked Comm ID, date, duration and attendees; the body is
    `[HH:MM:SS] Name (Org, Role): text`. Provenance is a time RANGE, so the
    parsed lines are kept and the scribe cites the span it drew from.
    """

    __tablename__ = "meeting_transcript"

    id: Mapped[int] = mapped_column(primary_key=True)
    transcript_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    comm_id: Mapped[str | None] = mapped_column(String(40), index=True)
    title: Mapped[str | None] = mapped_column(Text)
    meeting_date: Mapped[date | None] = mapped_column(Date, index=True)
    duration: Mapped[str | None] = mapped_column(String(20))
    attendees: Mapped[list | None] = mapped_column(JSON)
    body: Mapped[str | None] = mapped_column(Text)

    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    lines: Mapped[list["TranscriptLine"]] = relationship(
        back_populates="transcript", cascade="all, delete-orphan"
    )


class TranscriptLine(Base):
    """One utterance. `at` is the [HH:MM:SS] stamp, kept as text because that is
    the form the provenance ref uses: tx:TX-2026-0187@00:14:02-00:14:28.
    """

    __tablename__ = "transcript_line"

    id: Mapped[int] = mapped_column(primary_key=True)
    transcript_id: Mapped[str] = mapped_column(
        ForeignKey("meeting_transcript.transcript_id"), index=True
    )
    seq: Mapped[int] = mapped_column(Integer)
    at: Mapped[str | None] = mapped_column(String(12), index=True)
    speaker: Mapped[str | None] = mapped_column(String(120))
    speaker_org: Mapped[str | None] = mapped_column(String(120))
    speaker_role: Mapped[str | None] = mapped_column(String(120))
    text: Mapped[str | None] = mapped_column(Text)

    transcript: Mapped["MeetingTranscript"] = relationship(back_populates="lines")


class WorkOrder(Base):
    """sources/service/work-orders.csv — RMA capture's source.

    reported_fault_verbatim is the customer's words; the technician notes are
    where the actual finding is. The gap between them is the register's value.
    """

    __tablename__ = "work_order"

    id: Mapped[int] = mapped_column(primary_key=True)
    work_order_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    rma_number: Mapped[str | None] = mapped_column(String(40), index=True)
    raised_date: Mapped[date | None] = mapped_column(Date, index=True)
    serial_as_written: Mapped[str | None] = mapped_column(String(60))
    organisation_as_written: Mapped[str | None] = mapped_column(String(200))
    reported_fault_verbatim: Mapped[str | None] = mapped_column(Text)
    received_date: Mapped[date | None] = mapped_column(Date)
    technician: Mapped[str | None] = mapped_column(String(120))
    closed_date: Mapped[date | None] = mapped_column(Date)
    disposition: Mapped[str | None] = mapped_column(Text)

    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)


class TechnicianNote(Base):
    """sources/service/technician-notes.csv — several per work order, timestamped."""

    __tablename__ = "technician_note"

    id: Mapped[int] = mapped_column(primary_key=True)
    note_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    work_order_id: Mapped[str | None] = mapped_column(String(40), index=True)
    ts: Mapped[datetime | None] = mapped_column(DateTime)
    technician: Mapped[str | None] = mapped_column(String(120))
    note: Mapped[str | None] = mapped_column(Text)


class PartReplaced(Base):
    """sources/service/parts-replaced.csv — what was actually swapped.

    A comms module replaced is harder evidence of CONN-LINK-LOSS than any prose.
    """

    __tablename__ = "part_replaced"

    id: Mapped[int] = mapped_column(primary_key=True)
    line_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    work_order_id: Mapped[str | None] = mapped_column(String(40), index=True)
    part_number: Mapped[str | None] = mapped_column(String(60), index=True)
    part_description: Mapped[str | None] = mapped_column(Text)
    qty: Mapped[int | None] = mapped_column(Integer)


class WardRound(Base):
    """sources/ward-rounds/rounds.ndjson — field-check nudge's source.

    `complete` and `incomplete_reason` are the nudge: a round that was planned
    for six beds and walked three leaves three checks that never happened, and
    the log has no row saying so.
    """

    __tablename__ = "ward_round"

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    round_date: Mapped[date | None] = mapped_column(Date, index=True)
    customer_id: Mapped[str | None] = mapped_column(String(32), index=True)
    organisation_as_written: Mapped[str | None] = mapped_column(String(200))
    ward_id: Mapped[str | None] = mapped_column(String(40), index=True)
    walked_by: Mapped[str | None] = mapped_column(String(120))
    started: Mapped[datetime | None] = mapped_column(DateTime)
    beds_planned: Mapped[int | None] = mapped_column(Integer)
    beds_walked: Mapped[int | None] = mapped_column(Integer)
    complete: Mapped[bool | None] = mapped_column(Boolean, index=True)
    incomplete_reason: Mapped[str | None] = mapped_column(Text)

    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)

    beds: Mapped[list["RoundBed"]] = relationship(
        back_populates="round", cascade="all, delete-orphan"
    )


class RoundBed(Base):
    """One bed within a round. `walked` False means the check did not happen."""

    __tablename__ = "round_bed"

    id: Mapped[int] = mapped_column(primary_key=True)
    round_id: Mapped[str] = mapped_column(ForeignKey("ward_round.round_id"), index=True)
    bed_id: Mapped[str | None] = mapped_column(String(40))
    pairing_id: Mapped[str | None] = mapped_column(String(60), index=True)
    serial_read: Mapped[str | None] = mapped_column(String(60))
    patch_lot_read: Mapped[str | None] = mapped_column(String(40))
    observation: Mapped[str | None] = mapped_column(Text)
    action: Mapped[str | None] = mapped_column(Text)
    walked: Mapped[bool | None] = mapped_column(Boolean, index=True)
    check_id: Mapped[str | None] = mapped_column(String(40), index=True)

    round: Mapped["WardRound"] = relationship(back_populates="beds")
