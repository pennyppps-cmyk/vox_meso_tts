#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/5] Checking Docker..."
if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed in WSL2. Install Docker Desktop + WSL integration first."
  exit 1
fi

echo "[2/5] Checking Docker Compose..."
if ! docker compose version >/dev/null 2>&1; then
  echo "Docker Compose plugin is missing."
  exit 1
fi

echo "[3/5] Checking NVIDIA container runtime..."
if ! docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi >/dev/null 2>&1; then
  echo "GPU check failed in Docker. Ensure Docker Desktop GPU support is enabled."
  exit 1
fi

echo "[4/5] Creating .env if missing..."
if [[ ! -f .env ]]; then
  cat > .env <<EOF
MESOLITICA_BASE_URL=http://host.docker.internal:5500
EOF
fi

echo "[5/5] Starting multi-TTS stack..."
docker compose pull || true
docker compose build
docker compose up -d

echo
echo "Stack started."
echo "Nginx entrypoint: http://localhost:8080/tts/health"
echo "SIPHON router:    http://localhost:5010/v1/audio/speech"

