"""sources/meetings/ -> meeting_transcript + transcript_line.

Header block gives the linked Comm ID, date, duration and attendees. The body is
`[HH:MM:SS] Name (Org, Role): text`, with continuation lines indented.

Lines are stored individually because the meeting scribe's provenance is a time
RANGE — tx:TX-2026-0187@00:14:02-00:14:28 — not a whole file.
"""

import json
import re

from sqlalchemy.orm import Session

from asteria.config import settings
from asteria.ingest.common import as_date, clean, record_snapshot
from asteria.models.sources import MeetingTranscript, TranscriptLine

MEETINGS_DIR = settings.mock_company_path / "sources" / "meetings"

LINE_RE = re.compile(r"^\[(\d{2}:\d{2}:\d{2})\]\s+([^(]+?)\s*\(([^,]+?),\s*([^)]+)\):\s*(.*)$")
HEADER_RE = re.compile(r"^(Meeting|Date|Transcript|Duration):\s*(.*)$")


def _parse(text: str) -> tuple[dict, list[dict]]:
    header: dict[str, str] = {}
    lines: list[dict] = []
    body_started = False
    seq = 0

    for raw in text.splitlines():
        if raw.startswith("---"):
            body_started = True
            continue
        if not body_started:
            m = HEADER_RE.match(raw)
            if m:
                header[m.group(1)] = m.group(2).strip()
            continue

        m = LINE_RE.match(raw)
        if m:
            seq += 1
            lines.append(
                {
                    "seq": seq,
                    "at": m.group(1),
                    "speaker": m.group(2).strip(),
                    "speaker_org": m.group(3).strip(),
                    "speaker_role": m.group(4).strip(),
                    "text": m.group(5).strip(),
                }
            )
        elif lines and raw.strip():
            # Continuation of the previous utterance — wrapped in the source file.
            lines[-1]["text"] += " " + raw.strip()

    return header, lines


def load_all(session: Session) -> int:
    attendees_path = MEETINGS_DIR / "attendees.json"
    attendees_by_meeting = json.loads(attendees_path.read_text()).get("meetings", {})

    n = 0
    for path in sorted((MEETINGS_DIR / "transcripts").glob("*.txt")):
        text = path.read_text()
        header, lines = _parse(text)

        meeting = header.get("Meeting", "")
        comm_id = meeting.split(" - ")[0].strip() if " - " in meeting else None
        title = meeting.split(" - ", 1)[1].strip() if " - " in meeting else clean(meeting)
        transcript_id = clean(header.get("Transcript")) or path.stem

        session.add(
            MeetingTranscript(
                transcript_id=transcript_id,
                comm_id=comm_id,
                title=title,
                meeting_date=as_date(header.get("Date")),
                duration=clean(header.get("Duration")),
                attendees=attendees_by_meeting.get(comm_id, {}).get("attendees"),
                body=text,
            )
        )
        for line in lines:
            session.add(TranscriptLine(transcript_id=transcript_id, **line))
        n += 1

    record_snapshot(session, attendees_path, n, notes="transcripts + attendees")
    return n
