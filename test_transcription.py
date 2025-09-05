#!/usr/bin/env python3
"""
Test script for Echo speech-to-text service.
This script tests the transcription functionality using the local server.
"""

import requests
import base64
import os
import sys
from pathlib import Path

# Add the Echo directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_health_check():
    """Test health check endpoint."""
    try:
        response = requests.get("http://localhost:8003/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_transcribe_file(audio_file_path):
    """Test transcription with an audio file."""
    if not os.path.exists(audio_file_path):
        print(f"Audio file not found: {audio_file_path}")
        return False
        
    try:
        with open(audio_file_path, 'rb') as f:
            files = {'file': (os.path.basename(audio_file_path), f, 'audio/wav')}
            response = requests.post(
                "http://localhost:8003/transcribe",
                files=files,
                data={'language': 'auto', 'model_size': 'base'}
            )
        
        print(f"Transcribe file: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Transcription: {result.get('text', 'No text')}")
            print(f"Language: {result.get('language', 'unknown')}")
            print(f"Confidence: {result.get('confidence', 0.0)}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Transcribe file failed: {e}")
        return False

def test_transcribe_base64():
    """Test transcription with base64 audio data."""
    # Create a simple test audio (silence) in base64
    # This is a minimal WAV file with silence
    base64_audio = "UklGRnoAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoAAAA="
    
    try:
        response = requests.post(
            "http://localhost:8003/transcribe/base64",
            json={"audio_data": base64_audio},
            params={'language': 'auto', 'model_size': 'base'}
        )
        
        print(f"Transcribe base64: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Transcription: {result.get('text', 'No text')}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"Transcribe base64 failed: {e}")
        return False

def test_mcp_endpoint():
    """Test MCP endpoint with a JSON-RPC call."""
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/list"
        }
        
        response = requests.post("http://localhost:8003/mcp", json=payload)
        print(f"MCP tools/list: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"MCP response: {result}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
    except Exception as e:
        print(f"MCP endpoint failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Echo speech-to-text service...")
    print("=" * 50)
    
    # Test health check first
    if not test_health_check():
        print("Health check failed. Make sure the server is running on port 8003.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Testing MCP endpoint...")
    test_mcp_endpoint()
    
    print("\n" + "=" * 50)
    print("Testing base64 transcription...")
    test_transcribe_base64()
    
    print("\n" + "=" * 50)
    print("Note: To test with actual audio files, use:")
    print("curl -X POST http://localhost:8003/transcribe \\")
    print("  -F \"file=@path/to/audio.wav\" \\")
    print("  -F \"language=en\" \\")
    print("  -F \"model_size=base\"")
    
    print("\nOr for base64:")
    print("curl -X POST http://localhost:8003/transcribe/base64 \\")
    print("  -H \"Content-Type: application/json\" \\")
    print("  -d '{\"audio_data\": \"<base64_data>\"}'")