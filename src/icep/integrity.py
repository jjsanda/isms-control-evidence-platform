"""Evidence integrity and deterministic serialisation helpers.

SHA-256 anchors every generated evidence artifact: the seed step records a hash per artifact in
``evidence/manifest.json`` and the loader can re-verify it, so a tampered or stale artifact is
detectable. :func:`canonical_json` is the one JSON writer used everywhere, so manifests and
metrics snapshots are byte-identical across machines and runs.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

__all__ = [
    "sha256_bytes",
    "sha256_text",
    "sha256_file",
    "canonical_json",
    "write_json",
]


def sha256_bytes(data: bytes) -> str:
    """Hex SHA-256 of raw bytes.

    >>> sha256_bytes(b"")
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
    """
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    """Hex SHA-256 of a string encoded as UTF-8."""
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    """Hex SHA-256 of a file's contents."""
    return sha256_bytes(Path(path).read_bytes())


def canonical_json(obj: Any) -> str:
    """Deterministic JSON text: sorted keys, UTF-8, 2-space indent, trailing newline."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def write_json(path: Path, obj: Any) -> None:
    """Write ``obj`` as canonical JSON to ``path`` (parent dirs must exist)."""
    Path(path).write_text(canonical_json(obj), encoding="utf-8")
