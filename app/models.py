from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


EngineType = Literal["command", "http"]


class VoiceInfo(BaseModel):
    id: str
    language: Optional[str] = None
    description: Optional[str] = None


class EngineConfig(BaseModel):
    type: EngineType
    enabled: bool = True
    description: str = ""
    command_template: Optional[str] = None
    endpoint: Optional[str] = None
    timeout_seconds: int = 120
    extra_env: Dict[str, str] = Field(default_factory=dict)
    default_options: Dict[str, Any] = Field(default_factory=dict)
    voices: List[VoiceInfo] = Field(default_factory=list)


class AppConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 3000
    output_dir: str = "./outputs"
    base_url: str = "http://localhost:3000"
    engines: Dict[str, EngineConfig]


class SynthesizeRequest(BaseModel):
    text: str = Field(min_length=1)
    engine: str
    voice: Optional[str] = None
    language: Optional[str] = None
    options: Dict[str, Any] = Field(default_factory=dict)
    output_format: Literal["wav", "mp3", "ogg"] = "wav"


class SynthesizeResponse(BaseModel):
    engine: str
    voice: Optional[str]
    language: Optional[str]
    output_path: str
    output_url: str
    duration_seconds: Optional[float] = None
    meta: Dict[str, Any] = Field(default_factory=dict)

