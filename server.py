import io
import os
import threading
import wave
from typing import Dict, Iterable, Tuple

import numpy as np
from flask import Flask, Response, jsonify, request, stream_with_context

try:
    import torch
except ImportError:
    torch = None

try:
    import malaya_speech
except ImportError:
    malaya_speech = None


app = Flask(__name__)

DEFAULT_HOST = os.environ.get("MESOLITICA_TTS_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.environ.get("MESOLITICA_TTS_PORT", "5500"))
DEFAULT_VOICE = os.environ.get("MESOLITICA_TTS_VOICE", "yasmin")
DEFAULT_FORMAT = os.environ.get("MESOLITICA_TTS_FORMAT", "wav").lower()
DEFAULT_CHUNK_SIZE = int(os.environ.get("MESOLITICA_TTS_CHUNK_SIZE", "8192"))

VOICE_MODELS = {
    "husein": "mesolitica/VITS-osman",
    "osman": "mesolitica/VITS-osman",
    "yasmin": "mesolitica/VITS-yasmin",
    "haqkiem": "mesolitica/VITS-haqkiem",
}

MODEL_CACHE: Dict[str, object] = {}
MODEL_LOCK = threading.Lock()
VOCODER = None
VOCODER_LOCK = threading.Lock()


def pick_device() -> str:
    if torch is None:
        return "unknown"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


def normalize_voice(voice: str) -> Tuple[str, str]:
    selected = (voice or DEFAULT_VOICE).strip().lower()
    if selected not in VOICE_MODELS:
        allowed = ", ".join(sorted(VOICE_MODELS))
        raise ValueError(f"Unsupported voice '{selected}'. Allowed voices: {allowed}")
    return selected, VOICE_MODELS[selected]


def load_model(voice: str):
    if malaya_speech is None:
        raise RuntimeError(
            "malaya-speech is not installed. Install dependencies from requirements.txt first."
        )

    canonical_voice, model_name = normalize_voice(voice)
    with MODEL_LOCK:
        model = MODEL_CACHE.get(canonical_voice)
        if model is None:
            model = malaya_speech.tts.vits(model=model_name)
            MODEL_CACHE[canonical_voice] = model
    return model, canonical_voice


def load_vocoder():
    global VOCODER
    if malaya_speech is None:
        raise RuntimeError(
            "malaya-speech is not installed. Install dependencies from requirements.txt first."
        )

    with VOCODER_LOCK:
        if VOCODER is None:
            VOCODER = malaya_speech.vocoder.melgan(model="universal-1024")
    return VOCODER


def synthesize_waveform(text: str, voice: str) -> Tuple[np.ndarray, int, str]:
    cleaned = (text or "").strip()
    if not cleaned:
        raise ValueError("text is required")

    model, resolved_voice = load_model(voice)
    vocoder = load_vocoder()
    result = model.predict(cleaned)

    if "universal-output" in result:
        waveform = np.asarray(vocoder(result["universal-output"]), dtype=np.float32)
    elif "y" in result:
        waveform = np.asarray(result["y"], dtype=np.float32)
    else:
        raise RuntimeError("Unsupported TTS model output format")

    if waveform.ndim != 1:
        waveform = waveform.reshape(-1)

    return waveform, 22050, resolved_voice


def pcm16_bytes(waveform: np.ndarray) -> bytes:
    clipped = np.clip(waveform, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype(np.int16)
    return pcm.tobytes()


def wav_bytes(pcm_bytes: bytes, sample_rate: int) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_bytes)
    return buffer.getvalue()


def chunk_bytes(payload: bytes, chunk_size: int = DEFAULT_CHUNK_SIZE) -> Iterable[bytes]:
    for offset in range(0, len(payload), chunk_size):
        yield payload[offset: offset + chunk_size]


@app.get("/")
def home():
    return jsonify({
        "status": "ok",
        "provider": "mesolitica",
        "voices": sorted(VOICE_MODELS.keys()),
    })


@app.get("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "provider": "mesolitica",
            "engine": "malaya-speech VITS",
            "device": pick_device(),
            "voices": sorted(VOICE_MODELS.keys()),
            "loaded_voices": sorted(MODEL_CACHE.keys()),
            "default_voice": DEFAULT_VOICE,
            "default_format": DEFAULT_FORMAT,
        }
    )


@app.get("/voices")
def voices():
    return jsonify(
        {
            "default_voice": DEFAULT_VOICE,
            "voices": [
                {"id": voice, "model": model_name}
                for voice, model_name in sorted(VOICE_MODELS.items())
            ],
        }
    )


@app.post("/tts")
def tts():
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    voice = payload.get("voice", DEFAULT_VOICE)
    audio_format = str(payload.get("format", DEFAULT_FORMAT) or DEFAULT_FORMAT).lower()
    stream = bool(payload.get("stream", False))

    if audio_format not in {"wav", "pcm"}:
        return jsonify({"error": "format must be 'wav' or 'pcm'"}), 400

    try:
        waveform, sample_rate, resolved_voice = synthesize_waveform(text, voice)
        pcm_bytes_payload = pcm16_bytes(waveform)
    except Exception as error:
        return jsonify({"error": str(error)}), 500

    body = wav_bytes(pcm_bytes_payload, sample_rate) if audio_format == "wav" else pcm_bytes_payload
    mimetype = "audio/wav" if audio_format == "wav" else "application/octet-stream"
    headers = {
        "X-TTS-Voice": resolved_voice,
        "X-TTS-Sample-Rate": str(sample_rate),
        "X-TTS-Channels": "1",
        "Cache-Control": "no-store",
    }

    if stream:
        return Response(
            stream_with_context(chunk_bytes(body)),
            mimetype=mimetype,
            headers=headers,
            direct_passthrough=True,
        )

    return Response(body, mimetype=mimetype, headers=headers)


if __name__ == "__main__":
    if os.environ.get("MESOLITICA_TTS_PRELOAD", "true").lower() == "true":
        try:
            load_model(DEFAULT_VOICE)
            load_vocoder()
        except Exception as error:
            print(f"[mesolitica-tts] preload skipped: {error}")

    app.run(host=DEFAULT_HOST, port=DEFAULT_PORT, threaded=True)
