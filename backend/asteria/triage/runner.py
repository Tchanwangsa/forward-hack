"""Walk OPS-SOP-004 over one episode and record every step of it.

The output is the thing a reviewer reads: the checks in the order the procedure
puts them, what each one returned, which clause ended the triage, and what the
agent concluded. Including the checks that found nothing — §3 C3 requires them
recorded, and they are most of the value. "Power fine, path fine, box fine,
device fine, and then the radio" is a diagnosis; "it's the patch" on its own is
an opinion.

The runner does not know the situation it is diagnosing. It reads tool output
and follows the tree, so `result.correct` — the conclusion against the hidden
cause in estate.py — is a real score, and the run that lands on
`unknown-escalate` because nothing matched is the procedure working, not a bug.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from asteria.capture.episodes import Episode
from asteria.fleet import scenarios
from asteria.resolve.entities import HubFacts
from asteria.triage import conditions, estate, sop
from asteria.triage.sop import Outcome, Procedure, Step
from asteria.triage.tools import TOOLS, Probe, ToolResult

MAX_STEPS = 12  # the procedure is eight steps; anything past this is a cycle

# Causes for which `unknown-escalate` is the right answer rather than a miss:
# nothing was wrong, or nothing in the revision in force can name what was.
UNREACHABLE_CAUSES = {estate.NOTHING_FOUND, *scenarios.OFF_TAXONOMY}


@dataclass
class StepRecord:
    """One clause of the procedure, executed."""

    step_id: str
    section: str
    title: str
    question: str
    cite: str
    tools: list[ToolResult] = field(default_factory=list)
    # (tool, the step whose session it was read in). A later step reading the
    # same host is not a second login, and the record says where to look.
    reused: list[tuple[str, str]] = field(default_factory=list)
    satisfied: str | None = None  # the condition that fired, if one did
    outcome: str | None = None
    goto: str | None = None
    note: str | None = None

    @property
    def findings(self) -> dict:
        merged: dict = {}
        for t in self.tools:
            merged.update(t.metrics)
        return merged


@dataclass
class TriageResult:
    """One triage, start to finish."""

    episode: Episode
    hub: HubFacts | None
    procedure: Procedure
    outcome: Outcome
    steps: list[StepRecord]
    findings: dict
    verification: str
    actual_cause: str  # estate.py's hidden truth. Scoring only — never drafted.

    @property
    def cause(self) -> str:
        return self.outcome.key

    @property
    def correct(self) -> bool:
        """Did the procedure land where the estate actually was?

        Two cases where the right answer is not the cause's own name, and both
        of them are the procedure working rather than failing:

        `nothing-found` scores against `unknown-escalate`. When nothing is wrong
        that a remote check can see, escalating to a field visit is correct.

        An **off-taxonomy** cause — one OPS-SOP-004 rev 3.0 has no branch for —
        also scores against `unknown-escalate`. The agent cannot reach a
        conclusion the controlled document does not contain, and it must not
        invent one (§3 C4). Landing on "inconclusive, field visit" when the real
        cause is a drifted device clock is the correct behaviour of a correct
        procedure with a gap in it, and the gap is the finding.
        """
        if self.actual_cause in UNREACHABLE_CAUSES:
            return self.outcome.key == "unknown-escalate"
        return self.outcome.key == self.actual_cause

    @property
    def off_taxonomy(self) -> bool:
        """The cause has no clause in the revision in force.

        These are the runs worth reading. Cluster them and they are a proposed
        amendment to the controlled document, which is a better thing for the
        product to produce than another correct diagnosis.
        """
        return self.actual_cause in scenarios.OFF_TAXONOMY

    @property
    def checks_run(self) -> int:
        return sum(len(s.tools) for s in self.steps)

    @property
    def deciding_step(self) -> StepRecord:
        return self.steps[-1]

    @property
    def confidence(self) -> Decimal:
        return Decimal(str(self.outcome.confidence))

    @property
    def citation(self) -> str:
        return f"{self.procedure.document.cite} {self.deciding_step.cite}"

    def narrative(self) -> str:
        """What the agent says on the timeline. Plain, and it names the clause."""
        ruled_out = [s for s in self.steps[:-1] if s.tools and not s.satisfied]
        cleared = ", ".join(s.title.lower() for s in ruled_out)
        opening = (
            f"Ran {self.procedure.document.cite} over {len(self.steps)} steps"
            f" and {self.checks_run} checks on {self.episode.hub_id}."
        )
        if cleared:
            opening += f" Cleared {cleared}."
        deciding = self.deciding_step
        why = (
            f" {deciding.cite} — {self.outcome.label}."
            if deciding.satisfied is None
            else f" {deciding.cite} {deciding.satisfied.replace('_', ' ')}: {self.outcome.label}."
        )
        return opening + why + " " + self._evidence_sentence()

    def _evidence_sentence(self) -> str:
        f = self.findings
        match self.outcome.key:
            case "expected-removal":
                return (
                    "Nothing failed. The unit stopped reporting because somebody meant it to, "
                    "and an incident row here would be a signal about a discharge."
                )
            case "power-loss":
                return (
                    f"PDU port {f.get('pdu_port')} was {f.get('socket_state')} and the unit's "
                    f"last battery reading was {f.get('battery_pct_at_silence')}%. "
                    "The hub is not faulty; the socket is."
                )
            case "site-network":
                detail = (
                    "the tunnel was down"
                    if f.get("tunnel_up") is False
                    else "DNS was failing"
                    if f.get("dns_ok") is False
                    else f"{f.get('loss_pct')}% loss at {f.get('rtt_ms')}ms"
                )
                return (
                    f"{f.get('peers_affected')} hubs at this site went quiet together and "
                    f"{detail}. One site event, not {f.get('peers_affected')} unit faults."
                )
            case "data-box-backlog":
                return (
                    f"The hub was reporting in the whole time. The data box was holding "
                    f"{f.get('queue_depth')} frames it could not ship "
                    f"(collector {'stopped' if f.get('collector_active') is False else 'running'}, "
                    f"disk {f.get('disk_used_pct')}%, cert {f.get('cert_days_remaining')}d). "
                    "This one is ours, not the customer's."
                )
            case "device-fault":
                return (
                    "The unit answered and then failed on itself: "
                    + (
                        f"{f.get('restarts_24h')} agent restarts in 24h."
                        if f.get("restarts_24h")
                        else f"POST fail {f.get('post_code')}."
                    )
                    + " Everything underneath it was healthy."
                )
            case "consumable-patch":
                return (
                    f"Power, path, box and device all checked out; link margin was "
                    f"{f.get('rssi_dbm')} dBm"
                    + (f" at {f.get('wear_time_h')}h wear" if f.get("wear_time_h") else "")
                    + ". That points at the patch — but a radio cannot see a piece of tape, "
                    "so this is a question for the ward, not a classification."
                )
            case _:
                return (
                    "Every check in the procedure passed. Nothing reachable from here explains "
                    "the event, which is the case the procedure sends to a field visit rather "
                    "than a guess."
                )


def triage(
    episode: Episode,
    hub: HubFacts | None,
    *,
    session: Session | None = None,
    procedure: Procedure | None = None,
    readings: dict | None = None,
    actual_cause: str | None = None,
) -> TriageResult | None:
    """Run the procedure. None when the episode is out of its scope.

    Out of scope is a real answer and not an error: OPS-SOP-004 §2 covers hub
    and link codes. SKIN has no telemetry path at all, so nothing that reaches
    here should carry it — but if one ever does, the procedure declines it
    rather than inventing a branch to hold it.

    `readings` is a live probe of the estate off the fleet service, and
    `actual_cause` is that run's scenario, supplied by the *caller* for scoring.
    The runner still never looks at either while deciding: readings are handed
    to the tools, and `actual_cause` is written onto the result after the
    outcome is already fixed. Feeding the cause in earlier would turn the one
    honest number in the system into a tautology.
    """
    p = procedure or sop.load()
    if not p.in_scope(episode.code):
        return None

    situation = estate.derive(episode, hub)
    probe = Probe(
        episode=episode,
        hub=hub,
        situation=situation,
        thresholds=p.thresholds,
        session=session,
        readings=readings,
    )

    steps: list[StepRecord] = []
    findings: dict = {}
    cache: dict[str, ToolResult] = {}
    read_at: dict[str, str] = {}
    step: Step | None = p.first

    for _ in range(MAX_STEPS):
        if step is None:
            break
        record = StepRecord(
            step_id=step.id,
            section=step.section,
            title=step.title,
            question=step.question,
            cite=step.cite,
            note=step.note,
        )
        for name in step.tools:
            # One session per host, however many steps read from it — an
            # engineer does not ssh in twice to run two commands, and a
            # transcript that pretends otherwise is a lie about the work.
            if name not in cache:
                cache[name] = TOOLS[name](probe)
                read_at[name] = step.cite
                record.tools.append(cache[name])
            else:
                record.reused.append((name, read_at[name]))
            findings.update(cache[name].metrics)
        steps.append(record)

        fired = next(
            (b for b in step.branches if conditions.evaluate(b.when, findings, p.thresholds)),
            None,
        )
        if fired is not None:
            record.satisfied = fired.when
            if fired.outcome:
                record.outcome = fired.outcome
                return _result(
                    episode,
                    hub,
                    p,
                    p.outcomes[fired.outcome],
                    steps,
                    findings,
                    situation,
                    actual_cause,
                )
            record.goto = fired.goto
            record.note = fired.note or record.note
            step = p.steps[fired.goto]
            continue

        if step.default_outcome:
            record.outcome = step.default_outcome
            return _result(
                episode,
                hub,
                p,
                p.outcomes[step.default_outcome],
                steps,
                findings,
                situation,
                actual_cause,
            )
        step = p.steps.get(step.next) if step.next else None

    raise RuntimeError(
        f"OPS-SOP-004 did not terminate on {episode.artifact_ref} — "
        "the procedure has a cycle and no triage was recorded"
    )


def _result(
    episode, hub, p, outcome, steps, findings, situation, actual_cause=None
) -> TriageResult:
    return TriageResult(
        episode=episode,
        hub=hub,
        procedure=p,
        outcome=outcome,
        steps=steps,
        findings=findings,
        verification=p.document.verify(),
        actual_cause=actual_cause or situation.cause,
    )
