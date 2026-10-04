"""Presentation helpers shared by the templates (colours, labels, effective status).

Kept out of the routes so the same colour vocabulary is used everywhere and the templates stay
declarative. Registered as Jinja globals/filters in :func:`icep.web.app.create_app`.
"""

from __future__ import annotations

import html as _html
import re
from datetime import date

from markupsafe import Markup

from icep.domain import AuditStatus, ControlStatus, ReviewState
from icep.workflow import classify, effective_status
from icep.workflow.scoring import band_color

__all__ = [
    "STATUS_COLOR",
    "AUDIT_COLOR",
    "REVIEW_COLOR",
    "band_color",
    "status_color",
    "audit_color",
    "review_color",
    "label",
    "review_state_of",
    "effective_audit_of",
    "md_to_html",
]

STATUS_COLOR: dict[ControlStatus, str] = {
    ControlStatus.NOT_APPLICABLE: "#94a3b8",
    ControlStatus.PLANNED: "#f59e0b",
    ControlStatus.IN_PROGRESS: "#3b82f6",
    ControlStatus.IMPLEMENTED: "#10b981",
    ControlStatus.OPERATING: "#059669",
}

AUDIT_COLOR: dict[AuditStatus, str] = {
    AuditStatus.DRAFT: "#94a3b8",
    AuditStatus.REVIEWED: "#3b82f6",
    AuditStatus.ACCEPTED: "#059669",
    AuditStatus.EXPIRED: "#dc2626",
}

REVIEW_COLOR: dict[ReviewState, str] = {
    ReviewState.CURRENT: "#059669",
    ReviewState.DUE_SOON: "#f59e0b",
    ReviewState.OVERDUE: "#dc2626",
}


def status_color(value: ControlStatus) -> str:
    return STATUS_COLOR[value]


def audit_color(value: AuditStatus) -> str:
    return AUDIT_COLOR[value]


def review_color(value: ReviewState) -> str:
    return REVIEW_COLOR[value]


def label(value: object) -> str:
    """Turn an enum value like ``in_progress`` into a display label ``In Progress``."""
    text = value.value if hasattr(value, "value") else str(value)
    return str(text).replace("_", " ").title()


def review_state_of(due: date, today: date, warn_days: int = 30) -> ReviewState:
    return classify(due, today, warn_days)


def effective_audit_of(stored: AuditStatus, next_review: date, today: date) -> AuditStatus:
    return effective_status(stored, next_review, today)


_BOLD = re.compile(r"\*\*(.+?)\*\*")
_CODE = re.compile(r"`([^`]+?)`")


def _inline(text: str) -> str:
    escaped = _html.escape(text)
    escaped = _BOLD.sub(r"<strong>\1</strong>", escaped)
    return _CODE.sub(r"<code>\1</code>", escaped)


def md_to_html(markdown_text: str) -> Markup:
    """A tiny, safe Markdown renderer (headings, lists, blockquotes, bold, code, tables).

    Deliberately dependency-free so the web app needs nothing beyond the core stack. Input is
    HTML-escaped before any inline formatting, so it is safe to mark the result as trusted markup.
    """
    out: list[str] = []
    para: list[str] = []
    quote: list[str] = []
    table: list[str] = []
    in_list = False

    def flush_para() -> None:
        if para:
            out.append("<p>" + " ".join(_inline(line) for line in para) + "</p>")
            para.clear()

    def flush_quote() -> None:
        if quote:
            out.append("<blockquote>" + " ".join(_inline(line) for line in quote) + "</blockquote>")
            quote.clear()

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    def flush_block() -> None:
        flush_para()
        flush_quote()
        close_list()

    def flush_table() -> None:
        if not table:
            return
        header, *body = table
        # drop a Markdown separator row (---|:--) only when it is the first body row
        if body and set(body[0].replace("|", "").strip()) <= set("-: "):
            body = body[1:]
        cells = [[c.strip() for c in row.strip().strip("|").split("|")] for row in [header, *body]]
        out.append("<table class='data'><thead><tr>")
        out.extend(f"<th>{_inline(c)}</th>" for c in cells[0])
        out.append("</tr></thead><tbody>")
        for body_row in cells[1:]:
            out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in body_row) + "</tr>")
        out.append("</tbody></table>")
        table.clear()

    for raw in markdown_text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_block()
            table.append(stripped)
            continue
        flush_table()
        if not stripped:
            flush_block()
        elif stripped.startswith("### "):
            flush_block()
            out.append(f"<h4>{_inline(stripped[4:])}</h4>")
        elif stripped.startswith("## "):
            flush_block()
            out.append(f"<h3>{_inline(stripped[3:])}</h3>")
        elif stripped.startswith("# "):
            flush_block()
            out.append(f"<h2>{_inline(stripped[2:])}</h2>")
        elif stripped.startswith("> "):
            flush_para()
            close_list()
            quote.append(stripped[2:])
        elif stripped.startswith(("- ", "* ")):
            flush_para()
            flush_quote()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(stripped[2:])}</li>")
        else:
            flush_quote()
            close_list()
            para.append(stripped)

    flush_table()
    flush_block()
    return Markup("\n".join(out))
