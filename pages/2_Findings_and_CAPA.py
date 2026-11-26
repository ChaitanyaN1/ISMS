"""Findings and Corrective/Preventive Actions (CAPA) workflow page."""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from isms_tracker.db import append_audit_log, get_connection, read_table
from isms_tracker.ui import current_user, metric_card, page_heading, require_permission, setup

setup("Findings & CAPA")
page_heading(
    "CLAUSE 10.2 · NONCONFORMITY & REMEDIATION",
    "Findings & CAPA Register",
    "Document audit findings with criteria, condition, root cause, impact, and track linked corrective/preventive actions.",
)

user = current_user()
can_findings = require_permission("manage_findings")
can_actions = has_capa := (user["role"] in {"Admin", "Auditor", "Risk Owner"})

audits = read_table("audits")
findings = read_table("findings")
actions = read_table("actions")

k1, k2, k3, k4 = st.columns(4)
crit = int((findings.severity == "Critical").sum()) if not findings.empty else 0
high = int((findings.severity == "High").sum()) if not findings.empty else 0
open_f = int((~findings.status.str.lower().isin(["resolved", "closed", "verified"])).sum()) if not findings.empty else 0
resolved_f = len(findings) - open_f

with k1:
    metric_card("TOTAL FINDINGS", str(len(findings)), "Across all tracked audits")
with k2:
    metric_card("CRITICAL SEVERITY", str(crit), f"{high} High severity findings")
with k3:
    metric_card("OPEN / REMEDIATION", str(open_f), "Require verification before closure")
with k4:
    metric_card("RESOLVED / CLOSED", str(resolved_f), f"{len(actions)} CAPA records linked")

tab_f, tab_a = st.tabs(["Findings Register", "Corrective & Preventive Actions (CAPA)"])

with tab_f:
    sev_filter = st.multiselect(
        "Filter by severity",
        ["Critical", "High", "Medium", "Low"],
        default=["Critical", "High", "Medium", "Low"],
    )
    f_view = findings[findings.severity.isin(sev_filter)] if not findings.empty else findings
    st.dataframe(
        f_view[
            [
                "finding_id",
                "audit_id",
                "control_id",
                "title",
                "severity",
                "status",
                "affected_asset",
                "owner",
                "due_date",
                "record_type",
            ]
        ]
        if not f_view.empty
        else f_view,
        hide_index=True,
        use_container_width=True,
    )

    with st.expander("Log or Update Finding", expanded=False):
        with st.form("finding_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                fid = st.text_input("Finding ID", value=f"FND-2026-{len(findings)+10:03d}")
                aid = st.selectbox("Audit ID", audits.audit_id.tolist() if not audits.empty else ["AUD-2026-001"])
                cid = st.text_input("Control Reference", value="A.8.5")
            with c2:
                ftitle = st.text_input("Finding Title", placeholder="Missing MFA on Privileged Console")
                severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
                fstatus = st.selectbox("Status", ["Open", "In Remediation", "Resolved", "Closed"])
            with c3:
                asset = st.text_input("Affected Asset", placeholder="Cloud Console")
                owner = st.text_input("Assigned Owner", value=user["full_name"])
                due = st.date_input("Target Due Date", value=date.today() + timedelta(days=30))
            criteria = st.text_input("Criteria", placeholder="ISO/IEC 27001:2022 Annex A.8.5")
            condition = st.text_area("Condition (Observed issue)")
            cause = st.text_input("Root Cause")
            impact = st.text_input("Business / Security Impact")
            recommendation = st.text_area("Auditor Recommendation")
            sub_f = st.form_submit_button("Save Finding", disabled=not can_findings)
            if sub_f and can_findings:
                if not fid.strip() or not ftitle.strip():
                    st.error("Finding ID and Title are required.")
                else:
                    with get_connection() as conn:
                        conn.execute(
                            """
                            INSERT OR REPLACE INTO findings (
                                finding_id, audit_id, control_id, title, severity, status,
                                affected_asset, criteria, condition, cause, impact,
                                recommendation, owner, found_date, due_date, record_type
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
                            """,
                            (
                                fid.strip(),
                                aid,
                                cid.strip(),
                                ftitle.strip(),
                                severity,
                                fstatus,
                                asset.strip(),
                                criteria.strip(),
                                condition.strip(),
                                cause.strip(),
                                impact.strip(),
                                recommendation.strip(),
                                owner.strip(),
                                date.today().isoformat(),
                                due.isoformat(),
                            ),
                        )
                        append_audit_log(
                            conn,
                            actor=user["username"],
                            role=user["role"],
                            action="FINDING_SAVED",
                            entity_type="Finding",
                            entity_id=fid.strip(),
                            details=f"[{severity}] {ftitle.strip()} ({fstatus})",
                        )
                        conn.commit()
                    st.success(f"Finding {fid.strip()} saved.")
                    st.rerun()

with tab_a:
    st.dataframe(actions, hide_index=True, use_container_width=True)
    with st.expander("Create or Update CAPA Action", expanded=False):
        with st.form("capa_form"):
            a1, a2, a3 = st.columns(3)
            with a1:
                act_id = st.text_input("CAPA ID", value=f"CAPA-2026-{len(actions)+10:03d}")
                linked_fid = st.selectbox(
                    "Linked Finding",
                    findings.finding_id.tolist() if not findings.empty else ["FND-2026-001"],
                )
            with a2:
                act_title = st.text_input("Action Title", placeholder="Bind FIDO2 Keys to Admin Accounts")
                act_type = st.selectbox("Action Type", ["Corrective", "Preventive"])
            with a3:
                act_owner = st.text_input("Action Owner", value=user["full_name"])
                act_due = st.date_input("Target Completion Date", value=date.today() + timedelta(days=21))
                act_status = st.selectbox("Status", ["Open", "In Progress", "Completed", "Verified"])
            corr = st.text_area("Corrective Action Plan")
            prev = st.text_area("Preventive Action (Recurrence Prevention)")
            verif = st.text_input("Verification & Evidence Notes")
            sub_a = st.form_submit_button("Save CAPA Record", disabled=not can_actions)
            if sub_a and can_actions:
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO actions (
                            action_id, finding_id, title, action_type, owner, due_date,
                            status, corrective_action, preventive_action,
                            verification_notes, evidence_notes, record_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
                        """,
                        (
                            act_id.strip(),
                            linked_fid,
                            act_title.strip() or "Remediation Action",
                            act_type,
                            act_owner.strip(),
                            act_due.isoformat(),
                            act_status,
                            corr.strip(),
                            prev.strip(),
                            verif.strip(),
                            verif.strip(),
                        ),
                    )
                    append_audit_log(
                        conn,
                        actor=user["username"],
                        role=user["role"],
                        action="CAPA_SAVED",
                        entity_type="CAPA",
                        entity_id=act_id.strip(),
                        details=f"Linked to {linked_fid} -> {act_status}",
                    )
                    conn.commit()
                st.success(f"CAPA {act_id.strip()} saved.")
                st.rerun()
