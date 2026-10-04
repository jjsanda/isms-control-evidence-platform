"""The :class:`ImprovementAction` (CAPA): the ISMS continual-improvement backlog.

Actions are the "Act" of Plan-Do-Check-Act -- they originate from audits, management reviews, risk
assessments, incidents or vulnerabilities, carry an owner and a due date, and close with a
verification note.
"""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from icep.domain.common import ActionId, ControlId, IcepModel, OwnerRef, RiskId
from icep.domain.enums import ActionSource, ActionStatus

__all__ = ["ImprovementAction"]

_CLOSED_STATES = frozenset({ActionStatus.DONE, ActionStatus.VERIFIED, ActionStatus.CANCELLED})


class ImprovementAction(IcepModel):
    """A corrective or preventive action tracked to closure."""

    id: ActionId
    title: str = Field(min_length=1, max_length=200)
    source: ActionSource
    description: str = Field(min_length=1, max_length=1500)
    owner: OwnerRef
    status: ActionStatus
    opened_on: date
    due_date: date
    closed_on: date | None = None
    control_refs: list[ControlId] = Field(default_factory=list)
    risk_refs: list[RiskId] = Field(default_factory=list)
    verification: str = Field(default="", max_length=1000, description="How closure was verified.")

    @property
    def is_open(self) -> bool:
        return self.status not in _CLOSED_STATES

    def is_overdue(self, today: date) -> bool:
        """Whether the action is still open and past its due date."""
        return self.is_open and self.due_date < today

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.status in _CLOSED_STATES and self.closed_on is None:
            raise ValueError(f"{self.id}: a {self.status.value} action must record closed_on")
        if self.closed_on is not None and self.closed_on < self.opened_on:
            raise ValueError(f"{self.id}: closed_on precedes opened_on")
        return self
