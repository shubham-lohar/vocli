"""Voice Activity Detection wrapper around webrtcvad."""

import webrtcvad

from vocli import config as cfg


class VoiceActivityDetector:
    """Detect speech in audio frames using WebRTC VAD."""

    def __init__(
        self,
        aggressiveness: int | None = None,
        sample_rate: int | None = None,
    ):
        self.sample_rate = sample_rate or cfg.SAMPLE_RATE
        self.vad = webrtcvad.Vad(aggressiveness or cfg.VAD_AGGRESSIVENESS)

    def is_speech(self, frame: bytes) -> bool:
        """Check if a 30ms audio frame contains speech.

        Args:
            frame: Raw 16-bit PCM audio, 30ms at the configured sample rate.
                   At 16kHz: 960 bytes (480 samples x 2 bytes).
        """
        return self.vad.is_speech(frame, self.sample_rate)

    @property
    def frame_size(self) -> int:
        """Number of bytes in a 30ms frame (16-bit PCM)."""
        return int(self.sample_rate * 0.03) * 2
