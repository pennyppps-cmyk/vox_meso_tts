# Multi-TTS stack (Mesolitica, Kokoro, VibeVoice, Voxtral)

A Docker-based text-to-speech gateway for WSL2 Ubuntu with an NVIDIA GPU. Several TTS engines sit behind one OpenAI-style API,
and the SIPHON router picks the engine per request (Malay text to Mesolitica, for example). See `README.md` for ports and routes,
`docs/DEPLOYMENT.md` and `docs/TROUBLESHOOTING.md`.

## Layout

- `app/`: the gateway API (`main.py`, `router.py`, `engine_runner.py`, `config.py`, `models.py`).
- `siphon/`: the routing service that chooses an engine per request (`tts_router.py`).
- `services/`: engine adapters (`mesolitica_compat`, `vibevoice`).
- `docker/`, `docker-compose.yml`: one container per engine plus nginx in front.
- `config/engines.yaml`: which engines exist and their voices. `config/*.example` and `engines.sample.yaml` are templates.
- `scripts/`: WSL2 setup, health checks and engine start scripts. `deploy/`: the systemd unit.
- `server.py`, `run.sh`: the original single Flask service, still used by the Mesolitica bridge.

## Commands

- First setup on WSL2: `scripts/wsl2_setup_stack.sh`, then `docker compose up -d`.
- Health: `scripts/healthcheck_all.sh` (or `healthcheck.sh` for the single service).

## Rules

- This repository is public. Never commit keys, tokens, `.env`, model weights or generated audio.
- Keep the API OpenAI-compatible; add an engine by adding a container, an adapter and an `engines.yaml` entry.
- Test Malay and English text for every engine change, and say which engine served each test.
