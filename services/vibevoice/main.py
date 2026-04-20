import io
import os
import wave
from typing import Any, Dict, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel


class SpeechRequest(BaseModel):
    model: Optional[str] = None
    input: str
    voice: Optional[str] = "default"
    response_format: Optional[str] = "wav"
    speed: Optional[float] = 1.0
    stream: Optional[bool] = False


PORT = int(os.getenv("PORT", "5003"))
MODEL_ID = os.getenv("MODEL_ID", "microsoft/VibeVoice-Realtime-0.5B")
SAMPLE_RATE = 24000

app = FastAPI(title="VibeVoice OpenAI Compat", version="1.0.0")


def _fake_audio(text: str) -> bytes:
    # Placeholder waveform generator. Replace with real VibeVoice model inference.
    duration = max(0.4, min(8.0, len(text) * 0.045))
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = 0.15 * np.sin(2 * np.pi * 220 * t)
    pcm = np.int16(tone * 32767)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())
    return buf.getvalue()


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "provider": "vibevoice", "model": MODEL_ID}


@app.post("/v1/audio/speech")
def speech(req: SpeechRequest) -> Response:
    if not req.input.strip():
        raise HTTPException(status_code=400, detail="input is required")

    audio = _fake_audio(req.input)
    return Response(content=audio, media_type="audio/wav")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT)

