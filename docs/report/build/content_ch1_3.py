"""Chapters 1-3: Introduction, Literature Review, Methodology."""
from docx_base import Report

def ch1(r: Report):
    r.chapter(1, "Introduction")

    r.section("1.1", "Background and Context", first=True)
    r.body("Information is now among the most commercially significant assets that an organisation "
           "holds, and the systems that carry it are distributed across cloud tenancies, supplier "
           "platforms, staff devices and third-party integrations. Protecting that information is not "
           "a product decision but a management decision: it requires a defined scope, an understanding "
           "of risk, a selected set of controls, a way of measuring whether those controls operate, and "
           "a mechanism for improving when they do not. ISO/IEC 27001:2022 specifies the requirements "
           "for exactly this management structure through Clauses 4 to 10, and Annex A supplies a "
           "reference catalogue of organisational, people, physical and technological controls from "
           "which an organisation must determine its own applicability rather than simply adopting all "
           "of them.")
    r.para("The operating rhythm of that management system is the internal audit. An audit programme "
           "generates an unusually dense web of interconnected records. A single control test produces a "
           "criterion, a procedure, a sample population, an observed condition, an evidence artefact, a "
           "conclusion, possibly a nonconformity, a root-cause statement, a corrective action, a named "
           "owner, a due date and a verification note. Multiply that by forty Annex A controls, several "
           "audits per year, and a handful of auditors, and the record set becomes large enough that its "
           "internal consistency matters more than any individual document.")
    r.para("In practice, small audit teams frequently keep these records in a mixture of spreadsheets, "
           "documents, mail threads and shared drives. Each individual artefact may be perfectly "
           "adequate, yet the relationships between them live only in the auditor's memory. Three "
           "questions become disproportionately expensive to answer: which findings remain open and who "
           "owns them; what evidence was actually examined to support a stated conclusion; and whether a "
           "corrective action has been verified as effective rather than merely marked as done. This "
           "fragmentation is the operational problem that the present project addresses.")
    r.para("A second, more contemporary pressure is evidential integrity. Auditors increasingly present "
           "conclusions that rest on digital artefacts, and a reviewer is entitled to ask whether the "
           "file examined today is the same file that was examined at the time of the test. Cryptographic "
           "digests provide a practical answer to that narrow question, and a hash-chained log provides a "
           "related answer for the question of whether the record of activity has been altered after the "
           "fact. Neither mechanism proves that a conclusion was correct, but both materially raise the "
           "cost of undetected alteration.")
    r.para("SecureAudit was conceived against that background: a locally controllable, inspectable and "
           "deployable platform that carries an audit from scope definition through control testing, "
           "evidence capture, findings management, corrective action tracking and report sign-off, while "
           "recording every mutation in an append-only chain. The project has evolved through two "
           "substantial iterations. The first delivered a Streamlit workbench with SQLite persistence and "
           "documented a set of security gaps as proposed enhancements. The second, reported here, "
           "implements those enhancements, adds a React and TypeScript interface backed by a FastAPI REST "
           "service, and deploys the combined platform to a public production URL so that the artefact "
           "can be evaluated by a reviewer without local installation.")

    r.section("1.2", "Purpose of the Minor Project")
    r.body("The purpose of this project is to design, implement and evaluate a coherent web-based platform "
           "that organises the principal records of an ISO/IEC 27001 internal audit workflow, enforces a "
           "defensible baseline of authentication, authorisation and evidence integrity, and produces "
           "management-grade reporting from the same underlying data.")
    r.para("The project has four purposes in sequence. The first is architectural: to establish whether a "
           "single normalised schema can carry an audit record set from scope through to signed report "
           "without loss of traceability. The second is assurance-oriented: to close the security gaps "
           "identified in the first iteration, specifically password storage, session handling, brute-force "
           "resistance, evidence integrity and audit-trail tamper evidence, and to demonstrate that closure "
           "through automated tests rather than assertion. The third is presentational: to determine "
           "whether the same core can support two materially different interfaces without divergence, "
           "which tests the quality of the underlying separation between domain logic and presentation. "
           "The fourth is evaluative: to document honestly what the artefact demonstrates and what it does "
           "not, so that the report remains academically defensible.")
    r.para("The project is explicitly not an attempt to build a commercial GRC product. It does not aim "
           "for multi-tenancy, enterprise identity federation, workflow automation at scale, or the "
           "breadth of framework content that licensed platforms provide. Those exclusions are deliberate "
           "and are revisited in Chapter 7.")

    r.section("1.3", "Research Area and Gap")
    r.body("The research area is digital support for information security audit operations in "
           "resource-constrained settings, with particular attention to evidence traceability and "
           "record-level assurance. The area sits at the intersection of management systems research, "
           "audit methodology and applied software engineering.")
    r.para("Two bodies of existing work bound the project. Standards and guidance, principally ISO/IEC "
           "27001:2022 and ISO 19011, define what a defensible audit process must contain but deliberately "
           "say nothing about software implementation. Commercial GRC platforms implement the process "
           "comprehensively but are priced, scoped and governed for enterprise adoption, and their "
           "internals are not open to inspection. Between these two poles there is a practical gap: small "
           "teams, academic programmes and early-stage ISMS implementations need a tool that is small "
           "enough to understand completely, self-hostable, free of vendor lock-in, and honest about its "
           "assurance properties.")
    r.para("The gap this project addresses is therefore applied and bounded. It is not a claim that "
           "software for ISMS auditing does not exist, nor a claim that a lightweight tool performs better "
           "than an established platform or a disciplined spreadsheet. The contribution is a documented, "
           "reproducible reference implementation whose design decisions, security properties and "
           "limitations are stated explicitly and can be verified by a third party reading the source and "
           "running the test suite.")

    r.section("1.4", "Problem Statement")
    r.body("A small audit team conducting ISO/IEC 27001 internal audit work must coordinate audit scope, "
           "control selection, test procedures, sampled evidence, findings, corrective actions, owners and "
           "due dates, and management reporting. When these records are distributed across independent "
           "artefacts, the relationships between them are not machine-readable, status reporting becomes "
           "manual and error-prone, and the evidential basis of a conclusion cannot be independently "
           "reconstructed.")
    r.para("Compounding this, the tools that are cheap enough for such teams to adopt frequently lack the "
           "security properties that audit records demand: passwords stored with general-purpose hashes, "
           "no resistance to credential guessing, evidence stored without integrity verification, and "
           "activity logs that can be edited by anyone with database access. The problem is therefore "
           "twofold: how to represent an audit workflow as a traceable data model, and how to provide "
           "proportionate assurance over the integrity of that data without the operational overhead of an "
           "enterprise platform.")

    r.section("1.5", "Research Questions")
    r.body("The project is organised around three research questions, each answerable from evidence "
           "generated within the project rather than from opinion.")
    r.table(["ID", "Research question", "Evidence source used to answer it"],
            [["RQ1", "How can a single normalised data model represent the complete record set of an "
                     "ISO/IEC 27001 internal audit, from scope through control testing to signed report, "
                     "while preserving machine-readable traceability between records?",
              "Entity relationship model, schema definition, API contract and rendered interface plates."],
             ["RQ2", "Which security and assurance controls are necessary for an audit-record system to "
                     "support evidential claims, and can a proportionate implementation of those controls "
                     "be verified automatically rather than asserted?",
              "Automated pytest suite output, source inspection of the security module, and integrity "
              "verification against the live deployment."],
             ["RQ3", "What constraints does a lightweight, self-hostable architecture impose on "
                     "organisational adoption, and which residual risks must an adopting organisation "
                     "address before treating such a system as a record of authority?",
              "Architectural analysis, comparison with alternative approaches, deployment verification, "
              "and standards and literature review."]],
            "Research questions and corresponding evidence sources.", widths=[0.5, 3.0, 2.5])

    r.section("1.6", "Objectives")
    r.subsection("1.6.1", "Primary Objective")
    r.body("To design, implement and evaluate a web-based ISMS audit tracker that consolidates ISO/IEC "
           "27001 audit planning, control testing, evidence management, findings and corrective action "
           "tracking, and report generation into a single traceable workflow supported by a verified "
           "security baseline.")
    r.subsection("1.6.2", "Secondary Objectives")
    r.body("The primary objective decomposes into six secondary objectives, each of which maps to a "
           "chapter of this report.")
    r.bullets([
        "To review the standards and academic literature governing ISMS management, audit methodology and "
        "evidence integrity, and to derive design requirements from them (Chapter 2).",
        "To define a research design and a set of analytical instruments proportionate to a "
        "software-artefact study, including schema inspection, source inspection and automated "
        "verification (Chapter 3).",
        "To specify the system architecture, data model, role model and functional requirements, and to "
        "record their implementation status honestly (Chapter 4).",
        "To implement eight security and assurance controls that were previously only proposed, and to "
        "cover each with a repeatable automated test (Chapter 4).",
        "To present and analyse the results obtained from the test suite, the live deployment and the "
        "rendered interface, and to answer the research questions from that evidence (Chapter 5).",
        "To interpret the outcomes against the project objectives and the literature, and to state the "
        "limitations and the prioritised recommendations for further work (Chapters 6 to 8).",
    ])

    r.section("1.7", "Scope and Delimitations")
    r.body("The scope of this project comprises the complete source repository for SecureAudit, including "
           "the React and TypeScript single-page application, the FastAPI REST service, the eight-page "
           "Streamlit workbench, the shared Python core package, the SQLite schema of twelve tables, the "
           "ISO/IEC 27001:2022 reference catalogue, the automated test suite, and the Vercel deployment "
           "configuration. The analysis considers Clauses 4 to 10 of ISO/IEC 27001:2022, its 2024 climate "
           "action amendment, ISO 19011 audit guidance, and illustrative mappings to NIST CSF 2.0 and "
           "SOC 2.")
    r.para("The following are explicitly outside scope. No live organisational environment was audited, "
           "and no real Statement of Applicability was produced. No independent penetration test, "
           "usability study, controlled experiment or user-satisfaction survey was conducted. No claim of "
           "ISO/IEC 27001 conformity or certification is made for any organisation, and no assertion is "
           "made that the platform itself conforms to ISO 19011. Regulatory mappings included in the "
           "catalogue are navigational aids and carry no legal weight. The seeded demonstration records "
           "are fictional and are not evidence of any audit having occurred.")


