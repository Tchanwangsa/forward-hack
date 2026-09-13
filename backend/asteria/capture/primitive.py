"""The capture primitive. One shape, five instances.

    observe -> resolve -> classify -> draft the row -> human confirms -> committed

Four rules hold for all five (ARCHITECTURE.md §The capture primitive):

1. A bot never commits a row. It drafts; a human accepts, edits or rejects,
   and the verdict is logged.
2. A bot fills only the fields its source actually evidences. Unknown stays
   blank — never a guess.
3. The raw artifact is the provenance. Every drafted row points back to the
   message-ID, transcript range, telemetry event ID, work order or round.
4. Capture never edits an existing human row. It proposes a CompletionSuggestion
   and the original stands as written.

Capture is autonomy level 3, always. No promotion to level 5, ever.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from datetime import date, datetime
from decimal import Decimal

from asteria.agent.autonomy import Autonomy


@dataclass
class Field:
    """One drafted cell, and the thing in the artifact that evidences it.

    `evidence` is not decoration. A field the bot cannot point at should not
    have been filled (DASHBOARD.md §The artifact pane), so this is required and
    the queue renders it on hover.
    """

    name: str
    value: object
    evidence: str
    confidence: Decimal | None = None
    existing: object = None  # the human's value, on a completion


@dataclass
class Drafted:
    """One queue item. Three kinds, reviewed differently (DASHBOARD.md §Screen 1).

    new_row     is this a real event, and is the row right?
    completion  is this the right value for a cell a human left blank?
    question    the bot is not confident enough to draft — it is asking
    """

    kind: str
    artifact_ref: str
    fields: list[Field]
    blanks: dict[str, str] = dc_field(default_factory=dict)
    target_row_key: str | None = None
    event_code: str | None = None
    evidence_code: str | None = None
    confidence: Decimal | None = None
    rationale: str | None = None
    evidence_ids: list[str] = dc_field(default_factory=list)

    def payload(self) -> dict:
        """The drafted row as column -> value. Only what the source evidences.

        `blanks` travels with it so the screen can render `Assigned To — not
        evidenced by this source` rather than an empty cell a reviewer reads as
        an omission and helpfully fills in.
        """
        return {
            "fields": {f.name: _jsonable(f.value) for f in self.fields},
            "blank_by_design": self.blanks,
            "evidence": [f.evidence for f in self.fields],
            "events": self.evidence_ids,
        }


@dataclass
class CaptureOutput:
    """What one run produced, before a human has looked at any of it."""

    bot: str
    items: list[Drafted] = dc_field(default_factory=list)
    episodes_seen: int = 0
    # (artifact_ref, why) for artifacts deliberately not drafted. A skip with a
    # reason is a result; a silent drop is a bug nobody finds until the rate is
    # wrong.
    skipped: list[tuple[str, str]] = dc_field(default_factory=list)

    def add(self, item: Drafted | None) -> None:
        if item is None:
            return
        if item.kind == "completion" and not item.fields:
            return  # the human row was already complete and agreed with the stream
        self.items.append(item)

    def of_kind(self, kind: str) -> list[Drafted]:
        return [i for i in self.items if i.kind == kind]

    def summary(self) -> dict:
        return {
            "new_rows": len(self.of_kind("new_row")),
            "questions": len(self.of_kind("question")),
            "completions": sum(len(i.fields) for i in self.of_kind("completion")),
            "contradictions": sum(
                1 for i in self.of_kind("completion") for f in i.fields if f.existing is not None
            ),
            "episodes_seen": self.episodes_seen,
            "skipped": len(self.skipped),
        }


class CaptureBot:
    """Subclass per source. Each stage is overridable; the sequence is not."""

    name: str
    source: str
    target_register: str
    autonomy: Autonomy = Autonomy.DRAFT

    def observe(self):
        """Pull unprocessed artifacts from this bot's source."""
        raise NotImplementedError

    def resolve(self, artifact):
        """Hub, organisation, lot, ward. Delegates to asteria.resolve.entities."""
        raise NotImplementedError

    def classify(self, artifact, resolved):
        """Which of the seven indicators, or none."""
        raise NotImplementedError

    def draft(self, artifact, resolved, classification):
        """A CaptureDraft, or a CompletionSuggestion against an existing human row."""
        raise NotImplementedError

    def run(self):
        """observe -> resolve -> classify -> draft. Stops at the queue. Always."""
        raise NotImplementedError


def _jsonable(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value
