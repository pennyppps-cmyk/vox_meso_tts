#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -f "$ROOT_DIR/config/backend_commands.env" ]]; then
  # shellcheck disable=SC1091
  source "$ROOT_DIR/config/backend_commands.env"
fi

ENGINES=(
  mesolitica
  kokoro
  piper
  melotts
  xtts_v2
  fish_speech
  chatterbox
  vibevoice
  tinytts
  voxtral
)

echo "Preflight check for backend commands"
echo

missing=0
for engine in "${ENGINES[@]}"; do
  key="$(echo "$engine" | tr '[:lower:]-' '[:upper:]_')"
  var="TTS_CMD_${key}"
  val="${!var:-}"

  if [[ "$engine" == "piper" ]]; then
    echo "[ok] $engine uses scripts/run_piper.sh unless TTS_CMD_PIPER override is set"
    continue
  fi

  if [[ -n "$val" ]]; then
    echo "[ok] $engine -> $var is set"
  else
    echo "[missing] $engine -> set $var in config/backend_commands.env"
    missing=1
  fi
done

echo
if [[ $missing -eq 1 ]]; then
  echo "Some engines are missing command mappings."
  exit 1
fi

echo "All command mappings are present."

