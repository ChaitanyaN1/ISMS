"""Bibliography and annexures."""
from docx_base import Report

def back_matter(r: Report):
    # ---------------- BIBLIOGRAPHY ----------------
    r.chapter(9, "Bibliography and References")
    r.section("9.1", "Standards and Guidance", first=True)
    r.body("The following standards and guidance documents informed the requirements and design decisions in "
           "this report. Licensed standard text is not reproduced; references are cited at the level of "
           "clause and control identifiers.")
    refs_std = [
        "International Organization for Standardization. (2022). ISO/IEC 27001:2022 Information security, "
        "cybersecurity and privacy protection \u2014 Information security management systems \u2014 "
        "Requirements (3rd ed.). https://www.iso.org/standard/27001.html",
        "International Organization for Standardization. (2024). ISO/IEC 27001:2022/Amd 1:2024 Information "
        "security management systems \u2014 Requirements \u2014 Amendment 1: Climate action changes. "
        "https://www.iso.org/standard/88435.html",
        "International Organization for Standardization. (2026). ISO 19011:2026 Guidelines for auditing "
        "management systems (4th ed.). https://www.iso.org/standard/iso-19011",
        "Pascoe, C., Quinn, S., & Scarfone, K. (2024). The NIST Cybersecurity Framework (CSF) 2.0 (NIST "
        "CSWP 29). National Institute of Standards and Technology. https://doi.org/10.6028/NIST.CSWP.29",
        "American Institute of Certified Public Accountants. (2017). Trust Services Criteria for Security, "
        "Availability, Processing Integrity, Confidentiality and Privacy. AICPA.",
        "National Institute of Standards and Technology. (2017). Digital Identity Guidelines: "
        "Authentication and Lifecycle Management (NIST SP 800-63B). https://doi.org/10.6028/NIST.SP.800-63b",
        "National Institute of Standards and Technology. (2023). Secure Hash Standard (SHS) (FIPS 180-4). "
        "https://doi.org/10.6028/NIST.FIPS.180-4",
        "Internet Engineering Task Force. (2017). RFC 7914: The scrypt Password-Based Key Derivation "
        "Function. https://doi.org/10.17487/RFC7914",
    ]
    r.numbered(refs_std, size=11)

    r.section("9.2", "Academic Literature")
    r.body("The academic literature provided the analytical frame for the project, particularly the "
           "emphasis on context-dependent implementation and the caution about outcome claims.")
    refs_acad = [
        "Culot, G., Nassimbeni, G., Podrecca, M., & Sartor, M. (2021). The ISO/IEC 27001 information "
        "security management standard: Literature review and theory-based research agenda. The TQM "
        "Journal, 33(7), 76\u2013105. https://doi.org/10.1108/TQM-09-2020-0202",
        "Siponen, M., & Willison, R. (2009). Information security management standards: Problems and "
        "solutions. Information & Management, 46(5), 267\u2013270. "
        "https://doi.org/10.1016/j.im.2008.12.007",
        "Von Solms, B., & von Solms, R. (2018). Cybersecurity and information security: What goes where? "
        "Information & Computer Security, 26(1), 2\u20139. https://doi.org/10.1108/ICS-04-2017-0025",
        "Herath, T., & Rao, H. R. (2009). Encouraging information security behaviors in organizations: "
        "Role of penalties, pressures and perceived effectiveness. Decision Support Systems, 47(2), "
        "154\u2013165. https://doi.org/10.1016/j.dss.2009.02.005",
        "Hevner, A. R., March, S. T., Park, J., & Ram, S. (2004). Design science in information systems "
        "research. MIS Quarterly, 28(1), 75\u2013105. https://doi.org/10.2307/25148625",
    ]
    r.numbered(refs_acad, size=11)

    r.section("9.3", "Project and Technical Artefacts")
    r.body("Project artefacts and technical documentation consulted during implementation and verification.")
    refs_proj = [
        "Nagre, C. (2026). SecureAudit ISMS ISO 27001 audit tracker: Source repository, README and "
        "deployment configuration [Unpublished project artefacts]. "
        "https://github.com/ChaitanyaN1/ISMS",
        "SecureAudit live deployment. (2026). Public instance and OpenAPI specification. "
        "https://isms1.vercel.app",
        "School of Management Studies, National Forensic Sciences University. (n.d.). Minor Project "
        "Guideline, MBA Cyber Security Management, Semester III. Supplied course document.",
        "FastAPI and Starlette project documentation. (2026). Framework, dependency injection and testing "
        "utilities. https://fastapi.tiangolo.com",
        "React and Vite project documentation. (2026). Component model, build tooling and deployment. "
        "https://react.dev and https://vite.dev",
        "Python Software Foundation. (2026). sqlite3, hashlib and hmac standard library modules. "
        "https://docs.python.org/3/library/",
        "OpenPyXL and FPDF2 project documentation. (2026). Workbook and PDF generation libraries. "
        "https://openpyxl.readthedocs.io and https://py-pdf.github.io/fpdf2/",
    ]
    r.numbered(refs_proj, size=11)

    # ---------------- ANNEXURES ----------------
    r.chapter(10, "Annexures")

    r.section("10.1", "Annexure A: Requirements Traceability Summary", first=True)
    r.body("The matrix below links each workflow requirement to the artefact that implements it and to the "
           "instrument that evidences it. It is the compact form of the analysis presented in Chapter 4 and "
           "is provided so that a reviewer can verify any individual claim without reading the whole "
           "report.")
    r.table(["Requirement", "Implementation artefact", "Evidence"],
            [["Audit planning", "audits table; audit register and detail views; create and delete endpoints",
              "Interface plate 4.4; workspace payload check"],
             ["Statement of Applicability", "controls table; SoA view with applicability and justification",
              "Interface plate 4.6"],
             ["Control test workpapers", "tests table; workpaper view; automatic score recalculation",
              "Interface plate 4.4; export test group"],
             ["Findings and CAPA", "findings and actions tables; findings view and action table",
              "Interface plate 4.5"],
             ["Risk register", "risks table with inherent and residual scoring and linked controls",
              "Workspace payload check"],
             ["Evidence integrity", "evidence table; upload and download endpoints; digest re-verification",
              "Evidence test group; interface plate 4.7"],
             ["Audit trail", "audit_logs table; chained digests; verification endpoint",
              "Health assertions; interface plate 4.7"],
             ["Authentication", "security module; login endpoint; lockout state on users table",
              "Authentication test group"],
             ["Authorisation", "permission map; API dependency; both interfaces",
              "Authorisation test group"],
             ["Report approval", "approval fields on audits table; approve endpoint",
              "Export test group; interface plate 4.8"],
             ["Deliverables", "reports module; PDF, Excel, JSON and CSV endpoints",
              "Export test group; deployment verification"],
             ["Demonstration separation", "record-type marker; purge and restore endpoints",
              "Health and seeding test group"]],
            "Requirements traceability summary.", widths=[1.4, 2.85, 1.75], font_size=9)

    r.section("10.2", "Annexure B: Reproduction Instructions")
    r.body("Any claim in this report can be reproduced from a clean checkout. The sequence below is the one "
           "used to produce the results in Chapter 5.")
    r.subsection("10.2.1", "Local Verification")
    r.para("From the repository root, create a Python virtual environment and install the full local "
           "dependency set, then run the automated suite:", space_before=12)
    r.rich([("python3 -m venv .venv && source .venv/bin/activate", False, False)], size=10.5, align="left")
    r.rich([("pip install -r requirements-streamlit.txt", False, False)], size=10.5, align="left")
    r.rich([("pytest -v", False, False)], size=10.5, align="left")
    r.para("To run the interfaces, start the API service, the React client and the Streamlit workbench, or "
           "use the single launcher script provided for each platform. The API service exposes its "
           "interactive specification at the /api/docs path.", space_before=12)
    r.subsection("10.2.2", "Live Verification")
    r.para("Against the public deployment, the following endpoints reproduce the checks in Table 9. The "
           "health endpoint reports chain validity; the workspace endpoint returns the seeded record set; "
           "the report endpoints generate the PDF and workbook on demand; and the OpenAPI document lists the "
           "complete contract.", space_before=12)
    r.bullets([
        "/api/health \u2014 service status and audit-chain validity",
        "/api/workspace \u2014 complete relational payload",
        "/api/reports/audit/AUD-2026-001/pdf \u2014 generated audit report",
        "/api/reports/workbook.xlsx \u2014 generated nine-sheet workbook",
        "/api/audit-logs/verify \u2014 independent chain verification",
        "/api/docs \u2014 interactive OpenAPI specification",
    ])

    r.section("10.3", "Annexure C: Demonstration Data Notice")
    r.body("The dataset seeded by the application is fictional and exists solely so that the workflow can "
           "be exercised before an organisation enters records of its own. It contains four audits, twenty "
           "control test workpapers, eight findings across all four severity levels, seven corrective "
           "actions, forty Annex A reference controls, five risks and four evidence artefacts with genuine "
           "digests over generated files.")
    r.para("Organisation names, personnel names, email addresses, audit dates, control scores, findings and "
           "evidence content are invented. The email addresses use a reserved demonstration domain. The "
           "compliance percentages shown in the interface are computed arithmetically from the seeded test "
           "results and describe only that fictional dataset.")
    r.para("No output of this application, when generated from seeded records, may be presented as evidence "
           "of a real audit, a real organisational condition, a regulatory assessment or a certification "
           "outcome. The interface displays a persistent warning whenever demonstration records are visible, "
           "and every figure in this report that derives from the seeded data carries a caption to the same "
           "effect.")

    r.section("10.4", "Annexure D: Submission Checklist")
    r.body("The items below were completed before submission of this report. They are recorded so that the "
           "institutional review can confirm compliance with the format guidelines without re-deriving it.")
    r.bullets([
        "Paper size A4, with margins of 1.5 inches left, 0.75 inches right and 1.0 inch top and bottom.",
        "Times New Roman throughout, body text at 12 point, sections at 14 point, subsections at 12 point "
        "and chapter titles at 20 point, with 1.5 line spacing.",
        "Body text fully justified in single-column layout, with no first-line indentation and a 12 point "
        "gap between each heading and its first paragraph.",
        "Page numbers centred in the footer, in lower-case Roman numerals for the front matter and Arabic "
        "numerals beginning at 1 from the first page of Chapter 1, with no number on the title page.",
        "Each chapter beginning on a new page with an additional 30 millimetres of top margin, with 36 "
        "points before the first section heading and 24 points before subsequent headings.",
        "Table of contents inserted as a field so that page references remain accurate after any edit; "
        "update the field before printing.",
        "All figures generated from the submitted implementation rather than from external screenshots, "
        "and all tables numbered and captioned.",
        "Bibliography verified against publisher records, and no licensed standard text reproduced.",
        "Title page, declaration and guide certificate completed with institutional details, and "
        "signatures obtained through the university process only.",
    ])
