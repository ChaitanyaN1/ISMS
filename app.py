"""ISMS Audit Tracker home dashboard."""

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from isms_tracker.db import read_table
from isms_tracker.ui import PALETTE, TEAL, page_heading, plot_style, setup, metric_card

setup("Overview")
page_heading("SECURITY GOVERNANCE · AUDIT OPERATIONS", "ISMS Audit Tracker", "A practical workspace for audit coverage, control health, findings, and corrective actions.")

audits_all = read_table("audits")
findings_all = read_table("findings")
actions_all = read_table("actions")
controls_all = read_table("controls")
if audits_all.empty:
    st.info("Your workspace is empty. Add an audit from the Audit Register page or restore the demo dataset from Data Management.")
    st.stop()

with st.sidebar:
    st.markdown("### Dashboard filters")
    include_demo = st.toggle("Include demo records", value=True, help="Demo records are examples only. Turn this off to focus on records you entered.")

audits = audits_all if include_demo else audits_all[audits_all.record_type == "USER"]
findings = findings_all if include_demo else findings_all[findings_all.record_type == "USER"]
actions = actions_all if include_demo else actions_all[actions_all.record_type == "USER"]
controls = controls_all if include_demo else controls_all[controls_all.record_type == "USER"]
if not include_demo:
    valid_audits = set(audits.audit_id)
    valid_findings = set(findings.finding_id)
    findings = findings[findings.audit_id.isin(valid_audits)]
    actions = actions[actions.finding_id.isin(valid_findings)]
if audits.empty:
    st.info("No user audits are in this view. Add one from Audit Register, import a CSV in Data Management, or turn on demo records.")
    st.stop()

if include_demo and (audits.record_type == "DEMO").any():
    st.markdown("<div class='demo-banner'><b>DEMO DATA INCLUDED</b> · Illustrative sample records appear in this view. They are clearly identified in the registers and are not audit conclusions.</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='data-banner'><b>YOUR WORKSPACE</b> · Showing records you entered or imported. Demo records are hidden.</div>", unsafe_allow_html=True)

departments = sorted(audits.department.dropna().unique())
c1, c2 = st.columns([1, 3])
with c1:
    selected_depts = st.multiselect("Departments", departments, default=departments)
audits = audits[audits.department.isin(selected_depts)]
findings = findings[findings.audit_id.isin(audits.audit_id)]
actions = actions[actions.finding_id.isin(findings.finding_id)]

today = date.today().isoformat()
completed = int(audits.status.str.lower().isin(["completed", "closed"]).sum())
open_findings = int((~findings.status.str.lower().isin(["closed", "resolved", "verified"])).sum()) if not findings.empty else 0
open_actions = actions[~actions.status.str.lower().isin(["completed", "closed", "verified"])] if not actions.empty else actions
overdue = int(((open_actions.due_date != "") & (open_actions.due_date < today)).sum()) if not open_actions.empty else 0
compliance = pd.to_numeric(audits.compliance, errors="coerce").dropna()
avg_score = float(compliance.mean()) if not compliance.empty else None

kpis = st.columns(4, gap="medium")
with kpis[0]: metric_card("AUDITS IN SCOPE", str(len(audits)), f"{completed} completed · {len(audits)-completed} planned or in progress")
with kpis[1]: metric_card("AVERAGE COMPLIANCE", f"{avg_score:.0f}%" if avg_score is not None else "—", "Mean score across selected audits")
with kpis[2]: metric_card("OPEN FINDINGS", str(open_findings), f"{len(findings)} findings in selected scope")
with kpis[3]: metric_card("OVERDUE ACTIONS", str(overdue), "Open actions past their due date")

left, right = st.columns([1.35, 1], gap="medium")
with left:
    st.markdown('<h2 class="section-title">Compliance trend</h2>', unsafe_allow_html=True)
    trend = audits.copy()
    trend["compliance"] = pd.to_numeric(trend.compliance, errors="coerce")
    trend = trend.dropna(subset=["audit_date", "compliance"]).sort_values("audit_date")
    if trend.empty:
        st.info("Add audit dates and compliance scores to display a trend.")
    else:
        fig = px.line(trend, x="audit_date", y="compliance", markers=True, color_discrete_sequence=[TEAL], hover_name="title")
        fig.update_traces(line_width=3, marker_size=8, hovertemplate="%{x}<br>%{hovertext}<br>Compliance: %{y:.0f}%<extra></extra>")
        fig.update_yaxes(range=[0,105], ticksuffix="%", title=None)
        fig.update_xaxes(title=None)
        st.plotly_chart(plot_style(fig), use_container_width=True, config={"displayModeBar":False})
