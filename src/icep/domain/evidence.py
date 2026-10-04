"""The :class:`Evidence` record: a hash-anchored pointer to an audit artifact.

Evidence supports at least one control, has a collection date and a validity window, and carries a
SHA-256 of the artifact it points at. Hashes are *not* hand-authored -- the seed step computes them
into ``evidence/manifest.json`` and the loader can verify each record against that manifest, so a
tampered or stale artifact is detectable.
"""

from __future__ import annotations

from datetime import date
from typing import Self

from pydantic import Field, model_validator

from icep.domain.common import ControlId, EvidenceId, IcepModel, OwnerRef
from icep.domain.enums import AuditStatus, EvidenceType

__all__ = ["Evidence"]


class Evidence(IcepModel):
    """One piece of evidence backing one or more controls."""

    id: EvidenceId
    title: str = Field(min_length=1, max_length=200)
    type: EvidenceType
    control_refs: list[ControlId] = Field(
        min_length=1, description="Controls this evidence supports."
    )
    collected_on: date
    collected_by: OwnerRef
    artifact_path: str = Field(
        min_length=1,
        max_length=300,
        description="Path to the artifact, relative to the repository root.",
    )
    sha256: str | None = Field(
        default=None,
        pattern=r"^[0-9a-f]{64}$",
        description="SHA-256 of the artifact; verified against evidence/manifest.json when present.",
    )
    valid_from: date
    valid_until: date
    source: str = Field(
        default="manual", max_length=120, description="e.g. 'collector:ssh_hardening'."
    )
    audit_status: AuditStatus = AuditStatus.DRAFT
    notes: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.valid_until < self.valid_from:
            raise ValueError(f"{self.id}: valid_until precedes valid_from")
        if self.valid_from < self.collected_on:
            raise ValueError(f"{self.id}: valid_from precedes collected_on")
        return self

    def is_expired(self, today: date) -> bool:
        """Whether the evidence's validity window has closed as of ``today``."""
        return self.valid_until < today
