"""Local User Administration & Authentication Security Policy page."""

from __future__ import annotations

import streamlit as st

from isms_tracker.db import append_audit_log, get_connection, read_table
from isms_tracker.security import (
    hash_password,
    utc_now_iso,
    validate_password_strength,
)
from isms_tracker.ui import current_user, page_heading, require_permission, setup

setup("User & Role Administration")
page_heading(
    "RBAC · AUTHENTICATION ASSURANCE",
    "User & Role Administration",
    "Manage local role-based accounts (Admin, Auditor, Risk Owner, Viewer), inspect scrypt password policy, and unlock locked accounts.",
)

user = current_user()
is_admin = require_permission("manage_users")

users_df = read_table("users")
safe_cols = [
    "user_id",
    "username",
    "full_name",
    "email",
    "role",
    "failed_attempts",
    "locked_until",
    "is_active",
    "last_login",
    "record_type",
]
st.dataframe(users_df[safe_cols], hide_index=True, use_container_width=True)

tab_add, tab_unlock = st.tabs(["Provision Local Account", "Unlock / Reset Account Lockout"])

with tab_add:
    with st.form("create_user_form"):
        u1, u2, u3 = st.columns(3)
        with u1:
            uname = st.text_input("Username", placeholder="priya.nair")
            full_name = st.text_input("Full Name", placeholder="Priya Nair")
        with u2:
            email = st.text_input("Email", placeholder="priya.nair@secureaudit.local")
            role = st.selectbox("Assigned Role", ["Auditor", "Risk Owner", "Viewer", "Admin"])
        with u3:
            pwd = st.text_input(
                "Password (min 10 chars, upper, lower, digit)",
                type="password",
            )
        sub_u = st.form_submit_button("Create Salted Scrypt Account", disabled=not is_admin)
        if sub_u and is_admin:
            ok, msg = validate_password_strength(pwd)
            if not uname.strip() or not full_name.strip() or not email.strip():
                st.error("Username, Full Name, and Email are required.")
            elif not ok:
                st.error(msg)
            else:
                pwd_hash, salt_hex = hash_password(pwd)
                uid = f"USR-{len(users_df)+10:03d}"
                try:
                    with get_connection() as conn:
                        conn.execute(
                            """
                            INSERT INTO users (
                                user_id, username, full_name, email, role, password_hash,
                                salt_hex, failed_attempts, locked_until, is_active, created_at, record_type
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, '', 1, ?, 'USER')
                            """,
                            (
                                uid,
                                uname.strip().lower(),
                                full_name.strip(),
                                email.strip().lower(),
                                role,
                                pwd_hash,
                                salt_hex,
                                utc_now_iso(),
                            ),
                        )
                        append_audit_log(
                            conn,
                            actor=user["username"],
                            role=user["role"],
                            action="USER_CREATED",
                            entity_type="User",
                            entity_id=uid,
                            details=f"Created user '{uname.strip()}' with role {role}.",
                        )
                        conn.commit()
                    st.success(f"Account {uname.strip()} provisioned with salted scrypt hash.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not create user: {exc}")

with tab_unlock:
    target_user = st.selectbox("Select account to clear failed attempts / lockout", users_df.username.tolist())
    if st.button("Reset Lockout Counter", disabled=not is_admin):
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET failed_attempts = 0, locked_until = '' WHERE username = ?",
                (target_user,),
            )
            append_audit_log(
                conn,
                actor=user["username"],
                role=user["role"],
                action="USER_UNLOCKED",
                entity_type="User",
                entity_id=target_user,
                details="Cleared failed login counter and lockout window.",
            )
            conn.commit()
        st.success(f"Account '{target_user}' unlocked.")
        st.rerun()
