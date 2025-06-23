#!/usr/bin/env python3
"""
Tests for Web Scout MCP Client
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import json

import sys
from pathlib import Path

# Add parent directory to path to import client
sys.path.append(str(Path(__file__).parent.parent))

from client import WebScoutClient


class TestWebScoutClient:
    """Test cases for WebScoutClient."""
    
    @pytest.fixture
    def client(self):
        """Create a test client instance."""
        return WebScoutClient()
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock MCP session."""
        session = AsyncMock()
        session.initialize = AsyncMock()
        session.list_tools = AsyncMock()
        session.list_resources = AsyncMock()
        session.call_tool = AsyncMock()
        session.read_resource = AsyncMock()
        return session
    
    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.server_path == "python -m src.server"
        assert client.session is None
        assert client.tools == []
        assert client.resources == []
    
    def test_client_initialization_with_custom_path(self):
        """Test client initialization with custom server path."""
        custom_path = "/custom/path/to/server"
        client = WebScoutClient(custom_path)
        assert client.server_path == custom_path
    
    @pytest.mark.asyncio
    async def test_connect_success(self, client, mock_session):
        """Test successful connection to server."""
        # Mock the tools and resources
        mock_tool = Mock()
        mock_tool.model_dump.return_value = {
            "name": "test_tool",
            "description": "Test tool"
        }
        
        mock_resource = Mock()
        mock_resource.model_dump.return_value = {
            "uri": "test://resource",
            "name": "Test Resource"
        }
        
        mock_tools_result = Mock()
        mock_tools_result.tools = [mock_tool]
        
        mock_resources_result = Mock()
        mock_resources_result.resources = [mock_resource]
        
        mock_session.list_tools.return_value = mock_tools_result
        mock_session.list_resources.return_value = mock_resources_result
        
        # Mock the stdio_client and ClientSession
        with patch('client.stdio_client') as mock_stdio, \
             patch('client.ClientSession') as mock_client_session:
            
            mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(Mock(), Mock()))
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=None)
            
            mock_client_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await client.connect()
            
            assert result is True
            assert len(client.tools) == 1
            assert len(client.resources) == 1
            assert client.tools[0]["name"] == "test_tool"
            assert client.resources[0]["uri"] == "test://resource"
    
    @pytest.mark.asyncio
    async def test_connect_failure(self, client):
        """Test connection failure."""
        with patch('client.stdio_client') as mock_stdio:
            mock_stdio.side_effect = Exception("Connection failed")
            
            result = await client.connect()
            
            assert result is False
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, client, mock_session):
        """Test successful tool call."""
        client.session = mock_session
        
        # Mock the tool result
        mock_content = Mock()
        mock_content.model_dump.return_value = {
            "type": "text",
            "text": "Tool result"
        }
        
        mock_result = Mock()
        mock_result.content = [mock_content]
        
        mock_session.call_tool.return_value = mock_result
        
        result = await client.call_tool("test_tool", {"param": "value"})
        
        assert result is not None
        assert result["tool"] == "test_tool"
        assert result["arguments"] == {"param": "value"}
        assert len(result["result"]) == 1
        assert result["result"][0]["text"] == "Tool result"
    
    @pytest.mark.asyncio
    async def test_call_tool_no_session(self, client):
        """Test tool call without active session."""
        result = await client.call_tool("test_tool", {})
        assert result is None
    
    @pytest.mark.asyncio
    async def test_call_tool_failure(self, client, mock_session):
        """Test tool call failure."""
        client.session = mock_session
        mock_session.call_tool.side_effect = Exception("Tool call failed")
        
        result = await client.call_tool("test_tool", {})
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_resource_success(self, client, mock_session):
        """Test successful resource retrieval."""
        client.session = mock_session
        
        mock_content = Mock()
        mock_content.text = "Resource content"
        
        mock_result = Mock()
        mock_result.contents = [mock_content]
        
        mock_session.read_resource.return_value = mock_result
        
        result = await client.get_resource("test://resource")
        
        assert result == "Resource content"
    
    @pytest.mark.asyncio
    async def test_get_resource_no_session(self, client):
        """Test resource retrieval without active session."""
        result = await client.get_resource("test://resource")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_resource_failure(self, client, mock_session):
        """Test resource retrieval failure."""
        client.session = mock_session
        mock_session.read_resource.side_effect = Exception("Resource read failed")
        
        result = await client.get_resource("test://resource")
        assert result is None
    
    def test_list_tools_no_tools(self, client, capsys):
        """Test listing tools when none are available."""
        client.list_tools()
        captured = capsys.readouterr()
        assert "No tools available" in captured.out
    
    def test_list_tools_with_tools(self, client):
        """Test listing tools when tools are available."""
        client.tools = [
            {
                "name": "test_tool",
                "description": "Test tool",
                "inputSchema": {
                    "required": ["param1", "param2"]
                }
            }
        ]
        
        # Just test that it doesn't raise an exception
        # Rich output testing would require more complex mocking
        client.list_tools()
    
    def test_list_resources_no_resources(self, client, capsys):
        """Test listing resources when none are available."""
        client.list_resources()
        captured = capsys.readouterr()
        assert "No resources available" in captured.out
    
    def test_list_resources_with_resources(self, client):
        """Test listing resources when resources are available."""
        client.resources = [
            {
                "uri": "test://resource",
                "name": "Test Resource",
                "description": "Test resource description",
                "mimeType": "application/json"
            }
        ]
        
        # Just test that it doesn't raise an exception
        client.list_resources()
    
    def test_display_result_none(self, client):
        """Test displaying None result."""
        # Should not raise an exception
        client.display_result(None)
    
    def test_display_result_with_data(self, client):
        """Test displaying result with data."""
        result = {
            "tool": "test_tool",
            "arguments": {"param": "value"},
            "result": [
                {
                    "type": "text",
                    "text": '{"key": "value"}'
                }
            ]
        }
        
        # Just test that it doesn't raise an exception
        client.display_result(result)


