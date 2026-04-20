import os
import shlex
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Tuple

import httpx
from fastapi import HTTPException

from app.models import AppConfig, EngineConfig, SynthesizeRequest


class EngineRunner:
    def __init__(self, config: AppConfig):
        self.config = config
        self.output_dir = Path(config.output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def list_engines(self) -> Dict[str, EngineConfig]:
        return {k: v for k, v in self.config.engines.items() if v.enabled}

    def synthesize(self, req: SynthesizeRequest) -> Dict[str, Any]:
        engine = self.config.engines.get(req.engine)
        if engine is None or not engine.enabled:
            raise HTTPException(status_code=404, detail=f"Engine '{req.engine}' is not enabled.")

        ext = req.output_format
        output_file = self.output_dir / f"{req.engine}_{uuid.uuid4().hex}.{ext}"
        started = time.perf_counter()

        if engine.type == "command":
            meta = self._run_command_engine(engine, req, output_file)
        elif engine.type == "http":
            meta = self._run_http_engine(engine, req, output_file)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported engine type: {engine.type}")

        elapsed = time.perf_counter() - started
        rel_path = output_file.relative_to(Path.cwd().resolve())
        return {
            "engine": req.engine,
            "voice": req.voice,
            "language": req.language,
            "output_path": str(output_file),
            "output_url": f"{self.config.base_url}/files/{rel_path.as_posix()}",
            "duration_seconds": round(elapsed, 3),
            "meta": meta,
        }

    def _render_command(self, template: str, req: SynthesizeRequest, output_file: Path, opts: Dict[str, Any]) -> str:
        values = {
            "text": req.text.replace('"', '\\"'),
            "voice": req.voice or "",
            "language": req.language or "",
            "output": str(output_file),
            "format": req.output_format,
        }
        for key, value in opts.items():
            values[f"opt_{key}"] = str(value)
        return template.format(**values)

    def _merge_options(self, engine: EngineConfig, req: SynthesizeRequest) -> Dict[str, Any]:
        merged = dict(engine.default_options)
        merged.update(req.options)
        return merged

    def _run_command_engine(self, engine: EngineConfig, req: SynthesizeRequest, output_file: Path) -> Dict[str, Any]:
        if not engine.command_template:
            raise HTTPException(status_code=500, detail="command_template is missing for command engine")

        options = self._merge_options(engine, req)
        command = self._render_command(engine.command_template, req, output_file, options)
        cmd = shlex.split(command)

        env = os.environ.copy()
        env.update(engine.extra_env)

        try:
            proc = subprocess.run(
                cmd,
                env=env,
                timeout=engine.timeout_seconds,
                capture_output=True,
                text=True,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise HTTPException(status_code=504, detail=f"Engine timeout: {exc}") from exc

        if proc.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Engine command failed",
                    "command": command,
                    "stderr": proc.stderr[-2000:],
                    "stdout": proc.stdout[-2000:],
                },
            )

        if not output_file.exists():
            raise HTTPException(status_code=500, detail="Engine completed but output file was not created.")

        return {"mode": "command", "command": command}

    def _run_http_engine(self, engine: EngineConfig, req: SynthesizeRequest, output_file: Path) -> Dict[str, Any]:
        if not engine.endpoint:
            raise HTTPException(status_code=500, detail="endpoint is missing for http engine")

        options = self._merge_options(engine, req)
        payload = {
            "text": req.text,
            "voice": req.voice,
            "language": req.language,
            "options": options,
            "output_path": str(output_file),
            "output_format": req.output_format,
        }

        try:
            with httpx.Client(timeout=engine.timeout_seconds) as client:
                resp = client.post(engine.endpoint, json=payload)
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"HTTP engine unavailable: {exc}") from exc

        if resp.status_code >= 400:
            raise HTTPException(status_code=500, detail={"message": "HTTP engine failed", "body": resp.text})

        if not output_file.exists():
            # Some backends might return a file URL or path instead.
            backend = resp.json() if "application/json" in resp.headers.get("content-type", "") else {}
            returned = backend.get("output_path") if isinstance(backend, dict) else None
            if returned:
                output_file = Path(returned)
            if not output_file.exists():
                raise HTTPException(status_code=500, detail="HTTP engine response succeeded but output file missing.")

        return {"mode": "http", "endpoint": engine.endpoint}

