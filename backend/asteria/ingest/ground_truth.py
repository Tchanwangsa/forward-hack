"""mock-company/ground-truth/*.csv -> the `ground_truth` Postgres schema.

Deliberately NOT ORM models. Ground truth lives in its own schema, outside
Base.metadata, so no capture bot can reach it through the application's models —
if a bot can see the answers, the 53% number means nothing.

Read only by asteria.capture.scorecard.

What is in here:
    events.csv            369 indicator events that actually happened
    capture-targets.csv   3,463 field-level targets: what a bot should recover
    *-links.csv           which register row corresponds to which world event
    episodes.csv          raw telemetry clustered into world events
    sw-timeline.csv       the true SW version per hub over time
"""

import pandas as pd
from sqlalchemy import text

from asteria.config import settings
from asteria.db import engine

GROUND_TRUTH_DIR = settings.mock_company_path / "ground-truth"
SCHEMA = "ground_truth"


def load_all() -> dict[str, int]:
    """Table name is the filename with dashes as underscores: capture-targets.csv
    becomes ground_truth.capture_targets.
    """
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))

    counts: dict[str, int] = {}
    for path in sorted(GROUND_TRUTH_DIR.glob("*.csv")):
        table = path.stem.replace("-", "_")
        df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=[""])
        df.to_sql(table, engine, schema=SCHEMA, if_exists="replace", index=False)
        counts[table] = len(df)
    return counts
