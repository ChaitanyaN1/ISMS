"""Vercel Python Serverless Function entry point (`api/index.py`).

Serves all `/api/*` endpoints on Vercel (auth, workspace, audits, findings,
CAPA, controls SoA, risks, SHA-256 evidence vault, PDF/Excel reports, JSON backup).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if os.environ.get("VERCEL") or not os.access(ROOT_DIR / "data", os.W_OK):
    vercel_runtime_dir = Path("/tmp/isms_vercel")
    vercel_runtime_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("ISMS_DB_PATH", str(vercel_runtime_dir / "isms_tracker.db"))
    os.environ.setdefault("ISMS_UPLOADS_DIR", str(vercel_runtime_dir / "uploads"))

from api_server import app  # noqa: E402, F401
