# Multi-TTS Stack for WSL2 (Mesolitica + Kokoro + VibeVoice + Voxtral)

This repo now contains a Docker-based multi-provider TTS deployment for WSL2 Ubuntu with NVIDIA GPU access.

## Providers

- `Mesolitica` (existing Flask service, bridged to OpenAI-style API)
- `Kokoro` (`hexgrad/Kokoro-82M`)
- `VibeVoice-Realtime-0.5B` (custom FastAPI wrapper)
- `Voxtral-4B-TTS-2603` (vLLM-Omni style server + concurrency cap)

## Service Ports

- Mesolitica compat: `5001`
- Kokoro: `5002`
- VibeVoice: `5003`
- Voxtral: `5004`
- SIPHON router: `5010`
- Nginx ingress: `8080`
- Redis: `6379`

## One-Shot Setup (WSL2)

```bash
cd /home/andy/mesolitica-tts
./scripts/wsl2_setup_stack.sh
```

Health:

```bash
./scripts/wsl2_healthcheck_stack.sh
```

## Nginx Routes

- `/tts/mesolitica`
- `/tts/kokoro`
- `/tts/vibevoice`
- `/tts/voxtral`
- `/tts/health`

## SIPHON Routing Logic

The router in [siphon/tts_router.py](/home/andy/mesolitica-tts/siphon/tts_router.py) applies:

- Malay/BM -> Mesolitica
- Realtime requests -> VibeVoice
- Premium or cloning requests -> Voxtral
- Default -> Kokoro

Voxtral concurrency is capped to 3 with Redis-coordinated slots.

## Key Files

- Compose stack: [docker-compose.yml](/home/andy/mesolitica-tts/docker-compose.yml)
- SIPHON router API: [siphon/server.py](/home/andy/mesolitica-tts/siphon/server.py)
- Router logic: [siphon/tts_router.py](/home/andy/mesolitica-tts/siphon/tts_router.py)
- Nginx config: [docker/nginx/conf.d/default.conf](/home/andy/mesolitica-tts/docker/nginx/conf.d/default.conf)
- Mesolitica bridge: [services/mesolitica_compat/main.py](/home/andy/mesolitica-tts/services/mesolitica_compat/main.py)
- VibeVoice wrapper: [services/vibevoice/main.py](/home/andy/mesolitica-tts/services/vibevoice/main.py)
- Deployment guide: [docs/DEPLOYMENT.md](/home/andy/mesolitica-tts/docs/DEPLOYMENT.md)
- Troubleshooting guide: [docs/TROUBLESHOOTING.md](/home/andy/mesolitica-tts/docs/TROUBLESHOOTING.md)

## Important Notes

- `services/vibevoice/main.py` currently includes placeholder synthesis logic to keep the API contract stable. Replace with real model inference for production audio quality.
- The Voxtral container image/flags may need pinning based on your chosen vLLM-Omni release.
- Set `.env` value `MESOLITICA_BASE_URL` to your existing Mesolitica Flask endpoint.