class TestClientIntegration:
    """Integration tests for the client."""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a complete workflow (mocked)."""
        client = WebScoutClient()
        
        # Mock all the external dependencies
        with patch('client.stdio_client') as mock_stdio, \
             patch('client.ClientSession') as mock_client_session:
            
            # Set up mocks
            mock_session = AsyncMock()
            
            # Tools list
            mock_tool = Mock()
            mock_tool.model_dump.return_value = {
                "name": "scrape_url",
                "description": "Scrape a URL",
                "inputSchema": {"required": ["url"]}
            }
            mock_tools_result = Mock()
            mock_tools_result.tools = [mock_tool]
            mock_session.list_tools.return_value = mock_tools_result
            
            # Resources list
            mock_resources_result = Mock()
            mock_resources_result.resources = []
            mock_session.list_resources.return_value = mock_resources_result
            
            # Tool call result
            mock_content = Mock()
            mock_content.model_dump.return_value = {
                "type": "text",
                "text": '{"url": "https://example.com", "title": "Example"}'
            }
            mock_tool_result = Mock()
            mock_tool_result.content = [mock_content]
            mock_session.call_tool.return_value = mock_tool_result
            
            # Set up context managers
            mock_stdio.return_value.__aenter__ = AsyncMock(return_value=(Mock(), Mock()))
            mock_stdio.return_value.__aexit__ = AsyncMock(return_value=None)
            mock_client_session.return_value.__aenter__ = AsyncMock(return_value=mock_session)
            mock_client_session.return_value.__aexit__ = AsyncMock(return_value=None)
            
            # Test the workflow
            connected = await client.connect()
            assert connected is True
            
            result = await client.call_tool("scrape_url", {"url": "https://example.com"})
            assert result is not None
            assert result["tool"] == "scrape_url"


if __name__ == "__main__":
    pytest.main([__file__])