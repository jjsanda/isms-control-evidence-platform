"""Integrity of the committed register: it must load, resolve, and be ISO-complete.

These tests run against the real ``data/`` register (not fixtures) -- they are the guarantee that
the shipped ISMS content is internally consistent and matches ISO/IEC 27001:2022 Annex A.
"""

from __future__ import annotations

from collections import Counter

import pytest

from icep.domain import Nis2Area, Theme
from icep.repository import IcepRepository

pytestmark = pytest.mark.integrity


@pytest.fixture(scope="module")
def repo() -> IcepRepository:
    return IcepRepository.load()


def test_register_loads_without_integrity_errors(repo: IcepRepository) -> None:
    errors = repo.integrity_errors()
    assert errors == [], "\n".join(f"{e.category}: {e.message}" for e in errors)


def test_catalog_has_93_controls(repo: IcepRepository) -> None:
    assert len(repo.catalog) == 93


def test_annex_a_theme_counts(repo: IcepRepository) -> None:
    counts = Counter(control.theme for control in repo.catalog)
    assert counts[Theme.ORGANIZATIONAL] == 37
    assert counts[Theme.PEOPLE] == 8
    assert counts[Theme.PHYSICAL] == 14
    assert counts[Theme.TECHNOLOGICAL] == 34


def test_exactly_eleven_new_2022_controls(repo: IcepRepository) -> None:
    new_ids = {c.id for c in repo.catalog if c.is_new_2022}
    assert new_ids == {
        "A.5.7",
        "A.5.23",
        "A.5.30",
        "A.7.4",
        "A.8.9",
        "A.8.10",
        "A.8.11",
        "A.8.12",
        "A.8.16",
        "A.8.23",
        "A.8.28",
    }


def test_soa_covers_every_catalog_control(repo: IcepRepository) -> None:
    assert {e.control_id for e in repo.soa} == {c.id for c in repo.catalog}


def test_all_eleven_nis2_areas_are_mapped(repo: IcepRepository) -> None:
    assert set(repo.nis2_by_area) == set(Nis2Area)
    for measure in repo.nis2_measures:
        assert measure.control_refs, f"{measure.article} maps to no control"


def test_representative_control_count(repo: IcepRepository) -> None:
    assert len(repo.controls) == 25
    # spans all four themes
    assert {c.theme for c in repo.controls} == set(Theme)


def test_every_reference_resolves(repo: IcepRepository) -> None:
    documented = repo.documented_control_ids
    for control in repo.controls:
        assert all(p in repo.policies_by_id for p in control.policy_refs)
        assert all(e in repo.evidence_by_id for e in control.evidence_refs)
        assert all(r in repo.risks_by_id for r in control.risk_refs)
    for evidence in repo.evidence:
        assert all(c in documented for c in evidence.control_refs)
    for risk in repo.risks:
        assert all(c in documented for c in risk.control_refs)
    for measure in repo.nis2_measures:
        assert all(c in documented for c in measure.control_refs)


def test_relationship_helpers(repo: IcepRepository) -> None:
    # A.8.16 (Monitoring activities) is wired to evidence, a risk and a NIS2 area in the register.
    assert repo.control("A.8.16") is not None
    assert repo.evidence_for_control("A.8.16")
    assert repo.controls_for_nis2_area(Nis2Area.INCIDENT_HANDLING)


def test_accepted_risks_have_an_approver(repo: IcepRepository) -> None:
    from icep.domain import AcceptanceDecision

    for risk in repo.risks:
        if risk.acceptance is AcceptanceDecision.ACCEPTED:
            assert risk.accepted_by is not None
