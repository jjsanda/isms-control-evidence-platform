"""Shared building blocks: the strict model base, the owner value object, and typed id aliases.

The id aliases are ``Annotated[str, Field(pattern=...)]``: they make the *shape* of every
identifier part of the schema (so ``A.8.16``, ``R-001``, ``EV-004`` are validated on load), while
the *existence* of a referenced id is checked separately by the repository's cross-reference pass.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "IcepModel",
    "OwnerRef",
    "Email",
    "ControlId",
    "RiskId",
    "EvidenceId",
    "PolicyId",
    "ActionId",
    "InitiativeId",
    "TrainingId",
    "control_sort_key",
]


class IcepModel(BaseModel):
    """Base for every register entity: unknown keys are rejected so schema drift fails fast."""

    model_config = ConfigDict(extra="forbid")


# A light, dependency-free email check (avoids pulling in email-validator for a portfolio demo).
Email = Annotated[str, Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]

# Identifier shapes, enforced at load time.
ControlId = Annotated[str, Field(pattern=r"^A\.\d+\.\d+$")]
RiskId = Annotated[str, Field(pattern=r"^R-\d{3}$")]
EvidenceId = Annotated[str, Field(pattern=r"^EV-\d{3}$")]
PolicyId = Annotated[str, Field(pattern=r"^POL-[A-Z]{2,6}$")]
ActionId = Annotated[str, Field(pattern=r"^CAPA-\d{3}$")]
InitiativeId = Annotated[str, Field(pattern=r"^INIT-\d{3}$")]
TrainingId = Annotated[str, Field(pattern=r"^TRN-\d{3}$")]


class OwnerRef(BaseModel):
    """A named, accountable person (control owner, risk owner, action owner, ...).

    Frozen so owners can be safely shared/compared; email is optional and lightly validated.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=120)
    email: Email | None = None


def control_sort_key(control_id: str) -> tuple[int, int, str]:
    """Sort key for Annex A ids: (clause, number, id) so numbers order numerically, not lexically.

    >>> sorted(["A.8.16", "A.8.2", "A.5.1"], key=control_sort_key)
    ['A.5.1', 'A.8.2', 'A.8.16']
    """
    parts = control_id.split(".")
    try:
        return (int(parts[1]), int(parts[2]), control_id)
    except (IndexError, ValueError):
        return (0, 0, control_id)
