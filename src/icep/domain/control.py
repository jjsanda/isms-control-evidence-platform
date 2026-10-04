"""The :class:`Control` -- the heart of the register.

A control ties an ISO/IEC 27001:2022 Annex A requirement to an accountable owner, an
implementation status, the policies and evidence that back it, the risks it treats, the NIS2
measures it supports, and its place in the audit review cycle. Cross-references are validated for
*shape* here and for *existence* by the repository.
"""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from icep.domain.common import ControlId, EvidenceId, IcepModel, OwnerRef, PolicyId, RiskId
from icep.domain.enums import AuditStatus, ControlStatus, InclusionReason, Nis2Area, Theme

__all__ = ["Control"]


class Control(IcepModel):
    """A single Annex A control as implemented (or excluded) at the organisation."""

    id: ControlId
    title: str = Field(min_length=1, max_length=200)
    theme: Theme
    category: str = Field(
        min_length=1, max_length=120, description="Annex A grouping, e.g. 'Access control'."
    )
    objective: str = Field(
        min_length=1, max_length=1000, description="What the control is meant to achieve."
    )
    owner: OwnerRef
    status: ControlStatus
    maturity: int = Field(
        ge=1, le=5, description="Capability maturity 1 (initial) - 5 (optimising)."
    )
    applicable: bool = True
    inclusion_reason: InclusionReason
    soa_justification: str = Field(
        min_length=1,
        max_length=1000,
        description="Statement-of-Applicability rationale for inclusion or exclusion.",
    )
    policy_refs: list[PolicyId] = Field(default_factory=list)
    evidence_refs: list[EvidenceId] = Field(default_factory=list)
    risk_refs: list[RiskId] = Field(default_factory=list)
    nis2_areas: list[Nis2Area] = Field(default_factory=list)
    implementation_notes: str = Field(default="", max_length=2000)
    last_review: date | None = None
    next_review: date
    audit_status: AuditStatus = AuditStatus.DRAFT
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check(self) -> Self:
        if not self.applicable and self.status is not ControlStatus.NOT_APPLICABLE:
            raise ValueError(f"{self.id}: an excluded control must have status 'not_applicable'")
        if self.applicable and self.status is ControlStatus.NOT_APPLICABLE:
            raise ValueError(
                f"{self.id}: an applicable control cannot have status 'not_applicable'"
            )
        if self.last_review is not None and self.next_review < self.last_review:
            raise ValueError(f"{self.id}: next_review precedes last_review")
        return self
