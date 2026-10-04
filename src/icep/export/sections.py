"""Build the individual Markdown sections of the audit pack.

Each function turns the repository + metrics into one auditor-facing document. Everything is sorted
and derives dates from the injected ``today``, so the pack is byte-reproducible. The section set is
deliberately the same order an ISO 27001 auditor works through: scope, Statement of Applicability,
control register, risks, evidence, NIS2, improvement actions, and review/expiry status.
"""

from __future__ import annotations

from datetime import date

from icep.domain import AuditStatus, Nis2Area, ReviewState
from icep.domain.common import control_sort_key
from icep.domain.nis2 import NIS2_ARTICLE, NIS2_TITLE
from icep.metrics import Metrics
from icep.repository import IcepRepository
from icep.workflow import classify, effective_status

__all__ = [
    "SECTION_ORDER",
    "executive_summary",
    "statement_of_applicability",
    "control_register",
    "risk_register",
    "evidence_index",
    "nis2_readiness",
    "improvement_actions",
    "audit_status_and_expiry",
    "pack_readme",
    "build_sections",
]

SECTION_ORDER = [
    ("00-executive-summary", "Executive summary"),
    ("01-statement-of-applicability", "Statement of Applicability"),
    ("02-control-register", "Control register"),
    ("03-risk-register", "Risk register"),
    ("04-evidence-index", "Evidence index"),
    ("05-nis2-readiness", "NIS2 readiness"),
    ("06-improvement-actions", "Improvement actions"),
    ("07-audit-status-and-expiry", "Audit status & expiry"),
]


def _bullets(pairs: list[tuple[str, object]]) -> list[str]:
    return [f"- **{label}:** {value}" for label, value in pairs]


