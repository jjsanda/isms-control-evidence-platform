from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from icep.collectors import (
    access_review,
    auditd_coverage,
    backup_restore,
    ssh_hardening,
    vuln_scan,
)
from icep.collectors.base import CheckStatus, CollectorResult, render_markdown
from icep.config import get_settings

pytestmark = pytest.mark.collectors

TODAY = date(2026, 7, 7)


@pytest.fixture
def samples_dir() -> Path:
    return get_settings().data_dir / "samples"


def _fail_ids(result: CollectorResult) -> set[str]:
    return {f.id for f in result.findings if f.status is CheckStatus.FAIL}


def test_ssh_hardening_flags_the_three_weak_settings(samples_dir: Path) -> None:
    result = ssh_hardening.run(samples_dir, TODAY)
    assert result.failed == 3
    assert _fail_ids(result) == {"permitrootlogin", "passwordauthentication", "x11forwarding"}
    assert result.control_refs == ["A.8.9"]


def test_auditd_coverage_reports_the_two_gaps(samples_dir: Path) -> None:
    result = auditd_coverage.run(samples_dir, TODAY)
    assert _fail_ids(result) == {"modules", "immutable"}
    assert result.passed == 6
    assert result.coverage_pct == 75.0


def test_vuln_scan_counts_by_severity(samples_dir: Path) -> None:
    result = vuln_scan.run(samples_dir, TODAY)
    assert result.failed == 2  # two CRITICAL
    assert result.warned == 2  # two HIGH
    assert "2 critical" in result.summary
    assert result.control_refs == ["A.8.8"]


def test_backup_restore_flags_overdue_and_unencrypted(samples_dir: Path) -> None:
    result = backup_restore.run(samples_dir, TODAY)
    assert _fail_ids(result) == {"locker-config:restore-test", "object-store:encryption"}
    assert result.warned == 1  # locker-config integrity not verified


def test_access_review_flags_leaver_and_missing_mfa(samples_dir: Path) -> None:
    result = access_review.run(samples_dir, TODAY)
    assert _fail_ids(result) == {"jbauer:leaver", "sberger:mfa"}
    assert any(f.id == "ehuber:dormant" for f in result.findings)


@pytest.mark.parametrize(
    "collector",
    [ssh_hardening, auditd_coverage, vuln_scan, backup_restore, access_review],
    ids=lambda m: m.NAME,
)
def test_collectors_are_deterministic(collector: object, samples_dir: Path) -> None:
    first = collector.run(samples_dir, TODAY)  # type: ignore[attr-defined]
    second = collector.run(samples_dir, TODAY)  # type: ignore[attr-defined]
    assert first.model_dump() == second.model_dump()
    assert render_markdown(first) == render_markdown(second)


def test_render_markdown_has_report_shape(samples_dir: Path) -> None:
    md = render_markdown(ssh_hardening.run(samples_dir, TODAY))
    assert md.startswith("# SSH hardening check")
    assert "| Check | Result | Severity | Observed | Recommendation |" in md
    assert "2026-07-07" in md
