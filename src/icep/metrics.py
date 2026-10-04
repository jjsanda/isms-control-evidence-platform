"""Derived KPIs for the dashboard and audit pack.

Everything here is computed from the repository as of a given ``today`` -- nothing is stored. That
keeps the numbers honest (they always reflect the current register and the pinned audit date) and
deterministic (same register + same date -> same metrics).
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from enum import Enum

from icep.domain import (
    AcceptanceDecision,
    AuditStatus,
    Control,
    ControlStatus,
    Nis2Area,
    ReviewState,
    Risk,
    RiskBand,
)
from icep.repository import IcepRepository
from icep.workflow import classify, effective_status

__all__ = ["Metrics", "compute_metrics"]

_IMPLEMENTED_STATES = frozenset({ControlStatus.OPERATING, ControlStatus.IMPLEMENTED})


@dataclass(frozen=True)
class Metrics:
    """A snapshot of ISMS KPIs as of :attr:`generated_on`."""

    generated_on: date
    warn_days: int
    # catalog / Statement of Applicability
    catalog_total: int
    soa_applicable: int
    soa_not_applicable: int
    # documented controls
    documented_total: int
    status_counts: dict[ControlStatus, int]
    audit_counts: dict[AuditStatus, int]
    implemented_controls: int
    implementation_pct: float
    documentation_pct: float
    # control review windows
    review_counts: dict[ReviewState, int]
    overdue_controls: list[Control]
    due_soon_controls: list[Control]
    # evidence
    evidence_total: int
    evidence_expired: int
    evidence_expiring: int
    # risks
    risk_total: int
    inherent_band_counts: dict[RiskBand, int]
    residual_band_counts: dict[RiskBand, int]
    risks_accepted: int
    risks_high_or_critical_open: int
    top_residual_risks: list[Risk]
    # NIS2
    nis2_area_readiness: dict[Nis2Area, float]
    nis2_overall_pct: float
    # improvement actions
    action_total: int
    action_open: int
    action_overdue: int
    # awareness training
    training_completions: int
    training_passed: int
    training_pass_pct: float


def _count_enum[E: Enum](values: list[E], enum_cls: type[E]) -> dict[E, int]:
    counts = Counter(values)
    return {member: counts.get(member, 0) for member in enum_cls}


def _pct(part: int, whole: int) -> float:
    return round(100.0 * part / whole, 1) if whole else 0.0


def compute_metrics(repo: IcepRepository, today: date, warn_days: int = 30) -> Metrics:
    """Compute the full KPI snapshot from ``repo`` as of ``today``."""
    controls = repo.controls

    status_counts = _count_enum([c.status for c in controls], ControlStatus)
    audit_counts = _count_enum(
        [effective_status(c.audit_status, c.next_review, today) for c in controls], AuditStatus
    )

    documented_total = len(controls)
    implemented = sum(1 for c in controls if c.status in _IMPLEMENTED_STATES)
    applicable = len(repo.applicable_control_ids)

    review_states = {c.id: classify(c.next_review, today, warn_days) for c in controls}
    review_counts = _count_enum(list(review_states.values()), ReviewState)
    overdue_controls = sorted(
        (c for c in controls if review_states[c.id] is ReviewState.OVERDUE),
        key=lambda c: (c.next_review, c.id),
    )
    due_soon_controls = sorted(
        (c for c in controls if review_states[c.id] is ReviewState.DUE_SOON),
        key=lambda c: (c.next_review, c.id),
    )

    evidence_expired = sum(1 for e in repo.evidence if e.is_expired(today))
    evidence_expiring = sum(
        1
        for e in repo.evidence
        if not e.is_expired(today)
        and classify(e.valid_until, today, warn_days) is ReviewState.DUE_SOON
    )

    risks = repo.risks
    inherent_bands = _count_enum([r.inherent_band for r in risks], RiskBand)
    residual_bands = _count_enum([r.residual_band for r in risks], RiskBand)
    high_or_critical_open = sum(
        1
        for r in risks
        if r.residual_band in {RiskBand.HIGH, RiskBand.CRITICAL}
        and r.acceptance is not AcceptanceDecision.ACCEPTED
    )
    top_residual = sorted(risks, key=lambda r: (-r.residual_score, -r.inherent_score, r.id))[:5]

    nis2_readiness: dict[Nis2Area, float] = {}
    for area in Nis2Area:
        mapped = repo.controls_for_nis2_area(area)
        ready = sum(1 for c in mapped if c.status in _IMPLEMENTED_STATES)
        nis2_readiness[area] = _pct(ready, len(mapped))
    nis2_overall = (
        round(sum(nis2_readiness.values()) / len(nis2_readiness), 1) if nis2_readiness else 0.0
    )

    actions_open = sum(1 for a in repo.actions if a.is_open)
    actions_overdue = sum(1 for a in repo.actions if a.is_overdue(today))

    passed = sum(1 for rec in repo.completions if rec.passed)

    return Metrics(
        generated_on=today,
        warn_days=warn_days,
        catalog_total=len(repo.catalog),
        soa_applicable=applicable,
        soa_not_applicable=len(repo.soa) - applicable,
        documented_total=documented_total,
        status_counts=status_counts,
        audit_counts=audit_counts,
        implemented_controls=implemented,
        implementation_pct=_pct(implemented, documented_total),
        documentation_pct=_pct(
            len(repo.documented_control_ids & repo.applicable_control_ids), applicable
        ),
        review_counts=review_counts,
        overdue_controls=overdue_controls,
        due_soon_controls=due_soon_controls,
        evidence_total=len(repo.evidence),
        evidence_expired=evidence_expired,
        evidence_expiring=evidence_expiring,
        risk_total=len(risks),
        inherent_band_counts=inherent_bands,
        residual_band_counts=residual_bands,
        risks_accepted=sum(1 for r in risks if r.acceptance is AcceptanceDecision.ACCEPTED),
        risks_high_or_critical_open=high_or_critical_open,
        top_residual_risks=top_residual,
        nis2_area_readiness=nis2_readiness,
        nis2_overall_pct=nis2_overall,
        action_total=len(repo.actions),
        action_open=actions_open,
        action_overdue=actions_overdue,
        training_completions=len(repo.completions),
        training_passed=passed,
        training_pass_pct=_pct(passed, len(repo.completions)),
    )
