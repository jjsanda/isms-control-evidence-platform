# ADR 0001 — YAML register as the source of truth (compliance-as-code)

- **Status:** Accepted
- **Date:** 2026-07

## Context

An ISMS register (controls, risks, evidence, policies, NIS2 mapping) needs to be trustworthy,
reviewable, and auditable. The two obvious options are a database (e.g. SQLite/Postgres behind an
app) or plain structured files in version control.

## Decision

Store the entire register as **human-readable YAML under `data/`**, one file per control / risk /
evidence / policy, validated on load by **Pydantic v2** models with `extra="forbid"`. The
application and audit pack are read-only consumers of this data; there is no write path in the app.

## Consequences

- **Auditability by construction.** Every change to a control or risk is a Git diff with an author,
  a timestamp, and (via pull requests) a reviewer and approval — which is exactly the change-control
  and segregation-of-duties evidence an ISO 27001 auditor looks for.
- **Reviewable.** A compliance officer can read and comment on the register in a PR without running
  anything; the schema (`extra="forbid"`) rejects typos and drift immediately.
- **Portable and transparent.** No opaque binary database; the data is greppable, diff-able, and
  re-createable. Referential integrity (no dangling references, full SoA coverage) is enforced by a
  dedicated check rather than foreign keys.
- **Trade-off.** YAML does not scale to tens of thousands of concurrently-mutated rows. For a
  register of ~150 records that is read-mostly and changed through review, this is a non-issue; the
  transparency is worth far more than write throughput.
