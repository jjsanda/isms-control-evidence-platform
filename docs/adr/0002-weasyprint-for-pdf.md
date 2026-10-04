# ADR 0002 — WeasyPrint for the audit-pack PDF

- **Status:** Accepted
- **Date:** 2026-07

## Context

The audit pack must be shareable as a single, professional **PDF** as well as a Markdown bundle.
Options considered: `pandoc`/`wkhtmltopdf` (need system binaries, not installable without sudo in
the target environment), ReportLab (imperative, verbose), headless-Chromium print (heavy, harder to
make deterministic), and **WeasyPrint** (HTML/CSS → PDF, pure-Python with native pango/cairo libs
already present).

## Decision

Render the same Markdown sections that make up the bundle to HTML, apply a small print stylesheet,
and produce the PDF with **WeasyPrint**. Keep `weasyprint` + `markdown` in an optional **`pdf`**
extra so the core test gate stays dependency-free and fully offline.

## Consequences

- **Single source, two formats.** The Markdown bundle and the PDF are generated from the *same*
  section builders, so they can never disagree.
- **Reproducible.** WeasyPrint honours `SOURCE_DATE_EPOCH` for the PDF `/CreationDate`; with the
  clock and epoch pinned, the pack is byte-stable.
- **Offline.** No network, no external binary, no API key.
- **Trade-off.** WeasyPrint supports a CSS subset (no full flexbox/grid), so the print stylesheet is
  deliberately simple (tables and blocks). That is fine for an audit document and keeps it robust.
