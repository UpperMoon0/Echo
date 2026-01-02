from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import base64
from typing import Dict, Optional
from core.config import SPEECH_TO_TEXT_TOOL_SCHEMA, DEFAULT_WHISPER_MODEL
from services.speech_service import speech_service
from services.streaming_service import streaming_service, StreamingSpeechToTextService
from datetime import datetime
import io
import asyncio
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("echo-api")

router = APIRouter()

# In-memory dictionary to store streaming service instances for each client
streaming_sessions: Dict[str, StreamingSpeechToTextService] = {}

async def handle_json_rpc_message(message: dict) -> dict:
    """Handle a single JSON-RPC message for embedded MCP."""
    try:
        method = message.get('method')
        params = message.get('params', {})
        msg_id = message.get('id')

        if method == 'initialize':
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'result': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {
                        'tools': {}
                    },
                    'serverInfo': {
                        'name': 'echo-mcp',
                        'version': '1.0.0'
                    }
                }
            }

        elif method == 'tools/list':
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'result': {
                    'tools': [SPEECH_TO_TEXT_TOOL_SCHEMA]
                }
            }

        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_args = params.get('arguments', {})

            if tool_name == 'speech_to_text':
                audio_data = tool_args.get('audio_data')
                language = tool_args.get('language', 'auto')
                model_size = tool_args.get('model_size', 'base')

                if not audio_data:
                    raise ValueError("audio_data parameter is required")

                result = speech_service.transcribe_base64_audio(audio_data, model_size, language)
                
                if "error" in result:
                    raise ValueError(result["error"])

                return {
                    'jsonrpc': '2.0',
                    'id': msg_id,
                    'result': {
                        'content': [
                            {
                                'type': 'text',
                                'text': json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        else:
            return {
                'jsonrpc': '2.0',
                'id': msg_id,
                'error': {
                    'code': -32601,
                    'message': f'Method not found: {method}'
                }
            }

    except Exception as e:
        return {
            'jsonrpc': '2.0',
            'id': message.get('id'),
            'error': {
                'code': -32603,
                'message': str(e)
            }
        }

@router.post("/v1/mcp")
async def embedded_mcp_endpoint(request: Request):
    """Embedded MCP endpoint that handles JSON-RPC messages over HTTP."""
    try:
        json_data = await request.json()

        # Check if this is a JSON-RPC message
        if 'jsonrpc' in json_data and 'method' in json_data:
            response = await handle_json_rpc_message(json_data)
            return response
        else:
            raise HTTPException(status_code=400, detail="Not a valid JSON-RPC message")

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/v1/audio/transcriptions")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    model_size: str = Form("base")
):
    """Transcribe audio file to text."""
    if not file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio format")

    try:
        audio_data = await file.read()
        result = speech_service.transcribe_audio(audio_data, model_size, language)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.post("/v1/audio/transcriptions/base64")
async def transcribe_base64_audio(
    request: Request,
    language: str = Form("auto"),
    model_size: str = Form("base")
):
    """Transcribe base64 encoded audio data to text."""
    try:
        data = await request.json()
        audio_data = data.get("audio_data")
        
        if not audio_data:
            raise HTTPException(status_code=400, detail="audio_data field is required")
            
        result = speech_service.transcribe_base64_audio(audio_data, model_size, language)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@router.get("/health")
@router.head("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Echo",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """WebSocket endpoint for real-time audio streaming transcription with silence detection."""
    await websocket.accept()
    try:
        while True:
            try:
                # Receive audio data as bytes with timeout to allow silence checking
                data = await asyncio.wait_for(websocket.receive_bytes(), timeout=0.1)
                logger.info(f"DEBUG: Echo received {len(data)} bytes from WebSocket")
                streaming_service.add_audio_chunk(data)
            except asyncio.TimeoutError:
                # No data received, just check for silence events
                pass

            # Check for silence-based transcription events
            event = streaming_service.check_silence_events()
            if event:
                # Send event as JSON with type and text
                await websocket.send_json(event)

    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))

@router.post("/stream/start")
async def start_streaming_session(language: str = Form("auto")):
    """Start a new streaming session and clear any previous buffer."""
    streaming_service.clear_buffer()
    return {"status": "started", "language": language}

@router.post("/stream/chunk")
async def add_stream_chunk(file: UploadFile = File(...)):
    """Add an audio chunk to the streaming buffer."""
    audio_data = await file.read()
    streaming_service.add_audio_chunk(audio_data)
    return {"status": "chunk_added", "size": len(audio_data)}

@router.post("/stream/transcribe")
async def transcribe_stream(language: str = Form("auto")):
    """Transcribe the current streaming buffer."""
    transcription = streaming_service.transcribe_stream(language)
    return {"text": transcription}

@router.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Echo API 🎤→📝",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "POST /v1/audio/transcriptions": "Transcribe audio file",
            "POST /v1/audio/transcriptions/base64": "Transcribe base64 audio data",
            "POST /v1/mcp": "Embedded MCP endpoint",
            "WS /ws/transcribe": "WebSocket for real-time streaming",
            "POST /stream/start": "Start streaming session",
            "POST /stream/chunk": "Add audio chunk to stream",
            "POST /stream/transcribe": "Transcribe current stream buffer"
        },
        "features": [
            "Speech-to-text using OpenAI Whisper",
            "Completely local and free",
            "Multiple audio format support",
            "MCP (Model Context Protocol) support",
            "Real-time audio streaming capable",
            "WebSocket support for live transcription"
        ],
        "health_endpoint": "/health"
    }