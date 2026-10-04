from __future__ import annotations

from datetime import date

import pytest

from icep.domain.enums import ReviewState
from icep.workflow.duedates import classify, days_until

pytestmark = pytest.mark.unit

TODAY = date(2026, 7, 7)


@pytest.mark.parametrize(
    ("due", "expected"),
    [
        (date(2026, 7, 6), ReviewState.OVERDUE),  # yesterday
        (date(2026, 7, 7), ReviewState.DUE_SOON),  # today counts as due soon
        (date(2026, 8, 6), ReviewState.DUE_SOON),  # exactly warn_days ahead (inclusive)
        (date(2026, 8, 7), ReviewState.CURRENT),  # one day past the window
        (date(2027, 1, 1), ReviewState.CURRENT),
    ],
)
def test_classify_boundaries(due: date, expected: ReviewState) -> None:
    assert classify(due, TODAY, warn_days=30) is expected


def test_classify_respects_custom_warn_days() -> None:
    due = date(2026, 7, 14)
    assert classify(due, TODAY, warn_days=3) is ReviewState.CURRENT
    assert classify(due, TODAY, warn_days=7) is ReviewState.DUE_SOON


def test_days_until_is_signed() -> None:
    assert days_until(date(2026, 7, 20), TODAY) == 13
    assert days_until(date(2026, 7, 7), TODAY) == 0
    assert days_until(date(2026, 7, 1), TODAY) == -6
