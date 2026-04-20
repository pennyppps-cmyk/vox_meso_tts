import os
import time
import uuid
from dataclasses import dataclass
from typing import Dict, Optional

import httpx
from redis import Redis


@dataclass(frozen=True)
class Provider:
    name: str
    url: str
    timeout_seconds: int = 120


class VoxtralConcurrencyGate:
    def __init__(self, redis_client: Redis, max_slots: int, key: str = "tts:voxtral:slots"):
        self.redis = redis_client
        self.max_slots = max_slots
        self.key = key

    def acquire(self, request_id: str, wait_timeout: float = 20.0) -> bool:
        deadline = time.time() + wait_timeout
        while time.time() < deadline:
            with self.redis.pipeline() as pipe:
                try:
                    pipe.watch(self.key)
                    current = pipe.scard(self.key)
                    if current < self.max_slots:
                        pipe.multi()
                        pipe.sadd(self.key, request_id)
                        pipe.expire(self.key, 60)
                        pipe.execute()
                        return True
                    pipe.unwatch()
                except Exception:
                    pass
            time.sleep(0.08)
        return False

    def release(self, request_id: str) -> None:
        try:
            self.redis.srem(self.key, request_id)
        except Exception:
            # Do not fail request completion due to cleanup errors.
            pass


class TTSRouter:
    def __init__(self) -> None:
        self.providers: Dict[str, Provider] = {
            "mesolitica": Provider("mesolitica", os.getenv("MESOLITICA_URL", "http://localhost:5001/v1/audio/speech")),
            "kokoro": Provider("kokoro", os.getenv("KOKORO_URL", "http://localhost:5002/v1/audio/speech")),
            "vibevoice": Provider("vibevoice", os.getenv("VIBEVOICE_URL", "http://localhost:5003/v1/audio/speech")),
            "voxtral": Provider("voxtral", os.getenv("VOXTRAL_URL", "http://localhost:5004/v1/audio/speech")),
        }
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.voxtral_gate = VoxtralConcurrencyGate(
            redis_client=self.redis,
            max_slots=int(os.getenv("VOXTRAL_MAX_CONCURRENCY", "3")),
        )

    def pick_provider(
        self,
        language: Optional[str],
        realtime: bool,
        premium: bool,
        cloning: bool,
        engine: Optional[str],
    ) -> Provider:
        if engine:
            selected = engine.strip().lower()
            if selected in self.providers:
                return self.providers[selected]

        lang = (language or "").strip().lower()
        if lang in {"ms", "ms-my", "malay", "bahasa melayu", "bm"}:
            return self.providers["mesolitica"]
        if realtime:
            return self.providers["vibevoice"]
        if premium or cloning:
            return self.providers["voxtral"]
        return self.providers["kokoro"]

    def synthesize(
        self,
        text: str,
        voice: Optional[str],
        language: Optional[str],
        response_format: str,
        speed: float,
        realtime: bool,
        premium: bool,
        cloning: bool,
        engine: Optional[str],
    ) -> tuple[bytes, str, str]:
        provider = self.pick_provider(language, realtime, premium, cloning, engine)
        payload = {
            "model": provider.name,
            "input": text,
            "voice": voice or "default",
            "response_format": response_format,
            "speed": speed,
        }

        token = None
        if provider.name == "voxtral":
            token = uuid.uuid4().hex
            if not self.voxtral_gate.acquire(token):
                raise RuntimeError("Voxtral queue busy (max concurrency reached).")

        try:
            with httpx.Client(timeout=provider.timeout_seconds) as client:
                response = client.post(provider.url, json=payload)
        finally:
            if token:
                self.voxtral_gate.release(token)

        if response.status_code >= 400:
            raise RuntimeError(f"{provider.name} returned {response.status_code}: {response.text}")

        return response.content, response.headers.get("content-type", "audio/wav"), provider.name

