"""Chapters 4-5: System Analysis and Implementation, Results and Analysis."""
from docx_base import Report

def ch4(r: Report):
    r.chapter(4, "System Analysis and Implementation")

    r.section("4.1", "System Overview", first=True)
    r.body("SecureAudit is organised as a three-tier system in which a single domain core serves two "
           "independent presentation layers. The presentation tier comprises a React and TypeScript "
           "single-page application built with Vite and a Tailwind-based design system, together with an "
           "eight-page Streamlit governance workbench. The application tier comprises a FastAPI REST "
           "service exposing twenty-seven endpoints and a shared Python package that owns all domain "
           "logic. The data tier comprises a SQLite database of twelve tables and a controlled evidence "
           "store on the filesystem.")
    r.para("The architectural decision that matters most is that the presentation layers contain no domain "
           "logic. Neither the React client nor the Streamlit pages construct SQL, calculate compliance "
           "scores or derive permissions; both call the same core functions. This is what allows two "
           "materially different interfaces to remain consistent without duplicated rules, and it is why "
           "a defect fixed in the core is fixed in both.")
    r.para("The deployment topology is unusual for an academic artefact and deliberately so. The public "
           "instance is deployed to Vercel as a combined build: the React bundle is emitted as static "
           "assets, and the FastAPI application is deployed as a Python serverless function reachable "
           "under the /api path prefix. Because the serverless filesystem is read-only apart from the "
           "temporary directory, the deployment maps the database and the evidence store into a "
           "temporary runtime path. The consequence is that demonstration data may reset between cold "
           "starts, which is acceptable for an evaluation environment but is discussed as a limitation "
           "in Chapter 7.")
    r.figure("docs/report/figures/figure-3-1-architecture.png",
             "SecureAudit ISMS three-tier architecture. The shared core package is the single point of "
             "domain logic for both interfaces, which prevents divergence between the React client and "
             "the Streamlit workbench.", width_in=6.0)

    r.section("4.2", "User Roles and Access Model")
    r.body("The access model defines four roles and a flat permission set of twelve capabilities. "
           "Permissions are declared in the security module as data rather than scattered through route "
           "handlers, so that the complete authority of a role can be read in one place and audited "
           "without tracing call graphs.")
    r.table(["Capability", "Admin", "Auditor", "Risk Owner", "Viewer"],
            [["View registers, dashboards and reports", "Yes", "Yes", "Yes", "Yes"],
             ["Export reports and download deliverables", "Yes", "Yes", "Yes", "Yes"],
             ["Create and edit audits and test workpapers", "Yes", "Yes", "No", "No"],
             ["Manage control register and Statement of Applicability", "Yes", "Yes", "No", "No"],
             ["Manage findings", "Yes", "Yes", "No", "No"],
             ["Manage risk register", "Yes", "No", "Yes", "No"],
             ["Create and update corrective actions", "Yes", "Yes", "Yes", "No"],
             ["Upload and verify evidence", "Yes", "Yes", "Yes", "No"],
             ["Verify audit log chain", "Yes", "Yes", "No", "No"],
             ["Approve or reject a report", "Yes", "No", "No", "No"],
             ["Provision users and unlock accounts", "Yes", "No", "No", "No"],
             ["Remove or restore demonstration records", "Yes", "No", "No", "No"]],
            "User roles, permissions and enforcement points. Permissions are enforced identically in the "
            "REST service and in the Streamlit workbench because both call the same permission function.",
            widths=[2.6, 0.6, 0.7, 0.85, 0.65], font_size=9.5)
    r.para("Three properties of the model deserve comment. First, the roles are application roles, not "
           "enterprise identities; there is no integration with a directory service, so provisioning is "
           "manual and deprovisioning is manual, which is a real operational weakness for an adopting "
           "organisation. Second, the Risk Owner role is intentionally narrower than Auditor: a risk "
           "owner may manage risks and their own actions but may not test controls, which preserves the "
           "separation between the person accountable for a control and the person assessing it. Third, "
           "report approval is restricted to Admin, which implements the reviewer-versus-preparer "
           "separation required for a meaningful sign-off.")
    r.para("Enforcement occurs at the API boundary rather than only in the interface. Each mutating "
           "endpoint declares a dependency that resolves the caller's identity from the bearer token and "
           "checks the required capability before the handler executes. Interface-level hiding is treated "
           "as a usability measure, not a security control, because a client can always call the API "
           "directly.")

    r.section("4.3", "Data Model and Record Traceability")
    r.body("The schema comprises twelve tables. Design followed three rules: every record carries a stable "
           "human-readable identifier so that it can be cited in a report; every relationship is "
           "expressed as an identifier reference rather than as a duplicated label; and every table that "
           "holds assertions carries a record-type marker that distinguishes seeded demonstration data "
           "from user-entered data.")
    r.figure("docs/report/figures/figure-4-2-er-model.png",
             "Entity relationship model of the ISMS schema. Arrows show the traceability path from audit "
             "through tests and findings to actions; evidence records attach to any entity by type and "
             "identifier, which is what allows one vault to serve every stage of the audit.",
             width_in=6.0)
    r.table(["Table", "Purpose", "Key relationships"],
            [["users", "Accounts, salted scrypt derived keys, role assignment, lockout state.",
              "Referenced by sessions and by every audit-log entry as actor."],
             ["sessions", "Issued bearer tokens with issue and expiry timestamps.",
              "References users; supplemented by stateless signed tokens so that a cold start does not "
              "invalidate a live session."],
             ["audits", "Audit container: scope, objectives, criteria, team, dates, status, compliance "
                        "score, approval state and report version.",
              "Parent of tests and findings."],
             ["tests", "Control test workpapers: procedure, sample size, result, notes, evidence "
                       "reference, tester and date.",
              "References audits and controls; parent of evidence links."],
             ["findings", "Nonconformities with criteria, condition, cause, impact, recommendation, "
                          "severity, status and owner.",
              "References audits and controls; parent of actions."],
             ["actions", "Corrective and preventive actions with owner, due date, status and verification "
                         "notes.",
              "References findings."],
             ["controls", "Forty Annex A reference controls with domain, applicability, justification, "
                          "implementation status, owner and illustrative cross-framework mappings.",
              "Referenced by tests, findings and risks."],
             ["risks", "Risk register with threat, likelihood, impact, inherent score, treatment, linked "
                       "controls and residual score.",
              "References controls."],
             ["requirements", "Clause-level and regulatory reference entries used for navigation.",
              "Standalone reference data."],
             ["evidence", "Evidence artefacts with file name, storage path, media type, byte size, "
                          "SHA-256 digest, uploader, timestamp and verification status.",
              "Attaches to any entity by entity type and identifier."],
             ["audit_logs", "Append-only activity log where each entry records the previous entry's "
                            "digest and its own digest.",
              "References users as actor; self-referential chain."],
             ["meta_state", "Key-value store for schema version and seed state.",
              "Standalone."]],
            "Database schema summary.", widths=[1.2, 2.7, 2.1], font_size=9)
    r.para("Traceability is not merely declared but queryable. Given a finding identifier, the database "
           "yields the audit it belongs to, the control it concerns, the corrective actions raised "
           "against it and any evidence attached to it; from the audit, the complete set of test "
           "workpapers and the report approval state follow. This is the property that makes the record "
           "set reconstructible by a third party and is the structural answer to RQ1.")
    r.para("Two design decisions require justification. Evidence is attached polymorphically, by entity "
           "type and entity identifier, rather than by a foreign key per consumer table. This keeps one "
           "vault serving audits, tests, findings and actions without schema proliferation, at the cost of "
           "referential integrity being enforced in application logic rather than by the database. And "
           "the compliance score on the audit row is derived data, recomputed on every test update rather "
           "than entered by hand, which prevents the score and the underlying tests from disagreeing.")

    r.section("4.4", "Functional Requirements and Implementation Status")
    r.body("The functional requirements were derived from the workflow traceability model in Section 2.5 "
           "and validated against the standards review. Status is reported using the vocabulary defined "
           "in Section 3.6 and reflects the submitted revision.")
    r.table(["Requirement", "Implementation", "Status"],
            [["Audit planning with scope, objectives, criteria, team and dates",
              "Audit register, API create and delete endpoints, detail view with scope and objective panels.",
              "Implemented"],
             ["Control catalogue and Statement of Applicability",
              "Forty Annex A controls across four themes, sixteen clause entries, applicability decision, "
              "justification, implementation status and owner per control.",
              "Implemented"],
             ["Control test workpapers with procedure, sample and result",
              "Test register with automatic compliance recalculation on every update.",
              "Implemented"],
             ["Findings with structured nonconformity narrative",
              "Criteria, condition, cause, impact, recommendation, severity, owner and status.",
              "Implemented"],
             ["Corrective and preventive action tracking",
              "Action register with owner, due date, status, verification note and evidence note.",
              "Implemented"],
             ["Risk register with scoring and treatment",
              "Five-by-five likelihood and impact scoring, inherent and residual scores, treatment and "
              "linked controls.",
              "Implemented"],
             ["Evidence capture with integrity verification",
              "SHA-256 digest and byte size at upload, twenty megabyte cap, media-type and extension "
              "allowlist, re-verification before download with a conflict response on mismatch.",
              "Implemented"],
             ["Tamper-evident activity log",
              "Append-only log chained by SHA-256 with a live verification endpoint and interface status "
              "indicator.", "Implemented"],
             ["Role-based access control",
              "Twelve capabilities across four roles, enforced at the API boundary and in both interfaces.",
              "Implemented"],
             ["Authentication hardening",
              "scrypt key derivation with per-user salt, five-attempt fifteen-minute lockout, constant-time "
              "comparison, stateless HMAC-signed bearer tokens.", "Implemented"],
             ["Report review and approval workflow",
              "Four states with version, reviewer identity, timestamp and notes; approval restricted to "
              "Admin.", "Implemented"],
             ["PDF, Excel, JSON and CSV deliverables",
              "Server-generated PDF audit report, nine-sheet Excel workbook, manifest-verified JSON backup "
              "and append-only CSV import.", "Implemented"],
             ["Demonstration data separation",
              "Record-type marker on seeded rows, toggle in the interface, purge and restore operations.",
              "Implemented"],
             ["Automated regression suite",
              "Five test groups covering health, authentication and lockout, authorisation boundaries, "
              "evidence integrity and exports.", "Implemented"],
             ["Enterprise identity federation and multi-factor authentication",
              "No directory integration or second factor; provisioning and deprovisioning are manual.",
              "Not implemented"],
             ["Encryption at rest for the database and evidence store",
              "Relies on operating-system or platform-level disk encryption; the application does not "
              "encrypt records.", "Not implemented"],
             ["Multi-user concurrency and high availability",
              "Single-file SQLite; suitable for a small team on one host, not for concurrent multi-site "
              "operation.", "Partially implemented"],
             ["Retention, legal hold and secure deletion",
              "No retention policy engine; deletion is manual.", "Not implemented"]],
            "Functional requirements and implementation status.", widths=[2.0, 3.15, 0.85], font_size=9)

    r.section("4.5", "Security and Assurance Controls")
    r.body("Eight controls constitute the assurance baseline of the platform. All eight were identified as "
           "gaps or proposals in the earlier iteration of this artefact; all eight are implemented in the "
           "current revision and each is bound to an automated test so that the claim and its evidence "
           "were produced together.")
    r.figure("docs/report/figures/figure-4-1-workflow.png",
             "Seven-stage audit traceability model. Each stage writes a record carrying the identifier of "
             "the stage before it, and every mutation is appended to the hash chain.",
             width_in=6.0)
    r.subsection("4.5.1", "Password Derivation")
    r.body("Passwords are never stored or compared directly. At provisioning, a sixteen-byte random salt is "
           "generated and the password is derived using scrypt with parameters N equal to 16,384, r equal "
           "to 8, p equal to 1 and a derived key length of 64 bytes. The derived key and the salt are "
           "stored; the password is discarded. Verification re-derives with the stored salt and compares "
           "using a constant-time function. scrypt is memory-hard, which raises the cost of offline "
           "guessing on a stolen database substantially relative to a general-purpose hash, and the "
           "per-user salt prevents precomputation and cross-account comparison.")
    r.subsection("4.5.2", "Account Lockout")
    r.body("Failed authentication attempts are counted per account. On the fifth consecutive failure the "
           "account is locked for fifteen minutes and authentication returns a locked response rather "
           "than an authentication failure, so that a legitimate user receives an accurate message. "
           "Administrators can release a lock early. The counter resets on successful authentication. This "
           "control addresses online guessing against a known username; it does not address distributed "
           "spraying across many usernames, which is noted as a residual risk.")
    r.subsection("4.5.3", "Session Tokens")
    r.body("Authentication returns a bearer token whose payload is signed with an HMAC-SHA256 key held by "
           "the server. Because the token is verifiable without a database lookup, a live session survives "
           "a serverless cold start or a request routed to a different instance, which a purely "
           "database-backed session table cannot guarantee on that platform. Session rows are still "
           "written for auditability and for explicit revocation. Tokens carry issue and expiry "
           "timestamps and are rejected when the signature or the expiry check fails.")
    r.subsection("4.5.4", "Role-Based Access Control")
    r.body("Authorisation is centralised as a permission map from role to capability set, and every "
           "mutating endpoint declares the capability it requires. Because the check happens before the "
           "handler runs, a caller who bypasses the interface and calls the endpoint directly receives the "
           "same refusal. The automated suite includes a dedicated group of tests that authenticates as "
           "each role and asserts both the permitted and the refused operation, so that a future change "
           "that silently widens a role fails the suite.")
    r.subsection("4.5.5", "Evidence Integrity")
    r.body("At upload the service validates size against a twenty megabyte cap, validates the extension "
           "against an allowlist, normalises and validates the media type, computes the SHA-256 digest of "
           "the stored bytes and records the digest together with the exact byte count. Before download "
           "the service recomputes the digest from disk and compares it with the recorded value; a "
           "mismatch blocks the download and returns a conflict response, and the interface surfaces the "
           "verification status per artefact. Filenames are sanitised before storage to prevent path "
           "traversal. The claim supported here is narrow and is stated narrowly: the bytes served are the "
           "bytes captured.")
    r.subsection("4.5.6", "Report Approval Workflow")
    r.body("Each audit carries a report state of Draft, In Review, Changes Requested or Approved, together "
           "with a report version, the approving identity, the approval timestamp and approval notes. "
           "Only the Admin role may transition a report to Approved. The workflow separates preparation "
           "from sign-off, which is the property that makes a signature meaningful, and it preserves the "
           "version that was signed so that a later edit cannot silently inherit an earlier approval.")
    r.subsection("4.5.7", "Tamper-Evident Audit Trail")
    r.body("Every authentication, record mutation, evidence operation and approval appends an entry to a "
           "log table. Each entry records the digest of the previous entry and its own digest, computed "
           "over the entry content together with the previous digest, with the first entry chained to a "
           "fixed genesis value. A verification function recomputes the chain and reports validity, the "
           "number of entries checked and the head digest; this is exposed through an API endpoint and "
           "surfaced in the interface. Editing any historical entry invalidates every subsequent entry, "
           "so alteration is detectable rather than prevented.")
    r.subsection("4.5.8", "Verified Backup and Export")
    r.body("The JSON backup embeds a canonical manifest digest over the exported records. A dry-run "
           "verification endpoint recomputes the digest from a submitted payload and reports whether the "
           "payload is intact before any restoration is attempted, and the automated suite asserts that a "
           "backup produced by the system verifies under its own manifest. PDF audit reports and the "
           "nine-sheet Excel workbook are generated from the same records, so a report cannot assert a "
           "figure that the database does not contain.")
    r.table(["Control", "Mechanism", "Verification"],
            [["Password derivation", "scrypt, N=16,384, r=8, p=1, 64-byte key, 16-byte random salt, "
                                     "constant-time comparison", "Authentication test group"],
             ["Account lockout", "Five consecutive failures trigger a fifteen-minute lock; "
                                 "administrative release available", "Authentication test group"],
             ["Session integrity", "HMAC-SHA256 signed bearer token with issue and expiry, plus a session "
                                   "row for revocation", "Authentication and authorisation groups"],
             ["Authorisation", "Twelve capabilities across four roles, checked at the API boundary before "
                               "the handler executes", "Authorisation test group"],
             ["Evidence integrity", "SHA-256 digest and byte count at upload; twenty megabyte cap; media "
                                    "and extension allowlist; digest re-verified before download",
              "Evidence test group"],
             ["Report approval", "Draft, In Review, Changes Requested, Approved; version, reviewer, "
                                 "timestamp; Admin-only sign-off", "Export and approval assertions"],
             ["Audit trail", "Append-only chain of SHA-256 digests, genesis-anchored, with a live "
                             "verification endpoint", "Health and chain verification assertions"],
             ["Backup verification", "Canonical SHA-256 manifest embedded in the JSON export with a "
                                     "dry-run verification endpoint", "Export test group"]],
            "Implemented security and assurance controls.", widths=[1.3, 3.35, 1.35], font_size=9)

    r.section("4.6", "Interface Implementation")
    r.body("The React client is a single-page application with ten domain views behind a shared navigation "
           "shell: a public landing page, role sign-in, an executive dashboard, the audit projects list, a "
           "new-audit wizard, an audit detail view with test workpapers, a findings and CAPA view, an Annex "
           "A and Statement of Applicability view, a risk and frameworks view, an evidence vault, a reports "
           "centre, user management and a settings and logs view.")
    r.para("The interface follows an explicit design system rather than ad hoc styling: a defined "
           "typographic scale, a tokenised colour set with semantic roles for success, warning, error and "
           "information, a consistent eight-point spacing rhythm and a single corner-radius convention. "
           "The practical reason is not decoration. Audit users read the same table structures repeatedly "
           "and compare statuses constantly, so a consistent visual grammar for severity, status and "
           "verification reduces reading errors. The same reasoning governs the deliberate use of colour "
           "reinforcement alongside text labels for severity, rather than colour alone.")
    r.para("The interface captures reproduced in Chapter 5 were taken from the running build rather than "
           "drawn by hand or mocked up. A scripted headless-browser session signs in through the ordinary "
           "form, traverses each domain view and captures the rendered screen at twice the logical "
           "resolution, so the values shown are the values the live endpoints returned. This replaces the "
           "practice of presenting illustrations that could not be tied to the implementation: every audit "
           "title, compliance percentage, finding severity, digest prefix and chain length visible in the "
           "figures is a record described elsewhere in this report.")

    r.section("4.7", "Demonstration Data and Separation")
    r.body("The seeded dataset exists so that the workflow can be evaluated without an organisation first "
           "entering real records. It comprises four audits, twenty control test workpapers, eight findings "
           "across all four severity levels, seven corrective actions, forty Annex A controls, five risks "
           "and four evidence artefacts with genuine digests over generated files.")
    r.para("Separation between demonstration and user data is enforced structurally rather than by "
           "convention. Every seeded row carries a record-type marker, the interface exposes a toggle that "
           "filters on that marker, an administrative purge removes only marked rows, and a restore "
           "operation reinserts any marked rows that are missing without touching user-entered records. The "
           "interface displays a persistent warning banner whenever demonstration records are visible, so "
           "that a reader cannot mistake the content for organisational evidence.")


