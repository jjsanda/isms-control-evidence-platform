"""Access-review collector: reconcile an access export against HR joiner/leaver data.

Evidence for A.5.15 (access control), A.8.2 (privileged access rights) and A.8.5 (secure
authentication): the collector cross-checks a committed access export against the HR
joiner/mover/leaver list and flags the classics -- accounts still active for terminated staff,
dormant accounts, and privileged accounts without MFA.
"""

from __future__ import annotations

import csv
from datetime import date, timedelta
from io import StringIO
from pathlib import Path

from icep.collectors.base import CheckStatus, CollectorResult, Finding

__all__ = ["NAME", "SAMPLE", "HR_SAMPLE", "run"]

NAME = "access_review"
SAMPLE = "access-export.csv"
HR_SAMPLE = "hr-joiners-leavers.csv"
_DORMANT_DAYS = 90


def _rows(path: Path) -> list[dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    return [
        {k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(StringIO(text))
    ]


def _is_true(value: str) -> bool:
    return value.strip().lower() in {"true", "yes", "1", "y"}


def run(samples_dir: Path, today: date) -> CollectorResult:
    """Reconcile ``access-export.csv`` against ``hr-joiners-leavers.csv``."""
    base = Path(samples_dir)
    accounts = _rows(base / SAMPLE)
    hr_rows = _rows(base / HR_SAMPLE)
    hr_status = {row["full_name"]: row.get("employee_status", "").lower() for row in hr_rows}

    dormant_cutoff = today - timedelta(days=_DORMANT_DAYS)
    findings: list[Finding] = []
    for account in sorted(accounts, key=lambda a: a.get("username", "")):
        username = account.get("username", "?")
        full_name = account.get("full_name", "")
        active = account.get("status", "").lower() == "active"
        privileged = _is_true(account.get("privileged", ""))
        mfa = _is_true(account.get("mfa_enabled", ""))
        employee = hr_status.get(full_name)

        # 1. Leaver whose account is still active.
        if active and employee == "terminated":
            findings.append(
                Finding(
                    id=f"{username}:leaver",
                    description=f"{username}: account disabled for terminated staff",
                    status=CheckStatus.FAIL,
                    severity="high",
                    observed=f"{full_name} is terminated in HR but the account is active",
                    recommendation="Disable the account immediately and review its recent activity.",
                )
            )
        # 2. Active account with no HR record (orphan).
        if active and employee is None:
            findings.append(
                Finding(
                    id=f"{username}:orphan",
                    description=f"{username}: account maps to a current employee",
                    status=CheckStatus.WARN,
                    severity="medium",
                    observed=f"no HR record for '{full_name}'",
                    recommendation="Confirm ownership or disable the orphaned account.",
                )
            )
        # 3. Dormant active account.
        last_login = account.get("last_login", "")
        try:
            login_date = date.fromisoformat(last_login) if last_login else None
        except ValueError:
            login_date = None
        if active and login_date is not None and login_date < dormant_cutoff:
            findings.append(
                Finding(
                    id=f"{username}:dormant",
                    description=f"{username}: no dormant active account (> {_DORMANT_DAYS}d)",
                    status=CheckStatus.WARN,
                    severity="low",
                    observed=f"last login {last_login}",
                    recommendation="Review and disable if no longer required.",
                )
            )
        # 4. Privileged account without MFA.
        if active and privileged and not mfa:
            findings.append(
                Finding(
                    id=f"{username}:mfa",
                    description=f"{username}: privileged account has MFA",
                    status=CheckStatus.FAIL,
                    severity="high",
                    observed="privileged account without MFA",
                    recommendation="Enforce MFA on all privileged access (control A.8.5).",
                )
            )

    # Add a PASS baseline so a clean review still produces positive evidence.
    if not any(f.status is CheckStatus.FAIL for f in findings):
        findings.insert(
            0,
            Finding(
                id="baseline",
                description="No terminated-staff or privileged-MFA violations",
                status=CheckStatus.PASS,
                severity="low",
            ),
        )

    reviewed = len(accounts)
    failed = sum(1 for f in findings if f.status is CheckStatus.FAIL)
    summary = (
        f"{reviewed} account(s) reviewed against HR records; {failed} high-severity issue(s) found. "
        "Joiner/mover/leaver hygiene is the backbone of access control."
    )
    return CollectorResult(
        collector=NAME,
        title="Quarterly access review (joiner/mover/leaver)",
        target="Backend and admin account export vs HR records",
        report_date=today,
        summary=summary,
        control_refs=["A.5.15", "A.8.2", "A.8.5"],
        nis2_areas=["hr_access_asset", "mfa_comms"],
        findings=findings,
    )
