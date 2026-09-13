"""Bot 1 — telemetry -> PM-Incident-and-Outage-Log. Build this first.

The strongest single demo: it creates rows that do not exist (62 events, 17%,
were never written up) and fills `SW Version at Time` on rows that do (35% blank).

The planted story lives here: of the fifteen ALERT-FALSE events on SW 1.1.0 in
the live window, two carry a correct SW version in the human register. Tier 2
cannot find that cohort until this bot has run.
"""

from asteria.capture.primitive import CaptureBot


class OutageWatch(CaptureBot):
    name = "outage-watch"
    source = "telemetry"
    target_register = "incident"
