"""The audit review state machine: ``draft -> reviewed -> accepted``, lapsing to ``expired``.

Controls and evidence carry an :class:`~icep.domain.enums.AuditStatus`. The allowed transitions
encode segregation of duties (nothing jumps straight from *draft* to *accepted* -- it must be
*reviewed* first) and the reality that an accepted item lapses to *expired* once its review date
passes. :func:`effective_status` applies that time-driven expiry without mutating stored data.

>>> transition(AuditStatus.DRAFT, AuditStatus.REVIEWED)
<AuditStatus.REVIEWED: 'reviewed'>
>>> transition(AuditStatus.DRAFT, AuditStatus.ACCEPTED)
Traceback (most recent call last):
    ...
icep.workflow.audit.IllegalTransitionError: draft -> accepted is not permitted (allowed: reviewed)
"""

from __future__ import annotations

from datetime import date

from icep.domain.enums import AuditStatus

__all__ = [
    "IllegalTransitionError",
    "ALLOWED_TRANSITIONS",
    "can_transition",
    "transition",
    "effective_status",
]


class IllegalTransitionError(ValueError):
    """Raised when an audit-status change is not permitted by the state machine."""


ALLOWED_TRANSITIONS: dict[AuditStatus, frozenset[AuditStatus]] = {
    AuditStatus.DRAFT: frozenset({AuditStatus.REVIEWED}),
    AuditStatus.REVIEWED: frozenset({AuditStatus.ACCEPTED, AuditStatus.DRAFT}),
    AuditStatus.ACCEPTED: frozenset({AuditStatus.REVIEWED, AuditStatus.EXPIRED}),
    AuditStatus.EXPIRED: frozenset({AuditStatus.DRAFT, AuditStatus.REVIEWED}),
}


def can_transition(current: AuditStatus, target: AuditStatus) -> bool:
    """Return whether ``current -> target`` is a permitted transition.

    >>> can_transition(AuditStatus.REVIEWED, AuditStatus.ACCEPTED)
    True
    >>> can_transition(AuditStatus.ACCEPTED, AuditStatus.DRAFT)
    False
    """
    return target in ALLOWED_TRANSITIONS[current]


def transition(current: AuditStatus, target: AuditStatus) -> AuditStatus:
    """Return ``target`` if the move is legal, else raise :class:`IllegalTransitionError`."""
    if not can_transition(current, target):
        allowed = ", ".join(sorted(s.value for s in ALLOWED_TRANSITIONS[current])) or "(none)"
        raise IllegalTransitionError(
            f"{current.value} -> {target.value} is not permitted (allowed: {allowed})"
        )
    return target


def effective_status(stored_status: AuditStatus, next_review: date, today: date) -> AuditStatus:
    """The status *as of today*: an accepted item whose review date has passed reads as expired.

    >>> from datetime import date
    >>> effective_status(AuditStatus.ACCEPTED, date(2026, 1, 1), date(2026, 7, 7))
    <AuditStatus.EXPIRED: 'expired'>
    >>> effective_status(AuditStatus.ACCEPTED, date(2026, 12, 1), date(2026, 7, 7))
    <AuditStatus.ACCEPTED: 'accepted'>
    """
    if stored_status is AuditStatus.ACCEPTED and next_review < today:
        return AuditStatus.EXPIRED
    return stored_status
