"""Backup restore-test collector: verify backup jobs are tested, encrypted and current.

Evidence for A.8.13 (information backup) and A.5.30 (ICT readiness for business continuity): a
backup you have never restored is a hope, not a control. The collector reads a committed
``backup-jobs.yaml`` and, per job, checks that a restore test happened within 90 days, that backups
are encrypted, and that integrity was verified.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml

from icep.collectors.base import CheckStatus, CollectorResult, Finding

__all__ = ["NAME", "SAMPLE", "run"]

NAME = "backup_restore"
SAMPLE = "backup-jobs.yaml"
_RESTORE_TEST_MAX_AGE_DAYS = 90


def _as_date(value: Any) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def run(samples_dir: Path, today: date) -> CollectorResult:
    """Evaluate the backup jobs described in ``samples_dir/backup-jobs.yaml``."""
    raw = yaml.safe_load((Path(samples_dir) / SAMPLE).read_text(encoding="utf-8")) or {}
    jobs: list[dict[str, Any]] = list(raw.get("jobs", []))

    findings: list[Finding] = []
    cutoff = today - timedelta(days=_RESTORE_TEST_MAX_AGE_DAYS)
    for job in jobs:
        name = str(job.get("name", "job"))
        last_test = _as_date(job.get("last_restore_test"))
        tested_recently = last_test is not None and last_test >= cutoff
        findings.append(
            Finding(
                id=f"{name}:restore-test",
                description=f"{name}: restore test within {_RESTORE_TEST_MAX_AGE_DAYS} days",
                status=CheckStatus.PASS if tested_recently else CheckStatus.FAIL,
                severity="high",
                observed=f"last restore test: {last_test.isoformat() if last_test else 'never'}",
                recommendation=(
                    "" if tested_recently else "Run and document a restore test this quarter."
                ),
            )
        )
        encrypted = bool(job.get("encrypted", False))
        findings.append(
            Finding(
                id=f"{name}:encryption",
                description=f"{name}: backups encrypted at rest",
                status=CheckStatus.PASS if encrypted else CheckStatus.FAIL,
                severity="high",
                observed="encrypted" if encrypted else "not encrypted",
                recommendation="" if encrypted else "Enable encryption for this backup target.",
            )
        )
        integrity = bool(job.get("integrity_verified", False))
        findings.append(
            Finding(
                id=f"{name}:integrity",
                description=f"{name}: integrity checksums verified",
                status=CheckStatus.PASS if integrity else CheckStatus.WARN,
                severity="medium",
                observed="verified" if integrity else "not verified",
                recommendation="" if integrity else "Verify checksums after each backup run.",
            )
        )

    failed = sum(1 for f in findings if f.status is CheckStatus.FAIL)
    summary = (
        f"{len(jobs)} backup job(s) reviewed; {failed} check(s) failed. "
        "A restore test that is overdue or an unencrypted target is a business-continuity gap."
    )
    return CollectorResult(
        collector=NAME,
        title="Backup restore-test record",
        target="Backend and configuration backup jobs",
        report_date=today,
        summary=summary,
        control_refs=["A.8.13", "A.5.30"],
        nis2_areas=["business_continuity"],
        findings=findings,
    )
