"""Data Management: CSV import/export, JSON backup & restore check, and DEMO data controls."""

from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from isms_tracker.db import (
    ROOT_DIR,
    export_backup_json,
    import_audits_csv,
    read_table,
    remove_demo_records,
    restore_demo_records,
    validate_backup_payload,
)
from isms_tracker.ui import current_user, page_heading, require_permission, setup

setup("Data Management")
page_heading(
    "PORTABILITY & GOVERNANCE",
    "Data Management & Safe Demo Controls",
    "Import append-only audit CSV files, download CSV/JSON backups with SHA-256 manifests, and manage DEMO records safely.",
)

user = current_user()
can_demo = require_permission("manage_demo_data")

tab_imp, tab_exp, tab_demo = st.tabs(
    ["Append-Only CSV Import", "CSV & Verified JSON Backup", "Demo Dataset Controls"]
)

with tab_imp:
    st.markdown(
        "Required CSV columns: `audit_id`, `title`, `department`, `status`, `audit_date`. Existing IDs are skipped and never overwritten."
    )
    tpl_path = ROOT_DIR / "data" / "audit_import_template.csv"
    if tpl_path.exists():
        st.download_button(
            "Download CSV Import Template",
            data=tpl_path.read_bytes(),
            file_name="audit_import_template.csv",
            mime="text/csv",
        )
    uploaded = st.file_uploader("Upload Audit Register CSV", type=["csv"])
    if uploaded is not None:
        if st.button("Import Audits (Append-Only)", disabled=not can_demo):
            try:
                res = import_audits_csv(
                    uploaded.getvalue(), actor=user["username"], role=user["role"]
                )
                st.success(
                    f"Imported {res['imported']} new audit(s); skipped {res['skipped']} existing ID(s)."
                )
            except Exception as exc:
                st.error(str(exc))

with tab_exp:
    c1, c2, c3, c4 = st.columns(4)
    for col, (label, tname) in zip(
        [c1, c2, c3, c4],
        [
            ("Audits CSV", "audits"),
            ("Findings CSV", "findings"),
            ("CAPA Actions CSV", "actions"),
            ("Controls SoA CSV", "controls"),
        ],
    ):
        df = read_table(tname)
        with col:
            st.download_button(
                f"Download {label}",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"isms_{tname}.csv",
                mime="text/csv",
                use_container_width=True,
            )

    st.divider()
    st.markdown("### Complete JSON Backup with SHA-256 Manifest")
    backup_obj = export_backup_json()
    backup_bytes = json.dumps(backup_obj, indent=2).encode("utf-8")
    st.code(f"Backup Manifest SHA-256: {backup_obj['manifest_sha256']}", language="text")
    st.download_button(
        "Download Complete Verified JSON Backup",
        data=backup_bytes,
        file_name="isms_tracker_backup.json",
        mime="application/json",
    )

    st.markdown("#### Verify Backup File Integrity (Dry-Run Restore Check)")
    verify_file = st.file_uploader("Upload JSON Backup to Verify Manifest SHA-256", type=["json"])
    if verify_file is not None:
        try:
            parsed = json.loads(verify_file.getvalue().decode("utf-8"))
            v_res = validate_backup_payload(parsed)
            if v_res["valid"]:
                st.success(
                    f"Backup manifest verified! SHA-256 matches `{v_res['actual_sha256']}`. Record counts: {v_res['record_counts']}"
                )
            else:
                st.error("Manifest SHA-256 mismatch or invalid backup structure.")
        except Exception as exc:
            st.error(f"Invalid JSON file: {exc}")

with tab_demo:
    st.markdown(
        "Demo records are tagged `DEMO` and kept distinct from `USER` records. Restoring demo records inserts missing sample rows without overwriting your `USER` records."
    )
    d1, d2 = st.columns(2)
    with d1:
        if st.button("Restore Missing Demo Records", use_container_width=True, disabled=not can_demo):
            restored = restore_demo_records(actor=user["username"], role=user["role"])
            st.success(f"Restored {restored} missing DEMO record(s).")
    with d2:
        if st.button("Remove Demo Records (Keep USER Data)", use_container_width=True, disabled=not can_demo):
            removed = remove_demo_records(actor=user["username"], role=user["role"])
            st.warning(f"Removed {removed} DEMO record(s). USER records remain intact.")
