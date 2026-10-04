from __future__ import annotations

import pytest

from icep.web.charts import Segment, donut, hbars, risk_heatmap

pytestmark = pytest.mark.web


def test_donut_totals_and_segments() -> None:
    svg = donut([Segment("a", 3, "#ff0000"), Segment("b", 1, "#00ff00")], "controls")
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert ">4<" in svg  # total in the centre
    assert svg.count("stroke-dasharray") == 2  # one arc per non-zero segment


def test_donut_handles_all_zero() -> None:
    svg = donut([Segment("a", 0, "#ff0000")], "controls")
    assert ">0<" in svg
    assert "stroke-dasharray" not in svg  # nothing to draw, but still valid


def test_hbars_one_track_and_fill_per_row() -> None:
    svg = hbars([("a", 50.0, "#ff0000"), ("b", 100.0, "#00ff00")])
    assert svg.count("<rect") == 4  # a track + a fill per row
    assert "50%" in svg and "100%" in svg


def test_heatmap_is_25_cells_with_counts() -> None:
    svg = risk_heatmap({(2, 4): 3, (1, 1): 1})
    assert svg.count("<rect") == 25
    assert ">3<" in svg  # the overlaid count
    assert ">1<" in svg
