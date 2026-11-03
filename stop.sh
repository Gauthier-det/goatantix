#!/usr/bin/env bash
# Arrête backend + frontend. Laisse Postgres tourner (utile pour ne pas tout recréer) ;
# passe --db pour aussi arrêter le conteneur Postgres.
set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_DIR="$ROOT_DIR/.pids"

stop_pid_file() {
  local name="$1" file="$2"
  if [ -f "$file" ]; then
    local pid
    pid="$(cat "$file")"
    if kill "$pid" 2>/dev/null; then
      echo "$name arrêté (pid $pid)"
    fi
    rm -f "$file"
  fi
}

stop_pid_file "Backend" "$PID_DIR/backend.pid"
stop_pid_file "Frontend" "$PID_DIR/frontend.pid"

if [ "${1:-}" = "--db" ]; then
  echo "==> Arrêt de Postgres"
  cd "$ROOT_DIR/backend"
  docker-compose down
fi

echo "Terminé."
