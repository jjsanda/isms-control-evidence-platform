# ADR 0003 — Server-rendered FastAPI dashboard with inline SVG

- **Status:** Accepted
- **Date:** 2026-07

## Context

The platform needs a dashboard to make the register legible (KPIs, control register, risk heatmap,
NIS2 readiness, evidence library). The choice is between a single-page application (React/Vite) and
a server-rendered app.

## Decision

Use **FastAPI + Jinja2**, server-rendered, with charts drawn as **inline SVG** built from pure
Python functions. A few lines of vanilla JavaScript provide table filtering and client-side quiz
scoring. No build step, no bundler, no JavaScript charting dependency.

## Consequences

- **Auditable UI.** "View source" on any page shows the exact numbers and their SVG — nothing is
  computed in an opaque client bundle. This suits a compliance tool.
- **No build toolchain.** No `node_modules`, no webpack/vite; the app runs with the Python stack
  alone and the pages are trivially screenshot-reproducible for the README.
- **Validation at boot.** The app loads and validates the whole register at startup and refuses to
  start on invalid data, so a broken register can never be served.
- **Trade-off.** No rich client interactivity (drag, live editing). The tool is intentionally
  read-only — editing happens through reviewed pull requests to the YAML (see ADR 0001).
