"""Async HTTP clients for STT and TTS servers."""

import httpx

from vocli import config as cfg


async def check_stt_health() -> tuple[bool, str]:
    """Check if the STT server is healthy."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{cfg.STT_URL}/health")
            if resp.status_code == 200:
                return True, resp.text
            return False, f"status {resp.status_code}"
    except Exception as e:
        return False, str(e)


async def check_tts_health() -> tuple[bool, str]:
    """Check if the TTS server is healthy."""
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{cfg.TTS_URL}/health")
            if resp.status_code == 200:
                return True, resp.text
            return False, f"status {resp.status_code}"
    except Exception as e:
        return False, str(e)


async def transcribe(audio_bytes: bytes, language: str | None = None) -> str:
    """Send audio to the STT server and return transcribed text.

    Args:
        audio_bytes: WAV audio data.
        language: Language code (default from config).

    Returns:
        Transcribed text string.
    """
    lang = language or cfg.WHISPER_LANGUAGE
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{cfg.STT_URL}/v1/audio/transcriptions",
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data={"model": "whisper-1", "language": lang, "response_format": "json"},
        )
        resp.raise_for_status()
        return resp.json()["text"]


async def synthesize(text: str, voice: str | None = None, speed: float | None = None) -> bytes:
    """Send text to the TTS server and return WAV audio bytes.

    Args:
        text: Text to synthesize.
        voice: Voice name (default from config).
        speed: Speech speed (default from config).

    Returns:
        WAV audio bytes.
    """
    voice = voice or cfg.TTS_VOICE
    speed = speed or cfg.TTS_SPEED
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{cfg.TTS_URL}/v1/audio/speech",
            json={"input": text, "model": "tts-1", "voice": voice, "speed": speed},
        )
        resp.raise_for_status()
        return resp.content
