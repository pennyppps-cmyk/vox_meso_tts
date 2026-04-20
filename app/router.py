from app.models import SynthesizeRequest


def resolve_engine(req: SynthesizeRequest) -> str:
    requested = (req.engine or "auto").strip().lower()
    if requested and requested != "auto":
        return requested

    language = (req.language or "").lower()
    is_malay = language in {"ms", "ms-my", "malay", "bahasa melayu", "bm"}
    if is_malay:
        return "mesolitica"

    if req.realtime:
        return "vibevoice"

    if req.premium or req.cloning:
        return "voxtral"

    return "kokoro"

