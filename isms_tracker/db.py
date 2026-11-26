"""SQLite schema, persistence, RBAC authentication, evidence integrity,
report sign-off, hash-chained audit logs, and safe demo seeding.
"""

from __future__ import annotations

import csv
import io
import json
import os
import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from isms_tracker.catalogue import ANNEX_A_CONTROLS_CATALOGUE, REGULATORY_FRAMEWORKS
from isms_tracker.security import (
    MAX_FAILED_ATTEMPTS,
    compute_lockout_timestamp,
    compute_log_entry_hash,
    compute_sha256_bytes,
    compute_sha256_file,
    generate_session_token,
    hash_password,
    is_account_locked,
    sanitize_filename,
    utc_now_iso,
    validate_evidence_upload,
    verify_password,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
UPLOADS_DIR = DATA_DIR / "uploads"
DEMO_DATA_PATH = DATA_DIR / "demo_data.json"
DB_PATH = Path(os.environ.get("ISMS_DB_PATH", str(DATA_DIR / "isms_tracker.db")))

ALLOWED_TABLES = {
    "users",
    "audits",
    "tests",
    "findings",
    "actions",
    "controls",
    "risks",
    "requirements",
    "evidence",
    "audit_logs",
}

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS meta_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    salt_hex TEXT NOT NULL,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until TEXT DEFAULT '',
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL,
    last_login TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'DEMO'
);

CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    username TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audits (
    audit_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    organization TEXT NOT NULL DEFAULT 'TechCorp International',
    department TEXT NOT NULL,
    audit_type TEXT NOT NULL DEFAULT 'ISO 27001',
    status TEXT NOT NULL DEFAULT 'Planned',
    audit_date TEXT NOT NULL,
    start_date TEXT DEFAULT '',
    end_date TEXT DEFAULT '',
    lead_auditor TEXT DEFAULT '',
    audit_team TEXT DEFAULT '',
    created_by TEXT DEFAULT 'System',
    scope TEXT DEFAULT '',
    objectives TEXT DEFAULT '',
    compliance REAL,
    approval_status TEXT NOT NULL DEFAULT 'Draft',
    approved_by TEXT DEFAULT '',
    approved_at TEXT DEFAULT '',
    report_version TEXT NOT NULL DEFAULT '1.0',
    approval_notes TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'USER'
);

CREATE TABLE IF NOT EXISTS tests (
    test_id TEXT PRIMARY KEY,
    audit_id TEXT NOT NULL,
    control_id TEXT NOT NULL,
    control_title TEXT NOT NULL,
    domain TEXT NOT NULL DEFAULT 'Organizational (5)',
    procedure TEXT DEFAULT '',
    sample_size INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'Not Tested',
    auditor_notes TEXT DEFAULT '',
    evidence_ref TEXT DEFAULT '',
    tested_by TEXT DEFAULT '',
    tested_at TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'USER'
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    audit_id TEXT NOT NULL,
    control_id TEXT DEFAULT '',
    title TEXT NOT NULL,
    severity TEXT NOT NULL DEFAULT 'Medium',
    status TEXT NOT NULL DEFAULT 'Open',
    affected_asset TEXT DEFAULT '',
    criteria TEXT DEFAULT '',
    condition TEXT DEFAULT '',
    cause TEXT DEFAULT '',
    impact TEXT DEFAULT '',
    recommendation TEXT DEFAULT '',
    owner TEXT DEFAULT '',
    found_date TEXT DEFAULT '',
    due_date TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'USER'
);

CREATE TABLE IF NOT EXISTS actions (
    action_id TEXT PRIMARY KEY,
    finding_id TEXT NOT NULL,
    title TEXT NOT NULL,
    action_type TEXT NOT NULL DEFAULT 'Corrective',
    owner TEXT DEFAULT '',
    due_date TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Open',
    corrective_action TEXT DEFAULT '',
    preventive_action TEXT DEFAULT '',
    verification_notes TEXT DEFAULT '',
    evidence_notes TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'USER'
);

CREATE TABLE IF NOT EXISTS controls (
    control_id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    applicability TEXT NOT NULL DEFAULT 'Applicable',
    implementation_status TEXT NOT NULL DEFAULT 'Implemented',
    justification TEXT DEFAULT '',
    owner TEXT DEFAULT '',
    nist_csf TEXT DEFAULT '',
    soc2 TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'DEMO'
);

