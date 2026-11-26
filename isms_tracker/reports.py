"""PDF and Excel report generation for ISMS ISO/IEC 27001 Audit Tracker.

Generates structured audit reports matching the executive report layout shown in
Figure 4 of the Minor Project Report, including:
- Header banner & illustrative-data notice when DEMO records are included
- Executive summary (Audit Title, Type, Organization, Lead Auditor, Created By, Sign-off Status)
- KPI summary cards (Total Controls, Total Findings, Critical Findings, Compliance Score)
- Scope & Objectives
- Control Test Checklist & Evidence References
- Findings, Root Cause, Recommendations, and Linked CAPA Remediation
- Evidence SHA-256 Integrity Manifest
"""

from __future__ import annotations

import io
from typing import Any

import pandas as pd
from fpdf import FPDF

from isms_tracker.db import get_connection, ensure_initialized


def _clean_latin1(value: Any) -> str:
    """Normalize text safely for standard PDF Helvetica font encoding."""
    text = str(value if value is not None else "")
    replacements = {
        "—": "-",
        "–": "-",
        "•": "*",
        "“": '"',
        "”": '"',
        "’": "'",
        "‘": "'",
        "…": "...",
        "·": "|",
        "→": "->",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")


class AuditPDF(FPDF):
    def __init__(self, report_title: str, is_demo: bool = False) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = _clean_latin1(report_title)
        self.is_demo = is_demo
        self.set_auto_page_break(auto=True, margin=18)

    def header(self) -> None:
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 16, style="F")
        self.set_fill_color(37, 99, 235)
        self.rect(0, 16, 210, 1.5, style="F")
        self.set_xy(12, 4.5)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(255, 255, 255)
        self.cell(120, 7, "SecureAudit ISMS | Professional Security Audit Report", align="L")
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(191, 219, 254)
        tag = "ILLUSTRATIVE DEMO" if self.is_demo else "CONFIDENTIAL"
        self.cell(66, 7, tag, align="R")
        self.ln(16)

    def footer(self) -> None:
        self.set_y(-13)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 116, 139)
        notice = (
            "Illustrative prototype output - Not proof of ISO/IEC 27001 certification"
            if self.is_demo
            else "ISMS Governance Audit Record - Verify against controlled repository"
        )
        self.cell(140, 6, notice, align="L")
        self.cell(46, 6, f"Page {self.page_no()}/{{nb}}", align="R")


