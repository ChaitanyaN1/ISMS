"""Reference catalogue for ISO/IEC 27001:2022, 2024 Climate Action Amendment,
ISO 19011:2026 audit guidance themes, and illustrative cross-framework mappings.

Important governance note (per Chapter 2 & Annexure B of the Minor Project Report):
This catalogue provides plain-language summaries and reference identifiers only.
It does not reproduce copyrighted ISO standard text and does not constitute a
certified Statement of Applicability or legal/regulatory determination.
"""

from __future__ import annotations

ISO_27001_CLAUSES: list[dict[str, str]] = [
    {
        "clause_id": "4.1",
        "section": "4. Context of the Organization",
        "title": "Understanding the organization and its context",
        "summary": "Identify internal and external issues relevant to ISMS purpose and outcomes, including climate action considerations introduced in Amd 1:2024.",
        "amendment_2024": "Amd 1:2024 requires determining whether climate change is a relevant issue.",
    },
    {
        "clause_id": "4.2",
        "section": "4. Context of the Organization",
        "title": "Understanding the needs and expectations of interested parties",
        "summary": "Determine interested parties and relevant requirements addressed through the ISMS.",
        "amendment_2024": "Amd 1:2024 notes that interested parties can have requirements related to climate change.",
    },
    {
        "clause_id": "4.3",
        "section": "4. Context of the Organization",
        "title": "Determining the scope of the ISMS",
        "summary": "Define and document boundaries and applicability of the ISMS.",
        "amendment_2024": "",
    },
    {
        "clause_id": "4.4",
        "section": "4. Context of the Organization",
        "title": "Information security management system",
        "summary": "Establish, implement, maintain, and continually improve the ISMS and needed processes.",
        "amendment_2024": "",
    },
    {
        "clause_id": "5.1",
        "section": "5. Leadership",
        "title": "Leadership and commitment",
        "summary": "Top management demonstrates commitment to information security objectives, resources, and continual improvement.",
        "amendment_2024": "",
    },
    {
        "clause_id": "5.2",
        "section": "5. Leadership",
        "title": "Policy",
        "summary": "Establish, communicate, and maintain an information security policy aligned with organizational context.",
        "amendment_2024": "",
    },
    {
        "clause_id": "5.3",
        "section": "5. Leadership",
        "title": "Organizational roles, responsibilities and authorities",
        "summary": "Assign and communicate ISMS conformity and performance reporting responsibilities.",
        "amendment_2024": "",
    },
    {
        "clause_id": "6.1",
        "section": "6. Planning",
        "title": "Actions to address risks and opportunities (Risk Assessment & Treatment, SoA)",
        "summary": "Define risk assessment criteria, evaluate information security risks, select Annex A controls, and produce a Statement of Applicability.",
        "amendment_2024": "",
    },
    {
        "clause_id": "6.2",
        "section": "6. Planning",
        "title": "Information security objectives and planning to achieve them",
        "summary": "Establish measurable, monitored, and documented information security objectives.",
        "amendment_2024": "",
    },
    {
        "clause_id": "6.3",
        "section": "6. Planning",
        "title": "Planning of changes",
        "summary": "Carry out changes to the ISMS in a planned and controlled manner.",
        "amendment_2024": "",
    },
    {
        "clause_id": "7.1-7.5",
        "section": "7. Support",
        "title": "Resources, competence, awareness, communication, and documented information",
        "summary": "Provide resources, verify auditor and staff competence, run awareness activities, and control ISMS documentation.",
        "amendment_2024": "",
    },
    {
        "clause_id": "8.1-8.3",
        "section": "8. Operation",
        "title": "Operational planning, risk assessment execution, and risk treatment execution",
        "summary": "Plan and control ISMS processes, perform scheduled risk assessments, and implement risk treatment plans.",
        "amendment_2024": "",
    },
    {
        "clause_id": "9.1",
        "section": "9. Performance Evaluation",
        "title": "Monitoring, measurement, analysis and evaluation",
        "summary": "Evaluate information security performance and the effectiveness of the ISMS.",
        "amendment_2024": "",
    },
    {
        "clause_id": "9.2",
        "section": "9. Performance Evaluation",
        "title": "Internal audit",
        "summary": "Conduct planned internal audits to check conformity with organizational and ISO/IEC 27001 requirements.",
        "amendment_2024": "",
    },
    {
        "clause_id": "9.3",
        "section": "9. Performance Evaluation",
        "title": "Management review",
        "summary": "Top management reviews ISMS suitability, adequacy, effectiveness, audit results, and nonconformities.",
        "amendment_2024": "",
    },
    {
        "clause_id": "10.1-10.2",
        "section": "10. Improvement",
        "title": "Continual improvement, nonconformity and corrective action",
        "summary": "React to nonconformities, evaluate root causes, implement corrective actions (CAPA), and review effectiveness.",
        "amendment_2024": "",
    },
]


