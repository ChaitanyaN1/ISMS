"""Risk Register & Cross-Framework Regulatory Mapping page."""

from __future__ import annotations

import streamlit as st

from isms_tracker.db import append_audit_log, get_connection, read_table
from isms_tracker.ui import current_user, metric_card, page_heading, require_permission, setup

setup("Risk & Regulatory Governance")
page_heading(
    "CLAUSE 6.1.2 · RISK ASSESSMENT & TREATMENT",
    "Risk Register & Cross-Framework Mappings",
    "Track information security risks, inherent vs residual risk scores, Annex A treatment controls, and illustrative NIST CSF 2.0 / SOC 2 mappings.",
)

user = current_user()
can_edit = require_permission("manage_risks")

risks = read_table("risks")
requirements = read_table("requirements")

high_risks = int((risks.inherent_score >= 15).sum()) if not risks.empty else 0
avg_res = float(risks.residual_score.mean()) if not risks.empty else 0.0

k1, k2, k3 = st.columns(3)
with k1:
    metric_card("TRACKED RISKS", str(len(risks)), f"{high_risks} High/Critical inherent risk items")
with k2:
    metric_card("MEAN RESIDUAL SCORE", f"{avg_res:.1f} / 25", "Post-treatment 5x5 risk matrix average")
with k3:
    metric_card("MAPPED FRAMEWORKS", "3", "ISO 27001:2022 · NIST CSF 2.0 · SOC 2 (Illustrative)")

tab_r, tab_m = st.tabs(["Information Security Risk Register", "Illustrative Framework Mappings"])

with tab_r:
    st.dataframe(risks, hide_index=True, use_container_width=True)
    with st.expander("Add or Update Risk Assessment Entry"):
        with st.form("risk_form"):
            r1, r2, r3 = st.columns(3)
            with r1:
                risk_id = st.text_input("Risk ID", value=f"RSK-{len(risks)+10:03d}")
                asset = st.text_input("Information Asset", placeholder="Customer Database")
                owner = st.text_input("Risk Owner", value=user["full_name"])
            with r2:
                title = st.text_input("Risk Scenario Title", placeholder="Unauthorized Access to Production Backups")
                likelihood = st.slider("Inherent Likelihood (1-5)", 1, 5, 3)
                impact = st.slider("Inherent Impact (1-5)", 1, 5, 4)
            with r3:
                treatment = st.selectbox("Treatment Option", ["Mitigate", "Accept", "Transfer", "Avoid"])
                linked_controls = st.text_input("Linked Annex A Controls", value="A.8.13, A.8.24")
                residual = st.slider("Residual Risk Score (1-25)", 1, 25, 6)
            threat = st.text_input("Threat & Vulnerability Description")
            status = st.selectbox("Status", ["Open", "Treatment In Progress", "Monitored", "Closed"])
            sub_r = st.form_submit_button("Save Risk Entry", disabled=not can_edit)
            if sub_r and can_edit:
                inherent = int(likelihood) * int(impact)
                with get_connection() as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO risks (
                            risk_id, title, asset, threat, likelihood, impact,
                            inherent_score, treatment, linked_controls, residual_score,
                            owner, status, record_type
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
                        """,
                        (
                            risk_id.strip(),
                            title.strip() or "Untitled Risk",
                            asset.strip(),
                            threat.strip(),
                            int(likelihood),
                            int(impact),
                            inherent,
                            treatment,
                            linked_controls.strip(),
                            int(residual),
                            owner.strip(),
                            status,
                        ),
                    )
                    append_audit_log(
                        conn,
                        actor=user["username"],
                        role=user["role"],
                        action="RISK_SAVED",
                        entity_type="Risk",
                        entity_id=risk_id.strip(),
                        details=f"Inherent={inherent}, Residual={residual}, Treatment={treatment}",
                    )
                    conn.commit()
                st.success(f"Risk {risk_id.strip()} saved.")
                st.rerun()

with tab_m:
    st.warning(
        "Governance Notice: Cross-framework mappings between ISO/IEC 27001:2022, Amd 1:2024, NIST CSF 2.0, and SOC 2 are illustrative reference aids and require qualified legal/compliance review."
    )
    st.dataframe(requirements, hide_index=True, use_container_width=True)
