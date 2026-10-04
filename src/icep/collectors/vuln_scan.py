"""Vulnerability-scan collector: summarise a Trivy JSON report into an evidence artifact.

Evidence for A.8.8 (management of technical vulnerabilities): the collector reads a committed Trivy
report of the backend container images, counts findings by severity, and raises a FAIL per fixable
CRITICAL and a WARN per fixable HIGH -- the ones with a remediation SLA. Sorted deterministically so
the artifact is byte-stable.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from icep.collectors.base import CheckStatus, CollectorResult, Finding

__all__ = ["NAME", "SAMPLE", "run"]

NAME = "vuln_scan"
SAMPLE = "trivy-report.json"

_SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}


def _iter_vulns(report: dict[str, Any]) -> list[dict[str, Any]]:
    vulns: list[dict[str, Any]] = []
    for result in report.get("Results", []) or []:
        target = result.get("Target", "image")
        for vuln in result.get("Vulnerabilities", []) or []:
            vuln = dict(vuln)
            vuln["_target"] = target
            vulns.append(vuln)
    return vulns


def run(samples_dir: Path, today: date) -> CollectorResult:
    """Summarise ``samples_dir/trivy-report.json`` by severity and SLA."""
    report = json.loads((Path(samples_dir) / SAMPLE).read_text(encoding="utf-8"))
    vulns = _iter_vulns(report)

    counts = dict.fromkeys(_SEVERITY_RANK, 0)
    for vuln in vulns:
        severity = str(vuln.get("Severity", "UNKNOWN")).upper()
        counts[severity] = counts.get(severity, 0) + 1

    # Deterministic order: by severity rank, then CVE id.
    ordered = sorted(
        vulns,
        key=lambda v: (
            _SEVERITY_RANK.get(str(v.get("Severity", "UNKNOWN")).upper(), 9),
            str(v.get("VulnerabilityID", "")),
        ),
    )

    findings: list[Finding] = []
    for vuln in ordered:
        severity = str(vuln.get("Severity", "UNKNOWN")).upper()
        if severity not in {"CRITICAL", "HIGH"}:
            continue
        fixed = vuln.get("FixedVersion")
        pkg = vuln.get("PkgName", "?")
        installed = vuln.get("InstalledVersion", "?")
        cve = str(vuln.get("VulnerabilityID", "?"))
        findings.append(
            Finding(
                id=cve,
                description=f"{pkg} {installed} ({vuln.get('_target', 'image')}): {cve}",
                status=CheckStatus.FAIL if severity == "CRITICAL" else CheckStatus.WARN,
                severity=severity.lower(),
                observed=f"fixed in {fixed}" if fixed else "no fix available yet",
                recommendation=(
                    f"Patch to {fixed} within SLA (critical: 7 days, high: 30 days)."
                    if fixed
                    else "Track upstream; apply mitigations until a fix ships."
                ),
            )
        )

    summary = (
        f"{counts.get('CRITICAL', 0)} critical, {counts.get('HIGH', 0)} high, "
        f"{counts.get('MEDIUM', 0)} medium, {counts.get('LOW', 0)} low across "
        f"{len(report.get('Results', []) or [])} scanned image(s)."
    )
    return CollectorResult(
        collector=NAME,
        title="Vulnerability scan summary (container images)",
        target="Trivy scan of PaketPort backend container images",
        report_date=today,
        summary=summary,
        control_refs=["A.8.8"],
        nis2_areas=["acq_dev_maintenance"],
        findings=findings,
    )
