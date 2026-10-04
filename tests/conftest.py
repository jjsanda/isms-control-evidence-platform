"""Shared fixtures: a pinned clock and small factories for valid domain objects.

The factories return fully-valid instances with sensible defaults; pass keyword overrides to vary
one field at a time (the pattern most tests use to exercise a single validator or code path).
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

import pytest

from icep.clock import FrozenClock
from icep.domain import (
    AuditStatus,
    ControlStatus,
    Evidence,
    EvidenceType,
    InclusionReason,
    Nis2Area,
    OwnerRef,
    Risk,
    Theme,
    TreatmentOption,
)
from icep.domain.control import Control

TODAY = date(2026, 7, 7)


@pytest.fixture
def today() -> date:
    return TODAY


@pytest.fixture
def clock() -> FrozenClock:
    return FrozenClock.at("2026-07-07")


@pytest.fixture
def owner() -> OwnerRef:
    return OwnerRef(name="Alex Rossi", role="CISO", email="alex.rossi@paketport.example")


@pytest.fixture
def make_control(owner: OwnerRef) -> Callable[..., Control]:
    def _make(**over: Any) -> Control:
        base: dict[str, Any] = {
            "id": "A.8.16",
            "title": "Monitoring activities",
            "theme": Theme.TECHNOLOGICAL,
            "category": "Monitoring",
            "objective": "Detect anomalous behaviour on locker edge devices and the backend.",
            "owner": owner,
            "status": ControlStatus.OPERATING,
            "maturity": 3,
            "applicable": True,
            "inclusion_reason": InclusionReason.RISK,
            "soa_justification": "Required to detect intrusions on internet-facing lockers.",
            "nis2_areas": [Nis2Area.INCIDENT_HANDLING],
            "last_review": date(2026, 1, 15),
            "next_review": date(2026, 12, 1),
            "audit_status": AuditStatus.ACCEPTED,
        }
        base.update(over)
        return Control(**base)

    return _make


@pytest.fixture
def make_risk(owner: OwnerRef) -> Callable[..., Risk]:
    def _make(**over: Any) -> Risk:
        base: dict[str, Any] = {
            "id": "R-001",
            "title": "Firmware tampering on street-sited lockers",
            "description": "An attacker with physical access flashes malicious firmware.",
            "owner": owner,
            "asset": "Locker edge device",
            "threat": "Physical tampering",
            "vulnerability": "Unsigned firmware updates",
            "inherent_likelihood": 4,
            "inherent_impact": 5,
            "treatment": TreatmentOption.MITIGATE,
            "mitigation": "Secure boot + signed OTA images.",
            "control_refs": ["A.8.16"],
            "residual_likelihood": 2,
            "residual_impact": 4,
            "target_date": date(2026, 9, 30),
            "review_date": date(2026, 12, 1),
        }
        base.update(over)
        return Risk(**base)

    return _make


@pytest.fixture
def make_evidence(owner: OwnerRef) -> Callable[..., Evidence]:
    def _make(**over: Any) -> Evidence:
        base: dict[str, Any] = {
            "id": "EV-001",
            "title": "sshd hardening check",
            "type": EvidenceType.CONFIG_EXPORT,
            "control_refs": ["A.8.16"],
            "collected_on": date(2026, 6, 1),
            "collected_by": owner,
            "artifact_path": "evidence/artifacts/ssh-hardening-report.md",
            "valid_from": date(2026, 6, 1),
            "valid_until": date(2026, 12, 1),
            "source": "collector:ssh_hardening",
            "audit_status": AuditStatus.ACCEPTED,
        }
        base.update(over)
        return Evidence(**base)

    return _make
