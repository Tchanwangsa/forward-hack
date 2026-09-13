"""Bot 2 — mailboxes -> PM-Client-Communications-Log + a complaint recommendation.

Two outputs. The comms row is an ordinary draft. The complaint recommendation is
the first genuinely interesting human gate: the bot recommends, a human decides,
and a declined complaint is a permanent record with a named reviewer.
"""

from asteria.capture.primitive import CaptureBot


class InboxTriage(CaptureBot):
    name = "inbox-triage"
    source = "mail"
    target_register = "communication"