def ch2(r: Report):
    r.chapter(2, "Literature Review")

    r.section("2.1", "Information Security Management Systems", first=True)
    r.body("ISO/IEC 27001:2022 specifies the requirements for establishing, implementing, maintaining and "
           "continually improving an information security management system. The standard is structured as "
           "a management system rather than a checklist: Clause 4 addresses organisational context, Clauses "
           "5 and 6 address leadership and planning including risk assessment and risk treatment, Clause 7 "
           "addresses support and competence, Clause 8 addresses operation, Clause 9 addresses performance "
           "evaluation through monitoring, measurement, internal audit and management review, and Clause 10 "
           "addresses improvement through nonconformity handling and corrective action.")
    r.para("Two features of this structure are decisive for software design. First, the standard is "
           "explicit that Annex A is a reference set from which applicability must be determined, not a "
           "list to be adopted wholesale. Clause 6.1.3 therefore requires a Statement of Applicability "
           "recording which controls are applicable, why, and whether they are implemented. Any tool that "
           "treats Annex A as a fixed checklist misrepresents the standard. Second, Clause 9.2 requires a "
           "risk-based audit programme that considers the importance of processes and the results of "
           "previous audits. A tool that cannot record programme-level context, previous findings and "
           "risk-based prioritisation therefore cannot support the clause properly.")
    r.para("The 2024 amendment to the standard adds climate change considerations to Clause 4.1 and 4.2, "
           "requiring organisations to determine whether climate change is a relevant issue and whether "
           "interested parties have requirements related to it. This is a modest textual change with a "
           "disproportionate effect on register design: it implies that risk and applicability records must "
           "accommodate context-level factors that are not themselves information security controls. "
           "SecureAudit renders the amendment as a plain-language reference note within its clause "
           "catalogue rather than as a separate workflow, which is an honest representation of its role as "
           "a navigation aid.")
    r.para("A consistent theme in the implementation literature is that information security management "
           "systems succeed or fail on organisational factors rather than on documentation volume. Culot, "
           "Nassimbeni, Podrecca and Sartor conducted a structured review of ISO/IEC 27001 research and "
           "grouped the literature around relationships with other standards, adoption motivations, "
           "implementation issues, outcomes and contextual factors. Their principal finding relevant here "
           "is that implementation and reported outcomes vary substantially with organisational context, "
           "and that evidence about outcomes remains thin. This supports a restrained claim for any "
           "software artefact: a tool can make work visible and consistent, but it cannot manufacture "
           "management commitment, auditor competence or an appropriate risk appetite.")

    r.section("2.2", "Auditing, Evidence and Integrity")
    r.body("ISO 19011 provides guidance on auditing management systems, covering programme management, "
           "audit planning, conduct, reporting, follow-up and auditor competence. Its most useful "
           "contribution to this project is conceptual: it frames an audit as an evidence-based process in "
           "which conclusions must be traceable to criteria and to verified information. The guidance also "
           "encourages the use of risk analysis and technology in audit conduct, which provides "
           "justification for a digital tool while leaving the choice of tool to the organisation.")
    r.para("Audit evidence must be relevant and sufficient to support the conclusion it underpins, and it "
           "must remain intact and attributable throughout its lifecycle. Three distinct properties are "
           "often conflated in practice. Authenticity concerns whether an artefact is what it claims to be "
           "and originates from where it claims. Integrity concerns whether the artefact has changed since "
           "it was captured. Completeness concerns whether the sample examined was adequate for the "
           "conclusion drawn. A cryptographic digest addresses integrity and, weakly, helps detect "
           "substitution; it does not address authenticity or completeness at all. A tool that computes "
           "SHA-256 digests at upload and re-verifies them at download is therefore making a narrow, "
           "defensible claim: the bytes have not changed. It is not making the claim that the control "
           "operated effectively.")
    r.para("The same distinction applies to activity logging. An append-only log with a hash chain in which "
           "each entry incorporates the digest of its predecessor raises the cost of undetected "
           "retrospective editing, because altering entry n invalidates every subsequent entry. It does not "
           "prevent deletion of the entire database by an administrator with filesystem access, nor does it "
           "prevent tampering by an attacker who can recompute the whole chain. Tamper evidence is a "
           "deterrent and a detection mechanism, not an immutability guarantee. The project states this "
           "boundary explicitly in its documentation rather than overstating the property.")
    r.para("Industry guidance on evidence handling adds a fourth consideration that pure cryptography "
           "cannot solve: chain of custody. Recording who collected an artefact, when, from which system, "
           "using which method, and who has held it since, is an organisational control. A system can "
           "capture the metadata fields that support custody, and SecureAudit does record the uploading "
           "identity and timestamp, but it cannot compel the discipline that makes custody meaningful.")

    r.section("2.3", "Implementation Research on ISO/IEC 27001")
    r.body("Research on ISO/IEC 27001 implementation repeatedly identifies the translation step, from a "
           "generic requirement to an organisation-specific practice, as the point of greatest difficulty. "
           "Organisations of different sizes, sectors and technology profiles arrive at materially "
           "different practices while remaining conformant. The practical implication for tool design is "
           "that the tool must be configurable at the level of applicability and justification, not merely "
           "at the level of labels. SecureAudit therefore stores, for each control, an applicability "
           "decision, a justification, an implementation status and a named owner, rather than a binary "
           "compliant flag.")
    r.para("A second strand of the literature concerns the relationship between ISMS maturity and "
           "measurement. Compliance scores are widely used and widely criticised. A score derived from the "
           "proportion of compliant control tests is a useful indicator of testing progress and is useful "
           "for management dashboards, but it is not a measure of security, and it is trivially gamed by "
           "reclassifying tests as not applicable. The project therefore recomputes scores deterministically "
           "from the underlying test results, displays the count of tests that produced the score alongside "
           "the score itself, and avoids presenting the figure as an assurance rating.")
    r.para("Evidence on the outcomes of certification is similarly nuanced. Certification indicates that an "
           "auditor has found the management system to conform at a point in time; it does not indicate that "
           "controls are effective against a competent adversary. For a report of this kind, the only "
           "defensible position is to describe the artefact as an operational aid and to resist any "
           "inference that its use improves security outcomes.")

    r.section("2.4", "Cybersecurity Governance Frameworks and Cross-Mapping")
    r.body("The NIST Cybersecurity Framework 2.0 restructures earlier versions around six concurrent "
           "functions, namely Govern, Identify, Protect, Detect, Respond and Recover, with the Govern "
           "function newly elevated to recognise that cybersecurity risk is a component of organisational "
           "risk and that supply chain and third-party considerations belong within it. The framework is "
           "deliberately outcome-oriented and technology-neutral, which makes it a useful vocabulary for "
           "cross-framework discussion and a poor basis for prescriptive tooling.")
    r.para("Cross-framework mapping is attractive because it promises to reduce duplicated effort across "
           "ISO/IEC 27001, NIST CSF 2.0, SOC 2 and sector regulation. It is also a well-known source of "
           "false assurance. A mapping is an interpretation made in context; the same control may satisfy "
           "an ISO objective and a SOC 2 criterion for different reasons and to different degrees, and a "
           "mapping presented without provenance cannot be defended to an auditor. SecureAudit includes "
           "illustrative mappings in its control register precisely to support discussion, labels them as "
           "illustrative, and states in both the interface and the documentation that they require "
           "validation before any reliance.")
    r.para("A comparison of the principal options available to a small audit team clarifies the design space "
           "that the project occupies.")
    r.table(["Option", "Strengths", "Constraints for a small ISMS team", "Position taken by this project"],
            [["Discipline-only approach (spreadsheets and shared drives)",
              "Zero cost, no training, total flexibility.",
              "Relationships between records are implicit; status reporting is manual; no integrity "
              "verification; version confusion across copies.",
              "Baseline the project improves on, particularly for traceability and integrity."],
             ["Commercial GRC platform",
              "Broad framework coverage, enterprise workflow, vendor support and audit familiarity.",
              "Licensing cost, procurement and security review overhead, limited inspectability, data "
              "residency questions.",
              "Not displaced by this project; the appropriate choice at scale and for regulated enterprises."],
             ["Open-source ticketing or project tools",
              "Familiar interface, low cost, good collaboration.",
              "No ISMS-specific semantics: no Statement of Applicability, no control-test workpapers, no "
              "evidence digests.",
              "Rejected; domain semantics are the core value, not generic task tracking."],
             ["Purpose-built lightweight reference implementation",
              "Complete inspectability, exact domain model, self-hostable, no licence cost, honest "
              "assurance claims.",
              "Narrower framework coverage, no vendor support, single-team scale.",
              "Adopted as the architecture for SecureAudit."]],
            "Comparison of platform options for small-team ISMS audit work.", widths=[1.35, 1.5, 1.85, 1.8])

    r.section("2.5", "Conceptual Framework")
    r.body("The project adopts a workflow traceability model in which the audit is treated as a chain of "
           "records rather than a set of documents. Seven stages form the chain: establish scope and "
           "objectives; select criteria and applicable controls; record test procedures and samples; capture "
           "and digest evidence; document the finding where the condition differs from the criterion; assign "
           "corrective action with owner and due date; and review status before issuing a signed report. Each "
           "stage in the chain writes a record that carries the identifier of the stage before it, making the "
           "whole sequence reconstructible from the database alone.")
    r.para("Five constructs operationalise that model, and each is tied to an observable artefact rather "
           "than a subjective judgement. Traceability is observable as identifier linkage across tables. "
           "Accountability is observable as role permissions and named owners. Timeliness is observable as "
           "planned and due dates with derived overdue state. Evidence support is observable as evidence "
           "records with digests and byte counts. Assurance is observable as the outcomes of integrity and "
           "chain verification. The framework deliberately omits user satisfaction and perceived usability as "
           "primary constructs, because neither was measured in this project.")
    r.para("The model is also explicitly non-normative about effectiveness. It asserts that a record set can "
           "be made internally consistent and reconstructible; it does not assert that a consistent record "
           "set corresponds to a well-controlled environment. That distinction is the subject of Section 2.6.")

    r.section("2.6", "Research Gap Synthesis")
    r.body("The literature supports three conclusions that shape this project. Implementation success is "
           "context-dependent, so a tool must expose applicability and justification rather than enforce "
           "uniformity. Evidence integrity is a property that can be engineered and verified, but only for "
           "narrowly defined claims, so the tool must state which claim it supports. And measurement in this "
           "domain is prone to false precision, so reporting should separate facts from inferences.")
    r.para("The gap that remains is not conceptual but practical and evidential. Existing published accounts "
           "of ISMS tooling rarely disclose both the implementation and its assurance properties in a form "
           "that a third party can verify. This project addresses that gap by publishing a complete "
           "implementation together with an automated verification suite and a deployment that a reviewer can "
           "interrogate directly. The contribution is therefore a transparent reference implementation and an "
           "explicit requirement-to-implementation trace, not a new theory of auditing and not a measured "
           "improvement claim.")
    r.para("Consistent with that position, a future evaluation could legitimately compare a spreadsheet "
           "baseline against the platform on task completion time, completeness of evidence linkage and review "
           "effort, using a controlled protocol. That study was not conducted here, and Chapter 8 sets out how "
           "it would be designed.")


