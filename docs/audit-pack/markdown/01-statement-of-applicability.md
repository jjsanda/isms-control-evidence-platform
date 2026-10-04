# Statement of Applicability (ISO/IEC 27001:2022 Annex A)

All 93 Annex A controls, with the applicability decision and its justification. 'Documented' marks controls with a full control record in this register.

| Control | Title | Applicable | Reason | Documented | Justification |
| --- | --- | --- | --- | --- | --- |
| A.5.1 | Policies for information security | Yes | risk | Yes | Top-level security policy sets PaketPort's direction and is required by ISO 27001 clause 5.2. |
| A.5.2 | Information security roles and responsibilities | Yes | best_practice | — | Clear security roles across locker ops, cloud and admin staff prevent accountability gaps. |
| A.5.3 | Segregation of duties | Yes | risk | — | Separating duties like firmware deploy from approval limits fraud and error in a small team. |
| A.5.4 | Management responsibilities | Yes | best_practice | — | Management actively requires staff to apply security controls for lockers and the backend. |
| A.5.5 | Contact with authorities | Yes | legal | — | As a NIS2 operator PaketPort must reach CERT.at, the DSB and police fast during incidents. |
| A.5.6 | Contact with special interest groups | Yes | best_practice | — | Membership in security forums keeps PaketPort current on threats to lockers and logistics IT. |
| A.5.7 | Threat intelligence | Yes | risk | Yes | Internet-facing lockers are constantly scanned, so threat intel guides defence of edge and APIs. |
| A.5.8 | Information security in project management | Yes | best_practice | — | New locker rollouts and app features carry security requirements from design to go-live. |
| A.5.9 | Inventory of information and other associated assets | Yes | risk | Yes | A live inventory of every locker, cloud service and PII store is vital for a dispersed estate. |
| A.5.10 | Acceptable use of information and other associated assets | Yes | best_practice | — | Staff and contractors get clear rules for using PaketPort systems, data and locker tooling. |
| A.5.11 | Return of assets | Yes | best_practice | — | Leavers and field technicians must return laptops, locker keys and maintenance devices. |
| A.5.12 | Classification of information | Yes | risk | — | Classifying customer PII, parcel events and carrier keys drives proportionate protection. |
| A.5.13 | Labelling of information | Yes | best_practice | — | Consistent labels let staff handle classified customer and operational data correctly. |
| A.5.14 | Information transfer | Yes | risk | — | Parcel events and addresses moving between lockers, cloud and carriers must be encrypted. |
| A.5.15 | Access control | Yes | risk | Yes | Access to the backend, locker management plane and PII is restricted on need-to-know. |
| A.5.16 | Identity management | Yes | risk | — | Every user, technician and service identity across lockers and cloud is uniquely managed. |
| A.5.17 | Authentication information | Yes | risk | — | Passwords, keys and tokens for locker and cloud access are issued and stored securely. |
| A.5.18 | Access rights | Yes | risk | — | Access rights are granted and revoked as staff and carrier partners join, move or leave. |
| A.5.19 | Information security in supplier relationships | Yes | contractual | Yes | Reliance on carriers, cloud and hardware vendors means supplier security must be governed. |
| A.5.20 | Addressing information security within supplier agreements | Yes | contractual | — | Contracts with carriers and the cloud provider set explicit security and PII obligations. |
| A.5.21 | Managing information security in the ICT supply chain | Yes | contractual | Yes | Locker firmware and cloud components arrive via a supply chain assessed for tampering. |
| A.5.22 | Monitoring, review and change management of supplier services | Yes | contractual | — | Carrier API and cloud service changes are reviewed so they don't weaken PaketPort's posture. |
| A.5.23 | Information security for use of cloud services | Yes | contractual | Yes | Routing and the app backend run in the cloud, so cloud security duties are defined and monitored. |
| A.5.24 | Information security incident management planning and preparation | Yes | risk | Yes | Given NIS2 duties and 24/7 lockers, PaketPort keeps a prepared incident-management process. |
| A.5.25 | Assessment and decision on information security events | Yes | risk | Yes | Events from lockers, cloud and monitoring are triaged consistently to identify real incidents. |
| A.5.26 | Response to information security incidents | Yes | risk | — | A defined response limits impact when a locker or backend service is compromised. |
| A.5.27 | Learning from information security incidents | Yes | best_practice | — | Post-incident lessons feed back to harden lockers and the cloud against recurrence. |
| A.5.28 | Collection of evidence | Yes | legal | — | Evidence is collected soundly to support NIS2 reporting and prosecution after tampering. |
| A.5.29 | Information security during disruption | Yes | business | — | Security must hold during outages so parcel handover and customer data stay protected. |
| A.5.30 | ICT readiness for business continuity | Yes | business | Yes | Customers rely on 24/7 lockers, so ICT continuity for backend and devices is planned and tested. |
| A.5.31 | Legal, statutory, regulatory and contractual requirements | Yes | legal | — | PaketPort must identify GDPR, NIS2 and Austrian legal obligations binding its data and services. |
| A.5.32 | Intellectual property rights | Yes | legal | — | Licensing of software in lockers and the backend is tracked to avoid IP infringement. |
| A.5.33 | Protection of records | Yes | legal | — | Retention and integrity of contracts, logs and parcel evidence meet legal and evidential needs. |
| A.5.34 | Privacy and protection of personally identifiable information (PII) | Yes | legal | — | Handling customers' names, addresses and parcel events makes GDPR PII protection mandatory. |
| A.5.35 | Independent review of information security | Yes | best_practice | Yes | Periodic independent audits assure the ISMS works ahead of certification. |
| A.5.36 | Compliance with policies, rules and standards for information security | Yes | best_practice | — | Regular checks confirm lockers, cloud and staff follow PaketPort's security rules. |
| A.5.37 | Documented operating procedures | Yes | best_practice | — | Documented runbooks for locker maintenance and cloud ops ensure secure, repeatable handling. |
| A.6.1 | Screening | Yes | risk | — | Technicians reach street lockers and staff handle PII, so lawful screening cuts insider risk. |
| A.6.2 | Terms and conditions of employment | Yes | contractual | — | Employment contracts state each employee's information security responsibilities. |
| A.6.3 | Information security awareness, education and training | Yes | best_practice | Yes | Staff and field technicians are trained to spot phishing and handle customer data safely. |
| A.6.4 | Disciplinary process | Yes | best_practice | — | A formal disciplinary process addresses security policy breaches consistently and fairly. |
| A.6.5 | Responsibilities after termination or change of employment | Yes | risk | — | Confidentiality and access duties persist when staff leave or change roles. |
| A.6.6 | Confidentiality or non-disclosure agreements | Yes | contractual | — | NDAs bind employees, technicians and carrier partners handling customer and ops data. |
| A.6.7 | Remote working | Yes | risk | — | Office and remote staff connect to the cloud backend, so remote-working security is required. |
| A.6.8 | Information security event reporting | Yes | best_practice | Yes | Staff and technicians have an easy channel to report suspected incidents like tampered lockers. |
| A.7.1 | Physical security perimeters | Yes | risk | Yes | Offices and any hosting space have defined secure perimeters against intrusion. |
| A.7.2 | Physical entry | Yes | risk | — | Entry to PaketPort offices and technical rooms is limited to authorised people. |
| A.7.3 | Securing offices, rooms and facilities | Yes | best_practice | — | Offices and equipment rooms are physically secured against unauthorised access. |
| A.7.4 | Physical security monitoring | Yes | risk | Yes | Street-sited lockers and premises are monitored via CCTV and alarms to detect tampering. |
| A.7.5 | Protecting against physical and environmental threats | Yes | risk | — | Lockers face weather and vandalism, offices fire and flood, all needing protective measures. |
| A.7.6 | Working in secure areas | Yes | best_practice | — | Procedures govern work in server and comms rooms and other sensitive areas. |
| A.7.7 | Clear desk and clear screen | Yes | best_practice | — | Staff clear desks and lock screens to protect customer data in shared offices. |
| A.7.8 | Equipment siting and protection | Yes | risk | — | Locker hardware and IT equipment are sited to reduce theft, damage and unauthorised access. |
| A.7.9 | Security of assets off-premises | Yes | risk | — | Lockers and technicians' devices operate off-premises in public and must be protected. |
| A.7.10 | Storage media | Yes | risk | — | Storage media in lockers, technician kit and the cloud are managed across their lifecycle. |
| A.7.11 | Supporting utilities | Yes | business | — | Power and connectivity to lockers and hosting are protected to keep services and logs up. |
| A.7.12 | Cabling security | Yes | best_practice | — | Power and network cabling for lockers and offices is protected from interception and damage. |
| A.7.13 | Equipment maintenance | Yes | best_practice | — | Regular maintenance keeps lockers and IT equipment secure and available. |
| A.7.14 | Secure disposal or re-use of equipment | Yes | risk | — | Decommissioned lockers and drives are wiped so residual customer data can't be recovered. |
| A.8.1 | User endpoint devices | Yes | risk | — | Staff laptops and technicians' mobile devices accessing the backend are hardened and managed. |
| A.8.2 | Privileged access rights | Yes | risk | Yes | Admin access to the cloud backend and locker fleet management is restricted and monitored. |
| A.8.3 | Information access restriction | Yes | risk | — | Access to applications and personal data is limited by role and need-to-know. |
| A.8.4 | Access to source code | Yes | risk | — | Access to app and locker firmware source code and repositories is restricted and logged. |
| A.8.5 | Secure authentication | Yes | risk | Yes | MFA and strong authentication protect admin, staff and API access to lockers and cloud. |
| A.8.6 | Capacity management | Yes | business | — | Backend and network capacity is planned so parcel routing and lockers stay available at peak. |
| A.8.7 | Protection against malware | Yes | risk | — | Endpoints, servers and Linux edge devices are protected against malware. |
| A.8.8 | Management of technical vulnerabilities | Yes | risk | Yes | Vulnerabilities in the Linux lockers, cloud stack and dependencies are tracked and patched. |
| A.8.9 | Configuration management | Yes | risk | Yes | Secure, consistent baselines are enforced across the Linux locker fleet and cloud services. |
| A.8.10 | Information deletion | Yes | legal | — | Customer PII and parcel data are deleted when no longer needed to meet GDPR minimisation. |
| A.8.11 | Data masking | Yes | best_practice | — | PII is masked in test, support and analytics environments to limit exposure. |
| A.8.12 | Data leakage prevention | Yes | risk | — | DLP controls reduce the risk of customer address and parcel data leaving PaketPort. |
| A.8.13 | Information backup | Yes | business | Yes | Backups of the backend and configuration guard against data loss and enable recovery. |
| A.8.14 | Redundancy of information processing facilities | Yes | business | — | Redundant backend infrastructure keeps lockers and the app available during failures. |
| A.8.15 | Logging | Yes | risk | Yes | Logs from lockers, cloud and access systems are captured to detect and investigate incidents. |
| A.8.16 | Monitoring activities | Yes | risk | Yes | Continuous monitoring of the fleet and backend detects anomalous behaviour and attacks. |
| A.8.17 | Clock synchronization | Yes | best_practice | — | Synchronised clocks across lockers and servers make logs correlatable for investigations. |
| A.8.18 | Use of privileged utility programs | Yes | risk | — | Powerful utility programs on Linux edge devices and servers are restricted and monitored. |
| A.8.19 | Installation of software on operational systems | Yes | risk | — | Software changes on locker devices and production servers are controlled and approved. |
| A.8.20 | Networks security | Yes | risk | Yes | Networks linking lockers, cloud and carriers are secured against unauthorised access. |
| A.8.21 | Security of network services | Yes | risk | — | Security features and SLAs of network services connecting lockers are defined and enforced. |
| A.8.22 | Segregation of networks | Yes | risk | — | Locker, corporate and cloud management networks are segregated to contain compromise. |
| A.8.23 | Web filtering | Yes | best_practice | — | Web filtering on managed devices reduces exposure to malicious and phishing sites. |
| A.8.24 | Use of cryptography | Yes | risk | Yes | Encryption protects personal data in transit and at rest across lockers, cloud and APIs. |
| A.8.25 | Secure development life cycle | Yes | best_practice | — | The customer app and locker firmware are built under a defined secure development lifecycle. |
| A.8.26 | Application security requirements | Yes | risk | — | Security requirements are specified for the customer app and carrier-facing APIs. |
| A.8.27 | Secure system architecture and engineering principles | Yes | best_practice | — | Systems are designed with defence-in-depth and secure-by-default principles. |
| A.8.28 | Secure coding | Yes | best_practice | Yes | Developers follow secure coding standards to cut vulnerabilities in app and firmware. |
| A.8.29 | Security testing in development and acceptance | Yes | risk | — | Security testing including pen tests gates releases of the app and locker firmware. |
| A.8.30 | Outsourced development | Yes | contractual | — | Any outsourced development is bound by PaketPort's security and quality requirements. |
| A.8.31 | Separation of development, test and production environments | Yes | risk | — | Dev, test and production for backend and firmware are separated to prevent exposure. |
| A.8.32 | Change management | Yes | risk | — | Changes to lockers, backend and networks follow controlled change management. |
| A.8.33 | Test information | Yes | best_practice | — | Test data is chosen and protected so live customer PII is not exposed during testing. |
| A.8.34 | Protection of information systems during audit testing | Yes | best_practice | — | Audit and testing on production systems are planned to avoid disrupting lockers and backend. |