ANNEX_A_CONTROLS_CATALOGUE: list[dict[str, str]] = [
    # Domain 5: Organizational controls
    {"control_id": "A.5.1", "domain": "Organizational (5)", "title": "Policies for information security", "description": "Information security policy and topic-specific policies defined, approved by management, published, and reviewed.", "nist_csf": "GV.PO-01", "soc2": "CC1.2"},
    {"control_id": "A.5.2", "domain": "Organizational (5)", "title": "Information security roles and responsibilities", "description": "Information security roles and responsibilities defined and allocated according to organizational needs.", "nist_csf": "GV.RR-02", "soc2": "CC1.3"},
    {"control_id": "A.5.3", "domain": "Organizational (5)", "title": "Segregation of duties", "description": "Conflicting duties and conflicting areas of responsibility segregated to reduce unauthorized modification or misuse.", "nist_csf": "PR.AA-05", "soc2": "CC5.1"},
    {"control_id": "A.5.7", "domain": "Organizational (5)", "title": "Threat intelligence", "description": "Information relating to information security threats collected and analyzed to produce threat intelligence.", "nist_csf": "ID.RA-02", "soc2": "CC3.2"},
    {"control_id": "A.5.9", "domain": "Organizational (5)", "title": "Inventory of information and other associated assets", "description": "An inventory of information and other associated assets, including owners, developed and maintained.", "nist_csf": "ID.AM-01", "soc2": "CC6.1"},
    {"control_id": "A.5.12", "domain": "Organizational (5)", "title": "Classification of information", "description": "Information classified according to security needs based on confidentiality, integrity, and availability.", "nist_csf": "ID.AM-05", "soc2": "CC6.1"},
    {"control_id": "A.5.15", "domain": "Organizational (5)", "title": "Access control", "description": "Rules to control physical and logical access to information and assets established based on business requirements.", "nist_csf": "PR.AA-01", "soc2": "CC6.1"},
    {"control_id": "A.5.17", "domain": "Organizational (5)", "title": "Authentication information", "description": "Allocation and management of authentication information controlled by a management process.", "nist_csf": "PR.AA-02", "soc2": "CC6.2"},
    {"control_id": "A.5.19", "domain": "Organizational (5)", "title": "Information security in supplier relationships", "description": "Processes and procedures defined to manage information security risks associated with supplier access and services.", "nist_csf": "GV.SC-01", "soc2": "CC9.2"},
    {"control_id": "A.5.23", "domain": "Organizational (5)", "title": "Information security for use of cloud services", "description": "Processes for acquisition, use, management, and exit from cloud services established in accordance with security requirements.", "nist_csf": "GV.SC-06", "soc2": "CC9.2"},
    {"control_id": "A.5.24", "domain": "Organizational (5)", "title": "Information security incident management planning and preparation", "description": "Incident management responsibilities and procedures planned and prepared for effective response.", "nist_csf": "RS.MA-01", "soc2": "CC7.3"},
    {"control_id": "A.5.28", "domain": "Organizational (5)", "title": "Collection of evidence", "description": "Procedures established and implemented for identification, collection, acquisition, and preservation of evidence.", "nist_csf": "RS.AN-03", "soc2": "CC7.4"},
    {"control_id": "A.5.30", "domain": "Organizational (5)", "title": "ICT readiness for business continuity", "description": "ICT readiness planned, implemented, maintained, and tested based on business continuity objectives.", "nist_csf": "RC.RP-01", "soc2": "A1.2"},
    {"control_id": "A.5.34", "domain": "Organizational (5)", "title": "Privacy and protection of PII", "description": "Requirements regarding preservation of privacy and protection of PII identified and met.", "nist_csf": "GV.OC-03", "soc2": "P1.1"},
    {"control_id": "A.5.35", "domain": "Organizational (5)", "title": "Independent review of information security", "description": "Organization approach to managing information security reviewed independently at planned intervals.", "nist_csf": "GV.OV-03", "soc2": "CC4.1"},
    # Domain 6: People controls
    {"control_id": "A.6.1", "domain": "People (6)", "title": "Screening", "description": "Background verification checks on all candidates for employment carried out prior to joining.", "nist_csf": "PR.AT-01", "soc2": "CC1.4"},
    {"control_id": "A.6.2", "domain": "People (6)", "title": "Terms and conditions of employment", "description": "Employment contractual agreements state employee and organization responsibilities for information security.", "nist_csf": "GV.RR-04", "soc2": "CC1.4"},
    {"control_id": "A.6.3", "domain": "People (6)", "title": "Information security awareness, education and training", "description": "Personnel receive appropriate information security awareness education and regular updates.", "nist_csf": "PR.AT-01", "soc2": "CC1.4"},
    {"control_id": "A.6.5", "domain": "People (6)", "title": "Responsibilities after termination or change of employment", "description": "Information security responsibilities and duties remaining valid after termination defined and enforced.", "nist_csf": "PR.AA-01", "soc2": "CC6.2"},
    {"control_id": "A.6.7", "domain": "People (6)", "title": "Remote working", "description": "Security measures implemented when personnel work remotely to protect information accessed outside organizational premises.", "nist_csf": "PR.AC-03", "soc2": "CC6.6"},
    # Domain 7: Physical controls
    {"control_id": "A.7.1", "domain": "Physical (7)", "title": "Physical security perimeters", "description": "Security perimeters defined and used to protect areas containing information and other associated assets.", "nist_csf": "PR.AA-06", "soc2": "CC6.4"},
    {"control_id": "A.7.2", "domain": "Physical (7)", "title": "Physical entry", "description": "Secure areas protected by appropriate entry controls and access points to restrict authorized personnel only.", "nist_csf": "PR.AA-06", "soc2": "CC6.4"},
    {"control_id": "A.7.4", "domain": "Physical (7)", "title": "Physical security monitoring", "description": "Premises continuously monitored for unauthorized physical access.", "nist_csf": "DE.CM-02", "soc2": "CC6.4"},
    {"control_id": "A.7.10", "domain": "Physical (7)", "title": "Storage media", "description": "Storage media managed through their lifecycle of acquisition, use, transportation, and disposal.", "nist_csf": "PR.DS-01", "soc2": "CC6.5"},
    # Domain 8: Technological controls
    {"control_id": "A.8.1", "domain": "Technological (8)", "title": "User endpoint devices", "description": "Information stored on, processed by, or accessible via user endpoint devices protected.", "nist_csf": "PR.PS-01", "soc2": "CC6.8"},
    {"control_id": "A.8.2", "domain": "Technological (8)", "title": "Privileged access rights", "description": "Allocation and use of privileged access rights restricted and managed.", "nist_csf": "PR.AA-05", "soc2": "CC6.3"},
    {"control_id": "A.8.5", "domain": "Technological (8)", "title": "Secure authentication", "description": "Secure authentication technologies and procedures implemented based on access restrictions and MFA policy.", "nist_csf": "PR.AA-03", "soc2": "CC6.1"},
    {"control_id": "A.8.7", "domain": "Technological (8)", "title": "Protection against malware", "description": "Protection against malware implemented and supported by appropriate user awareness.", "nist_csf": "DE.CM-09", "soc2": "CC6.8"},
    {"control_id": "A.8.8", "domain": "Technological (8)", "title": "Management of technical vulnerabilities", "description": "Information about technical vulnerabilities of information systems obtained in a timely fashion and remediated.", "nist_csf": "ID.RA-01", "soc2": "CC7.1"},
    {"control_id": "A.8.9", "domain": "Technological (8)", "title": "Configuration management", "description": "Configurations, including security configurations, of hardware, software, services, and networks established and monitored.", "nist_csf": "PR.PS-01", "soc2": "CC6.1"},
    {"control_id": "A.8.12", "domain": "Technological (8)", "title": "Data leakage prevention", "description": "Data leakage prevention measures applied to systems, networks, and devices that process sensitive information.", "nist_csf": "PR.DS-05", "soc2": "CC6.7"},
    {"control_id": "A.8.13", "domain": "Technological (8)", "title": "Information backup", "description": "Backup copies of information, software, and systems maintained and regularly tested.", "nist_csf": "PR.DS-11", "soc2": "A1.2"},
    {"control_id": "A.8.15", "domain": "Technological (8)", "title": "Logging", "description": "Logs that record activities, exceptions, faults, and other relevant events produced, stored, protected, and analyzed.", "nist_csf": "DE.CM-01", "soc2": "CC7.2"},
    {"control_id": "A.8.16", "domain": "Technological (8)", "title": "Monitoring activities", "description": "Networks, systems, and applications monitored for anomalous behaviour and appropriate actions taken.", "nist_csf": "DE.AE-02", "soc2": "CC7.2"},
    {"control_id": "A.8.20", "domain": "Technological (8)", "title": "Networks security", "description": "Networks and network devices secured, managed, and controlled to protect information in systems and applications.", "nist_csf": "PR.IR-01", "soc2": "CC6.6"},
    {"control_id": "A.8.24", "domain": "Technological (8)", "title": "Use of cryptography", "description": "Rules for the effective use of cryptography, including cryptographic key management, defined and implemented.", "nist_csf": "PR.DS-01", "soc2": "CC6.1"},
    {"control_id": "A.8.25", "domain": "Technological (8)", "title": "Secure development life cycle", "description": "Rules for the secure development of software and systems established and applied.", "nist_csf": "PR.PS-06", "soc2": "CC8.1"},
    {"control_id": "A.8.28", "domain": "Technological (8)", "title": "Secure coding", "description": "Secure coding principles applied to software development to minimize security vulnerabilities.", "nist_csf": "PR.PS-06", "soc2": "CC8.1"},
    {"control_id": "A.8.29", "domain": "Technological (8)", "title": "Security testing in development and acceptance", "description": "Security testing processes defined and implemented in the development life cycle.", "nist_csf": "ID.RA-01", "soc2": "CC8.1"},
    {"control_id": "A.8.32", "domain": "Technological (8)", "title": "Change management", "description": "Changes to information processing facilities and information systems subject to change management procedures.", "nist_csf": "PR.PS-02", "soc2": "CC8.1"},
]


