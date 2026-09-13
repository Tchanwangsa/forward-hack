"""Screen 1 — capture queue. Ship this one if you ship one screen.

    GET  /api/capture/drafts            the queue: pending drafts + completions
    GET  /api/capture/drafts/{id}       the draft, its fields, and the raw artifact
    POST /api/capture/drafts/{id}/accept
    POST /api/capture/drafts/{id}/edit
    POST /api/capture/drafts/{id}/reject    rationale required
    GET  /api/capture/scorecard         coverage, field completeness, accept rate
"""

from fastapi import APIRouter

router = APIRouter()