def _section_heading(pdf: AuditPDF, number: str, title: str) -> None:
    pdf.ln(3)
    y = pdf.get_y()
    pdf.set_fill_color(37, 99, 235)
    pdf.rect(12, y, 2.5, 7, style="F")
    pdf.set_xy(17, y)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 7, _clean_latin1(f"{number}. {title}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def generate_audit_pdf(audit_id: str) -> bytes:
    """Generate a multi-section PDF report for a selected audit."""
    ensure_initialized()
    with get_connection() as conn:
        audit_row = conn.execute(
            "SELECT * FROM audits WHERE audit_id = ?", (audit_id,)
        ).fetchone()
        if not audit_row:
            raise KeyError(f"Audit {audit_id} not found.")
        audit = dict(audit_row)
        tests = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM tests WHERE audit_id = ? ORDER BY control_id", (audit_id,)
            ).fetchall()
        ]
        findings = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM findings WHERE audit_id = ? ORDER BY finding_id", (audit_id,)
            ).fetchall()
        ]
        finding_ids = [f["finding_id"] for f in findings]
        actions: list[dict[str, Any]] = []
        if finding_ids:
            placeholders = ",".join("?" for _ in finding_ids)
            actions = [
                dict(r)
                for r in conn.execute(
                    f"SELECT * FROM actions WHERE finding_id IN ({placeholders}) ORDER BY due_date",
                    finding_ids,
                ).fetchall()
            ]
        evidence = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM evidence WHERE audit_id = ? ORDER BY evidence_id", (audit_id,)
            ).fetchall()
        ]

    is_demo = audit.get("record_type") == "DEMO"
    pdf = AuditPDF(audit["title"], is_demo=is_demo)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Section 1: Executive Summary
    _section_heading(pdf, "1", "Executive Summary")

    box_y = pdf.get_y()
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(12, box_y, 186, 36, style="DF")

    pdf.set_xy(16, box_y + 4)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(92, 4, "AUDIT TITLE")
    pdf.cell(90, 4, "AUDIT TYPE & VERSION", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(16)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(92, 6, _clean_latin1(audit["title"])[:46])
    pdf.cell(
        90,
        6,
        _clean_latin1(f"{audit.get('audit_type', 'ISO 27001')} | v{audit.get('report_version', '1.0')}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_x(16)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(92, 4, "ORGANIZATION & DEPARTMENT")
    pdf.cell(90, 4, "LEAD AUDITOR & CREATED BY", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(16)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(
        92,
        6,
        _clean_latin1(f"{audit.get('organization', '')} - {audit.get('department', '')}")[:48],
    )
    pdf.cell(
        90,
        6,
        _clean_latin1(f"{audit.get('lead_auditor', 'Unassigned')} | Created: {audit.get('created_by', 'System')}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.set_x(16)
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(92, 4, "AUDIT PERIOD")
    pdf.cell(90, 4, "APPROVAL SIGN-OFF STATUS", new_x="LMARGIN", new_y="NEXT")

    pdf.set_x(16)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(30, 41, 59)
    period = f"{audit.get('start_date') or audit.get('audit_date')} to {audit.get('end_date') or audit.get('audit_date')}"
    signoff = audit.get("approval_status", "Draft")
    if audit.get("approved_by"):
        signoff += f" by {audit['approved_by']}"
    pdf.cell(92, 5, _clean_latin1(period))
    pdf.cell(90, 5, _clean_latin1(signoff), new_x="LMARGIN", new_y="NEXT")

    pdf.set_y(box_y + 40)

    # 4 KPI Cards (Total Controls, Total Findings, Critical Findings, Compliance Score)
    crit_count = sum(1 for f in findings if (f.get("severity") or "").lower() == "critical")
    comp_score = f"{audit['compliance']:.0f}%" if audit.get("compliance") is not None else "N/A"
    cards = [
        (str(len(tests)), "Controls Tested", (37, 99, 235)),
        (str(len(findings)), "Total Findings", (220, 38, 38)),
        (str(crit_count), "Critical Findings", (127, 29, 29)),
        (comp_score, "Compliance Score", (217, 119, 6)),
    ]
    card_y = pdf.get_y()
    card_w = 43.5
    gap = 4
    for idx, (val, label, rgb) in enumerate(cards):
        cx = 12 + idx * (card_w + gap)
        pdf.set_fill_color(*rgb)
        pdf.rect(cx, card_y, card_w, 20, style="F")
        pdf.set_xy(cx, card_y + 3.5)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(card_w, 7, val, align="C")
        pdf.set_xy(cx, card_y + 12)
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(card_w, 5, label, align="C")

    pdf.set_y(card_y + 24)

    # Section 2: Scope & Objectives
    _section_heading(pdf, "2", "Scope & Objectives")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 5, "SCOPE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(30, 41, 59)
    pdf.set_x(12)
    pdf.multi_cell(186, 5, _clean_latin1(audit.get("scope") or "Scope not specified."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 5, "OBJECTIVES", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(30, 41, 59)
    pdf.set_x(12)
    pdf.multi_cell(186, 5, _clean_latin1(audit.get("objectives") or "Objectives not specified."), new_x="LMARGIN", new_y="NEXT")

    # Section 3: Control Test Workpapers
    _section_heading(pdf, "3", "ISO/IEC 27001 Control Checklist & Workpapers")
    if not tests:
        pdf.set_font("Helvetica", "", 9.5)
        pdf.cell(0, 6, "No control tests recorded for this audit.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_fill_color(241, 245, 249)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(20, 7, "Control", border=1, fill=True)
        pdf.cell(68, 7, "Title", border=1, fill=True)
        pdf.cell(34, 7, "Status", border=1, fill=True)
        pdf.cell(20, 7, "Sample", border=1, fill=True, align="C")
        pdf.cell(44, 7, "Evidence Ref", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(30, 41, 59)
        for t in tests:
            pdf.cell(20, 6.5, _clean_latin1(t["control_id"]), border=1)
            pdf.cell(68, 6.5, _clean_latin1(t["control_title"])[:38], border=1)
            pdf.cell(34, 6.5, _clean_latin1(t["status"]), border=1)
            pdf.cell(20, 6.5, str(t.get("sample_size", 1)), border=1, align="C")
            pdf.cell(
                44,
                6.5,
                _clean_latin1(t.get("evidence_ref") or "-")[:24],
                border=1,
                new_x="LMARGIN",
                new_y="NEXT",
            )

    # Section 4: Findings & CAPA
    _section_heading(pdf, "4", "Findings, Nonconformities & CAPA")
    if not findings:
        pdf.set_font("Helvetica", "", 9.5)
        pdf.cell(0, 6, "No findings recorded for this audit.", new_x="LMARGIN", new_y="NEXT")
    else:
        for f in findings:
            pdf.set_fill_color(248, 250, 252)
            pdf.set_font("Helvetica", "B", 9.5)
            pdf.set_text_color(15, 23, 42)
            header_line = f"[{f['severity'].upper()}] {f['finding_id']} - {f['title']} ({f['status']})"
            pdf.cell(0, 7, _clean_latin1(header_line), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 8.5)
            pdf.set_text_color(51, 65, 85)
            meta_line = f"Control: {f.get('control_id') or 'N/A'} | Asset: {f.get('affected_asset') or 'N/A'} | Owner: {f.get('owner') or 'Unassigned'} | Due: {f.get('due_date') or 'TBD'}"
            pdf.cell(0, 5.5, _clean_latin1(meta_line), new_x="LMARGIN", new_y="NEXT")
            if f.get("condition"):
                pdf.set_x(12)
                pdf.multi_cell(186, 5, _clean_latin1(f"Condition: {f['condition']}"), new_x="LMARGIN", new_y="NEXT")
            if f.get("recommendation"):
                pdf.set_x(12)
                pdf.multi_cell(186, 5, _clean_latin1(f"Recommendation: {f['recommendation']}"), new_x="LMARGIN", new_y="NEXT")
            linked = [a for a in actions if a["finding_id"] == f["finding_id"]]
            for act in linked:
                pdf.set_x(12)
                pdf.multi_cell(
                    186,
                    5,
                    _clean_latin1(
                        f"Linked CAPA ({act['action_id']} - {act['status']}): {act['title']} | Owner: {act['owner']} | Due: {act['due_date']}"
                    ),
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
            pdf.ln(2)

    # Section 5: Evidence SHA-256 Integrity Manifest
    _section_heading(pdf, "5", "Evidence SHA-256 Integrity Manifest")
    if not evidence:
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, "No uploaded evidence artefacts linked directly to this audit.", new_x="LMARGIN", new_y="NEXT")
    else:
        pdf.set_font("Helvetica", "", 8)
        for ev in evidence:
            pdf.set_x(12)
            pdf.multi_cell(
                186,
                5,
                _clean_latin1(
                    f"{ev['evidence_id']} | {ev['file_name']} ({ev['file_size_bytes']} bytes) | Integrity: {ev['verified_status']}\nSHA-256: {ev['sha256_hash']}"
                ),
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.ln(1)

    return bytes(pdf.output())


def generate_executive_workbook() -> bytes:
    """Export all ISMS registers into a formatted multi-sheet Excel (.xlsx) workbook."""
    ensure_initialized()
    sheets = [
        ("Audits", "audits"),
        ("Control_Tests", "tests"),
        ("Findings", "findings"),
        ("CAPA_Actions", "actions"),
        ("SoA_Controls", "controls"),
        ("Risk_Register", "risks"),
        ("Regulatory_Map", "requirements"),
        ("Evidence_Hashes", "evidence"),
        ("Audit_Trail", "audit_logs"),
    ]
    buf = io.BytesIO()
    with get_connection() as conn, pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet_title, table_name in sheets:
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            df.to_excel(writer, sheet_name=sheet_title, index=False)
    return buf.getvalue()