def ch3(r: Report):
    r.chapter(3, "Research Methodology")

    r.section("3.1", "Research Design", first=True)
    r.body("The project follows a design-and-development case design, sometimes described in information "
           "systems research as a build-and-evaluate cycle. A practical problem is characterised, an "
           "artefact is designed and constructed to address it, the artefact is demonstrated in a realistic "
           "configuration, and the result is evaluated against requirements derived before construction "
           "began.")
    r.para("Three considerations justified this design over an empirical or survey design. The research "
           "questions concern the feasibility and properties of a constructed artefact rather than the "
           "behaviour of people or organisations, so a construction study is the proportionate instrument. "
           "The principal claims to be tested, namely that a single schema can carry an audit end to end "
           "and that eight security controls can be implemented and verified, are falsifiable by inspecting "
           "and executing the artefact, which gives the study genuine evaluative content rather than merely "
           "descriptive content. And the constraint of a single-semester project with no access to "
           "organisational sites made any design requiring live audit participants infeasible.")
    r.para("The evaluation within the design-and-development cycle is deliberately plural. It combines "
           "automated verification, which provides reproducible and binary evidence for the security and "
           "export claims; deployment verification, which demonstrates that the artefact operates outside the "
           "authoring environment; and structured interface inspection, which provides evidence for the "
           "workflow and traceability claims. No single source of evidence is treated as sufficient for any "
           "claim, and the boundaries of each source are stated in Chapter 5.")

    r.section("3.2", "Population, Sample and Frame")
    r.body("The population of interest is the set of information security audit activities and records that "
           "an organisation operating an ISO/IEC 27001 management system must coordinate. Because the study "
           "is an artefact study rather than an observational one, the population is not sampled in the "
           "statistical sense; it defines the requirements space against which the artefact is assessed.")
    r.para("The sampling frame is the set of modules represented in the implementation. Twelve frames "
           "correspond to the twelve database tables, grouped into five functional clusters: identity and "
           "session management comprising the user and session tables; audit planning comprising the audit "
           "table; control testing and findings comprising the test, finding and action tables; the control "
           "and risk registers comprising the control, risk and requirement tables; and assurance comprising "
           "the evidence, audit log and meta-state tables.")
    r.para("The purposive sample is the complete submitted source repository, comprising seventeen Python "
           "modules totalling approximately 4,800 lines and twelve TypeScript modules totalling "
           "approximately 5,100 lines, together with the SQLite schema, the automated test suite, the "
           "deployment configuration and the live deployment. The seeded demonstration dataset of four "
           "audits, twenty control tests, eight findings, seven corrective actions, forty Annex A controls, "
           "five risks and four evidence artefacts is included as illustrative content only; it is not "
           "treated as sampled organisational observations and no statistical inference is drawn from it.")

    r.section("3.3", "Sampling Technique")
    r.body("Purposive selection was used because the study concerns a single artefact and the relevant "
           "evidence is the artefact itself. Within the artefact, every module that implements a claimed "
           "capability was inspected; nothing was sampled out. Where a claim could be tested by execution "
           "rather than inspection, execution was preferred, because inspection alone cannot distinguish "
           "between code that appears correct and code that behaves correctly.")
    r.para("No probabilistic sampling was used and no inferential generalisation is made. Statements in this "
           "report are about SecureAudit as submitted, not about ISMS tooling in general. This limitation is "
           "restated in Chapter 8 because it is the most common way in which artefact studies overreach.")

    r.section("3.4", "Research Instruments")
    r.body("Five analytical instruments were constructed for this study. Each is described below with its "
           "purpose and its limitation.")
    r.bullets([
        "Document review sheet. Records the standards and guidance references relevant to each requirement, "
        "with edition and clause level where applicable, so that design decisions can be traced to a source. "
        "Limitation: standards were consulted as published summaries and licensed text was not reproduced.",
        "Feature traceability matrix. Maps each intended requirement to the module, table, API endpoint or "
        "export that implements it, and records a status of implemented, partially implemented or not "
        "implemented. Limitation: status reflects the submitted revision and is time-bounded.",
        "Automated verification suite. A pytest suite of five test groups covering health and seeding, "
        "scrypt login with lockout, role-based authorisation boundaries, SHA-256 evidence upload and "
        "verification, and PDF, Excel and JSON export. Limitation: it tests behaviour, not security against "
        "an adversary; it is not a penetration test.",
        "Deployment verification checklist. A defined sequence of requests against the production URL "
        "checking the health endpoint, the OpenAPI document, the workspace payload, report generation and "
        "the hash-chain status. Limitation: it demonstrates availability and correctness, not load behaviour.",
        "Interface rendering instrument. A deterministic renderer that reads the live SQLite database and "
        "draws the interface plates in Chapter 4 directly from the recorded values. This replaces the "
        "screenshot approach of the earlier iteration, where displayed values could not be tied to the "
        "database. Limitation: it reproduces layout faithfully but is not a browser capture, so it cannot "
        "evidence rendering behaviour of the React components.",
    ])
    r.para("The instruments were prepared for this report and are not validated psychometric or security "
           "instruments. Where an instrument produces a binary result, such as a test passing or a digest "
           "matching, the result is reported as produced. Where an instrument produces an interpretation, "
           "such as a requirement being partially implemented, the basis for the interpretation is stated "
           "alongside it.")

    r.section("3.5", "Data Collection")
    r.body("Data collection proceeded in four streams, sequenced so that later streams could challenge the "
           "output of earlier ones.")
    r.para("The documentary stream collected the standards and guidance references, namely ISO/IEC "
           "27001:2022 and its 2024 amendment, ISO 19011 audit guidance, NIST CSF 2.0 and peer-reviewed "
           "literature on ISO/IEC 27001 implementation, together with the institutional minor project "
           "format guidelines that govern this document. Bibliographic details were verified against "
           "publisher records.")
    r.para("The code inspection stream examined every Python and TypeScript module, the SQLite schema "
           "definition, the API contract exposed through the OpenAPI document, and the deployment "
           "configuration. Particular attention was paid to the security module, where the earlier "
           "iteration stored passwords with unsalted SHA-256, to confirm that the current revision derives "
           "keys with scrypt and that the lockout and token logic are reachable from the authentication "
           "endpoint rather than merely present in a library.")
    r.para("The execution stream ran the automated suite under a clean environment, collected the recorded "
           "pass and fail status of each test group, and separately exercised the production deployment. "
           "Execution results were taken from the runner's own output rather than transcribed, so that the "
           "reported count reflects what the runner observed.")
    r.para("The data stream queried the seeded SQLite database for the values used in the interface plates "
           "and in the analysis of counts and distributions. Because the plates are rendered from those "
           "query results, any discrepancy between the prose and the interface would be a defect in the "
           "report rather than an artefact of screenshot drift.")
    r.para("No human participants were involved, no personal data was collected, and no organisational "
           "systems were accessed. The demonstration dataset contains fictional names and email addresses "
           "in the .local domain.")

    r.section("3.6", "Data Analysis")
    r.body("Analysis is descriptive and traceability-driven. Each requirement was assigned to a workflow "
           "stage, each implementation was traced to the requirement it satisfies, and each claim in this "
           "report was tied to at least one instrument output. Where an instrument could not support a "
           "claim, the claim was withdrawn rather than softened.")
    r.para("A three-level status vocabulary was applied consistently. Implemented means the capability is "
           "present in the submitted source and is exercised by the automated suite or by deployment "
           "verification. Partially implemented means the capability is present but with a stated "
           "limitation, for example integrity verification without encryption at rest. Not implemented "
           "means no supporting code path was found, and such items are described as future work rather "
           "than as features.")
    r.para("Two analyses were applied to the research questions. RQ1 was analysed structurally, by "
           "decomposing the schema into entities and relationships and then demonstrating that a record "
           "entered at each stage retains a resolvable path to every other stage. RQ2 was analysed "
           "behaviourally, by mapping each security control to the test that exercises it and recording "
           "the observed outcome. RQ3 was analysed comparatively, by contrasting the architecture against "
           "the alternatives set out in Table 2 and by enumerating the residual risks that the "
           "architecture cannot address.")
    r.table(["RQ", "Analysis procedure", "Output produced"],
            [["RQ1", "Decompose the schema into entities and reference relationships; trace an audit record "
                     "from creation through testing, evidence, findings and actions to report generation; "
                     "render the interface directly from the resulting values.",
              "Entity relationship model, workflow traceability model, feature traceability matrix and eight "
              "interface plates."],
             ["RQ2", "Enumerate each claimed security control; locate its implementation in source; identify "
                     "the test that exercises it; record the observed result; verify the same behaviour on "
                     "the production deployment.",
              "Security control matrix, test coverage table and deployment verification results."],
             ["RQ3", "Compare the architecture against spreadsheet, commercial and generic tooling "
                     "alternatives; enumerate residual risks that the architecture cannot mitigate; relate "
                     "to standards and literature.",
              "Comparative analysis, limitations register and prioritised recommendations."]],
            "Mapping of research questions to analysis procedures.", widths=[0.5, 3.0, 2.5])
    r.para("No inferential statistics were computed because no sample of observations exists. Where counts "
           "and percentages appear in the results, they describe the seeded dataset and are labelled as such.")

    r.section("3.7", "Implementation Method")
    r.body("Construction followed nine work packages, sequenced to keep a runnable artefact at every stage. "
           "The sequence is presented as a retrospective organisation of the work rather than as a dated "
           "changelog, and the deliverables named are those that exist in the submitted repository.")
    r.figure("docs/report/figures/figure-3-2-phases.png",
             "Nine-phase implementation roadmap and deliverables. The sequence keeps the artefact runnable "
             "at every stage; later phases extend earlier ones rather than replacing them.", width_in=6.0)
    r.para("The first two phases established the runtime and the data foundation: the Vite and React "
           "scaffold, the FastAPI application, the cross-platform launchers, the twelve-table SQLite schema "
           "and the ISO/IEC 27001:2022 reference catalogue of forty Annex A controls and sixteen clause "
           "entries. Phases three to five built the domain workflows: the risk and Statement of "
           "Applicability registers, audit planning with control-test workpapers, and findings with "
           "corrective and preventive action tracking. Phase six introduced assurance: the SHA-256 evidence "
           "vault and the hash-chained audit log. Phase seven added analytical views. Phase eight "
           "implemented the security baseline of scrypt authentication, role-based access control, account "
           "lockout, signed session tokens and user administration. Phase nine completed the exports, the "
           "documentation and the serverless deployment.")
    r.para("One methodological point deserves emphasis. In the earlier iteration of this artefact, several "
           "capabilities were described in the project narrative but were not present in the inspected "
           "source, and the corresponding report was obliged to classify them as proposed rather than "
           "implemented. The present iteration treats that as a design input: each previously unverified "
           "capability was implemented and then bound to an automated test, so that the claim and its "
           "evidence were created together. This is why the test suite in Chapter 5 is organised around "
           "capabilities rather than around modules.")

    r.section("3.8", "Ethical and Academic Considerations")
    r.body("Four ethical commitments governed the work. The report does not present fictional data as "
           "organisational evidence, and every interface plate is captioned to that effect. The report "
           "does not claim certification, conformity or effectiveness for any organisation. The report "
           "does not overstate the assurance properties of the artefact, and in particular distinguishes "
           "tamper evidence from immutability and integrity from authenticity. And the report discloses "
           "the capabilities that remain unimplemented rather than omitting them.")
    r.para("No human participants were involved, so no ethics approval was required. No personal data was "
           "collected. The demonstration dataset uses fictional identities. Licensed ISO standard text is "
           "not reproduced; clause and control identifiers are cited as references, and their content is "
           "described in the author's own words. Third-party documentation and repository conventions "
           "consulted during development are acknowledged in the bibliography.")
