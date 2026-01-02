import whisper
import numpy as np
import io
import tempfile
import os
import time
from typing import Generator, Optional, Dict, Any
from core.config import (
    DEFAULT_WHISPER_MODEL,
    SILENCE_SHORT_DURATION,
    SILENCE_LONG_DURATION,
    SILENCE_THRESHOLD
)
import logging

logger = logging.getLogger("echo-streaming")
logging.basicConfig(level=logging.INFO)

class StreamingSpeechToTextService:
    def __init__(self, client_id: str = "default"):
        self.client_id = client_id
        self.model = whisper.load_model(DEFAULT_WHISPER_MODEL)
        self.audio_buffer = np.array([], dtype=np.float32)
        self.sample_rate = 16000  # Whisper expects 16kHz audio

        # Silence detection state
        self.last_audio_time = time.time()
        self.silence_start_time = None
        self.last_interim_transcription = ""
        self.final_transcription_sent = False

    def add_audio_chunk(self, audio_data: bytes) -> None:
        """Add an audio chunk to the buffer for streaming transcription."""
        # Convert bytes to numpy array (assuming 16-bit PCM, mono)
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Calculate RMS level for silence detection
        rms = np.sqrt(np.mean(audio_array ** 2)) if len(audio_array) > 0 else 0.0

        current_time = time.time()
        # print(f"DEBUG: Processing chunk size={len(audio_array)}, rms={rms:.4f}")

        # Check if this chunk contains audio (above silence threshold)
        if rms > SILENCE_THRESHOLD:
            # Audio detected - reset silence tracking
            if self.silence_start_time is not None:
                print(f"DEBUG: Speech detected! (RMS={rms:.4f}). Resetting silence tracking.")
            self.last_audio_time = current_time
            self.silence_start_time = None
            self.final_transcription_sent = False
        else:
            # Silence detected
            if self.silence_start_time is None:
                self.silence_start_time = current_time
                print(f"DEBUG: Silence started at {self.silence_start_time}")

        # Add to buffer
        self.audio_buffer = np.concatenate([self.audio_buffer, audio_array])

    def check_silence_events(self) -> Optional[Dict[str, Any]]:
        """Check for silence-based transcription events.

        Returns:
            Dict with 'type' ('interim' or 'final') and 'text', or None if no event
        """
        if self.silence_start_time is None:
            return None

        current_time = time.time()
        silence_duration = current_time - self.silence_start_time

        # Check for interim transcription (short pause)
        if (silence_duration >= SILENCE_SHORT_DURATION and
            not self.final_transcription_sent and
            len(self.audio_buffer) > 0):

            # Transcribe current buffer for interim result
            logger.info(f"DEBUG: Triggering interim transcription. Buffer size: {len(self.audio_buffer)}")
            interim_text = self._transcribe_current_buffer()
            logger.info(f"DEBUG: Interim transcription result: '{interim_text}'")
            if interim_text and interim_text != self.last_interim_transcription:
                self.last_interim_transcription = interim_text
                return {
                    'type': 'interim',
                    'text': interim_text.strip(),
                    'client_id': self.client_id
                }

        # Check for final transcription (long pause)
        if (silence_duration >= SILENCE_LONG_DURATION and
            not self.final_transcription_sent and
            len(self.audio_buffer) > 0):

            # Transcribe and clear buffer for final result
            logger.info(f"DEBUG: Triggering final transcription. Buffer size: {len(self.audio_buffer)}")
            final_text = self._transcribe_and_clear_buffer()
            logger.info(f"DEBUG: Final transcription result: '{final_text}'")
            if final_text:
                self.final_transcription_sent = True
                self.last_interim_transcription = ""
                return {
                    'type': 'final',
                    'text': final_text.strip(),
                    'client_id': self.client_id
                }

        return None

    def _transcribe_current_buffer(self) -> str:
        """Transcribe the current audio buffer without clearing it."""
        if len(self.audio_buffer) == 0:
            return ""

        # Save buffer to temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            # Convert to 16kHz if needed (Whisper expects 16kHz)
            if self.sample_rate != 16000:
                import librosa
                audio_resampled = librosa.resample(
                    self.audio_buffer,
                    orig_sr=self.sample_rate,
                    target_sr=16000
                )
            else:
                audio_resampled = self.audio_buffer

            # Save as WAV file
            import scipy.io.wavfile as wav
            wav.write(temp_audio.name, 16000, (audio_resampled * 32767).astype(np.int16))
            temp_audio_path = temp_audio.name

        try:
            # Transcribe the audio
            result = self.model.transcribe(
                temp_audio_path,
                language=None,  # Auto-detect
                fp16=False
            )

            return result["text"]
        finally:
            # Clean up temporary file
            os.unlink(temp_audio_path)

    def _transcribe_and_clear_buffer(self) -> str:
        """Transcribe the current audio buffer and clear it."""
        text = self._transcribe_current_buffer()
        self.audio_buffer = np.array([], dtype=np.float32)
        return text

    def transcribe_stream(self, language: Optional[str] = None) -> str:
        """Legacy method for backward compatibility - transcribe and clear buffer."""
        if len(self.audio_buffer) == 0:
            return ""

        # Save buffer to temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
            # Convert to 16kHz if needed (Whisper expects 16kHz)
            if self.sample_rate != 16000:
                import librosa
                audio_resampled = librosa.resample(
                    self.audio_buffer,
                    orig_sr=self.sample_rate,
                    target_sr=16000
                )
            else:
                audio_resampled = self.audio_buffer

            # Save as WAV file
            import scipy.io.wavfile as wav
            wav.write(temp_audio.name, 16000, (audio_resampled * 32767).astype(np.int16))
            temp_audio_path = temp_audio.name

        try:
            # Transcribe the audio
            result = self.model.transcribe(
                temp_audio_path,
                language=language if language != 'auto' else None,
                fp16=False
            )

            # Clear the buffer after successful transcription
            self.audio_buffer = np.array([], dtype=np.float32)

            return result["text"]
        finally:
            # Clean up temporary file
            os.unlink(temp_audio_path)

    def clear_buffer(self) -> None:
        """Clear the audio buffer and reset silence detection state."""
        self.audio_buffer = np.array([], dtype=np.float32)
        self.last_audio_time = time.time()
        self.silence_start_time = None
        self.last_interim_transcription = ""
        self.final_transcription_sent = False

# Global streaming service instance
streaming_service = StreamingSpeechToTextService()