"""Audio recording, playback, and chime generation."""

import asyncio
import io
import time

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from vocli import config as cfg


def _get_output_device():
    """Get configured output device, or None for default."""
    conf = cfg.get_config()
    device = conf.get("output_device")
    if device and device != "default":
        return device
    return None


def _get_input_device():
    """Get configured input device, or None for default."""
    conf = cfg.get_config()
    device = conf.get("input_device")
    if device and device != "default":
        return device
    return None


async def play_audio(wav_bytes: bytes) -> None:
    """Play WAV audio through the configured output device."""

    def _play():
        buf = io.BytesIO(wav_bytes)
        sample_rate, data = wavfile.read(buf)
        # Normalize to float32 for sounddevice
        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            data = data.astype(np.float32) / 2147483648.0
        sd.play(data, samplerate=sample_rate, device=_get_output_device())
        sd.wait()

    await asyncio.to_thread(_play)


async def play_chime() -> None:
    """Play a short chime to signal 'start speaking'."""

    def _chime():
        duration = 0.15  # seconds
        freq = 880  # Hz (A5)
        t = np.linspace(0, duration, int(cfg.SAMPLE_RATE * duration), endpoint=False)
        # Sine wave with fade in/out
        wave = np.sin(2 * np.pi * freq * t).astype(np.float32)
        fade_len = int(cfg.SAMPLE_RATE * 0.02)
        wave[:fade_len] *= np.linspace(0, 1, fade_len)
        wave[-fade_len:] *= np.linspace(1, 0, fade_len)
        wave *= 0.3  # Low volume
        sd.play(wave, samplerate=cfg.SAMPLE_RATE, device=_get_output_device())
        sd.wait()

    await asyncio.to_thread(_chime)


async def record_audio(
    max_duration: float | None = None,
    use_vad: bool = True,
) -> bytes:
    """Record audio from the microphone.

    Uses VAD to detect when the user stops speaking.

    Args:
        max_duration: Maximum recording duration in seconds.
        use_vad: Whether to use voice activity detection for auto-stop.

    Returns:
        WAV audio bytes (16kHz, mono, 16-bit PCM).
    """

    def _record():
        from vocli.vad import VoiceActivityDetector

        max_dur = max_duration or cfg.MAX_RECORDING_DURATION
        sample_rate = cfg.SAMPLE_RATE
        frame_duration_ms = 30
        frame_samples = int(sample_rate * frame_duration_ms / 1000)
        frame_bytes = frame_samples * 2  # 16-bit

        vad = VoiceActivityDetector() if use_vad else None
        frames = []
        silent_ms = 0
        speech_detected = False
        start_time = time.time()

        def callback(indata, frame_count, time_info, status):
            frames.append(indata.copy())

        with sd.InputStream(
            samplerate=sample_rate,
            channels=cfg.CHANNELS,
            dtype="int16",
            blocksize=frame_samples,
            callback=callback,
            device=_get_input_device(),
        ):
            while (time.time() - start_time) < max_dur:
                time.sleep(frame_duration_ms / 1000)

                if not use_vad or vad is None:
                    continue

                # Check VAD on the latest frame
                if len(frames) == 0:
                    continue

                latest = frames[-1]
                raw = latest.tobytes()
                # Ensure frame is exactly the right size
                if len(raw) < frame_bytes:
                    continue

                chunk = raw[:frame_bytes]
                if vad.is_speech(chunk):
                    speech_detected = True
                    silent_ms = 0
                else:
                    silent_ms += frame_duration_ms

                # Stop after sustained silence, but only if we heard speech first
                if speech_detected and silent_ms >= cfg.SILENCE_THRESHOLD_MS:
                    break

                # Minimum recording duration
                elapsed = time.time() - start_time
                if elapsed < cfg.MIN_RECORDING_DURATION:
                    continue

        # Combine all frames into WAV
        if not frames:
            return b""

        audio_data = np.concatenate(frames, axis=0)
        buf = io.BytesIO()
        wavfile.write(buf, sample_rate, audio_data)
        return buf.getvalue()

    return await asyncio.to_thread(_record)
