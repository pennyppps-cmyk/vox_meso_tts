# Voxpro Meso TTS

Small Flask API for Mesolitica TTS using `malaya-speech` VITS voices.

## What To Put In GitHub

Commit only the project files:

- `server.py`
- `requirements.txt`
- `README.md`
- `.gitignore`
- `run.sh`
- `healthcheck.sh`
- `deploy/mesolitica-tts.service`

Do not commit:

- `venv/`
- downloaded Hugging Face caches
- Ubuntu system folders
- logs or temporary files

The voice models are downloaded automatically on first run and are usually stored under:

- `~/.cache/huggingface/`

## Server Endpoints

- `GET /`
- `GET /health`
- `GET /voices`
- `POST /tts`

## Supported Voices

- `yasmin`
- `haqkiem`
- `osman`
- `husein`

## Ubuntu Deployment

These steps are for your colleague on the Proxmox or RDP Ubuntu server.

### 1. Clone the repo

```bash
git clone <your-github-repo-url> mesolitica-tts
cd mesolitica-tts
```

### 2. Install system packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

### 3. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

### 4. Run the server

```bash
./run.sh
```

By default it listens on `0.0.0.0:5500`.

### 5. Verify it is up

```bash
./healthcheck.sh
```

You should get a JSON response from `/health`.

## Systemd Service

If your colleague wants it to start automatically on Ubuntu:

### 1. Review the service file

Open:

- `deploy/mesolitica-tts.service`

Update these values if needed:

- `User=andy`
- `WorkingDirectory=/home/andy/mesolitica-tts`
- `ExecStart=/home/andy/mesolitica-tts/run.sh`

### 2. Install the service

```bash
sudo cp deploy/mesolitica-tts.service /etc/systemd/system/mesolitica-tts.service
sudo systemctl daemon-reload
sudo systemctl enable mesolitica-tts
sudo systemctl start mesolitica-tts
```

### 3. Check service status

```bash
sudo systemctl status mesolitica-tts
journalctl -u mesolitica-tts -f
```

## Environment Variables

- `MESOLITICA_TTS_HOST` default: `0.0.0.0`
- `MESOLITICA_TTS_PORT` default: `5500`
- `MESOLITICA_TTS_VOICE` default: `yasmin`
- `MESOLITICA_TTS_FORMAT` default: `wav`
- `MESOLITICA_TTS_CHUNK_SIZE` default: `8192`
- `MESOLITICA_TTS_PRELOAD` default: `true`

Example:

```bash
MESOLITICA_TTS_PORT=5500 MESOLITICA_TTS_VOICE=yasmin ./run.sh
```

## First Run Note

On first run, `malaya-speech` downloads the required voice and vocoder files from Hugging Face. The server must have internet access for that initial download.

After the models are cached, later runs can reuse the local cache.

## API Example

```bash
curl -X POST http://127.0.0.1:5500/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello from Mesolitica TTS",
    "voice": "yasmin",
    "format": "wav"
  }' \
  --output sample.wav
```
