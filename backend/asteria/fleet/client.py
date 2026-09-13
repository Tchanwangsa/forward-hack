"""Asteria's side of the wire to the fleet service.

The product is a consumer of a device cloud it does not own. That is true in
production and it is true here, so this is an HTTP client and not an import:
everything the product knows about the estate arrives through a route a real
PulseOne cloud would also expose, and nothing reaches into the simulator.

Two things it deliberately will not do:

    It will not call `/v1/sim/scenarios`. That endpoint carries the hidden
    cause. A triage that read it would score 100% and measure nothing.

    It will not write. QMS-WI-011 grants remote access for diagnosis;
    remediation is a human with a change ticket (OPS-SOP-004 §3 C1).

When the service is not running, every call returns None and the caller falls
back to the derived estate. A demo without the simulator still works; it just
works on the frozen twenty months, which is what it always did.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Self

import httpx

FLEET_URL = os.getenv("FLEET_URL", "http://127.0.0.1:8100")
TIMEOUT = 3.0

# The answer key. Named here so that the one place it is legitimate to read —
# the scorer — is explicit, and so that grepping for it finds every caller.
SCENARIOS_PATH = "/v1/sim/scenarios"


@dataclass
class FleetClient:
    """Read-only HTTP against the fleet service. Silent when it is not there."""

    base_url: str = FLEET_URL
    timeout: float = TIMEOUT
    _client: httpx.Client | None = None

    def __post_init__(self) -> None:
        self._client = httpx.Client(base_url=self.base_url, timeout=self.timeout)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def _get(self, path: str, **params) -> dict | None:
        try:
            response = self._client.get(path, params=params)
        except httpx.HTTPError:
            return None
        if response.status_code != 200:
            return None
        return response.json()

    @property
    def available(self) -> bool:
        return self._get("/health") is not None

    # -- the stream --------------------------------------------------------

    def events_since(self, cursor: int, *, limit: int = 500) -> tuple[list[dict], int]:
        """New telemetry. Returns the events and the cursor to ask with next."""
        body = self._get("/v1/telemetry/events", since=cursor, limit=limit)
        if body is None:
            return [], cursor
        return body["events"], body["cursor"]

    # -- the diagnostic surface -------------------------------------------

    def estate_hub(self, hub_id: str) -> dict | None:
        """Power, device and link on one unit. What §5.3, §5.6 and §5.7 read."""
        return self._get(f"/v1/estate/hubs/{hub_id}")

    def estate_site(self, customer_id: str) -> dict | None:
        """Net path and data box. What §5.4 and §5.5 read."""
        return self._get(f"/v1/estate/sites/{customer_id}")

    def occupancy(self, hub_id: str) -> dict | None:
        """Bed occupied at onset: yes or no, and nothing else (§3 C2)."""
        return self._get("/v1/ward/occupancy", hub_id=hub_id)

    def fleet_hub(self, hub_id: str) -> dict | None:
        return self._get(f"/v1/fleet/hubs/{hub_id}")

    def readings(self, hub_id: str, customer_id: str | None) -> dict | None:
        """One round of probes, taken together.

        The eight tools run over one estate at one moment, and taking their
        readings in one pass is both faster and more honest than eight separate
        requests that could each catch the world in a different state — a
        transcript where the socket is dead at §5.3 and live at §5.6 describes
        a fleet that never existed.
        """
        hub = self.estate_hub(hub_id)
        if hub is None:
            return None
        return {
            "hub": hub,
            "site": self.estate_site(customer_id) if customer_id else None,
            "ward": self.occupancy(hub_id),
        }

    # -- scoring only ------------------------------------------------------

    def scenarios(self) -> dict | None:
        """The hidden causes. **Scoring only — never an input to triage.**

        `tests/test_triage.py` asserts that nothing on the triage path calls
        this. If that test ever has to be relaxed, the score stops being a
        measurement of anything.
        """
        return self._get(SCENARIOS_PATH)
