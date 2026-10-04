"""Audit-pack export: sections build, manifest hashes match, and the bundle is reproducible."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from icep.clock import FrozenClock
from icep.config import Settings
from icep.export import build_audit_pack
from icep.export.sections import SECTION_ORDER
from icep.integrity import sha256_file
from icep.seed import seed

pytestmark = pytest.mark.export

CLOCK = FrozenClock.at("2026-07-07")


@pytest.fixture
def seeded_settings(tmp_path: Path) -> Settings:
    settings = Settings(evidence_dir=tmp_path / "evidence")
    seed(settings, CLOCK)  # generates the evidence artifacts + manifest the pack references
    return settings


def test_pack_contains_every_section(seeded_settings: Settings, tmp_path: Path) -> None:
    result = build_audit_pack(
        tmp_path / "pack", settings=seeded_settings, clock=CLOCK, with_pdf=False
    )
    for slug, _title in SECTION_ORDER:
        assert (result.markdown_dir / f"{slug}.md").exists()
    assert (result.markdown_dir / "README.md").exists()
    text = (result.markdown_dir / "00-executive-summary.md").read_text(encoding="utf-8")
    assert "PaketPort Systems GmbH" in text


def test_manifest_hashes_match_files(seeded_settings: Settings, tmp_path: Path) -> None:
    result = build_audit_pack(
        tmp_path / "pack", settings=seeded_settings, clock=CLOCK, with_pdf=False
    )
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["files"], "manifest should list the pack files"
    for rel, digest in manifest["files"].items():
        assert sha256_file(result.out_dir / rel) == digest


def test_markdown_bundle_is_deterministic(seeded_settings: Settings, tmp_path: Path) -> None:
    first = build_audit_pack(tmp_path / "p1", settings=seeded_settings, clock=CLOCK, with_pdf=False)
    second = build_audit_pack(
        tmp_path / "p2", settings=seeded_settings, clock=CLOCK, with_pdf=False
    )
    for slug, _title in SECTION_ORDER:
        a = (first.markdown_dir / f"{slug}.md").read_text(encoding="utf-8")
        b = (second.markdown_dir / f"{slug}.md").read_text(encoding="utf-8")
        assert a == b


def test_pdf_smoke(seeded_settings: Settings, tmp_path: Path) -> None:
    pytest.importorskip("weasyprint")
    result = build_audit_pack(
        tmp_path / "pack", settings=seeded_settings, clock=CLOCK, with_pdf=True
    )
    assert result.pdf_path is not None
    assert result.pdf_path.exists()
    assert result.pdf_path.read_bytes()[:5] == b"%PDF-"
