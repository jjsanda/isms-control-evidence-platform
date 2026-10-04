"""auditd coverage collector: check an ``auditd.rules`` file against a required rule baseline.

Evidence for A.8.15 (logging) and A.8.16 (monitoring), and the acceptance criteria of the
"centralised Linux audit logging" initiative: does the edge/backend audit ruleset cover the events
an investigator needs (identity changes, logins, privileged commands, kernel-module loads, an
immutable config)? The sample is missing a couple on purpose, so coverage lands below 100%.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from icep.collectors.base import CheckStatus, CollectorResult, Finding

__all__ = ["NAME", "SAMPLE", "run"]

NAME = "auditd_coverage"
SAMPLE = "auditd.rules"


@dataclass(frozen=True)
class _Requirement:
    id: str
    description: str
    needles: tuple[str, ...]
    severity: str
    recommendation: str


# Each requirement is present if ANY of its needles appears in the ruleset (case-insensitive).
_REQUIREMENTS: tuple[_Requirement, ...] = (
    _Requirement(
        "time_change",
        "Time-change events audited",
        ("-k time-change", "/etc/localtime", "adjtimex"),
        "medium",
        "Add the CIS 'time-change' rules (adjtimex/settimeofday/clock_settime).",
    ),
    _Requirement(
        "identity",
        "Identity file changes audited",
        ("-k identity", "/etc/passwd", "/etc/shadow", "/etc/group"),
        "high",
        "Watch /etc/passwd, /etc/shadow, /etc/group with key 'identity'.",
    ),
    _Requirement(
        "logins",
        "Login/logout events audited",
        ("-k logins", "/var/log/faillog", "/var/log/lastlog", "/var/run/faillock"),
        "medium",
        "Watch faillog/lastlog with key 'logins'.",
    ),
    _Requirement(
        "privileged",
        "Privileged command use audited",
        ("-k privileged", "-k actions", "/usr/bin/sudo", "execve"),
        "high",
        "Audit sudo/execve of privileged binaries with key 'privileged'.",
    ),
    _Requirement(
        "mac_policy",
        "MAC policy changes audited",
        ("-k MAC-policy", "/etc/selinux", "/etc/apparmor"),
        "medium",
        "Watch /etc/selinux or /etc/apparmor with key 'MAC-policy'.",
    ),
    _Requirement(
        "modules",
        "Kernel module loading audited",
        ("-k modules", "init_module", "delete_module", "finit_module"),
        "high",
        "Audit init_module/delete_module with key 'modules'.",
    ),
    _Requirement(
        "scope",
        "Sudoers changes audited",
        ("-k scope", "/etc/sudoers"),
        "medium",
        "Watch /etc/sudoers and /etc/sudoers.d with key 'scope'.",
    ),
    _Requirement(
        "immutable",
        "Audit configuration made immutable",
        ("-e 2",),
        "medium",
        "End the ruleset with '-e 2' so rules cannot be changed without a reboot.",
    ),
)


def run(samples_dir: Path, today: date) -> CollectorResult:
    """Evaluate ``samples_dir/auditd.rules`` for required audit coverage."""
    text = (Path(samples_dir) / SAMPLE).read_text(encoding="utf-8").lower()

    findings: list[Finding] = []
    for req in _REQUIREMENTS:
        present = any(needle.lower() in text for needle in req.needles)
        findings.append(
            Finding(
                id=req.id,
                description=req.description,
                status=CheckStatus.PASS if present else CheckStatus.FAIL,
                severity=req.severity,
                observed="rule present" if present else "no matching rule",
                recommendation="" if present else req.recommendation,
            )
        )

    covered = sum(1 for f in findings if f.status is CheckStatus.PASS)
    summary = (
        f"Audit rule coverage is {covered}/{len(findings)} required categories; "
        "gaps feed the centralised-logging initiative (INIT-001)."
    )
    return CollectorResult(
        collector=NAME,
        title="auditd rule coverage (edge + backend)",
        target="auditd.rules baseline across locker edge devices and backend hosts",
        report_date=today,
        summary=summary,
        control_refs=["A.8.15", "A.8.16"],
        nis2_areas=["incident_handling"],
        findings=findings,
    )
