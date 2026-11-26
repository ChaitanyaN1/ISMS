# 🛡️ SecureAudit Web Tracker — ISMS ISO/IEC 27001:2022 Audit Management Platform

[![Live Deployment](https://img.shields.io/badge/Live%20Portal-isms1.vercel.app-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://isms1.vercel.app)
[![API Health](https://img.shields.io/badge/Serverless%20API-Online%20%28FastAPI%29-059669?style=for-the-badge&logo=fastapi&logoColor=white)](https://isms1.vercel.app/api/health)
[![Sample PDF Report](https://img.shields.io/badge/Live%20PDF-AUD--2026--001-2563EB?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](https://isms1.vercel.app/api/reports/audit/AUD-2026-001/pdf)

[![ISO/IEC 27001:2022](https://img.shields.io/badge/Standard-ISO%2FIEC%2027001%3A2022%20%2B%20Amd%201%3A2024-2563EB?style=flat-square)](#key-features--capabilities)
[![ISO 19011:2026](https://img.shields.io/badge/Audit%20Guidelines-ISO%2019011%3A2026-0284C7?style=flat-square)](#key-features--capabilities)
[![Frontend](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TypeScript%20%2B%20Tailwind%20v4-0F172A?style=flat-square)](#system-architecture--project-layout)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20Streamlit%20%2B%20SQLite-059669?style=flat-square)](#system-architecture--project-layout)
[![Assurance](https://img.shields.io/badge/Assurance-Salted%20scrypt%20%7C%20HMAC%20Auth%20%7C%20SHA--256%20Chain-D97706?style=flat-square)](#implemented-security--assurance-controls)

---

## 📌 About This Project

**SecureAudit Web Tracker** is a full-stack **Information Security Management System (ISMS) Audit, Risk, and Compliance Governance Platform** aligned with **ISO/IEC 27001:2022** (including **Amendment 1:2024 Climate Action**) and **ISO 19011:2026** audit programme traceability principles, with cross-framework reference mappings to **NIST CSF 2.0** and **SOC 2**.

> 🌐 **Live Production Portal:** **[https://isms1.vercel.app](https://isms1.vercel.app)**  
> Open the link directly in any browser — both the **React + TypeScript SPA** and the **Python FastAPI Serverless Backend** run under a single unified URL with one-click RBAC demo sign-in, live audit checklists, CAPA remediation workflows, SHA-256 evidence verification, and instant PDF/Excel report generation.

### Dual-Interface Architecture
The repository delivers **two synchronized governance interfaces** powered by a shared Python core (`isms_tracker/`) and SQLite database:

1. **SecureAudit Web Tracker (`React + TypeScript + Vite + FastAPI`)** — Hosted live on Vercel at **[https://isms1.vercel.app](https://isms1.vercel.app)** (and runnable locally on `http://localhost:5173`), providing an interactive product landing page, RBAC sign-in, executive compliance analytics, ISO 27001 audit checklists, findings & vulnerabilities cards, CAPA tracker, Statement of Applicability (SoA), 5×5 risk register, SHA-256 evidence vault, formal report sign-off, and 1-click PDF/Excel exports.
2. **ISMS Streamlit Governance Workbench (`Streamlit + Plotly + Pandas`)** — Local 8-page analytical suite on `http://localhost:8501` for audit workpapers, SoA management, append-only CSV imports, SHA-256 manifest-verified JSON backups, and user administration.

---

## 🌐 Live Vercel Deployment & Endpoints

| Resource | Live URL | Description |
| :--- | :--- | :--- |
| **Web Portal (SPA + Landing + Dashboard)** | **[https://isms1.vercel.app](https://isms1.vercel.app)** | Full interactive SecureAudit Web Tracker |
| **API Health & Log-Chain Status** | [`https://isms1.vercel.app/api/health`](https://isms1.vercel.app/api/health) | Live FastAPI status & SHA-256 audit-trail chain verification |
| **Live Generated PDF Audit Report** | [`https://isms1.vercel.app/api/reports/audit/AUD-2026-001/pdf`](https://isms1.vercel.app/api/reports/audit/AUD-2026-001/pdf) | Multi-page ISO 27001 audit report rendered on demand |
| **Live Executive Excel Workbook (`.xlsx`)** | [`https://isms1.vercel.app/api/reports/workbook.xlsx`](https://isms1.vercel.app/api/reports/workbook.xlsx) | 9-sheet ISMS register export (`Audits`, `Tests`, `Findings`, `CAPA`, `SoA`, `Risks`, `Regulatory`, `Evidence`, `Logs`) |
| **OpenAPI / Swagger Documentation** |  [`https://isms1.vercel.app/api/docs`](https://isms1.vercel.app/api/docs) | Interactive FastAPI REST API specification |

---

## ✨ Key Features & Capabilities

### Core Audit & GRC Lifecycle
- **Executive Security Dashboard** — Live KPI cards, per-audit compliance bar charts, severity distribution donuts, control status breakdown, open findings, and overdue CAPA alerts.
- **Audit Programme & Test Workpapers (ISO 27001 Clause 9.2)** — Create, update, and review audits with scope, objectives, lead auditor, audit team, control test procedures, sample sizes, auditor notes, and automatic compliance score recalculation.
- **ISO/IEC 27001:2022 Control Catalogue & Statement of Applicability (Clause 6.1.3)** — 40 Annex A reference controls across all 4 themes (*Organizational, People, Physical, Technological*), plus Clauses 4–10 and 2024 Climate Action Amendment summaries.
- **Findings, Nonconformities & CAPA Remediation (Clause 10.2)** — Structured nonconformity capture (*Criteria, Condition, Root Cause, Impact, Recommendation*) linked to Corrective and Preventive Actions with owners, due dates, overdue flags, and verification notes.
- **Risk Register & Cross-Framework Mappings (Clause 6.1.2)** — 5×5 inherent likelihood × impact scoring, treatment strategy selection, Annex A control linkage, residual risk tracking, and **NIST CSF 2.0** / **SOC 2** mappings.
- **Automated Reporting & Portability** — Generate multi-section **PDF Audit Reports**, 9-sheet **Executive Excel Workbooks (`.xlsx`)**, append-only **CSV imports/exports**, and **SHA-256 manifest-verified JSON backups**.
- **Safe Demo vs. User Data Separation** — Seeded sample records carry an explicit `DEMO` tag and governance banner. Toggle demo records off, purge them cleanly, or restore missing demo records without overwriting `USER` data.

### Implemented Security & Assurance Controls
All eight security and auditability enhancements are implemented and verified by automated `pytest` tests:
1. **Salted `scrypt` Password Hashing (RFC 7914)** — `hashlib.scrypt` (`N=16384, r=8, p=1`, 16-byte random salt) with constant-time `hmac.compare_digest` verification (`isms_tracker/security.py`).
2. **Stateless HMAC-SHA256 Session Tokens** — Signed bearer tokens paired with SQLite session tracking so authentication remains resilient across serverless cold starts and multi-instance deployments.
3. **Failed-Login Lockout Policy** — Automatically locks an account for **15 minutes** after **5 consecutive failed login attempts** (`HTTP 423 Locked`), with Admin unlock capability.
4. **Role-Based Access Control (RBAC)** — Enforced across both UI views and FastAPI endpoints for `Admin`, `Auditor`, `Risk Owner`, and `Viewer` roles.
5. **SHA-256 Evidence Integrity & Upload Validation** — Computes SHA-256 file digest and exact byte size at upload, enforces a **20 MB** cap and MIME/extension allowlist, and re-verifies disk SHA-256 integrity on demand and before download.
6. **Formal Report Review & Approval Sign-Off** — Dedicated workflow tracking `Draft`, `In Review`, `Changes Requested`, and `Approved` states with version numbers, reviewer identity, timestamps, and Admin-only final sign-off.
7. **Tamper-Evident Hash-Chained Audit Trail** — Every login, record mutation, evidence upload, and report sign-off is appended to an immutable SHA-256 hash chain (`GENESIS -> prev_hash -> entry_hash`) with live integrity verification.
8. **Automated Pytest Suite** — Repeatable test suite validating `scrypt` login, 5-attempt lockout, RBAC boundaries, SHA-256 evidence verification, hash-chained logs, and PDF/Excel/JSON exports (`tests/test_isms_platform.py`).

---

## 🏗️ System Architecture & Project Layout

```text
ISMS/
├── vercel.json                       # Vercel full-stack routing (/api/* -> Python serverless, SPA -> dist/)
├── api/
│   └── index.py                      # Vercel Python ASGI entry point with /tmp/isms_vercel storage adapter
├── index.html                        # Vite + React entry HTML (Manrope & Geist Mono typography)
├── package.json                      # Node.js scripts & React/Tailwind/Phosphor/Recharts dependencies
├── vite.config.ts                    # Vite config (0.0.0.0:5173 + local /api proxy to FastAPI :8000)
├── src/                              # SecureAudit React + TypeScript Frontend
│   ├── index.css                     # Systematic brand/neutral/semantic colour & type scale tokens
│   ├── types.ts                      # TypeScript interfaces for all ISMS entities
│   ├── api.ts                        # Typed REST client & bearer session management
│   ├── App.tsx                       # Unified navigation shell & workspace state sync
│   └── components/
│       ├── LandingPage.tsx           # Product overview landing page with scroll word-reveal
│       ├── LoginView.tsx             # Salted scrypt sign-in & 1-click RBAC demo role selector
│       ├── DashboardView.tsx         # KPI cards, Recharts compliance & severity analytics
│       ├── AuditViews.tsx            # Audit projects list, new audit wizard, checklist & sign-off
│       ├── FindingsView.tsx          # Findings & vulnerabilities cards + CAPA remediation tracker
│       ├── ControlsAndRisksView.tsx  # Annex A SoA table, Clauses 4–10, 5x5 Risk Register
│       ├── EvidenceReportsSettings.tsx # SHA-256 Evidence Vault, Report Preview, RBAC Users & Logs
│       └── LegalAndNotFound.tsx      # Privacy policy, governance terms & branded 404 view
├── api_server.py                     # FastAPI REST backend (:8000 locally / serverless on Vercel)
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
│   ├── security.py                   # Scrypt KDF, HMAC tokens, lockout policy, SHA-256 & RBAC
│   ├── catalogue.py                  # ISO 27001:2022 Clauses, Amd 1:2024 & 40 Annex A controls
│   ├── reports.py                    # FPDF2 audit PDF builder & OpenPyXL 9-sheet Excel exporter
│   └── ui.py                         # Shared Streamlit styling & sidebar auth
├── data/
│   ├── demo_data.json                # Illustrative fictional audits, tests, findings, CAPA & risks
│   ├── audit_import_template.csv     # Sample CSV template for append-only audit import
│   └── uploads/                      # Controlled storage for SHA-256 verified evidence files
├── tests/
│   └── test_isms_platform.py         # Automated pytest suite (auth, RBAC, SHA-256, PDF/XLSX)
├── requirements.txt                  # Lean Python dependencies for Vercel Serverless FastAPI
├── requirements-streamlit.txt        # Full local Python suite (FastAPI + Streamlit + Plotly + Pytest)
├── run_all.bat                       # One-click Windows launcher
└── run_all.sh                        # One-command Linux / macOS launcher
```

---

## 🔐 Demonstration Accounts (RBAC)

Both the live portal (**[https://isms1.vercel.app](https://isms1.vercel.app)**) and local installations come pre-seeded with four role-based demonstration accounts (available as 1-click pills on the Sign-In page):

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `Admin@27001!` | Full access, user provisioning, lockout reset, DEMO data purge/restore, and final **Approved** report sign-off |
| **Auditor** | `auditor` | `Auditor@27001!` | Create/edit audits, Annex A SoA, control workpapers, findings, CAPA, evidence uploads, and PDF/Excel exports |
| **Risk Owner** | `riskowner` | `RiskOwner@27001!` | Manage risk register, update assigned CAPA actions, upload evidence, and export reports |
| **Viewer** | `viewer` | `Viewer@27001!` | Read-only access across dashboards and registers + report downloads |

> **Security Note:** These credentials exist strictly for academic demonstration and portfolio evaluation. Never use public demo credentials in a real production environment with confidential organizational data.

---

## 🚀 Local Quick Start (Run Everything Locally)

### Prerequisites
- **Python 3.10+** ([python.org](https://www.python.org/downloads/))
- **Node.js 18+** & **npm** ([nodejs.org](https://nodejs.org/))

### Option A: One-Command Launch

**Windows (PowerShell / Command Prompt):**
```bat
.\run_all.bat
```

**Linux / macOS:**
```bash
./run_all.sh
```

Starts all three local services automatically:
- **SecureAudit React Web Tracker**: `http://localhost:5173`
- **FastAPI REST Backend & OpenAPI Docs**: `http://localhost:8000/api/docs`
- **Streamlit ISMS Workspace**: `http://localhost:8501`

### Option B: Manual Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ChaitanyaN1/ISMS.git
   cd ISMS
   ```
2. **Create a Python virtual environment & install dependencies**
   - **Windows (PowerShell):**
     ```powershell
     py -m venv .venv
     .\.venv\Scripts\Activate.ps1
     python -m pip install --upgrade pip
     python -m pip install -r requirements-streamlit.txt
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     pip install --upgrade pip
     pip install -r requirements-streamlit.txt
     ```
3. **Install Frontend dependencies**
   ```bash
   npm install
   ```
4. **Run the services**
   - **Terminal 1 — FastAPI Backend (`:8000`)**: `uvicorn api_server:app --host 0.0.0.0 --port 8000`
   - **Terminal 2 — React Web Tracker (`:5173`)**: `npm run dev`
   - **Terminal 3 (Optional) — Streamlit Suite (`:8501`)**: `streamlit run app.py --server.port 8501`

---

## ☁️ Deploying Your Own Copy to Vercel

This repository is pre-configured for zero-config full-stack deployment on **Vercel** via `vercel.json` and `api/index.py`:
1. Import `ChaitanyaN1/ISMS` into Vercel.
2. Keep **Build Command** as `npm run build` and **Output Directory** as `dist`.
3. Vercel automatically compiles `dist/` for the React SPA and deploys `api/index.py` as a Python Serverless Function serving `/api/*`.

---

## 🧪 Automated Testing & Build Verification

```bash
# Run automated security, RBAC, SHA-256 evidence & export tests
pytest -v

# Type-check TypeScript and build production frontend bundle
npm run build
```

---

## ⚖️ Academic & Governance Disclaimer

- **Educational Prototype:** Developed as an applied software artefact for *MBA in Cyber Security Management* (National Forensic Sciences University, Gandhinagar).
- **Illustrative Data Notice:** All pre-seeded records (`record_type = 'DEMO'`), organization names (*TechCorp International*), personnel names, scores, and sample evidence files are fictional examples and must **not** be treated as real audit evidence or certification status.
- **Standards Reference:** Plain-language summaries of ISO/IEC 27001:2022, Amendment 1:2024, ISO 19011:2026, NIST CSF 2.0, and SOC 2 are navigation aids only and do not replace licensed ISO standards, accredited certification audits, or qualified legal advice.
