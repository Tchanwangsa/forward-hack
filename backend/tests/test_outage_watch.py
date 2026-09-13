"""Bot 1, scored against the world it was supposed to describe.

Integration tests — they need an ingested database (`make ingest`). The bot
itself never reads the ground_truth schema; these tests do, which is the whole
point of keeping the two apart.

Each test names a rule from plan/CAPTURE-AGENTS.md §1, because the rules are
what make a capture tier trustworthy and a regression in any of them is worth
more noise than a failing assertion about a count.
"""

from decimal import Decimal

import pytest
from sqlalchemy import select, text

from asteria.capture.episodes import find_clusters, to_episodes
from asteria.capture.outage_watch import INFERRED, NEVER_FROM_TELEMETRY, InventedEvent, OutageWatch
from asteria.db import SessionLocal
from asteria.models.capture import CaptureDraft, CompletionSuggestion
from asteria.models.capture_fed import Incident
from asteria.models.enums import DraftStatus, RowOrigin
from asteria.models.sources import TelemetryEvent

CAPTURE_TABLES = ("draft_field", "review_verdict", "capture_draft", "completion_suggestion")


@pytest.fixture(scope="module")
def session():
    with SessionLocal() as s:
        if not s.execute(text("SELECT count(*) FROM telemetry_event")).scalar():
            pytest.skip("database not ingested — run `make ingest`")
        yield s


@pytest.fixture(scope="module")
def run(session):
    """One clean run of the bot, shared by the module.

    Agent-written incident rows are cleared first: an accepted draft from an
    earlier run is a committed row, and leaving it in place would let a second
    run draft against a register the first one changed.
    """
    for table in CAPTURE_TABLES:
        session.execute(text(f"DELETE FROM {table}"))
    session.execute(text("DELETE FROM incident WHERE row_origin <> 'Human'"))
    session.execute(text("DELETE FROM agent_action"))
    session.commit()
    return OutageWatch(session).run()


# -- the two rules that must never bend -----------------------------------


def test_skin_is_never_drafted_from_telemetry(session, run):
    """A patch cannot detect a rash. IND-06 has no telemetry path at all, so a
    SKIN row sourced from this bot means it invented an event.
    """
    codes = {d.proposed_event_code for d in session.execute(select(CaptureDraft)).scalars()}
    assert not (codes & NEVER_FROM_TELEMETRY)

    rows = session.execute(
        select(Incident).where(Incident.event_code == "SKIN", Incident.source == "Telemetry")
    ).scalars()
    assert list(rows) == []


def test_a_skin_event_off_the_wire_raises_rather_than_drafts(session):
    """If one ever appears, that is a bug upstream and it should be loud."""
    bot = OutageWatch(session)
    invented = TelemetryEvent(event_id="TEL-FAKE", hub_id="HUB-04507", code="SKIN")
    episode = to_episodes([invented])[0]
    with pytest.raises(InventedEvent):
        bot.classify(episode, bot.resolve(episode))


def test_adhesive_is_asked_never_asserted(session, run):
    """The stream carries ADHESIVE, but as a signal-loss pattern *consistent
    with* detachment — an inference about a piece of tape, made by a radio.
    """
    drafts = session.execute(
        select(CaptureDraft).where(CaptureDraft.confidence == INFERRED)
    ).scalars()
    for draft in drafts:
        assert draft.proposed_event_code is None, "an inferred code must not be asserted"
        assert draft.payload["fields"].get("Event Code") is None
        assert "confirm" in draft.rationale.lower()

    adhesive_completions = session.execute(
        select(CompletionSuggestion).where(
            CompletionSuggestion.field_name == "Event Code",
            CompletionSuggestion.proposed_value == "ADHESIVE",
        )
    ).scalars()
    for completion in adhesive_completions:
        assert completion.confidence < Decimal("0.5"), "ADHESIVE may only be question-grade"


# -- capture rules 2, 3 and 4 ---------------------------------------------


def test_it_fills_only_what_the_source_evidences(session, run):
    """A blank is a correct answer. Guessing `Assigned To` to make a row look
    complete is the failure mode that discredits the whole tier.
    """
    for draft in session.execute(select(CaptureDraft)).scalars():
        fields = draft.payload["fields"]
        assert "Reported By" not in fields, "a telemetry event has no reporter"
        assert "Assigned To" not in fields, "triage is a human act"
        assert "Date of Last Email Sent" not in fields
        assert set(draft.payload["blank_by_design"]) == {
            "Reported By",
            "Assigned To",
            "Date of Last Email Sent",
        }


