# Contributing

This is a personal portfolio project, but it is built like a real one. If you want to run or extend
it, here is the workflow.

## Setup

```bash
make setup   # uv sync --dev --extra pdf, plus pre-commit hooks
```

Requires Python 3.12 and [`uv`](https://docs.astral.sh/uv/). Node.js is only needed to re-render the
Mermaid diagrams.

## The gate

Every change should pass the same gate CI runs:

```bash
make ci      # fmt-check + lint (ruff) + type (mypy --strict) + test-cov (90%) + security (pip-audit)
```

Individual targets: `make fmt`, `make lint`, `make type`, `make test`, `make test-cov`. Run
`make help` for the full list.

## Conventions

- **The register is data, not code.** Add or change controls/risks/evidence by editing the YAML under
  `data/` — the Pydantic schema (`extra="forbid"`) and the integrity check keep it honest. Run
  `make validate` to check schema + cross-references.
- **Determinism.** Never call `datetime.now()` directly — read time through `icep.clock`. Keep output
  sorted and JSON canonical, so `make seed-demo-data` stays byte-reproducible.
- **Types & style.** `mypy --strict` and ruff must pass; formatting is black. Prefer pure, testable
  functions (see `workflow/` and `collectors/`).
- **Commits.** Conventional Commits (`feat(...)`, `fix(...)`, `docs:`, `ci:`, `chore:`).
- **Diagrams & screenshots** are regenerated with `make diagrams` and `make screenshots` and the
  rendered outputs are committed.
