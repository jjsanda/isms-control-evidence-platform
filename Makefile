UV ?= uv

# Pin "now" and the PDF creation timestamp so `seed`, `export` and the tests are byte-reproducible.
# 2026-07-07T00:00:00Z. Override on the command line if you want to simulate a different audit date.
ICEP_NOW ?= 2026-07-07
SOURCE_DATE_EPOCH ?= 1783382400

.DEFAULT_GOAL := help
.PHONY: help setup fmt fmt-check lint type test test-cov security ci \
        validate seed-demo-data run export-audit-pack metrics \
        diagrams screenshots readme-pdf clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

## ---------- Setup & quality gate ----------

setup: ## Install dependencies (dev + pdf extra) and pre-commit hooks
	$(UV) sync --dev --extra pdf
	$(UV) run pre-commit install || true

fmt: ## Auto-fix lint issues and format the code
	$(UV) run ruff check --fix .
	$(UV) run black .

fmt-check: ## Check formatting without modifying files
	$(UV) run black --check --diff .

lint: ## Lint with ruff
	$(UV) run ruff check .

type: ## Strict type-check with mypy
	$(UV) run mypy

test: ## Run the offline test suite
	$(UV) run pytest -q

test-cov: ## Run tests with coverage and enforce the 90% gate
	$(UV) run pytest --cov=icep --cov-report=term-missing --cov-fail-under=90

security: ## Audit Python dependencies for known vulnerabilities
	$(UV) run pip-audit || true

ci: fmt-check lint type test-cov security ## Run the full local gate (mirrors GitHub Actions)

## ---------- ISMS demo flow ----------

validate: ## Validate the whole YAML register against the schema and cross-references
	$(UV) run icep validate

seed-demo-data: ## Generate evidence artifacts + hashes + metrics from committed samples (deterministic)
	ICEP_NOW=$(ICEP_NOW) $(UV) run icep seed

run: ## Serve the ISMS dashboard at http://127.0.0.1:8000
	$(UV) run icep serve --host 127.0.0.1 --port 8000

export-audit-pack: ## Build the audit pack (Markdown bundle + single PDF + manifest) into dist/
	ICEP_NOW=$(ICEP_NOW) SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) \
		$(UV) run --extra pdf icep export --out dist/audit-pack

metrics: ## Print the current ISMS KPI snapshot
	$(UV) run icep metrics

## ---------- Docs & media (build-time; need node/network) ----------

diagrams: ## Render the Mermaid diagrams to SVG + PNG
	./scripts/render_diagrams.sh

screenshots: ## Capture dashboard PNGs from a freshly seeded, running app
	./scripts/serve_and_shoot.sh

readme-pdf: ## Render README.md to README.pdf via WeasyPrint
	ICEP_NOW=$(ICEP_NOW) SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) \
		$(UV) run --extra pdf icep export --readme-pdf README.pdf

clean: ## Remove caches, coverage and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage coverage.xml dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
