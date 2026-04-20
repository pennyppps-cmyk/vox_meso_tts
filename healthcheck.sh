#!/usr/bin/env bash
set -euo pipefail

HOST="${1:-127.0.0.1}"
PORT="${2:-3000}"

curl --fail --silent --show-error "http://${HOST}:${PORT}/health"
