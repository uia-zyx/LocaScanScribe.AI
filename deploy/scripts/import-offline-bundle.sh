#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
IMAGES_DIR="${IMAGES_DIR:-${PROJECT_ROOT}/deploy/offline/images}"

step() { echo "==> $*"; }

load_archive() {
  local archive="$1"
  step "  loading $(basename "${archive}")"
  gunzip -c "${archive}" | docker load
}

cd "${PROJECT_ROOT}"

if [[ ! -d "${IMAGES_DIR}" ]]; then
  echo "Images directory not found: ${IMAGES_DIR}" >&2
  exit 1
fi

mapfile -t ARCHIVES < <(find "${IMAGES_DIR}" -maxdepth 1 -name '*.tar.gz' | sort)
if [[ ${#ARCHIVES[@]} -eq 0 ]]; then
  echo "No .tar.gz images found in ${IMAGES_DIR}" >&2
  exit 1
fi

step "Loading ${#ARCHIVES[@]} image archive(s)"
for archive in "${ARCHIVES[@]}"; do
  load_archive "${archive}"
done

step "Done"
echo "Images loaded. Run ./deploy/scripts/offline-up.sh to start services."
