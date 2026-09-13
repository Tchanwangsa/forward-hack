"""Bot 3 — transcripts -> PM-Client-Communications-Log, Channel = Meeting.

Demos live and needs no integration story. Provenance is the timestamp range.
"""

from asteria.capture.primitive import CaptureBot


class MeetingScribe(CaptureBot):
    name = "meeting-scribe"
    source = "meetings"
    target_register = "communication"