CREATE TABLE IF NOT EXISTS risks (
    risk_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    asset TEXT DEFAULT '',
    threat TEXT DEFAULT '',
    likelihood INTEGER NOT NULL DEFAULT 3,
    impact INTEGER NOT NULL DEFAULT 3,
    inherent_score INTEGER NOT NULL DEFAULT 9,
    treatment TEXT NOT NULL DEFAULT 'Mitigate',
    linked_controls TEXT DEFAULT '',
    residual_score INTEGER NOT NULL DEFAULT 4,
    owner TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Open',
    record_type TEXT NOT NULL DEFAULT 'USER'
);

CREATE TABLE IF NOT EXISTS requirements (
    req_id TEXT PRIMARY KEY,
    framework TEXT NOT NULL,
    reference TEXT NOT NULL,
    requirement_summary TEXT NOT NULL,
    mapped_controls TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'In Review',
    notes TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'DEMO'
);

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    audit_id TEXT DEFAULT '',
    control_id TEXT DEFAULT '',
    file_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    sha256_hash TEXT NOT NULL,
    uploaded_by TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    verified_status TEXT NOT NULL DEFAULT 'Verified',
    notes TEXT DEFAULT '',
    record_type TEXT NOT NULL DEFAULT 'USER'
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    role TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    details TEXT DEFAULT '',
    prev_hash TEXT NOT NULL,
    entry_hash TEXT NOT NULL
);
"""


DEMO_ACCOUNTS = [
    ("USR-001", "admin", "Alex Johnson", "alex.johnson@secureaudit.local", "Admin", "Admin@27001!"),
    ("USR-002", "auditor", "Sarah Chen", "sarah.chen@secureaudit.local", "Auditor", "Auditor@27001!"),
    ("USR-003", "riskowner", "Marcus Williams", "marcus.williams@secureaudit.local", "Risk Owner", "RiskOwner@27001!"),
    ("USR-004", "viewer", "Rohan Mehta", "rohan.mehta@secureaudit.local", "Viewer", "Viewer@27001!"),
]


def _resolve_db_path() -> Path:
    return Path(os.environ.get("ISMS_DB_PATH", str(DB_PATH)))


def get_connection() -> sqlite3.Connection:
    """Open SQLite connection with row dictionary access."""
    path = _resolve_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def append_audit_log(
    conn: sqlite3.Connection,
    actor: str,
    role: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: str = "",
) -> str:
    """Append a tamper-evident hash-chained audit trail event."""
    last = conn.execute(
        "SELECT entry_hash FROM audit_logs ORDER BY log_id DESC LIMIT 1"
    ).fetchone()
    prev_hash = last["entry_hash"] if last else "GENESIS"
    ts = utc_now_iso()
    entry_hash = compute_log_entry_hash(
        prev_hash=prev_hash,
        timestamp=ts,
        actor=actor,
        role=role,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    conn.execute(
        """
        INSERT INTO audit_logs (
            timestamp, actor, role, action, entity_type, entity_id, details, prev_hash, entry_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (ts, actor, role, action, entity_type, entity_id, details, prev_hash, entry_hash),
    )
    return entry_hash