with right:
    st.markdown('<h2 class="section-title">Audit status</h2>', unsafe_allow_html=True)
    status = audits.status.value_counts().rename_axis("Status").reset_index(name="Audits")
    fig = px.pie(status, names="Status", values="Audits", hole=.68, color_discrete_sequence=PALETTE)
    fig.update_traces(textposition="inside", textinfo="percent", marker_line_color="white", marker_line_width=3)
    fig.update_layout(showlegend=True, legend=dict(orientation="h",y=-.08,x=0), annotations=[dict(text=f"{len(audits)}<br><span style='font-size:11px;color:#8190A0'>audits</span>",x=.5,y=.5,showarrow=False,font=dict(size=25,color="#10243A"))])
    st.plotly_chart(plot_style(fig), use_container_width=True, config={"displayModeBar":False})

left, right = st.columns(2, gap="medium")
with left:
    st.markdown('<h2 class="section-title">Compliance by department</h2>', unsafe_allow_html=True)
    by_dept = audits.assign(compliance=pd.to_numeric(audits.compliance, errors="coerce")).groupby("department", as_index=False).compliance.mean().dropna().sort_values("compliance")
    if by_dept.empty:
        st.info("No compliance scores available.")
    else:
        fig = px.bar(by_dept, x="compliance", y="department", orientation="h", text="compliance", color="compliance", color_continuous_scale=["#E9A23B","#58B6A8",TEAL])
        fig.update_traces(texttemplate="%{text:.0f}%",textposition="outside",cliponaxis=False)
        fig.update_xaxes(range=[0,112],ticksuffix="%",title=None)
        fig.update_yaxes(title=None,showgrid=False)
        fig.update_layout(coloraxis_showscale=False)
        st.plotly_chart(plot_style(fig,max(250,48*len(by_dept))),use_container_width=True,config={"displayModeBar":False})
with right:
    st.markdown('<h2 class="section-title">Control implementation</h2>', unsafe_allow_html=True)
    applicable = controls[controls.applicability == "Applicable"]
    if applicable.empty:
        st.info("Add or mark controls as applicable to see implementation coverage.")
    else:
        control_summary = applicable.implementation_status.value_counts().rename_axis("Implementation").reset_index(name="Controls")
        fig = px.pie(control_summary,names="Implementation",values="Controls",hole=.58,color_discrete_sequence=PALETTE)
        fig.update_traces(textposition="inside",textinfo="percent+label",marker_line_color="white",marker_line_width=3)
        st.plotly_chart(plot_style(fig),use_container_width=True,config={"displayModeBar":False})

st.markdown('<h2 class="section-title">Items needing attention</h2>', unsafe_allow_html=True)
tab1, tab2 = st.tabs(["Open findings", "Upcoming & overdue actions"])
with tab1:
    open_rows = findings[~findings.status.str.lower().isin(["closed","resolved","verified"])].copy()
    if open_rows.empty:
        st.success("No open findings in the selected scope.")
    else:
        open_rows = open_rows.merge(audits[["audit_id","title"]].rename(columns={"title":"Audit"}),on="audit_id",how="left")
        cols = [c for c in ["finding_id","title","Audit","control_id","severity","status","owner","due_date","record_type"] if c in open_rows]
        st.dataframe(open_rows[cols].rename(columns={"finding_id":"ID","title":"Finding","control_id":"Control","severity":"Severity","status":"Status","owner":"Owner","due_date":"Due","record_type":"Record type"}),hide_index=True,use_container_width=True)
with tab2:
    if open_actions.empty:
        st.success("No outstanding corrective actions.")
    else:
        action_view = open_actions.copy()
        due_soon_cutoff = (date.today() + timedelta(days=30)).isoformat()
        action_view["Timing"] = action_view.due_date.map(lambda value: "Overdue" if value and value < today else ("Due soon" if value and value <= due_soon_cutoff else "On track"))
        action_view = action_view.sort_values("due_date")
        cols = [c for c in ["action_id","title","owner","due_date","Timing","status","record_type"] if c in action_view]
        st.dataframe(action_view[cols].rename(columns={"action_id":"ID","title":"Action","owner":"Owner","due_date":"Due","status":"Status","record_type":"Record type"}),hide_index=True,use_container_width=True)
        st.caption("Due soon means due within 30 days. Overdue actions are past their due date and not marked complete.")

st.markdown("<div class='footnote'>This tracker supports audit operations. Verify applicability, evidence, scoring, and conclusions through your approved ISMS governance process.</div>",unsafe_allow_html=True)
