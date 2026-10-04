"""Loader failure modes and the duplicate-id integrity check (over a copy of the real register)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from icep.config import Settings
from icep.loader import LoaderError, load_register
from icep.repository import IcepRepository

pytestmark = pytest.mark.integrity


@pytest.fixture
def data_copy(tmp_path: Path) -> Path:
    destination = tmp_path / "data"
    shutil.copytree(Settings().data_dir, destination)
    return destination


def test_empty_required_file_raises_loader_error(data_copy: Path) -> None:
    (data_copy / "organization.yaml").write_text("", encoding="utf-8")
    with pytest.raises(LoaderError) as excinfo:
        load_register(Settings(data_dir=data_copy))
    assert "organization.yaml" in str(excinfo.value)


def test_malformed_yaml_raises_loader_error(data_copy: Path) -> None:
    (data_copy / "organization.yaml").write_text("name: [unterminated\n", encoding="utf-8")
    with pytest.raises(LoaderError):
        load_register(Settings(data_dir=data_copy))


def test_duplicate_control_id_is_flagged(data_copy: Path) -> None:
    controls = sorted((data_copy / "controls").glob("*.yaml"))
    (data_copy / "controls" / "zz-duplicate.yaml").write_text(
        controls[0].read_text(encoding="utf-8"), encoding="utf-8"
    )
    repo = IcepRepository.load(Settings(data_dir=data_copy))
    assert any(issue.category == "duplicate" for issue in repo.integrity_errors())
