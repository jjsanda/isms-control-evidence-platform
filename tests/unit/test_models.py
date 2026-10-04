from __future__ import annotations

from collections.abc import Callable
from datetime import date

import pytest
from pydantic import ValidationError

from icep.domain import (
    AcceptanceDecision,
    Control,
    ControlStatus,
    Evidence,
    OwnerRef,
    Quiz,
    QuizQuestion,
    RiskBand,
    score_quiz,
)

pytestmark = pytest.mark.unit


class TestControl:
    def test_valid(self, make_control: Callable[..., Control]) -> None:
        c = make_control()
        assert c.id == "A.8.16"

    def test_extra_field_rejected(self, make_control: Callable[..., Control]) -> None:
        with pytest.raises(ValidationError):
            make_control(unexpected="nope")

    @pytest.mark.parametrize("bad_id", ["5.1", "A.5", "A5.1", "B.5.1", "a.5.1"])
    def test_bad_id_pattern(self, make_control: Callable[..., Control], bad_id: str) -> None:
        with pytest.raises(ValidationError):
            make_control(id=bad_id)

    def test_excluded_control_must_be_not_applicable(
        self, make_control: Callable[..., Control]
    ) -> None:
        with pytest.raises(ValidationError):
            make_control(applicable=False, status=ControlStatus.IMPLEMENTED)

    def test_applicable_control_cannot_be_not_applicable(
        self, make_control: Callable[..., Control]
    ) -> None:
        with pytest.raises(ValidationError):
            make_control(applicable=True, status=ControlStatus.NOT_APPLICABLE)

    def test_excluded_control_ok_when_not_applicable(
        self, make_control: Callable[..., Control]
    ) -> None:
        c = make_control(applicable=False, status=ControlStatus.NOT_APPLICABLE)
        assert c.status is ControlStatus.NOT_APPLICABLE

    def test_next_review_before_last_review_rejected(
        self, make_control: Callable[..., Control]
    ) -> None:
        with pytest.raises(ValidationError):
            make_control(last_review=date(2026, 6, 1), next_review=date(2026, 1, 1))

    def test_maturity_bounds(self, make_control: Callable[..., Control]) -> None:
        with pytest.raises(ValidationError):
            make_control(maturity=0)
        with pytest.raises(ValidationError):
            make_control(maturity=6)


class TestRisk:
    def test_scoring_properties(self, make_risk: Callable[..., object]) -> None:
        r = make_risk()  # inherent 4x5=20 (critical), residual 2x4=8 (medium)
        assert r.inherent_score == 20  # type: ignore[attr-defined]
        assert r.inherent_band is RiskBand.CRITICAL  # type: ignore[attr-defined]
        assert r.residual_score == 8  # type: ignore[attr-defined]
        assert r.residual_band is RiskBand.MEDIUM  # type: ignore[attr-defined]
        assert r.reduction == 12  # type: ignore[attr-defined]

    def test_residual_cannot_exceed_inherent(self, make_risk: Callable[..., object]) -> None:
        with pytest.raises(ValidationError):
            make_risk(residual_impact=5, inherent_impact=4)
        with pytest.raises(ValidationError):
            make_risk(residual_likelihood=5, inherent_likelihood=4)

    def test_accepted_risk_needs_accepted_by(self, make_risk: Callable[..., object]) -> None:
        with pytest.raises(ValidationError):
            make_risk(acceptance=AcceptanceDecision.ACCEPTED, accepted_by=None)

    def test_accepted_risk_with_owner_ok(self, make_risk: Callable[..., object]) -> None:
        acceptor = OwnerRef(name="Dana Weber", role="Managing Director")
        r = make_risk(acceptance=AcceptanceDecision.ACCEPTED, accepted_by=acceptor)
        assert r.acceptance is AcceptanceDecision.ACCEPTED  # type: ignore[attr-defined]


class TestEvidence:
    def test_validity_window_ordering(self, make_evidence: Callable[..., Evidence]) -> None:
        with pytest.raises(ValidationError):
            make_evidence(valid_from=date(2026, 6, 1), valid_until=date(2026, 5, 1))

    def test_valid_from_not_before_collected(self, make_evidence: Callable[..., Evidence]) -> None:
        with pytest.raises(ValidationError):
            make_evidence(collected_on=date(2026, 6, 1), valid_from=date(2026, 5, 1))

    def test_is_expired(self, make_evidence: Callable[..., Evidence]) -> None:
        ev = make_evidence(valid_until=date(2026, 6, 30))
        assert ev.is_expired(date(2026, 7, 7)) is True
        assert ev.is_expired(date(2026, 6, 15)) is False

    def test_needs_at_least_one_control_ref(self, make_evidence: Callable[..., Evidence]) -> None:
        with pytest.raises(ValidationError):
            make_evidence(control_refs=[])

    @pytest.mark.parametrize("bad", ["abc", "0" * 63, "g" * 64, "0" * 65])
    def test_bad_sha256_rejected(self, make_evidence: Callable[..., Evidence], bad: str) -> None:
        with pytest.raises(ValidationError):
            make_evidence(sha256=bad)

    def test_good_sha256_accepted(self, make_evidence: Callable[..., Evidence]) -> None:
        ev = make_evidence(sha256="a" * 64)
        assert ev.sha256 == "a" * 64


class TestQuiz:
    def _quiz(self) -> Quiz:
        return Quiz(
            id="QZ1",
            title="Phishing basics",
            training_ref="TRN-001",
            questions=[
                QuizQuestion(id="Q1", prompt="a?", options=["x", "y"], correct_index=1),
                QuizQuestion(id="Q2", prompt="b?", options=["x", "y"], correct_index=0),
            ],
        )

    def test_correct_index_must_be_in_range(self) -> None:
        with pytest.raises(ValidationError):
            QuizQuestion(id="Q9", prompt="?", options=["x", "y"], correct_index=2)

    def test_scoring_pass_and_fail(self) -> None:
        quiz = self._quiz()
        assert score_quiz(quiz, {"Q1": 1, "Q2": 0}).passed is True
        result = score_quiz(quiz, {"Q1": 0, "Q2": 0})
        assert (result.correct, result.total, result.passed) == (1, 2, False)

    def test_missing_answer_counts_wrong(self) -> None:
        quiz = self._quiz()
        result = score_quiz(quiz, {"Q1": 1})
        assert result.correct == 1
        assert result.passed is False
