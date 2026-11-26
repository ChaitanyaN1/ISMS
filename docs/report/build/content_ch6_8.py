"""Chapters 6-8, references and annexures."""
from docx_base import Report

def ch6(r: Report):
    r.chapter(6, "Discussion")

    r.section("6.1", "Interpretation in Relation to Objectives", first=True)
    r.body("The primary objective was to design, implement and evaluate a web-based tracker that "
           "consolidates ISO/IEC 27001 audit planning, control testing, evidence management, findings, "
           "corrective action tracking and reporting into one traceable workflow with a verified security "
           "baseline. That objective is met at the level of a working artefact: the seven stages of the "
           "workflow model are each backed by a record type, the relationships between records are "
           "queryable, the deliverables are generated from the same data, and eight security controls are "
           "implemented and covered by automated tests.")
    r.para("The objective is not met at the level of organisational effect, and it was never framed that "
           "way. The project does not establish that an organisation using the platform conducts better "
           "audits, closes findings faster, reduces risk or achieves certification. Those are outcome "
           "claims, and the design of this study cannot support them. The honest formulation of the "
           "achievement is that the project demonstrates a coherent, inspectable mechanism for making audit "
           "work consistent and reconstructible, with a security baseline proportionate to a small team and "
           "with its limits documented.")
    r.para("Of the six secondary objectives, five are met without qualification: the literature review "
           "produced design requirements that are traceable into the implementation; the methodology is "
           "appropriate to a software artefact and is stated with its limitations; the architecture, data "
           "model and role model are specified and their status recorded; the eight assurance controls are "
           "implemented and verified; and the results, discussion and limitations are reported from evidence. "
           "The sixth, concerning prioritised recommendations, is met in Chapter 7 but with the qualification "
           "that the recommendations are derived from analysis rather than from operational trial.")

    r.section("6.2", "Relationship to Literature and Standards")
    r.body("The platform's workflow is consistent with the management-system audit cycle described in ISO "
           "19011 guidance and with the plan-do-check-act orientation of ISO/IEC 27001 Clauses 4 to 10. The "
           "design decision to record applicability and justification per control, rather than a compliance "
           "flag, follows directly from Clause 6.1.3 and from the literature's emphasis on context-dependent "
           "implementation. The audit container records the risk-based selection considerations that Clause "
           "9.2 requires, although it does not automate the selection itself.")
    r.para("The project also aligns with NIST CSF 2.0 in a structural sense that is worth stating. The "
           "framework's elevation of the Govern function reflects the position that cybersecurity risk is "
           "organisational risk; the platform's role model, approval workflow and chained audit trail are "
           "governance mechanisms rather than technical controls, and they occupy the space the framework "
           "describes. The cross-framework mappings included in the control register are illustrative and "
           "are labelled as such, consistent with the framework's own technology-neutral stance and with the "
           "warning in Section 2.4 that mappings without provenance are a source of false assurance.")
    r.para("The most important relationship to the literature concerns the limits of tooling. Culot and "
           "colleagues found that ISO/IEC 27001 implementation and outcomes vary substantially with "
           "organisational context, and that evidence about outcomes remains thin. This project reaches the "
           "same conclusion from a different direction: the engineering work can make a workflow "
           "reconstructible, but the factors that determine whether an ISMS actually protects information, "
           "namely management commitment, competent auditors, appropriate risk appetite and organisational "
           "discipline, are outside the artefact entirely. A tool that made audit records complete while "
           "the underlying controls remained ineffective would have achieved nothing of substance.")

    r.section("6.3", "Strengths")
    r.body("Six strengths emerged from the work, and each is supported by evidence in this report rather "
           "than asserted.")
    r.bullets([
        "A complete and machine-readable traceability chain. The schema carries an audit from scope to "
        "signed report without a break, and the relationships are queryable rather than implicit "
        "(Section 4.3, Figures 4.2 and 4.4).",
        "A security baseline that is proportionate and verified. Eight controls address the failure modes "
        "most common in small-team tooling, and each is bound to an automated test written alongside the "
        "implementation (Section 4.5, Table 7).",
        "Genuine single-source domain logic across two interfaces. The React client and the Streamlit "
        "workbench share one core, which demonstrates that the architecture separates domain rules from "
        "presentation rather than claiming to (Figure 4.1).",
        "Deliverables derived rather than authored. PDF, Excel, JSON and CSV outputs are generated from the "
        "same records, so a report cannot silently disagree with the register it describes "
        "(Figure 4.8).",
        "Structural separation of demonstration and user data. The record-type marker, filtered views, "
        "scoped purge and non-destructive restore make accidental contamination of user data unlikely, and "
        "the persistent interface banner prevents misreading (Section 4.7).",
        "Honest reporting of boundaries. The report states which capabilities are unimplemented, "
        "distinguishes tamper evidence from immutability, and refuses to present demonstration data as "
        "evidence. In an academic artefact this is a substantive contribution to its credibility.",
    ])

    r.section("6.4", "Weaknesses and Residual Risks")
    r.body("Seven weaknesses and residual risks were identified. They are stated with the mitigation that an "
           "adopting organisation would require, because a limitation without a mitigation is only half a "
           "finding.")
    r.table(["Weakness or risk", "Why it matters", "Mitigation required before operational use"],
            [["Single-file SQLite persistence",
              "No concurrency control across sites, no high availability, backup window depends on file "
              "copy.",
              "Deploy against a managed relational database or a replicated volume; schedule verified "
              "backups with tested restore."],
             ["Local identity only",
              "Provisioning and deprovisioning are manual, so a leaver may retain access; no second factor.",
              "Integrate a directory or identity provider; add multifactor authentication for "
              "privileged roles."],
             ["No application-level encryption at rest",
              "Record and evidence confidentiality depends entirely on host and storage controls.",
              "Encrypt the volume or database; define key management and rotation; classify data before "
              "storage."],
             ["Tamper evidence is not immutability",
              "An attacker with write access could recompute the hash chain; an administrator could delete "
              "the database.",
              "Ship log entries and digests to an append-only external store; restrict filesystem access; "
              "retain periodic digest snapshots off-host."],
             ["Lockout does not stop distributed guessing",
              "Spraying across many accounts with a small number of attempts each evades per-account "
              "lockout.",
              "Add per-address rate limiting and anomaly detection; alert on distributed failure patterns."],
             ["Evidence authenticity and completeness are out of scope",
              "A digest proves the bytes did not change, not that the artefact is genuine or the sample "
              "adequate.",
              "Define collection procedures and custody records; require independent review of sampling."],
             ["Demonstration deployment is ephemeral",
              "Runtime writes on the serverless deployment do not persist across cold starts.",
              "Use a persistent volume or managed database for any instance intended as a system of record."]],
            "Weaknesses, residual risks and required mitigations.", widths=[1.45, 2.2, 2.35], font_size=9)
    r.para("One further weakness concerns the tool rather than the platform. Compliance scoring derived from "
           "test outcomes is easy to misread, and can be improved cosmetically by reclassifying tests as not "
           "applicable. The interface mitigates this by always showing the count of tests behind the score, "
           "and the documentation states that the figure is an indicator of testing progress rather than a "
           "measure of security. An organisation could still misuse it, which is why the mitigation is "
           "procedural as much as technical.")

    r.section("6.5", "Implications")
    r.body("Four sets of implications follow, addressed to the audiences for whom this report is written.")
    r.para("For students and small audit teams, the practical implication is that a modest, well-structured "
           "tool removes a specific and expensive class of effort: reconstructing the relationship between "
           "a finding, its evidence and its remediation. That reconstruction is where spreadsheet practice "
           "consumes time, and it is addressable with a normalised schema and a consistent interface. The "
           "project also demonstrates that security engineering does not require an enterprise budget; it "
           "requires choosing the right primitives and binding each claim to a test.")
    r.para("For audit practitioners, the implication is that automation accelerates formatting and does not "
           "validate judgement. A generated report is only as defensible as the records behind it, and the "
           "platform makes those records visible precisely so that a reviewer can challenge them. The most "
           "useful feature for a practitioner may be the one that makes weakness obvious: a workpaper with "
           "a small sample size and a single evidence reference is visibly thin in a way that the same "
           "claim buried in a document is not.")
    r.para("For information security leaders, the prototype is best used as a requirements discussion aid "
           "rather than a system of record. It makes concrete the questions that an ISMS tooling decision "
           "must answer: where evidence lives, who can approve a report, what happens when an artefact "
           "changes, how long records are kept, and how access is withdrawn. Those questions are better "
           "answered before procurement than after.")
    r.para("For academic reviewers, the implication concerns method. Distinguishing implementation "
           "observations from demonstration data and from future work is what makes an artefact study "
           "reproducible and credible, and generating figures from the artefact rather than from "
           "screenshots removes the most common source of drift between a report and its implementation.")


