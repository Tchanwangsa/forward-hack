"""Telemetry is chatty. The register wants incidents, not packets.

A hub that flaps offline eleven times in six days is *one* incident, and the
near-miss story in this dataset is exactly that shape: ten HUB-OFFLINE events at
Ashfield Private inside six days, all explained by a hospital network cutover.
A bot that turns a network maintenance window into ten separate incident rows
has made the register worse, not better (CAPTURE-AGENTS.md §1).

So the stream is reduced in three steps before anything is drafted:

    replays   a reconnecting hub replays its buffer. Same dedupe_key = same
              event, arriving twice. Dropped, not counted twice — a replayed
              buffer counted five times is a fabricated signal.
    episodes  one hub, one code, events within EPISODE_GAP of each other.
              One episode, one drafted row, every raw event kept as evidence.
    clusters  several hubs at one site, same code, same few days. Not merged —
              each hub keeps its own row — but every row carries the
              co-occurrence in its Notes, so tier 2 can close the lot as
              no-action honestly rather than reading ten unrelated faults.

Pure functions over telemetry rows. No database writes, no model calls.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from asteria.models.sources import TelemetryEvent

# Same hub, same code, within this of the previous event: the same episode.
# In this dataset the largest gap inside a true episode is 12.7 hours and the
# smallest gap between two true episodes on one hub is 98 hours, so anything
# from ~13h to ~4d separates them identically. 24h is the round number in the
# middle, and it is the shift boundary a ward would recognise.
EPISODE_GAP = timedelta(hours=24)

# Several hubs at one customer, same code, each within this of the next: one
# site-wide disturbance. 72h spans a weekend, which is how long a hospital
# network cutover takes to finish annoying everybody.
CLUSTER_GAP = timedelta(hours=72)

# Below this many distinct hubs it is a coincidence, not a site event.
CLUSTER_MIN_HUBS = 3


@dataclass
class Episode:
    """One incident as the world had it, however many packets it arrived in."""

    hub_id: str
    code: str
    events: list[TelemetryEvent]
    replays_dropped: list[TelemetryEvent] = field(default_factory=list)
    cluster: SiteCluster | None = None

    @property
    def primary(self) -> TelemetryEvent:
        """The event that opened it. Its ID is the episode's provenance."""
        return self.events[0]

    @property
    def last(self) -> TelemetryEvent:
        return self.events[-1]

    @property
    def artifact_ref(self) -> str:
        return f"tel:{self.primary.event_id}"

    @property
    def event_ids(self) -> list[str]:
        return [e.event_id for e in self.events]

    @property
    def opened_at(self) -> datetime:
        return self.primary.ts_device or self.primary.ts_received

    @property
    def closed_at(self) -> datetime:
        return self.last.ts_device or self.last.ts_received

    @property
    def repeats(self) -> int:
        """Events after the first. Eleven flaps is one incident and ten repeats."""
        return len(self.events) - 1

    @property
    def span_hours(self) -> float:
        return (self.closed_at - self.opened_at).total_seconds() / 3600

    def payload_value(self, key: str):
        """First non-null value for a payload key across the episode."""
        for e in self.events:
            if e.payload and e.payload.get(key) is not None:
                return e.payload[key]
        return None


@dataclass
class SiteCluster:
    """Same customer, same code, same few days, three or more hubs.

    Evidence, not a merge. Ten hubs offline at one hospital is ten rows and one
    explanation, and the explanation belongs on every one of them.
    """

    customer_id: str
    code: str
    episodes: list[Episode]

    @property
    def hub_ids(self) -> list[str]:
        return sorted({e.hub_id for e in self.episodes})

    @property
    def opened_at(self) -> datetime:
        return min(e.opened_at for e in self.episodes)

    @property
    def closed_at(self) -> datetime:
        return max(e.closed_at for e in self.episodes)

    @property
    def span_days(self) -> int:
        return (self.closed_at.date() - self.opened_at.date()).days + 1

    @property
    def ward_wide(self) -> bool:
        """The hubs' own judgement, where the code carries one.

        HUB-OFFLINE is raised cloud-side and its payload says whether the whole
        site went with it — a fact the platform knows and the spreadsheet never
        records.
        """
        return any(e.payload_value("ward_wide") for e in self.episodes)

    def note(self) -> str:
        """The sentence that goes in Notes on every row in the cluster."""
        return (
            f"{len(self.hub_ids)} hubs at this site raised {self.code} within "
            f"{self.span_days} days — {len(self.episodes)} episodes, "
            f"{sum(len(e.events) for e in self.episodes)} events "
            f"({', '.join(self.hub_ids)})"
            + (", reported site-wide by the platform" if self.ward_wide else "")
            + ". Site-wide cause to rule out before treating these as unit faults."
        )


