"""The :class:`Risk` and its inherent/residual scoring.

Each risk records the threat/vulnerability against an asset, the *inherent* likelihood x impact
before treatment, the treatment and controls applied, and the *residual* likelihood x impact after
treatment. Scores and bands are computed (never hand-stored) via ``workflow.scoring`` so the
register and the heatmap can never disagree.
"""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from icep.domain.common import ControlId, IcepModel, OwnerRef, RiskId
from icep.domain.enums import AcceptanceDecision, RiskBand, TreatmentOption
from icep.workflow.scoring import band, residual_reduction, score

__all__ = ["Risk"]


class Risk(IcepModel):
    """A risk in the register, with inherent and residual assessments."""

    id: RiskId
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1500)
    owner: OwnerRef
    asset: str = Field(min_length=1, max_length=200, description="The asset or service at risk.")
    threat: str = Field(min_length=1, max_length=400)
    vulnerability: str = Field(min_length=1, max_length=400)
    inherent_likelihood: int = Field(ge=1, le=5)
    inherent_impact: int = Field(ge=1, le=5)
    treatment: TreatmentOption
    mitigation: str = Field(
        min_length=1, max_length=1500, description="Planned or applied treatment."
    )
    control_refs: list[ControlId] = Field(default_factory=list)
    residual_likelihood: int = Field(ge=1, le=5)
    residual_impact: int = Field(ge=1, le=5)
    target_date: date
    review_date: date
    acceptance: AcceptanceDecision = AcceptanceDecision.PENDING
    accepted_by: OwnerRef | None = None
    acceptance_rationale: str = Field(default="", max_length=1000)

    @property
    def inherent_score(self) -> int:
        return score(self.inherent_likelihood, self.inherent_impact)

    @property
    def residual_score(self) -> int:
        return score(self.residual_likelihood, self.residual_impact)

    @property
    def inherent_band(self) -> RiskBand:
        return band(self.inherent_score)

    @property
    def residual_band(self) -> RiskBand:
        return band(self.residual_score)

    @property
    def reduction(self) -> int:
        """Score points removed by treatment (inherent - residual)."""
        return residual_reduction(self.inherent_score, self.residual_score)

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.residual_likelihood > self.inherent_likelihood:
            raise ValueError(f"{self.id}: residual likelihood cannot exceed inherent likelihood")
        if self.residual_impact > self.inherent_impact:
            raise ValueError(f"{self.id}: residual impact cannot exceed inherent impact")
        if self.acceptance is AcceptanceDecision.ACCEPTED and self.accepted_by is None:
            raise ValueError(
                f"{self.id}: an accepted risk must record who accepted it (accepted_by)"
            )
        return self
