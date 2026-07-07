from fastapi import APIRouter, Depends, File, UploadFile

from app.api.dependencies import get_voice_service
from app.schemas.voice import TTSRequest, TTSResponse, TranscriptionResponse
from app.services.voice import VoiceService


router = APIRouter(tags=["voice"])


@router.post("/voice/stt", response_model=TranscriptionResponse)
async def speech_to_text(
    file: UploadFile = File(...),
    voice_service: VoiceService = Depends(get_voice_service),
) -> TranscriptionResponse:
    return TranscriptionResponse(**await voice_service.transcribe(file))


@router.post("/voice/tts", response_model=TTSResponse)
async def text_to_speech(
    payload: TTSRequest,
    voice_service: VoiceService = Depends(get_voice_service),
) -> TTSResponse:
    return TTSResponse(**await voice_service.synthesize(payload.text))