def drop_replays(events: list[TelemetryEvent]) -> tuple[list[TelemetryEvent], dict[str, list]]:
    """Idempotency on (hub, ts, code), which is what dedupe_key encodes.

    Returns the surviving events and, per survivor, the replays it absorbed —
    kept as evidence so the queue can show that the drop happened rather than
    quietly losing rows.
    """
    seen: dict[str, TelemetryEvent] = {}
    replays: dict[str, list[TelemetryEvent]] = defaultdict(list)
    kept: list[TelemetryEvent] = []
    for e in sorted(events, key=_received):
        key = e.dedupe_key or f"{e.hub_id}:{e.code}:{e.ts_device}"
        if key in seen:
            replays[seen[key].event_id].append(e)
            continue
        seen[key] = e
        kept.append(e)
    return kept, dict(replays)


def to_episodes(events: list[TelemetryEvent]) -> list[Episode]:
    """Group one hub's run of one code into episodes. Chronological."""
    kept, replays = drop_replays(events)
    by_hub_code: dict[tuple[str, str], list[TelemetryEvent]] = defaultdict(list)
    for e in kept:
        by_hub_code[(e.hub_id, e.code)].append(e)

    episodes: list[Episode] = []
    for (hub_id, code), run in by_hub_code.items():
        run.sort(key=_received)
        current = [run[0]]
        for e in run[1:]:
            if _received(e) - _received(current[-1]) <= EPISODE_GAP:
                current.append(e)
            else:
                episodes.append(_episode(hub_id, code, current, replays))
                current = [e]
        episodes.append(_episode(hub_id, code, current, replays))

    episodes.sort(key=lambda ep: _received(ep.primary))
    return episodes


def find_clusters(episodes: list[Episode]) -> list[SiteCluster]:
    """Site-wide co-occurrence. Sets episode.cluster on the members."""
    by_site: dict[tuple[str, str], list[Episode]] = defaultdict(list)
    for ep in episodes:
        customer_id = ep.primary.customer_id
        if customer_id:
            by_site[(customer_id, ep.code)].append(ep)

    clusters: list[SiteCluster] = []
    for (customer_id, code), eps in by_site.items():
        eps.sort(key=lambda ep: ep.opened_at)
        run = [eps[0]]
        for ep in eps[1:]:
            if ep.opened_at - max(e.closed_at for e in run) <= CLUSTER_GAP:
                run.append(ep)
            else:
                clusters.append(_cluster(customer_id, code, run))
                run = [ep]
        clusters.append(_cluster(customer_id, code, run))

    real = [c for c in clusters if c and len({e.hub_id for e in c.episodes}) >= CLUSTER_MIN_HUBS]
    for cluster in real:
        for ep in cluster.episodes:
            ep.cluster = cluster
    return real


def _episode(hub_id, code, events, replays) -> Episode:
    dropped = [r for e in events for r in replays.get(e.event_id, [])]
    return Episode(hub_id=hub_id, code=code, events=list(events), replays_dropped=dropped)


def _cluster(customer_id, code, episodes) -> SiteCluster | None:
    if len(episodes) < CLUSTER_MIN_HUBS:
        return None
    return SiteCluster(customer_id=customer_id, code=code, episodes=list(episodes))


def _received(e: TelemetryEvent) -> datetime:
    return e.ts_received or e.ts_device