def ch7(r: Report):
    r.chapter(7, "Conclusion And Recommendations")

    r.section("7.1", "Conclusion", first=True)
    r.body("This project set out to determine whether a single normalised data model could carry an "
           "ISO/IEC 27001 internal audit from scope definition through control testing, evidence capture, "
           "findings management, corrective action tracking and report sign-off without loss of "
           "traceability, and whether the assurance properties such a system needs could be implemented "
           "proportionately and verified automatically. The answer to both questions is yes, within stated "
           "boundaries.")
    r.para("The artefact delivered is a three-tier platform consisting of a React and TypeScript "
           "single-page application, a FastAPI REST service exposing twenty-seven endpoints, an eight-page "
           "Streamlit governance workbench, and a shared Python core over a twelve-table SQLite schema. It "
           "is deployed publicly and can be inspected without local installation. The seven-stage "
           "traceability model is realised in the schema, and every stage writes a record that references "
           "the stage before it.")
    r.para("The eight security and assurance controls that the earlier iteration of this artefact could only "
           "propose are now implemented. Passwords are derived with scrypt using per-user salts; sessions "
           "are carried by HMAC-SHA256 signed tokens that survive serverless cold starts; five consecutive "
           "failed attempts lock an account for fifteen minutes; twelve capabilities across four roles are "
           "enforced at the API boundary rather than only in the interface; evidence carries a SHA-256 "
           "digest and byte count that is re-verified before download; reports move through a four-state "
           "approval workflow with version and approver recorded; every mutation appends to a "
           "genesis-anchored SHA-256 chain whose validity is exposed live; and JSON backups embed a manifest "
           "that verifies before restoration. All five automated test groups pass, including the negative "
           "assertions that prove authorisation boundaries and integrity checks actually refuse what they "
           "should refuse.")
    r.para("The project does not demonstrate conformity to ISO/IEC 27001, certification readiness, "
           "operational effectiveness, or measurable improvement in audit outcomes. It does not address "
           "enterprise identity, encryption at rest, retention policy or multi-site concurrency. Those "
           "omissions are stated in Chapter 6 as weaknesses with required mitigations rather than left for a "
           "reader to discover, which is the appropriate posture for an artefact that claims to support "
           "evidential work.")

    r.section("7.2", "Recommendations")
    r.body("Eight recommendations follow, ordered by the ratio of assurance gained to effort required. Each "
           "carries an explicit completion test, because a recommendation without a verification criterion "
           "tends not to be completed.")
    r.table(["Priority", "Recommendation", "Completion criterion"],
            [["1", "Replace the demonstration deployment's ephemeral storage with a persistent volume or a "
                  "managed database, and schedule automated backups.",
              "A record written in the interface survives a cold start; a scheduled backup restores into a "
              "clean environment with matching digests."],
             ["2", "Integrate an identity provider and add multifactor authentication for privileged roles, "
                  "retaining local roles as an authorisation layer.",
              "Sign-in through the provider issues a session; a user disabled in the directory loses access "
              "without manual intervention; an Admin sign-in requires a second factor."],
             ["3", "Add per-address rate limiting and distributed-guessing detection alongside the existing "
                  "per-account lockout.",
              "A scripted spray across many usernames is throttled and generates an alert; the legitimate "
              "user experience is unaffected."],
             ["4", "Encrypt the database and evidence store at rest and define key management, rotation and "
                  "escrow.",
              "Files on disk are unreadable without the key; rotation succeeds without data loss; key "
              "custody is documented."],
             ["5", "Ship the audit-chain head digest to an append-only external store on a schedule, so that "
                  "chain recomputation by an attacker is detectable.",
              "A deliberately recomputed local chain is detected by comparison against the external "
              "anchors."],
             ["6", "Implement retention, legal hold and secure deletion with an auditable policy engine.",
              "A record past its retention period is deleted or held according to policy; every deletion is "
              "logged in the chain."],
             ["7", "Extend the automated suite and add continuous integration so that the negative tests run "
                  "on every change rather than on demand.",
              "A deliberately introduced authorisation regression fails the pipeline before merge."],
             ["8", "Add accessibility and usability evaluation with real auditors, including keyboard "
                  "navigation and screen-reader review of the dense data tables.",
              "Documented evaluation against an accessibility standard, with defects raised and closed."]],
            "Prioritised recommendations and completion criteria.", widths=[0.6, 2.7, 2.7], font_size=9)
    r.para("Recommendations one to three address the constraints that most directly prevent operational "
           "adoption, and each is small in engineering terms relative to its effect. Recommendations four "
           "and five address confidentiality and tamper evidence, which are the two properties most often "
           "assumed and least often verified in small-team tooling. Recommendations six to eight address the "
           "gaps that become material once the system holds real records rather than demonstration data.")

    r.section("7.3", "Practical Implications for Deployment")
    r.body("Any organisation contemplating operational use should complete a defined sequence of steps "
           "before the platform holds a single real record. The sequence below is ordered so that decisions "
           "precede configuration.")
    r.numbered([
        "Define the ISMS scope, the audit programme and the record retention obligations, because these "
        "determine what the system must be able to store and for how long.",
        "Classify the data that will be held, including evidence artefacts, and confirm that the chosen "
        "hosting arrangement satisfies the resulting confidentiality and residency requirements.",
        "Define roles and approve the permission matrix, noting that the shipped roles are a starting point "
        "rather than a finished model for any particular organisation.",
        "Complete a threat model covering the evidence store, the database, the audit chain, the deployment "
        "pipeline and administrative access.",
        "Deploy against persistent storage, enable encryption at rest, restrict filesystem access and "
        "configure verified backups with a tested restore.",
        "Integrate identity and add multifactor authentication for every role that can approve a report or "
        "provision a user.",
        "Replace demonstration data with a controlled initial population, and retain the demonstration purge "
        "as a safety mechanism rather than as a routine operation.",
        "Obtain approval from the accountable security, privacy, legal and internal audit stakeholders, and "
        "document the operating procedures that govern evidence collection and custody.",
        "Run a supervised pilot with a single audit before general adoption, and record the findings as the "
        "basis for the first revision of the operating procedures.",
    ])
    r.para("One point deserves restating in the deployment context. The platform's integrity features raise "
           "the cost of undetected alteration and do not prevent alteration by someone with sufficient "
           "access. An organisation that adopts the tool without addressing administrative access, "
           "off-host anchoring of the chain head and evidence custody procedures would have purchased an "
           "appearance of integrity rather than its substance.")


