#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-http://127.0.0.1:8080}"

echo "Checking aggregate health..."
curl --fail --silent --show-error "${BASE}/tts/health"
echo
echo "Done."

