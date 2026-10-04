"""Load the YAML register into validated Pydantic models, aggregating every error.

The loader never loads a half-valid register: it collects *all* schema problems across *all* files
and raises a single :class:`LoaderError` listing them, so a typo in one control doesn't hide a
problem in another. This is what lets the web app "refuse to boot on invalid data" with a useful
message, and what the schema test asserts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from icep.config import Settings, get_settings
from icep.domain import (
    AnnexAControl,
    CompletionRecord,
    Control,
    Evidence,
    ImprovementAction,
    Initiative,
    Nis2Measure,
    Nis2Reporting,
    Policy,
    Quiz,
    Risk,
    SoAEntry,
    Training,
)
from icep.domain.organization import OrganizationProfile

__all__ = ["LoaderError", "RegisterData", "load_register"]


class LoaderError(Exception):
    """Raised when one or more register files fail to parse or validate."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        joined = "\n  - ".join(errors)
        super().__init__(f"{len(errors)} problem(s) loading the ISMS register:\n  - {joined}")


@dataclass(frozen=True)
class RegisterData:
    """The whole register, parsed and validated -- the raw material for the repository."""

    organization: OrganizationProfile
    catalog: list[AnnexAControl]
    soa: list[SoAEntry]
    controls: list[Control]
    risks: list[Risk]
    evidence: list[Evidence]
    policies: list[Policy]
    nis2_measures: list[Nis2Measure]
    nis2_reporting: list[Nis2Reporting]
    actions: list[ImprovementAction]
    initiatives: list[Initiative]
    trainings: list[Training]
    quizzes: list[Quiz]
    completions: list[CompletionRecord]


def _rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _format_validation_error(exc: ValidationError, where: str) -> list[str]:
    out: list[str] = []
    for err in exc.errors():
        loc = ".".join(str(p) for p in err["loc"]) or "(root)"
        out.append(f"{where}: {loc}: {err['msg']}")
    return out


def _read_yaml(path: Path, root: Path, errors: list[str]) -> Any:
    if not path.exists():
        errors.append(f"{_rel(path, root)}: file not found")
        return None
    try:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        errors.append(f"{_rel(path, root)}: invalid YAML: {exc}")
        return None
    if data is None:
        errors.append(f"{_rel(path, root)}: file is empty")
        return None
    return data


def _load_one[TModel: BaseModel](
    path: Path, model: type[TModel], root: Path, errors: list[str]
) -> TModel | None:
    raw = _read_yaml(path, root, errors)
    if raw is None:
        return None
    if not isinstance(raw, dict):
        errors.append(f"{_rel(path, root)}: expected a mapping, got {type(raw).__name__}")
        return None
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        errors.extend(_format_validation_error(exc, _rel(path, root)))
        return None


def _load_collection[TModel: BaseModel](
    path: Path, key: str, model: type[TModel], root: Path, errors: list[str]
) -> list[TModel]:
    raw = _read_yaml(path, root, errors)
    if raw is None:
        return []
    if not isinstance(raw, dict) or key not in raw:
        errors.append(f"{_rel(path, root)}: expected a mapping with a '{key}:' list")
        return []
    items = raw[key]
    if not isinstance(items, list):
        errors.append(f"{_rel(path, root)}: '{key}' must be a list")
        return []
    out: list[TModel] = []
    for index, item in enumerate(items):
        where = f"{_rel(path, root)}[{key}][{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: expected a mapping, got {type(item).__name__}")
            continue
        try:
            out.append(model.model_validate(item))
        except ValidationError as exc:
            errors.extend(_format_validation_error(exc, where))
    return out


def _load_dir[TModel: BaseModel](
    directory: Path, model: type[TModel], root: Path, errors: list[str]
) -> list[TModel]:
    if not directory.is_dir():
        return []
    out: list[TModel] = []
    for path in sorted(directory.glob("*.yaml")):
        parsed = _load_one(path, model, root, errors)
        if parsed is not None:
            out.append(parsed)
    return out


def load_register(settings: Settings | None = None) -> RegisterData:
    """Load and validate the entire register, raising :class:`LoaderError` on any problem."""
    settings = settings or get_settings()
    root = settings.data_dir
    errors: list[str] = []

    organization = _load_one(root / "organization.yaml", OrganizationProfile, root, errors)
    catalog = _load_collection(
        root / "catalog" / "iso27001-2022-annexa.yaml", "controls", AnnexAControl, root, errors
    )
    soa = _load_collection(
        root / "statement_of_applicability.yaml", "entries", SoAEntry, root, errors
    )
    controls = _load_dir(root / "controls", Control, root, errors)
    risks = _load_dir(root / "risks", Risk, root, errors)
    evidence = _load_dir(root / "evidence", Evidence, root, errors)
    policies = _load_dir(root / "policies", Policy, root, errors)
    nis2_measures = _load_collection(
        root / "nis2" / "art21-measures.yaml", "measures", Nis2Measure, root, errors
    )
    nis2_reporting = _load_collection(
        root / "nis2" / "art23-reporting.yaml", "phases", Nis2Reporting, root, errors
    )
    actions = _load_dir(root / "actions", ImprovementAction, root, errors)
    initiatives = _load_dir(root / "initiatives", Initiative, root, errors)
    awareness = _load_one(root / "training" / "awareness.yaml", Training, root, errors)
    quiz = _load_one(root / "training" / "quiz.yaml", Quiz, root, errors)
    completions = _load_collection(
        root / "training" / "completions.yaml", "records", CompletionRecord, root, errors
    )

    # A missing/empty/invalid file already appended an error above; guard the required singletons
    # explicitly (rather than assert) so this holds even under `python -O`.
    if errors or organization is None or awareness is None or quiz is None:
        raise LoaderError(errors or ["the register is missing a required file"])

    return RegisterData(
        organization=organization,
        catalog=catalog,
        soa=soa,
        controls=controls,
        risks=risks,
        evidence=evidence,
        policies=policies,
        nis2_measures=nis2_measures,
        nis2_reporting=nis2_reporting,
        actions=actions,
        initiatives=initiatives,
        trainings=[awareness],
        quizzes=[quiz],
        completions=completions,
    )
