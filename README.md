# Web Scout MCP Client

A powerful command-line client for interacting with the Web Scout MCP (Model Context Protocol) Server. This client provides easy access to web scraping, searching, and analysis tools through a rich CLI interface.

## Features

- 🌐 **Web Scraping**: Extract content, links, and images from websites
- 🔍 **Web Search**: Search the web with multiple search types (web, images, news, videos)
- 📊 **Website Analysis**: Comprehensive analysis including SEO, performance, accessibility, and security
- 📝 **Content Analysis**: Analyze text for sentiment, entities, and keywords
- 🎯 **Domain Search**: Search within specific domains
- 📱 **Website Monitoring**: Monitor websites for changes
- 🎨 **Rich CLI**: Beautiful command-line interface with progress indicators and formatted output

## Installation

### From Source

1. Clone the repository:
```bash
git clone <repository-url>
cd Web-Scout-MCP-Client
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the client:
```bash
pip install -e .
```

### Using pip (when published)

```bash
pip install web-scout-mcp-client
```

## Quick Start

### 1. Start the Web Scout MCP Server

First, make sure the Web Scout MCP Server is running. Navigate to the server directory and start it:

```bash
cd ../Web-Scout-MCP-Server
python -m src.server
```

### 2. Connect to the Server

```bash
webscout connect
```

### 3. List Available Tools

```bash
webscout tools
```

### 4. Use the Tools

```bash
# Scrape a website
webscout scrape https://example.com

# Search the web
webscout search "python web scraping"

# Analyze a website
webscout analyze https://example.com

# Monitor a website for changes
webscout monitor https://example.com --interval 30
```

## Usage

### Connection Management

```bash
# Connect to the server (required before using other commands)
webscout connect

# List available tools
webscout tools

# List available resources
webscout resources
```

### Web Scraping

```bash
# Basic scraping
webscout scrape https://example.com

# Scraping with JavaScript rendering
webscout scrape https://spa-website.com --javascript

# Scraping without extracting links or images
webscout scrape https://example.com --no-links --no-images
```

### Web Search

```bash
# Basic web search
webscout search "machine learning tutorials"

# Search with specific parameters
webscout search "AI news" --max-results 20 --search-type news

# Image search
webscout search "beautiful landscapes" --search-type images
```

### Website Analysis

```bash
# Full website analysis
webscout analyze https://example.com

# Analysis with specific components
webscout analyze https://example.com --no-security --no-performance

# SEO-focused analysis
webscout analyze https://example.com --no-accessibility --no-security
```

### Content Analysis

```bash
# Analyze text content
webscout analyze-content "This is a great product! I love it."

# Analysis with specific features
webscout analyze-content "Some text" --no-entities --no-keywords
```

### Domain Search

```bash
# Search within a specific domain
webscout search-domain github.com "python mcp"

# Search with more results
webscout search-domain stackoverflow.com "async python" --max-results 20
```

### Website Monitoring

```bash
# Monitor a website (check every hour)
webscout monitor https://example.com --interval 60

# Monitor without notifications
webscout monitor https://example.com --no-notify
```

### Resource Access

```bash
# Access server resources
webscout resource "webscout://history/scraping"
webscout resource "webscout://cache/analysis"
webscout resource "webscout://example.com/analysis"
```

## Command Reference

### Global Options

- `--server-path`: Path to the MCP server executable (optional)

### Commands

#### `connect`
Connect to the Web Scout MCP server.

#### `tools`
List all available tools from the server.

#### `resources`
List all available resources from the server.

#### `scrape <url>`
Scrape content from a URL.

**Options:**
- `--javascript/--no-javascript`: Use JavaScript rendering (default: no)
- `--links/--no-links`: Extract links (default: yes)
- `--images/--no-images`: Extract images (default: yes)

#### `search <query>`
Search the web for information.

**Options:**
- `--max-results`: Maximum number of results (default: 10)
- `--search-type`: Type of search - web, images, news, videos (default: web)

#### `analyze <url>`
Perform comprehensive website analysis.

**Options:**
- `--seo/--no-seo`: Include SEO analysis (default: yes)
- `--performance/--no-performance`: Include performance analysis (default: yes)
- `--accessibility/--no-accessibility`: Include accessibility analysis (default: yes)
- `--security/--no-security`: Include security analysis (default: yes)

#### `analyze-content <content>`
Analyze text content for insights.

**Options:**
- `--sentiment/--no-sentiment`: Include sentiment analysis (default: yes)
- `--entities/--no-entities`: Include entity extraction (default: yes)
- `--keywords/--no-keywords`: Include keyword extraction (default: yes)

#### `search-domain <domain> <query>`
Search within a specific domain.

**Options:**
- `--max-results`: Maximum number of results (default: 10)

#### `monitor <url>`
Monitor a website for changes.

**Options:**
- `--interval`: Check interval in minutes (default: 60)
- `--notify/--no-notify`: Notify about changes (default: yes)

#### `resource <uri>`
Get a resource from the server.

## Examples

### Complete Website Analysis Workflow

```bash
# 1. Connect to server
webscout connect

# 2. Scrape a website
webscout scrape https://example.com --javascript

# 3. Analyze the website
webscout analyze https://example.com

# 4. Search for related content
webscout search "example.com reviews"

# 5. Monitor for changes
webscout monitor https://example.com --interval 30
```

### Content Research Workflow

```bash
# 1. Search for information
webscout search "sustainable energy solutions" --max-results 15

# 2. Analyze specific domains
webscout search-domain energy.gov "renewable energy"

# 3. Scrape detailed content
webscout scrape https://energy.gov/renewable-energy

# 4. Analyze the content
webscout analyze-content "The scraped content here..."
```

## Configuration

The client automatically connects to the Web Scout MCP Server. You can specify a custom server path using the `--server-path` option.

## Error Handling

The client provides detailed error messages and uses rich formatting to display results. If you encounter connection issues:

1. Ensure the Web Scout MCP Server is running
2. Check that all dependencies are installed
3. Verify the server path is correct

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black client.py
flake8 client.py
```

### Type Checking

```bash
mypy client.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the examples above

## Related Projects

- [Web Scout MCP Server](../Web-Scout-MCP-Server/): The backend server providing the web scraping and analysis capabilities