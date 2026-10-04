"""Assemble the audit pack: a Markdown bundle, a single PDF, and a sealing manifest.

``make export-audit-pack`` calls :func:`build_audit_pack`. It validates the register, computes the
metrics, writes each section as Markdown, renders the same sections to a PDF (when the ``pdf`` extra
is present), and writes a manifest hashing every file. With the clock and ``SOURCE_DATE_EPOCH``
pinned, the whole pack is reproducible.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from icep import __version__
from icep.clock import Clock, default_clock
from icep.config import Settings, get_settings
from icep.export.manifest import build_manifest
from icep.export.sections import SECTION_ORDER, build_sections
from icep.integrity import sha256_file, sha256_text, write_json
from icep.metrics import compute_metrics
from icep.repository import IcepRepository
from icep.seed import read_manifest

__all__ = ["ExportError", "AuditPackResult", "build_audit_pack", "build_readme_pdf"]


class ExportError(Exception):
    """Raised when the audit pack cannot be built (e.g. the register has integrity errors)."""


@dataclass(frozen=True)
class AuditPackResult:
    out_dir: Path
    markdown_dir: Path
    pdf_path: Path | None
    manifest_path: Path
    file_count: int


def build_audit_pack(
    out_dir: Path | str,
    settings: Settings | None = None,
    clock: Clock | None = None,
    with_pdf: bool = True,
) -> AuditPackResult:
    """Build the full audit pack into ``out_dir`` and return the result summary."""
    settings = settings or get_settings()
    clock = clock or default_clock()
    today = clock.today()
    out_dir = Path(out_dir)

    repo = IcepRepository.load(settings)
    errors = repo.integrity_errors()
    if errors:
        joined = "\n  - ".join(f"{e.category}: {e.message}" for e in errors)
        raise ExportError(f"register has {len(errors)} integrity error(s):\n  - {joined}")

    metrics = compute_metrics(repo, today, settings.warn_days)
    evidence_hashes = read_manifest(settings)
    sections = build_sections(repo, metrics, evidence_hashes, today)

    markdown_dir = out_dir / "markdown"
    markdown_dir.mkdir(parents=True, exist_ok=True)
    pack_files: dict[str, str] = {}
    for slug, markdown in sorted(sections.items()):
        path = markdown_dir / f"{slug}.md"
        path.write_text(markdown, encoding="utf-8")
        pack_files[f"markdown/{slug}.md"] = sha256_text(markdown)

    pdf_path: Path | None = None
    if with_pdf:
        from icep.export.pdf import PDF_AVAILABLE, build_pdf

        if PDF_AVAILABLE:
            pdf_path = out_dir / "audit-pack.pdf"
            build_pdf(repo.organization.name, sections, SECTION_ORDER, today, pdf_path)
            pack_files["audit-pack.pdf"] = sha256_file(pdf_path)

    generated_at = clock.now().isoformat()
    manifest = build_manifest(
        pack_files, evidence_hashes, metrics, __version__, generated_at, today
    )
    manifest_path = out_dir / "manifest.json"
    write_json(manifest_path, manifest)

    return AuditPackResult(
        out_dir=out_dir,
        markdown_dir=markdown_dir,
        pdf_path=pdf_path,
        manifest_path=manifest_path,
        file_count=len(pack_files),
    )


def build_readme_pdf(
    readme_path: Path | str,
    out_path: Path | str,
    settings: Settings | None = None,
) -> Path:
    """Render the project README to a PDF (used by ``make readme-pdf``)."""
    from icep.export.pdf import PDF_AVAILABLE, markdown_to_pdf

    if not PDF_AVAILABLE:
        raise ExportError("PDF export needs the 'pdf' extra: uv sync --extra pdf")
    settings = settings or get_settings()
    readme_path = Path(readme_path)
    out_path = Path(out_path)
    base_url = str(readme_path.resolve().parent) + "/"
    markdown_to_pdf(readme_path.read_text(encoding="utf-8"), out_path, base_url=base_url)
    return out_path
