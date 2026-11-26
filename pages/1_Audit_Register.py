"""Audit Register & Control Test Workpapers page."""

from __future__ import annotations

from datetime import date

import streamlit as st

from isms_tracker.catalogue import ANNEX_A_CONTROLS_CATALOGUE
from isms_tracker.db import (
    append_audit_log,
    get_connection,
    read_table,
    recalculate_audit_compliance,
)
from isms_tracker.ui import current_user, page_heading, require_permission, setup

setup("Audit Register")
page_heading(
    "AUDIT PROGRAMME · CLAUSE 9.2",
    "Audit Register & Workpapers",
    "Plan internal and readiness audits, define scope and objectives, and record control test workpapers.",
)

user = current_user()
can_edit = require_permission("manage_audits")

audits = read_table("audits")
tests = read_table("tests")

col_search, col_status = st.columns([2, 1])
with col_search:
    q = st.text_input("Search audits", placeholder="Search by ID, title, department, or lead auditor")
with col_status:
    statuses = ["All"] + sorted(audits.status.dropna().unique().tolist()) if not audits.empty else ["All"]
    status_filter = st.selectbox("Status filter", statuses)

filtered = audits.copy()
if q:
    mask = (
        filtered.audit_id.str.contains(q, case=False, na=False)
        | filtered.title.str.contains(q, case=False, na=False)
        | filtered.department.str.contains(q, case=False, na=False)
        | filtered.lead_auditor.str.contains(q, case=False, na=False)
    )
    filtered = filtered[mask]
if status_filter != "All":
    filtered = filtered[filtered.status == status_filter]

st.dataframe(
    filtered[
        [
            "audit_id",
            "title",
            "department",
            "audit_type",
            "status",
            "audit_date",
            "lead_auditor",
            "compliance",
            "approval_status",
            "record_type",
        ]
    ],
    hide_index=True,
    use_container_width=True,
)

tab_create, tab_tests, tab_delete = st.tabs(
    ["Create / Update Audit", "Control Test Workpapers", "Remove Audit"]
)

