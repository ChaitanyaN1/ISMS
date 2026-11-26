#!/usr/bin/env bash
set -euo pipefail

echo "========================================================="
echo "  SecureAudit Web Tracker & ISMS ISO/IEC 27001 Platform"
echo "========================================================="

if [ ! -d ".venv" ]; then
  echo "[1/4] Creating Python virtual environment..."
  python3 -m venv .venv
fi

echo "[2/4] Installing Python packages..."
./.venv/bin/pip install -q --upgrade pip
./.venv/bin/pip install -q -r requirements-streamlit.txt

if [ ! -d "node_modules" ]; then
  echo "[3/4] Installing Node.js frontend packages..."
  npm install
fi

cleanup() {
  echo "Stopping background services..."
  kill "${API_PID:-}" "${ST_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "[4/4] Starting FastAPI (:8000), Streamlit (:8501), and React Web Tracker (:5173)..."
./.venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000 &
API_PID=$!

./.venv/bin/streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true &
ST_PID=$!

npm run dev
