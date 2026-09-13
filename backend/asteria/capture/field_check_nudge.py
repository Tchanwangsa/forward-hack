"""Bot 5 — ward rounds -> PM-Data-Check-and-Troubleshooting-Log. Stub.

Recovers Action Taken (66% blank — often stated in the round and lost on the way
to the spreadsheet) and Patch Lot (51% blank — resolvable from lot allocation).
"""

from asteria.capture.primitive import CaptureBot


class FieldCheckNudge(CaptureBot):
    name = "field-check-nudge"
    source = "ward-rounds"
    target_register = "data_check"
