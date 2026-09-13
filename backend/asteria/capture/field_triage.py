"""Bot 2 — OPS-SOP-004 -> PM-Data-Check-and-Troubleshooting-Log.

Outage watch says *what* happened and that nobody wrote it down. This one says
*why*, by running the ops team's own triage procedure against the estate and
writing the result up where the ops team writes it up: the troubleshooting log,
whose `Action Taken` column is blank on 66% of its rows because the work is done
on a phone call and never reaches the spreadsheet.

    observe    episodes in OPS-SOP-004 §2 scope
    resolve    hub -> organisation, ward, bed, pairing (the same Resolver)
    classify   not a code — a cause. The procedure decides, not the model.
    draft      a troubleshooting row, plus the diagnosis as a Note on the
               incident row where a human already wrote one

Three things it must not do, all three tested:

    Never conclude past the procedure. A branch that does not fire is not a
    finding, and the run that clears every check ends at a field visit rather
    than the most likely-sounding cause.

    Never fill `Checked By`. A check has a person's name against it because
    somebody is accountable for it. The agent is not a person and the field is
    blank by design until a reviewer's name goes on the row.

    Never write an incident row for a benign outcome. A hub that stopped
    reporting because the patient was discharged is not an incident, and the
    honest output is a recorded decision to close it — which is why a benign
    triage still leaves a TriageRun behind.
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from asteria.agent.action_log import log_action
from asteria.agent.autonomy import Autonomy
from asteria.capture.episodes import Episode, find_clusters, to_episodes
from asteria.capture.outage_watch import MATCH_WINDOW_AFTER, MATCH_WINDOW_BEFORE
from asteria.capture.primitive import CaptureBot, CaptureOutput, Drafted, Field
from asteria.fleet.client import FleetClient
from asteria.models.capture import CaptureDraft, CompletionSuggestion, DraftField
from asteria.models.capture_fed import Incident
from asteria.models.enums import DraftStatus
from asteria.models.sources import TelemetryEvent
from asteria.models.triage import TriageRun, TriageStep
from asteria.resolve.entities import Resolver
from asteria.triage import sop
from asteria.triage.runner import TriageResult, triage

# The register's own column names, which is what the reviewer sees.
FIELD_COLUMNS = {
    "Date": "check_date",
    "Organisation": "organisation_as_written",
    "Ward": "ward",
    "Bed": "bed",
    "PulseOne-PulsePatch Pairing": "pairing",
    "Serial Number": "serial_number_as_written",
    "Patch Lot": "patch_lot",
    "Hardware Issues": "hardware_issues",
    "Alert Misclassifications": "alert_misclassifications",
    "Patient & Alert Issues": "patient_and_alert_issues",
    "Software Issues": "software_issues",
    "Issue Found": "issue_found",
    "Checked By": "checked_by",
    "Action Taken": "action_taken",
}

# Which of the four free-text issue columns an outcome belongs in. Outcomes with
# no entry belong in none of them: a hospital network cutover is not a hardware
# issue and filing it as one is how a site event becomes a product signal.
ISSUE_COLUMN = {
    "power-loss": "Hardware Issues",
    "device-fault": "Hardware Issues",
    "consumable-patch": "Hardware Issues",
    "data-box-backlog": "Software Issues",
}

NOT_EVIDENCED = {
    "Checked By": "the person accountable for the check — assigned when a human accepts",
    "Alert Misclassifications": "remote triage cannot see how an alert was judged",
    "Patient & Alert Issues": "clinical observation, and out of this procedure's scope",
}


class FieldTriage(CaptureBot):
    name = "field-triage"
    source = "estate probes"
    target_register = "data_check"
    autonomy = Autonomy.DRAFT

    def __init__(
        self,
        session: Session,
        *,
        since: datetime | None = None,
        fleet: FleetClient | None = None,
    ) -> None:
        self.since = since
        # The estate, live, when the fleet service is up. Absent it, the tools
        # fall back to the derived estate and this bot behaves exactly as it did
        # over the frozen stream — which is the point of the fallback: the
        # simulator is a richer input, not a second code path.
        self.fleet = fleet
        self.session = session
        self.resolver = Resolver(session)
        self.procedure = sop.load()
        self.runs: dict[str, TriageResult] = {}

    # -- observe ---------------------------------------------------------

    def observe(self) -> list[Episode]:
        """The same episodes outage watch drafts from, filtered to §2 scope.

        Reduced identically and deliberately: triage and capture must agree on
        what one incident *is*, or the register gets a row saying a hub was
        offline eleven times and a triage saying it went offline once.
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
        return [e for e in episodes if self.procedure.in_scope(e.code)]

    # -- resolve ---------------------------------------------------------

    def resolve(self, episode: Episode):
        return self.resolver.hub(episode.hub_id)

    # -- classify --------------------------------------------------------

    def classify(self, episode: Episode, resolved) -> TriageResult | None:
        """Not a code — a cause, reached by walking OPS-SOP-004.

        The model does not pick the outcome and neither does this method. The
        procedure's conditions read the tools' findings and the branch that
        fires is the answer, which is the only version of this a quality team
        can sign off on: the reasoning is a controlled document, not a prompt.
        """
        readings = None
        if self.fleet is not None:
            # One round of probes for the whole run, so every step of the
            # transcript describes the same instant. A transcript where the
            # socket is dead at §5.3 and live at §5.6 describes a fleet that
            # never existed.
            readings = self.fleet.readings(
                episode.hub_id, resolved.customer_id if resolved else None
            )
        return triage(
            episode,
            resolved,
            session=self.session,
            procedure=self.procedure,
            readings=readings,
        )

    # -- draft -----------------------------------------------------------

    def draft(self, episode: Episode, resolved, result: TriageResult) -> Drafted | None:
        """A troubleshooting row. None when the outcome is not an incident."""
        if not result.outcome.is_incident:
            return None

        hub = resolved
        ref = result.deciding_step.cite
        fields: list[Field] = [
            Field("Date", episode.opened_at.date(), f"tel:{episode.primary.event_id} ts_device"),
            Field("Organisation", hub.organisation if hub else None, f"inv:{episode.hub_id}"),
            Field(
                "Ward",
                (hub.ward_id if hub else None) or episode.primary.ward_id,
                f"inv:{episode.hub_id}",
            ),
            Field(
                "Bed",
                (hub.bed_id if hub else None) or episode.primary.bed_id,
                f"inv:{episode.hub_id}",
            ),
            Field(
                "PulseOne-PulsePatch Pairing",
                hub.pairing_id if hub else None,
                f"inv:{episode.hub_id}",
            ),
            Field(
                "Serial Number",
                self.resolver.canonical_serial(episode.hub_id) or episode.primary.serial,
                f"inv:{episode.hub_id} — canonical serial for this hub",
            ),
            Field(
                "Issue Found",
                self._issue_found(result),
                f"{self.procedure.document.cite} {ref} — {result.deciding_step.title}",
                result.confidence,
            ),
            Field(
                "Action Taken",
                self._action_taken(result),
                f"{self.procedure.document.cite} outcome `{result.outcome.key}`",
                result.confidence,
            ),
        ]

        column = ISSUE_COLUMN.get(result.outcome.key)
        if column:
            fields.append(
                Field(
                    column,
                    self._issue_detail(result),
                    self._probe_evidence(result),
                    result.confidence,
                )
            )

        lot = result.findings.get("patch_lot") or episode.payload_value("patch_lot")
        if lot:
            fields.append(
                Field("Patch Lot", lot, f"tel:{episode.primary.event_id} payload patch_lot")
            )

        return Drafted(
            kind="question" if result.outcome.ask_do_not_assert else "new_row",
            artifact_ref=episode.artifact_ref,
            fields=[f for f in fields if f.value is not None],
            blanks=NOT_EVIDENCED,
            event_code=episode.code,
            confidence=result.confidence,
            rationale=result.narrative(),
            evidence_ids=episode.event_ids,
        )

    def note_on_incident(self, episode: Episode, result: TriageResult) -> Drafted | None:
        """The diagnosis, offered to the human row that already covers it.

        A `Notes` cell on an incident row is where an ops team writes what it
        turned out to be, and 'the site's core switch was being replaced' on a
        row someone opened as a unit fault is the sentence that stops it being
        counted as one. The row itself is not touched (capture rule 4).
        """
        incident = self._existing_incident(episode)
        if incident is None or (incident.notes or "").strip():
            return None
        return Drafted(
            kind="completion",
            artifact_ref=episode.artifact_ref,
            target_row_key=incident.incident_id,
            fields=[
                Field(
                    "Notes",
                    result.narrative(),
                    f"{result.citation} — {result.checks_run} checks over "
                    f"{len(result.steps)} steps of the procedure",
                    result.confidence,
                    existing=incident.notes,
                )
            ],
            confidence=result.confidence,
            rationale=(
                f"{incident.incident_id} covers this episode and its Notes are blank. "
                f"Triage under {self.procedure.document.cite} concluded "
                f"{result.outcome.label.lower()}; the checks behind it are on this item."
            ),
            evidence_ids=episode.event_ids,
        )

    # -- run -------------------------------------------------------------

    def run(self) -> CaptureOutput:
        output = CaptureOutput(bot=self.name)
        episodes = self.observe()
        output.episodes_seen = len(episodes)

        for episode in episodes:
            resolved = self.resolve(episode)
            result = self.classify(episode, resolved)
            if result is None:
                output.skipped.append(
                    (episode.artifact_ref, f"{episode.code} is outside OPS-SOP-004 §2")
                )
                continue
            self.runs[episode.artifact_ref] = result

            drafted = self.draft(episode, resolved, result)
            if drafted is None:
                # A recorded decision, not a silence: the run is persisted, the
                # reason is named, and the coverage numbers can tell a benign
                # close apart from an episode nobody looked at.
                output.skipped.append(
                    (episode.artifact_ref, f"{result.outcome.label} — no incident")
                )
                continue
            output.add(drafted)
            output.add(self.note_on_incident(episode, result))

        self.persist(output)
        return output

    # -- persistence -----------------------------------------------------

    def persist(self, output: CaptureOutput) -> None:
        """Drafts, completions, and the procedure walk behind each of them.

        Idempotent on artifact_ref, like every capture bot: a re-run adds what
        is new and re-proposes nothing already reviewed.
        """
        existing_drafts = {
            ref
            for (ref,) in self.session.execute(
                select(CaptureDraft.artifact_ref).where(CaptureDraft.bot == self.name)
            )
        }
        # Not filtered by bot. The uniqueness that matters is one proposal per
        # cell: if outage watch already offered this row's Notes, this bot does
        # not offer a competing one — two agents arguing in a reviewer's queue
        # is worse than either of them staying quiet.
        claimed_cells = {
            (row, field_name)
            for row, field_name in self.session.execute(
                select(CompletionSuggestion.target_row_key, CompletionSuggestion.field_name).where(
                    CompletionSuggestion.target_register == "incident"
                )
            )
        }
        persisted_runs = {
            ref
            for (ref,) in self.session.execute(
                select(TriageRun.artifact_ref).where(TriageRun.bot == self.name)
            )
        }

        draft_ids: dict[str, int] = {}
        for item in output.items:
            if item.kind == "completion":
                for field in item.fields:
                    if (item.target_row_key, field.name) in claimed_cells:
                        continue
                    claimed_cells.add((item.target_row_key, field.name))
                    self.session.add(
                        CompletionSuggestion(
                            bot=self.name,
                            target_register="incident",
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
            self.session.flush()
            draft_ids[item.artifact_ref] = draft.id

        for ref, result in self.runs.items():
            if ref in persisted_runs:
                continue
            self.session.add(self._run_row(ref, result, draft_ids.get(ref)))

        log_action(
            self.session,
            tier=1,
            workflow=self.name,
            autonomy=self.autonomy,
            inputs={
                "procedure": self.procedure.document.cite,
                "verification": self.procedure.document.verify(),
                "episodes": output.episodes_seen,
            },
            output={**output.summary(), **self.score()},
            notes=(
                "Diagnoses drafted, nothing committed. Every check is read-only: "
                "OPS-SOP-004 §3 C1 allows diagnosis and recording, and nothing in this "
                "run wrote to a device, a hub or a customer's estate."
            ),
            rule_model_version=f"{self.procedure.document.id} rev {self.procedure.document.revision}",
        )
        self.session.commit()

    def _run_row(self, ref: str, result: TriageResult, draft_id: int | None) -> TriageRun:
        doc = self.procedure.document
        run = TriageRun(
            bot=self.name,
            artifact_ref=ref,
            hub_id=result.episode.hub_id,
            event_code=result.episode.code,
            procedure_id=doc.id,
            procedure_revision=doc.revision,
            procedure_verification=result.verification,
            outcome=result.outcome.key,
            disposition=result.outcome.disposition,
            confidence=result.confidence,
            deciding_step=result.deciding_step.step_id,
            citation=result.citation,
            narrative=result.narrative(),
            escalate_to=result.outcome.escalate_to,
            checks_run=result.checks_run,
            findings=_jsonable(result.findings),
            actual_cause=result.actual_cause,
            correct=result.correct,
            draft_id=draft_id,
        )
        run.steps = [
            TriageStep(
                ordinal=i,
                step_id=s.step_id,
                section=s.section,
                title=s.title,
                question=s.question,
                satisfied=s.satisfied,
                outcome=s.outcome,
                goto=s.goto,
                note=s.note,
                probes=[
                    {
                        "tool": t.tool,
                        "target": t.target,
                        "summary": t.summary,
                        "ref": t.ref,
                        "metrics": _jsonable(t.metrics),
                        "transcript": t.transcript,
                        "reused_from": None,
                    }
                    for t in s.tools
                ]
                + [
                    {
                        "tool": tool,
                        "target": "",
                        "summary": f"already read in {where} — same session, not a second login",
                        "ref": f"probe:{tool}@{where}",
                        "metrics": {},
                        "transcript": [],
                        "reused_from": where,
                    }
                    for tool, where in s.reused
                ],
            )
            for i, s in enumerate(result.steps)
        ]
        return run

    # -- scoring ---------------------------------------------------------

    def score(self) -> dict:
        """The diagnosis against what was actually wrong.

        Honest because the runner never sees the situation it is diagnosing —
        it reads tool output and follows the tree. A procedure that scores badly
        here is a procedure with a gap in it, which is a finding worth having.
        """
        runs = list(self.runs.values())
        if not runs:
            return {"diagnosed": 0}
        return {
            "diagnosed": len(runs),
            "correct": sum(1 for r in runs if r.correct),
            "escalated": sum(1 for r in runs if r.outcome.key == "unknown-escalate"),
            "closed_benign": sum(1 for r in runs if not r.outcome.is_incident),
            "checks_run": sum(r.checks_run for r in runs),
        }

    # -- helpers ---------------------------------------------------------

    def _existing_incident(self, episode: Episode) -> Incident | None:
        """The human row covering this episode, by the same rule outage watch
        matches on — same hub, written up within a week of the event.
        """
        day = episode.opened_at.date()
        rows = self.session.execute(
            select(Incident).where(
                Incident.hub_id == episode.hub_id, Incident.reported_date.is_not(None)
            )
        ).scalars()
        candidates = [
            i
            for i in rows
            if day - MATCH_WINDOW_BEFORE <= i.reported_date <= day + MATCH_WINDOW_AFTER
        ]
        candidates.sort(key=lambda i: abs((i.reported_date - day).days))
        return candidates[0] if candidates else None

    def _issue_found(self, result: TriageResult) -> str:
        cleared = [s.title.lower() for s in result.steps[:-1] if s.tools and not s.satisfied]
        tail = f" Cleared first: {', '.join(cleared)}." if cleared else ""
        return f"{result.outcome.issue_found}{tail}"

    def _action_taken(self, result: TriageResult) -> str:
        escalation = (
            f" Escalated to: {result.outcome.escalate_to}." if result.outcome.escalate_to else ""
        )
        return f"{result.outcome.action_taken}{escalation} ({result.citation})"

    def _issue_detail(self, result: TriageResult) -> str:
        f = result.findings
        match result.outcome.key:
            case "power-loss":
                return (
                    f"PDU port {f.get('pdu_port')} {f.get('socket_state')}; no power at the unit."
                )
            case "device-fault":
                return (
                    f"Agent restarted {f.get('restarts_24h')}x in 24h."
                    if f.get("restarts_24h")
                    else f"POST fail {f.get('post_code')} on the unit."
                )
            case "consumable-patch":
                return (
                    f"Link margin {f.get('rssi_dbm')} dBm"
                    + (f" at {f.get('wear_time_h')}h wear" if f.get("wear_time_h") else "")
                    + " with the unit otherwise healthy."
                )
            case "data-box-backlog":
                return (
                    f"Site data box: collector "
                    f"{'stopped' if f.get('collector_active') is False else 'running'}, "
                    f"{f.get('queue_depth')} frames queued, disk {f.get('disk_used_pct')}%."
                )
            case _:
                return result.outcome.label

    def _probe_evidence(self, result: TriageResult) -> str:
        step = result.deciding_step
        return step.tools[0].ref if step.tools else result.citation


def _text(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return str(value)


def _jsonable(d: dict) -> dict:
    return {k: (float(v) if isinstance(v, Decimal) else v) for k, v in (d or {}).items()}


def run(session: Session) -> CaptureOutput:
    return FieldTriage(session).run()
