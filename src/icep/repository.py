"""The in-memory :class:`IcepRepository`: one validated, cross-referenced view of the register.

Everything downstream -- the dashboard, the CLI, the metrics, the audit pack -- reads through the
repository. It indexes entities by id, resolves the relationships between them, and runs a
structural integrity check (no dangling references, SoA covers the whole catalog, every NIS2 area
maps to a real control). ``icep validate`` and the integrity tests are thin wrappers over
:meth:`check_integrity`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from icep.config import Settings
from icep.domain import (
    AnnexAControl,
    CompletionRecord,
    Control,
    ControlStatus,
    Evidence,
    ImprovementAction,
    Initiative,
    Nis2Area,
    Nis2Measure,
    Nis2Reporting,
    Policy,
    Quiz,
    Risk,
    SoAEntry,
    Training,
)
from icep.domain.organization import OrganizationProfile
from icep.loader import RegisterData, load_register

__all__ = ["IntegrityIssue", "IcepRepository"]

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class IntegrityIssue:
    """One finding from the structural integrity check."""

    severity: Severity
    category: str
    message: str


class IcepRepository:
    """A validated, indexed, cross-referenced view of the whole ISMS register."""

    def __init__(self, data: RegisterData) -> None:
        self.organization: OrganizationProfile = data.organization
        self.catalog: list[AnnexAControl] = data.catalog
        self.soa: list[SoAEntry] = data.soa
        self.controls: list[Control] = data.controls
        self.risks: list[Risk] = data.risks
        self.evidence: list[Evidence] = data.evidence
        self.policies: list[Policy] = data.policies
        self.nis2_measures: list[Nis2Measure] = data.nis2_measures
        self.nis2_reporting: list[Nis2Reporting] = data.nis2_reporting
        self.actions: list[ImprovementAction] = data.actions
        self.initiatives: list[Initiative] = data.initiatives
        self.trainings: list[Training] = data.trainings
        self.quizzes: list[Quiz] = data.quizzes
        self.completions: list[CompletionRecord] = data.completions

        # id indexes
        self.catalog_by_id = {c.id: c for c in self.catalog}
        self.soa_by_id = {e.control_id: e for e in self.soa}
        self.controls_by_id = {c.id: c for c in self.controls}
        self.risks_by_id = {r.id: r for r in self.risks}
        self.evidence_by_id = {e.id: e for e in self.evidence}
        self.policies_by_id = {p.id: p for p in self.policies}
        self.nis2_by_area = {m.area: m for m in self.nis2_measures}
        self.training_by_id = {t.id: t for t in self.trainings}

    # ------------------------------------------------------------------ loading
    @classmethod
    def load(cls, settings: Settings | None = None) -> IcepRepository:
        """Load, validate and index the register from ``settings.data_dir``."""
        return cls(load_register(settings))

    # -------------------------------------------------------------- id lookups
    def control(self, control_id: str) -> Control | None:
        return self.controls_by_id.get(control_id)

    def risk(self, risk_id: str) -> Risk | None:
        return self.risks_by_id.get(risk_id)

    def evidence_item(self, evidence_id: str) -> Evidence | None:
        return self.evidence_by_id.get(evidence_id)

    def policy(self, policy_id: str) -> Policy | None:
        return self.policies_by_id.get(policy_id)

    # ---------------------------------------------------------- relationships
    @property
    def documented_control_ids(self) -> set[str]:
        return set(self.controls_by_id)

    @property
    def applicable_control_ids(self) -> set[str]:
        return {e.control_id for e in self.soa if e.applicable}

    def evidence_for_control(self, control_id: str) -> list[Evidence]:
        return [e for e in self.evidence if control_id in e.control_refs]

    def risks_for_control(self, control_id: str) -> list[Risk]:
        return [r for r in self.risks if control_id in r.control_refs]

    def policies_for_control(self, control_id: str) -> list[Policy]:
        return [p for p in self.policies if control_id in p.control_refs]

    def actions_for_control(self, control_id: str) -> list[ImprovementAction]:
        return [a for a in self.actions if control_id in a.control_refs]

    def controls_for_nis2_area(self, area: Nis2Area) -> list[Control]:
        measure = self.nis2_by_area.get(area)
        if measure is None:
            return []
        return [self.controls_by_id[c] for c in measure.control_refs if c in self.controls_by_id]

    # --------------------------------------------------------------- integrity
    def check_integrity(self) -> list[IntegrityIssue]:
        """Return all structural issues (errors, warnings, info), ordered by severity."""
        issues: list[IntegrityIssue] = []

        def add(severity: Severity, category: str, message: str) -> None:
            issues.append(IntegrityIssue(severity, category, message))

        catalog_ids = set(self.catalog_by_id)
        soa_ids = set(self.soa_by_id)
        documented = self.documented_control_ids

        # duplicate primary keys (the by-id indexes silently collapse them, desyncing counts)
        def _dupes(name: str, ids: list[str]) -> None:
            seen: set[str] = set()
            for ident in ids:
                if ident in seen:
                    add("error", "duplicate", f"duplicate {name} id {ident}")
                seen.add(ident)

        _dupes("catalog control", [c.id for c in self.catalog])
        _dupes("SoA entry", [e.control_id for e in self.soa])
        _dupes("control", [c.id for c in self.controls])
        _dupes("risk", [r.id for r in self.risks])
        _dupes("evidence", [e.id for e in self.evidence])
        _dupes("policy", [p.id for p in self.policies])
        _dupes("improvement action", [a.id for a in self.actions])
        _dupes("initiative", [i.id for i in self.initiatives])

        # SoA <-> catalog completeness
        for cid in sorted(catalog_ids - soa_ids):
            add("error", "soa", f"catalog control {cid} has no Statement-of-Applicability entry")
        for cid in sorted(soa_ids - catalog_ids):
            add("error", "soa", f"SoA entry {cid} is not a valid Annex A control")

        # documented controls must be real Annex A controls
        for cid in sorted(documented - catalog_ids):
            add("error", "control", f"documented control {cid} is not in the Annex A catalog")

        # dangling references out of controls
        for control in self.controls:
            for pid in control.policy_refs:
                if pid not in self.policies_by_id:
                    add(
                        "error",
                        "reference",
                        f"control {control.id} references unknown policy {pid}",
                    )
            for eid in control.evidence_refs:
                if eid not in self.evidence_by_id:
                    add(
                        "error",
                        "reference",
                        f"control {control.id} references unknown evidence {eid}",
                    )
            for rid in control.risk_refs:
                if rid not in self.risks_by_id:
                    add("error", "reference", f"control {control.id} references unknown risk {rid}")

        # references into controls must resolve to documented controls
        for evidence in self.evidence:
            for cid in evidence.control_refs:
                if cid not in documented:
                    add(
                        "error",
                        "reference",
                        f"evidence {evidence.id} references undocumented control {cid}",
                    )
        for risk in self.risks:
            for cid in risk.control_refs:
                if cid not in documented:
                    add(
                        "error",
                        "reference",
                        f"risk {risk.id} references undocumented control {cid}",
                    )
        for policy in self.policies:
            for cid in policy.control_refs:
                if cid not in documented:
                    add(
                        "error",
                        "reference",
                        f"policy {policy.id} references undocumented control {cid}",
                    )

        # NIS2: every measure resolves, and every area is covered
        covered_areas: set[Nis2Area] = set()
        for measure in self.nis2_measures:
            covered_areas.add(measure.area)
            for cid in measure.control_refs:
                if cid not in documented:
                    add(
                        "error",
                        "nis2",
                        f"NIS2 {measure.article} references undocumented control {cid}",
                    )
        for area in Nis2Area:
            if area not in covered_areas:
                add("error", "nis2", f"NIS2 area '{area.value}' is not covered by any measure")

        # initiatives + actions
        for initiative in self.initiatives:
            for cid in initiative.control_refs:
                if cid not in documented:
                    add(
                        "error",
                        "reference",
                        f"initiative {initiative.id} references undocumented control {cid}",
                    )
            for eid in initiative.evidence_refs:
                if eid not in self.evidence_by_id:
                    add(
                        "error",
                        "reference",
                        f"initiative {initiative.id} references unknown evidence {eid}",
                    )
            for criterion in initiative.acceptance_criteria:
                ref = criterion.evidence_ref
                if ref is not None and ref not in self.evidence_by_id:
                    add(
                        "error",
                        "reference",
                        f"initiative {initiative.id} criterion {criterion.id} references unknown evidence {ref}",
                    )
        for action in self.actions:
            for cid in action.control_refs:
                if cid not in documented:
                    add(
                        "error",
                        "reference",
                        f"action {action.id} references undocumented control {cid}",
                    )
            for rid in action.risk_refs:
                if rid not in self.risks_by_id:
                    add("error", "reference", f"action {action.id} references unknown risk {rid}")

        # training linkage
        for quiz in self.quizzes:
            if quiz.training_ref not in self.training_by_id:
                add(
                    "error",
                    "training",
                    f"quiz {quiz.id} references unknown training {quiz.training_ref}",
                )
        for record in self.completions:
            if record.training_ref not in self.training_by_id:
                add(
                    "error",
                    "training",
                    f"completion references unknown training {record.training_ref}",
                )

        # warnings + info (never fail the gate, but surface real gaps)
        for control in self.controls:
            if (
                control.status in {ControlStatus.OPERATING, ControlStatus.IMPLEMENTED}
                and not control.evidence_refs
            ):
                add(
                    "warning",
                    "evidence",
                    f"control {control.id} is {control.status.value} but has no evidence",
                )

        undocumented_applicable = self.applicable_control_ids - documented
        if undocumented_applicable:
            add(
                "info",
                "coverage",
                f"{len(undocumented_applicable)} applicable control(s) are covered at SoA level only "
                f"(no full control record yet)",
            )

        order: dict[Severity, int] = {"error": 0, "warning": 1, "info": 2}
        return sorted(issues, key=lambda i: (order[i.severity], i.category, i.message))

    def integrity_errors(self) -> list[IntegrityIssue]:
        """Just the blocking issues."""
        return [issue for issue in self.check_integrity() if issue.severity == "error"]
