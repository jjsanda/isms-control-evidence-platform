"""NIS2 mapping: Art. 21(2) risk-management measures and Art. 23 incident-reporting deadlines.

``NIS2_ARTICLE`` and ``NIS2_TITLE`` pin each :class:`~icep.domain.enums.Nis2Area` to its exact
directive reference and short title, so the dashboard and audit pack cite NIS2 precisely rather
than paraphrasing it.
"""

from __future__ import annotations

from pydantic import Field

from icep.domain.common import ControlId, IcepModel, OwnerRef
from icep.domain.enums import Nis2Area, ReportingPhase

__all__ = ["NIS2_ARTICLE", "NIS2_TITLE", "Nis2Measure", "Nis2Reporting"]

# NIS2 Directive (EU) 2022/2555 -- Art. 21(2)(a)-(j) plus the Art. 20 management-body duty.
NIS2_ARTICLE: dict[Nis2Area, str] = {
    Nis2Area.RISK_ANALYSIS: "Art. 21(2)(a)",
    Nis2Area.INCIDENT_HANDLING: "Art. 21(2)(b)",
    Nis2Area.BUSINESS_CONTINUITY: "Art. 21(2)(c)",
    Nis2Area.SUPPLY_CHAIN: "Art. 21(2)(d)",
    Nis2Area.ACQ_DEV_MAINTENANCE: "Art. 21(2)(e)",
    Nis2Area.EFFECTIVENESS: "Art. 21(2)(f)",
    Nis2Area.CYBER_HYGIENE_TRAINING: "Art. 21(2)(g)",
    Nis2Area.CRYPTOGRAPHY: "Art. 21(2)(h)",
    Nis2Area.HR_ACCESS_ASSET: "Art. 21(2)(i)",
    Nis2Area.MFA_COMMS: "Art. 21(2)(j)",
    Nis2Area.MANAGEMENT_ACCOUNTABILITY: "Art. 20",
}

NIS2_TITLE: dict[Nis2Area, str] = {
    Nis2Area.RISK_ANALYSIS: "Risk analysis and information system security policies",
    Nis2Area.INCIDENT_HANDLING: "Incident handling",
    Nis2Area.BUSINESS_CONTINUITY: "Business continuity, backup management and crisis management",
    Nis2Area.SUPPLY_CHAIN: "Supply chain security",
    Nis2Area.ACQ_DEV_MAINTENANCE: "Security in acquisition, development and maintenance",
    Nis2Area.EFFECTIVENESS: "Policies to assess the effectiveness of risk-management measures",
    Nis2Area.CYBER_HYGIENE_TRAINING: "Basic cyber hygiene practices and security training",
    Nis2Area.CRYPTOGRAPHY: "Cryptography and, where appropriate, encryption",
    Nis2Area.HR_ACCESS_ASSET: "Human resources security, access control and asset management",
    Nis2Area.MFA_COMMS: "Multi-factor authentication and secured communications",
    Nis2Area.MANAGEMENT_ACCOUNTABILITY: "Governance and management-body accountability",
}


class Nis2Measure(IcepModel):
    """One NIS2 measure and the Annex A controls that implement it at the organisation."""

    area: Nis2Area
    article: str = Field(
        min_length=1, max_length=20, description="Directive reference, e.g. 'Art. 21(2)(b)'."
    )
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=1200)
    control_refs: list[ControlId] = Field(
        min_length=1, description="Controls that satisfy this measure."
    )


class Nis2Reporting(IcepModel):
    """One NIS2 Art. 23 incident-reporting obligation and its statutory deadline."""

    phase: ReportingPhase
    deadline_label: str = Field(
        min_length=1, max_length=40, description="e.g. '24 hours', '72 hours', '1 month'."
    )
    deadline_hours: int | None = Field(
        default=None, ge=1, description="Deadline in hours, when fixed."
    )
    trigger: str = Field(min_length=1, max_length=300, description="What starts the clock.")
    content: str = Field(
        min_length=1, max_length=600, description="What must be reported at this phase."
    )
    owner: OwnerRef
    procedure_ref: str = Field(default="", max_length=120)
