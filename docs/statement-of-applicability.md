# Statement of Applicability (guide)

> A short narrative guide to PaketPort's Statement of Applicability — what it is, why an auditor reaches for it first, the stance PaketPort takes, and where to read it in this repository. This is the guide, not the data.

## What a Statement of Applicability is

The **Statement of Applicability (SoA)** is the master list that records, for **every** control in Annex A of ISO/IEC 27001:2022, whether it applies to the organisation and the reason for that decision. It is the hinge between the *risk assessment* (what could go wrong) and the *controls* (what we do about it) — the place where an organisation declares which safeguards it has chosen and justifies any it has left out. See the [glossary](./glossary.md) for supporting terms and [methodology](./methodology.md) for how it fits the wider cycle.

## Why it is the auditor's first artifact

A certification auditor typically asks for the SoA before anything else, because it defines the **scope of the audit** in one document: it tells them exactly which controls to expect evidence for, and forces the organisation to make a defensible, on-the-record decision about each one — no control can be silently ignored. From there, the auditor navigates outward to the control register, the risks and the evidence.

## PaketPort's stance

PaketPort treats **all 93 Annex A:2022 controls as applicable** — none are excluded. For a NIS2 essential entity running internet-facing Linux lockers and a cloud backend full of customers' personal data, that breadth is a deliberate, defensible stance. Each control carries an **inclusion reason** from a fixed vocabulary:

- **risk** — required to treat an identified risk;
- **legal** — required by law or regulation (e.g. NIS2, GDPR);
- **contractual** — required by a customer or carrier agreement;
- **best_practice** — industry-standard good practice;
- **business** — needed for a business or operational objective.

Depth varies by design: **25 controls are documented with full records** — owner, implementation status, maturity, linked policies and hash-anchored evidence — while the remaining 68 are **covered at SoA level** (an applicability decision and justification, without a full control record yet). This is the representative-subset approach explained in [certification readiness](./certification-readiness.md).

## The four themes and the 2022 controls

Annex A:2022 groups its 93 controls into four themes — **Organizational (A.5)**, **People (A.6)**, **Physical (A.7)** and **Technological (A.8)** — and introduces **11 controls new in the 2022 edition**, several of which map directly onto PaketPort's risk profile: threat intelligence (A.5.7), cloud-service security (A.5.23), ICT readiness for business continuity (A.5.30), physical security monitoring (A.7.4), configuration management (A.8.9), information deletion (A.8.10), data masking (A.8.11), data-leakage prevention (A.8.12), monitoring activities (A.8.16), web filtering (A.8.23) and secure coding (A.8.28).

## How to read the SoA in this repository

- **Source data:** [`../data/statement_of_applicability.yaml`](../data/statement_of_applicability.yaml) — the authoritative list, one entry per control with its applicability flag, inclusion reason and justification.
- **Dashboard:** the `/soa` page of the ISMS web app renders the same data with filtering and links through to each control.
- **Audit pack:** the *Statement of Applicability* section is the first document after the executive summary, exported alongside the rest of the pack (see the [README](../README.md) quickstart).