def verify_audit_log_chain() -> dict[str, Any]:
    """Verify every hash link across the append-only audit_logs table."""
    ensure_initialized()
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM audit_logs ORDER BY log_id ASC").fetchall()
    prev = "GENESIS"
    broken_at: int | None = None
    for row in rows:
        expected = compute_log_entry_hash(
            prev_hash=prev,
            timestamp=row["timestamp"],
            actor=row["actor"],
            role=row["role"],
            action=row["action"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            details=row["details"],
        )
        if row["prev_hash"] != prev or row["entry_hash"] != expected:
            broken_at = int(row["log_id"])
            break
        prev = row["entry_hash"]
    return {
        "valid": broken_at is None,
        "checked_entries": len(rows),
        "broken_log_id": broken_at,
        "head_hash": prev if rows else "GENESIS",
    }


def _seed_demo_evidence_files(conn: sqlite3.Connection) -> None:
    """Create deterministic illustrative evidence artefacts with genuine SHA-256 digests."""
    samples = [
        (
            "EVD-2026-001",
            "Information Security Policy v3.2 Sign-Off",
            "Audit",
            "AUD-2026-001",
            "AUD-2026-001",
            "A.5.1",
            "evidence_doc_c1.pdf",
            "application/pdf",
            b"%PDF-1.4\n% Illustrative ISMS Policy Sign-Off Evidence (DEMO)\nPolicy: Information Security Policy v3.2\nApproved By: Executive Security Committee\nControl: ISO/IEC 27001:2022 A.5.1\n%%EOF\n",
            "Sarah Chen",
            "Board-approved policy artefact verified during AUD-2026-001.",
        ),
        (
            "EVD-2026-002",
            "CMDB Production Asset Reconciliation Export",
            "Control",
            "A.5.9",
            "AUD-2026-001",
            "A.5.9",
            "evidence_doc_c4.pdf",
            "application/pdf",
            b"%PDF-1.4\n% Illustrative CMDB Asset Inventory Sample (DEMO)\nSampled Assets: 40/40 matched\nControl: ISO/IEC 27001:2022 A.5.9\n%%EOF\n",
            "Sarah Chen",
            "40 sampled cloud instances reconciled against CMDB owners.",
        ),
        (
            "EVD-2026-003",
            "Privileged Cloud Console MFA Audit Snapshot",
            "Finding",
            "FND-2026-003",
            "AUD-2026-001",
            "A.8.5",
            "mfa_status_report.json",
            "application/json",
            json.dumps(
                {
                    "_demo_notice": "Illustrative MFA audit snapshot",
                    "checked_accounts": 18,
                    "mfa_enforced": 16,
                    "non_compliant_accounts": ["breakglass-admin-01", "breakglass-admin-02"],
                },
                indent=2,
            ).encode("utf-8"),
            "Sarah Chen",
            "Evidence supporting Critical finding FND-2026-003.",
        ),
        (
            "EVD-2026-004",
            "Production Vulnerability Scan Extract",
            "Finding",
            "FND-2026-002",
            "AUD-2026-001",
            "A.8.8",
            "vuln_scan_sep2026.csv",
            "text/csv",
            b"host,package,cve,severity,days_open\nprod-app-01,openssh-server,CVE-2024-6387,Critical,22\nprod-app-02,linux-image,CVE-2024-1086,Critical,19\n",
            "Marcus Williams",
            "Authenticated vulnerability scan extract for Linux hosts.",
        ),
    ]
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    for (
        evd_id,
        title,
        ent_type,
        ent_id,
        aud_id,
        ctrl_id,
        fname,
        mime,
        raw_bytes,
        uploader,
        notes,
    ) in samples:
        existing = conn.execute(
            "SELECT 1 FROM evidence WHERE evidence_id = ?", (evd_id,)
        ).fetchone()
        disk_path = UPLOADS_DIR / f"{evd_id}_{fname}"
        if not disk_path.exists():
            disk_path.write_bytes(raw_bytes)
        if existing:
            continue
        digest = compute_sha256_bytes(raw_bytes)
        conn.execute(
            """
            INSERT OR IGNORE INTO evidence (
                evidence_id, title, entity_type, entity_id, audit_id, control_id,
                file_name, stored_path, mime_type, file_size_bytes, sha256_hash,
                uploaded_by, uploaded_at, verified_status, notes, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Verified', ?, 'DEMO')
            """,
            (
                evd_id,
                title,
                ent_type,
                ent_id,
                aud_id,
                ctrl_id,
                fname,
                str(disk_path.relative_to(ROOT_DIR)),
                mime,
                len(raw_bytes),
                digest,
                uploader,
                utc_now_iso(),
                notes,
            ),
        )


def seed_demo_records(conn: sqlite3.Connection, force_restore: bool = False) -> int:
    """Insert missing demo records safely (insert-only; never overwrites user IDs)."""
    already_seeded = conn.execute(
        "SELECT value FROM meta_state WHERE key = 'demo_seeded'"
    ).fetchone()
    if already_seeded and not force_restore:
        return 0

    inserted = 0
    now = utc_now_iso()

    # Seed demo users
    for uid, uname, fname, email, role, pwd in DEMO_ACCOUNTS:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE user_id = ? OR username = ?", (uid, uname)
        ).fetchone()
        if not exists:
            pwd_hash, salt_hex = hash_password(pwd)
            conn.execute(
                """
                INSERT INTO users (
                    user_id, username, full_name, email, role, password_hash, salt_hex,
                    failed_attempts, locked_until, is_active, created_at, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 0, '', 1, ?, 'DEMO')
                """,
                (uid, uname, fname, email, role, pwd_hash, salt_hex, now),
            )
            inserted += 1

    payload = json.loads(DEMO_DATA_PATH.read_text(encoding="utf-8"))
    overrides = payload.get("controls_overrides", {})

    # Seed Annex A controls
    for ctrl in ANNEX_A_CONTROLS_CATALOGUE:
        cid = ctrl["control_id"]
        exists = conn.execute(
            "SELECT 1 FROM controls WHERE control_id = ?", (cid,)
        ).fetchone()
        if not exists:
            ov = overrides.get(cid, {})
            conn.execute(
                """
                INSERT INTO controls (
                    control_id, domain, title, description, applicability,
                    implementation_status, justification, owner, nist_csf, soc2, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DEMO')
                """,
                (
                    cid,
                    ctrl["domain"],
                    ctrl["title"],
                    ctrl["description"],
                    ov.get("applicability", "Applicable"),
                    ov.get("implementation_status", "Implemented"),
                    ov.get("justification", "Included in baseline ISMS scope."),
                    ov.get("owner", "Alex Johnson"),
                    ctrl.get("nist_csf", ""),
                    ctrl.get("soc2", ""),
                ),
            )
            inserted += 1

    # Seed regulatory requirements
    for req in REGULATORY_FRAMEWORKS:
        exists = conn.execute(
            "SELECT 1 FROM requirements WHERE req_id = ?", (req["req_id"],)
        ).fetchone()
        if not exists:
            conn.execute(
                """
                INSERT INTO requirements (
                    req_id, framework, reference, requirement_summary,
                    mapped_controls, status, notes, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'DEMO')
                """,
                (
                    req["req_id"],
                    req["framework"],
                    req["reference"],
                    req["requirement_summary"],
                    req["mapped_controls"],
                    req["status"],
                    req["notes"],
                ),
            )
            inserted += 1

    # Seed audits
    for row in payload.get("audits", []):
        exists = conn.execute(
            "SELECT 1 FROM audits WHERE audit_id = ?", (row["audit_id"],)
        ).fetchone()
        if not exists:
            conn.execute(
                """
                INSERT INTO audits (
                    audit_id, title, organization, department, audit_type, status,
                    audit_date, start_date, end_date, lead_auditor, audit_team,
                    created_by, scope, objectives, compliance, approval_status,
                    approved_by, approved_at, report_version, approval_notes, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DEMO')
                """,
                (
                    row["audit_id"],
                    row["title"],
                    row.get("organization", "TechCorp International"),
                    row["department"],
                    row.get("audit_type", "ISO 27001"),
                    row["status"],
                    row["audit_date"],
                    row.get("start_date", row["audit_date"]),
                    row.get("end_date", row["audit_date"]),
                    row.get("lead_auditor", ""),
                    row.get("audit_team", ""),
                    row.get("created_by", "Alex Johnson"),
                    row.get("scope", ""),
                    row.get("objectives", ""),
                    row.get("compliance"),
                    row.get("approval_status", "Draft"),
                    row.get("approved_by", ""),
                    row.get("approved_at", ""),
                    row.get("report_version", "1.0"),
                    row.get("approval_notes", ""),
                ),
            )
            inserted += 1

    # Seed test workpapers
    for row in payload.get("tests", []):
        exists = conn.execute(
            "SELECT 1 FROM tests WHERE test_id = ?", (row["test_id"],)
        ).fetchone()
        if not exists:
            conn.execute(
                """
                INSERT INTO tests (
                    test_id, audit_id, control_id, control_title, domain, procedure,
                    sample_size, status, auditor_notes, evidence_ref, tested_by, tested_at, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DEMO')
                """,
                (
                    row["test_id"],
                    row["audit_id"],
                    row["control_id"],
                    row["control_title"],
                    row.get("domain", "Organizational (5)"),
                    row.get("procedure", ""),
                    row.get("sample_size", 1),
                    row["status"],
                    row.get("auditor_notes", ""),
                    row.get("evidence_ref", ""),
                    row.get("tested_by", ""),
                    row.get("tested_at", ""),
                ),
            )
            inserted += 1

    # Seed findings
    for row in payload.get("findings", []):
        exists = conn.execute(
            "SELECT 1 FROM findings WHERE finding_id = ?", (row["finding_id"],)
        ).fetchone()
        if not exists:
            conn.execute(
                """
                INSERT INTO findings (
                    finding_id, audit_id, control_id, title, severity, status,
                    affected_asset, criteria, condition, cause, impact,
                    recommendation, owner, found_date, due_date, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DEMO')
                """,
                (
                    row["finding_id"],
                    row["audit_id"],
                    row.get("control_id", ""),
                    row["title"],
                    row["severity"],
                    row["status"],
                    row.get("affected_asset", ""),
                    row.get("criteria", ""),
                    row.get("condition", ""),
                    row.get("cause", ""),
                    row.get("impact", ""),
                    row.get("recommendation", ""),
                    row.get("owner", ""),
                    row.get("found_date", ""),
                    row.get("due_date", ""),
                ),
            )
            inserted += 1

    # Seed CAPA actions
    for row in payload.get("actions", []):
        exists = conn.execute(
            "SELECT 1 FROM actions WHERE action_id = ?", (row["action_id"],)
        ).fetchone()
        if not exists:
            conn.execute(
                """
                INSERT INTO actions (
                    action_id, finding_id, title, action_type, owner, due_date,
                    status, corrective_action, preventive_action,
                    verification_notes, evidence_notes, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DEMO')
                """,
                (
                    row["action_id"],
                    row["finding_id"],
                    row["title"],
                    row.get("action_type", "Corrective"),
                    row.get("owner", ""),
                    row.get("due_date", ""),
                    row["status"],
                    row.get("corrective_action", ""),
                    row.get("preventive_action", ""),
                    row.get("verification_notes", ""),
                    row.get("evidence_notes", ""),
                ),
            )
            inserted += 1

    # Seed risks
    for row in payload.get("risks", []):
        exists = conn.execute(
            "SELECT 1 FROM risks WHERE risk_id = ?", (row["risk_id"],)
        ).fetchone()
        if not exists:
            conn.execute(
                """
                INSERT INTO risks (
                    risk_id, title, asset, threat, likelihood, impact,
                    inherent_score, treatment, linked_controls, residual_score,
                    owner, status, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'DEMO')
                """,
                (
                    row["risk_id"],
                    row["title"],
                    row.get("asset", ""),
                    row.get("threat", ""),
                    int(row.get("likelihood", 3)),
                    int(row.get("impact", 3)),
                    int(row.get("inherent_score", 9)),
                    row.get("treatment", "Mitigate"),
                    row.get("linked_controls", ""),
                    int(row.get("residual_score", 4)),
                    row.get("owner", ""),
                    row.get("status", "Open"),
                ),
            )
            inserted += 1

    _seed_demo_evidence_files(conn)

    conn.execute(
        "INSERT OR REPLACE INTO meta_state (key, value) VALUES ('demo_seeded', ?)",
        (now,),
    )
    if inserted > 0:
        append_audit_log(
            conn,
            actor="system",
            role="System",
            action="DEMO_SEED",
            entity_type="Database",
            entity_id="isms_tracker.db",
            details=f"Inserted {inserted} illustrative demo records safely.",
        )
    conn.commit()
    return inserted


