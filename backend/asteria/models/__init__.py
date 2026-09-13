"""The eleven registers plus the capture layer. See ../../plan/REGISTERS.md §The map.

    reference     1  Customer Organisations and Hubs   7  PMS Plan and Report
    capture_fed   2  Incident   3  Returns   4  Data Check   5  Comms   6  Complaint
    system        8  Signal   9  Product NC   10  CAPA   11  Agent Action Log
    capture       drafts, completion suggestions, review verdicts, snapshots
    triage        the SOP runs behind a diagnosis, step by step
    sources       the raw upstream artifacts tier 1 watches (not registers)
"""

from asteria.models.base import Base, CaptureColumnsMixin, TimestampMixin
from asteria.models.capture import (
    CaptureDraft,
    CompletionSuggestion,
    DraftField,
    ReviewVerdict,
    SourceSnapshot,
)
from asteria.models.capture_fed import (
    Communication,
    Complaint,
    DataCheck,
    Incident,
    ProductReturn,
)
from asteria.models.reference import (
    ControlledDocument,
    CustomerOrganisation,
    Hub,
    Indicator,
    PatchLotAllocation,
    PMSReviewMeeting,
)
from asteria.models.sources import (
    EmailMessage,
    MeetingTranscript,
    PartReplaced,
    RoundBed,
    TechnicianNote,
    TelemetryEvent,
    TelemetryHeartbeat,
    TranscriptLine,
    WardRound,
    WorkOrder,
)
from asteria.models.system import CAPA, AgentAction, ProductNC, Signal
from asteria.models.triage import TriageRun, TriageStep

__all__ = [
    "Base",
    "TimestampMixin",
    "CaptureColumnsMixin",
    # reference
    "CustomerOrganisation",
    "Hub",
    "PatchLotAllocation",
    "Indicator",
    "ControlledDocument",
    "PMSReviewMeeting",
    # capture-fed
    "Incident",
    "ProductReturn",
    "DataCheck",
    "Communication",
    "Complaint",
    # system
    "Signal",
    "ProductNC",
    "CAPA",
    "AgentAction",
    # raw upstream artifacts
    "TelemetryEvent",
    "TelemetryHeartbeat",
    "EmailMessage",
    "MeetingTranscript",
    "TranscriptLine",
    "WorkOrder",
    "TechnicianNote",
    "PartReplaced",
    "WardRound",
    "RoundBed",
    # capture layer
    "SourceSnapshot",
    "CaptureDraft",
    "DraftField",
    "CompletionSuggestion",
    "ReviewVerdict",
    # triage
    "TriageRun",
    "TriageStep",
]
