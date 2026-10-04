from __future__ import annotations

from pathlib import Path

import pytest

from icep.cli import main

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _pinned(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ICEP_NOW", "2026-07-07")


def test_validate_returns_zero_on_clean_register() -> None:
    assert main(["validate"]) == 0


def test_metrics_command() -> None:
    assert main(["metrics"]) == 0


def test_seed_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ICEP_EVIDENCE_DIR", str(tmp_path / "evidence"))
    assert main(["seed"]) == 0
    assert (tmp_path / "evidence" / "manifest.json").exists()


def test_export_markdown_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ICEP_EVIDENCE_DIR", str(tmp_path / "evidence"))
    out = tmp_path / "pack"
    assert main(["export", "--out", str(out), "--no-pdf"]) == 0
    assert (out / "markdown" / "00-executive-summary.md").exists()
    assert (out / "manifest.json").exists()


def test_validate_fails_on_missing_register(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ICEP_DATA_DIR", str(tmp_path))  # empty dir -> loader errors
    assert main(["validate"]) == 1
