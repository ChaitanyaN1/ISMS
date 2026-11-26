"""Shared Streamlit styling, colour system, RBAC session sidebar, and chart helpers."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from isms_tracker.db import DEMO_ACCOUNTS, authenticate_user, ensure_initialized
from isms_tracker.security import has_permission

TEAL = "#0F766E"
NAVY = "#0F172A"
PALETTE = ["#2563EB", "#0F766E", "#D97706", "#DC2626", "#4F46E5", "#64748B"]


def setup(page_title: str) -> None:
    """Configure Streamlit page, inject systematic CSS tokens, and render RBAC sidebar."""
    ensure_initialized()
    st.set_page_config(
        page_title=f"{page_title} · ISMS Audit Tracker",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }
        .eyebrow {
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.08em;
            color: #2563EB;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .page-title {
            font-size: 30px;
            line-height: 36px;
            font-weight: 600;
            color: #0F172A;
            margin: 0 0 6px 0;
        }
        .page-sub {
            font-size: 15px;
            line-height: 24px;
            color: #475569;
            margin: 0 0 20px 0;
        }
        .section-title {
            font-size: 18px;
            line-height: 28px;
            font-weight: 600;
            color: #0F172A;
            margin: 20px 0 10px 0;
        }
        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }
        .kpi-label {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        .kpi-value {
            font-size: 28px;
            line-height: 34px;
            font-weight: 700;
            color: #0F172A;
            margin: 6px 0 4px 0;
        }
        .kpi-caption {
            font-size: 13px;
            color: #64748B;
        }
        .demo-banner {
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            color: #92400E;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 13px;
            margin-bottom: 16px;
        }
        .data-banner {
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            color: #065F46;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 13px;
            margin-bottom: 16px;
        }
        .footnote {
            margin-top: 32px;
            padding-top: 14px;
            border-top: 1px solid #E2E8F0;
            font-size: 12px;
            color: #64748B;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "auth_user" not in st.session_state:
        st.session_state.auth_user = {
            "user_id": "USR-001",
            "username": "admin",
            "full_name": "Alex Johnson",
            "email": "alex.johnson@secureaudit.local",
            "role": "Admin",
        }

    with st.sidebar:
        st.markdown("### 🛡️ ISMS Governance")
        user = st.session_state.auth_user
        if user:
            st.caption(
                f"Signed in as **{user['full_name']}**  \nRole: `{user['role']}`"
            )
            if st.button("Sign out / Switch role", use_container_width=True):
                st.session_state.auth_user = None
                st.rerun()
        else:
            st.warning("Sign in required for editing actions.")
            with st.form("sidebar_login_form"):
                uname = st.text_input("Username", placeholder="admin")
                pwd = st.text_input("Password", type="password", placeholder="Admin@27001!")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
                if submitted:
                    res = authenticate_user(uname, pwd)
                    if res.get("ok"):
                        st.session_state.auth_user = res["user"]
                        st.success("Authenticated.")
                        st.rerun()
                    else:
                        st.error(res.get("error", "Sign-in failed."))
            with st.expander("Demo accounts (local testing)"):
                for _, u, _, _, role, pw in DEMO_ACCOUNTS:
                    st.caption(f"**{role}**: `{u}` / `{pw}`")
        st.divider()


def current_user() -> dict[str, Any]:
    """Return active Streamlit session user or Viewer fallback."""
    return st.session_state.get("auth_user") or {
        "user_id": "GUEST",
        "username": "guest",
        "full_name": "Guest Viewer",
        "role": "Viewer",
    }


def require_permission(permission: str) -> bool:
    """Return True if active user holds permission, otherwise render notice."""
    user = current_user()
    allowed = has_permission(user["role"], permission)
    if not allowed:
        st.info(
            f"Read-only view for role **{user['role']}**. Sign in with an authorized role to modify records."
        )
    return allowed


def page_heading(eyebrow: str, title: str, subtitle: str) -> None:
    """Render standardized page header."""
    st.markdown(
        f"""
        <div class="eyebrow">{html.escape(eyebrow)}</div>
        <h1 class="page-title">{html.escape(title)}</h1>
        <p class="page-sub">{html.escape(subtitle)}</p>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, caption: str) -> None:
    """Render accessible KPI metric card."""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{html.escape(label)}</div>
            <div class="kpi-value">{html.escape(value)}</div>
            <div class="kpi-caption">{html.escape(caption)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def plot_style(fig: Any, height: int = 300) -> Any:
    """Apply clean, consistent layout styling to Plotly figures."""
    fig.update_layout(
        height=height,
        margin=dict(l=12, r=18, t=16, b=16),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope, sans-serif", size=12, color="#1E293B"),
        xaxis=dict(gridcolor="#F1F5F9", zeroline=False),
        yaxis=dict(gridcolor="#F1F5F9", zeroline=False),
    )
    return fig
