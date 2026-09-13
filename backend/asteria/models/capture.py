"""The capture layer — what tier 1 writes before a human confirms anything.

CaptureDraft            a proposed new register row, with per-field provenance
CompletionSuggestion    a proposed fill for a blank field on an existing human row;
                        the original row is never edited (ARCHITECTURE.md, rule 4)
ReviewVerdict           accept | edit | reject, a named reviewer, a rationale
SourceSnapshot          a versioned import of a customer .xlsx; source rows are
                        never overwritten
"""

# TODO: CaptureDraft, DraftField, CompletionSuggestion, ReviewVerdict, SourceSnapshot
