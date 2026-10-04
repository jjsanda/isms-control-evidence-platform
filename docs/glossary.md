# Glossary

> Plain-language definitions of the information-security and audit terms used across this project — written for readers who are not IT specialists.

This glossary supports the [methodology](./methodology.md), [certification readiness](./certification-readiness.md) and [Statement of Applicability](./statement-of-applicability.md) guides, and the [README](../README.md). Terms are grouped loosely from the general to the specific.

| Term | Plain-language meaning |
| --- | --- |
| **ISMS** (Information Security Management System) | The organised set of policies, people, processes and technology a company uses to keep information secure and to keep improving that security over time. It is a *management system*, not a single tool. |
| **ISO/IEC 27001** | The leading international standard for an ISMS. An organisation can be independently audited and **certified** against the 2022 edition, which is what PaketPort is working towards. |
| **Annex A** | The catalogue of 93 security controls listed in ISO/IEC 27001:2022, grouped into four themes: Organizational (A.5), People (A.6), Physical (A.7) and Technological (A.8). |
| **Statement of Applicability (SoA)** | The master list that records, for every Annex A control, whether it applies to the organisation and why. It is usually the first document an auditor asks to see. |
| **NIS2** | An EU cybersecurity law (Directive 2022/2555) that places binding security and incident-reporting duties on "essential" operators. As an Austrian parcel-locker operator, PaketPort is in scope and treats it as a parallel driver alongside ISO 27001. |
| **Control** | A specific safeguard that reduces a risk — for example, requiring multi-factor login, encrypting data, or reviewing who has access. |
| **Control owner** | The named person accountable for a control working as intended and for keeping its evidence current. |
| **Implementation status** | How far a control has progressed: *planned*, *in progress*, *implemented*, or *operating* (implemented **and** backed by current evidence — the state an auditor wants to see). |
| **Maturity** | A 1–5 rating of how well-established and repeatable a control is, from 1 (ad-hoc/initial) to 5 (optimising). It answers "how good", not just "done or not". |
| **Risk** | The chance that something bad happens to information — such as a locker being tampered with or customer data leaking — combined with how much it would hurt. |
| **Inherent vs residual risk** | *Inherent* risk is the danger before any controls are applied; *residual* risk is what remains after the controls are in place. The gap between them shows how much the controls help. |
| **Likelihood** | How probable a risk is, rated 1 (rare) to 5 (almost certain) on this platform. |
| **Impact** | How damaging a risk would be if it happened, rated 1 (minor) to 5 (severe). Likelihood × impact gives the risk score (1–25). |
| **Risk treatment** | The decision on what to do about a risk. The four standard options are **mitigate** (add controls), **accept** (live with it), **transfer** (e.g. insure or outsource) or **avoid** (stop the risky activity). |
| **Risk acceptance** | A formal, documented decision by management to tolerate a remaining (residual) risk rather than spend more reducing it. |
| **Evidence** | Proof that a control is genuinely working — a configuration export, a test record, meeting minutes, a scan report and so on. |
| **Artifact** | The actual evidence file itself (a document, log or report) that a control points to. |
| **SHA-256 / hash** | A short "digital fingerprint" calculated from a file. If even one character changes, the fingerprint changes — so an auditor can confirm a piece of evidence has not been altered since it was collected. |
| **Audit status** | Where a control or evidence record sits in its review lifecycle: **draft → reviewed → accepted**, lapsing to **expired** once its review date passes. |
| **Review / due date** | The date by which a control or piece of evidence must be re-checked. Past that date it is *overdue*; within a warning window (30 days) it is *due soon*. |
| **CAPA** (corrective / preventive action) | An improvement task raised to fix a problem that occurred (*corrective*) or to stop one before it happens (*preventive*). Each has an owner and a due date. |
| **PDCA** (Plan-Do-Check-Act) | The repeating four-step improvement cycle that the whole ISMS runs on: plan it, do it, check it works, then act on what you learned. |
| **Security initiative / PoC** | A planned improvement project or **proof of concept** — a small trial to test whether a new security idea works before rolling it out fleet-wide. |
| **Awareness training** | Regular staff education on security basics (phishing, passwords, safe handling of customer data) so that people, not just technology, act as a line of defence. |
| **Joiner-mover-leaver** | The lifecycle of managing someone's access as they **join** the company, **move** to a new role, or **leave** — making sure access is granted, changed and, crucially, removed at the right time. |
