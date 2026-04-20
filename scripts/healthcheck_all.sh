#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-127.0.0.1}"
PORT="${2:-3000}"
BASE="http://${HOST}:${PORT}"

echo "Checking gateway: ${BASE}/health"
curl --fail --silent --show-error "${BASE}/health" >/dev/null
echo "[ok] gateway health"

echo "Checking /engines"
curl --fail --silent --show-error "${BASE}/engines" >/dev/null
echo "[ok] engines endpoint"

echo "Running synth smoke test (kokoro)"
resp="$(curl --fail --silent --show-error -X POST "${BASE}/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"engine":"kokoro","text":"health check","voice":"af_alloy","language":"en","output_format":"wav"}')"

echo "$resp" | grep -q "output_url"
echo "[ok] synth endpoint responded"

