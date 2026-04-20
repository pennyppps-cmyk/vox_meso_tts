#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage: run_piper.sh <text> <voice> <output_path>" >&2
  exit 1
fi

TEXT="$1"
VOICE="$2"
OUT="$3"

if [[ -z "${PIPER_BIN:-}" ]]; then
  PIPER_BIN="piper"
else
  PIPER_BIN="$PIPER_BIN"
fi

if [[ -z "$VOICE" ]]; then
  echo "Voice is required for piper (for example en_US-lessac-medium)." >&2
  exit 1
fi

MODEL_DIR="${PIPER_MODEL_DIR:-./models/piper}"
MODEL_PATH="${MODEL_DIR}/${VOICE}.onnx"
CONFIG_PATH="${MODEL_DIR}/${VOICE}.onnx.json"

if [[ ! -f "$MODEL_PATH" ]]; then
  echo "Missing Piper model: $MODEL_PATH" >&2
  exit 1
fi

if [[ ! -f "$CONFIG_PATH" ]]; then
  echo "Missing Piper config: $CONFIG_PATH" >&2
  exit 1
fi

echo "$TEXT" | "$PIPER_BIN" --model "$MODEL_PATH" --config "$CONFIG_PATH" --output_file "$OUT"

