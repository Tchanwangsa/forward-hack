"""Integration test — needs an ingested database (`make ingest`).

Guards the headline. If ingest silently changes shape, this fails loudly rather
than the demo quietly quoting a wrong number.
"""

import pytest
from sqlalchemy import text

from asteria.capture.scorecard import baseline
from asteria.db import SessionLocal


@pytest.fixture
def session():
    with SessionLocal() as s:
        if not s.execute(text("SELECT count(*) FROM incident")).scalar():
            pytest.skip("database not ingested — run `make ingest`")
        yield s


def test_baseline_matches_the_pitch(session):
    b = baseline(session)
    assert b.events_happened == 369
    assert b.events_logged == 307
    assert b.correctly_coded == 197
    assert b.never_written_up == 62
    assert round(b.identified_pct) == 53
