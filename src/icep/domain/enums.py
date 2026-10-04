"""Controlled vocabularies for the ISMS register.

Every categorical field in the domain draws from one of these ``StrEnum``s, so the register is
consistent, the schema rejects typos, and the dashboard/audit-pack can rely on a fixed set of
values. Values are lower_snake_case; ``StrEnum`` means they serialise to plain strings in YAML.
"""

from __future__ import annotations

from enum import StrEnum

__all__ = [
    "Theme",
    "ControlStatus",
    "AuditStatus",
    "InclusionReason",
    "TreatmentOption",
    "AcceptanceDecision",
    "RiskBand",
    "ReviewState",
    "EvidenceType",
    "Nis2Area",
    "ReportingPhase",
    "ActionSource",
    "ActionStatus",
    "TaskStatus",
    "InitiativeStatus",
]


class Theme(StrEnum):
    """The four ISO/IEC 27001:2022 Annex A themes (clauses A.5-A.8)."""

    ORGANIZATIONAL = "organizational"  # A.5
    PEOPLE = "people"  # A.6
    PHYSICAL = "physical"  # A.7
    TECHNOLOGICAL = "technological"  # A.8


class ControlStatus(StrEnum):
    """Implementation state of a control.

    ``OPERATING`` = implemented *and* backed by current (non-expired) evidence; it is the state an
    auditor wants to see. ``NOT_APPLICABLE`` is reserved for controls excluded in the SoA.
    """

    NOT_APPLICABLE = "not_applicable"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    IMPLEMENTED = "implemented"
    OPERATING = "operating"


class AuditStatus(StrEnum):
    """The review lifecycle of a control or evidence record: ``draft -> reviewed -> accepted``,
    lapsing to ``expired`` when its next-review date passes."""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    ACCEPTED = "accepted"
    EXPIRED = "expired"


class InclusionReason(StrEnum):
    """Why a control is included (or excluded) in the Statement of Applicability."""

    RISK = "risk"
    LEGAL = "legal"
    CONTRACTUAL = "contractual"
    BEST_PRACTICE = "best_practice"
    BUSINESS = "business"


class TreatmentOption(StrEnum):
    """The four ISO/IEC 27005 risk-treatment options."""

    MITIGATE = "mitigate"
    ACCEPT = "accept"
    TRANSFER = "transfer"
    AVOID = "avoid"


class AcceptanceDecision(StrEnum):
    """Management's decision on a (residual) risk."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class RiskBand(StrEnum):
    """Severity band derived from a likelihood x impact score (see ``workflow.scoring``)."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewState(StrEnum):
    """Where a due date sits relative to today (see ``workflow.duedates``)."""

    CURRENT = "current"
    DUE_SOON = "due_soon"
    OVERDUE = "overdue"


class EvidenceType(StrEnum):
    """The kind of artifact an evidence record points at."""

    SCREENSHOT = "screenshot"
    CONFIG_EXPORT = "config_export"
    SCAN_REPORT = "scan_report"
    BACKUP_TEST = "backup_test"
    ACCESS_REVIEW = "access_review"
    TRAINING_RECORD = "training_record"
    POLICY_DOC = "policy_doc"
    LOG_EXPORT = "log_export"
    ATTESTATION = "attestation"
    TEST_RECORD = "test_record"


class Nis2Area(StrEnum):
    """The ten cybersecurity risk-management measures of NIS2 Art. 21(2)(a)-(j), plus the
    Art. 20 management-accountability duty. ``workflow``/``domain.nis2`` map these to the
    exact article references and to Annex A controls."""

    RISK_ANALYSIS = "risk_analysis"  # 21(2)(a)
    INCIDENT_HANDLING = "incident_handling"  # 21(2)(b)
    BUSINESS_CONTINUITY = "business_continuity"  # 21(2)(c)
    SUPPLY_CHAIN = "supply_chain"  # 21(2)(d)
    ACQ_DEV_MAINTENANCE = "acq_dev_maintenance"  # 21(2)(e)
    EFFECTIVENESS = "effectiveness"  # 21(2)(f)
    CYBER_HYGIENE_TRAINING = "cyber_hygiene_training"  # 21(2)(g)
    CRYPTOGRAPHY = "cryptography"  # 21(2)(h)
    HR_ACCESS_ASSET = "hr_access_asset"  # 21(2)(i)
    MFA_COMMS = "mfa_comms"  # 21(2)(j)
    MANAGEMENT_ACCOUNTABILITY = "management_accountability"  # Art. 20


class ReportingPhase(StrEnum):
    """NIS2 Art. 23 incident-reporting phases and their statutory deadlines."""

    EARLY_WARNING = "early_warning"  # 24 hours
    NOTIFICATION = "notification"  # 72 hours
    PROGRESS_UPDATE = "progress_update"  # upon CSIRT request
    FINAL_REPORT = "final_report"  # 1 month


class ActionSource(StrEnum):
    """What triggered an improvement action (CAPA)."""

    INTERNAL_AUDIT = "internal_audit"
    MANAGEMENT_REVIEW = "management_review"
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT = "incident"
    VULNERABILITY = "vulnerability"
    EVIDENCE_REVIEW = "evidence_review"


class ActionStatus(StrEnum):
    """Lifecycle of an improvement action."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    DONE = "done"
    VERIFIED = "verified"
    CANCELLED = "cancelled"


class TaskStatus(StrEnum):
    """State of a single task inside a security initiative."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class InitiativeStatus(StrEnum):
    """State of a security initiative / proof-of-concept."""

    PROPOSED = "proposed"
    IN_PROGRESS = "in_progress"
    PILOTING = "piloting"
    DONE = "done"
    ON_HOLD = "on_hold"
