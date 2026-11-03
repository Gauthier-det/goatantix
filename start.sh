#!/usr/bin/env bash
# Démarre toute la stack Goatantix : Postgres (Docker), backend FastAPI, frontend Vue.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
PID_DIR="$ROOT_DIR/.pids"
mkdir -p "$PID_DIR"

echo "==> Docker (Colima)"
if ! docker info > /dev/null 2>&1; then
  echo "Démarrage de Colima..."
  colima start
fi

echo "==> Postgres"
cd "$BACKEND_DIR"
docker-compose up -d

echo "==> Backend (FastAPI)"
cd "$BACKEND_DIR"
if [ ! -d ".venv" ]; then
  echo "Pas de venv trouvé : exécute d'abord 'python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt'"
  exit 1
fi
source .venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$ROOT_DIR/backend.log" 2>&1 &
echo $! > "$PID_DIR/backend.pid"
deactivate

echo "==> Frontend (Vite)"
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  echo "Pas de node_modules trouvé : exécute d'abord 'npm install' dans frontend/"
  exit 1
fi
nohup npm run dev -- --port 5173 > "$ROOT_DIR/frontend.log" 2>&1 &
echo $! > "$PID_DIR/frontend.pid"

sleep 2
echo ""
echo "Goatantix est lancé :"
echo "  - API      : http://localhost:8000"
echo "  - Frontend : http://localhost:5173"
echo ""
echo "Logs : backend.log / frontend.log à la racine du projet."
echo "Pour arrêter : ./stop.sh"
