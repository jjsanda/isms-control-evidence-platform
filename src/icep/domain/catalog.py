"""The ISO/IEC 27001:2022 Annex A reference catalog and the Statement of Applicability.

:class:`AnnexAControl` is a catalog row (all 93 controls, by theme, flagging the 11 new-in-2022
controls). :class:`SoAEntry` is one Statement-of-Applicability decision per catalog control:
applicable or not, why, and -- for applicable controls -- the register is expected to hold a fully
documented :class:`~icep.domain.control.Control` with the same id (the repository checks that).
"""

from __future__ import annotations

from pydantic import Field

from icep.domain.common import ControlId, IcepModel
from icep.domain.enums import InclusionReason, Theme

__all__ = ["AnnexAControl", "SoAEntry"]


class AnnexAControl(IcepModel):
    """A single reference control from ISO/IEC 27001:2022 Annex A."""

    id: ControlId
    title: str = Field(min_length=1, max_length=200)
    theme: Theme
    is_new_2022: bool = Field(default=False, description="Introduced in the 2022 revision.")


class SoAEntry(IcepModel):
    """One Statement-of-Applicability decision for a catalog control."""

    control_id: ControlId
    applicable: bool
    inclusion_reason: InclusionReason
    justification: str = Field(min_length=1, max_length=1000)
