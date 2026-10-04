from __future__ import annotations

import pytest

from icep.domain.enums import RiskBand
from icep.workflow.scoring import (
    BAND_COLORS,
    band,
    band_color,
    heatmap_cells,
    residual_reduction,
    score,
)

pytestmark = pytest.mark.unit


def test_score_multiplies_axes() -> None:
    assert score(3, 4) == 12
    assert score(1, 1) == 1
    assert score(5, 5) == 25


@pytest.mark.parametrize(("likelihood", "impact"), [(0, 3), (6, 3), (3, 0), (3, 6), (-1, 2)])
def test_score_rejects_out_of_range(likelihood: int, impact: int) -> None:
    with pytest.raises(ValueError):
        score(likelihood, impact)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1, RiskBand.LOW),
        (4, RiskBand.LOW),
        (5, RiskBand.MEDIUM),
        (9, RiskBand.MEDIUM),
        (10, RiskBand.HIGH),
        (14, RiskBand.HIGH),
        (15, RiskBand.CRITICAL),
        (25, RiskBand.CRITICAL),
    ],
)
def test_band_thresholds(value: int, expected: RiskBand) -> None:
    assert band(value) is expected


@pytest.mark.parametrize("value", [0, 26, 100])
def test_band_rejects_out_of_range(value: int) -> None:
    with pytest.raises(ValueError):
        band(value)


def test_every_band_has_a_distinct_color() -> None:
    colors = {band_color(b) for b in RiskBand}
    assert len(colors) == len(RiskBand)  # no two bands share a colour
    assert set(BAND_COLORS) == set(RiskBand)


def test_heatmap_is_5x5_and_consistent() -> None:
    cells = heatmap_cells()
    assert len(cells) == 25
    coords = {(c.likelihood, c.impact) for c in cells}
    assert len(coords) == 25  # every (likelihood, impact) pair exactly once
    for c in cells:
        assert c.score == c.likelihood * c.impact
        assert c.band is band(c.score)
        assert c.color == band_color(c.band)
    # ordering: first cell is top-left of the rendered grid (high impact, low likelihood)
    assert (cells[0].impact, cells[0].likelihood) == (5, 1)
    assert (cells[-1].impact, cells[-1].likelihood) == (1, 5)


def test_residual_reduction_never_negative() -> None:
    assert residual_reduction(20, 6) == 14
    assert residual_reduction(6, 20) == 0
    assert residual_reduction(9, 9) == 0
