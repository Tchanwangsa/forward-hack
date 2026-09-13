"""Simulated time.

The fleet runs on a clock that is real time multiplied. Everything in the
simulator asks the clock for `now`, and nothing calls `datetime.now()` — which
is what makes a demo at 60x and a test at 0x the same code path, and what
TELEMETRY-API.md §4 means by "the accelerated clock is a demo setting, not a
second code path".

A `speed` of 60 means one wall-clock second is one simulated minute: a shift
passes in eight minutes and a data box backlog is watchable. `speed` of 0
freezes the clock, and `advance()` steps it by hand — the shape every test uses.
"""

from __future__ import annotations

import time
from datetime import UTC, datetime, timedelta


class Clock:
    """Wall time, multiplied, with an origin you choose."""

    def __init__(self, *, origin: datetime | None = None, speed: float = 60.0) -> None:
        self.origin = (origin or datetime.now(UTC)).astimezone(UTC)
        self.speed = speed
        self._started = time.monotonic()
        self._frozen_offset = timedelta(0)

    def now(self) -> datetime:
        if self.speed == 0:
            return self.origin + self._frozen_offset
        return self.origin + timedelta(seconds=(time.monotonic() - self._started) * self.speed)

    def advance(self, seconds: float) -> datetime:
        """Step a frozen clock. Simulated seconds, not wall seconds."""
        self._frozen_offset += timedelta(seconds=seconds)
        return self.now()

    @property
    def sim_seconds_per_tick(self) -> float:
        return self.speed

    def describe(self) -> dict:
        return {
            "origin": self.origin.isoformat(),
            "now": self.now().isoformat(),
            "speed": self.speed,
            "frozen": self.speed == 0,
        }
