"""Domain models for the ISMS register (all Pydantic v2, ``extra='forbid'``)."""

from __future__ import annotations

from icep.domain.action import ImprovementAction
from icep.domain.catalog import AnnexAControl, SoAEntry
from icep.domain.common import (
    ActionId,
    ControlId,
    Email,
    EvidenceId,
    IcepModel,
    InitiativeId,
    OwnerRef,
    PolicyId,
    RiskId,
    TrainingId,
)
from icep.domain.control import Control
from icep.domain.enums import (
    AcceptanceDecision,
    ActionSource,
    ActionStatus,
    AuditStatus,
    ControlStatus,
    EvidenceType,
    InclusionReason,
    InitiativeStatus,
    Nis2Area,
    ReportingPhase,
    ReviewState,
    RiskBand,
    TaskStatus,
    Theme,
    TreatmentOption,
)
from icep.domain.evidence import Evidence
from icep.domain.initiative import AcceptanceCriterion, Initiative, Task
from icep.domain.nis2 import NIS2_ARTICLE, NIS2_TITLE, Nis2Measure, Nis2Reporting
from icep.domain.policy import Policy
from icep.domain.risk import Risk
from icep.domain.training import (
    CompletionRecord,
    Quiz,
    QuizQuestion,
    QuizResult,
    Training,
    score_quiz,
)

__all__ = [
    # base + value objects + id aliases
    "IcepModel",
    "OwnerRef",
    "Email",
    "ControlId",
    "RiskId",
    "EvidenceId",
    "PolicyId",
    "ActionId",
    "InitiativeId",
    "TrainingId",
    # entities
    "Control",
    "Risk",
    "Evidence",
    "Policy",
    "Nis2Measure",
    "Nis2Reporting",
    "ImprovementAction",
    "Initiative",
    "Task",
    "AcceptanceCriterion",
    "Training",
    "Quiz",
    "QuizQuestion",
    "QuizResult",
    "CompletionRecord",
    "AnnexAControl",
    "SoAEntry",
    "score_quiz",
    # nis2 reference maps
    "NIS2_ARTICLE",
    "NIS2_TITLE",
    # enums
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
