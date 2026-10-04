"""Inline-SVG charts, built as pure strings -- no JavaScript, no charting dependency.

Server-rendered SVG keeps the dashboard auditable (view-source shows exactly the numbers), prints
cleanly into the audit pack, and works with the strictest content-security policy. Every function is
deterministic and unit-tested on the elements it emits.
"""

from __future__ import annotations

import html
import math
from dataclasses import dataclass

from icep.workflow import band
from icep.workflow.scoring import BAND_COLORS

__all__ = ["Segment", "donut", "hbars", "risk_heatmap"]


@dataclass(frozen=True)
class Segment:
    label: str
    value: int
    color: str


def _esc(text: str) -> str:
    return html.escape(text, quote=True)


def donut(segments: list[Segment], center_label: str, size: int = 180, thickness: int = 26) -> str:
    """A donut chart. Segments with value 0 are skipped; an all-zero input renders an empty ring."""
    total = sum(s.value for s in segments)
    radius = (size - thickness) / 2
    cx = cy = size / 2
    circumference = 2 * math.pi * radius
    parts = [
        f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" '
        f'aria-label="{_esc(center_label)}">',
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="#e2e8f0" '
        f'stroke-width="{thickness}"/>',
    ]
    offset = 0.0
    if total > 0:
        for seg in segments:
            if seg.value <= 0:
                continue
            length = circumference * seg.value / total
            parts.append(
                f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{seg.color}" '
                f'stroke-width="{thickness}" stroke-dasharray="{length:.2f} {circumference - length:.2f}" '
                f'stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>'
            )
            offset += length
    parts.append(
        f'<text x="{cx}" y="{cy - 4}" text-anchor="middle" font-size="26" font-weight="700" '
        f'fill="#1e293b">{_esc(str(total))}</text>'
        f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="11" fill="#64748b">'
        f"{_esc(center_label)}</text>"
    )
    parts.append("</svg>")
    return "".join(parts)


def hbars(rows: list[tuple[str, float, str]], width: int = 320, row_h: int = 26) -> str:
    """Horizontal percentage bars: each row is (label, pct 0-100, color). Labels left, value right."""
    label_w = 150
    bar_w = width - label_w - 44
    height = row_h * len(rows) + 6
    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">']
    for i, (label, pct, color) in enumerate(rows):
        y = i * row_h + 4
        filled = max(0.0, min(100.0, pct)) / 100.0 * bar_w
        parts.append(
            f'<text x="0" y="{y + row_h / 2 + 4}" font-size="11" fill="#334155">{_esc(label)}</text>'
            f'<rect x="{label_w}" y="{y + 4}" width="{bar_w}" height="{row_h - 12}" rx="3" '
            f'fill="#e2e8f0"/>'
            f'<rect x="{label_w}" y="{y + 4}" width="{filled:.1f}" height="{row_h - 12}" rx="3" '
            f'fill="{color}"/>'
            f'<text x="{width}" y="{y + row_h / 2 + 4}" text-anchor="end" font-size="11" '
            f'fill="#475569">{pct:.0f}%</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def risk_heatmap(counts: dict[tuple[int, int], int], cell: int = 46) -> str:
    """A 5x5 likelihood x impact heatmap; ``counts[(likelihood, impact)]`` overlays a risk count."""
    pad = 30
    size = cell * 5
    width = size + pad + 12
    height = size + pad + 12
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
        'aria-label="Residual risk heatmap">'
    ]
    for impact in range(5, 0, -1):
        for likelihood in range(1, 6):
            x = pad + (likelihood - 1) * cell
            y = pad + (5 - impact) * cell
            colour = BAND_COLORS[band(likelihood * impact)]
            count = counts.get((likelihood, impact), 0)
            parts.append(
                f'<rect x="{x}" y="{y}" width="{cell - 2}" height="{cell - 2}" rx="3" '
                f'fill="{colour}" fill-opacity="0.30" stroke="#ffffff"/>'
            )
            if count:
                parts.append(
                    f'<circle cx="{x + cell / 2 - 1}" cy="{y + cell / 2 - 1}" r="13" fill="{colour}"/>'
                    f'<text x="{x + cell / 2 - 1}" y="{y + cell / 2 + 3}" text-anchor="middle" '
                    f'font-size="13" font-weight="700" fill="#ffffff">{count}</text>'
                )
    # axes
    parts.append(
        f'<text x="{pad + size / 2}" y="{height - 2}" text-anchor="middle" font-size="11" '
        f'fill="#64748b">Likelihood &#8594;</text>'
        f'<text x="10" y="{pad + size / 2}" text-anchor="middle" font-size="11" fill="#64748b" '
        f'transform="rotate(-90 10 {pad + size / 2})">Impact &#8594;</text>'
    )
    parts.append("</svg>")
    return "".join(parts)
