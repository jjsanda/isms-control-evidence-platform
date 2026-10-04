# Executive summary

**PaketPort Systems GmbH** — Information Security Management System audit pack, generated 2026-07-07.

## Scope

The ISMS covers the design, operation, monitoring and continual improvement of PaketPort Systems GmbH's parcel-locker service: the internet-facing Linux edge devices (street-sited lockers) and their fleet-management plane, the cloud-hosted backend (customer application, parcel-routing engine and carrier-API integrations), the supporting corporate IT and identity services, and the people and processes that operate them. It encompasses the end-to-end processing of customers' personal data — names, contact details, delivery addresses and parcel-event records — from locker to backend to carrier, and the related NIS2 and GDPR obligations of an Austrian essential entity.

*Boundary:* In scope: all production locker edge devices and the OTA/fleet-management plane; the cloud backend, its data stores and APIs; the CI/CD pipeline and source repositories for the customer app and locker firmware; corporate endpoints, identity and email; and the Vienna head office, security operations centre and provisioning depot. Out of scope: the public cloud provider's underlying physical infrastructure (addressed under the shared-responsibility model and the provider's own certifications), carrier partners' internal networks and systems, and the public street locations where lockers stand beyond the locker enclosure itself. Interfaces to these out-of-scope parties are governed by supplier agreements and monitored as third-party risk.

## Posture at a glance

- **Certification target:** ISO/IEC 27001:2022
- **Annex A controls:** 25 fully documented of 93 (93 applicable in the SoA)
- **Implementation:** 19/25 documented controls implemented or operating (76.0%)
- **NIS2 readiness:** 82.6% across the Art. 21(2) measures and the Art. 20 duty
- **Risks:** 13 tracked, 0 high/critical unaccepted, 2 formally accepted
- **Improvement actions:** 5 open (0 overdue)
- **Reviews:** 3 controls overdue for review, 1 evidence artifact expired

## Management commitment

PaketPort's management, led by the Managing Director, is committed to protecting the confidentiality, integrity and availability of the information entrusted to it by customers, carriers and staff. We establish, operate and continually improve an information security management system aligned to ISO/IEC 27001:2022 and to our duties as a NIS2 essential entity; we set and review measurable security objectives, provide the resources to meet them, comply with applicable legal and contractual requirements including the GDPR, and require every employee and contractor to understand and uphold this commitment. Security responsibilities are assigned, risks are managed to defined criteria, and this policy is reviewed at least annually.

*ISMS owner:* Alex Rossi (Information Security Officer / ISMS Manager). *Management representative:* Dana Weber (Managing Director).
