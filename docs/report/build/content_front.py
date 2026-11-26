"""Front matter: title page, declaration, certificate, abstract, TOC, lists."""

def build_front_block(r, docx=True):
    if docx:
        return _build_front_docx(r)
    return _build_front_pdf(r)


def _build_front_docx(r):
    docx = True
    # ---------------- TITLE PAGE (no page number) ----------------
    d = r.doc
    r.suppress_footer()
    r.para("PAPER VI \u2013 MINOR PROJECT", size=12, bold=True, align="center", space_before=6)
    r.para("", size=10)
    r.para("ISMS ISO 27001 AUDIT TRACKER", size=20, bold=True, align="center", space_before=24)
    r.para("A Web-Based Audit Workflow and Compliance Tracking Platform", size=14, italic=True,
           align="center", space_before=6)
    r.para("", size=10)
    r.para("Submitted in partial fulfilment of the requirements for the award of", size=12,
           align="center", space_before=36)
    r.para("MASTER OF BUSINESS ADMINISTRATION", size=14, bold=True, align="center", space_before=10)
    r.para("in", size=12, align="center", space_before=4)
    r.para("CYBER SECURITY MANAGEMENT", size=14, bold=True, align="center", space_before=4)
    r.para("", size=8)
    r.para("Submitted to", size=12, align="center", space_before=30)
    r.para("School of Management Studies", size=13, bold=True, align="center", space_before=4)
    r.para("National Forensic Sciences University", size=13, bold=True, align="center", space_before=2)
    r.para("", size=8)
    r.para("Submitted by", size=12, align="center", space_before=30)
    r.para("Chaitanya Nagre", size=13, bold=True, align="center", space_before=4)
    r.para("Enrolment No. 250104002013", size=12, align="center", space_before=2)
    r.para("", size=8)
    r.para("Under the supervision of", size=12, align="center", space_before=30)
    r.para("Dr. Hetal Thaker", size=13, bold=True, align="center", space_before=4)
    r.para("", size=8)
    r.para("National Forensic Sciences University", size=12, bold=True, align="center", space_before=34)
    r.para("Gandhinagar Campus, Gandhinagar \u2013 382009, Gujarat, India", size=12, align="center", space_before=2)
    r.para("2026\u20132027", size=12, bold=True, align="center", space_before=8)

    # ---------------- DECLARATION (roman ii) ----------------
    r.new_section(footer_fmt="lowerRoman", start=2)
    r.para("STUDENT DECLARATION", size=16, bold=True, align="center", space_before=0)
    r.para("", size=8)
    r.body("I declare that the minor project report titled \u201cISMS ISO 27001 Audit Tracker: "
           "A Web-Based Audit Workflow and Compliance Tracking Platform\u201d has been prepared by me "
           "as part of the Master of Business Administration in Cyber Security Management programme "
           "at the School of Management Studies, National Forensic Sciences University, Gandhinagar.")
    r.para("I further declare that the software artefact, source code, database schema, generated "
           "figures and analysis presented in this report are my own work. The report distinguishes "
           "clearly between implemented functionality, verified test results and illustrative "
           "demonstration data. No part of this report has been submitted for the award of any other "
           "degree or diploma at this or any other institution.", space_before=10)
    r.para("All pre-seeded demonstration records, organisation names, personnel names, control scores "
           "and evidence files shipped with the application are fictional. They are included solely to "
           "demonstrate workflow behaviour and must not be interpreted as real audit evidence, "
           "organisational conclusions or certification status.", space_before=10)
    r.para("", size=10)
    r.para("Place: Gandhinagar", size=12, align="left", space_before=26)
    r.para("Date: ______________", size=12, align="left", space_before=6)
    r.para("", size=12)
    r.para("Signature: ______________________________", size=12, align="left", space_before=24)
    r.para("Chaitanya Nagre  (Enrolment No. 250104002013)", size=12, bold=True, align="left", space_before=6)

    # ---------------- CERTIFICATE (roman iii) ----------------
    r.new_section(footer_fmt="lowerRoman", start=3)
    r.para("GUIDE CERTIFICATE", size=16, bold=True, align="center")
    r.para("", size=8)
    r.body("This is to certify that the minor project report entitled \u201cISMS ISO 27001 Audit Tracker: "
           "A Web-Based Audit Workflow and Compliance Tracking Platform\u201d submitted by "
           "Mr. Chaitanya Nagre (Enrolment No. 250104002013) is a record of work carried out under my "
           "supervision during the academic year 2026\u20132027.")
    r.para("The report has been examined for structure, technical accuracy and academic integrity. "
           "The implementation claims have been verified against the submitted source repository, and "
           "the distinction maintained between implemented controls, automated test results and "
           "illustrative demonstration data is satisfactory.", space_before=10)
    r.para("", size=10)
    r.para("Guide: Dr. Hetal Thaker", size=12, align="left", space_before=30)
    r.para("School of Management Studies", size=12, align="left", space_before=4)
    r.para("National Forensic Sciences University", size=12, align="left", space_before=4)
    r.para("", size=12)
    r.para("Signature: ______________________________", size=12, align="left", space_before=24)
    r.para("Date: ______________", size=12, align="left", space_before=6)

    # ---------------- ABSTRACT (roman iv) ----------------
    r.new_section(footer_fmt="lowerRoman", start=4)
    r.para("ABSTRACT", size=16, bold=True, align="center")
    r.para("", size=8)
    r.body("Organisations that operate an Information Security Management System (ISMS) accumulate a "
           "large volume of connected audit records: audit scope and criteria, control selection and "
           "justification, test procedures and samples, supporting evidence, nonconformities, "
           "corrective actions, owners, due dates and management reports. When these artefacts live in "
           "separate spreadsheets, mailboxes and shared folders, reviewers struggle to answer three "
           "basic questions: what was tested, what evidence supports the conclusion, and whether "
           "remediation has actually closed.")
    r.para("This project designs, implements and evaluates SecureAudit, a full-stack platform that "
           "consolidates those records into a single traceable workflow aligned with ISO/IEC "
           "27001:2022 and its 2024 climate action amendment, with reference mappings to ISO 19011 "
           "audit guidance, NIST CSF 2.0 and SOC 2. The platform is delivered in two synchronised "
           "interfaces over a shared Python core: a React and TypeScript single-page application served "
           "with a FastAPI REST service, and an eight-page Streamlit governance workbench. Both write to "
           "the same normalised SQLite schema of twelve tables and are deployed publicly at "
           "https://isms1.vercel.app.", space_before=10)
    r.para("The project follows a design-and-development methodology supported by documentary review "
           "of published standards and academic literature, schema and source inspection, and an "
           "automated verification suite. Eight security and assurance capabilities that were only "
           "proposed in the earlier iteration of this artefact are now implemented and covered by "
           "repeatable tests: scrypt password derivation with per-user salting, stateless HMAC-SHA256 "
           "session tokens, a five-attempt fifteen-minute account lockout, role-based access control "
           "enforced at both interface and API layers, SHA-256 evidence integrity with byte-size and "
           "media-type validation, a formal four-state report approval workflow, a tamper-evident "
           "SHA-256 hash-chained audit trail, and manifest-verified JSON backup with dry-run "
           "validation.", space_before=10)
    r.para("Results are reported from three evidence sources: the automated pytest suite, which passes "
           "all five test groups; direct inspection of the live production deployment, which returns a "
           "valid audit-chain status and generates PDF and Excel deliverables on demand; and the "
           "rendered interface captures reproduced in Chapter 5, which were taken from the running "
           "deployment rather than being illustrative mock-ups. Analysis confirms that the "
           "traceability chain from audit to test to evidence to finding to corrective action to report "
           "is complete and machine-readable.", space_before=10)
    r.para("The report is deliberately explicit about its boundaries. No organisational field study, "
           "user-satisfaction survey or independent penetration test was conducted. The platform is an "
           "educational reference implementation: it demonstrates a defensible workflow and security "
           "baseline, but it does not establish that any organisation conforms to ISO/IEC 27001, and it "
           "is not a substitute for competent auditors, licensed standards or accredited certification.",
           space_before=10)
    r.para("", size=8)
    r.rich([("Keywords: ", True, False),
            ("ISMS; ISO/IEC 27001:2022; internal audit; Statement of Applicability; risk register; "
             "audit evidence; SHA-256 integrity; corrective and preventive action; FastAPI; React; "
             "SQLite; cybersecurity governance.", False, False)], space_before=10)

    # ---------------- TABLE OF CONTENTS (roman v) ----------------
    r.new_section(footer_fmt="lowerRoman", start=5)
    r.para("CONTENTS", size=16, bold=True, align="center")
    r.para("", size=8)
    if docx:
        # a printed list, so the contents are readable without updating a field
        for kind, number, title in _toc_entries():
            indent = {"chapter": 0, "section": 1, "subsection": 2}[kind]
            label = f"Chapter {number}   {title}" if kind == "chapter" else f"{number}   {title}"
            p = r.para("      " * indent + label, size=11 if kind == "chapter" else 10.5,
                       bold=(kind == "chapter"), align="left", space_before=6 if kind == "chapter" else 1)
        r.toc_field(empty=False)
    else:
        r.toc_field()
    r.para("", size=8)
    note = r.para("Note on pagination: front matter is numbered in lower-case Roman numerals and the "
                  "body restarts at 1 on the first page of Chapter 1, in accordance with the "
                  "institutional format guidelines.", size=10, italic=True, space_before=14)

    # ---------------- LIST OF FIGURES AND TABLES (roman vii) ----------------
    r.new_section(footer_fmt="lowerRoman", start=7)
    r.para("LIST OF FIGURES AND TABLES", size=16, bold=True, align="center")
    r.para("", size=8)
    r.para("Figures", size=14, bold=True, align="left", space_before=12)
    r.para("Figure numbers, captions and the page on which each figure appears are generated by Word "
           "from the caption fields. The list below identifies the figures included in this report.",
           size=11, italic=False, space_before=6)
    for n, c, _src in FIGURES:
        r.rich([(f"Figure {n}   ", True, False), (c, False, False)], size=12, align="left",
               space_before=4)
    r.para("Tables", size=14, bold=True, align="left", space_before=20)
    for n, c in TABLES:
        r.rich([(f"Table {n}   ", True, False), (c, False, False)], size=12, align="left",
               space_before=4)

    # ---------------- ABBREVIATIONS (roman ix) ----------------
    r.new_section(footer_fmt="lowerRoman", start=9)
    r.para("ABBREVIATIONS", size=16, bold=True, align="center")
    r.para("", size=8)
    rows = [
        ("API", "Application Programming Interface"),
        ("CAPA", "Corrective and Preventive Action"),
        ("CIA", "Confidentiality, Integrity and Availability"),
        ("CSF", "Cybersecurity Framework (NIST)"),
        ("CSV", "Comma-Separated Values"),
        ("GRC", "Governance, Risk and Compliance"),
        ("HMAC", "Hash-based Message Authentication Code"),
        ("HTTP", "Hypertext Transfer Protocol"),
        ("ISMS", "Information Security Management System"),
        ("JSON", "JavaScript Object Notation"),
        ("KDF", "Key Derivation Function"),
        ("MFA", "Multi-Factor Authentication"),
        ("NFSU", "National Forensic Sciences University"),
        ("PDF", "Portable Document Format"),
        ("RBAC", "Role-Based Access Control"),
        ("REST", "Representational State Transfer"),
        ("SHA", "Secure Hash Algorithm"),
        ("SoA", "Statement of Applicability"),
        ("SPA", "Single-Page Application"),
        ("SQL", "Structured Query Language"),
        ("XLSX", "Microsoft Excel Open XML Workbook"),
    ]
    r.table(["Abbreviation", "Expansion"], rows,
            "Abbreviations used throughout this report.", widths=[1.6, 4.4], font_size=11)