def test_every_drafted_field_points_at_something(session, run):
    """Capture rule 3. A field the bot cannot point at should not have been filled."""
    drafts = list(session.execute(select(CaptureDraft)).scalars())
    assert drafts
    for draft in drafts:
        assert draft.artifact_ref.startswith("tel:")
        assert draft.fields
        for field in draft.fields:
            assert field.evidence, f"{draft.artifact_ref}.{field.field_name} has no evidence"

    for completion in session.execute(select(CompletionSuggestion)).scalars():
        assert completion.evidence
        assert completion.artifact_ref.split(":")[0] in {"tel", "hb", "inv"}


def test_a_drafted_row_is_resolvable_back_to_its_events(session, run):
    """Provenance is not decoration: every event ID on a draft must exist."""
    for draft in session.execute(select(CaptureDraft)).scalars():
        ids = draft.payload["events"]
        assert ids
        found = session.execute(
            select(TelemetryEvent.event_id).where(TelemetryEvent.event_id.in_(ids))
        ).scalars()
        assert sorted(found) == sorted(ids)


def test_capture_never_edits_a_human_row(session, run):
    """Capture rule 4. A completion lives in the capture layer; the customer's
    row stands as written, wrong serial and all.
    """
    before = session.execute(
        text("SELECT count(*) FROM incident WHERE row_origin = 'Human'")
    ).scalar()
    contradicted = session.execute(
        select(CompletionSuggestion).where(CompletionSuggestion.existing_value.isnot(None))
    ).scalars()
    for completion in list(contradicted)[:20]:
        row = session.execute(
            select(Incident).where(Incident.incident_id == completion.target_row_key)
        ).scalar_one()
        assert row.row_origin == RowOrigin.HUMAN
        if completion.field_name == "SW Version at Time":
            assert row.sw_version_at_time == completion.existing_value
    assert (
        session.execute(text("SELECT count(*) FROM incident WHERE row_origin = 'Human'")).scalar()
        == before
    )


def test_nothing_is_committed_by_the_bot(session, run):
    """Level 3, always. A run ends at the queue."""
    statuses = {d.status for d in session.execute(select(CaptureDraft)).scalars()}
    assert statuses == {DraftStatus.PENDING}
    assert (
        session.execute(text("SELECT count(*) FROM incident WHERE row_origin <> 'Human'")).scalar()
        == 0
    )


# -- the failure mode this bot is designed against ------------------------


def test_a_replayed_buffer_is_dropped_not_counted(session, run):
    """A hub reconnecting replays its buffer. Counting those five times is a
    fabricated signal, and the dataset plants eight of them.
    """
    duplicated = session.execute(
        text("SELECT dedupe_key FROM telemetry_event GROUP BY 1 HAVING count(*) > 1")
    ).scalars()
    keys = list(duplicated)
    assert keys, "the planted replays are missing from the ingest"

    events = list(session.execute(select(TelemetryEvent)).scalars())
    episodes = to_episodes(events)
    assert sum(len(ep.replays_dropped) for ep in episodes) == len(keys)
    assert sum(len(ep.events) for ep in episodes) == len(events) - len(keys)


def test_a_site_wide_outage_is_one_story_not_thirty_six_incidents(session, run):
    """The near-miss: a hospital network cutover at Ashfield Private, ten hubs
    flapping over six days. One row per hub, each carrying the co-occurrence —
    a bot that files thirty-six incidents has made the register worse.
    """
    events = list(session.execute(select(TelemetryEvent)).scalars())
    episodes = to_episodes(events)
    clusters = find_clusters(episodes)
    assert len(clusters) == 1
    cluster = clusters[0]
    assert len(cluster.episodes) < sum(len(ep.events) for ep in cluster.episodes)
    assert cluster.ward_wide
    assert "Site-wide cause to rule out" in cluster.note()

    drafted = session.execute(
        select(CaptureDraft).where(
            CaptureDraft.artifact_ref.in_([ep.artifact_ref for ep in cluster.episodes])
        )
    ).scalars()
    for draft in drafted:
        assert "hubs at this site raised" in draft.payload["fields"]["Notes"]


