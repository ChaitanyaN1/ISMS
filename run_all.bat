@echo off
setlocal
echo =========================================================
echo   SecureAudit Web Tracker ^& ISMS ISO/IEC 27001 Platform
echo =========================================================

if not exist ".venv" (
    echo [1/4] Creating Python virtual environment...
    py -m venv .venv
)

echo [2/4] Installing Python dependencies...
.\.venv\Scripts\python.exe -m pip install --upgrade pip -q
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -q

if not exist "node_modules" (
    echo [3/4] Installing Node.js frontend dependencies...
    call npm install
)

echo [4/4] Launching FastAPI (8000), React Web Tracker (5173), and Streamlit (8501)...
start "SecureAudit API Server" .\.venv\Scripts\python.exe -m uvicorn api_server:app --host 0.0.0.0 --port 8000
start "Streamlit ISMS Workspace" .\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
call npm run dev
