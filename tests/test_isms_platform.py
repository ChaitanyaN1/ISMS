"""Automated unit, security, authorization, evidence integrity, and export tests.

Implements Priority 6 recommendation from Chapter 7 of the Minor Project Report:
repeatable verification of scrypt password hashing, failed-login lockout,
SHA-256 evidence integrity, report sign-off RBAC, hash-chained audit logs,
and PDF/Excel/JSON exports.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def isolated_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> TestClient:
    db_file = tmp_path / "test_isms.db"
    monkeypatch.setenv("ISMS_DB_PATH", str(db_file))
    from api_server import app
    from isms_tracker.db import ensure_initialized

    ensure_initialized()
    return TestClient(app)


def test_health_and_initial_seed(isolated_client: TestClient) -> None:
    res = isolated_client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert body["audit_log_chain_valid"] is True

    ws = isolated_client.get("/api/workspace").json()
    assert len(ws["audits"]) >= 4
    assert len(ws["controls"]) == 40
    assert len(ws["findings"]) >= 8
    assert len(ws["actions"]) >= 7


def test_scrypt_login_and_lockout_policy(isolated_client: TestClient) -> None:
    # Wrong password 5 times triggers 423 Locked
    for attempt in range(1, 5):
        bad = isolated_client.post(
            "/api/auth/login", json={"username": "viewer", "password": "WrongPassword123"}
        )
        assert bad.status_code == 401

    fifth = isolated_client.post(
        "/api/auth/login", json={"username": "viewer", "password": "WrongPassword123"}
    )
    assert fifth.status_code == 423
    assert "locked" in fifth.json()["detail"].lower()

    # Even valid password fails while locked
    blocked = isolated_client.post(
        "/api/auth/login", json={"username": "viewer", "password": "Viewer@27001!"}
    )
    assert blocked.status_code == 423

    # Admin login succeeds and unlocks viewer
    admin_login = isolated_client.post(
        "/api/auth/login", json={"username": "admin", "password": "Admin@27001!"}
    )
    assert admin_login.status_code == 200
    token = admin_login.json()["token"]

    unlock = isolated_client.post(
        "/api/users/viewer/unlock",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert unlock.status_code == 200

    viewer_ok = isolated_client.post(
        "/api/auth/login", json={"username": "viewer", "password": "Viewer@27001!"}
    )
    assert viewer_ok.status_code == 200


def test_rbac_authorization_boundaries(isolated_client: TestClient) -> None:
    viewer_token = isolated_client.post(
        "/api/auth/login", json={"username": "viewer", "password": "Viewer@27001!"}
    ).json()["token"]
    auditor_token = isolated_client.post(
        "/api/auth/login", json={"username": "auditor", "password": "Auditor@27001!"}
    ).json()["token"]
    admin_token = isolated_client.post(
        "/api/auth/login", json={"username": "admin", "password": "Admin@27001!"}
    ).json()["token"]

    # Viewer cannot create audit
    forbidden = isolated_client.post(
        "/api/audits",
        headers={"Authorization": f"Bearer {viewer_token}"},
        json={"title": "Unauthorized Audit", "audit_date": "2026-11-26"},
    )
    assert forbidden.status_code == 403

    # Auditor can create audit
    created = isolated_client.post(
        "/api/audits",
        headers={"Authorization": f"Bearer {auditor_token}"},
        json={
            "title": "Cloud IAM Quarterly Review",
            "department": "Cloud Security",
            "audit_date": "2026-11-26",
            "seed_default_controls": True,
        },
    )
    assert created.status_code == 200
    new_aid = created.json()["audit"]["audit_id"]

    # Auditor can submit for review, but only Admin can grant final 'Approved' sign-off
    aud_sign = isolated_client.post(
        f"/api/audits/{new_aid}/approve",
        headers={"Authorization": f"Bearer {auditor_token}"},
        json={"approval_status": "Approved", "report_version": "1.0"},
    )
    assert aud_sign.status_code == 403

    adm_sign = isolated_client.post(
        f"/api/audits/{new_aid}/approve",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "approval_status": "Approved",
            "report_version": "1.0",
            "approval_notes": "Approved for executive distribution.",
        },
    )
    assert adm_sign.status_code == 200
    assert adm_sign.json()["audit"]["approval_status"] == "Approved"


def test_evidence_sha256_upload_and_verification(isolated_client: TestClient) -> None:
    auditor_token = isolated_client.post(
        "/api/auth/login", json={"username": "auditor", "password": "Auditor@27001!"}
    ).json()["token"]

    content = b"Control A.8.5 MFA Configuration Export - Verified Sample\n"
    up = isolated_client.post(
        "/api/evidence/upload",
        headers={"Authorization": f"Bearer {auditor_token}"},
        data={
            "title": "MFA Policy Export",
            "entity_type": "Control",
            "entity_id": "A.8.5",
            "audit_id": "AUD-2026-001",
            "control_id": "A.8.5",
            "notes": "Unit test upload",
        },
        files={"file": ("mfa_policy_sample.txt", content, "text/plain")},
    )
    assert up.status_code == 200
    ev = up.json()["evidence"]
    assert len(ev["sha256_hash"]) == 64
    assert ev["file_size_bytes"] == len(content)

    ver = isolated_client.post(
        f"/api/evidence/{ev['evidence_id']}/verify",
        headers={"Authorization": f"Bearer {auditor_token}"},
    )
    assert ver.status_code == 200
    assert ver.json()["matches"] is True


def test_pdf_excel_and_backup_manifest_exports(isolated_client: TestClient) -> None:
    pdf_res = isolated_client.get("/api/reports/audit/AUD-2026-001/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF")

    xlsx_res = isolated_client.get("/api/reports/workbook.xlsx")
    assert xlsx_res.status_code == 200
    assert len(xlsx_res.content) > 2000

    bkp_res = isolated_client.get("/api/backup/json")
    assert bkp_res.status_code == 200

    ver_bkp = isolated_client.post(
        "/api/backup/verify",
        files={"file": ("backup.json", bkp_res.content, "application/json")},
    )
    assert ver_bkp.status_code == 200
    assert ver_bkp.json()["valid"] is True

    chain = isolated_client.get("/api/audit-logs/verify")
    assert chain.status_code == 200
    assert chain.json()["valid"] is True
