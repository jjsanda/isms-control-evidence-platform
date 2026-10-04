"""SSH hardening collector: evaluate an ``sshd_config`` against a CIS-style baseline.

Evidence for A.8.9 (configuration management) on the Linux locker fleet: the collector parses the
committed ``sshd_config`` sample (first-value-wins, matching sshd semantics) and checks the
directives that most often let an attacker in -- root login, password auth, forwarding, auth
throttling. The sample carries a few intentional weaknesses so the report shows real findings.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from icep.collectors.base import CheckStatus, CollectorResult, Finding

__all__ = ["NAME", "SAMPLE", "run"]

NAME = "ssh_hardening"
SAMPLE = "sshd_config"


def _parse_sshd(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        key, value = parts[0].lower(), parts[1].strip()
        values.setdefault(key, value)  # sshd uses the first obtained value
    return values


def _seconds(value: str) -> int | None:
    text = value.strip().lower()
    try:
        if text.endswith("m"):
            return int(text[:-1]) * 60
        if text.endswith("s"):
            return int(text[:-1])
        return int(text)
    except ValueError:
        return None


def _expect(
    cfg: dict[str, str],
    key: str,
    description: str,
    expected: set[str],
    severity: str,
    recommendation: str,
) -> Finding:
    value = cfg.get(key)
    if value is None:
        return Finding(
            id=key,
            description=description,
            status=CheckStatus.WARN,
            severity=severity,
            observed="not set (relies on the compiled-in default)",
            recommendation=recommendation,
        )
    ok = value.lower() in expected
    return Finding(
        id=key,
        description=description,
        status=CheckStatus.PASS if ok else CheckStatus.FAIL,
        severity=severity,
        observed=f"{key} {value}",
        recommendation="" if ok else recommendation,
    )


def _threshold(
    cfg: dict[str, str],
    key: str,
    description: str,
    limit: int,
    severity: str,
    recommendation: str,
) -> Finding:
    value = cfg.get(key)
    seconds = _seconds(value) if value is not None else None
    if seconds is None:
        return Finding(
            id=key,
            description=description,
            status=CheckStatus.WARN,
            severity=severity,
            observed="not set" if value is None else f"{key} {value}",
            recommendation=recommendation,
        )
    ok = 0 < seconds <= limit
    return Finding(
        id=key,
        description=description,
        status=CheckStatus.PASS if ok else CheckStatus.FAIL,
        severity=severity,
        observed=f"{key} {value}",
        recommendation="" if ok else recommendation,
    )


def run(samples_dir: Path, today: date) -> CollectorResult:
    """Evaluate ``samples_dir/sshd_config`` and return the hardening result."""
    cfg = _parse_sshd((Path(samples_dir) / SAMPLE).read_text(encoding="utf-8"))

    findings = [
        _expect(
            cfg,
            "permitrootlogin",
            "Root login disabled",
            {"no", "prohibit-password"},
            "high",
            "Set 'PermitRootLogin no' and administer via named accounts + sudo.",
        ),
        _expect(
            cfg,
            "passwordauthentication",
            "Password authentication disabled",
            {"no"},
            "high",
            "Set 'PasswordAuthentication no' and use SSH keys / certificates.",
        ),
        _expect(
            cfg,
            "permitemptypasswords",
            "Empty passwords rejected",
            {"no"},
            "high",
            "Set 'PermitEmptyPasswords no'.",
        ),
        _expect(
            cfg,
            "x11forwarding",
            "X11 forwarding disabled",
            {"no"},
            "medium",
            "Set 'X11Forwarding no' on headless locker hosts.",
        ),
        _expect(
            cfg,
            "hostbasedauthentication",
            "Host-based authentication disabled",
            {"no"},
            "medium",
            "Set 'HostbasedAuthentication no'.",
        ),
        _expect(
            cfg, "ignorerhosts", "Legacy .rhosts ignored", {"yes"}, "low", "Set 'IgnoreRhosts yes'."
        ),
        _threshold(
            cfg,
            "maxauthtries",
            "Auth attempts throttled (<= 4)",
            4,
            "medium",
            "Set 'MaxAuthTries 4' to slow brute-force attempts.",
        ),
        _threshold(
            cfg,
            "logingracetime",
            "Login grace time short (<= 60s)",
            60,
            "low",
            "Set 'LoginGraceTime 60'.",
        ),
        _threshold(
            cfg,
            "clientaliveinterval",
            "Idle sessions expire (<= 300s)",
            300,
            "low",
            "Set 'ClientAliveInterval 300' and 'ClientAliveCountMax 1'.",
        ),
    ]

    failed = sum(1 for f in findings if f.status is CheckStatus.FAIL)
    summary = (
        f"{failed} of {len(findings)} SSH hardening checks failed against the locker-fleet baseline; "
        "failures are tracked as improvement actions."
    )
    return CollectorResult(
        collector=NAME,
        title="SSH hardening check (locker fleet)",
        target="sshd_config baseline for internet-facing locker edge devices",
        report_date=today,
        summary=summary,
        control_refs=["A.8.9"],
        nis2_areas=["acq_dev_maintenance"],
        findings=findings,
    )
