# ISMS Audit Tracker

A local Streamlit workspace for managing ISO/IEC 27001 audit programmes, control implementation, findings, and corrective and preventive actions (CAPA).

## Included features

- Dashboard with audit status, compliance trend, department summary, control implementation, open findings, and upcoming or overdue actions
- Audit register with create, edit, delete, search, and status filters
- Findings and CAPA workflows with owners, target dates, status, evidence notes, and linked records
- Control register with applicability, implementation status, domain, and findings count
- Append-only audit CSV import, CSV exports, and a complete JSON backup download
- Separate demo and user records, with safe restore and removal controls for demo data
- Local SQLite storage; no cloud service or account is required

The bundled control list is a small illustrative Annex A selection, not the full catalogue or a Statement of Applicability. The sample records are fictional and must not be treated as audit evidence or conclusions.

## Windows installation and run

1. Install Python 3.10 or newer from [python.org](https://www.python.org/downloads/windows/) and select **Add Python to PATH**.
2. Open PowerShell in this project folder.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install the project packages and launch the app:

   ```powershell
   python -m pip install -r requirements.txt
   python -m streamlit run app.py
   ```

The app opens in your browser at `http://localhost:8501` by default. Stop it with **Ctrl+C** in PowerShell.

If PowerShell prevents environment activation, run it directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## First launch and data safety

On first launch, the app creates `data/isms_tracker.db` and inserts clearly labelled demo records. Seeding is one-time and uses insert-only behavior: it does not replace an existing record with the same ID. Records created or imported through the app are labelled `USER`.

Use **Data Management** to:

- Import an audit register CSV. Required columns: `audit_id`, `title`, `department`, `status`, and `audit_date`. Existing IDs are skipped; they are never overwritten.
- Export audits, findings, actions, and controls to CSV, or download a complete JSON backup.
- Restore missing demo records or remove demo records without deleting user records.

A CSV example is provided at `data/audit_import_template.csv`. Dates should use `YYYY-MM-DD`; compliance scores are optional numbers from 0 to 100. Findings and actions can be created and maintained in the app.

The database stays on the computer running Streamlit. Back it up before moving or reinstalling the project. This starter project is designed for one local user and does not provide sign-in, role-based access, or multi-user synchronization. Keep the database and exports within your organization's approved storage controls.

## Project layout

- `app.py` — dashboard
- `pages/1_Audit_Register.py` — audit programme management
- `pages/2_Findings_and_CAPA.py` — findings and corrective actions
- `pages/3_Control_Register.py` — control applicability and implementation
- `pages/4_Data_Management.py` — import, export, and demo record management
- `isms_tracker/db.py` — SQLite schema, persistence, and safe demo seeding
- `isms_tracker/ui.py` — shared page styling
- `data/demo_data.json` — illustrative sample audits, findings, actions, and controls
- `data/audit_import_template.csv` — audit import example
- `requirements.txt` — Python package requirements
