#!/bin/bash

# Web Scout MCP Client - CLI Usage Examples
# This script demonstrates various ways to use the Web Scout client from the command line.

echo "Web Scout MCP Client - CLI Examples"
echo "=================================="

# Check if the client is installed
if ! command -v webscout &> /dev/null; then
    echo "Error: webscout command not found. Please install the client first."
    echo "Run: pip install -e . from the client directory"
    exit 1
fi

echo ""
echo "1. Connecting to the server..."
webscout connect

echo ""
echo "2. Listing available tools..."
webscout tools

echo ""
echo "3. Basic web scraping..."
webscout scrape https://example.com

echo ""
echo "4. Web scraping with JavaScript..."
webscout scrape https://httpbin.org/html --javascript

echo ""
echo "5. Basic web search..."
webscout search "python web scraping tutorial"

echo ""
echo "6. Image search..."
webscout search "beautiful nature photos" --search-type images --max-results 5

echo ""
echo "7. News search..."
webscout search "artificial intelligence" --search-type news --max-results 8

echo ""
echo "8. Website analysis..."
webscout analyze https://github.com

echo ""
echo "9. SEO-focused analysis..."
webscout analyze https://www.python.org --no-performance --no-accessibility --no-security

echo ""
echo "10. Content analysis..."
webscout analyze-content "This product is absolutely fantastic! Great quality and excellent customer service."

echo ""
echo "11. Domain-specific search..."
webscout search-domain stackoverflow.com "python async programming" --max-results 5

echo ""
echo "12. Website monitoring setup..."
webscout monitor https://httpbin.org/html --interval 30 --notify

echo ""
echo "13. Accessing resources..."
webscout resource "webscout://history/scraping"

echo ""
echo "14. Listing available resources..."
webscout resources

echo ""
echo "CLI Examples completed!"
echo "======================"
echo ""
echo "Tips:"
echo "- Use --help with any command to see available options"
echo "- Results are displayed in a rich, formatted output"
echo "- All operations require an active connection to the MCP server"
echo "- Check the README.md for more detailed usage instructions"