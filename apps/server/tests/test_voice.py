import asyncio
import base64
from io import BytesIO

import httpx
from fastapi import UploadFile

from app.core.config import Settings
from app.services.voice import VoiceService


class _FakeAudioResponse:
    def __init__(self, content: bytes | None = None, json_payload: dict | None = None) -> None:
        self.content = content
        self._json_payload = json_payload or {}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return self._json_payload


class _FakeAsyncClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post(self, url: str, *, headers: dict, json: dict) -> _FakeAudioResponse:
        assert url == "https://api.openai.com/v1/audio/speech"
        assert json["model"] == "gpt-4o-mini-tts"
        assert json["voice"] == "alloy"
        assert json["response_format"] == "mp3"
        return _FakeAudioResponse(content=b"\x00\x01")


class _FakeGroqAsyncClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post(self, url: str, *, headers: dict, files: dict, data: dict) -> _FakeAudioResponse:
        assert url == "https://api.groq.com/openai/v1/audio/transcriptions"
        assert headers["Authorization"] == "Bearer groq-key"
        assert data["model"] == "whisper-large-v3-turbo"
        assert data["response_format"] == "json"
        assert files["file"][0] == "voice.m4a"
        return _FakeAudioResponse(json_payload={"text": "Email Rahul and schedule a meeting."})


class _FakeGoogleTTSAsyncClient:
    def __init__(self, *args, **kwargs) -> None:
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def post(self, url: str, *, headers: dict, json: dict) -> _FakeAudioResponse:
        assert (
            url
            == "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent"
        )
        assert headers["x-goog-api-key"] == "google-key"
        assert json["model"] == "gemini-2.5-flash-preview-tts"
        assert json["generationConfig"]["speechConfig"]["voiceConfig"]["prebuiltVoiceConfig"]["voiceName"] == "Kore"
        encoded_pcm = base64.b64encode(b"\x00\x00\x01\x00").decode("ascii")
        return _FakeAudioResponse(
            json_payload={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "inlineData": {
                                        "data": encoded_pcm,
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        )


def test_openai_tts_returns_data_url(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)

    service = VoiceService(
        Settings(
            tts_provider="openai",
            tts_model="gpt-4o-mini-tts",
            tts_voice="alloy",
            openai_api_key="test-key",
        )
    )

    result = asyncio.run(service.synthesize("Hello from voice"))

    assert result["provider"] == "openai"
    assert result["audio_url"] == "data:audio/mp3;base64,AAE="


def test_transcribe_fallback_returns_empty_text() -> None:
    service = VoiceService(
        Settings(
            stt_provider="groq",
            stt_model="whisper-large-v3-turbo",
            groq_api_key="",
        )
    )

    upload = UploadFile(filename="voice.m4a", file=BytesIO(b"voice-bytes"))
    result = asyncio.run(service.transcribe(upload))

    assert result["text"] == ""
    assert result["provider"] == "groq"
    assert result["model"] == "whisper-large-v3-turbo"


def test_groq_transcription_returns_text(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _FakeGroqAsyncClient)

    service = VoiceService(
        Settings(
            stt_provider="groq",
            stt_model="whisper-large-v3-turbo",
            groq_api_key="groq-key",
        )
    )

    upload = UploadFile(filename="voice.m4a", file=BytesIO(b"voice-bytes"))
    result = asyncio.run(service.transcribe(upload))

    assert result["text"] == "Email Rahul and schedule a meeting."
    assert result["provider"] == "groq"
    assert result["model"] == "whisper-large-v3-turbo"


def test_google_tts_returns_wav_data_url(monkeypatch) -> None:
    monkeypatch.setattr(httpx, "AsyncClient", _FakeGoogleTTSAsyncClient)

    service = VoiceService(
        Settings(
            tts_provider="google",
            tts_model="gemini-2.5-flash-preview-tts",
            tts_voice="Kore",
            google_api_key="google-key",
        )
    )

    result = asyncio.run(service.synthesize("Have a great day"))

    assert result["provider"] == "google"
    assert result["voice"] == "Kore"
    assert result["audio_url"].startswith("data:audio/wav;base64,")
