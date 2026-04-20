import os
from typing import Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field

from siphon.tts_router import TTSRouter


class RouterSpeechRequest(BaseModel):
    input: str = Field(min_length=1)
    engine: Optional[str] = None
    voice: Optional[str] = "default"
    language: Optional[str] = "en"
    response_format: str = "wav"
    speed: float = 1.0
    realtime: bool = False
    premium: bool = False
    cloning: bool = False


app = FastAPI(title="SIPHON TTS Router", version="1.0.0")
router = TTSRouter()
PORT = int(os.getenv("ROUTER_PORT", "5010"))


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/tts/health")
def provider_health() -> JSONResponse:
    status: Dict[str, Dict[str, str]] = {}
    for provider_name, provider in router.providers.items():
        base = provider.url.rsplit("/", 3)[0]
        health_url = f"{base}/health"
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(health_url)
            status[provider_name] = {"status": "ok" if resp.status_code < 400 else "degraded", "url": provider.url}
        except Exception:
            status[provider_name] = {"status": "down", "url": provider.url}
    return JSONResponse({"status": "ok", "providers": status})


@app.post("/v1/audio/speech")
def route_speech(req: RouterSpeechRequest) -> Response:
    try:
        audio, ctype, selected = router.synthesize(
            text=req.input,
            voice=req.voice,
            language=req.language,
            response_format=req.response_format,
            speed=req.speed,
            realtime=req.realtime,
            premium=req.premium,
            cloning=req.cloning,
            engine=req.engine,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    headers = {"X-TTS-Provider": selected}
    return Response(content=audio, media_type=ctype, headers=headers)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("siphon.server:app", host="0.0.0.0", port=PORT)

