from __future__ import annotations

from datetime import date

import pytest

from icep.domain.enums import AuditStatus
from icep.workflow.audit import (
    IllegalTransitionError,
    can_transition,
    effective_status,
    transition,
)

pytestmark = pytest.mark.unit

D, R, A, E = AuditStatus.DRAFT, AuditStatus.REVIEWED, AuditStatus.ACCEPTED, AuditStatus.EXPIRED

LEGAL = [(D, R), (R, A), (R, D), (A, R), (A, E), (E, D), (E, R)]
ILLEGAL = [
    (D, A),  # cannot accept without review (segregation of duties)
    (D, E),
    (D, D),  # no self-loops
    (A, D),  # must go back via 'reviewed'
    (R, E),
    (R, R),
    (A, A),
    (E, E),
    (E, A),
]


@pytest.mark.parametrize(("current", "target"), LEGAL)
def test_legal_transitions(current: AuditStatus, target: AuditStatus) -> None:
    assert can_transition(current, target) is True
    assert transition(current, target) is target


@pytest.mark.parametrize(("current", "target"), ILLEGAL)
def test_illegal_transitions_raise(current: AuditStatus, target: AuditStatus) -> None:
    assert can_transition(current, target) is False
    with pytest.raises(IllegalTransitionError):
        transition(current, target)


def test_legal_and_illegal_partition_the_matrix() -> None:
    # every (from, to) pair with distinct-or-equal states is covered exactly once by the two lists
    assert set(LEGAL).isdisjoint(ILLEGAL)
    assert len(LEGAL) + len(ILLEGAL) == len(list(AuditStatus)) ** 2


class TestEffectiveStatus:
    today = date(2026, 7, 7)

    def test_accepted_but_past_review_reads_as_expired(self) -> None:
        assert effective_status(A, date(2026, 1, 1), self.today) is E

    def test_accepted_and_current_stays_accepted(self) -> None:
        assert effective_status(A, date(2026, 12, 1), self.today) is A

    @pytest.mark.parametrize("stored", [D, R, E])
    def test_non_accepted_is_never_auto_expired(self, stored: AuditStatus) -> None:
        # only an *accepted* item lapses to expired; drafts/reviewed keep their stored status
        assert effective_status(stored, date(2026, 1, 1), self.today) is stored
