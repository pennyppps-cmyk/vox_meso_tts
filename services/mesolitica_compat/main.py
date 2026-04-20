import os
from typing import Any, Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel


class SpeechRequest(BaseModel):
    model: Optional[str] = None
    input: str
    voice: Optional[str] = None
    response_format: Optional[str] = "wav"
    speed: Optional[float] = 1.0


BASE_URL = os.getenv("MESOLITICA_BASE_URL", "http://host.docker.internal:5001").rstrip("/")
TIMEOUT = int(os.getenv("MESOLITICA_TIMEOUT_SECONDS", "120"))
PORT = int(os.getenv("PORT", "5001"))

app = FastAPI(title="Mesolitica OpenAI Compat", version="1.0.0")


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"status": "ok", "provider": "mesolitica_compat", "upstream": BASE_URL}


@app.post("/v1/audio/speech")
def speech(req: SpeechRequest) -> Response:
    payload = {
        "text": req.input,
        "voice": req.voice or "default",
        "output_format": req.response_format or "wav",
    }

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            upstream = client.post(f"{BASE_URL}/synthesize", json=payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Mesolitica upstream unreachable: {exc}") from exc

    if upstream.status_code >= 400:
        raise HTTPException(status_code=upstream.status_code, detail=upstream.text)

    ctype = upstream.headers.get("content-type", "audio/wav")
    if "application/json" in ctype.lower():
        data = upstream.json()
        if isinstance(data, dict) and "audio_base64" in data:
            import base64

            return Response(content=base64.b64decode(data["audio_base64"]), media_type="audio/wav")
        raise HTTPException(
            status_code=500, detail="Mesolitica upstream returned JSON without an 'audio_base64' field."
        )

    return Response(content=upstream.content, media_type=ctype)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=PORT)