def executive_summary(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    org = repo.organization
    overdue = metrics.review_counts.get(ReviewState.OVERDUE, 0)
    expired = metrics.evidence_expired
    lines = [
        "# Executive summary",
        "",
        f"**{org.name}** — Information Security Management System audit pack, generated "
        f"{today.isoformat()}.",
        "",
        "## Scope",
        "",
        org.isms_scope,
        "",
        f"*Boundary:* {org.scope_boundary}",
        "",
        "## Posture at a glance",
        "",
        *_bullets(
            [
                ("Certification target", org.certification_target),
                (
                    "Annex A controls",
                    f"{metrics.documented_total} fully documented of {metrics.catalog_total} "
                    f"({metrics.soa_applicable} applicable in the SoA)",
                ),
                (
                    "Implementation",
                    f"{metrics.implemented_controls}/{metrics.documented_total} documented controls "
                    f"implemented or operating ({metrics.implementation_pct}%)",
                ),
                (
                    "NIS2 readiness",
                    f"{metrics.nis2_overall_pct}% across the Art. 21(2) measures and the Art. 20 duty",
                ),
                (
                    "Risks",
                    f"{metrics.risk_total} tracked, {metrics.risks_high_or_critical_open} high/critical "
                    f"unaccepted, {metrics.risks_accepted} formally accepted",
                ),
                (
                    "Improvement actions",
                    f"{metrics.action_open} open ({metrics.action_overdue} overdue)",
                ),
                (
                    "Reviews",
                    f"{overdue} control{'' if overdue == 1 else 's'} overdue for review, "
                    f"{expired} evidence artifact{'' if expired == 1 else 's'} expired",
                ),
            ]
        ),
        "",
        "## Management commitment",
        "",
        org.policy_statement,
        "",
        f"*ISMS owner:* {org.isms_owner.name} ({org.isms_owner.role}). "
        f"*Management representative:* {org.management_representative.name} "
        f"({org.management_representative.role}).",
        "",
    ]
    return "\n".join(lines)


def statement_of_applicability(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    documented = repo.documented_control_ids
    lines = [
        "# Statement of Applicability (ISO/IEC 27001:2022 Annex A)",
        "",
        f"All {metrics.catalog_total} Annex A controls, with the applicability decision and its "
        "justification. 'Documented' marks controls with a full control record in this register.",
        "",
        "| Control | Title | Applicable | Reason | Documented | Justification |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    catalog = {c.id: c for c in repo.catalog}
    for entry in sorted(repo.soa, key=lambda e: control_sort_key(e.control_id)):
        title = catalog[entry.control_id].title if entry.control_id in catalog else ""
        applicable = "Yes" if entry.applicable else "No"
        documented_mark = "Yes" if entry.control_id in documented else "—"
        lines.append(
            f"| {entry.control_id} | {title} | {applicable} | {entry.inclusion_reason.value} | "
            f"{documented_mark} | {entry.justification} |"
        )
    lines.append("")
    return "\n".join(lines)


def control_register(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    lines = [
        "# Control register (documented controls)",
        "",
        f"{len(repo.controls)} controls with owners, implementation status, evidence and review "
        "dates. 'Audit status' is the effective status as of the report date (accepted controls "
        "whose review date has passed read as expired).",
        "",
        "| Control | Title | Theme | Owner | Status | Maturity | Audit | Next review | Evidence | Risks |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for control in sorted(repo.controls, key=lambda c: control_sort_key(c.id)):
        effective = effective_status(control.audit_status, control.next_review, today)
        review_state = classify(control.next_review, today, metrics.warn_days)
        marker = "" if review_state is ReviewState.CURRENT else f" ({review_state.value})"
        lines.append(
            f"| {control.id} | {control.title} | {control.theme.value} | {control.owner.name} | "
            f"{control.status.value} | {control.maturity}/5 | {effective.value} | "
            f"{control.next_review.isoformat()}{marker} | {len(control.evidence_refs)} | "
            f"{len(control.risk_refs)} |"
        )
    lines.append("")
    return "\n".join(lines)


def risk_register(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    lines = [
        "# Risk register",
        "",
        f"{len(repo.risks)} risks with inherent and residual assessments on a 5x5 likelihood x "
        "impact scale (Low <=4, Medium 5-9, High 10-14, Critical >=15).",
        "",
        "| Risk | Title | Owner | Inherent | Treatment | Residual | Acceptance | Target |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for risk in sorted(repo.risks, key=lambda r: r.id):
        inherent = f"{risk.inherent_band.value} ({risk.inherent_score})"
        residual = f"{risk.residual_band.value} ({risk.residual_score})"
        acceptance = risk.acceptance.value
        if risk.accepted_by is not None:
            acceptance += f" by {risk.accepted_by.name}"
        lines.append(
            f"| {risk.id} | {risk.title} | {risk.owner.name} | {inherent} | "
            f"{risk.treatment.value} | {residual} | {acceptance} | {risk.target_date.isoformat()} |"
        )
    lines.append("")
    return "\n".join(lines)


def evidence_index(repo: IcepRepository, hashes: dict[str, str], today: date) -> str:
    lines = [
        "# Evidence index",
        "",
        f"{len(repo.evidence)} evidence artifacts. Each SHA-256 anchors the artifact to the audit "
        "manifest so tampering is detectable.",
        "",
        "| Evidence | Title | Type | Controls | Collected by | Valid until | Status | SHA-256 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for evidence in sorted(repo.evidence, key=lambda e: e.id):
        digest = hashes.get(evidence.artifact_path, "")
        short = digest[:12] if digest else "—"
        status = "expired" if evidence.is_expired(today) else "valid"
        lines.append(
            f"| {evidence.id} | {evidence.title} | {evidence.type.value} | "
            f"{', '.join(evidence.control_refs)} | {evidence.collected_by.name} | "
            f"{evidence.valid_until.isoformat()} | {status} | `{short}` |"
        )
    lines.append("")
    return "\n".join(lines)


def nis2_readiness(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    lines = [
        "# NIS2 readiness",
        "",
        "Mapping of NIS2 Directive (EU) 2022/2555 Art. 21(2) risk-management measures to the Annex A "
        f"controls that implement them. Overall readiness: **{metrics.nis2_overall_pct}%**.",
        "",
        "| Article | Measure | Controls | Readiness |",
        "| --- | --- | --- | --- |",
    ]
    for area in Nis2Area:
        measure = repo.nis2_by_area.get(area)
        if measure is None:
            continue
        readiness = metrics.nis2_area_readiness.get(area, 0.0)
        lines.append(
            f"| {NIS2_ARTICLE[area]} | {NIS2_TITLE[area]} | {', '.join(measure.control_refs)} | "
            f"{readiness}% |"
        )
    lines.extend(
        [
            "",
            "## Incident reporting (Art. 23)",
            "",
            "| Phase | Deadline | Trigger / content |",
            "| --- | --- | --- |",
        ]
    )
    for report in repo.nis2_reporting:
        lines.append(f"| {report.phase.value} | {report.deadline_label} | {report.content} |")
    lines.append("")
    return "\n".join(lines)


def improvement_actions(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    lines = [
        "# Improvement actions (CAPA)",
        "",
        f"{metrics.action_total} actions, {metrics.action_open} open ({metrics.action_overdue} "
        "overdue). These are the continual-improvement backlog of the ISMS.",
        "",
        "| Action | Title | Source | Owner | Status | Due | Overdue |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for action in sorted(repo.actions, key=lambda a: a.id):
        overdue = "yes" if action.is_overdue(today) else "—"
        lines.append(
            f"| {action.id} | {action.title} | {action.source.value} | {action.owner.name} | "
            f"{action.status.value} | {action.due_date.isoformat()} | {overdue} |"
        )
    lines.append("")
    return "\n".join(lines)


def audit_status_and_expiry(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    lines = [
        "# Audit status & expiry",
        "",
        "Effective audit status of documented controls and evidence validity as of "
        f"{today.isoformat()}.",
        "",
        "## Control audit status",
        "",
        "| Status | Count |",
        "| --- | --- |",
    ]
    for status in AuditStatus:
        lines.append(f"| {status.value} | {metrics.audit_counts.get(status, 0)} |")

    lines.extend(["", "## Controls overdue for review", ""])
    if metrics.overdue_controls:
        lines.append("| Control | Title | Owner | Next review |")
        lines.append("| --- | --- | --- | --- |")
        for control in metrics.overdue_controls:
            lines.append(
                f"| {control.id} | {control.title} | {control.owner.name} | "
                f"{control.next_review.isoformat()} |"
            )
    else:
        lines.append("_None._")

    lines.extend(["", "## Expired or expiring evidence", ""])
    expired = [e for e in repo.evidence if e.is_expired(today)]
    expiring = [
        e
        for e in repo.evidence
        if not e.is_expired(today)
        and classify(e.valid_until, today, metrics.warn_days) is ReviewState.DUE_SOON
    ]
    if expired or expiring:
        lines.append("| Evidence | Title | Valid until | State |")
        lines.append("| --- | --- | --- | --- |")
        for evidence in sorted(expired, key=lambda e: e.id):
            lines.append(
                f"| {evidence.id} | {evidence.title} | {evidence.valid_until.isoformat()} | expired |"
            )
        for evidence in sorted(expiring, key=lambda e: e.id):
            lines.append(
                f"| {evidence.id} | {evidence.title} | {evidence.valid_until.isoformat()} | expiring |"
            )
    else:
        lines.append("_All evidence is current._")
    lines.append("")
    return "\n".join(lines)


def pack_readme(repo: IcepRepository, metrics: Metrics, today: date) -> str:
    lines = [
        f"# Audit pack — {repo.organization.name}",
        "",
        f"Generated {today.isoformat()} by `icep`. This bundle is a point-in-time snapshot of the "
        "ISMS suitable for an ISO/IEC 27001:2022 certification review.",
        "",
        "## Contents",
        "",
    ]
    for slug, title in SECTION_ORDER:
        lines.append(f"- [{title}](./{slug}.md)")
    lines.extend(
        [
            "",
            "Integrity of every included file and evidence artifact is recorded in "
            "`../manifest.json` (SHA-256).",
            "",
        ]
    )
    return "\n".join(lines)


def build_sections(
    repo: IcepRepository, metrics: Metrics, hashes: dict[str, str], today: date
) -> dict[str, str]:
    """Return ``{slug: markdown}`` for every audit-pack section plus the pack README."""
    return {
        "00-executive-summary": executive_summary(repo, metrics, today),
        "01-statement-of-applicability": statement_of_applicability(repo, metrics, today),
        "02-control-register": control_register(repo, metrics, today),
        "03-risk-register": risk_register(repo, metrics, today),
        "04-evidence-index": evidence_index(repo, hashes, today),
        "05-nis2-readiness": nis2_readiness(repo, metrics, today),
        "06-improvement-actions": improvement_actions(repo, metrics, today),
        "07-audit-status-and-expiry": audit_status_and_expiry(repo, metrics, today),
        "README": pack_readme(repo, metrics, today),
    }
