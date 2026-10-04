# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project adheres
to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **ISMS register (compliance-as-code).** Pydantic-validated YAML for the fictional PaketPort Systems
  GmbH: the full ISO/IEC 27001:2022 Annex A catalog (93 controls) and Statement of Applicability, 25
  fully documented controls, 13 risks, 18 evidence records, 8 policies, the NIS2 Art. 21(2)/23
  mapping, 6 improvement actions, a security initiative, and awareness training + quiz.
- **Repository & integrity engine.** In-memory repository with cross-reference resolution and a
  structural integrity check (no dangling references, full SoA coverage, every NIS2 area mapped).
- **Risk & audit workflow.** 5×5 inherent/residual risk scoring with bands, the
  `draft → reviewed → accepted → expired` audit state machine with time-driven expiry, and due-date
  classification.
- **Linux evidence collectors.** SSH hardening, auditd coverage, Trivy vuln summary, backup
  restore-test, and joiner/mover/leaver access review — turned into hash-anchored evidence by a
  byte-deterministic seed.
- **CLI.** `icep validate | seed | serve | export | metrics`.
- **Audit pack export.** Deterministic Markdown bundle + WeasyPrint PDF + SHA-256 manifest.
- **Dashboard.** Server-rendered FastAPI + Jinja2 with inline-SVG charts (status donut, NIS2 bars,
  5×5 risk heatmap), control/risk/evidence detail, the SoA, NIS2 mapping, and a client-scored quiz.
- **Docs.** Methodology, glossary, certification-readiness and SoA guides, four ADRs, six rendered
  Mermaid diagrams, dashboard screenshots, and a committed sample audit pack.
- **Quality gate.** ruff, black, `mypy --strict`, pytest with a 90% coverage gate, `pip-audit`, and
  GitHub Actions CI + CodeQL. Runs fully offline with no API key.

[Unreleased]: https://github.com/jjsanda/isms-control-evidence-platform
