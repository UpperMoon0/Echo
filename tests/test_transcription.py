#!/usr/bin/env python3
"""
Pytest-based tests for Echo speech-to-text service.
These tests require the server to be running on localhost:8003.
"""

import pytest
import requests
import os
from pathlib import Path

# Base URL for the service
BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def check_server_running():
    """Ensure the server is running before tests."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, "Server health check failed"
    except Exception as e:
        pytest.fail(f"Server not running or accessible: {e}")

def test_health_check():
    """Test health check endpoint."""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data

def test_transcribe_hello_world():
    """Test transcription of hello_world.mp3 expecting 'hello world' output."""
    audio_file_path = Path(__file__).parent / "hello_world.mp3"
    assert audio_file_path.exists(), f"Test audio file not found: {audio_file_path}"

    with open(audio_file_path, 'rb') as f:
        files = {'file': ('hello_world.mp3', f, 'audio/mp3')}
        response = requests.post(
            f"{BASE_URL}/transcribe",
            files=files,
            data={'language': 'auto', 'model_size': 'base'}
        )

    assert response.status_code == 200, f"Transcription failed: {response.text}"
    result = response.json()
    assert 'text' in result, "No text in response"

    transcription = result['text'].strip().lower()
    assert transcription == "hello world", f"Expected 'hello world', got '{transcription}'"

def test_transcribe_base64():
    """Test transcription with base64 audio data."""
    # Create a simple test audio (silence) in base64
    base64_audio = "UklGRnoAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoAAAA="

    response = requests.post(
        f"{BASE_URL}/transcribe/base64",
        json={"audio_data": base64_audio},
        params={'language': 'auto', 'model_size': 'base'}
    )

    assert response.status_code == 200, f"Base64 transcription failed: {response.text}"
    result = response.json()
    assert 'text' in result

def test_mcp_endpoint():
    """Test MCP endpoint with a JSON-RPC call."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }

    response = requests.post(f"{BASE_URL}/mcp", json=payload)
    assert response.status_code == 200, f"MCP call failed: {response.text}"
    result = response.json()
    assert "result" in result or "error" in result