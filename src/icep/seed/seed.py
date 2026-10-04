"""Deterministic seeding: generate evidence artifacts, hashes, a manifest and a metrics snapshot.

``make seed-demo-data`` calls :func:`seed`. It (1) loads and validates the register, (2) for every
evidence record either runs the referenced collector over the committed samples or renders a small
attestation stub, writing the artifact to its ``artifact_path``, (3) SHA-256s each artifact into
``evidence/manifest.json``, and (4) writes a ``metrics.json`` snapshot and a human-readable
``index.md``. With the clock pinned (``ICEP_NOW``), re-running produces byte-identical output -- the
determinism the CI gate checks with ``git diff --exit-code``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from icep import __version__
from icep.clock import Clock, default_clock
from icep.collectors import (
    access_review,
    auditd_coverage,
    backup_restore,
    ssh_hardening,
    vuln_scan,
)
from icep.collectors.base import CollectorResult, render_markdown
from icep.config import Settings, get_settings
from icep.domain import Evidence
from icep.integrity import sha256_text, write_json
from icep.metrics import Metrics, compute_metrics
from icep.repository import IcepRepository

__all__ = ["SeedError", "SeedResult", "seed", "read_manifest", "COLLECTORS"]

COLLECTORS: dict[str, Callable[[Path, date], CollectorResult]] = {
    ssh_hardening.NAME: ssh_hardening.run,
    auditd_coverage.NAME: auditd_coverage.run,
    vuln_scan.NAME: vuln_scan.run,
    backup_restore.NAME: backup_restore.run,
    access_review.NAME: access_review.run,
}


class SeedError(Exception):
    """Raised when the register cannot be seeded (integrity errors or an unknown collector)."""


@dataclass(frozen=True)
class SeedResult:
    artifacts: dict[str, str]
    collector_runs: int
    manifest_path: Path
    metrics_path: Path
    index_path: Path


def _render_manual_artifact(evidence: Evidence, today: date) -> str:
    """Render a small attestation artifact for a manually-collected evidence record."""
    controls = ", ".join(evidence.control_refs)
    return "\n".join(
        [
            f"# {evidence.title}",
            "",
            f"- **Evidence id:** {evidence.id}",
            f"- **Type:** {evidence.type.value}",
            f"- **Controls:** {controls}",
            f"- **Collected on:** {evidence.collected_on.isoformat()} by "
            f"{evidence.collected_by.name} ({evidence.collected_by.role})",
            f"- **Valid:** {evidence.valid_from.isoformat()} to {evidence.valid_until.isoformat()}",
            f"- **Report date:** {today.isoformat()}",
            "",
            f"> {evidence.notes}" if evidence.notes else "> Attested evidence record.",
            "",
            "_Illustrative evidence artifact for the PaketPort Systems ISMS portfolio "
            "(fictional company, no confidential data)._",
            "",
        ]
    )


def _artifact_content(evidence: Evidence, samples_dir: Path, today: date) -> str:
    if evidence.source.startswith("collector:"):
        name = evidence.source.split(":", 1)[1]
        run = COLLECTORS.get(name)
        if run is None:
            raise SeedError(
                f"{evidence.id}: unknown collector '{name}' in source '{evidence.source}'"
            )
        return render_markdown(run(samples_dir, today))
    return _render_manual_artifact(evidence, today)


def _metrics_summary(metrics: Metrics) -> dict[str, object]:
    return {
        "generated_on": metrics.generated_on.isoformat(),
        "controls": {
            "catalog_total": metrics.catalog_total,
            "applicable": metrics.soa_applicable,
            "documented": metrics.documented_total,
            "implemented": metrics.implemented_controls,
            "implementation_pct": metrics.implementation_pct,
            "documentation_pct": metrics.documentation_pct,
            "status": {k.value: v for k, v in metrics.status_counts.items()},
            "audit": {k.value: v for k, v in metrics.audit_counts.items()},
            "reviews": {k.value: v for k, v in metrics.review_counts.items()},
            "overdue": [c.id for c in metrics.overdue_controls],
            "due_soon": [c.id for c in metrics.due_soon_controls],
        },
        "risks": {
            "total": metrics.risk_total,
            "inherent_bands": {k.value: v for k, v in metrics.inherent_band_counts.items()},
            "residual_bands": {k.value: v for k, v in metrics.residual_band_counts.items()},
            "accepted": metrics.risks_accepted,
            "high_or_critical_open": metrics.risks_high_or_critical_open,
            "top_residual": [
                {
                    "id": r.id,
                    "title": r.title,
                    "residual_score": r.residual_score,
                    "band": r.residual_band.value,
                }
                for r in metrics.top_residual_risks
            ],
        },
        "nis2": {
            "overall_pct": metrics.nis2_overall_pct,
            "area_readiness": {k.value: v for k, v in metrics.nis2_area_readiness.items()},
        },
        "evidence": {
            "total": metrics.evidence_total,
            "expired": metrics.evidence_expired,
            "expiring": metrics.evidence_expiring,
        },
        "actions": {
            "total": metrics.action_total,
            "open": metrics.action_open,
            "overdue": metrics.action_overdue,
        },
        "training": {
            "completions": metrics.training_completions,
            "passed": metrics.training_passed,
            "pass_pct": metrics.training_pass_pct,
        },
    }


def _render_index(repo: IcepRepository, artifacts: dict[str, str], today: date) -> str:
    lines = [
        "# Evidence index",
        "",
        f"Generated {today.isoformat()} from the PaketPort Systems ISMS register. "
        f"{len(artifacts)} artifacts, each anchored by a SHA-256 in `manifest.json`.",
        "",
        "| Evidence | Title | Type | Controls | Collected | Valid until | SHA-256 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for evidence in sorted(repo.evidence, key=lambda e: e.id):
        digest = artifacts.get(evidence.artifact_path, "")
        short = f"`{digest[:12]}`" if digest else "-"
        controls = ", ".join(evidence.control_refs)
        lines.append(
            f"| {evidence.id} | {evidence.title} | {evidence.type.value} | {controls} | "
            f"{evidence.collected_on.isoformat()} | {evidence.valid_until.isoformat()} | {short} |"
        )
    lines.append("")
    return "\n".join(lines)


def seed(settings: Settings | None = None, clock: Clock | None = None) -> SeedResult:
    """Generate all evidence artifacts, the manifest, the metrics snapshot and the index."""
    settings = settings or get_settings()
    clock = clock or default_clock()
    today = clock.today()

    repo = IcepRepository.load(settings)
    errors = repo.integrity_errors()
    if errors:
        joined = "\n  - ".join(f"{e.category}: {e.message}" for e in errors)
        raise SeedError(f"register has {len(errors)} integrity error(s):\n  - {joined}")

    samples_dir = settings.data_dir / "samples"
    root = settings.evidence_dir.parent  # artifact_path values are relative to the repo root
    artifacts: dict[str, str] = {}
    collector_runs = 0

    for evidence in sorted(repo.evidence, key=lambda e: e.id):
        content = _artifact_content(evidence, samples_dir, today)
        if evidence.source.startswith("collector:"):
            collector_runs += 1
        out_path = root / evidence.artifact_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        artifacts[evidence.artifact_path] = sha256_text(content)

    settings.evidence_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "tool": "icep",
        "version": __version__,
        "generated_at": clock.now().isoformat(),
        "artifact_count": len(artifacts),
        "artifacts": dict(sorted(artifacts.items())),
    }
    manifest_path = settings.evidence_dir / "manifest.json"
    write_json(manifest_path, manifest)

    metrics = compute_metrics(repo, today, settings.warn_days)
    metrics_path = settings.evidence_dir / "metrics.json"
    write_json(metrics_path, _metrics_summary(metrics))

    index_path = settings.evidence_dir / "index.md"
    index_path.write_text(_render_index(repo, artifacts, today), encoding="utf-8")

    return SeedResult(
        artifacts=artifacts,
        collector_runs=collector_runs,
        manifest_path=manifest_path,
        metrics_path=metrics_path,
        index_path=index_path,
    )


def read_manifest(settings: Settings | None = None) -> dict[str, str]:
    """Return the ``artifact_path -> sha256`` map from ``evidence/manifest.json`` (empty if absent)."""
    settings = settings or get_settings()
    path = settings.evidence_dir / "manifest.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    artifacts = data.get("artifacts", {})
    return {str(k): str(v) for k, v in artifacts.items()}
