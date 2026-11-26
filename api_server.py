"""FastAPI REST server backing the SecureAudit React + TypeScript Web Tracker.

Shares the exact SQLite database (`isms_tracker.db`), scrypt RBAC auth, failed-login
lockout, SHA-256 evidence hashing, report approval workflow, hash-chained audit trail,
and PDF/Excel/JSON generators with the Streamlit interface.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import json
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field

from isms_tracker.catalogue import ANNEX_A_CONTROLS_CATALOGUE, ISO_27001_CLAUSES
from isms_tracker.db import (
    DEMO_ACCOUNTS,
    ROOT_DIR,
    append_audit_log,
    approve_audit_report,
    authenticate_user,
    ensure_initialized,
    export_backup_json,
    get_connection,
    get_session_user,
    import_audits_csv,
    recalculate_audit_compliance,
    remove_demo_records,
    restore_demo_records,
    save_evidence_file,
    validate_backup_payload,
    verify_audit_log_chain,
    verify_evidence_integrity,
)
from isms_tracker.reports import generate_audit_pdf, generate_executive_workbook
from isms_tracker.security import (
    has_permission,
    hash_password,
    utc_now_iso,
    validate_password_strength,
)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    ensure_initialized()
    yield


app = FastAPI(
    title="SecureAudit ISMS ISO/IEC 27001:2022 API",
    version="2.0.0",
    description="REST API for SecureAudit Web Tracker & ISMS ISO/IEC 27001:2022 Audit Platform",
    lifespan=lifespan,
    # Docs live under /api/* so they remain reachable on Vercel, where all
    # non-/api/ paths are rewritten to the React SPA (index.html).
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    username: str
    password: str


class AuditPayload(BaseModel):
    audit_id: str | None = None
    title: str
    organization: str = "TechCorp International"
    department: str = "Enterprise IT"
    audit_type: str = "ISO 27001"
    status: str = "Planned"
    audit_date: str
    start_date: str = ""
    end_date: str = ""
    lead_auditor: str = ""
    audit_team: str = ""
    scope: str = ""
    objectives: str = ""
    compliance: float | None = None
    seed_default_controls: bool = True


class TestWorkpaperPayload(BaseModel):
    test_id: str | None = None
    audit_id: str
    control_id: str
    control_title: str = ""
    domain: str = "Organizational (5)"
    procedure: str = ""
    sample_size: int = 10
    status: str = "Compliant"
    auditor_notes: str = ""
    evidence_ref: str = ""
    tested_at: str = ""


class FindingPayload(BaseModel):
    finding_id: str | None = None
    audit_id: str
    control_id: str = ""
    title: str
    severity: str = "High"
    status: str = "Open"
    affected_asset: str = ""
    criteria: str = ""
    condition: str = ""
    cause: str = ""
    impact: str = ""
    recommendation: str = ""
    owner: str = ""
    found_date: str = ""
    due_date: str = ""


class ActionPayload(BaseModel):
    action_id: str | None = None
    finding_id: str
    title: str
    action_type: str = "Corrective"
    owner: str = ""
    due_date: str = ""
    status: str = "Open"
    corrective_action: str = ""
    preventive_action: str = ""
    verification_notes: str = ""
    evidence_notes: str = ""


class ControlUpdatePayload(BaseModel):
    applicability: str
    implementation_status: str
    justification: str = ""
    owner: str = ""


class RiskPayload(BaseModel):
    risk_id: str | None = None
    title: str
    asset: str = ""
    threat: str = ""
    likelihood: int = Field(default=3, ge=1, le=5)
    impact: int = Field(default=3, ge=1, le=5)
    treatment: str = "Mitigate"
    linked_controls: str = ""
    residual_score: int = Field(default=6, ge=1, le=25)
    owner: str = ""
    status: str = "Open"


class ApprovalPayload(BaseModel):
    approval_status: str
    report_version: str = "1.0"
    approval_notes: str = ""


class CreateUserPayload(BaseModel):
    username: str
    full_name: str
    email: str
    role: str
    password: str


def resolve_actor(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Resolve Authorization Bearer token to user or raise 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required. Sign in first.")
    token = authorization.removeprefix("Bearer ").strip()
    session_user = get_session_user(token)
    if not session_user:
        raise HTTPException(status_code=401, detail="Session expired or invalid. Sign in again.")
    return session_user


def enforce_perm(user: dict[str, Any], permission: str) -> None:
    if not has_permission(user["role"], permission):
        raise HTTPException(
            status_code=403,
            detail=f"Role '{user['role']}' does not have '{permission}' permission.",
        )


@app.get("/")
def api_root() -> dict[str, Any]:
    return {
        "service": "SecureAudit ISMS ISO/IEC 27001:2022 API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "workspace": "/api/workspace",
    }


@app.get("/api/health")
def health_check() -> dict[str, Any]:
    ensure_initialized()
    chain = verify_audit_log_chain()
    return {
        "status": "ok",
        "service": "SecureAudit ISMS API",
        "audit_log_chain_valid": chain["valid"],
        "audit_log_entries": chain["checked_entries"],
    }


@app.get("/api/auth/demo-accounts")
def list_demo_accounts() -> dict[str, Any]:
    return {
        "notice": "Illustrative local demonstration accounts only.",
        "accounts": [
            {"username": u, "full_name": fn, "email": em, "role": role, "password": pw}
            for _, u, fn, em, role, pw in DEMO_ACCOUNTS
        ],
    }


@app.post("/api/auth/login")
def api_login(payload: LoginRequest) -> dict[str, Any]:
    res = authenticate_user(payload.username, payload.password)
    if not res.get("ok"):
        code = 423 if res.get("locked") else 401
        raise HTTPException(status_code=code, detail=res.get("error", "Authentication failed."))
    return res


@app.get("/api/auth/me")
def api_me(user: dict[str, Any] = Depends(resolve_actor)) -> dict[str, Any]:
    return {"user": user}


@app.get("/api/workspace")
def get_workspace_snapshot(include_demo: bool = True) -> dict[str, Any]:
    """Return synchronized workspace tables for Dashboard, Audits, Findings, Controls, Risks, Evidence & Logs."""
    ensure_initialized()
    where_clause = "" if include_demo else "WHERE record_type = 'USER'"
    with get_connection() as conn:
        audits = [
            dict(r)
            for r in conn.execute(
                f"SELECT * FROM audits {where_clause} ORDER BY audit_date DESC"
            ).fetchall()
        ]
        tests = [
            dict(r)
            for r in conn.execute(
                f"SELECT * FROM tests {where_clause} ORDER BY control_id ASC"
            ).fetchall()
        ]
        findings = [
            dict(r)
            for r in conn.execute(
                f"SELECT * FROM findings {where_clause} ORDER BY CASE severity WHEN 'Critical' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 ELSE 4 END, due_date ASC"
            ).fetchall()
        ]
        actions = [
            dict(r)
            for r in conn.execute(
                f"SELECT * FROM actions {where_clause} ORDER BY due_date ASC"
            ).fetchall()
        ]
        controls = [
            dict(r)
            for r in conn.execute("SELECT * FROM controls ORDER BY control_id ASC").fetchall()
        ]
        risks = [
            dict(r)
            for r in conn.execute(
                f"SELECT * FROM risks {where_clause} ORDER BY inherent_score DESC"
            ).fetchall()
        ]
        requirements = [
            dict(r)
            for r in conn.execute("SELECT * FROM requirements ORDER BY req_id ASC").fetchall()
        ]
        evidence = [
            dict(r)
            for r in conn.execute(
                f"SELECT * FROM evidence {where_clause} ORDER BY uploaded_at DESC"
            ).fetchall()
        ]
        logs = [
            dict(r)
            for r in conn.execute(
                "SELECT * FROM audit_logs ORDER BY log_id DESC LIMIT 250"
            ).fetchall()
        ]
        users = [
            dict(r)
            for r in conn.execute(
                "SELECT user_id, username, full_name, email, role, failed_attempts, locked_until, is_active, created_at, last_login, record_type FROM users ORDER BY user_id ASC"
            ).fetchall()
        ]

    return {
        "audits": audits,
        "tests": tests,
        "findings": findings,
        "actions": actions,
        "controls": controls,
        "risks": risks,
        "requirements": requirements,
        "evidence": evidence,
        "audit_logs": logs,
        "users": users,
        "clauses": ISO_27001_CLAUSES,
        "log_chain": verify_audit_log_chain(),
    }


@app.post("/api/audits")
def upsert_audit(
    payload: AuditPayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_audits")
    with get_connection() as conn:
        aid = (payload.audit_id or "").strip()
        is_new = False
        if not aid:
            cnt = conn.execute("SELECT COUNT(*) AS c FROM audits").fetchone()["c"]
            aid = f"AUD-2026-{cnt + 10:03d}"
            while conn.execute("SELECT 1 FROM audits WHERE audit_id = ?", (aid,)).fetchone():
                cnt += 1
                aid = f"AUD-2026-{cnt + 10:03d}"
            is_new = True
        else:
            is_new = conn.execute("SELECT 1 FROM audits WHERE audit_id = ?", (aid,)).fetchone() is None

        conn.execute(
            """
            INSERT INTO audits (
                audit_id, title, organization, department, audit_type, status,
                audit_date, start_date, end_date, lead_auditor, audit_team,
                created_by, scope, objectives, compliance, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
            ON CONFLICT(audit_id) DO UPDATE SET
                title=excluded.title,
                organization=excluded.organization,
                department=excluded.department,
                audit_type=excluded.audit_type,
                status=excluded.status,
                audit_date=excluded.audit_date,
                start_date=excluded.start_date,
                end_date=excluded.end_date,
                lead_auditor=excluded.lead_auditor,
                audit_team=excluded.audit_team,
                scope=excluded.scope,
                objectives=excluded.objectives,
                compliance=COALESCE(excluded.compliance, audits.compliance)
            """,
            (
                aid,
                payload.title.strip(),
                payload.organization.strip(),
                payload.department.strip(),
                payload.audit_type.strip(),
                payload.status.strip(),
                payload.audit_date.strip(),
                (payload.start_date or payload.audit_date).strip(),
                (payload.end_date or payload.audit_date).strip(),
                (payload.lead_auditor or user["full_name"]).strip(),
                payload.audit_team.strip(),
                user["full_name"],
                payload.scope.strip(),
                payload.objectives.strip(),
                payload.compliance,
            ),
        )

        if is_new and payload.seed_default_controls:
            base_cnt = conn.execute("SELECT COUNT(*) AS c FROM tests").fetchone()["c"]
            for idx, ctrl in enumerate(ANNEX_A_CONTROLS_CATALOGUE[:12], start=1):
                tid = f"TST-{base_cnt + idx + 100:03d}"
                conn.execute(
                    """
                    INSERT OR IGNORE INTO tests (
                        test_id, audit_id, control_id, control_title, domain, procedure,
                        sample_size, status, auditor_notes, evidence_ref, tested_by, tested_at, record_type
                    ) VALUES (?, ?, ?, ?, ?, ?, 10, 'Not Tested', '', '', ?, ?, 'USER')
                    """,
                    (
                        tid,
                        aid,
                        ctrl["control_id"],
                        ctrl["title"],
                        ctrl["domain"],
                        f"Verify design and operating evidence for {ctrl['control_id']} ({ctrl['title']}).",
                        user["full_name"],
                        payload.audit_date,
                    ),
                )

        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="AUDIT_CREATED" if is_new else "AUDIT_UPDATED",
            entity_type="Audit",
            entity_id=aid,
            details=f"{payload.title.strip()} ({payload.status})",
        )
        conn.commit()
        row = conn.execute("SELECT * FROM audits WHERE audit_id = ?", (aid,)).fetchone()
        return {"audit": dict(row)}


@app.delete("/api/audits/{audit_id}")
def delete_audit(
    audit_id: str,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_audits")
    with get_connection() as conn:
        conn.execute("DELETE FROM tests WHERE audit_id = ?", (audit_id,))
        conn.execute("DELETE FROM audits WHERE audit_id = ?", (audit_id,))
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="AUDIT_DELETED",
            entity_type="Audit",
            entity_id=audit_id,
            details="Removed audit and associated control tests.",
        )
        conn.commit()
    return {"deleted": audit_id}


@app.post("/api/tests")
def upsert_test_workpaper(
    payload: TestWorkpaperPayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_audits")
    with get_connection() as conn:
        tid = (payload.test_id or "").strip()
        if not tid:
            cnt = conn.execute("SELECT COUNT(*) AS c FROM tests").fetchone()["c"]
            tid = f"TST-{cnt + 100:03d}"
            while conn.execute("SELECT 1 FROM tests WHERE test_id = ?", (tid,)).fetchone():
                cnt += 1
                tid = f"TST-{cnt + 100:03d}"

        ctrl_title = payload.control_title.strip()
        domain = payload.domain.strip()
        if not ctrl_title:
            c_row = conn.execute(
                "SELECT title, domain FROM controls WHERE control_id = ?",
                (payload.control_id,),
            ).fetchone()
            if c_row:
                ctrl_title = c_row["title"]
                domain = c_row["domain"]
            else:
                ctrl_title = payload.control_id

        conn.execute(
            """
            INSERT INTO tests (
                test_id, audit_id, control_id, control_title, domain, procedure,
                sample_size, status, auditor_notes, evidence_ref, tested_by, tested_at, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
            ON CONFLICT(test_id) DO UPDATE SET
                control_id=excluded.control_id,
                control_title=excluded.control_title,
                domain=excluded.domain,
                procedure=excluded.procedure,
                sample_size=excluded.sample_size,
                status=excluded.status,
                auditor_notes=excluded.auditor_notes,
                evidence_ref=excluded.evidence_ref,
                tested_by=excluded.tested_by,
                tested_at=excluded.tested_at
            """,
            (
                tid,
                payload.audit_id,
                payload.control_id,
                ctrl_title,
                domain,
                payload.procedure,
                payload.sample_size,
                payload.status,
                payload.auditor_notes,
                payload.evidence_ref,
                user["full_name"],
                payload.tested_at or utc_now_iso()[:10],
            ),
        )
        new_comp = recalculate_audit_compliance(conn, payload.audit_id)
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="CONTROL_TEST_UPDATED",
            entity_type="Test",
            entity_id=tid,
            details=f"{payload.audit_id} / {payload.control_id} -> {payload.status} (Compliance: {new_comp}%)",
        )
        conn.commit()
        row = conn.execute("SELECT * FROM tests WHERE test_id = ?", (tid,)).fetchone()
        return {"test": dict(row), "audit_compliance": new_comp}


@app.post("/api/findings")
def upsert_finding(
    payload: FindingPayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_findings")
    with get_connection() as conn:
        fid = (payload.finding_id or "").strip()
        if not fid:
            cnt = conn.execute("SELECT COUNT(*) AS c FROM findings").fetchone()["c"]
            fid = f"FND-2026-{cnt + 10:03d}"
            while conn.execute("SELECT 1 FROM findings WHERE finding_id = ?", (fid,)).fetchone():
                cnt += 1
                fid = f"FND-2026-{cnt + 10:03d}"

        conn.execute(
            """
            INSERT INTO findings (
                finding_id, audit_id, control_id, title, severity, status,
                affected_asset, criteria, condition, cause, impact,
                recommendation, owner, found_date, due_date, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
            ON CONFLICT(finding_id) DO UPDATE SET
                audit_id=excluded.audit_id,
                control_id=excluded.control_id,
                title=excluded.title,
                severity=excluded.severity,
                status=excluded.status,
                affected_asset=excluded.affected_asset,
                criteria=excluded.criteria,
                condition=excluded.condition,
                cause=excluded.cause,
                impact=excluded.impact,
                recommendation=excluded.recommendation,
                owner=excluded.owner,
                due_date=excluded.due_date
            """,
            (
                fid,
                payload.audit_id,
                payload.control_id,
                payload.title.strip(),
                payload.severity,
                payload.status,
                payload.affected_asset.strip(),
                payload.criteria.strip(),
                payload.condition.strip(),
                payload.cause.strip(),
                payload.impact.strip(),
                payload.recommendation.strip(),
                (payload.owner or user["full_name"]).strip(),
                payload.found_date or utc_now_iso()[:10],
                payload.due_date,
            ),
        )
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="FINDING_SAVED",
            entity_type="Finding",
            entity_id=fid,
            details=f"[{payload.severity}] {payload.title.strip()} ({payload.status})",
        )
        conn.commit()
        row = conn.execute("SELECT * FROM findings WHERE finding_id = ?", (fid,)).fetchone()
        return {"finding": dict(row)}


@app.post("/api/actions")
def upsert_action(
    payload: ActionPayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_actions")
    with get_connection() as conn:
        act_id = (payload.action_id or "").strip()
        if not act_id:
            cnt = conn.execute("SELECT COUNT(*) AS c FROM actions").fetchone()["c"]
            act_id = f"CAPA-2026-{cnt + 10:03d}"
            while conn.execute("SELECT 1 FROM actions WHERE action_id = ?", (act_id,)).fetchone():
                cnt += 1
                act_id = f"CAPA-2026-{cnt + 10:03d}"

        conn.execute(
            """
            INSERT INTO actions (
                action_id, finding_id, title, action_type, owner, due_date,
                status, corrective_action, preventive_action,
                verification_notes, evidence_notes, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
            ON CONFLICT(action_id) DO UPDATE SET
                finding_id=excluded.finding_id,
                title=excluded.title,
                action_type=excluded.action_type,
                owner=excluded.owner,
                due_date=excluded.due_date,
                status=excluded.status,
                corrective_action=excluded.corrective_action,
                preventive_action=excluded.preventive_action,
                verification_notes=excluded.verification_notes,
                evidence_notes=excluded.evidence_notes
            """,
            (
                act_id,
                payload.finding_id,
                payload.title.strip(),
                payload.action_type,
                (payload.owner or user["full_name"]).strip(),
                payload.due_date,
                payload.status,
                payload.corrective_action.strip(),
                payload.preventive_action.strip(),
                payload.verification_notes.strip(),
                payload.evidence_notes.strip(),
            ),
        )
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="CAPA_SAVED",
            entity_type="CAPA",
            entity_id=act_id,
            details=f"{payload.title.strip()} -> {payload.status}",
        )
        conn.commit()
        row = conn.execute("SELECT * FROM actions WHERE action_id = ?", (act_id,)).fetchone()
        return {"action": dict(row)}


@app.put("/api/controls/{control_id}")
def update_soa_control(
    control_id: str,
    payload: ControlUpdatePayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_controls")
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE controls
            SET applicability = ?, implementation_status = ?,
                justification = ?, owner = ?, record_type = 'USER'
            WHERE control_id = ?
            """,
            (
                payload.applicability,
                payload.implementation_status,
                payload.justification.strip(),
                (payload.owner or user["full_name"]).strip(),
                control_id,
            ),
        )
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="SOA_UPDATED",
            entity_type="Control",
            entity_id=control_id,
            details=f"{payload.applicability} | {payload.implementation_status}",
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM controls WHERE control_id = ?", (control_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Control not found.")
        return {"control": dict(row)}


@app.post("/api/risks")
def upsert_risk(
    payload: RiskPayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_risks")
    inherent = payload.likelihood * payload.impact
    with get_connection() as conn:
        rid = (payload.risk_id or "").strip()
        if not rid:
            cnt = conn.execute("SELECT COUNT(*) AS c FROM risks").fetchone()["c"]
            rid = f"RSK-{cnt + 10:03d}"
            while conn.execute("SELECT 1 FROM risks WHERE risk_id = ?", (rid,)).fetchone():
                cnt += 1
                rid = f"RSK-{cnt + 10:03d}"

        conn.execute(
            """
            INSERT INTO risks (
                risk_id, title, asset, threat, likelihood, impact,
                inherent_score, treatment, linked_controls, residual_score,
                owner, status, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
            ON CONFLICT(risk_id) DO UPDATE SET
                title=excluded.title,
                asset=excluded.asset,
                threat=excluded.threat,
                likelihood=excluded.likelihood,
                impact=excluded.impact,
                inherent_score=excluded.inherent_score,
                treatment=excluded.treatment,
                linked_controls=excluded.linked_controls,
                residual_score=excluded.residual_score,
                owner=excluded.owner,
                status=excluded.status
            """,
            (
                rid,
                payload.title.strip(),
                payload.asset.strip(),
                payload.threat.strip(),
                payload.likelihood,
                payload.impact,
                inherent,
                payload.treatment,
                payload.linked_controls.strip(),
                payload.residual_score,
                (payload.owner or user["full_name"]).strip(),
                payload.status,
            ),
        )
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="RISK_SAVED",
            entity_type="Risk",
            entity_id=rid,
            details=f"{payload.title.strip()} (Inherent={inherent}, Residual={payload.residual_score})",
        )
        conn.commit()
        row = conn.execute("SELECT * FROM risks WHERE risk_id = ?", (rid,)).fetchone()
        return {"risk": dict(row)}


@app.post("/api/evidence/upload")
async def upload_evidence(
    title: str = Form(...),
    entity_type: str = Form("Audit"),
    entity_id: str = Form("AUD-2026-001"),
    audit_id: str = Form("AUD-2026-001"),
    control_id: str = Form(""),
    notes: str = Form(""),
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_evidence")
    raw = await file.read()
    try:
        saved = save_evidence_file(
            title=title,
            entity_type=entity_type,
            entity_id=entity_id,
            audit_id=audit_id,
            control_id=control_id,
            filename=file.filename or "evidence.bin",
            content_type=file.content_type or "application/octet-stream",
            data=raw,
            uploaded_by=user["full_name"],
            actor_role=user["role"],
            notes=notes,
        )
        return {"evidence": saved}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/evidence/{evidence_id}/verify")
def api_verify_evidence(
    evidence_id: str,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    try:
        return verify_evidence_integrity(
            evidence_id, actor=user["username"], role=user["role"]
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@app.get("/api/evidence/{evidence_id}/download")
def api_download_evidence(evidence_id: str) -> FileResponse:
    res = verify_evidence_integrity(evidence_id, actor="download_check", role="System")
    if not res["matches"]:
        raise HTTPException(
            status_code=409,
            detail=f"Evidence file failed SHA-256 verification ({res['status']}). Download blocked.",
        )
    return FileResponse(
        path=res["disk_path"],
        filename=res["file_name"],
        media_type=res["mime_type"],
        headers={"X-Evidence-SHA256": res["actual_sha256"]},
    )


@app.post("/api/audits/{audit_id}/approve")
def api_approve_report(
    audit_id: str,
    payload: ApprovalPayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    try:
        updated = approve_audit_report(
            audit_id=audit_id,
            approval_status=payload.approval_status,
            reviewer_name=user["full_name"],
            reviewer_role=user["role"],
            report_version=payload.report_version,
            approval_notes=payload.approval_notes,
        )
        return {"audit": updated}
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except (ValueError, KeyError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/reports/audit/{audit_id}/pdf")
def download_audit_pdf(audit_id: str) -> Response:
    try:
        pdf_bytes = generate_audit_pdf(audit_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="SecureAudit_Report_{audit_id}.pdf"'
        },
    )


@app.get("/api/reports/workbook.xlsx")
def download_workbook() -> Response:
    xlsx_bytes = generate_executive_workbook()
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="SecureAudit_ISMS_Workbook.xlsx"'
        },
    )


@app.get("/api/backup/json")
def download_backup_json() -> Response:
    data = export_backup_json()
    return Response(
        content=json.dumps(data, indent=2).encode("utf-8"),
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="isms_tracker_backup.json"'
        },
    )


@app.post("/api/backup/verify")
async def verify_backup_json(file: UploadFile = File(...)) -> dict[str, Any]:
    raw = await file.read()
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Uploaded file is not valid JSON.")
    return validate_backup_payload(parsed)


@app.post("/api/import/audits-csv")
async def api_import_audits_csv(
    file: UploadFile = File(...),
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_demo_data")
    raw = await file.read()
    try:
        return import_audits_csv(raw, actor=user["username"], role=user["role"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/demo/restore")
def api_restore_demo(user: dict[str, Any] = Depends(resolve_actor)) -> dict[str, Any]:
    enforce_perm(user, "manage_demo_data")
    count = restore_demo_records(actor=user["username"], role=user["role"])
    return {"restored": count}


@app.post("/api/demo/remove")
def api_remove_demo(user: dict[str, Any] = Depends(resolve_actor)) -> dict[str, Any]:
    enforce_perm(user, "manage_demo_data")
    count = remove_demo_records(actor=user["username"], role=user["role"])
    return {"removed": count}


@app.post("/api/users")
def api_create_user(
    payload: CreateUserPayload,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_users")
    ok, msg = validate_password_strength(payload.password)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    pwd_hash, salt_hex = hash_password(payload.password)
    with get_connection() as conn:
        cnt = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        uid = f"USR-{cnt + 10:03d}"
        try:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, username, full_name, email, role, password_hash,
                    salt_hex, failed_attempts, locked_until, is_active, created_at, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, '', 1, ?, 'USER')
                """,
                (
                    uid,
                    payload.username.strip().lower(),
                    payload.full_name.strip(),
                    payload.email.strip().lower(),
                    payload.role,
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
                details=f"Created account '{payload.username.strip().lower()}' ({payload.role})",
            )
            conn.commit()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Username already exists or invalid: {exc}")
    return {"created_user_id": uid}


@app.post("/api/users/{username}/unlock")
def api_unlock_user(
    username: str,
    user: dict[str, Any] = Depends(resolve_actor),
) -> dict[str, Any]:
    enforce_perm(user, "manage_users")
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = '' WHERE username = ?",
            (username,),
        )
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="USER_UNLOCKED",
            entity_type="User",
            entity_id=username,
            details="Cleared lockout window and failed attempt counter.",
        )
        conn.commit()
    return {"unlocked": username}


@app.get("/api/audit-logs/verify")
def api_verify_log_chain() -> dict[str, Any]:
    return verify_audit_log_chain()
