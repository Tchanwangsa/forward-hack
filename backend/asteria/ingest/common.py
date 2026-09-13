"""Shared ingest helpers.

The rule for all of them: preserve the mess. A value that is blank in the source
stays None here; a serial written 'SN 4216' stays 'SN 4216'. Normalisation
happens in asteria.resolve, into separate resolved_* columns, never in place.
"""

import hashlib
from datetime import date, datetime
from pathlib import Path
from typing import Any

from dateutil import parser as dateparser
from sqlalchemy.orm import Session

from asteria.models.capture import SourceSnapshot


def clean(v: Any) -> str | None:
    """Blank stays blank. Trailing whitespace in the source is stripped for the
    *value*; the fact that it was there is not information anyone needs.
    """
    if v is None:
        return None
    s = str(v).strip()
    return s or None


def as_date(v: Any) -> date | None:
    """The registers carry two date formats, and openpyxl hands back datetimes
    for some cells and strings for others. Both are accepted; neither is trusted.
    """
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    try:
        return dateparser.parse(str(v).strip(), dayfirst=True).date()
    except (ValueError, OverflowError):
        return None


def as_dt(v: Any) -> datetime | None:
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v
    try:
        return dateparser.parse(str(v).strip())
    except (ValueError, OverflowError):
        return None


def as_int(v: Any) -> int | None:
    s = clean(v)
    if s is None:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def as_decimal(v: Any) -> float | None:
    s = clean(v)
    if s is None:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def as_bool(v: Any) -> bool | None:
    """The registers write Y/N, not true/false. Blank is genuinely unknown —
    on `Vigilance screen required (Y/N)` the difference matters.
    """
    s = clean(v)
    if s is None:
        return None
    return s.upper() in {"Y", "YES", "TRUE", "1"}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def record_snapshot(session: Session, path: Path, row_count: int, notes: str = "") -> SourceSnapshot:
    """Every import is retained as a versioned snapshot; source rows are never
    overwritten (ARCHITECTURE.md §Runtime and storage).
    """
    snap = SourceSnapshot(
        filename=path.name, sha256=sha256_of(path), row_count=row_count, notes=notes or None
    )
    session.add(snap)
    return snap


def sheet_rows(ws) -> list[dict[str, Any]]:
    """Header row -> list of dicts, keyed by the workbook's own column names."""
    rows = ws.iter_rows(values_only=True)
    header = [clean(h) for h in next(rows)]
    return [dict(zip(header, r)) for r in rows if any(c is not None for c in r)]
