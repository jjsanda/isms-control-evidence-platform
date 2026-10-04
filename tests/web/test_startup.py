from __future__ import annotations

from pathlib import Path

import pytest

from icep.loader import LoaderError
from icep.web.app import create_app

pytestmark = pytest.mark.web


def test_app_refuses_to_boot_on_invalid_register(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Point the data dir at an empty directory: the loader can't find the register and raises,
    # so the app never starts with half-valid data.
    monkeypatch.setenv("ICEP_DATA_DIR", str(tmp_path))
    with pytest.raises(LoaderError):
        create_app()
