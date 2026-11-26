"""Evidence Repository (SHA-256 Integrity), Report Approval Sign-Off, PDF/Excel Exports & Hash-Chained Audit Log."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from isms_tracker.db import (
    ROOT_DIR,
    approve_audit_report,
    read_table,
    save_evidence_file,
    verify_audit_log_chain,
    verify_evidence_integrity,
)
from isms_tracker.reports import generate_audit_pdf, generate_executive_workbook
from isms_tracker.ui import current_user, metric_card, page_heading, require_permission, setup

setup("Evidence, Reports & Audit Trail")
page_heading(
    "ASSURANCE · SHA-256 INTEGRITY & SIGN-OFF",
    "Evidence Repository, Reports & Tamper-Evident Log",
    "Upload evidence with SHA-256 hashing and MIME/size checks, manage formal report sign-off, export PDF/Excel reports, and verify the hash-chained audit trail.",
)

user = current_user()
can_evidence = require_permission("manage_evidence")

evidence = read_table("evidence")
audits = read_table("audits")
logs = read_table("audit_logs")
chain_state = verify_audit_log_chain()

k1, k2, k3 = st.columns(3)
with k1:
    metric_card(
        "EVIDENCE ARTEFACTS",
        str(len(evidence)),
        f"{int((evidence.verified_status == 'Verified').sum()) if not evidence.empty else 0} SHA-256 verified",
    )
with k2:
    approved_cnt = int((audits.approval_status == "Approved").sum()) if not audits.empty else 0
    metric_card("APPROVED REPORTS", str(approved_cnt), f"Out of {len(audits)} total audits")
with k3:
    metric_card(
        "AUDIT LOG CHAIN",
        "INTACT" if chain_state["valid"] else "TAMPERED",
        f"{chain_state['checked_entries']} hash-chained events verified",
    )

tab_ev, tab_rep, tab_log = st.tabs(
    ["Evidence Repository (SHA-256)", "PDF / Excel Reports & Sign-Off", "Tamper-Evident Audit Trail"]
)

with tab_ev:
    st.dataframe(
        evidence[
            [
                "evidence_id",
                "title",
                "entity_type",
                "entity_id",
                "audit_id",
                "control_id",
                "file_name",
                "file_size_bytes",
                "mime_type",
                "sha256_hash",
                "verified_status",
                "uploaded_by",
            ]
        ]
        if not evidence.empty
        else evidence,
        hide_index=True,
        use_container_width=True,
    )

    c_ver, c_dl = st.columns(2)
    if not evidence.empty:
        with c_ver:
            sel_ev = st.selectbox("Select evidence for SHA-256 re-verification", evidence.evidence_id.tolist())
            if st.button("Verify SHA-256 Hash on Disk", use_container_width=True):
                res = verify_evidence_integrity(sel_ev, actor=user["username"], role=user["role"])
                if res["matches"]:
                    st.success(f"SHA-256 match confirmed: `{res['actual_sha256']}`")
                else:
                    st.error(f"Integrity failure ({res['status']}). Expected `{res['expected_sha256']}`")
        with c_dl:
            ev_row = evidence[evidence.evidence_id == sel_ev].iloc[0]
            disk_file = ROOT_DIR / ev_row["stored_path"]
            if disk_file.exists():
                st.download_button(
                    f"Download {ev_row['file_name']}",
                    data=disk_file.read_bytes(),
                    file_name=ev_row["file_name"],
                    mime=ev_row["mime_type"],
                    use_container_width=True,
                )

    with st.expander("Upload New Evidence Artefact (Max 20 MB · Automatic SHA-256)"):
        with st.form("evidence_upload_form"):
            e1, e2, e3 = st.columns(3)
            with e1:
                ev_title = st.text_input("Evidence Title", placeholder="Q4 Firewall Rule Review Sign-Off")
                ent_type = st.selectbox("Linked Entity Type", ["Audit", "Control", "Finding", "CAPA"])
            with e2:
                aud_id = st.selectbox("Audit ID", audits.audit_id.tolist() if not audits.empty else ["AUD-2026-001"])
                ctrl_id = st.text_input("Control ID", value="A.8.20")
            with e3:
                ent_id = st.text_input("Entity Record ID", value="AUD-2026-001")
                ev_notes = st.text_input("Evidence Notes")
            up_file = st.file_uploader(
                "Choose Evidence File (PDF, CSV, TXT, JSON, PNG, JPG, XLSX, DOCX)",
                type=["pdf", "csv", "txt", "json", "png", "jpg", "jpeg", "xlsx", "docx", "log"],
            )
            sub_ev = st.form_submit_button("Calculate SHA-256 & Store Evidence", disabled=not can_evidence)
            if sub_ev and can_evidence:
                if up_file is None:
                    st.error("Select a file to upload.")
                else:
                    try:
                        saved = save_evidence_file(
                            title=ev_title or up_file.name,
                            entity_type=ent_type,
                            entity_id=ent_id,
                            audit_id=aud_id,
                            control_id=ctrl_id,
                            filename=up_file.name,
                            content_type=up_file.type or "application/octet-stream",
                            data=up_file.getvalue(),
                            uploaded_by=user["full_name"],
                            actor_role=user["role"],
                            notes=ev_notes,
                        )
                        st.success(
                            f"Stored {saved['evidence_id']} ({saved['file_size_bytes']} bytes) · SHA-256: `{saved['sha256_hash']}`"
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

with tab_rep:
    if audits.empty:
        st.info("No audits available for report generation.")
    else:
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("### Export Selected Audit PDF Report")
            rep_audit = st.selectbox("Select Audit for PDF Export", audits.audit_id.tolist())
            pdf_bytes = generate_audit_pdf(rep_audit)
            st.download_button(
                f"Download PDF Report ({rep_audit})",
                data=pdf_bytes,
                file_name=f"SecureAudit_Report_{rep_audit}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        with r2:
            st.markdown("### Export Executive Multi-Sheet Excel Workbook")
            xlsx_bytes = generate_executive_workbook()
            st.download_button(
                "Download Full ISMS Workbook (.xlsx)",
                data=xlsx_bytes,
                file_name="SecureAudit_ISMS_Executive_Workbook.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

        st.divider()
        st.markdown("### Formal Report Review & Approval Sign-Off")
        with st.form("report_approval_form"):
            s1, s2, s3 = st.columns(3)
            with s1:
                sign_audit = st.selectbox("Audit Report", audits.audit_id.tolist(), key="sign_aud")
            with s2:
                sign_status = st.selectbox(
                    "Approval Decision",
                    ["Draft", "In Review", "Approved", "Changes Requested"],
                )
            with s3:
                sign_ver = st.text_input("Report Version", value="1.0")
            sign_notes = st.text_input("Reviewer Sign-Off Notes")
            sub_sign = st.form_submit_button("Record Review / Sign-Off Decision")
            if sub_sign:
                try:
                    approve_audit_report(
                        audit_id=sign_audit,
                        approval_status=sign_status,
                        reviewer_name=user["full_name"],
                        reviewer_role=user["role"],
                        report_version=sign_ver,
                        approval_notes=sign_notes,
                    )
                    st.success(f"Updated report {sign_audit} to '{sign_status}'.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))

with tab_log:
    if chain_state["valid"]:
        st.success(
            f"Cryptographic hash chain verified across {chain_state['checked_entries']} entries. Head hash: `{chain_state['head_hash']}`"
        )
    else:
        st.error(f"Chain integrity mismatch detected at log_id={chain_state['broken_log_id']}!")
    st.dataframe(
        logs.sort_values("log_id", ascending=False) if not logs.empty else logs,
        hide_index=True,
        use_container_width=True,
    )
