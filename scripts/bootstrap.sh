#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ -d .venv ]]; then
  VENV_DIR=".venv"
elif [[ -d venv ]]; then
  VENV_DIR="venv"
else
  python3 -m venv .venv
  VENV_DIR=".venv"
fi

source "${VENV_DIR}/bin/activate"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

mkdir -p outputs config
if [[ ! -f config/engines.yaml ]]; then
  cp config/engines.sample.yaml config/engines.yaml
fi
if [[ ! -f config/backend_commands.env ]]; then
  cp config/backend_commands.env.example config/backend_commands.env
fi

echo "Bootstrap complete."
echo "Next: ./scripts/run_gateway.sh"
