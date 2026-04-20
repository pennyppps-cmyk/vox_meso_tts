#!/usr/bin/env bash
set -euo pipefail

# Copy to scripts/start_backends.sh and edit each command for your installed models.
# Example:
#   cp scripts/start_backends.example.sh scripts/start_backends.sh
#   chmod +x scripts/start_backends.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p logs

run_bg() {
  local name="$1"
  local cmd="$2"
  echo "Starting ${name}: ${cmd}"
  nohup bash -lc "$cmd" >"logs/${name}.log" 2>&1 &
  echo "${name} pid=$!"
}

# Replace placeholders below with real commands for your environment.
run_bg "mesolitica" "python services/mesolitica_server.py --port 7101"
run_bg "kokoro" "python services/kokoro_server.py --port 7102"
run_bg "melotts" "python services/melotts_server.py --port 7103"
run_bg "xtts_v2" "python services/xtts_server.py --port 7104"
run_bg "fish_speech" "python services/fish_speech_server.py --port 7105"
run_bg "chatterbox" "python services/chatterbox_server.py --port 7106"
run_bg "vibevoice" "python services/vibevoice_server.py --port 7107"
run_bg "tinytts" "python services/tinytts_server.py --port 7108"
run_bg "voxtral" "python services/voxtral_server.py --port 7109"

echo "All backend launch commands submitted."

