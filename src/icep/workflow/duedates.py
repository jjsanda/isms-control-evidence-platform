"""Due-date classification for reviews and evidence validity.

A single rule drives every "is this overdue?" badge in the dashboard and the expiry section of the
audit pack: past = OVERDUE, within the warning window = DUE_SOON, otherwise CURRENT.

>>> from datetime import date
>>> classify(date(2026, 6, 1), today=date(2026, 7, 7))
<ReviewState.OVERDUE: 'overdue'>
>>> classify(date(2026, 7, 20), today=date(2026, 7, 7), warn_days=30)
<ReviewState.DUE_SOON: 'due_soon'>
>>> classify(date(2027, 1, 1), today=date(2026, 7, 7))
<ReviewState.CURRENT: 'current'>
"""

from __future__ import annotations

from datetime import date, timedelta

from icep.domain.enums import ReviewState

__all__ = ["DEFAULT_WARN_DAYS", "classify", "days_until"]

DEFAULT_WARN_DAYS = 30


def classify(due: date, today: date, warn_days: int = DEFAULT_WARN_DAYS) -> ReviewState:
    """Classify a due date relative to ``today`` and a ``warn_days`` lead time."""
    if due < today:
        return ReviewState.OVERDUE
    if due <= today + timedelta(days=warn_days):
        return ReviewState.DUE_SOON
    return ReviewState.CURRENT


def days_until(due: date, today: date) -> int:
    """Signed days from ``today`` to ``due`` (negative when overdue).

    >>> from datetime import date
    >>> days_until(date(2026, 7, 20), date(2026, 7, 7))
    13
    >>> days_until(date(2026, 7, 1), date(2026, 7, 7))
    -6
    """
    return (due - today).days
