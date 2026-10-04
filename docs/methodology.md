# ISMS methodology

> How PaketPort Systems GmbH runs its information security management system as a continual **Plan-Do-Check-Act** cycle, aligned to ISO/IEC 27001:2022 clauses 4–10 and its Annex A controls — and how this platform implements each stage as version-controlled data.

An **ISMS** is not a one-off project; it is a management system that is planned, operated, measured and improved on a repeating cycle. PaketPort structures that cycle as **Plan-Do-Check-Act (PDCA)**, the model underlying ISO/IEC 27001. Every artifact in this repository — the control register, the risk register, the evidence index and the audit pack — is a stage of that cycle made inspectable. See the [glossary](./glossary.md) for any unfamiliar term, and the [README](../README.md) for the demo flow.

## PDCA mapped to ISO/IEC 27001:2022 clauses 4–10

The management-system clauses of the standard divide neatly into the four PDCA stages:

| PDCA | ISO/IEC 27001:2022 clause | What happens at PaketPort |
| --- | --- | --- |
| **Plan** | 4 Context · 5 Leadership · 6 Planning · 7 Support | Define the ISMS scope and interested parties; the Managing Director sets the security policy and objectives; assess and plan treatment of risks; provide people, competence, awareness and documented information. |
| **Do** | 8 Operation | Execute the risk-treatment plan and operate the Annex A controls that protect the lockers, the cloud backend and customers' personal data. |
| **Check** | 9 Performance evaluation | Monitor and measure the controls (KPIs), run internal audits, and hold management reviews. |
| **Act** | 10 Improvement | Handle nonconformities, drive corrective and preventive actions (CAPA), and feed lessons back into the next Plan. |

## The four Annex A themes

The controls operated in the **Do** stage come from Annex A of ISO/IEC 27001:2022, which groups its 93 controls into four themes. PaketPort treats **all 93 as applicable** (see the [Statement of Applicability guide](./statement-of-applicability.md)):

| Theme | Clause | PaketPort focus |
| --- | --- | --- |
| **Organizational** | A.5 | Policies, roles, supplier and cloud-service security, incident management, continuity. |
| **People** | A.6 | Screening, awareness training, and the joiner-mover-leaver access lifecycle. |
| **Physical** | A.7 | Locker enclosure security, siting, tamper detection, and equipment protection. |
| **Technological** | A.8 | Access control, cryptography, logging, secure development, and network security across the Linux edge and cloud. |

## How this platform implements each stage

**Plan — the register as version-controlled YAML.** Context, scope, controls, risks and objectives are hand-authored YAML validated by Pydantic schemas. Because the register lives in Git, every change is diff-able, attributable and reviewable in a pull request — an auditable trail that a spreadsheet cannot give. `data/organization.yaml` captures the scope, boundary and policy statement; the control and risk registers capture the rest.

**Plan — risk methodology.** Risks are scored on a transparent **5×5 likelihood × impact** model. The product (1–25) is bucketed into four bands: **Low ≤ 4, Medium 5–9, High 10–14, Critical ≥ 15**. Each risk carries an **inherent** score (before controls) and a **residual** score (after controls), so treatment effectiveness is visible as the reduction between them. Residual scores describe the planned end-state once the documented treatment is fully operating; where a control is still in progress (for example centralised logging under INIT-001), the linked improvement action tracks it to completion. Treatment follows the four risk-treatment options set out in ISO/IEC 27001:2022 clause 6.1.3 — **mitigate, accept, transfer, avoid** — and any residual risk in the High/Critical bands requires an explicit management acceptance decision. Today the register holds **13 risks**: their inherent profile is dominated by the Critical and High bands, but treatment pulls every residual risk down to Medium or Low — leaving **no residual High or Critical risks** (12 Medium, 1 Low), of which **2 are formally accepted** by management.

**Do — the audit review workflow.** Each control and evidence record moves through a state machine — **draft → reviewed → accepted**, lapsing to **expired**. The transitions enforce **segregation of duties**: nothing jumps straight from *draft* to *accepted*; an item must be *reviewed* by someone other than its author first. Expiry is **time-driven** — an accepted control whose next-review date has passed is reported as *expired* without anyone editing the record — which is why the platform currently surfaces **3 controls overdue for review** and **1 expired evidence artifact**.

**Do — the evidence model.** Evidence records are **hash-anchored** pointers to artifacts: each carries a **SHA-256** digest recorded in a manifest, so an auditor can confirm the file has not changed since it was collected. Many artifacts are produced by **collectors** — small, deterministic programs that read a real Linux input (an `sshd_config`, `auditd` rules, a vulnerability-scan report) and render a findings report. Every artifact has a **validity window** (`valid_from` / `valid_until`); once past its end date it counts as expired and prompts recollection. The index holds **18 artifacts** today.

**Check — measurement and audit.** KPIs are **computed from the register as of a pinned date**, never stored, so the numbers always reflect the current data (`evidence/metrics.json`). Headline figures include **25 of 93 controls documented in depth**, **76% of documented controls implemented or operating**, and **NIS2 readiness of 82.6%** (averaged across the Art. 21(2) measures and the Art. 20 duty). Internal audit findings and evidence reviews feed the improvement backlog.

**Act — continual improvement.** Findings become **CAPA** items (corrective/preventive actions) with an owner, a source and a due date; there are **5 open improvement actions** now. These, together with KPIs and the risk picture, are the inputs to the **management review**, which closes the loop by re-planning objectives — restarting the PDCA cycle. How this feeds an external certification audit is covered in [certification readiness](./certification-readiness.md).
