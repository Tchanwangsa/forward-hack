"""OPS-SOP-004, loaded. The procedure is data, not code.

The controlled PDF in mock-company/sops/ is the document the ops team is
audited against. This module loads its executable twin and — when the twin
carries a checksum — checks that the PDF it claims to mirror is the PDF on
disk. A procedure revised on paper and not here would otherwise produce an
agent confidently and traceably following a superseded revision, which is worse
than an agent with no procedure at all.

`revision` travels with every action this package logs. When the SOP moves to
4.0, last month's triage decisions still say which rules they were made under.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

import yaml

from asteria.config import REPO_ROOT

SOP_PATH = REPO_ROOT / "reference-data" / "sop" / "OPS-SOP-004-outage-triage.yaml"


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    revision: str
    effective: str
    owner: str
    approved_by: str
    pdf: str
    sha256: str | None

    @property
    def cite(self) -> str:
        return f"{self.id} rev {self.revision}"

    def verify(self) -> str:
        """Does the PDF on disk match the one this file was written against?

        Returns a phrase for the action log rather than raising: a hackathon
        checkout with no PDF should still run, and 'unverified' in the audit
        trail is an honest thing to say. A *mismatch* is not — that one raises.
        """
        path = REPO_ROOT / self.pdf
        if self.sha256 is None:
            return "controlled PDF checksum not recorded — procedure unverified"
        if not path.exists():
            return f"controlled PDF absent at {self.pdf} — procedure unverified"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != self.sha256:
            raise SupersededProcedure(
                f"{self.id}: {self.pdf} has changed since the machine-readable "
                f"procedure was written against it ({actual[:12]} != {self.sha256[:12]}). "
                "Reconcile the YAML with the issued document before triage runs again."
            )
        return f"verified against {self.pdf} ({self.sha256[:12]})"


@dataclass(frozen=True)
class Branch:
    """One `when:` on a step. Either it ends the triage or it jumps."""

    when: str
    outcome: str | None = None
    goto: str | None = None
    note: str | None = None


@dataclass(frozen=True)
class Step:
    id: str
    section: str
    title: str
    question: str
    tools: tuple[str, ...]
    branches: tuple[Branch, ...]
    next: str | None
    note: str | None
    default_outcome: str | None

    @property
    def cite(self) -> str:
        return f"§{self.section} {self.id}"


@dataclass(frozen=True)
class Outcome:
    key: str
    label: str
    disposition: str
    confidence: float
    issue_found: str
    action_taken: str
    escalate_to: str | None
    ask_do_not_assert: bool = False

    @property
    def is_incident(self) -> bool:
        return self.disposition != "no_incident"


@dataclass(frozen=True)
class Procedure:
    document: Document
    steps: dict[str, Step]
    outcomes: dict[str, Outcome]
    thresholds: dict
    scope_codes: frozenset[str]
    excluded_codes: frozenset[str]
    constraints: tuple[str, ...] = field(default=())

    @property
    def first(self) -> Step:
        return next(iter(self.steps.values()))

    def in_scope(self, code: str | None) -> bool:
        return bool(code) and code in self.scope_codes


@cache
def load(path: Path | None = None) -> Procedure:
    """Parse and validate. Cached — the procedure does not change mid-run."""
    raw = yaml.safe_load((path or SOP_PATH).read_text())
    doc = Document(**{k: raw["document"].get(k) for k in Document.__annotations__})

    outcomes = {
        key: Outcome(key=key, **{k: v for k, v in body.items() if k in Outcome.__annotations__})
        for key, body in raw["outcomes"].items()
    }
    steps: dict[str, Step] = {}
    for s in raw["steps"]:
        steps[s["id"]] = Step(
            id=s["id"],
            section=s["section"],
            title=s["title"],
            question=s.get("question", ""),
            tools=tuple(s.get("tools") or ()),
            branches=tuple(Branch(**b) for b in s.get("branches") or ()),
            next=s.get("next"),
            note=s.get("note"),
            default_outcome=s.get("default_outcome"),
        )

    procedure = Procedure(
        document=doc,
        steps=steps,
        outcomes=outcomes,
        thresholds=raw["thresholds"],
        scope_codes=frozenset(raw["scope"]["codes"]),
        excluded_codes=frozenset(raw["scope"].get("excludes") or ()),
        constraints=tuple(c["rule"] for c in raw.get("constraints") or ()),
    )
    _validate(procedure)
    return procedure


def _validate(p: Procedure) -> None:
    """Every jump lands somewhere and every outcome exists. Checked at load,
    because a dangling `goto` discovered halfway through a triage run is a
    half-recorded procedure — the one state the audit trail must never be in.
    """
    for step in p.steps.values():
        if step.next and step.next not in p.steps:
            raise InvalidProcedure(f"{step.id}.next -> unknown step {step.next}")
        if step.default_outcome and step.default_outcome not in p.outcomes:
            raise InvalidProcedure(f"{step.id}.default_outcome -> unknown {step.default_outcome}")
        for branch in step.branches:
            if branch.goto and branch.goto not in p.steps:
                raise InvalidProcedure(f"{step.id}[{branch.when}].goto -> unknown {branch.goto}")
            if branch.outcome and branch.outcome not in p.outcomes:
                raise InvalidProcedure(f"{step.id}[{branch.when}] -> unknown {branch.outcome}")
            if not branch.goto and not branch.outcome:
                raise InvalidProcedure(f"{step.id}[{branch.when}] does nothing")
    terminal = [s for s in p.steps.values() if s.default_outcome]
    if not terminal:
        raise InvalidProcedure("no step carries a default_outcome — triage could not terminate")


class InvalidProcedure(ValueError):
    """The YAML is not a walkable procedure. Raised at load, never mid-run."""


class SupersededProcedure(RuntimeError):
    """The controlled PDF has moved and the executable twin has not."""
