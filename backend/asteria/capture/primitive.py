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


class CaptureBot:
    """Subclass per source. Each stage is overridable; the sequence is not."""

    name: str
    source: str
    target_register: str

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
