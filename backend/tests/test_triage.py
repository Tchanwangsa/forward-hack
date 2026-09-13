"""The triage agent, scored against what was actually wrong.

Integration tests — they need an ingested database (`make ingest`).

Each test names a rule from OPS-SOP-004 or from the capture primitive, because
a triage agent is only worth having if the procedure it claims to follow is the
procedure it actually follows. A diagnosis nobody can audit is an opinion with a
citation stapled to it.
"""

import pytest
from sqlalchemy import select, text

from asteria.capture.episodes import find_clusters, to_episodes
from asteria.capture.field_triage import FieldTriage
from asteria.db import SessionLocal
from asteria.models.capture import CaptureDraft, CompletionSuggestion
from asteria.models.sources import TelemetryEvent
from asteria.models.triage import TriageRun
from asteria.resolve.entities import Resolver
from asteria.triage import conditions, sop
from asteria.triage.runner import triage
from asteria.triage.tools import TOOLS

# The estate access this agent is granted. A ninth entry is a decision about
# what a customer agreed to, not a refactor, so it fails this test first.
ALLOWED_TOOLS = {
    "fleet.hub_status",
    "fleet.heartbeat_gaps",
    "registers.context",
    "ward.occupancy",
    "power.socket_check",
    "net.path_check",
    "ssh.databox",
    "ssh.hub",
}


@pytest.fixture(scope="module")
def session():
    with SessionLocal() as s:
        if not s.execute(text("SELECT count(*) FROM telemetry_event")).scalar():
            pytest.skip("database not ingested — run `make ingest`")
        yield s


@pytest.fixture(scope="module")
def bot(session):
    """One clean run, shared by the module."""
    session.execute(text("DELETE FROM triage_step"))
    session.execute(text("DELETE FROM triage_run"))
    session.execute(
        text(
            "DELETE FROM draft_field WHERE draft_id IN "
            "(SELECT id FROM capture_draft WHERE bot = 'field-triage')"
        )
    )
    session.execute(text("DELETE FROM capture_draft WHERE bot = 'field-triage'"))
    session.execute(text("DELETE FROM completion_suggestion WHERE bot = 'field-triage'"))
    session.commit()
    b = FieldTriage(session)
    b.run()
    return b


@pytest.fixture(scope="module")
def procedure():
    return sop.load()


# -- the procedure is a procedure -----------------------------------------


def test_every_branch_has_a_predicate(procedure):
    """A `when:` the code cannot evaluate is a clause that silently never fires,
    which is the worst possible failure: a procedure that looks followed and is
    not. Caught here rather than in a run.
    """
    named = {b.when for s in procedure.steps.values() for b in s.branches}
    assert named <= set(conditions.CONDITIONS), named - set(conditions.CONDITIONS)


def test_every_outcome_is_reachable(procedure):
    """An outcome no branch can reach is a diagnosis the agent can never give."""
    reachable = {b.outcome for s in procedure.steps.values() for b in s.branches if b.outcome}
    reachable |= {s.default_outcome for s in procedure.steps.values() if s.default_outcome}
    assert reachable == set(procedure.outcomes)


def test_skin_is_out_of_scope(procedure):
    """IND-06 has no telemetry path, so no branch of this procedure may hold it.
    A triage agent that invents a clause to cover a code the device cannot emit
    has stopped following the document it cites.
    """
    assert "SKIN" in procedure.excluded_codes
    assert "SKIN" not in procedure.scope_codes


# -- the estate access is read-only ---------------------------------------


def test_the_tool_set_is_the_granted_one():
    """OPS-SOP-004 §3 C1 and TELEMETRY-API.md §7: diagnosis, not remediation.
    Remote access to a customer's estate is granted for one of those.
    """
    assert set(TOOLS) == ALLOWED_TOOLS


def test_no_tool_writes(session, bot):
    """No probe transcript may contain a command that changes anything. The
    transcript is what a reviewer reads as proof of what was done, so it is the
    thing worth asserting on.
    """
    forbidden = ("systemctl restart", "systemctl start", "reboot", "rm -", "flash", "> /")
    lines = [
        line
        for (probes,) in session.execute(text("SELECT probes FROM triage_step")).all()
        for probe in (probes or [])
        for line in probe["transcript"]
    ]
    assert lines, "no transcripts recorded"
    assert not [ln for ln in lines if any(f in ln for f in forbidden)]


# -- what a run records ---------------------------------------------------


