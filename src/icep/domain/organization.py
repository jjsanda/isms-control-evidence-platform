"""The :class:`OrganizationProfile`: ISMS scope and context for the fictional company.

This backs the audit pack's executive summary and the dashboard's context, and pins down the
ISO 27001 clause-4 "context of the organisation" and scope statement in one auditable record.
"""

from __future__ import annotations

from pydantic import Field

from icep.domain.common import IcepModel, OwnerRef

__all__ = ["OrganizationProfile"]


class OrganizationProfile(IcepModel):
    """Who the ISMS is for, what it covers, and who is accountable."""

    name: str = Field(min_length=1, max_length=200)
    legal_form: str = Field(min_length=1, max_length=80)
    sector: str = Field(min_length=1, max_length=200)
    certification_target: str = Field(
        min_length=1, max_length=120, description="e.g. 'ISO/IEC 27001:2022'."
    )
    isms_scope: str = Field(
        min_length=1, max_length=1200, description="The formal ISO 27001 scope statement."
    )
    scope_boundary: str = Field(
        min_length=1, max_length=1200, description="What is in and out of scope."
    )
    policy_statement: str = Field(
        min_length=1, max_length=1200, description="Top-management ISMS commitment."
    )
    employees: int = Field(ge=1, description="Approximate headcount within scope.")
    locations: list[str] = Field(default_factory=list)
    key_services: list[str] = Field(default_factory=list)
    key_assets: list[str] = Field(default_factory=list)
    isms_owner: OwnerRef
    management_representative: OwnerRef
