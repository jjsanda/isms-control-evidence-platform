# Evidence index

18 evidence artifacts. Each SHA-256 anchors the artifact to the audit manifest so tampering is detectable.

| Evidence | Title | Type | Controls | Collected by | Valid until | Status | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EV-001 | sshd hardening check (locker fleet) | config_export | A.8.9 | Sara Berger | 2026-12-01 | valid | `a909c40ab7c3` |
| EV-002 | auditd rule coverage (edge + backend) | config_export | A.8.15, A.8.16 | Milan Novak | 2026-12-01 | valid | `929bac696a5b` |
| EV-003 | Vulnerability scan summary (container images) | scan_report | A.8.8 | Tomas Horak | 2026-09-15 | valid | `18dce233a204` |
| EV-004 | Backup restore test record | backup_test | A.8.13, A.5.30 | Sara Berger | 2026-11-20 | valid | `c3f973a8111c` |
| EV-005 | Quarterly access review (joiners/movers/leavers) | access_review | A.5.15, A.8.2, A.8.5 | Alex Rossi | 2026-09-30 | valid | `fb6d8d8d7ede` |
| EV-006 | Asset inventory export (CMDB) | config_export | A.5.9 | Sara Berger | 2027-05-01 | valid | `2586b57413fd` |
| EV-007 | Supplier security register | attestation | A.5.19 | Jan Fischer | 2026-06-30 | expired | `792c62e9e7fc` |
| EV-008 | SBOM & third-party component assessment | scan_report | A.5.21 | Jan Fischer | 2026-10-01 | valid | `4f3fd79c7a7c` |
| EV-009 | Cloud tenant hardening baseline | config_export | A.5.23 | Milan Novak | 2027-03-05 | valid | `b4d72ad17a34` |
| EV-010 | Incident response plan (approved) | policy_doc | A.5.24 | Alex Rossi | 2027-03-10 | valid | `73ac26d2f351` |
| EV-011 | Incident triage log (sample) | log_export | A.5.25, A.6.8 | Tomas Horak | 2026-12-01 | valid | `91b2c1ed225e` |
| EV-012 | Awareness training completion report | training_record | A.6.3 | Petra Klein | 2026-12-05 | valid | `bfa7f18e289c` |
| EV-013 | Locker enclosure physical security review | screenshot | A.7.1 | Karl Mayer | 2027-02-05 | valid | `f282ed6c6144` |
| EV-014 | Tamper-detection monitoring export | log_export | A.7.4 | Karl Mayer | 2026-11-10 | valid | `eae33992721c` |
| EV-015 | Management review minutes | attestation | A.5.1 | Dana Weber | 2027-03-01 | valid | `f66667d1d241` |
| EV-016 | Threat intelligence briefing | attestation | A.5.7 | Tomas Horak | 2026-07-25 | valid | `782be7189f0b` |
| EV-017 | Internal ISMS audit report | test_record | A.5.35 | Alex Rossi | 2027-02-01 | valid | `68207cf0558d` |
| EV-018 | Network segmentation & TLS configuration export | config_export | A.8.20, A.8.24 | Milan Novak | 2027-03-08 | valid | `73ef2741ce59` |