with tab_create:
    with st.form("audit_upsert_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            audit_id = st.text_input("Audit ID", value=f"AUD-2026-{len(audits)+10:03d}")
            department = st.text_input("Department", value="Cloud Operations")
            audit_date = st.date_input("Audit Date", value=date.today())
        with c2:
            title = st.text_input("Audit Title", placeholder="Q4 Access Governance Audit")
            audit_type = st.selectbox("Audit Type", ["ISO 27001", "SOC 2", "Internal Audit", "Supplier Review"])
            status = st.selectbox("Status", ["Planned", "In Progress", "Completed", "Closed"])
        with c3:
            lead_auditor = st.text_input("Lead Auditor", value=user["full_name"])
            organization = st.text_input("Organization", value="TechCorp International")
            compliance = st.number_input("Compliance Score (%)", min_value=0.0, max_value=100.0, value=75.0)
        scope = st.text_area("Scope", placeholder="Systems, locations, and processes covered...")
        objectives = st.text_area("Objectives", placeholder="Verify Annex A control design and operating effectiveness...")
        submitted = st.form_submit_button("Save Audit Record", disabled=not can_edit)
        if submitted and can_edit:
            if not audit_id.strip() or not title.strip():
                st.error("Audit ID and Title are required.")
            else:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT INTO audits (
                            audit_id, title, organization, department, audit_type, status,
                            audit_date, start_date, end_date, lead_auditor, created_by,
                            scope, objectives, compliance, record_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
                        ON CONFLICT(audit_id) DO UPDATE SET
                            title=excluded.title,
                            organization=excluded.organization,
                            department=excluded.department,
                            audit_type=excluded.audit_type,
                            status=excluded.status,
                            audit_date=excluded.audit_date,
                            lead_auditor=excluded.lead_auditor,
                            scope=excluded.scope,
                            objectives=excluded.objectives,
                            compliance=excluded.compliance
                        """,
                        (
                            audit_id.strip(),
                            title.strip(),
                            organization.strip(),
                            department.strip(),
                            audit_type,
                            status,
                            audit_date.isoformat(),
                            audit_date.isoformat(),
                            audit_date.isoformat(),
                            lead_auditor.strip(),
                            user["full_name"],
                            scope.strip(),
                            objectives.strip(),
                            float(compliance),
                        ),
                    )
                    append_audit_log(
                        conn,
                        actor=user["username"],
                        role=user["role"],
                        action="AUDIT_SAVED",
                        entity_type="Audit",
                        entity_id=audit_id.strip(),
                        details=f"Saved audit '{title.strip()}' ({status}).",
                    )
                    conn.commit()
                st.success(f"Audit {audit_id.strip()} saved.")
                st.rerun()

with tab_tests:
    if audits.empty:
        st.info("Create an audit first to log control test workpapers.")
    else:
        selected_audit = st.selectbox("Select audit", audits.audit_id.tolist())
        audit_tests = tests[tests.audit_id == selected_audit]
        st.dataframe(audit_tests, hide_index=True, use_container_width=True)

        ctrl_options = {
            f"{c['control_id']} — {c['title']}": c for c in ANNEX_A_CONTROLS_CATALOGUE
        }
        with st.form("test_workpaper_form"):
            t1, t2, t3 = st.columns(3)
            with t1:
                test_id = st.text_input("Test ID", value=f"TST-{len(tests)+25:03d}")
                ctrl_choice = st.selectbox("Annex A Control", list(ctrl_options.keys()))
            with t2:
                test_status = st.selectbox(
                    "Test Result",
                    ["Compliant", "Partially Compliant", "Non-Compliant", "Not Applicable", "Not Tested"],
                )
                sample_size = st.number_input("Sample Size", min_value=1, max_value=500, value=15)
            with t3:
                evidence_ref = st.text_input("Evidence Reference", placeholder="evidence_doc_c1.pdf")
                tested_at = st.date_input("Tested Date", value=date.today())
            procedure = st.text_area("Test Procedure", placeholder="Describe inspection, inquiry, or re-performance steps...")
            notes = st.text_area("Auditor Notes", placeholder="Observed results across sampled items...")
            save_test = st.form_submit_button("Record Workpaper & Recalculate Compliance", disabled=not can_edit)
            if save_test and can_edit:
                ctrl_meta = ctrl_options[ctrl_choice]
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO tests (
                            test_id, audit_id, control_id, control_title, domain, procedure,
                            sample_size, status, auditor_notes, evidence_ref, tested_by, tested_at, record_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
                        """,
                        (
                            test_id.strip(),
                            selected_audit,
                            ctrl_meta["control_id"],
                            ctrl_meta["title"],
                            ctrl_meta["domain"],
                            procedure.strip(),
                            int(sample_size),
                            test_status,
                            notes.strip(),
                            evidence_ref.strip(),
                            user["full_name"],
                            tested_at.isoformat(),
                        ),
                    )
                    recalculate_audit_compliance(conn, selected_audit)
                    append_audit_log(
                        conn,
                        actor=user["username"],
                        role=user["role"],
                        action="WORKPAPER_RECORDED",
                        entity_type="Test",
                        entity_id=test_id.strip(),
                        details=f"{selected_audit} / {ctrl_meta['control_id']} -> {test_status}",
                    )
                    conn.commit()
                st.success(f"Workpaper {test_id.strip()} saved and compliance score updated.")
                st.rerun()

with tab_delete:
    if not audits.empty:
        del_id = st.selectbox("Audit ID to delete", audits.audit_id.tolist(), key="del_audit_select")
        if st.button("Delete Selected Audit", type="secondary", disabled=not can_edit):
            with get_connection() as conn:
                conn.execute("DELETE FROM audits WHERE audit_id = ?", (del_id,))
                append_audit_log(
                    conn,
                    actor=user["username"],
                    role=user["role"],
                    action="AUDIT_DELETED",
                    entity_type="Audit",
                    entity_id=del_id,
                    details="Deleted audit from register.",
                )
                conn.commit()
            st.success(f"Audit {del_id} removed.")
            st.rerun()
