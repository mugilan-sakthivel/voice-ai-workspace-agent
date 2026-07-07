from pydantic import BaseModel


class TranscriptionResponse(BaseModel):
    text: str
    provider: str
    model: str
    is_final: bool = True


class TTSRequest(BaseModel):
    text: str


class TTSResponse(BaseModel):
    text: str
    provider: str
    model: str
    voice: str
    audio_url: str | None = None

