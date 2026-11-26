"""ISO/IEC 27001:2022 Annex A Control Register & Statement of Applicability (SoA)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from isms_tracker.catalogue import ISO_27001_CLAUSES
from isms_tracker.db import append_audit_log, get_connection, read_table
from isms_tracker.ui import current_user, metric_card, page_heading, require_permission, setup

setup("Control Register & SoA")
page_heading(
    "CLAUSE 6.1.3 · ANNEX A REFERENCE",
    "Control Register & Statement of Applicability",
    "Review Annex A control domains, applicability justifications, implementation status, and linked open findings.",
)

user = current_user()
can_edit = require_permission("manage_controls")

controls = read_table("controls")
findings = read_table("findings")

if not findings.empty:
    f_counts = findings.groupby("control_id").size().rename("findings_count")
    controls = controls.merge(f_counts, on="control_id", how="left")
    controls["findings_count"] = controls["findings_count"].fillna(0).astype(int)
else:
    controls["findings_count"] = 0

applicable_count = int((controls.applicability == "Applicable").sum())
impl_count = int(
    ((controls.applicability == "Applicable") & (controls.implementation_status == "Implemented")).sum()
)
partial_count = int(
    ((controls.applicability == "Applicable") & (controls.implementation_status == "Partially Implemented")).sum()
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("CATALOGUE CONTROLS", str(len(controls)), "ISO/IEC 27001:2022 4-domain selection")
with c2:
    metric_card("APPLICABLE IN SoA", str(applicable_count), f"{len(controls) - applicable_count} marked Not Applicable")
with c3:
    metric_card("IMPLEMENTED", str(impl_count), f"{partial_count} Partially Implemented")
with c4:
    cov = round((impl_count / applicable_count) * 100) if applicable_count else 0
    metric_card("IMPLEMENTATION COVERAGE", f"{cov}%", "Implemented / Applicable controls")

tab_soa, tab_clauses = st.tabs(
    ["Annex A Statement of Applicability", "ISO/IEC 27001:2022 Clauses & 2024 Amendment"]
)

with tab_soa:
    domains = ["All"] + sorted(controls.domain.unique().tolist())
    sel_dom = st.selectbox("Filter by Annex A domain", domains)
    view = controls if sel_dom == "All" else controls[controls.domain == sel_dom]

    st.dataframe(
        view[
            [
                "control_id",
                "domain",
                "title",
                "applicability",
                "implementation_status",
                "owner",
                "findings_count",
                "nist_csf",
                "soc2",
                "justification",
            ]
        ],
        hide_index=True,
        use_container_width=True,
    )

    with st.expander("Update Control Applicability & Implementation Status"):
        with st.form("soa_update_form"):
            u1, u2, u3 = st.columns(3)
            with u1:
                ctrl_id = st.selectbox("Control ID", controls.control_id.tolist())
            with u2:
                app_val = st.selectbox("Applicability", ["Applicable", "Not Applicable"])
            with u3:
                impl_val = st.selectbox(
                    "Implementation Status",
                    ["Implemented", "Partially Implemented", "Not Implemented", "Not Applicable"],
                )
            owner_val = st.text_input("Control Owner", value=user["full_name"])
            just_val = st.text_area(
                "SoA Inclusion / Exclusion Justification",
                placeholder="Document risk assessment or contractual rationale...",
            )
            sub_c = st.form_submit_button("Update SoA Entry", disabled=not can_edit)
            if sub_c and can_edit:
                with get_connection() as conn:
                    conn.execute(
                        """
                        UPDATE controls
                        SET applicability = ?, implementation_status = ?, owner = ?,
                            justification = COALESCE(NULLIF(?, ''), justification),
                            record_type = 'USER'
                        WHERE control_id = ?
                        """,
                        (app_val, impl_val, owner_val.strip(), just_val.strip(), ctrl_id),
                    )
                    append_audit_log(
                        conn,
                        actor=user["username"],
                        role=user["role"],
                        action="SOA_CONTROL_UPDATED",
                        entity_type="Control",
                        entity_id=ctrl_id,
                        details=f"{app_val} | {impl_val}",
                    )
                    conn.commit()
                st.success(f"Updated {ctrl_id} in Statement of Applicability.")
                st.rerun()

with tab_clauses:
    st.info(
        "Reference aid only: includes plain-language summaries of ISO/IEC 27001:2022 Clauses 4–10 and Amendment 1:2024 (Climate Action). Always consult licensed ISO standards."
    )
    st.dataframe(pd.DataFrame(ISO_27001_CLAUSES), hide_index=True, use_container_width=True)