def ensure_initialized() -> None:
    """Ensure SQLite schema exists and one-time demo seed has run."""
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
        seed_demo_records(conn, force_restore=False)


def read_table(table_name: str) -> pd.DataFrame:
    """Read an allowed SQLite table into a pandas DataFrame."""
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Unsupported table: {table_name}")
    ensure_initialized()
    with get_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def authenticate_user(username_or_email: str, password: str) -> dict[str, Any]:
    """Authenticate a local user with salted scrypt verification and lockout enforcement."""
    ensure_initialized()
    ident = (username_or_email or "").strip().lower()
    if not ident or not password:
        return {"ok": False, "error": "Enter both username and password."}

    with get_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?",
            (ident, ident),
        ).fetchone()
        if not user:
            append_audit_log(
                conn,
                actor=ident,
                role="Unauthenticated",
                action="LOGIN_FAILED",
                entity_type="User",
                entity_id=ident,
                details="Unknown username or email.",
            )
            conn.commit()
            return {"ok": False, "error": "Unrecognized username or password."}

        if not user["is_active"]:
            return {"ok": False, "error": "Account is deactivated. Contact an administrator."}

        locked, remaining_secs = is_account_locked(user["locked_until"])
        if locked:
            mins = max(1, (remaining_secs + 59) // 60)
            append_audit_log(
                conn,
                actor=user["username"],
                role=user["role"],
                action="LOGIN_BLOCKED_LOCKED",
                entity_type="User",
                entity_id=user["user_id"],
                details=f"Attempt during active lockout ({remaining_secs}s remaining).",
            )
            conn.commit()
            return {
                "ok": False,
                "locked": True,
                "error": f"Account locked after {MAX_FAILED_ATTEMPTS} failed attempts. Try again in {mins} minute(s).",
            }

        if not verify_password(password, user["password_hash"], user["salt_hex"]):
            attempts = int(user["failed_attempts"]) + 1
            locked_until = ""
            if attempts >= MAX_FAILED_ATTEMPTS:
                locked_until = compute_lockout_timestamp()
            conn.execute(
                "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE user_id = ?",
                (attempts, locked_until, user["user_id"]),
            )
            append_audit_log(
                conn,
                actor=user["username"],
                role=user["role"],
                action="ACCOUNT_LOCKED" if locked_until else "LOGIN_FAILED",
                entity_type="User",
                entity_id=user["user_id"],
                details=f"Failed password verification ({attempts}/{MAX_FAILED_ATTEMPTS}).",
            )
            conn.commit()
            if locked_until:
                return {
                    "ok": False,
                    "locked": True,
                    "error": f"Account locked for 15 minutes after {MAX_FAILED_ATTEMPTS} failed login attempts.",
                }
            remaining_tries = MAX_FAILED_ATTEMPTS - attempts
            return {
                "ok": False,
                "error": f"Unrecognized username or password. {remaining_tries} attempt(s) remaining before lockout.",
            }

        # Successful login: reset failed_attempts & issue session token
        now = utc_now_iso()
        token = generate_session_token()
        expires = compute_lockout_timestamp(minutes=720)
        conn.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = '', last_login = ? WHERE user_id = ?",
            (now, user["user_id"]),
        )
        conn.execute(
            """
            INSERT INTO sessions (token, user_id, username, full_name, email, role, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                token,
                user["user_id"],
                user["username"],
                user["full_name"],
                user["email"],
                user["role"],
                now,
                expires,
            ),
        )
        append_audit_log(
            conn,
            actor=user["username"],
            role=user["role"],
            action="LOGIN_SUCCESS",
            entity_type="User",
            entity_id=user["user_id"],
            details="Authenticated via salted scrypt verification.",
        )
        conn.commit()
        return {
            "ok": True,
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"],
                "last_login": now,
            },
        }


def get_session_user(token: str | None) -> dict[str, Any] | None:
    """Resolve bearer token to an active session user."""
    if not token:
        return None
    ensure_initialized()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM sessions WHERE token = ?", (token,)
        ).fetchone()
        if not row:
            return None
        return dict(row)


def save_evidence_file(
    *,
    title: str,
    entity_type: str,
    entity_id: str,
    audit_id: str,
    control_id: str,
    filename: str,
    content_type: str,
    data: bytes,
    uploaded_by: str,
    actor_role: str,
    notes: str = "",
) -> dict[str, Any]:
    """Validate, hash with SHA-256, persist file to disk, and insert evidence metadata."""
    ensure_initialized()
    safe_name = sanitize_filename(filename)
    ok, message = validate_evidence_upload(safe_name, content_type, len(data))
    if not ok:
        raise ValueError(message)

    digest = compute_sha256_bytes(data)
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) AS c FROM evidence").fetchone()["c"]
        evd_id = f"EVD-2026-{count + 101:03d}"
        while conn.execute("SELECT 1 FROM evidence WHERE evidence_id = ?", (evd_id,)).fetchone():
            count += 1
            evd_id = f"EVD-2026-{count + 101:03d}"

        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        disk_path = UPLOADS_DIR / f"{evd_id}_{safe_name}"
        disk_path.write_bytes(data)
        rel_path = str(disk_path.relative_to(ROOT_DIR))
        now = utc_now_iso()

        conn.execute(
            """
            INSERT INTO evidence (
                evidence_id, title, entity_type, entity_id, audit_id, control_id,
                file_name, stored_path, mime_type, file_size_bytes, sha256_hash,
                uploaded_by, uploaded_at, verified_status, notes, record_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Verified', ?, 'USER')
            """,
            (
                evd_id,
                title.strip() or safe_name,
                entity_type,
                entity_id,
                audit_id,
                control_id,
                safe_name,
                rel_path,
                content_type or "application/octet-stream",
                len(data),
                digest,
                uploaded_by,
                now,
                notes,
            ),
        )
        append_audit_log(
            conn,
            actor=uploaded_by,
            role=actor_role,
            action="EVIDENCE_UPLOADED",
            entity_type="Evidence",
            entity_id=evd_id,
            details=f"File '{safe_name}' ({len(data)} bytes) SHA-256={digest[:16]}...",
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM evidence WHERE evidence_id = ?", (evd_id,)
        ).fetchone()
        return dict(row)


def verify_evidence_integrity(evidence_id: str, actor: str = "system", role: str = "Auditor") -> dict[str, Any]:
    """Re-calculate SHA-256 of stored evidence file and compare with recorded digest."""
    ensure_initialized()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM evidence WHERE evidence_id = ?", (evidence_id,)
        ).fetchone()
        if not row:
            raise KeyError(f"Evidence {evidence_id} not found.")
        disk_path = ROOT_DIR / row["stored_path"]
        if not disk_path.exists():
            status = "Missing File"
            actual_hash = ""
            matches = False
        else:
            actual_hash = compute_sha256_file(str(disk_path))
            matches = actual_hash == row["sha256_hash"]
            status = "Verified" if matches else "Hash Mismatch"

        conn.execute(
            "UPDATE evidence SET verified_status = ? WHERE evidence_id = ?",
            (status, evidence_id),
        )
        append_audit_log(
            conn,
            actor=actor,
            role=role,
            action="EVIDENCE_HASH_VERIFIED",
            entity_type="Evidence",
            entity_id=evidence_id,
            details=f"Integrity check result: {status}",
        )
        conn.commit()
        return {
            "evidence_id": evidence_id,
            "expected_sha256": row["sha256_hash"],
            "actual_sha256": actual_hash,
            "matches": matches,
            "status": status,
            "file_size_bytes": row["file_size_bytes"],
            "disk_path": str(disk_path),
            "file_name": row["file_name"],
            "mime_type": row["mime_type"],
        }


def approve_audit_report(
    *,
    audit_id: str,
    approval_status: str,
    reviewer_name: str,
    reviewer_role: str,
    report_version: str,
    approval_notes: str = "",
) -> dict[str, Any]:
    """Record formal report review/sign-off metadata (Priority 4 recommendation)."""
    ensure_initialized()
    if approval_status not in {"Draft", "In Review", "Approved", "Changes Requested"}:
        raise ValueError("Invalid approval status.")
    if approval_status == "Approved" and reviewer_role != "Admin":
        raise PermissionError("Only an Admin role can grant final report sign-off.")

    now = utc_now_iso() if approval_status == "Approved" else ""
    approver = reviewer_name if approval_status == "Approved" else ""
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT * FROM audits WHERE audit_id = ?", (audit_id,)
        ).fetchone()
        if not existing:
            raise KeyError(f"Audit {audit_id} not found.")
        conn.execute(
            """
            UPDATE audits
            SET approval_status = ?, approved_by = ?, approved_at = ?,
                report_version = ?, approval_notes = ?
            WHERE audit_id = ?
            """,
            (approval_status, approver, now, report_version, approval_notes, audit_id),
        )
        append_audit_log(
            conn,
            actor=reviewer_name,
            role=reviewer_role,
            action=f"REPORT_{approval_status.upper().replace(' ', '_')}",
            entity_type="Audit",
            entity_id=audit_id,
            details=f"Version {report_version} — {approval_notes or 'Status updated.'}",
        )
        conn.commit()
        updated = conn.execute(
            "SELECT * FROM audits WHERE audit_id = ?", (audit_id,)
        ).fetchone()
        return dict(updated)


def recalculate_audit_compliance(conn: sqlite3.Connection, audit_id: str) -> float | None:
    """Recalculate an audit's compliance % from its linked control test results."""
    rows = conn.execute(
        "SELECT status FROM tests WHERE audit_id = ?", (audit_id,)
    ).fetchall()
    scored: list[float] = []
    for r in rows:
        st = (r["status"] or "").strip().lower()
        if st == "compliant":
            scored.append(100.0)
        elif st in {"partially compliant", "partial"}:
            scored.append(50.0)
        elif st in {"non-compliant", "non compliant"}:
            scored.append(0.0)
    if not scored:
        return None
    avg = round(sum(scored) / len(scored), 1)
    conn.execute(
        "UPDATE audits SET compliance = ? WHERE audit_id = ?", (avg, audit_id)
    )
    return avg


def import_audits_csv(csv_bytes: bytes, actor: str = "local_user", role: str = "Admin") -> dict[str, Any]:
    """Append-only CSV import for audits; skips existing audit_id values safely."""
    ensure_initialized()
    text = csv_bytes.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))
    required = {"audit_id", "title", "department", "status", "audit_date"}
    if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
        missing = sorted(required - set(reader.fieldnames or []))
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")

    imported = 0
    skipped = 0
    with get_connection() as conn:
        for row in reader:
            aid = (row.get("audit_id") or "").strip()
            if not aid:
                continue
            exists = conn.execute(
                "SELECT 1 FROM audits WHERE audit_id = ?", (aid,)
            ).fetchone()
            if exists:
                skipped += 1
                continue
            raw_comp = (row.get("compliance") or "").strip()
            comp_val = float(raw_comp) if raw_comp != "" else None
            conn.execute(
                """
                INSERT INTO audits (
                    audit_id, title, organization, department, audit_type, status,
                    audit_date, start_date, end_date, lead_auditor, created_by,
                    scope, objectives, compliance, record_type
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'USER')
                """,
                (
                    aid,
                    (row.get("title") or "").strip(),
                    (row.get("organization") or "User Organization").strip(),
                    (row.get("department") or "General").strip(),
                    (row.get("audit_type") or "ISO 27001").strip(),
                    (row.get("status") or "Planned").strip(),
                    (row.get("audit_date") or "").strip(),
                    (row.get("start_date") or row.get("audit_date") or "").strip(),
                    (row.get("end_date") or row.get("audit_date") or "").strip(),
                    (row.get("lead_auditor") or "").strip(),
                    actor,
                    (row.get("scope") or "").strip(),
                    (row.get("objectives") or "").strip(),
                    comp_val,
                ),
            )
            imported += 1
        append_audit_log(
            conn,
            actor=actor,
            role=role,
            action="CSV_AUDIT_IMPORT",
            entity_type="Audit",
            entity_id="batch",
            details=f"Imported {imported} audits, skipped {skipped} existing IDs.",
        )
        conn.commit()
    return {"imported": imported, "skipped": skipped}


