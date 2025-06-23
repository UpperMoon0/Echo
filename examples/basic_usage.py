#!/usr/bin/env python3
"""
Basic usage examples for Web Scout MCP Client

This script demonstrates how to use the Web Scout client programmatically.
"""

import asyncio
import json
from pathlib import Path
import sys

# Add parent directory to path to import client
sys.path.append(str(Path(__file__).parent.parent))

from client import WebScoutClient


async def basic_scraping_example():
    """Example of basic web scraping."""
    print("=== Basic Web Scraping Example ===")
    
    client = WebScoutClient()
    
    # Connect to server
    print("Connecting to Web Scout server...")
    connected = await client.connect()
    if not connected:
        print("Failed to connect to server")
        return
    
    # Scrape a website
    print("Scraping example.com...")
    result = await client.call_tool("scrape_url", {
        "url": "https://example.com",
        "use_javascript": False,
        "extract_links": True,
        "extract_images": True
    })
    
    if result:
        print("Scraping completed successfully!")
        print(json.dumps(result, indent=2))
    else:
        print("Scraping failed")


async def search_example():
    """Example of web searching."""
    print("\n=== Web Search Example ===")
    
    client = WebScoutClient()
    
    # Connect to server
    connected = await client.connect()
    if not connected:
        print("Failed to connect to server")
        return
    
    # Search the web
    print("Searching for 'python web scraping'...")
    result = await client.call_tool("search_web", {
        "query": "python web scraping",
        "max_results": 5,
        "search_type": "web"
    })
    
    if result:
        print("Search completed successfully!")
        print(json.dumps(result, indent=2))
    else:
        print("Search failed")


async def analysis_example():
    """Example of website analysis."""
    print("\n=== Website Analysis Example ===")
    
    client = WebScoutClient()
    
    # Connect to server
    connected = await client.connect()
    if not connected:
        print("Failed to connect to server")
        return
    
    # Analyze a website
    print("Analyzing github.com...")
    result = await client.call_tool("analyze_website", {
        "url": "https://github.com",
        "include_seo": True,
        "include_performance": True,
        "include_accessibility": False,
        "include_security": False
    })
    
    if result:
        print("Analysis completed successfully!")
        print(json.dumps(result, indent=2))
    else:
        print("Analysis failed")


async def content_analysis_example():
    """Example of content analysis."""
    print("\n=== Content Analysis Example ===")
    
    client = WebScoutClient()
    
    # Connect to server
    connected = await client.connect()
    if not connected:
        print("Failed to connect to server")
        return
    
    # Analyze some text content
    sample_text = """
    This is an amazing product! I absolutely love using it every day.
    The customer service is outstanding and the quality is top-notch.
    However, the price could be a bit lower. Overall, I would definitely
    recommend this to anyone looking for a reliable solution.
    """
    
    print("Analyzing sample text content...")
    result = await client.call_tool("analyze_content", {
        "content": sample_text,
        "include_sentiment": True,
        "include_entities": True,
        "include_keywords": True
    })
    
    if result:
        print("Content analysis completed successfully!")
        print(json.dumps(result, indent=2))
    else:
        print("Content analysis failed")


async def main():
    """Run all examples."""
    print("Web Scout MCP Client - Basic Usage Examples")
    print("=" * 50)
    
    try:
        await basic_scraping_example()
        await search_example()
        await analysis_example()
        await content_analysis_example()
        
        print("\n" + "=" * 50)
        print("All examples completed!")
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"\nError running examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())