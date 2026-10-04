"""Risk scoring: a transparent 5x5 likelihood x impact model.

The whole scheme is intentionally simple and inspectable -- an auditor can re-derive any number by
hand. ``score`` multiplies the two 1-5 axes; ``band`` buckets the 1-25 result into four severity
bands; ``heatmap_cells`` produces the 5x5 grid the dashboard renders.

>>> score(4, 5)
20
>>> band(20)
<RiskBand.CRITICAL: 'critical'>
>>> band(6)
<RiskBand.MEDIUM: 'medium'>
"""

from __future__ import annotations

from dataclasses import dataclass

from icep.domain.enums import RiskBand

__all__ = [
    "MIN_AXIS",
    "MAX_AXIS",
    "score",
    "band",
    "band_color",
    "HeatCell",
    "heatmap_cells",
    "residual_reduction",
    "BAND_COLORS",
]

MIN_AXIS = 1
MAX_AXIS = 5

# Colourblind-considerate ramp. Colour is NEVER the only signal in the UI/audit pack -- the band
# label ("High", "Critical", ...) is always shown alongside it -- but the tones also separate in
# lightness so the grid stays legible in greyscale and to red-green colourblind readers.
BAND_COLORS: dict[RiskBand, str] = {
    RiskBand.LOW: "#2f9e44",
    RiskBand.MEDIUM: "#f59f00",
    RiskBand.HIGH: "#e8590c",
    RiskBand.CRITICAL: "#c92a2a",
}


def score(likelihood: int, impact: int) -> int:
    """Return the risk score ``likelihood * impact`` (both on a 1-5 scale, result 1-25).

    >>> score(1, 1)
    1
    >>> score(5, 5)
    25
    """
    for name, value in (("likelihood", likelihood), ("impact", impact)):
        if not MIN_AXIS <= value <= MAX_AXIS:
            raise ValueError(f"{name} must be within {MIN_AXIS}-{MAX_AXIS}, got {value}")
    return likelihood * impact


def band(value: int) -> RiskBand:
    """Bucket a 1-25 score into a severity band.

    Thresholds: Low <= 4, Medium 5-9, High 10-14, Critical >= 15.

    >>> [band(s) for s in (4, 5, 10, 15)]
    [<RiskBand.LOW: 'low'>, <RiskBand.MEDIUM: 'medium'>, <RiskBand.HIGH: 'high'>, <RiskBand.CRITICAL: 'critical'>]
    """
    if not 1 <= value <= MAX_AXIS * MAX_AXIS:
        raise ValueError(f"score must be within 1-25, got {value}")
    if value <= 4:
        return RiskBand.LOW
    if value <= 9:
        return RiskBand.MEDIUM
    if value <= 14:
        return RiskBand.HIGH
    return RiskBand.CRITICAL


def band_color(value_band: RiskBand) -> str:
    """Hex colour for a band (see :data:`BAND_COLORS`)."""
    return BAND_COLORS[value_band]


@dataclass(frozen=True)
class HeatCell:
    """One cell of the 5x5 risk heatmap."""

    likelihood: int
    impact: int
    score: int
    band: RiskBand
    color: str


def heatmap_cells() -> list[HeatCell]:
    """Return all 25 heatmap cells, ordered impact 5->1 (rows) then likelihood 1->5 (cols).

    >>> cells = heatmap_cells()
    >>> len(cells)
    25
    >>> cells[0].impact, cells[0].likelihood      # top-left = high impact, low likelihood
    (5, 1)
    """
    cells: list[HeatCell] = []
    for impact in range(MAX_AXIS, MIN_AXIS - 1, -1):
        for likelihood in range(MIN_AXIS, MAX_AXIS + 1):
            value = score(likelihood, impact)
            cell_band = band(value)
            cells.append(HeatCell(likelihood, impact, value, cell_band, band_color(cell_band)))
    return cells


def residual_reduction(inherent_score: int, residual_score: int) -> int:
    """How many score points the treatment removed (inherent - residual, never negative).

    >>> residual_reduction(20, 6)
    14
    """
    return max(0, inherent_score - residual_score)