def _build_front_pdf(p):
    docx = False
    """Front matter for the PDF renderer: lowercase Roman numerals, none on the title page."""
    from fpdf.enums import XPos, YPos
    from pdf_report import TEXT_W, PAGE_H, MB
    TL, TR = 25.4, 297 - 25.4

    # ---------------- TITLE PAGE (no page number) ----------------
    p.fmt = "off"
    p.add_page()
    p.set_y(26)
    p.heading_center("PAPER VI \u2013 MINOR PROJECT", size=11.5, before=0)
    p.ln(14)
    p.heading_center("ISMS ISO 27001 AUDIT TRACKER", size=23)
    p.ln(1)
    p.set_font(p.fam, "I", 13)
    p.multi_cell(p.epw, 6.6, "A Web-Based Audit Workflow and Compliance Tracking Platform",
                 align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    p.ln(17)
    p.para("Submitted in partial fulfilment of the requirements for the award of", align="center")
    p.ln(3)
    p.heading_center("MASTER OF BUSINESS ADMINISTRATION", size=13.5)
    p.para("in", align="center", size=11.5)
    p.heading_center("CYBER SECURITY MANAGEMENT", size=13.5)
    p.ln(14)
    p.para("Submitted to", align="center", size=11.5)
    p.heading_center("School of Management Studies", size=12.5)
    p.heading_center("National Forensic Sciences University", size=12.5)
    p.ln(13)
    p.para("Submitted by", align="center", size=11.5)
    p.heading_center("Chaitanya Nagre", size=12.5)
    p.para("Enrolment No. 250104002013", align="center", size=11.5)
    p.ln(13)
    p.para("Under the supervision of", align="center", size=11.5)
    p.heading_center("Dr. Hetal Thaker", size=12.5)
    p.ln(15)
    p.heading_center("National Forensic Sciences University", size=11.5)
    p.para("Gandhinagar Campus, Gandhinagar \u2013 382009, Gujarat, India", align="center", size=11.5)
    p.ln(6)
    p.heading_center("2026\u20132027", size=11.5)

    # ---------------- DECLARATION (ii) ----------------
    p.new_front_page()
    p.heading_center("STUDENT DECLARATION", size=15)
    p.ln(4)
    p.body("I declare that the minor project report titled \u201cISMS ISO 27001 Audit Tracker: A Web-Based "
           "Audit Workflow and Compliance Tracking Platform\u201d has been prepared by me as part of the "
           "Master of Business Administration in Cyber Security Management programme at the School of "
           "Management Studies, National Forensic Sciences University, Gandhinagar.")
    p.para("I further declare that the software artefact, source code, database schema, generated figures "
           "and analysis presented in this report are my own work. The report distinguishes clearly between "
           "implemented functionality, verified test results and illustrative demonstration data. No part of "
           "this report has been submitted for the award of any other degree or diploma at this or any other "
           "institution.", space_before=12)
    p.para("All pre-seeded demonstration records, organisation names, personnel names, control scores and "
           "evidence files shipped with the application are fictional. They are included solely to "
           "demonstrate workflow behaviour and must not be interpreted as real audit evidence, "
           "organisational conclusions or certification status.", space_before=12)
    p.ln(16)
    p.para("Place: Gandhinagar", align="left")
    p.para("Date: ______________", align="left", space_before=4)
    p.ln(12)
    p.para("Signature: __________________________________", align="left")
    p.para("Chaitanya Nagre  (Enrolment No. 250104002013)", bold=True, align="left", space_before=4)

    # ---------------- GUIDE CERTIFICATE (iii) ----------------
    p.new_front_page()
    p.heading_center("GUIDE CERTIFICATE", size=15)
    p.ln(4)
    p.body("This is to certify that the minor project report entitled \u201cISMS ISO 27001 Audit Tracker: A "
           "Web-Based Audit Workflow and Compliance Tracking Platform\u201d submitted by Mr. Chaitanya Nagre "
           "(Enrolment No. 250104002013) is a record of work carried out under my supervision during the "
           "academic year 2026\u20132027.")
    p.para("The report has been examined for structure, technical accuracy and academic integrity. The "
           "implementation claims have been verified against the submitted source repository, and the "
           "distinction maintained between implemented controls, automated test results and illustrative "
           "demonstration data is satisfactory.", space_before=12)
    p.ln(20)
    p.para("Guide: Dr. Hetal Thaker", align="left")
    p.para("School of Management Studies", align="left", space_before=3)
    p.para("National Forensic Sciences University", align="left", space_before=3)
    p.ln(12)
    p.para("Signature: __________________________________", align="left")
    p.para("Date: ______________", align="left", space_before=4)

    # ---------------- ABSTRACT (iv) ----------------
    p.new_front_page()
    p.heading_center("ABSTRACT", size=15)
    p.ln(4)
    p.body("Organisations that operate an Information Security Management System (ISMS) accumulate a large "
           "volume of connected audit records: audit scope and criteria, control selection and "
           "justification, test procedures and samples, supporting evidence, nonconformities, corrective "
           "actions, owners, due dates and management reports. When these artefacts live in separate "
           "spreadsheets, mailboxes and shared folders, reviewers struggle to answer three basic questions: "
           "what was tested, what evidence supports the conclusion, and whether remediation has actually "
           "closed.")
    p.para("This project designs, implements and evaluates SecureAudit, a full-stack platform that "
           "consolidates those records into a single traceable workflow aligned with ISO/IEC 27001:2022 and "
           "its 2024 climate action amendment, with reference mappings to ISO 19011 audit guidance, NIST "
           "CSF 2.0 and SOC 2. The platform is delivered in two synchronised interfaces over a shared Python "
           "core: a React and TypeScript single-page application served with a FastAPI REST service, and an "
           "eight-page Streamlit governance workbench. Both write to the same normalised SQLite schema of "
           "twelve tables and are deployed publicly at https://isms1.vercel.app.", space_before=12)
    p.para("The project follows a design-and-development methodology supported by documentary review of "
           "published standards and academic literature, schema and source inspection, and an automated "
           "verification suite. Eight security and assurance capabilities that were only proposed in the "
           "earlier iteration of this artefact are now implemented and covered by repeatable tests: scrypt "
           "password derivation with per-user salting, stateless HMAC-SHA256 session tokens, a five-attempt "
           "fifteen-minute account lockout, role-based access control enforced at both interface and API "
           "layers, SHA-256 evidence integrity with byte-size and media-type validation, a formal four-state "
           "report approval workflow, a tamper-evident SHA-256 hash-chained audit trail, and "
           "manifest-verified JSON backup with dry-run validation.", space_before=12)
    p.para("Results are reported from three evidence sources: the automated pytest suite, which passes all "
           "five test groups; direct inspection of the live production deployment, which returns a valid "
           "audit-chain status and generates PDF and Excel deliverables on demand; and the rendered "
           "interface captures in Chapter 5, which were taken from the running deployment rather than being "
           "illustrative mock-ups. Analysis confirms that the traceability chain from audit to test to "
           "evidence to finding to corrective action to report is complete and machine-readable.",
           space_before=12)
    p.para("The report is deliberately explicit about its boundaries. No organisational field study, "
           "user-satisfaction survey or independent penetration test was conducted. The platform is an "
           "educational reference implementation: it demonstrates a defensible workflow and security "
           "baseline, but it does not establish that any organisation conforms to ISO/IEC 27001, and it is "
           "not a substitute for competent auditors, licensed standards or accredited certification.",
           space_before=12)
    p.para("", space_before=4)
    p.set_font(p.fam, "B", 12)
    p.write(LEADFY := 6.35, "Keywords: ")
    p.set_font(p.fam, "I", 12)
    p.write(6.35, "ISMS; ISO/IEC 27001:2022; internal audit; Statement of Applicability; risk register; "
                  "audit evidence; SHA-256 integrity; corrective and preventive action; FastAPI; React; "
                  "SQLite; cybersecurity governance.")
    p.ln(7)

    # ---------------- CONTENTS (v) ----------------
    p.new_front_page()
    p.heading_center("CONTENTS", size=15)
    p.ln(6)
    _toc_table(p)


CHAPTERS = [
    (1, "Introduction", [
        "1.1  Background and Context", "1.2  Purpose of the Minor Project",
        "1.3  Research Area and Gap", "1.4  Problem Statement",
        "1.5  Research Questions", "1.6  Objectives", "1.7  Scope and Delimitations"]),
    (2, "Literature Review", [
        "2.1  Information Security Management Systems", "2.2  Auditing, Evidence and Integrity",
        "2.3  Implementation Research on ISO/IEC 27001",
        "2.4  Cybersecurity Governance Frameworks and Cross-Mapping",
        "2.5  Conceptual Framework", "2.6  Research Gap Synthesis"]),
    (3, "Research Methodology", [
        "3.1  Research Design", "3.2  Population, Sample and Frame", "3.3  Sampling Technique",
        "3.4  Research Instruments", "3.5  Data Collection", "3.6  Data Analysis",
        "3.7  Implementation Method", "3.8  Ethical and Academic Considerations"]),
    (4, "System Analysis and Implementation", [
        "4.1  System Overview", "4.2  User Roles and Access Model",
        "4.3  Data Model and Record Traceability",
        "4.4  Functional Requirements and Implementation Status",
        "4.5  Security and Assurance Controls", "4.6  Interface Implementation",
        "4.7  Demonstration Data and Separation"]),
    (5, "Results and Analysis", [
        "5.1  Verification Results", "5.2  Illustrative Workflow Walkthrough",
        "5.3  Analysis of Research Questions", "5.4  Results Boundaries"]),
    (6, "Discussion", [
        "6.1  Interpretation in Relation to Objectives",
        "6.2  Relationship to Literature and Standards", "6.3  Strengths",
        "6.4  Weaknesses and Residual Risks", "6.5  Implications"]),
    (7, "Conclusion and Recommendations", [
        "7.1  Conclusion", "7.2  Recommendations",
        "7.3  Practical Implications for Deployment"]),
    (8, "Limitations and Future Research", [
        "8.1  Limitations", "8.2  Future Research", "8.3  Concluding Note"]),
    (9, "Bibliography and References", [
        "9.1  Standards and Guidance", "9.2  Academic Literature",
        "9.3  Project and Technical Artefacts"]),
    (10, "Annexures", [
        "10.1  Annexure A: Requirements Traceability Summary",
        "10.2  Annexure B: Reproduction Instructions",
        "10.3  Annexure C: Demonstration Data Notice",
        "10.4  Annexure D: Submission Checklist"]),
]

# (number, caption, source image) -- the image is resolved through build_all.FIGMAP
FIGURES = [
    ("3.1", "Nine-phase implementation roadmap", "figure-3-2-phases.png"),
    ("4.1", "SecureAudit ISMS three-tier architecture", "figure-3-1-architecture.png"),
    ("4.2", "Entity relationship model of the ISMS schema", "figure-4-2-er-model.png"),
    ("4.3", "Seven-stage audit traceability model", "figure-4-1-workflow.png"),
    ("5.1", "Public landing page and entry to the workspace", "figure-5-0-landing.png"),
    ("5.2", "Role sign-in with the five-attempt lockout policy", "figure-5-11-login.png"),
    ("5.3", "Executive security dashboard", "figure-5-1-dashboard.png"),
    ("5.4", "Audit projects register", "figure-5-10-audits.png"),
    ("5.5", "Audit detail view with control test workpapers", "figure-5-2-audit-detail.png"),
    ("5.6", "Findings and vulnerability register", "figure-5-3-findings.png"),
    ("5.7", "Annex A Statement of Applicability", "figure-5-4-soa.png"),
    ("5.8", "SHA-256 evidence vault", "figure-5-5-evidence.png"),
    ("5.9", "Hash-chained audit trail and workspace settings", "figure-5-8-audit-trail.png"),
    ("5.10", "Executive audit report centre", "figure-5-6-reports.png"),
    ("5.11", "Clause 6.1.2 risk register with residual scoring", "figure-5-7-risks.png"),
    ("5.12", "User and role management", "figure-5-9-users.png"),
]

# (number, title) -- numbered per chapter, matching the order the tables appear in
TABLES = [
    ("1.1", "Research questions and corresponding evidence sources"),
    ("2.1", "Comparison of platform options for small-team ISMS audit work"),
    ("3.1", "Mapping of research questions to analysis procedures"),
    ("4.1", "User roles, permissions and enforcement points"),
    ("4.2", "Database schema summary"),
    ("4.3", "Functional requirements and implementation status"),
    ("4.4", "Implemented security and assurance controls"),
    ("5.1", "Automated test suite coverage"),
    ("5.2", "Live deployment verification results"),
    ("5.3", "Illustrative workflow walkthrough"),
    ("6.1", "Weaknesses, residual risks and required mitigations"),
    ("7.1", "Prioritised recommendations and completion criteria"),
    ("10.1", "Requirements traceability summary"),
]

ABBREV = [
    ("API", "Application Programming Interface"),
    ("CAPA", "Corrective and Preventive Action"),
    ("CIA", "Confidentiality, Integrity and Availability"),
    ("CSF", "Cybersecurity Framework (NIST)"),
    ("CSV", "Comma-Separated Values"),
    ("GRC", "Governance, Risk and Compliance"),
    ("HMAC", "Hash-based Message Authentication Code"),
    ("HTTP", "Hypertext Transfer Protocol"),
    ("ISMS", "Information Security Management System"),
    ("JSON", "JavaScript Object Notation"),
    ("KDF", "Key Derivation Function"),
    ("MFA", "Multi-Factor Authentication"),
    ("NFSU", "National Forensic Sciences University"),
    ("PDF", "Portable Document Format"),
    ("RBAC", "Role-Based Access Control"),
    ("REST", "Representational State Transfer"),
    ("SHA", "Secure Hash Algorithm"),
    ("SoA", "Statement of Applicability"),
    ("SPA", "Single-Page Application"),
    ("SQL", "Structured Query Language"),
    ("XLSX", "Microsoft Excel Open XML Workbook"),
]


def _toc_entries():
    """Default outline used when the renderer has not recorded one (DOCX path)."""
    rows = []
    for num, title, subs in CHAPTERS:
        rows.append(("chapter", str(num), title))
        for sub in subs:
            head = sub.split("  ")[0].strip()
            label = sub[len(head):].strip()
            rows.append(("section", head, label))
    return rows


def _toc_table(p):
    """Contents with three levels and dot leaders, using live page numbers."""
    from fpdf.enums import XPos, YPos
    from pdf_report import TEXT_W
    pagemap = getattr(p, "pagemap", {})
    # the contents page is typeset before the chapters exist, so it uses the
    # outline recorded by the previous build pass
    outline = (getattr(p, "toc_outline", None)
               or getattr(p, "outline", None)
               or _toc_entries())
    lead = 4.15
    PAGE_W_COL = 12.0

    def entry(kind, number, title, page):
        indent = {"chapter": 0.0, "section": 6.0, "subsection": 12.0}[kind]
        size = {"chapter": 11.0, "section": 10.0, "subsection": 9.6}[kind]
        if kind == "chapter":
            labels = [f"Chapter {number}   {title}"]
        else:
            labels = [f"{number}   {title}"]
        p.set_font(p.fam, "B" if kind == "chapter" else "", size)
        avail = TEXT_W - indent - PAGE_W_COL - 2.0
        # wrap long titles, keeping the page number on the last line
        lines, cur = [], ""
        for word in labels[0].split():
            trial = (cur + " " + word).strip()
            if p.get_string_width(trial) <= avail or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)

        p._need(lead * (len(lines) + 1.2))
        for i, line in enumerate(lines):
            last = i == len(lines) - 1
            p.set_x(p.l_margin + indent)
            p.set_font(p.fam, "B" if kind == "chapter" else "", size)
            txt_w = p.get_string_width(line)
            p.cell(txt_w + 0.4, lead, line)
            if last:
                # dot leader between the text and the page number
                dots_x = p.l_margin + indent + txt_w + 1.6
                dots_end = p.l_margin + TEXT_W - PAGE_W_COL
                if dots_end > dots_x:
                    p.set_font(p.fam, "", size)
                    n_dots = max(1, int((dots_end - dots_x) / 1.15))
                    p.set_xy(dots_x, p.get_y())
                    p.cell(dots_end - dots_x, lead, "." * n_dots)
                p.set_font(p.fam, "B" if kind == "chapter" else "", size)
                p.cell(PAGE_W_COL, lead, str(page), align="C")
            p.set_xy(p.l_margin, p.get_y() + lead)

    p.set_font(p.fam, "B", 10.2)
    p.cell(TEXT_W - PAGE_W_COL, 5.4, "Chapter, section and subsection", border="B")
    p.cell(PAGE_W_COL, 5.4, "Page", border="B", align="C",
           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    p.ln(3.0)

    last_chapter = None
    for kind, number, title in outline:
        if kind == "chapter" and last_chapter is not None:
            p.ln(2.6)
        key = ("ch" if kind == "chapter" else "s") + number
        entry(kind, number, title, pagemap.get(key, ""))
        if kind == "chapter":
            last_chapter = number

    # ---------------- ABBREVIATIONS (ix) ----------------
    p.new_front_page()
    p.heading_center("ABBREVIATIONS", size=15)
    p.ln(4)
    p.table(["Abbreviation", "Expansion"], ABBREV,
            "Abbreviations used throughout this report.",
            widths=[1.5, 4.5], font_size=10.2)
