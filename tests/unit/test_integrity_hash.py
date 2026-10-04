from __future__ import annotations

import json
from pathlib import Path

import pytest

from icep.integrity import canonical_json, sha256_bytes, sha256_file, sha256_text, write_json

pytestmark = pytest.mark.unit


def test_sha256_of_empty() -> None:
    assert sha256_bytes(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_sha256_text_matches_bytes() -> None:
    assert sha256_text("hello") == sha256_bytes(b"hello")


def test_sha256_file(tmp_path: Path) -> None:
    path = tmp_path / "a.txt"
    path.write_text("hello", encoding="utf-8")
    assert sha256_file(path) == sha256_text("hello")


def test_sha256_detects_change(tmp_path: Path) -> None:
    path = tmp_path / "a.txt"
    path.write_text("hello", encoding="utf-8")
    before = sha256_file(path)
    path.write_text("hello!", encoding="utf-8")
    assert sha256_file(path) != before


def test_canonical_json_sorts_keys_and_ends_with_newline() -> None:
    text = canonical_json({"b": 1, "a": 2})
    assert text.index('"a"') < text.index('"b"')
    assert text.endswith("\n")


def test_write_json_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "out.json"
    write_json(path, {"z": 1, "a": [1, 2]})
    assert json.loads(path.read_text(encoding="utf-8")) == {"z": 1, "a": [1, 2]}
