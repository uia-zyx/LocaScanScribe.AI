#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROJECT_NAME="${PROJECT_NAME:-openlocalsearchparser}"

step() { echo "==> $*"; }

cd "${PROJECT_ROOT}"

PORTS_ENV="${PROJECT_ROOT}/deploy/ports.env"
if [[ ! -f "${PORTS_ENV}" ]]; then
  cp "${PROJECT_ROOT}/deploy/ports.example.env" "${PORTS_ENV}"
  echo "Created deploy/ports.env from ports.example.env"
fi

if [[ "${1:-}" == "--import" ]]; then
  "${SCRIPT_DIR}/import-offline-bundle.sh"
fi

COMPOSE=(docker compose --env-file "${PORTS_ENV}" -f deploy/docker-compose.yml -f deploy/docker-compose.offline.yml -p "${PROJECT_NAME}")

step "Starting services (offline mode)"
"${COMPOSE[@]}" up -d --no-build

source "${PORTS_ENV}"
FRONTEND_PORT="${OLSP_FRONTEND_HOST_PORT:-18473}"
BACKEND_PORT="${OLSP_BACKEND_HOST_PORT:-52891}"

step "Services started"
echo "Frontend: http://localhost:${FRONTEND_PORT}"
echo "Backend:  http://localhost:${BACKEND_PORT}/docs"
echo "MCP:      http://localhost:${BACKEND_PORT}/mcp"
