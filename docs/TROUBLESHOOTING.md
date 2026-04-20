# Multi-TTS Troubleshooting Guide

## Quick Triage

1. Verify Docker services:
   ```bash
   docker compose ps
   ```
2. Verify aggregate health:
   ```bash
   ./scripts/wsl2_healthcheck_stack.sh
   ```
3. Check router health directly:
   ```bash
   curl -s http://127.0.0.1:5010/v1/tts/health
   ```
4. Check logs:
   ```bash
   docker compose logs --tail=200 nginx siphon_router kokoro vibevoice voxtral mesolitica_compat
   ```

## Common Issues

### 1) `docker: could not select device driver "" with capabilities: [[gpu]]`
- Cause: NVIDIA runtime not available to Docker in WSL2.
- Fix:
  1. Enable GPU support in Docker Desktop.
  2. Update NVIDIA Windows driver.
  3. Verify from WSL:
     ```bash
     docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
     ```

### 2) `tts/health` shows provider `down`
- Cause: upstream container failed or wrong route path.
- Fix:
  1. Check container status: `docker compose ps`
  2. Check per-service logs.
  3. Validate provider endpoint in router env vars (`MESOLITICA_URL`, `KOKORO_URL`, `VIBEVOICE_URL`, `VOXTRAL_URL`).

### 3) Mesolitica path failing only
- Cause: existing Mesolitica Flask service not reachable from container network.
- Fix:
  1. Confirm Mesolitica is running in WSL host.
  2. Validate `.env`:
     ```env
     MESOLITICA_BASE_URL=http://host.docker.internal:5500
     ```
  3. Restart `mesolitica_compat`.

### 4) Voxtral returns busy / queued failures
- Cause: hard cap is 3 concurrent requests.
- Fix:
  1. Keep cap at 3 for stability.
  2. Add retries with exponential backoff in caller.
  3. Route non-premium traffic to Kokoro.

### 5) Latency spikes
- Cause: model cold start or VRAM pressure.
- Fix:
  1. Keep Kokoro and VibeVoice warm.
  2. Reduce Voxtral workload and use premium-only route.
  3. Check GPU memory:
     ```bash
     watch -n 1 nvidia-smi
     ```

## Router Behavior (Expected)

- `language` Malay/BM -> Mesolitica
- `realtime=true` -> VibeVoice
- `premium=true` or `cloning=true` -> Voxtral
- default -> Kokoro

## Smoke Test Calls

Standard (Kokoro expected):
```bash
curl -X POST http://127.0.0.1:5010/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"hello team","language":"en"}' \
  --output /tmp/kokoro.wav -i
```

Realtime (VibeVoice expected):
```bash
curl -X POST http://127.0.0.1:5010/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"live response","language":"en","realtime":true}' \
  --output /tmp/vibevoice.wav -i
```

Premium (Voxtral expected):
```bash
curl -X POST http://127.0.0.1:5010/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"premium voice sample","language":"en","premium":true}' \
  --output /tmp/voxtral.wav -i
```

Malay (Mesolitica expected):
```bash
curl -X POST http://127.0.0.1:5010/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{"input":"Apa khabar semua","language":"ms"}' \
  --output /tmp/mesolitica.wav -i
```