def test_checks_that_found_nothing_are_recorded(session, bot):
    """§3 C3. 'Power fine, path fine, box fine, device fine, and then the radio'
    is a diagnosis; 'it's the patch' on its own is an opinion.
    """
    run = (
        session.execute(select(TriageRun).where(TriageRun.outcome == "consumable-patch"))
        .scalars()
        .first()
    )
    assert run is not None
    cleared = [s for s in run.steps if s.probes and not s.satisfied]
    assert len(cleared) >= 4


def test_every_run_cites_a_clause_and_a_revision(session, bot):
    """A diagnosis made under revision 3.0 still says so when the SOP moves on."""
    runs = list(session.execute(select(TriageRun)).scalars())
    assert runs
    assert all(r.citation and r.procedure_revision for r in runs)
    assert all(r.deciding_step in {s.step_id for s in r.steps} for r in runs)


def test_inconclusive_escalates_rather_than_guessing(session, bot):
    """§3 C4. The run that clears every check ends at a field visit."""
    runs = list(
        session.execute(select(TriageRun).where(TriageRun.outcome == "unknown-escalate")).scalars()
    )
    assert runs
    assert all(r.deciding_step == "T8" for r in runs)
    # A branch may have fired to *move* (T1 sending a site event to §5.4). None
    # may have fired to conclude: reaching T8 means nothing was found.
    assert all(all(s.outcome is None for s in r.steps[:-1]) for r in runs)


# -- what a run drafts ----------------------------------------------------


def test_checked_by_is_never_drafted(session, bot):
    """A check has a name against it because somebody is accountable for it.
    The agent is not a person.
    """
    drafts = session.execute(
        select(CaptureDraft).where(CaptureDraft.bot == "field-triage")
    ).scalars()
    for d in drafts:
        assert "Checked By" not in d.payload["fields"]
        assert "Checked By" in d.payload["blank_by_design"]


def test_a_benign_outcome_drafts_nothing(session, bot):
    """A hub that stopped reporting because the patient was discharged is not an
    incident. The decision is recorded; the row is not written.
    """
    benign = list(
        session.execute(select(TriageRun).where(TriageRun.disposition == "no_incident")).scalars()
    )
    assert benign
    assert all(r.draft_id is None for r in benign)
    assert all(r.narrative for r in benign)


def test_the_patch_outcome_is_asked_not_asserted(session, bot):
    """A radio cannot see a piece of tape. IND-05 off the wire is a question for
    someone who can look at the ward (TELEMETRY-API.md §5).
    """
    procedure = sop.load()
    assert procedure.outcomes["consumable-patch"].ask_do_not_assert
    runs = session.execute(
        select(TriageRun).where(TriageRun.outcome == "consumable-patch")
    ).scalars()
    for r in runs:
        assert float(r.confidence) < 0.5


def test_no_second_proposal_for_a_cell_another_bot_already_owns(session, bot):
    """Two agents arguing in a reviewer's queue is worse than either of them
    staying quiet.
    """
    rows = session.execute(
        select(CompletionSuggestion.target_row_key, CompletionSuggestion.field_name)
    ).all()
    assert len(rows) == len(set(rows))


def test_it_never_edits_the_human_row(session, bot):
    """Capture rule 4. The diagnosis is offered as a completion; the incident
    row stands as the human wrote it.
    """
    completions = list(
        session.execute(
            select(CompletionSuggestion).where(CompletionSuggestion.bot == "field-triage")
        ).scalars()
    )
    assert completions
    assert all(c.existing_value is None for c in completions)
    assert all(c.field_name == "Notes" for c in completions)


# -- does it get the answer right -----------------------------------------


def test_the_diagnosis_matches_what_was_wrong(session, bot):
    """The runner never sees the situation it is diagnosing — it reads tool
    output and follows the tree — so this is a score and not a tautology.
    """
    score = bot.score()
    assert score["correct"] / score["diagnosed"] >= 0.85


def test_the_same_episode_triages_the_same_way(session):
    """Deterministic on the episode. A re-run that reaches a different diagnosis
    from the same evidence is not a diagnosis.
    """
    events = list(session.execute(select(TelemetryEvent).limit(400)).scalars())
    episodes = to_episodes(events)
    find_clusters(episodes)
    resolver = Resolver(session)
    episode = next(e for e in episodes if sop.load().in_scope(e.code))
    first = triage(episode, resolver.hub(episode.hub_id), session=session)
    second = triage(episode, resolver.hub(episode.hub_id), session=session)
    assert first.outcome.key == second.outcome.key
    assert [s.step_id for s in first.steps] == [s.step_id for s in second.steps]
