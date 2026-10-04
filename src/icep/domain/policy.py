"""The :class:`Policy` record: an approved ISMS document that controls point back to."""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from icep.domain.common import ControlId, IcepModel, OwnerRef, PolicyId

__all__ = ["Policy"]


class Policy(IcepModel):
    """A versioned, approved policy document within the ISMS."""

    id: PolicyId
    title: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=20, description="e.g. '1.3'.")
    owner: OwnerRef
    approved_on: date
    next_review: date
    summary: str = Field(min_length=1, max_length=1000)
    control_refs: list[ControlId] = Field(default_factory=list)
    document_path: str = Field(default="", max_length=300)

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.next_review < self.approved_on:
            raise ValueError(f"{self.id}: next_review precedes approved_on")
        return self
