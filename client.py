#!/usr/bin/env python3
"""
Web Scout MCP Client

A command-line client for interacting with the Web Scout MCP Server.
Provides easy access to web scraping, searching, and analysis tools.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.json import JSON
from rich.syntax import Syntax

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Console for rich output
console = Console()


class WebScoutClient:
    """MCP Client for Web Scout server."""
    
    def __init__(self, server_path: Optional[str] = None):
        """Initialize the client with server path."""
        self.server_path = server_path or "python -m src.server"
        self.session: Optional[ClientSession] = None
        self.tools: List[Dict[str, Any]] = []
        self.resources: List[Dict[str, Any]] = []
    
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Connecting to Web Scout server...", total=None)
                
                # Start the server process and create a session
                async with stdio_client() as (read, write):
                    async with ClientSession(read, write) as session:
                        self.session = session
                        
                        # Initialize the session
                        await session.initialize()
                        
                        # Get available tools and resources
                        tools_result = await session.list_tools()
                        self.tools = [tool.model_dump() for tool in tools_result.tools]
                        
                        resources_result = await session.list_resources()
                        self.resources = [resource.model_dump() for resource in resources_result.resources]
                        
                        progress.update(task, description="Connected successfully!")
                        await asyncio.sleep(0.5)  # Brief pause to show success
                        
                        return True
        
        except Exception as e:
            console.print(f"[red]Error connecting to server: {e}[/red]")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Call a tool on the MCP server."""
        if not self.session:
            console.print("[red]Not connected to server. Use 'connect' command first.[/red]")
            return None
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Executing {tool_name}...", total=None)
                
                result = await self.session.call_tool(tool_name, arguments)
                
                progress.update(task, description=f"Tool {tool_name} completed!")
                await asyncio.sleep(0.3)
                
                return {
                    "tool": tool_name,
                    "arguments": arguments,
                    "result": [content.model_dump() for content in result.content]
                }
        
        except Exception as e:
            console.print(f"[red]Error calling tool {tool_name}: {e}[/red]")
            return None
    
    async def get_resource(self, uri: str) -> Optional[str]:
        """Get a resource from the MCP server."""
        if not self.session:
            console.print("[red]Not connected to server. Use 'connect' command first.[/red]")
            return None
        
        try:
            result = await self.session.read_resource(uri)
            return result.contents[0].text if result.contents else None
        
        except Exception as e:
            console.print(f"[red]Error getting resource {uri}: {e}[/red]")
            return None
    
    def list_tools(self):
        """Display available tools."""
        if not self.tools:
            console.print("[yellow]No tools available. Connect to server first.[/yellow]")
            return
        
        table = Table(title="Available Web Scout Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Required Parameters", style="yellow")
        
        for tool in self.tools:
            required_params = []
            if "inputSchema" in tool and "required" in tool["inputSchema"]:
                required_params = tool["inputSchema"]["required"]
            
            table.add_row(
                tool["name"],
                tool.get("description", "No description"),
                ", ".join(required_params) if required_params else "None"
            )
        
        console.print(table)
    
    def list_resources(self):
        """Display available resources."""
        if not self.resources:
            console.print("[yellow]No resources available. Connect to server first.[/yellow]")
            return
        
        table = Table(title="Available Web Scout Resources")
        table.add_column("URI", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Description", style="yellow")
        table.add_column("MIME Type", style="blue")
        
        for resource in self.resources:
            table.add_row(
                resource["uri"],
                resource.get("name", "Unknown"),
                resource.get("description", "No description"),
                resource.get("mimeType", "unknown")
            )
        
        console.print(table)
    
    def display_result(self, result: Dict[str, Any]):
        """Display tool result in a formatted way."""
        if not result:
            return
        
        # Create panel with tool info
        tool_info = f"Tool: {result['tool']}\nArguments: {json.dumps(result['arguments'], indent=2)}"
        console.print(Panel(tool_info, title="Tool Execution", border_style="blue"))
        
        # Display results
        for i, content in enumerate(result["result"]):
            if content["type"] == "text":
                try:
                    # Try to parse as JSON for pretty printing
                    parsed = json.loads(content["text"])
                    console.print(Panel(JSON.from_data(parsed), title=f"Result {i+1}", border_style="green"))
                except json.JSONDecodeError:
                    # Display as plain text
                    console.print(Panel(content["text"], title=f"Result {i+1}", border_style="green"))


# Global client instance
client = WebScoutClient()


@click.group()
@click.option('--server-path', help='Path to the MCP server executable')
@click.pass_context
def cli(ctx, server_path):
    """Web Scout MCP Client - Interact with web scraping and analysis tools."""
    ctx.ensure_object(dict)
    if server_path:
        global client
        client = WebScoutClient(server_path)


@cli.command()
async def connect():
    """Connect to the Web Scout MCP server."""
    success = await client.connect()
    if success:
        console.print("[green]Successfully connected to Web Scout server![/green]")
        console.print("\nUse 'tools' to see available tools or 'resources' to see available resources.")
    else:
        console.print("[red]Failed to connect to Web Scout server.[/red]")
        sys.exit(1)


@cli.command()
def tools():
    """List available tools."""
    client.list_tools()


@cli.command()
def resources():
    """List available resources."""
    client.list_resources()


@cli.command()
@click.argument('url')
@click.option('--javascript/--no-javascript', default=False, help='Use JavaScript rendering')
@click.option('--links/--no-links', default=True, help='Extract links')
@click.option('--images/--no-images', default=True, help='Extract images')
async def scrape(url, javascript, links, images):
    """Scrape content from a URL."""
    arguments = {
        "url": url,
        "use_javascript": javascript,
        "extract_links": links,
        "extract_images": images
    }
    
    result = await client.call_tool("scrape_url", arguments)
    if result:
        client.display_result(result)


@cli.command()
@click.argument('query')
@click.option('--max-results', default=10, help='Maximum number of results')
@click.option('--search-type', default='web', type=click.Choice(['web', 'images', 'news', 'videos']), help='Type of search')
async def search(query, max_results, search_type):
    """Search the web for information."""
    arguments = {
        "query": query,
        "max_results": max_results,
        "search_type": search_type
    }
    
    result = await client.call_tool("search_web", arguments)
    if result:
        client.display_result(result)


@cli.command()
@click.argument('url')
@click.option('--seo/--no-seo', default=True, help='Include SEO analysis')
@click.option('--performance/--no-performance', default=True, help='Include performance analysis')
@click.option('--accessibility/--no-accessibility', default=True, help='Include accessibility analysis')
@click.option('--security/--no-security', default=True, help='Include security analysis')
async def analyze(url, seo, performance, accessibility, security):
    """Analyze a website comprehensively."""
    arguments = {
        "url": url,
        "include_seo": seo,
        "include_performance": performance,
        "include_accessibility": accessibility,
        "include_security": security
    }
    
    result = await client.call_tool("analyze_website", arguments)
    if result:
        client.display_result(result)


@cli.command()
@click.argument('content')
@click.option('--sentiment/--no-sentiment', default=True, help='Include sentiment analysis')
@click.option('--entities/--no-entities', default=True, help='Include entity extraction')
@click.option('--keywords/--no-keywords', default=True, help='Include keyword extraction')
async def analyze_content(content, sentiment, entities, keywords):
    """Analyze text content for insights."""
    arguments = {
        "content": content,
        "include_sentiment": sentiment,
        "include_entities": entities,
        "include_keywords": keywords
    }
    
    result = await client.call_tool("analyze_content", arguments)
    if result:
        client.display_result(result)


@cli.command()
@click.argument('domain')
@click.argument('query')
@click.option('--max-results', default=10, help='Maximum number of results')
async def search_domain(domain, query, max_results):
    """Search within a specific domain."""
    arguments = {
        "domain": domain,
        "query": query,
        "max_results": max_results
    }
    
    result = await client.call_tool("search_domain", arguments)
    if result:
        client.display_result(result)


@cli.command()
@click.argument('url')
@click.option('--interval', default=60, help='Check interval in minutes')
@click.option('--notify/--no-notify', default=True, help='Notify about changes')
async def monitor(url, interval, notify):
    """Monitor a website for changes."""
    arguments = {
        "url": url,
        "check_interval": interval,
        "notify_changes": notify
    }
    
    result = await client.call_tool("monitor_website", arguments)
    if result:
        client.display_result(result)


@cli.command()
@click.argument('uri')
async def resource(uri):
    """Get a resource from the server."""
    content = await client.get_resource(uri)
    if content:
        try:
            # Try to parse and display as JSON
            parsed = json.loads(content)
            console.print(Panel(JSON.from_data(parsed), title=f"Resource: {uri}", border_style="cyan"))
        except json.JSONDecodeError:
            # Display as plain text
            console.print(Panel(content, title=f"Resource: {uri}", border_style="cyan"))


def main():
    """Main entry point with async support."""
    def run_async_command(func):
        """Wrapper to run async commands."""
        def wrapper(*args, **kwargs):
            return asyncio.run(func(*args, **kwargs))
        return wrapper
    
    # Wrap async commands
    for command in [connect, scrape, search, analyze, analyze_content, search_domain, monitor, resource]:
        command.callback = run_async_command(command.callback)
    
    cli()


if __name__ == "__main__":
    main()