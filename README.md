# 🛡️ SecureAudit Web Tracker — ISMS ISO/IEC 27001:2022 Audit Management Platform

[![ISO/IEC 27001:2022](https://img.shields.io/badge/Standard-ISO%2FIEC%2027001%3A2022%20%2B%20Amd%201%3A2024-2563EB?style=flat-square)](#standards--reference-coverage)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript%20%2B%20Vite-0F172A?style=flat-square)](#system-architecture)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Streamlit%20%2B%20SQLite-059669?style=flat-square)](#system-architecture)
[![Security Assurance](https://img.shields.io/badge/Assurance-Salted%20scrypt%20%7C%20SHA--256%20Evidence%20%26%20Logs-D97706?style=flat-square)](#implemented-security--assurance-controls)

A complete, locally self-contained **Information Security Management System (ISMS) Audit & Governance Platform** aligned with **ISO/IEC 27001:2022** (including **Amendment 1:2024 Climate Action**) and **ISO 19011:2026** audit programme traceability principles.

The repository delivers **two synchronized web interfaces** backed by a single shared **SQLite** database (`data/isms_tracker.db`):

1. **SecureAudit Web Tracker (`React + TypeScript + Tailwind CSS v4 + FastAPI`)** — Modern web platform on `http://localhost:5173` featuring an interactive product overview page, role-based sign-in, executive security dashboard, ISO 27001 audit checklists, findings & vulnerabilities cards, CAPA tracker, Statement of Applicability (SoA), risk register, SHA-256 evidence vault, live report preview, and 1-click PDF/Excel exports.
2. **ISMS Streamlit Governance Suite (`Streamlit + Plotly + Pandas`)** — Full 8-page analytical workspace on `http://localhost:8501` for audit operations, SoA management, CSV append-only imports, verified JSON backups, and administrative review.

---

## ✨ Key Features & Capabilities

### Core Audit & GRC Lifecycle
- **Executive Security Dashboard** — Live KPI cards, compliance trend & per-audit scores, severity distribution, control status overview, open findings, and overdue CAPA alerts.
- **Audit Programme & Test Workpapers (Clause 9.2)** — Create/update/delete audits with scope, objectives, lead auditor, audit team, control test procedures, sample sizes, auditor notes, and automatic compliance score recalculation.
- **ISO/IEC 27001:2022 Control Catalogue & Statement of Applicability (Clause 6.1.3)** — 40 Annex A reference controls across all 4 domains (*Organizational, People, Physical, Technological*), plus Clauses 4–10 and 2024 Climate Action Amendment summaries.
- **Findings, Nonconformities & CAPA Remediation (Clause 10.2)** — Structured issue capture (*Criteria, Condition, Root Cause, Impact, Recommendation*) linked to Corrective and Preventive Actions with owners, target dates, overdue tracking, and verification notes.
- **Risk Register & Cross-Framework Mappings (Clause 6.1.2)** — 5×5 inherent likelihood × impact scoring, treatment selection, Annex A linkage, residual risk tracking, and illustrative **NIST CSF 2.0** and **SOC 2** mappings.
- **Automated Reporting & Portability** — Generate multi-section **PDF Audit Reports**, 9-sheet **Executive Excel Workbooks (`.xlsx`)**, append-only **CSV imports/exports**, and **SHA-256 manifest-verified JSON backups**.
- **Safe Demo vs. User Data Separation** — Seeded sample records carry an explicit `DEMO` tag and warning banner. Toggle demo records off, remove them cleanly, or restore missing demo records without ever overwriting `USER` data.

### Implemented Security & Assurance Controls
All eight priority recommendations from the Minor Project Report are implemented and verified by automated tests:
1. **Salted `scrypt` Password Hashing (RFC 7914)** — Replaces legacy unsalted SHA-256 with `hashlib.scrypt` (`N=16384, r=8, p=1`, 16-byte cryptographic salt) and constant-time `hmac.compare_digest` verification (`isms_tracker/security.py`).
2. **Failed-Login Lockout Policy** — Automatically locks an account for **15 minutes** after **5 consecutive failed login attempts** (`HTTP 423 Locked`), with Admin unlock capability.
3. **Role-Based Access Control (RBAC)** — Enforced across both UI and REST API endpoints for `Admin`, `Auditor`, `Risk Owner`, and `Viewer` roles.
4. **SHA-256 Evidence Integrity & Upload Validation** — Computes SHA-256 file digest and exact byte size at upload, enforces a **20 MB** cap and MIME/extension allowlist, and verifies the disk SHA-256 digest before every download.
5. **Formal Report Review & Approval Sign-Off** — Dedicated workflow tracking `Draft`, `In Review`, `Changes Requested`, and `Approved` states with version numbers, reviewer identity, timestamps, and Admin-only final sign-off.
6. **Tamper-Evident Hash-Chained Audit Trail** — Every authentication, record edit, evidence upload, and report approval is recorded in an append-only SHA-256 hash chain (`GENESIS -> prev_hash -> entry_hash`) with live chain verification.
7. **Verified Backup & Dry-Run Restore Validation** — JSON backups embed a canonical SHA-256 manifest digest that can be verified prior to restoration.
8. **Automated Pytest Suite** — Repeatable tests covering authentication, lockout, RBAC boundaries, SHA-256 evidence verification, hash-chained logs, and PDF/Excel/JSON exports (`tests/test_isms_platform.py`).

---

## 🏗️ System Architecture & Project Layout

```text
ISMS/
├── index.html                        # Vite + React entry HTML (Manrope & Geist Mono typography)
├── package.json                      # Node.js scripts & React/Tailwind/Phosphor dependencies
├── vite.config.ts                    # Vite config (0.0.0.0:5173 + /api proxy to FastAPI :8000)
├── src/                              # SecureAudit React + TypeScript Frontend
│   ├── index.css                     # Systematic brand/neutral/semantic colour & type scale tokens
│   ├── types.ts                      # TypeScript interfaces for all ISMS entities
│   ├── api.ts                        # Typed REST client & session management
│   ├── App.tsx                       # Unified navigation shell & workspace state sync
│   └── components/
│       ├── LandingPage.tsx           # Conversion & overview landing page with scroll word-reveal
│       ├── LoginView.tsx             # Salted scrypt sign-in & demo role selector
│       ├── DashboardView.tsx         # KPI cards, Recharts compliance & severity analytics
│       ├── AuditViews.tsx            # Audit projects list, new audit wizard, checklist & sign-off
│       ├── FindingsView.tsx          # Findings & vulnerabilities cards + CAPA remediation tracker
│       ├── ControlsAndRisksView.tsx  # Annex A SoA table, Clauses 4–10, 5x5 Risk Register
│       ├── EvidenceReportsSettings.tsx # SHA-256 Evidence Vault, Report Preview, RBAC Users & Logs
│       └── LegalAndNotFound.tsx      # Privacy policy, governance terms & branded 404 view
├── api_server.py                     # FastAPI REST backend (:8000) serving React Web Tracker
├── app.py                            # Streamlit Home Overview Dashboard (:8501)
├── pages/                            # Multi-page Streamlit Governance Suite
│   ├── 1_Audit_Register.py           # Audit planning & control test workpapers
│   ├── 2_Findings_and_CAPA.py        # Findings & CAPA workflows
│   ├── 3_Control_Register.py         # Annex A SoA & Clauses 4–10 reference
│   ├── 4_Data_Management.py          # Append-only CSV import, JSON backup & DEMO controls
│   ├── 5_Risk_and_Compliance.py      # Risk register & NIST CSF 2.0 / SOC 2 mappings
│   ├── 6_Evidence_Reports_and_Logs.py # SHA-256 evidence vault, PDF/XLSX exports & log chain
│   └── 7_User_Administration.py      # Local RBAC provisioning & lockout reset
├── isms_tracker/                     # Shared Core Python Package
│   ├── db.py                         # SQLite schema, CRUD, safe demo seeding & hash-chain logs
│   ├── security.py                   # Scrypt KDF, lockout policy, SHA-256 & RBAC permissions
│   ├── catalogue.py                  # ISO 27001:2022 Clauses, Amd 1:2024 & 40 Annex A controls
│   ├── reports.py                    # FPDF2 audit PDF builder & OpenPyXL 9-sheet Excel exporter
│   └── ui.py                         # Shared Streamlit styling & sidebar auth
├── data/
│   ├── demo_data.json                # Illustrative fictional audits, tests, findings, CAPA & risks
│   ├── audit_import_template.csv     # Sample CSV template for append-only audit import
│   └── uploads/                      # Local controlled storage for SHA-256 verified evidence
├── tests/
│   └── test_isms_platform.py         # Automated pytest suite (auth, RBAC, SHA-256, PDF/XLSX)
├── run_all.bat                       # One-click Windows launcher
├── run_all.sh                        # One-command Linux / macOS launcher
└── requirements.txt                  # Python package dependencies
```

---

## 🚀 Quick Start (Run Everything)

### Prerequisites
- **Python 3.10+** ([python.org](https://www.python.org/downloads/))
- **Node.js 18+** & **npm** ([nodejs.org](https://nodejs.org/))

---

### Option A: One-Command Launch

#### On Windows (PowerShell / Command Prompt)
```bat
.\run_all.bat
```

#### On Linux / macOS
```bash
./run_all.sh
```

This automatically creates `.venv`, installs Python and Node dependencies if needed, and starts all three services:
- **SecureAudit React Web Tracker**: `http://localhost:5173`
- **FastAPI REST Backend & OpenAPI Docs**: `http://localhost:8000/docs`
- **Streamlit ISMS Workspace**: `http://localhost:8501`

---

### Option B: Manual Step-by-Step Setup

#### 1. Clone the repository
```bash
git clone https://github.com/ChaitanyaN1/ISMS.git
cd ISMS
```

#### 2. Set up Python environment & install backend dependencies
**Windows (PowerShell):**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-streamlit.txt
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-streamlit.txt
```

#### 3. Install Frontend dependencies
```bash
npm install
```

#### 4. Start the services
1. **Terminal 1 — FastAPI Backend (`:8000`)**:
   ```bash
   uvicorn api_server:app --host 0.0.0.0 --port 8000
   ```
2. **Terminal 2 — SecureAudit React Web App (`:5173`)**:
   ```bash
   npm run dev
   ```
3. **Terminal 3 (Optional) — Streamlit ISMS Interface (`:8501`)**:
   ```bash
   streamlit run app.py --server.port 8501
   ```

---

## 🔐 Local Demonstration Accounts (RBAC)

On first launch, `data/isms_tracker.db` is automatically initialized with salted `scrypt` demonstration accounts for testing role-based permissions:

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `Admin@27001!` | Full access, user provisioning, lockout reset, DEMO data purge/restore, and final **Approved** report sign-off |
| **Auditor** | `auditor` | `Auditor@27001!` | Create/edit audits, Annex A SoA, control workpapers, findings, CAPA, evidence uploads, and PDF/Excel exports |
| **Risk Owner** | `riskowner` | `RiskOwner@27001!` | Manage risk register, update assigned CAPA actions, upload evidence, and export reports |
| **Viewer** | `viewer` | `Viewer@27001!` | Read-only access across dashboards and registers + report downloads |

> **Security Warning:** These credentials exist strictly for local academic demonstration and evaluation. Never use public demo credentials in a shared or production environment.

---

## 🧪 Running Tests & Production Build Verification

Run the automated Python security, RBAC, evidence SHA-256, and report export test suite:
```bash
pytest -v
```

Verify TypeScript compilation and build the production React bundle:
```bash
npm run build
```

---

## ⚖️ Academic & Governance Disclaimer

- **Educational Prototype:** Prepared as an applied software artefact for *MBA in Cyber Security Management* (National Forensic Sciences University, Gandhinagar).
- **Illustrative Data Notice:** All pre-seeded records (`record_type = 'DEMO'`), organization names (*TechCorp International*), personnel names, scores, and evidence files are fictional examples and must **not** be treated as real audit evidence or organizational conclusions.
- **Standards Reference:** Plain-language summaries of ISO/IEC 27001:2022, Amendment 1:2024, ISO 19011:2026, NIST CSF 2.0, and SOC 2 are navigation aids only and do not substitute for licensed ISO standards, accredited certification audits, or qualified legal review.
