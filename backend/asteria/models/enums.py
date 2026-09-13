"""Controlled vocabularies. Stored as VARCHAR + CHECK, not native PG enums —
adding a value shouldn't need a migration dance during a hackathon.

Values are the exact strings the registers use, so ingest and export are identity.
"""

from enum import StrEnum


class RowOrigin(StrEnum):
    """REGISTERS.md §3.0. Never 'Agent (pending)' — a pending draft is not a row."""

    HUMAN = "Human"
    AGENT_ACCEPTED = "Agent (accepted)"
    AGENT_EDITED = "Agent (edited)"


class Channel(StrEnum):
    """Communication medium. Shared by the comms log and the complaint register."""

    EMAIL = "Email"
    MEETING = "Meeting"
    PHONE = "Phone"
    PORTAL = "Portal"


class UnitStatus(StrEnum):
    """Hub Inventory. Drives the unit-months denominator — see analysis/denominators.py.

    IN_SERVICE and INSTALLED are the same state with different data-entry habits.
    Treating them as two is a denominator bug.
    """

    IN_SERVICE = "In service"
    INSTALLED = "Installed"
    AT_DEPOT_RMA = "At depot (RMA)"
    DECOMMISSIONED = "Decommissioned"
    SPARE = "Spare"
    SHIPPED_NOT_INSTALLED = "Shipped - not installed"


ACCRUING_STATUSES = {
    UnitStatus.IN_SERVICE,
    UnitStatus.INSTALLED,
    UnitStatus.AT_DEPOT_RMA,
    UnitStatus.DECOMMISSIONED,
}


class DenominatorKind(StrEnum):
    UNIT_MONTHS = "unit_months"
    PATCHES = "patches"


class ThresholdKind(StrEnum):
    RATIO = "ratio"
    ANY_INCREASE = "any_increase"


class CohortKind(StrEnum):
    ALL = "all"
    SW_VERSION = "sw_version"
    HW_REVISION = "hw_revision"
    SITE = "site"
    WARD = "ward"
    LOT = "lot"


class IncidentSource(StrEnum):
    """How much to trust Event Code on an incident row."""

    TELEMETRY = "Telemetry"
    DASHBOARD_ALERT = "Dashboard alert"
    WARD_STAFF = "Ward staff"
    EMAIL = "Email"


class ComplaintStatus(StrEnum):
    OPEN = "Open"
    UNDER_INVESTIGATION = "Under investigation"
    CLOSED = "Closed"
    DECLINED = "Declined"


class SignalStatus(StrEnum):
    OPEN = "Open"
    MONITORING = "Monitoring"
    PROMOTED = "Promoted"
    CLOSED_NO_ACTION = "Closed - no action"


class CAPATrigger(StrEnum):
    RECURRENCE = "Recurrence"
    CROSS_REGISTER = "Cross-register convergence"
    PRIOR_NC_INEFFECTIVE = "Prior NC ineffective"
    SINGLE_SEVERE_NC = "Single severe NC"
    EXTERNAL = "External"


class CAPADecision(StrEnum):
    """Human-only. The agent never writes this field."""

    OPENED = "Opened"
    DECLINED = "Declined"
    DEFERRED = "Deferred"


class CAPAStatus(StrEnum):
    RECOMMENDED = "Recommended"
    OPEN = "Open"
    IMPLEMENTED = "Implemented"
    VERIFYING = "Verifying"
    CLOSED = "Closed"
    DECLINED = "Declined"
    DEFERRED = "Deferred"


class DraftStatus(StrEnum):
    """Lifecycle of a capture draft. It leaves the queue only through a human."""

    PENDING = "Pending"
    ACCEPTED = "Accepted"
    EDITED = "Edited"
    REJECTED = "Rejected"


class HumanVerdict(StrEnum):
    ACCEPTED = "accepted"
    EDITED = "edited"
    REJECTED = "rejected"


class Autonomy(StrEnum):
    """Mirrors agent/autonomy.py. Capture is DRAFT, always."""

    OBSERVE = "1"
    RECOMMEND = "2"
    DRAFT = "3"
    EXECUTE_WITH_APPROVAL = "4"
    AUTOMATIC = "5"
