import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Shared tool schema definition for speech-to-text
SPEECH_TO_TEXT_TOOL_SCHEMA = {
    'name': 'speech_to_text',
    'description': 'Description: Convert speech audio to text using Whisper. Strength: Accurate transcription, supports multiple languages, works offline. Weakness: Requires audio input, may have latency for long audio. Best practice: Provide clear audio for best results.',
    'inputSchema': {
        'type': 'object',
        'properties': {
            'audio_data': {
                'type': 'string',
                'description': 'Base64 encoded audio data or URL to audio file',
                'format': 'byte'
            },
            'language': {
                'type': 'string',
                'description': 'Language code for transcription (e.g., en, fr, es). Auto-detect if not specified',
                'default': 'auto'
            },
            'model_size': {
                'type': 'string',
                'description': 'Whisper model size: tiny, base, small, medium, large',
                'enum': ['tiny', 'base', 'small', 'medium', 'large'],
                'default': 'base'
            }
        },
        'required': ['audio_data']
    }
}

# Configuration constants
DEFAULT_WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
MAX_AUDIO_LENGTH = int(os.getenv("MAX_AUDIO_LENGTH", "30"))  # seconds
SUPPORTED_AUDIO_FORMATS = ["wav", "mp3", "m4a", "flac"]