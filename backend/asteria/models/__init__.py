"""The eleven registers plus the capture layer. See ../../plan/REGISTERS.md §The map.

    reference.py     1  Customer Organisations and Hubs   7  PMS Plan and Report
    capture_fed.py   2  Incident and Outage   3  Returns and Replacements
                     4  Data Check and Troubleshooting   5  Client Communications
                     6  Complaint
    system.py        8  Signal   9  Product NC   10  CAPA   11  Agent Action Log
    capture.py       drafts, completion suggestions, review verdicts, snapshots
"""

from asteria.models.base import Base, TimestampMixin

__all__ = ["Base", "TimestampMixin"]
