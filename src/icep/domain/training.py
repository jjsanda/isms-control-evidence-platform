"""Security-awareness training, its quiz, completion records, and pure quiz scoring."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date
from typing import Self

from pydantic import Field, model_validator

from icep.domain.common import IcepModel, OwnerRef, TrainingId
from icep.domain.enums import Nis2Area

__all__ = [
    "Training",
    "QuizQuestion",
    "Quiz",
    "CompletionRecord",
    "QuizResult",
    "score_quiz",
]


class Training(IcepModel):
    """An awareness-training module (the internal training page lives in ``body_markdown``)."""

    id: TrainingId
    title: str = Field(min_length=1, max_length=200)
    audience: str = Field(min_length=1, max_length=200)
    version: str = Field(min_length=1, max_length=20)
    learning_objectives: list[str] = Field(min_length=1)
    nis2_areas: list[Nis2Area] = Field(default_factory=list)
    body_markdown: str = Field(min_length=1)


class QuizQuestion(IcepModel):
    """A single multiple-choice question with exactly one correct option."""

    id: str = Field(min_length=1, max_length=20, description="e.g. 'Q1'.")
    prompt: str = Field(min_length=1, max_length=400)
    options: list[str] = Field(min_length=2)
    correct_index: int = Field(ge=0)
    explanation: str = Field(default="", max_length=600)

    @model_validator(mode="after")
    def _check(self) -> Self:
        if self.correct_index >= len(self.options):
            raise ValueError(f"{self.id}: correct_index {self.correct_index} out of range")
        return self


class Quiz(IcepModel):
    """A short quiz gating training completion."""

    id: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=200)
    training_ref: TrainingId
    pass_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    questions: list[QuizQuestion] = Field(min_length=1)


class CompletionRecord(IcepModel):
    """Evidence that a named person completed the training and passed the quiz."""

    person: OwnerRef
    training_ref: TrainingId
    completed_on: date
    score: float = Field(ge=0.0, le=1.0)
    passed: bool


class QuizResult(IcepModel):
    """The outcome of scoring a set of answers against a quiz."""

    total: int = Field(ge=1)
    correct: int = Field(ge=0)
    score: float = Field(ge=0.0, le=1.0)
    passed: bool


def score_quiz(quiz: Quiz, answers: Mapping[str, int]) -> QuizResult:
    """Score ``answers`` (question id -> chosen option index) against ``quiz``.

    >>> q = Quiz(
    ...     id="QZ1", title="Basics", training_ref="TRN-001",
    ...     questions=[
    ...         QuizQuestion(id="Q1", prompt="a?", options=["x", "y"], correct_index=1),
    ...         QuizQuestion(id="Q2", prompt="b?", options=["x", "y"], correct_index=0),
    ...     ],
    ... )
    >>> score_quiz(q, {"Q1": 1, "Q2": 0}).passed
    True
    >>> r = score_quiz(q, {"Q1": 0, "Q2": 0})
    >>> (r.correct, r.total, round(r.score, 2), r.passed)
    (1, 2, 0.5, False)
    """
    total = len(quiz.questions)
    correct = sum(
        1 for question in quiz.questions if answers.get(question.id) == question.correct_index
    )
    score = correct / total
    return QuizResult(
        total=total, correct=correct, score=score, passed=score >= quiz.pass_threshold
    )