REGULATORY_FRAMEWORKS: list[dict[str, str]] = [
    {
        "req_id": "REQ-ISO-9.2",
        "framework": "ISO/IEC 27001:2022",
        "reference": "Clause 9.2",
        "requirement_summary": "Conduct internal audits at planned intervals to verify ISMS conformity and maintenance.",
        "mapped_controls": "A.5.35, A.5.1, A.8.15",
        "status": "Assessed",
        "notes": "Illustrative mapping for audit programme governance.",
    },
    {
        "req_id": "REQ-ISO-AMD1",
        "framework": "ISO/IEC 27001:2022/Amd 1:2024",
        "reference": "Clauses 4.1 & 4.2",
        "requirement_summary": "Evaluate whether climate change is a relevant issue and review interested party climate expectations.",
        "mapped_controls": "A.5.1, A.5.30",
        "status": "In Review",
        "notes": "Illustrative reference to 2024 climate action amendment.",
    },
    {
        "req_id": "REQ-NIST-GV",
        "framework": "NIST CSF 2.0",
        "reference": "GV.OC / GV.RR / GV.SC",
        "requirement_summary": "Establish cybersecurity governance context, risk roles, oversight, and supply chain risk management.",
        "mapped_controls": "A.5.1, A.5.2, A.5.19, A.5.23",
        "status": "Assessed",
        "notes": "Illustrative cross-framework outcome mapping.",
    },
    {
        "req_id": "REQ-NIST-PR",
        "framework": "NIST CSF 2.0",
        "reference": "PR.AA / PR.DS / PR.PS",
        "requirement_summary": "Manage identity, privileged access, MFA authentication, data protection, and secure configurations.",
        "mapped_controls": "A.5.15, A.8.2, A.8.5, A.8.9, A.8.24",
        "status": "Gap Identified",
        "notes": "Linked to privileged account MFA finding in illustrative audit.",
    },
    {
        "req_id": "REQ-SOC2-CC6",
        "framework": "SOC 2 Trust Services Criteria",
        "reference": "CC6.1 - CC6.8",
        "requirement_summary": "Logical and physical access controls restrict unauthorized access and enforce strong authentication.",
        "mapped_controls": "A.5.15, A.5.17, A.7.2, A.8.5",
        "status": "In Review",
        "notes": "Tracked under SOC 2 Type II Readiness Assessment.",
    },
    {
        "req_id": "REQ-SOC2-CC7",
        "framework": "SOC 2 Trust Services Criteria",
        "reference": "CC7.1 - CC7.4",
        "requirement_summary": "Detect configuration anomalies, monitor security events, manage vulnerabilities, and execute incident response.",
        "mapped_controls": "A.5.24, A.8.8, A.8.15, A.8.16",
        "status": "Gap Identified",
        "notes": "Linked to patch management remediation tracking.",
    },
]
