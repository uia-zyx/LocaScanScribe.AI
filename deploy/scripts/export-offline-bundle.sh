#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
PROJECT_NAME="${PROJECT_NAME:-openlocalsearchparser}"
OUTPUT_DIR="${OUTPUT_DIR:-${PROJECT_ROOT}/deploy/offline/images}"

step() { echo "==> $*"; }

ensure_ports_env() {
  local deploy_dir="${PROJECT_ROOT}/deploy"
  local ports_env="${deploy_dir}/ports.env"
  if [[ ! -f "${ports_env}" ]]; then
    cp "${deploy_dir}/ports.example.env" "${ports_env}"
    echo "Created deploy/ports.env from ports.example.env"
  fi
  echo "${ports_env}"
}

save_image() {
  local tag="$1"
  local output="$2"
  step "  saving ${tag} -> $(basename "${output}")"
  docker save "${tag}" | gzip -c > "${output}"
}

cd "${PROJECT_ROOT}"
mkdir -p "${OUTPUT_DIR}"

PORTS_ENV="$(ensure_ports_env)"
COMPOSE=(docker compose --env-file "${PORTS_ENV}" -f deploy/docker-compose.yml -p "${PROJECT_NAME}")

step "Building application images"
"${COMPOSE[@]}" build

step "Pulling third-party images"
"${COMPOSE[@]}" pull postgres qdrant redis minio llama-ocr llama-embedding

OFFLINE_BACKEND="openlocalsearchparser/backend:offline"
OFFLINE_WORKER="openlocalsearchparser/worker:offline"
OFFLINE_FRONTEND="openlocalsearchparser/frontend:offline"

step "Tagging offline images"
docker tag "${PROJECT_NAME}-backend" "${OFFLINE_BACKEND}"
docker tag "${PROJECT_NAME}-worker" "${OFFLINE_WORKER}"
docker tag "${PROJECT_NAME}-frontend" "${OFFLINE_FRONTEND}"

declare -a FILES=(
  "backend.tar.gz"
  "worker.tar.gz"
  "frontend.tar.gz"
  "postgres-16-alpine.tar.gz"
  "qdrant.tar.gz"
  "redis-7-alpine.tar.gz"
  "minio.tar.gz"
  "llama-cpp-server-cuda.tar.gz"
)
declare -a TAGS=(
  "${OFFLINE_BACKEND}"
  "${OFFLINE_WORKER}"
  "${OFFLINE_FRONTEND}"
  "postgres:16-alpine"
  "qdrant/qdrant:latest"
  "redis:7-alpine"
  "minio/minio:latest"
  "ghcr.io/ggml-org/llama.cpp:server-cuda"
)

step "Saving images to ${OUTPUT_DIR}"
for i in "${!FILES[@]}"; do
  save_image "${TAGS[$i]}" "${OUTPUT_DIR}/${FILES[$i]}"
done

cat > "${OUTPUT_DIR}/manifest.json" <<EOF
{
  "version": 1,
  "created_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "project_name": "${PROJECT_NAME}",
  "images": [
    {"file": "backend.tar.gz", "tag": "${OFFLINE_BACKEND}"},
    {"file": "worker.tar.gz", "tag": "${OFFLINE_WORKER}"},
    {"file": "frontend.tar.gz", "tag": "${OFFLINE_FRONTEND}"},
    {"file": "postgres-16-alpine.tar.gz", "tag": "postgres:16-alpine"},
    {"file": "qdrant.tar.gz", "tag": "qdrant/qdrant:latest"},
    {"file": "redis-7-alpine.tar.gz", "tag": "redis:7-alpine"},
    {"file": "minio.tar.gz", "tag": "minio/minio:latest"},
    {"file": "llama-cpp-server-cuda.tar.gz", "tag": "ghcr.io/ggml-org/llama.cpp:server-cuda"}
  ]
}
EOF

step "Done"
echo "Offline bundle ready in: ${OUTPUT_DIR}"