def test_a_unit_that_does_not_accrue_is_not_written_up(session, run):
    """Spare and 'Shipped - not installed' units do not accrue unit-months, so
    an event from one must never reach a numerator — and a hub reporting itself
    offline from a warehouse shelf is not a ward incident.
    """
    assert run.summary()["skipped"] == 6
    hubs_drafted = {
        d.payload["fields"]["HubID"] for d in session.execute(select(CaptureDraft)).scalars()
    }
    statuses = session.execute(
        text("SELECT hub_id, unit_status FROM hub WHERE hub_id = ANY(:ids)"),
        {"ids": list(hubs_drafted)},
    )
    for _hub_id, status in statuses:
        assert status not in ("Spare", "Shipped - not installed")


def test_running_twice_proposes_nothing_twice(session, run):
    """Idempotent on (bot, artifact_ref) and on (row, field)."""
    before = (
        session.execute(text("SELECT count(*) FROM capture_draft")).scalar(),
        session.execute(text("SELECT count(*) FROM completion_suggestion")).scalar(),
    )
    OutageWatch(session).run()
    after = (
        session.execute(text("SELECT count(*) FROM capture_draft")).scalar(),
        session.execute(text("SELECT count(*) FROM completion_suggestion")).scalar(),
    )
    assert before == after


# -- scored against ground truth ------------------------------------------


def test_it_recovers_the_forty_four_rows_it_owns(session, run):
    """The headline. 62 indicator events never reached the incident log: 44 are
    hub codes this bot owns outright, 15 are ADHESIVE it can only ask about, and
    3 are SKIN it will never see.
    """
    recovered = session.execute(
        text(
            """
            SELECT count(DISTINCT a.event_id)
            FROM capture_draft d
            JOIN ground_truth.artifact_index a
              ON a.artifact_id = replace(d.artifact_ref, 'tel:', '')
            WHERE d.proposed_event_code IS NOT NULL
              AND a.row_id IS NULL AND d.proposed_event_code = a.true_code
            """
        )
    ).scalar()
    assert recovered == 44

    questions = session.execute(
        text(
            """
            SELECT count(DISTINCT a.event_id)
            FROM capture_draft d
            JOIN ground_truth.artifact_index a
              ON a.artifact_id = replace(d.artifact_ref, 'tel:', '')
            WHERE d.proposed_event_code IS NULL AND a.row_id IS NULL
            """
        )
    ).scalar()
    assert questions == 15


def test_it_never_proposes_a_wrong_value(session, run):
    """Field accuracy against `ground_truth.capture_targets` — not against the
    human's typed value, and not against a reviewer's verdict.
    """
    wrong = session.execute(
        text(
            """
            SELECT c.target_row_key, c.field_name, c.proposed_value, t.true_value
            FROM completion_suggestion c
            JOIN ground_truth.capture_targets t
              ON t.row_id = c.target_row_key AND t.field = c.field_name
             AND t.register LIKE 'PM-Incident%'
            WHERE c.proposed_value <> t.true_value
            """
        )
    ).all()
    assert wrong == []


def test_it_fills_every_sw_version_the_stream_can_evidence(session, run):
    """The line that matters most, and not because 35% is a big number: of the
    fifteen ALERT-FALSE events on SW 1.1.0 in the live window, two carry a
    correct version in the human register. Tier 2 cannot find that cohort until
    this has run.
    """
    missed = session.execute(
        text(
            """
            SELECT count(*)
            FROM ground_truth.capture_targets t
            LEFT JOIN completion_suggestion c
              ON c.target_row_key = t.row_id AND c.field_name = t.field
            WHERE t.register LIKE 'PM-Incident%' AND t.row_id <> 'NEW'
              AND t.fillable = 'Y' AND t.field = 'SW Version at Time' AND c.id IS NULL
            """
        )
    ).scalar()
    # One row's hub had not reported a heartbeat by the date it was written up.
    # A blank is the correct answer there; the inventory's stale column is not.
    assert missed == 1


def test_the_code_it_drafts_is_the_code_that_happened(session, run):
    """Classification accuracy on telemetry. The code is read, not judged, so
    anything below 100% here is a plumbing bug rather than a model limit.
    """
    from asteria.capture.scorecard import classification_accuracy

    by_bot = {r["bot"]: r for r in classification_accuracy(session)["by_bot"]}
    assert by_bot["outage-watch"]["accuracy_pct"] == 100.0


def test_coverage_moves_only_when_a_human_accepts(session, run):
    """53% is what the register achieves alone. Drafting changes nothing about
    what it says — a projection is labelled a projection.
    """
    from asteria.capture.scorecard import coverage

    assert coverage(session)["pct_after"] == pytest.approx(53.4, abs=0.1)
    projected = coverage(session, projected=True)
    assert projected["rows_recovered"] == 44
    assert projected["pct_after"] > 90
