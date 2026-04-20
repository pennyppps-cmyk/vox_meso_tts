#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 6 ]]; then
  echo "Usage: run_engine.sh <engine> <text> <voice> <language> <output_path> <format>" >&2
  exit 1
fi

ENGINE="$1"
TEXT="$2"
VOICE="$3"
LANGUAGE="$4"
OUTPUT_PATH="$5"
OUTPUT_FORMAT="$6"

KEY="$(echo "$ENGINE" | tr '[:lower:]-' '[:upper:]_')"
VAR_NAME="TTS_CMD_${KEY}"
CMD="${!VAR_NAME:-}"

if [[ -z "$CMD" ]]; then
  cat >&2 <<EOF
No command configured for engine '$ENGINE'.
Set environment variable:
  $VAR_NAME

The command runs in a shell and can use:
  \$TTS_TEXT
  \$TTS_VOICE
  \$TTS_LANGUAGE
  \$TTS_OUTPUT_PATH
  \$TTS_OUTPUT_FORMAT

Example:
  export $VAR_NAME='python -m my_tts --text "$TTS_TEXT" --voice "$TTS_VOICE" --out "$TTS_OUTPUT_PATH"'
EOF
  exit 1
fi

export TTS_ENGINE="$ENGINE"
export TTS_TEXT="$TEXT"
export TTS_VOICE="$VOICE"
export TTS_LANGUAGE="$LANGUAGE"
export TTS_OUTPUT_PATH="$OUTPUT_PATH"
export TTS_OUTPUT_FORMAT="$OUTPUT_FORMAT"

bash -lc "$CMD"

if [[ ! -f "$OUTPUT_PATH" ]]; then
  echo "Engine '$ENGINE' command finished but no output file was created at: $OUTPUT_PATH" >&2
  exit 1
fi

