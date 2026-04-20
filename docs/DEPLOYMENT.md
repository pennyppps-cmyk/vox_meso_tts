# WSL2 Multi-TTS Deployment Guide

## Scope

This stack adds:
- Mesolitica OpenAI-compatible bridge (`5001`)
- Kokoro (`5002`)
- VibeVoice (`5003`)
- Voxtral (`5004`)
- SIPHON router (`5010`)
- Nginx unified ingress (`8080`)
- Redis queue/coordination (`6379`)

## Prerequisites

1. Docker Desktop installed on Windows.
2. Docker WSL integration enabled for Ubuntu.
3. GPU integration enabled in Docker Desktop.
4. Existing Mesolitica Flask service running in WSL host.

## Install + Start

```bash
cd /home/andy/mesolitica-tts
./scripts/wsl2_setup_stack.sh
```

## Health

```bash
./scripts/wsl2_healthcheck_stack.sh
```

Expected:
```json
{"status":"ok","providers":{...}}
```

## Endpoint Map

- Nginx aggregate health:
  - `GET http://127.0.0.1:8080/tts/health`
- Direct providers:
  - `http://127.0.0.1:8080/tts/mesolitica/v1/audio/speech`
  - `http://127.0.0.1:8080/tts/kokoro/v1/audio/speech`
  - `http://127.0.0.1:8080/tts/vibevoice/v1/audio/speech`
  - `http://127.0.0.1:8080/tts/voxtral/v1/audio/speech`
- SIPHON router:
  - `POST http://127.0.0.1:5010/v1/audio/speech`

## Stop / Restart

```bash
docker compose down
docker compose up -d
```

## Notes

- `services/vibevoice/main.py` is a compatibility wrapper scaffold. Replace placeholder synthesis with actual VibeVoice inference code in production.
- Voxtral image and runtime flags may require adjustment depending on the exact `vLLM-Omni` image version you pin.

