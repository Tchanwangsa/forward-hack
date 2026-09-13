"""Bot 1 — telemetry -> PM-Incident-and-Outage-Log. Build this first.

The strongest single demo: it creates rows that do not exist (62 events, 17%,
were never written up) and fills `SW Version at Time` on rows that do (35% blank).

The planted story lives here: of the fifteen ALERT-FALSE events on SW 1.1.0 in
the live window, two carry a correct SW version in the human register. Tier 2
cannot find that cohort until this bot has run.

    observe    the telemetry event stream, reduced to episodes (episodes.py)
    resolve    hub -> organisation, ward, bed, pairing, canonical serial
    classify   nothing to do. The event's code IS the indicator code — except
               for ADHESIVE, which is an inference and is asked, not asserted.
    draft      an episode with no incident row becomes a drafted row; an episode
               with one becomes completions for the cells it can evidence.

What it must never do, both of them tested:

    SKIN has no telemetry path. A patch cannot detect a rash. Zero SKIN rows may
    carry Source = Telemetry; emitting one means the bot invented an event.

    Reported By and Assigned To stay blank. A telemetry event has no reporter,
    and triage is a human act. Filling either to make a row look complete is the
    failure mode that discredits the tier.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from asteria.agent.action_log import log_action
from asteria.agent.autonomy import Autonomy
from asteria.capture.episodes import Episode, find_clusters, to_episodes
from asteria.capture.primitive import CaptureBot, CaptureOutput, Drafted, Field
from asteria.models.capture import CaptureDraft, CompletionSuggestion, DraftField
from asteria.models.capture_fed import Incident
from asteria.models.enums import DraftStatus, IncidentSource
from asteria.models.sources import TelemetryEvent
from asteria.resolve.entities import Resolver

# The five the hub knows outright. Drafted as confident rows.
CONFIDENT_CODES = frozenset({"CONN-LINK-LOSS", "HUB-OFFLINE", "BATT", "ALERT-FALSE", "DISPLAY"})

# The stream carries it, but only as a signal-loss pattern *consistent with*
# detachment — an inference about a piece of tape, made by a radio. Raised as a
# question for someone who can look at the patient, never as a classification.
INFERRED_CODES = frozenset({"ADHESIVE"})

# No device emits it, and if one does we have a bug upstream, not an incident.
NEVER_FROM_TELEMETRY = frozenset({"SKIN"})

CONFIDENT = Decimal("0.99")
INFERRED = Decimal("0.35")  # below the queue's question threshold, deliberately

# A human writes the row up to a week after the event: median 0 days, p90 5,
# max 6 in this dataset. A day either side of that is the matching window; the
# three rows in the register that sit 122, 149 and 239 days after their event
# are not matchable by any honest rule and are left to arrive as new drafts.
MATCH_WINDOW_BEFORE = timedelta(days=1)
MATCH_WINDOW_AFTER = timedelta(days=7)

# The register's own column names, which are what the reviewer sees and what
# ground-truth scoring keys on. The database attribute is on the right.
FIELD_COLUMNS = {
    "Pairing ID": "pairing_id",
    "Pairing Status": "pairing_status",
    "Organisation": "organisation_as_written",
    "HubID": "hub_id",
    "Serial Number": "serial_number_as_written",
    "WardID": "ward_id",
    "BedID": "bed_id",
    "Last Online": "last_online",
    "Offline Duration (hrs)": "offline_duration_hrs",
    "Reported Date": "reported_date",
    "Incident Description": "incident_description",
    "Status": "status",
    "SW Version at Time": "sw_version_at_time",
    "Notes": "notes",
    "Event Code": "event_code",
    "Source": "source",
}

# Fields this source does not evidence, stated rather than omitted so the queue
# can render them as deliberate blanks (DASHBOARD.md §The artifact pane).
NOT_EVIDENCED = {
    "Reported By": "a telemetry event has no reporter",
    "Assigned To": "triage is a human act",
    "Date of Last Email Sent": "not this bot's business",
}

# What the register's own prose calls each code. Drafted descriptions are
# written in the register's vocabulary, not the API's, because a reviewer
# scanning the log should not be able to tell which rows a machine wrote.
DESCRIPTIONS = {
    "CONN-LINK-LOSS": "Patch to hub link lost during session",
    "HUB-OFFLINE": "Hub not reporting to dashboard",
    "BATT": "Battery outside specification",
    "ALERT-FALSE": "Alert raised and dismissed as inappropriate",
    "DISPLAY": "Display or power-on self-test fault",
    "ADHESIVE": "Signal loss consistent with patch detachment",
}

# Used only to break a tie between two candidate rows on the same hub in the
# same week. It corroborates a match; it never makes a classification — the
# code does that, and the code came off the device.
DESCRIPTION_HINTS = {
    "CONN-LINK-LOSS": ("link", "pairing", "dropout", "dropping", "connection", "e-207", "detected"),
    "HUB-OFFLINE": ("offline", "outage", "not reporting", "dashboard", "network", "missing"),
    "BATT": ("battery", "charge", "flat", "powered down", "dock"),
    "ALERT-FALSE": ("alert", "alarm", "false", "misclassified", "unoccupied", "no patient"),
    "DISPLAY": ("display", "screen", "blank", "flicker", "cracked"),
    "ADHESIVE": ("adhesive", "patch detached", "lifting", "adhering", "stay on", "wear"),
}


@dataclass
class Match:
    """An episode and the human row that already covers it, if there is one."""

    episode: Episode
    incident: Incident | None
    why: str | None = None


class OutageWatch(CaptureBot):
    name = "outage-watch"
    source = "telemetry"
    target_register = "incident"
    autonomy = Autonomy.DRAFT

    def __init__(self, session: Session, *, since: datetime | None = None) -> None:
        self.session = session
        self.resolver = Resolver(session)
        self.since = since

    # -- observe ---------------------------------------------------------

    def observe(self) -> list[Episode]:
        """Every telemetry event, reduced to episodes and site clusters.

        Reading the whole stream each run is deliberate: the run is idempotent
        on (bot, artifact_ref), so a re-run adds what is new and re-proposes
        nothing that was already reviewed.
        """
        # A live run scopes to what has arrived since the loop started. The
        # frozen twenty months are already drafted and re-reducing them every
        # few seconds would be 35,000 rows of work to reach the same answer.
        query = select(TelemetryEvent)
        if self.since is not None:
            query = query.where(TelemetryEvent.ts_received >= self.since)
        events = list(self.session.execute(query).scalars())
        episodes = to_episodes(events)
        find_clusters(episodes)
        return episodes

    # -- resolve ---------------------------------------------------------

    def resolve(self, episode: Episode):
        """Hub -> organisation, ward, bed, pairing, canonical serial.

        The event carries a ward and bed too, but the inventory is the roster of
        record for where a unit is, so the inventory wins and the event fills
        the gaps.
        """
        return self.resolver.hub(episode.hub_id)

    # -- classify --------------------------------------------------------

    def classify(self, episode: Episode, resolved) -> tuple[str | None, Decimal, str]:
        """The hinge: a hub emitting CONN-LINK-LOSS has classified itself.

        Returns (code, confidence, rationale). A code of None is the bot saying
        it will not assert one — the queue renders that as a question.
        """
        code = episode.code
        if code in NEVER_FROM_TELEMETRY:
            raise InventedEvent(f"{code} has no telemetry path — {episode.primary.event_id}")
        if code in INFERRED_CODES:
            lot = episode.payload_value("patch_lot")
            wear = episode.payload_value("wear_time_h")
            return (
                None,
                INFERRED,
                f"The stream reports {code} on {episode.hub_id}, but a hub infers detachment "
                f"from a signal-loss pattern — it cannot see the patch"
                + (f" (lot {lot}" if lot else "")
                + (f", {wear}h wear time)" if wear and lot else ")" if lot else "")
                + ". Confirm against the ward before this is coded IND-05: "
                "a detachment, a skin reaction and a flat battery look alike from here.",
            )
        return (
            code,
            CONFIDENT,
            (
                f"The hub reported {code} itself. The telemetry code is the indicator's "
                f"internal code, so this is a reading rather than a judgement."
            ),
        )

    # -- draft -----------------------------------------------------------

    def draft(self, episode: Episode, resolved, classification) -> Drafted:
        """A new row, or completions against the row a human already wrote."""
        code, confidence, rationale = classification
        incident = self.match(episode)
        if incident is None:
            return self.draft_new_row(episode, resolved, code, confidence, rationale)
        return self.draft_completions(episode, resolved, incident, code, confidence)

    def match(self, episode: Episode) -> Incident | None:
        """Does a human row already cover this episode?

        Same hub, reported within the window, and — only to choose between two
        candidates — a description that reads like the code. Each row is claimed
        at most once, so a hub with two faults in a week gets two rows and not
        two drafts against one.
        """
        day = episode.opened_at.date()
        candidates = [
            i
            for i in self._incidents_by_hub().get(episode.hub_id, [])
            if i.incident_id not in self._claimed
            and i.reported_date
            and day - MATCH_WINDOW_BEFORE <= i.reported_date <= day + MATCH_WINDOW_AFTER
        ]
        if not candidates:
            return None
        candidates.sort(
            key=lambda i: (self._match_rank(i, episode.code), abs((i.reported_date - day).days))
        )
        best = candidates[0]
        self._claimed.add(best.incident_id)
        return best

    def _match_rank(self, incident: Incident, code: str) -> int:
        """0 the row already names this code · 1 blank code, description agrees ·
        2 blank code, description silent · 3 the row names a different code.

        Rank 3 still matches. A miscoded row is the same incident written up
        wrongly — 9% of coded rows carry the wrong code — and the honest output
        there is a contradiction on Event Code, not a second row for the same
        fault. Drafting a duplicate to avoid disagreeing with a human is the
        cowardly failure and the one that inflates every count downstream.
        """
        if incident.event_code == code:
            return 0
        if incident.event_code is None:
            text = (incident.incident_description or "").lower()
            hints = DESCRIPTION_HINTS.get(code, ())
            return 1 if any(h in text for h in hints) else 2
        return 3

    def draft_new_row(self, episode, hub, code, confidence, rationale) -> Drafted:
        """A row that does not exist. 44 of these are the product's headline.

        `Incident/Outage ID` is not drafted: a pending draft is not a row, and
        an ID allocated now would leave a hole in the sequence the moment a
        reviewer rejects it. It is assigned on accept.
        """
        primary = episode.primary
        event_day = episode.opened_at.date()
        fields: list[Field] = [
            Field("HubID", episode.hub_id, f"tel:{primary.event_id} hub_id"),
            Field(
                "Serial Number",
                self.resolver.canonical_serial(episode.hub_id) or primary.serial,
                f"inv:{episode.hub_id} — canonical serial for this hub",
            ),
            Field("Organisation", hub.organisation if hub else None, f"inv:{episode.hub_id}"),
            Field(
                "WardID",
                (hub.ward_id if hub else None) or primary.ward_id,
                f"tel:{primary.event_id} ward_id",
            ),
            Field(
                "BedID", (hub.bed_id if hub else None) or primary.bed_id, f"inv:{episode.hub_id}"
            ),
            Field("Pairing ID", hub.pairing_id if hub else None, f"inv:{episode.hub_id}"),
            Field("Pairing Status", hub.pairing_status if hub else None, f"inv:{episode.hub_id}"),
            Field(
                "Reported Date",
                event_day,
                f"tel:{primary.event_id} ts_device — the day it happened",
            ),
            Field(
                "Last Online",
                episode.closed_at,
                f"tel:{episode.last.event_id} — the event's own last online, not the inventory snapshot",
            ),
            Field(
                "SW Version at Time",
                primary.sw_version,
                f"tel:{primary.event_id} sw_version — reported by the hub at the moment of the fault",
            ),
            Field(
                "Incident Description",
                self._description(episode),
                f"tel:{primary.event_id} code + payload",
            ),
            Field("Status", "Open", "drafted rows open"),
            Field("Source", IncidentSource.TELEMETRY.value, "read from the event stream"),
        ]
        duration = self._offline_hours(episode)
        if duration is not None:
            fields.append(
                Field("Offline Duration (hrs)", duration, self._duration_evidence(episode))
            )
        notes = self._notes(episode)
        if notes:
            fields.append(Field("Notes", notes, f"{len(episode.events)} events in this episode"))
        if code:
            fields.append(
                Field(
                    "Event Code",
                    code,
                    f"tel:{primary.event_id} code — the hub's own classification",
                    CONFIDENT,
                )
            )

        return Drafted(
            kind="question" if code is None else "new_row",
            artifact_ref=episode.artifact_ref,
            fields=[f for f in fields if f.value is not None],
            blanks=NOT_EVIDENCED,
            event_code=code,
            confidence=confidence,
            rationale=rationale,
            evidence_ids=episode.event_ids,
        )

    def draft_completions(self, episode, hub, incident, code, confidence) -> Drafted:
        """The human wrote the row. The stream knows what they left blank.

        Never an edit to their row — a completion lives in the capture layer
        with its evidence and the original stands as written (capture rule 4).
        """
        primary = episode.primary
        out: list[Field] = []

        if code is not None and incident.event_code != code:
            out.append(
                Field(
                    "Event Code",
                    code,
                    f"tel:{primary.event_id} code — the hub's own classification",
                    CONFIDENT,
                    existing=incident.event_code,
                )
            )
        elif code is None and incident.event_code != episode.code:
            # The inferred codes. The candidate value is carried so a reviewer
            # can accept it in one keystroke, but at question confidence and
            # with the rationale phrased as a question — the queue renders it
            # as something to answer, not something to wave through.
            out.append(
                Field(
                    "Event Code",
                    episode.code,
                    f"tel:{primary.event_id} code — inferred from a signal-loss pattern",
                    INFERRED,
                    existing=incident.event_code,
                )
            )

        if primary.sw_version and incident.sw_version_at_time != primary.sw_version:
            out.append(
                Field(
                    "SW Version at Time",
                    primary.sw_version,
                    f"tel:{primary.event_id} sw_version — the hub reported it at the moment of the fault",
                    CONFIDENT,
                    existing=incident.sw_version_at_time,
                )
            )

        duration = self._offline_hours(episode)
        if duration is not None and incident.offline_duration_hrs is None:
            out.append(
                Field(
                    "Offline Duration (hrs)", duration, self._duration_evidence(episode), CONFIDENT
                )
            )

        cluster = episode.cluster
        if cluster and not (incident.notes or "").strip():
            out.append(
                Field(
                    "Notes",
                    cluster.note(),
                    f"tel:{primary.event_id} + {len(cluster.episodes)} episodes at this site",
                    CONFIDENT,
                )
            )

        return Drafted(
            kind="completion",
            artifact_ref=episode.artifact_ref,
            fields=out,
            target_row_key=incident.incident_id,
            event_code=code,
            evidence_code=episode.code,
            confidence=confidence,
            rationale=(
                f"{incident.incident_id} already covers this episode "
                f"(reported {incident.reported_date}, event {episode.opened_at.date()}). "
                f"These cells are blank or disagree with the stream."
                + (
                    f" The {episode.code} code is the hub's inference from a signal-loss "
                    "pattern, so it is asked rather than asserted: confirm against the ward."
                    if code is None
                    else ""
                )
            ),
            evidence_ids=episode.event_ids,
        )

    # -- completions against rows with no event behind them --------------

    def completions_without_an_event(self) -> list[Drafted]:
        """The rows this bot found no event for still have cells it can fill.

        167 of the 295 fillable `SW Version at Time` cells sit on rows with no
        indicator event behind them at all — a user error, a logistics call, a
        row written up from an email. The heartbeat timeline still knows what
        that hub was running that day, and that is the column tier 2 cohorts on.

        `Serial Number` is simpler still: blank on 11% of rows and resolvable
        from HubID through the inventory. A join, not an artifact read, and the
        evidence says so rather than implying the stream reported it.
        """
        out: list[Drafted] = []
        for incident in self.session.execute(select(Incident)).scalars():
            if not incident.hub_id:
                continue

            if not incident.serial_number_as_written:
                serial = self.resolver.canonical_serial(incident.hub_id)
                if serial:
                    out.append(
                        self._reference_completion(
                            incident,
                            Field(
                                "Serial Number",
                                serial,
                                f"inv:{incident.hub_id} — resolvable from HubID. "
                                "A join, not an artifact read.",
                                CONFIDENT,
                            ),
                            artifact_ref=f"inv:{incident.hub_id}",
                            rationale="HubID is present on every row in this register, and the "
                            "inventory holds one canonical serial per hub.",
                        )
                    )

            if incident.incident_id in self._claimed or not incident.reported_date:
                continue
            sw = self.resolver.sw_version_at(incident.hub_id, incident.reported_date)
            if not sw or sw == incident.sw_version_at_time:
                continue
            ref = self.resolver.heartbeat_ref(incident.hub_id, incident.reported_date)
            out.append(
                self._reference_completion(
                    incident,
                    Field(
                        "SW Version at Time",
                        sw,
                        f"{ref} — last heartbeat at or before the reported date",
                        CONFIDENT,
                        existing=incident.sw_version_at_time,
                    ),
                    artifact_ref=ref,
                    rationale=(
                        "No indicator event sits behind this row, so the version comes from the "
                        "heartbeat timeline rather than from an event. The inventory's "
                        "last-observed column is not used: it is a stale value with a date, and "
                        "some of those dates are a year in the future."
                    ),
                )
            )
        return out

    def _reference_completion(self, incident, field, *, artifact_ref, rationale) -> Drafted:
        return Drafted(
            kind="completion",
            artifact_ref=artifact_ref,
            target_row_key=incident.incident_id,
            fields=[field],
            confidence=CONFIDENT,
            rationale=rationale,
        )

    # -- run -------------------------------------------------------------

    def run(self) -> CaptureOutput:
        """observe -> resolve -> classify -> draft. Stops at the queue. Always."""
        self._claimed: set[str] = set()
        self._by_hub = None
        output = CaptureOutput(bot=self.name)

        episodes = self.observe()
        output.episodes_seen = len(episodes)
        for episode in episodes:
            resolved = self.resolve(episode)
            if resolved and not resolved.accrues:
                # A unit that does not accrue unit-months must never contribute
                # to a numerator either (TELEMETRY-API.md §4). A Spare or a
                # not-yet-installed hub reporting itself offline is a true event
                # about a warehouse, and writing it up as a ward incident would
                # put it in front of a reviewer and into a rate. Counted, named,
                # not drafted.
                output.skipped.append(
                    (episode.artifact_ref, f"{resolved.unit_status} — unit does not accrue")
                )
                continue
            classification = self.classify(episode, resolved)
            output.add(self.draft(episode, resolved, classification))

        for completion in self.completions_without_an_event():
            output.add(completion)

        self.persist(output)
        return output

    # -- persistence -----------------------------------------------------

    def persist(self, output: CaptureOutput) -> None:
        """Write the queue. Idempotent: a re-run never re-proposes a reviewed item."""
        existing_drafts = {
            ref
            for (ref,) in self.session.execute(
                select(CaptureDraft.artifact_ref).where(CaptureDraft.bot == self.name)
            )
        }
        # Not filtered by bot, and the database agrees: the uniqueness that
        # matters is one proposal per cell, whoever made it. If field triage has
        # already offered this row's Notes, this bot does not offer a competing
        # one — two agents arguing in a reviewer's queue is worse than either of
        # them staying quiet, and `uq_completion_target_field` will refuse the
        # write anyway.
        existing_completions = {
            (row, field_name)
            for row, field_name in self.session.execute(
                select(CompletionSuggestion.target_row_key, CompletionSuggestion.field_name).where(
                    CompletionSuggestion.target_register == self.target_register
                )
            )
        }

        for item in output.items:
            if item.kind == "completion":
                for field in item.fields:
                    if (item.target_row_key, field.name) in existing_completions:
                        continue
                    existing_completions.add((item.target_row_key, field.name))
                    self.session.add(
                        CompletionSuggestion(
                            bot=self.name,
                            target_register=self.target_register,
                            target_row_key=item.target_row_key,
                            field_name=field.name,
                            existing_value=_text(field.existing),
                            proposed_value=_text(field.value),
                            artifact_ref=item.artifact_ref,
                            evidence=field.evidence,
                            confidence=field.confidence or item.confidence,
                            rationale=item.rationale,
                            status=DraftStatus.PENDING,
                        )
                    )
                continue

            if item.artifact_ref in existing_drafts:
                continue
            existing_drafts.add(item.artifact_ref)
            draft = CaptureDraft(
                bot=self.name,
                target_register=self.target_register,
                artifact_ref=item.artifact_ref,
                payload=item.payload(),
                proposed_event_code=item.event_code,
                confidence=item.confidence,
                rationale=item.rationale,
                status=DraftStatus.PENDING,
            )
            draft.fields = [
                DraftField(
                    field_name=f.name,
                    proposed_value=_text(f.value),
                    evidence=f.evidence,
                    confidence=f.confidence or item.confidence,
                )
                for f in item.fields
            ]
            self.session.add(draft)

        log_action(
            self.session,
            tier=1,
            workflow=self.name,
            autonomy=self.autonomy,
            inputs={"source": "telemetry_event", "episodes": output.episodes_seen},
            output=output.summary(),
            notes=(
                "Drafted only. Nothing committed — every item in this run waits on a human "
                "(capture is autonomy level 3, always)."
            ),
        )
        self.session.commit()

    # -- helpers ---------------------------------------------------------

    def _incidents_by_hub(self) -> dict[str, list[Incident]]:
        if self._by_hub is None:
            by_hub: dict[str, list[Incident]] = {}
            for incident in self.session.execute(select(Incident)).scalars():
                by_hub.setdefault(incident.hub_id, []).append(incident)
            self._by_hub = by_hub
        return self._by_hub

    def _description(self, episode: Episode) -> str:
        base = DESCRIPTIONS.get(episode.code, episode.code)
        if episode.repeats:
            base += f", {len(episode.events)} times over {episode.span_hours:.0f}h"
        detail = self._payload_detail(episode)
        return f"{base}{detail}"

    def _payload_detail(self, episode: Episode) -> str:
        """Only where the payload says something a human would have written."""
        p = episode.primary.payload or {}
        match episode.code:
            case "BATT" if p.get("capacity_pct_nominal") is not None:
                return f" — capacity {p['capacity_pct_nominal']}% of nominal, {p.get('cycles', '?')} cycles"
            case "CONN-LINK-LOSS" if p.get("rssi_at_loss") is not None:
                return f" — RSSI {p['rssi_at_loss']} dBm at loss"
            case "ALERT-FALSE" if p.get("alert_type"):
                profile = p.get("threshold_profile")
                return f" — {p['alert_type']} alert" + (f", {profile} profile" if profile else "")
            case "DISPLAY" if p.get("fault"):
                return f" — {p['fault']}" + (
                    f" (POST {p['post_code']})" if p.get("post_code") else ""
                )
            case _:
                return ""

    def _notes(self, episode: Episode) -> str | None:
        parts = []
        if episode.cluster:
            parts.append(episode.cluster.note())
        if episode.repeats:
            parts.append(
                f"{len(episode.events)} telemetry events grouped into one episode "
                f"({episode.opened_at:%Y-%m-%d %H:%M} to {episode.closed_at:%Y-%m-%d %H:%M}): "
                f"{', '.join(episode.event_ids)}."
            )
        if episode.replays_dropped:
            parts.append(
                f"{len(episode.replays_dropped)} replayed duplicate(s) dropped on dedupe key."
            )
        if (
            episode.code == "ALERT-FALSE"
            and (episode.primary.payload or {}).get("ward_profile_applied") is False
        ):
            parts.append("Hub reports the ward threshold profile was not applied.")
        return " ".join(parts) or None

    def _offline_hours(self, episode: Episode) -> Decimal | None:
        """Event-close minus event-open, where the stream carries both."""
        hours = episode.payload_value("offline_duration_h")
        if hours is not None:
            return Decimal(str(hours))
        if episode.code == "HUB-OFFLINE" and episode.repeats:
            return Decimal(f"{episode.span_hours:.2f}")
        return None

    def _duration_evidence(self, episode: Episode) -> str:
        if episode.payload_value("offline_duration_h") is not None:
            return f"tel:{episode.primary.event_id} payload offline_duration_h"
        return f"tel:{episode.primary.event_id} to tel:{episode.last.event_id} — episode span"


class InventedEvent(RuntimeError):
    """Raised rather than drafted. A SKIN event off the wire is a bug upstream."""


def _text(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def run(session: Session) -> CaptureOutput:
    return OutageWatch(session).run()
