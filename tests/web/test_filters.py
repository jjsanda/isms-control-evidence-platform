from __future__ import annotations

import pytest

from icep.web.filters import label, md_to_html

pytestmark = pytest.mark.web


def test_blockquote_renders_not_literal_gt() -> None:
    html = str(md_to_html("> a quoted summary line"))
    assert "<blockquote>" in html
    assert "&gt;" not in html  # the marker is consumed, never shown literally


def test_headings_lists_bold_and_code() -> None:
    html = str(md_to_html("## Section\n\n- one\n- two\n\n**bold** and `code`"))
    assert "<h3>Section</h3>" in html
    assert html.count("<li>") == 2
    assert "<strong>bold</strong>" in html
    assert "<code>code</code>" in html


def test_table_drops_separator_row_only() -> None:
    html = str(md_to_html("| A | B |\n| --- | --- |\n| 1 | 2 |"))
    assert "<table" in html
    assert html.count("<th>") == 2
    assert html.count("<td>") == 2  # exactly one data row; the --- separator is dropped
    assert "---" not in html


def test_escapes_html_input() -> None:
    html = str(md_to_html("<script>alert(1)</script>"))
    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_label_humanises_enum_values() -> None:
    assert label("in_progress") == "In Progress"
