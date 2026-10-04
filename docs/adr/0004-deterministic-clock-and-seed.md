# ADR 0004 — Deterministic clock and reproducible seed

- **Status:** Accepted
- **Date:** 2026-07

## Context

Evidence artifacts, the metrics snapshot, and the audit pack all depend on "today" (review dates,
expiry, hashes). If generation is not reproducible, the committed evidence and the audit pack churn
on every run and their hashes become meaningless.

## Decision

Read "now" through a single injectable **`Clock`**. The default clock resolves `ICEP_NOW` (an ISO
date) then `SOURCE_DATE_EPOCH` (unix seconds) then the real system clock. No code calls
`datetime.now()` directly. All iteration is sorted and all JSON is written canonically (sorted keys,
trailing newline). The `make` targets pin `ICEP_NOW=2026-07-07`.

## Consequences

- **Byte-reproducible.** Re-running `make seed-demo-data` produces identical bytes; CI asserts this
  with `git diff --exit-code evidence/`. The audit-pack Markdown is likewise deterministic.
- **Meaningful hashes.** Because artifacts are stable, their SHA-256 manifest entries are a real
  integrity anchor, not noise.
- **Testable time.** Tests inject a `FrozenClock`, so date-driven logic (overdue reviews, expiry,
  auto-expiring audit status) is exercised against a fixed "today" without mocking.
- **Trade-off.** A little discipline (never call the wall clock directly) is required throughout;
  the `Clock` protocol makes that easy to enforce and review.
