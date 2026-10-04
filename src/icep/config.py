"""Runtime configuration, overridable via ``ICEP_``-prefixed environment variables."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "get_settings"]

# repo root = .../isms-control-evidence-platform (this file is src/icep/config.py)
_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Where the register and generated evidence live, plus review-window policy.

    Defaults are repo-relative so the ``make`` flow works from a clean checkout; every value
    can be overridden (e.g. ``ICEP_DATA_DIR=/some/where``) for tests or alternate deployments.
    """

    model_config = SettingsConfigDict(env_prefix="ICEP_", extra="ignore")

    data_dir: Path = Field(
        default=_REPO_ROOT / "data",
        description="Root directory of the hand-authored YAML register.",
    )
    evidence_dir: Path = Field(
        default=_REPO_ROOT / "evidence",
        description="Directory of collector-generated evidence artifacts and manifest.",
    )
    warn_days: int = Field(
        default=30,
        ge=1,
        le=365,
        description="Lead time (days) before a review due date at which it is flagged DUE_SOON.",
    )
    organization: str = Field(
        default="PaketPort Systems GmbH",
        description="Display name of the ISMS scope owner.",
    )


def get_settings() -> Settings:
    """Load settings from the environment (a thin, mockable indirection)."""
    return Settings()
