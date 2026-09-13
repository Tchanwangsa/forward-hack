"""Asteria — PMS capture, analysis and CAPA tiers.

See ../../plan/ARCHITECTURE.md for the spine. Package layout mirrors the tiers:

    ingest/    raw artifacts and customer registers -> database
    resolve/   entity resolution plumbing (never a screen)
    capture/   tier 1 — five bots, one primitive
    analysis/  tier 2 — indicator engine, five workflows, Product NC
    capa/      tier 3 — recurrence and cross-register overlap
    api/       the HTTP surface the dashboard talks to
"""

__version__ = "0.1.0"
