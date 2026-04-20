#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -d .venv ]]; then
  source .venv/bin/activate
elif [[ -d venv ]]; then
  source venv/bin/activate
else
  echo "No virtual environment found (.venv or venv). Run ./scripts/bootstrap.sh first." >&2
  exit 1
fi

export TTS_CONFIG_PATH="${TTS_CONFIG_PATH:-$ROOT_DIR/config/engines.yaml}"
if [[ -f "$ROOT_DIR/config/backend_commands.env" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/config/backend_commands.env"
fi
python -m app.main
