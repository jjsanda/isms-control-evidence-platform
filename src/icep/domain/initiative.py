"""The :class:`Initiative`: a security project / proof-of-concept, concept through acceptance.

The register ships one worked example -- "centralised Linux audit logging" -- with a concept, a
task list, testable acceptance criteria (each optionally linked to the evidence that satisfies it),
and the controls and NIS2 areas it advances. This is the "security project from concept to PoC to
implementation" story an ISMS/compliance role is expected to run.
"""

from __future__ import annotations

from pydantic import Field

from icep.domain.common import ControlId, EvidenceId, IcepModel, InitiativeId, OwnerRef
from icep.domain.enums import InitiativeStatus, Nis2Area, TaskStatus

__all__ = ["Task", "AcceptanceCriterion", "Initiative"]


class Task(IcepModel):
    """One task within an initiative's implementation plan."""

    id: str = Field(min_length=1, max_length=20, description="e.g. 'T1'.")
    title: str = Field(min_length=1, max_length=200)
    status: TaskStatus
    owner: str = Field(default="", max_length=120)


class AcceptanceCriterion(IcepModel):
    """A testable definition-of-done for the initiative, optionally proven by an evidence record."""

    id: str = Field(min_length=1, max_length=20, description="e.g. 'AC1'.")
    text: str = Field(min_length=1, max_length=400)
    met: bool = False
    evidence_ref: EvidenceId | None = None


class Initiative(IcepModel):
    """A security initiative / PoC tracked inside the ISMS."""

    id: InitiativeId
    title: str = Field(min_length=1, max_length=200)
    status: InitiativeStatus
    owner: OwnerRef
    concept: str = Field(
        min_length=1, max_length=4000, description="The problem and proposed approach."
    )
    objective: str = Field(min_length=1, max_length=600)
    control_refs: list[ControlId] = Field(default_factory=list)
    nis2_areas: list[Nis2Area] = Field(default_factory=list)
    tasks: list[Task] = Field(default_factory=list)
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)
    evidence_refs: list[EvidenceId] = Field(default_factory=list)

    @property
    def criteria_met(self) -> int:
        return sum(1 for c in self.acceptance_criteria if c.met)

    @property
    def tasks_done(self) -> int:
        return sum(1 for t in self.tasks if t.status is TaskStatus.DONE)
