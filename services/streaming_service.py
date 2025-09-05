import whisper
import numpy as np
import io
import tempfile
import os
from typing import Generator, Optional
from core.config import DEFAULT_WHISPER_MODEL

class StreamingSpeechToTextService:
    def __init__(self):
        self.model = whisper.load_model(DEFAULT_WHISPER_MODEL)
        self.audio_buffer = np.array([], dtype=np.float32)
        self.sample_rate = 16000  # Whisper expects 16kHz audio
        
    def add_audio_chunk(self, audio_data: bytes) -> None:
        """Add an audio chunk to the buffer for streaming transcription."""
        # Convert bytes to numpy array (assuming 16-bit PCM, mono)
        audio_array = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        self.audio_buffer = np.concatenate([self.audio_buffer, audio_array])
        
    def transcribe_stream(self, language: Optional[str] = None) -> str:
        """Transcribe the current audio buffer and clear it."""
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
        """Clear the audio buffer."""
        self.audio_buffer = np.array([], dtype=np.float32)

# Global streaming service instance
streaming_service = StreamingSpeechToTextService()