def ch5(r: Report):
    r.chapter(5, "Results and Analysis")

    r.section("5.1", "Verification Results", first=True)
    r.body("Results are presented from three independent sources in the order in which they were "
           "collected: the automated verification suite, the live deployment, and the rendered interface. "
           "Presenting them separately matters because each supports a different class of claim, and no "
           "single source is sufficient on its own.")

    r.subsection("5.1.1", "Automated Verification Suite")
    r.body("The suite is organised into five test groups, each targeting one cluster of claims rather than "
           "one module. All five groups passed in the recorded run, with a single third-party deprecation "
           "warning unrelated to application behaviour.")
    r.table(["Test group", "What it asserts", "Result"],
            [["Health and initial seeding",
              "The service starts, ensures schema initialisation, seeds demonstration records exactly once, "
              "and reports a valid audit-log chain on the health endpoint.", "Passed"],
             ["scrypt authentication and lockout",
              "A correct credential yields a token; an incorrect credential is refused; five consecutive "
              "failures lock the account; a locked account is refused even with the correct credential; an "
              "administrative release restores access.", "Passed"],
             ["Role-based authorisation boundaries",
              "Viewer is refused every mutating operation while retaining read access; Auditor may create "
              "audits and findings but may not approve a report or provision a user; Risk Owner may manage "
              "risks but may not create audits; Admin is permitted everywhere.",
              "Passed"],
             ["Evidence SHA-256 upload and verification",
              "An accepted upload records the digest and byte count and verifies on demand; an oversized "
              "file is refused; a disallowed extension is refused; a modified file is detected as a hash "
              "mismatch and the download is blocked.", "Passed"],
             ["PDF, Excel and backup exports",
              "A PDF audit report is produced with the expected section structure; a nine-sheet workbook "
              "is produced with the expected sheet names; a JSON backup carries a manifest digest that "
              "verifies against its own payload.", "Passed"]],
            "Automated test suite coverage.", widths=[1.5, 3.75, 0.75], font_size=9)
    r.para("The significance of the third group deserves emphasis. A test that asserts a refusal is the only "
           "kind of test that can detect privilege escalation introduced by a later change. Positive tests "
           "alone, which confirm that an administrator can perform an action, would pass identically "
           "against a system with no authorisation at all. The suite therefore asserts both directions for "
           "each role boundary.")

    r.subsection("5.1.2", "Live Deployment Verification")
    r.body("The platform is deployed publicly and was verified by direct request against the production URL "
           "rather than by proxy or local instance. The checks exercise the same code paths a reviewer "
           "would use.")
    r.table(["Check", "Observation", "Interpretation"],
            [["Application shell", "The single-page application responds and renders the dashboard bound to "
                                   "live API data.", "Front-end build and API routing are correctly "
                                   "configured in production."],
             ["Health endpoint", "Returns an OK status with a valid audit-chain assertion and an entry "
                                 "count.", "Schema initialisation and chain verification execute on a cold "
                                 "serverless instance."],
             ["Workspace payload", "Returns the complete seeded record set across audits, tests, findings, "
                                   "actions, controls, risks and evidence.", "The relational read path is "
                                   "exercised end to end, not merely a cached fixture."],
             ["PDF audit report", "Generates and serves a multi-page report on demand for a specified audit.",
              "Report generation works in the serverless runtime, including font and library "
              "availability."],
             ["Excel workbook", "Generates and serves the nine-sheet workbook on demand.",
              "Workbook generation works in the serverless runtime."],
             ["OpenAPI document", "Serves the interactive specification listing all twenty-seven endpoints "
                                  "under the API prefix.", "The full contract is discoverable in production, "
                                  "which supports third-party verification."],
             ["Demo account listing", "Returns the four demonstration identities with their roles.",
              "Seeded identity provisioning is intact after deployment."]],
            "Live deployment verification results.", widths=[1.15, 2.85, 2.0], font_size=9)
    r.para("One behaviour observed during verification is worth recording because it is a genuine "
           "deployment property rather than a defect. Because the platform runs as a serverless function "
           "with a temporary filesystem, records written at runtime do not necessarily persist across cold "
           "starts; the seeded dataset is re-created on initialisation. For an evaluation deployment this "
           "is acceptable, and it has the useful side effect of keeping the public instance in a known "
           "state. For any operational use it would be disqualifying, and Chapter 7 treats persistence "
           "accordingly.")

    r.subsection("5.1.3", "Screen Captures of the Deployed Interface")
    r.body("The twelve figures that follow are screen captures of the deployed application, taken from "
           "the running build against the seeded dataset. They are included for a specific reason. The "
           "earlier iteration of this artefact circulated mock-ups whose displayed values could not "
           "be reconciled with the submitted source, and screenshot drift of that kind is a credibility "
           "problem in an artefact study. Every value visible below therefore comes from the same "
           "records described in this report: the four audit identifiers, the compliance percentages "
           "recomputed from control tests, the eight seeded findings with their severities, the digest "
           "prefixes in the evidence vault and the head hash of the audit chain.")
    r.figure("docs/report/figures/figure-5-0-landing.png",
             "Public landing page of the deployed application. The overview describes the platform, "
             "states that all records are illustrative, and routes to the sign-in page, which is the "
             "single point of entry to the audit workspace.", width_in=6.0)
    r.figure("docs/report/figures/figure-5-11-login.png",
             "Role sign-in. Authentication is against a salted scrypt-derived secret, and the screen "
             "states the five-attempt lockout policy that governs failed authentication; no "
             "demonstration credentials are prefilled or displayed.", width_in=4.0)
    r.figure("docs/report/figures/figure-5-1-dashboard.png",
             "Executive security dashboard. Compliance percentages are recomputed from test results, "
             "the severity distribution counts the eight seeded findings, and the demonstration-data "
             "banner remains visible while seeded records are shown.", width_in=6.0)
    r.para("The dashboard illustrates one deliberate analytical choice. Each compliance figure is "
           "displayed together with the count of tests that produced it, the aggregated average is "
           "accompanied by the statement that it is based on ten of twenty control tests, and the score "
           "is never labelled as a security or assurance rating. A reader can therefore see the "
           "denominator, which is what distinguishes an indicator from a claim.")
    r.figure("docs/report/figures/figure-5-10-audits.png",
             "Audit projects register. Each card carries the audit identifier, the framework, a "
             "demonstration-data marker, the lead auditor, the derived compliance score and the current "
             "report sign-off state.", width_in=6.0)
    r.figure("docs/report/figures/figure-5-2-audit-detail.png",
             "Audit detail view with the control test workpapers for AUD-2026-001. Each workpaper "
             "records a control identifier, documented procedure, sample size, outcome, evidence "
             "reference and the quoted observation, with the approved report version shown in the "
             "header.", width_in=6.0)
    r.para("The audit detail view is the clearest demonstration of the traceability claim in RQ1. "
           "Reading down the workpaper list, each row carries a control identifier, a documented "
           "procedure, a sample size, an outcome and an evidence reference. Reading across to the "
           "header, the approved report version and the sign-off state are named. The whole audit is "
           "reconstructible from this single view without opening another document, which is precisely "
           "what fragmented spreadsheet practice cannot provide.")
    r.figure("docs/report/figures/figure-5-3-findings.png",
             "Findings and vulnerability register. Severity counts are aggregated at the top, and each "
             "finding below states its criterion, observed condition, owning individual, linked audit "
             "and control reference, and due date.", width_in=6.0)
    r.para("The findings view evidences the accountability construct. The substantive content is "
           "per-finding rather than aggregate: a control criterion, the observed condition, the owning "
           "individual, and both the audit and control identifiers. Because the corrective action "
           "records carry the finding identifier forward, a reader can move from a condition statement "
           "to the remediation commitment without leaving the register.")
    r.figure("docs/report/figures/figure-5-4-soa.png",
             "Annex A Statement of Applicability. Forty controls across the four ISO/IEC 27001:2022 "
             "themes, each with an applicability decision, an implementation status, an owner, a "
             "justification and an illustrative cross-framework mapping.", width_in=6.0)
    r.para("The Statement of Applicability implements Clause 6.1.3 as a workflow rather than a "
           "checklist. Applicability is an explicit decision per control with a stored justification, "
           "and implementation status is held separately from applicability, so a control can be "
           "recorded as applicable but not yet implemented. The cross-framework column is populated "
           "with illustrative mappings only, and the interface states that they require validation, "
           "which keeps the distinction between navigation and determination visible to the user.")
    r.figure("docs/report/figures/figure-5-5-evidence.png",
             "SHA-256 evidence vault. Each artefact records its byte size, MIME type, uploader and full "
             "digest, and exposes an independent re-verification action.", width_in=6.0)
    r.figure("docs/report/figures/figure-5-8-audit-trail.png",
             "Settings view with the hash-chained audit trail. The panel reports chain validity together "
             "with the number of links examined, and each entry records actor, role, action, target, "
             "timestamp and entry digest.", width_in=6.0)
    r.para("The evidence view is where the narrowness of the integrity claim is made visible. The "
           "interface reports that the stored artefact verifies, not that it is authentic or complete. "
           "Alongside it, the chain panel reports validity with an explicit count of links examined, "
           "which a reviewer can compare against a later reading to detect change. Stating the count "
           "matters: a validity assertion over ten entries is a materially weaker statement than one "
           "over ten thousand, and the interface does not obscure that difference.")
    r.figure("docs/report/figures/figure-5-6-reports.png",
             "Executive audit report centre. The PDF report and the nine-sheet workbook are generated "
             "server-side from the same records, and the preview states the approval state and version "
             "carried by the selected audit.", width_in=6.0)
    r.figure("docs/report/figures/figure-5-7-risks.png",
             "Clause 6.1.2 risk register with inherent and residual scoring. Each scenario shows its "
             "five-by-five scores, treatment decision, owner and linked Annex A controls.", width_in=6.0)
    r.figure("docs/report/figures/figure-5-9-users.png",
             "User and role management. Accounts are provisioned with a salted scrypt-derived secret, "
             "and each row exposes the failed-attempt counter, lockout window and an administrative "
             "reset action.", width_in=6.0)
    r.para("The reports view demonstrates that the deliverables are derived rather than authored. The "
           "register underlying the preview shows one audit approved at version 1.2, one in review at "
           "version 0.9, one still in draft and one approved at version 1.0, which is the mixed "
           "maturity a real programme exhibits. Because the PDF and the workbook are built from the "
           "same tables, an inconsistency between a signed report and the register it describes would "
           "require a defect in generation rather than an oversight in assembly.")

    r.section("5.2", "Illustrative Workflow Walkthrough")
    r.body("A single fictional audit can be traced through the platform to demonstrate that the stages "
           "compose. The walkthrough describes capability that the interface and database support; it is "
           "not a record of a real audit having been performed.")
    r.table(["Stage", "Record created", "Observation"],
            [["Plan", "Audit with title, department, type, scope, objectives, lead auditor and dates.",
              "Provides a container to which every later record attaches."],
             ["Controls", "Applicability decision and justification per Annex A control.",
              "Implements Clause 6.1.3 as a decision record rather than a default."],
             ["Test", "Workpaper with control identifier, procedure, sample size, result and notes.",
              "Captures the evidential basis of the conclusion; sampling adequacy remains auditor judgement."],
             ["Evidence", "Artefact with digest and byte count, attached to the test.",
              "Makes the bytes durable and verifiable; says nothing about their relevance."],
             ["Finding", "Nonconformity citing criterion, condition, cause, impact and recommendation.",
              "Produces an auditable statement that distinguishes the requirement from the observation."],
             ["Action", "Corrective action with owner, due date, status and verification note.",
              "Creates accountability and a due date; effectiveness still requires human verification."],
             ["Report", "PDF and workbook generated from the records, then approved with version recorded.",
              "Separates preparation from sign-off and preserves the approved version."]],
            "Illustrative workflow walkthrough.", widths=[0.8, 2.6, 2.6], font_size=9)
    r.para("The observation column is deliberately restrained. At every stage the platform captures a "
           "record and enforces a structural property, and at every stage a substantive judgement remains "
           "with a human: whether the sample was adequate, whether the evidence was relevant, whether the "
           "root cause is correct, whether the action was effective, whether the report should be signed. "
           "The platform improves the consistency and reconstructibility of those judgements; it does not "
           "make them.")

    r.section("5.3", "Analysis of Research Questions")
    r.subsection("5.3.1", "RQ1: Can a single normalised model carry the audit end to end?")
    r.body("The evidence supports an affirmative answer within a defined boundary. Twelve tables with "
           "identifier-based references are sufficient to represent every record type the workflow "
           "requires, and the traceability path from audit to test to evidence to finding to action to "
           "report is complete and resolvable by query. The seven-stage model in Figure 4.3 is realised in "
           "the schema without a stage that exists only in prose.")
    r.para("The boundary is that normalisation is necessary but not sufficient for evidential quality. A "
           "complete and internally consistent record set can still describe an inadequate audit, and the "
           "schema cannot detect that. The claim supported is therefore about representational completeness "
           "and machine-readable traceability, not about audit adequacy.")

    r.subsection("5.3.2", "RQ2: Can the assurance controls be verified automatically?")
    r.body("The evidence supports an affirmative answer for all eight controls. Each control has an "
           "identifiable code path, each is exercised by a named test group, and the recorded outcomes are "
           "passes rather than assertions. The lockout control is demonstrated by a test that drives five "
           "failures and then presents the correct credential, which is the only way to distinguish "
           "lockout from password verification. The evidence control is demonstrated by a test that "
           "modifies a stored file and observes the download being refused. These are falsifiable "
           "demonstrations rather than descriptions.")
    r.para("Two qualifications bound the claim. The suite is a regression instrument, not a security "
           "assessment; it demonstrates that the intended behaviour occurs under the tested conditions and "
           "does not demonstrate the absence of exploitable defects. And several controls address online "
           "threats only: account lockout constrains guessing against a single account but not distributed "
           "spraying, and the hash chain detects tampering by someone who edits rows without recomputing "
           "digests, but not by an attacker who recomputes the whole chain with database access.")

    r.subsection("5.3.3", "RQ3: Which constraints limit organisational adoption?")
    r.body("Four constraints emerge from the analysis, and each is architectural rather than incidental. "
           "Persistence is a single SQLite file, which is appropriate for a small team on one host and "
           "unsuitable for concurrent multi-site operation or high availability. Identity is local, so "
           "provisioning and deprovisioning depend on manual discipline and there is no integration with "
           "the directory services most organisations already operate. Records are not encrypted by the "
           "application, so confidentiality depends entirely on the host and its storage controls. And "
           "there is no retention or legal-hold engine, which is a substantive gap for any organisation "
           "subject to record-keeping obligations.")
    r.para("A fifth constraint concerns the deployment model rather than the architecture. Serverless "
           "hosting with an ephemeral filesystem is well suited to demonstration and unsuitable for a "
           "system of record. An adopting organisation would deploy the same code against a persistent "
           "volume or a managed database, and the configuration already supports that through environment "
           "variables, but such a deployment was not built or tested in this project and is stated as "
           "future work instead.")

    r.section("5.4", "Results Boundaries")
    r.body("The results reported in this chapter are implementation observations and structured analysis, "
           "not empirical findings. There were no survey responses, no interviews, no controlled "
           "comparison, no production telemetry and no measured efficiency gains. No test pass rate is "
           "reported as a quality metric, because a suite written by the same author as the implementation "
           "measures regression safety rather than correctness. The seeded dataset contains fictional "
           "records and supports no inferential claim.")
    r.para("These boundaries are stated plainly because the principal risk in an artefact study of this "
           "kind is not that the work is weak but that the claims outrun the evidence. A reader should "
           "leave this chapter able to distinguish three things: what was built and can be inspected, what "
           "was verified and can be reproduced, and what remains argued rather than demonstrated.")
