# Echo

A high-performance, local speech-to-text service using OpenAI's Whisper model, built with FastAPI. Supports REST API, WebSocket streaming, and MCP (Model Context Protocol) integration.

## Features

- **Local Processing**: Completely offline speech-to-text using Whisper models
- **Multiple Interfaces**: REST API, WebSocket for real-time streaming, and MCP for AI assistant integration
- **Multi-format Support**: WAV, MP3, M4A, FLAC audio files
- **Multi-language**: Auto-detection or manual language specification
- **Real-time Streaming**: Silence-based transcription with interim and final results
- **Docker Ready**: Easy containerized deployment

## Quick Start

### Using Docker (Recommended)

```bash
cd Echo
docker build -t echo-stt .
docker run -p 8000:8000 echo-stt
```

### Local Development

```bash
cd Echo
pip install -r requirements.txt
python main.py
```

The service will be available at `http://localhost:8000`.

## API Usage

### REST Endpoints

#### Transcribe Audio File
```bash
curl -X POST "http://localhost:8000/v1/audio/transcriptions" \
  -F "file=@audio.wav" \
  -F "language=en" \
  -F "model_size=base"
```

#### Transcribe Base64 Audio
```bash
curl -X POST "http://localhost:8000/v1/audio/transcriptions/base64" \
  -H "Content-Type: application/json" \
  -d '{"audio_data": "base64_string", "language": "en"}'
```

#### Health Check
```bash
curl http://localhost:8000/health
```

### WebSocket Streaming

Connect to `ws://localhost:8000/ws/transcribe` and send audio chunks as bytes. Receive JSON events:
- `{"type": "interim", "text": "..."}` - During short pauses
- `{"type": "final", "text": "..."}` - After longer pauses

### MCP Integration

The service exposes a `speech_to_text` tool via the `/v1/mcp` endpoint for JSON-RPC communication with AI assistants.

## Configuration

Configure via environment variables:

- `WHISPER_MODEL`: Model size (tiny/base/small/medium/large) - default: base
- `MAX_AUDIO_LENGTH`: Maximum audio length in seconds - default: 30
- `SILENCE_SHORT_DURATION`: Seconds for interim transcription - default: 0.7
- `SILENCE_LONG_DURATION`: Seconds for final transcription - default: 1.5
- `SILENCE_THRESHOLD`: RMS threshold for silence - default: 0.01
- `PORT`: Server port - default: 8000

## Architecture

- **main.py**: FastAPI application entry point
- **api/routes.py**: API endpoint definitions
- **services/speech_service.py**: Core Whisper transcription service
- **services/streaming_service.py**: Real-time audio streaming with silence detection
- **core/config.py**: Configuration and MCP tool schema

## Dependencies

- openai-whisper
- torch/torchaudio
- fastapi/uvicorn
- numpy/scipy/librosa

## License

MIT License