def ch8(r: Report):
    r.chapter(8, "Limitations And Future Research")

    r.section("8.1", "Limitations", first=True)
    r.body("The following limitations apply to the study and to the claims made in this report. They are "
           "stated in full because the credibility of an artefact study depends on the reader knowing "
           "exactly where its evidence stops.")
    r.bullets([
        "Evaluation was confined to the submitted source, the seeded dataset and the deployed instance. "
        "Behaviour under a different configuration, dataset size or load profile is not characterised.",
        "No organisation, external auditor or end user participated. No usability evaluation, task "
        "measurement or satisfaction survey was conducted.",
        "The automated suite was written by the same author as the implementation. It provides regression "
        "safety and demonstrates intended behaviour; it is not an independent security assessment and it "
        "does not demonstrate the absence of exploitable defects.",
        "The interface plates are produced by a deterministic renderer reading the database, not by a "
        "browser capture. They reproduce content and layout faithfully but do not evidence the rendering "
        "behaviour of the React components in different browsers.",
        "The demonstration dataset is fictional. No statistical inference is drawn from it and no "
        "performance claim rests on it.",
        "Feature status reflects the submitted revision and is time-bounded. A later revision will need a "
        "re-verification pass before this report's status table can be relied upon.",
        "Persistence is a single SQLite file, so conclusions about concurrency and availability do not "
        "transfer to a multi-user or cloud-native deployment.",
        "The ISO/IEC 27001, ISO 19011, NIST CSF 2.0 and SOC 2 content included in the platform and in this "
        "report is a navigational aid. It is not a substitute for licensed standards, authoritative legal "
        "requirements or qualified professional interpretation.",
    ])

    r.section("8.2", "Future Research")
    r.body("Six directions would extend this work in ways that produce genuinely new evidence rather than "
           "additional features.")
    r.bullets([
        "A controlled comparison against a documented spreadsheet baseline, using identical synthetic audit "
        "tasks and predefined measures of completion time, evidence linkage completeness and review effort. "
        "This is the study most likely to produce a defensible outcome claim.",
        "A supervised usability study with practising auditors and an ethics-approved protocol, measuring "
        "task success, error rate and time on task for the highest-frequency operations.",
        "An adversarial security assessment in an isolated environment, covering the evidence store, the "
        "token implementation, the audit chain and the authorisation boundary, with findings triaged by "
        "severity.",
        "A multi-user architecture study comparing a managed relational database against the single-file "
        "design on concurrency, migration cost and operational burden at realistic record volumes.",
        "An adoption study across small and medium organisations using a declared sampling frame and a "
        "validated instrument, to establish which record-keeping problems are actually felt rather than "
        "assumed.",
        "A longitudinal pilot examining whether the structured approval workflow and overdue-action "
        "visibility change review completeness or remediation timeliness over several audit cycles.",
    ])
    r.para("Each of these would require resources or access that were unavailable for a single-semester "
           "project. Naming them precisely is more useful than a general observation that further work is "
           "needed, because each implies a specific design, population and measure that a subsequent "
           "student could adopt directly.")

    r.section("8.3", "Concluding Note")
    r.body("This report has described an artefact, the reasoning behind its design, the evidence that it "
           "operates as intended, and the boundaries within which that evidence holds. The platform is "
           "available for inspection at its public deployment and its source, schema and test suite are "
           "submitted alongside this document. A reader who wishes to challenge any claim in these pages is "
           "invited to do so by running the suite, querying the database or reading the modules cited in "
           "each chapter.")
    r.para("The broader lesson, consistent with the literature reviewed in Chapter 2, is that tooling can "
           "make an audit process visible and consistent but cannot make it competent. The value of a "
           "system like SecureAudit is that it makes the difference between a well-evidenced conclusion and "
           "an asserted one visible to everyone who reads the record. That visibility is a modest "
           "contribution, and it is the one this project is entitled to claim.")
