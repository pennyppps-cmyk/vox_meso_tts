import os
from pathlib import Path
from typing import Dict

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import load_config
from app.engine_runner import EngineRunner
from app.models import SynthesizeRequest, SynthesizeResponse


CONFIG_PATH = os.getenv("TTS_CONFIG_PATH")
config = load_config(CONFIG_PATH)
runner = EngineRunner(config)

app = FastAPI(title="Multi-Engine TTS Server", version="1.0.0")
app.mount("/files", StaticFiles(directory=str(Path(config.output_dir).resolve())), name="files")


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/engines")
def list_engines() -> Dict[str, dict]:
    engines = runner.list_engines()
    return {name: engine.model_dump() for name, engine in engines.items()}


@app.post("/synthesize", response_model=SynthesizeResponse)
def synthesize(req: SynthesizeRequest) -> SynthesizeResponse:
    result = runner.synthesize(req)
    return SynthesizeResponse.model_validate(result)


def run() -> None:
    uvicorn.run("app.main:app", host=config.host, port=config.port, reload=False)


if __name__ == "__main__":
    run()