def export_backup_json() -> dict[str, Any]:
    """Generate a complete JSON backup with SHA-256 manifest for restore verification."""
    ensure_initialized()
    tables_dump: dict[str, list[dict[str, Any]]] = {}
    export_tables = [
        "audits",
        "tests",
        "findings",
        "actions",
        "controls",
        "risks",
        "requirements",
        "evidence",
        "audit_logs",
    ]
    with get_connection() as conn:
        for tname in export_tables:
            rows = conn.execute(f"SELECT * FROM {tname}").fetchall()
            tables_dump[tname] = [dict(r) for r in rows]

    canonical = json.dumps(tables_dump, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest_sha256 = compute_sha256_bytes(canonical)
    return {
        "schema_version": "2.0",
        "exported_at": utc_now_iso(),
        "manifest_sha256": manifest_sha256,
        "record_counts": {k: len(v) for k, v in tables_dump.items()},
        "log_chain_verification": verify_audit_log_chain(),
        "tables": tables_dump,
    }


def validate_backup_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Dry-run restore validation verifying manifest SHA-256 and table structures."""
    tables = payload.get("tables")
    expected_hash = payload.get("manifest_sha256", "")
    if not isinstance(tables, dict):
        return {"valid": False, "error": "Backup payload is missing 'tables' object."}
    canonical = json.dumps(tables, sort_keys=True, separators=(",", ":")).encode("utf-8")
    actual_hash = compute_sha256_bytes(canonical)
    matches = (actual_hash == expected_hash) if expected_hash else False
    return {
        "valid": matches,
        "expected_sha256": expected_hash,
        "actual_sha256": actual_hash,
        "record_counts": {k: len(v) for k, v in tables.items() if isinstance(v, list)},
    }


def remove_demo_records(actor: str = "admin", role: str = "Admin") -> int:
    """Remove records tagged DEMO without touching USER records."""
    ensure_initialized()
    removed = 0
    target_tables = ["actions", "findings", "tests", "evidence", "audits", "risks"]
    with get_connection() as conn:
        for tname in target_tables:
            cur = conn.execute(f"DELETE FROM {tname} WHERE record_type = 'DEMO'")
            removed += cur.rowcount
        append_audit_log(
            conn,
            actor=actor,
            role=role,
            action="DEMO_DATA_REMOVED",
            entity_type="Database",
            entity_id="DEMO",
            details=f"Removed {removed} DEMO operational records; USER records preserved.",
        )
        conn.commit()
    return removed


def restore_demo_records(actor: str = "admin", role: str = "Admin") -> int:
    """Restore any missing DEMO records safely without overwriting USER records."""
    ensure_initialized()
    with get_connection() as conn:
        inserted = seed_demo_records(conn, force_restore=True)
        append_audit_log(
            conn,
            actor=actor,
            role=role,
            action="DEMO_DATA_RESTORED",
            entity_type="Database",
            entity_id="DEMO",
            details=f"Restored {inserted} missing DEMO records.",
        )
        conn.commit()
    return inserted
