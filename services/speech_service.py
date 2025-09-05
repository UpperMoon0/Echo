import whisper
import base64
import tempfile
import os
from typing import Dict, Optional
import numpy as np
from core.config import DEFAULT_WHISPER_MODEL, MAX_AUDIO_LENGTH, SUPPORTED_AUDIO_FORMATS

class SpeechToTextService:
    def __init__(self):
        self.models = {}
        self.default_model = DEFAULT_WHISPER_MODEL
        
    def load_model(self, model_size: str = None) -> whisper.Whisper:
        """Load a Whisper model of specified size."""
        if model_size is None:
            model_size = self.default_model
            
        if model_size not in self.models:
            print(f"Loading Whisper model: {model_size}")
            self.models[model_size] = whisper.load_model(model_size)
            
        return self.models[model_size]
    
    def transcribe_audio(self, audio_data: bytes, model_size: str = None, language: str = None) -> Dict:
        """Transcribe audio data to text using Whisper."""
        try:
            # Load the appropriate model
            model = self.load_model(model_size)
            
            # Save audio to temporary file for processing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_audio_path = temp_audio.name
            
            try:
                # Transcribe the audio
                result = model.transcribe(
                    temp_audio_path,
                    language=language if language != 'auto' else None,
                    fp16=False  # Use FP32 for compatibility
                )
                
                return {
                    "text": result["text"],
                    "language": result.get("language", "unknown"),
                    "confidence": result.get("confidence", 1.0)
                }
            finally:
                # Clean up temporary file
                os.unlink(temp_audio_path)
                
        except Exception as e:
            return {
                "error": f"Transcription failed: {str(e)}",
                "text": "",
                "language": "unknown",
                "confidence": 0.0
            }
    
    def transcribe_base64_audio(self, base64_data: str, model_size: str = None, language: str = None) -> Dict:
        """Transcribe base64 encoded audio data to text."""
        try:
            # Decode base64 audio data
            audio_bytes = base64.b64decode(base64_data)
            return self.transcribe_audio(audio_bytes, model_size, language)
        except Exception as e:
            return {
                "error": f"Base64 decoding failed: {str(e)}",
                "text": "",
                "language": "unknown",
                "confidence": 0.0
            }

# Global service instance
speech_service = SpeechToTextService()