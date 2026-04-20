#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
  echo "venv/ not found. Create it first with:"
  echo "  python3 -m venv venv"
  echo "  source venv/bin/activate"
  echo "  pip install -r requirements.txt"
  exit 1
fi

source venv/bin/activate

export MESOLITICA_TTS_HOST="${MESOLITICA_TTS_HOST:-0.0.0.0}"
export MESOLITICA_TTS_PORT="${MESOLITICA_TTS_PORT:-5500}"
export MESOLITICA_TTS_VOICE="${MESOLITICA_TTS_VOICE:-yasmin}"
export MESOLITICA_TTS_FORMAT="${MESOLITICA_TTS_FORMAT:-wav}"
export MESOLITICA_TTS_PRELOAD="${MESOLITICA_TTS_PRELOAD:-true}"

exec python server.py
