"""Security, cryptographic hashing, lockout, and evidence verification utilities.

Implements the Priority 1, 2, 3, and 5 assurance controls recommended in
Chapter 7 of the Minor Project Report:
1. Cryptographically strong salted password hashing via scrypt (RFC 7914) with
   constant-time comparison (`hmac.compare_digest`).
2. Account rate-limiting and failed-login lockout policy.
3. SHA-256 evidence file hashing, file size accounting, MIME allowlist validation,
   and download-time hash verification.
4. Append-only hash-chained audit trail (`prev_hash` -> `entry_hash`) for tamper detection.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

SESSION_SIGNING_KEY = os.environ.get(
    "ISMS_SESSION_SECRET",
    "secureaudit-isms-hmac-sha256-session-key-v2-27001",
).encode("utf-8")

# Lockout policy constants
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15

# Evidence upload policy constants
MAX_EVIDENCE_BYTES = 20 * 1024 * 1024  # 20 MB
ALLOWED_EVIDENCE_MIME_TYPES = {
    "application/pdf",
    "text/plain",
    "text/csv",
    "application/json",
    "image/png",
    "image/jpeg",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
ALLOWED_EVIDENCE_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".csv",
    ".json",
    ".png",
    ".jpg",
    ".jpeg",
    ".xlsx",
    ".docx",
    ".log",
}

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "Admin": {
        "view_all",
        "manage_users",
        "manage_audits",
        "manage_controls",
        "manage_risks",
        "manage_findings",
        "manage_actions",
        "manage_evidence",
        "approve_reports",
        "export_reports",
        "manage_demo_data",
        "verify_audit_log",
    },
    "Auditor": {
        "view_all",
        "manage_audits",
        "manage_controls",
        "manage_findings",
        "manage_actions",
        "manage_evidence",
        "export_reports",
        "verify_audit_log",
    },
    "Risk Owner": {
        "view_all",
        "manage_risks",
        "manage_actions",
        "manage_evidence",
        "export_reports",
    },
    "Viewer": {
        "view_all",
        "export_reports",
    },
}


def utc_now_iso() -> str:
    """Return UTC timestamp in ISO-8601 format."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def hash_password(password: str, salt_hex: str | None = None) -> tuple[str, str]:
    """Hash a password with scrypt (N=16384, r=8, p=1, dklen=64) and 16-byte random salt.

    Replaces the legacy unsalted SHA-256 construction noted in Chapter 4.2 & 7.2.
    """
    if not password or len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    salt = bytes.fromhex(salt_hex) if salt_hex else secrets.token_bytes(16)
    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=64,
    )
    return f"scrypt$16384$8$1${derived.hex()}", salt.hex()


def verify_password(password: str, stored_hash: str, salt_hex: str) -> bool:
    """Verify a password against its stored scrypt hash in constant time."""
    if not password or not stored_hash or not salt_hex:
        return False
    try:
        salt = bytes.fromhex(salt_hex)
        if stored_hash.startswith("scrypt$"):
            parts = stored_hash.split("$")
            n_val, r_val, p_val, expected_hex = int(parts[1]), int(parts[2]), int(parts[3]), parts[4]
            candidate = hashlib.scrypt(
                password.encode("utf-8"),
                salt=salt,
                n=n_val,
                r=r_val,
                p=p_val,
                dklen=len(bytes.fromhex(expected_hex)),
            ).hex()
            return hmac.compare_digest(candidate, expected_hex)
        return False
    except Exception:
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password complexity requirements (min 10 chars, upper, lower, digit)."""
    if len(password) < 10:
        return False, "Password must be at least 10 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must include at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must include at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must include at least one number."
    return True, "Strong password."


def is_account_locked(locked_until: str | None) -> tuple[bool, int]:
    """Return whether account is currently locked and remaining seconds."""
    if not locked_until:
        return False, 0
    try:
        until_dt = datetime.fromisoformat(locked_until)
        if until_dt.tzinfo is None:
            until_dt = until_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        if until_dt > now:
            remaining = int((until_dt - now).total_seconds())
            return True, max(1, remaining)
    except ValueError:
        return False, 0
    return False, 0


def compute_lockout_timestamp(minutes: int = LOCKOUT_MINUTES) -> str:
    """Return ISO timestamp when a locked account becomes eligible again."""
    return (
        datetime.now(timezone.utc) + timedelta(minutes=minutes)
    ).replace(microsecond=0).isoformat()


def compute_sha256_bytes(data: bytes) -> str:
    """Calculate hex SHA-256 digest of raw bytes."""
    return hashlib.sha256(data).hexdigest()


def compute_sha256_file(file_path: str) -> str:
    """Calculate hex SHA-256 digest of a file on disk."""
    digest = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename to prevent path traversal."""
    base = os.path.basename(filename or "evidence.bin")
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", base)
    return cleaned[:120] or "evidence.bin"


def validate_evidence_upload(
    filename: str, content_type: str, size_bytes: int
) -> tuple[bool, str]:
    """Validate evidence file size, extension, and media type."""
    if size_bytes <= 0:
        return False, "Uploaded file is empty."
    if size_bytes > MAX_EVIDENCE_BYTES:
        return False, "Upload failed. The file is over 20 MB."
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EVIDENCE_EXTENSIONS:
        return (
            False,
            f"Unsupported file extension '{ext}'. Allowed formats: PDF, TXT, CSV, JSON, PNG, JPG, XLSX, DOCX, LOG.",
        )
    normalized_mime = (content_type or "application/octet-stream").split(";")[0].strip().lower()
    if normalized_mime != "application/octet-stream" and normalized_mime not in ALLOWED_EVIDENCE_MIME_TYPES:
        return False, f"Unsupported media type '{normalized_mime}'."
    return True, "Valid evidence file."


def compute_log_entry_hash(
    prev_hash: str,
    timestamp: str,
    actor: str,
    role: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: str,
) -> str:
    """Compute deterministic SHA-256 chain hash for an audit log entry."""
    payload = json.dumps(
        {
            "prev_hash": prev_hash,
            "timestamp": timestamp,
            "actor": actor,
            "role": role,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def generate_session_token(user_payload: dict[str, str] | None = None) -> str:
    """Generate a stateless HMAC-SHA256 signed bearer token (works across serverless instances)."""
    if not user_payload:
        return secrets.token_urlsafe(32)
    body = dict(user_payload)
    body["nonce"] = secrets.token_hex(8)
    raw = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    sig = hmac.new(SESSION_SIGNING_KEY, b64.encode("ascii"), hashlib.sha256).hexdigest()
    return f"{b64}.{sig}"


def verify_signed_session_token(token: str) -> dict[str, Any] | None:
    """Verify an HMAC-SHA256 signed bearer token and return its user payload."""
    if not token or "." not in token:
        return None
    try:
        b64, sig = token.rsplit(".", 1)
        expected_sig = hmac.new(
            SESSION_SIGNING_KEY, b64.encode("ascii"), hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(sig, expected_sig):
            return None
        pad = "=" * (-len(b64) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(b64 + pad).decode("utf-8"))
        exp = decoded.get("expires_at")
        if exp:
            exp_dt = datetime.fromisoformat(exp)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if exp_dt < datetime.now(timezone.utc):
                return None
        return decoded
    except Exception:
        return None


def has_permission(role: str, permission: str) -> bool:
    """Return True if role holds the requested permission."""
    return permission in ROLE_PERMISSIONS.get(role, set())
