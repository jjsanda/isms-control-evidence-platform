"""Run the doctests embedded in the pure-logic modules as part of the suite.

The scoring, audit, due-date, clock and quiz docstrings carry worked examples; treating them as
tests keeps the documentation honest.
"""

from __future__ import annotations

import doctest
from types import ModuleType

import pytest

import icep.clock
import icep.domain.common
import icep.domain.training
import icep.workflow.audit
import icep.workflow.duedates
import icep.workflow.scoring

pytestmark = pytest.mark.unit

MODULES: list[ModuleType] = [
    icep.clock,
    icep.domain.common,
    icep.workflow.scoring,
    icep.workflow.audit,
    icep.workflow.duedates,
    icep.domain.training,
]


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.__name__)
def test_module_doctests(module: ModuleType) -> None:
    results = doctest.testmod(module, verbose=False)
    assert results.failed == 0, f"{results.failed} doctest failure(s) in {module.__name__}"
    assert results.attempted > 0, f"no doctests found in {module.__name__}"
