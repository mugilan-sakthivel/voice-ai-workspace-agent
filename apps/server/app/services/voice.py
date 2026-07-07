import base64
import io
import wave

from fastapi import UploadFile

from app.core.config import Settings


class VoiceService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def transcribe(self, audio: UploadFile) -> dict:
        if self.settings.stt_provider == "openai" and self.settings.openai_api_key:
            return await self._transcribe_openai(audio)
        if self.settings.stt_provider == "groq" and self.settings.groq_api_key:
            return await self._transcribe_groq(audio)
        return {
            "text": "",
            "provider": self.settings.stt_provider,
            "model": self.settings.stt_model,
            "is_final": True,
        }

    async def synthesize(self, text: str) -> dict:
        if self.settings.tts_provider == "openai" and self.settings.openai_api_key:
            return await self._synthesize_openai(text)
        if self.settings.tts_provider == "google" and self.settings.google_api_key:
            return await self._synthesize_google(text)
        return {
            "text": text,
            "provider": self.settings.tts_provider,
            "model": self.settings.tts_model,
            "voice": self.settings.tts_voice,
            "audio_url": None,
        }

    async def _transcribe_openai(self, audio: UploadFile) -> dict:
        import httpx

        content = await audio.read()
        files = {"file": (audio.filename or "audio.wav", content, audio.content_type or "audio/wav")}
        data = {"model": self.settings.stt_model}

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.settings.openai_api_key}"},
                files=files,
                data=data,
            )
            response.raise_for_status()
            payload = response.json()

        return {
            "text": payload.get("text", ""),
            "provider": "openai",
            "model": self.settings.stt_model,
            "is_final": True,
        }

    async def _transcribe_groq(self, audio: UploadFile) -> dict:
        import httpx

        content = await audio.read()
        files = {"file": (audio.filename or "audio.wav", content, audio.content_type or "audio/wav")}
        data = {
            "model": self.settings.stt_model,
            "response_format": "json",
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.settings.groq_api_key}"},
                files=files,
                data=data,
            )
            response.raise_for_status()
            payload = response.json()

        return {
            "text": payload.get("text", ""),
            "provider": "groq",
            "model": self.settings.stt_model,
            "is_final": True,
        }

    async def _synthesize_openai(self, text: str) -> dict:
        import httpx

        response_format = "mp3"

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                "https://api.openai.com/v1/audio/speech",
                headers={
                    "Authorization": f"Bearer {self.settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.settings.tts_model,
                    "input": text,
                    "voice": self.settings.tts_voice,
                    "response_format": response_format,
                },
            )
            response.raise_for_status()

        encoded_audio = base64.b64encode(response.content).decode("ascii")
        return {
            "text": text,
            "provider": "openai",
            "model": self.settings.tts_model,
            "voice": self.settings.tts_voice,
            "audio_url": f"data:audio/{response_format};base64,{encoded_audio}",
        }

    async def _synthesize_google(self, text: str) -> dict:
        import httpx

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{self.settings.tts_model}:generateContent",
                headers={
                    "x-goog-api-key": self.settings.google_api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": text,
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "responseModalities": ["AUDIO"],
                        "speechConfig": {
                            "voiceConfig": {
                                "prebuiltVoiceConfig": {
                                    "voiceName": self.settings.tts_voice,
                                }
                            }
                        },
                    },
                    "model": self.settings.tts_model,
                },
            )
            response.raise_for_status()
            payload = response.json()

        encoded_pcm = (
            payload.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("inlineData", {})
            .get("data", "")
        )
        pcm_bytes = base64.b64decode(encoded_pcm) if encoded_pcm else b""
        wav_bytes = self._pcm_to_wav(pcm_bytes)
        encoded_audio = base64.b64encode(wav_bytes).decode("ascii")

        return {
            "text": text,
            "provider": "google",
            "model": self.settings.tts_model,
            "voice": self.settings.tts_voice,
            "audio_url": f"data:audio/wav;base64,{encoded_audio}",
        }

    def _pcm_to_wav(self, pcm_bytes: bytes) -> bytes:
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            wav_file.writeframes(pcm_bytes)
        return buffer.getvalue()
