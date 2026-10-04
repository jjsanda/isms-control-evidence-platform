"""Build the deterministic manifest that seals an audit pack.

The manifest records the tool version, the pinned generation timestamp, a headline summary, and a
SHA-256 for every file in the pack and every referenced evidence artifact -- so the whole bundle is
tamper-evident and reproducible.
"""

from __future__ import annotations

from datetime import date

from icep.metrics import Metrics

__all__ = ["build_manifest"]


def build_manifest(
    pack_files: dict[str, str],
    evidence_hashes: dict[str, str],
    metrics: Metrics,
    tool_version: str,
    generated_at: str,
    today: date,
) -> dict[str, object]:
    """Assemble the audit-pack manifest as a JSON-serialisable dict (keys are sorted on write)."""
    return {
        "tool": "icep",
        "version": tool_version,
        "generated_at": generated_at,
        "report_date": today.isoformat(),
        "summary": {
            "controls_documented": metrics.documented_total,
            "controls_applicable": metrics.soa_applicable,
            "controls_implemented": metrics.implemented_controls,
            "implementation_pct": metrics.implementation_pct,
            "nis2_overall_pct": metrics.nis2_overall_pct,
            "risks_total": metrics.risk_total,
            "risks_accepted": metrics.risks_accepted,
            "risks_high_or_critical_open": metrics.risks_high_or_critical_open,
            "actions_open": metrics.action_open,
            "actions_overdue": metrics.action_overdue,
            "evidence_total": metrics.evidence_total,
            "evidence_expired": metrics.evidence_expired,
        },
        "files": dict(sorted(pack_files.items())),
        "evidence_artifacts": dict(sorted(evidence_hashes.items())),
    }
