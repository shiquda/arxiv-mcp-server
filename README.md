# ArXiv MCP Server

A Model Context Protocol server for searching and analyzing arXiv papers. This server enables AI models like Claude to access and analyze academic papers from arXiv.

## Features

- **Paper Search**: Full-text search across arXiv papers with filtering options
- **Paper Analysis**: Detailed metadata and analysis of specific papers
- **Async Support**: Efficient handling of concurrent requests
- **Structured Output**: Clean JSON responses for easy parsing

## Installation

```bash
uv add mcp-server arxiv httpx
```

## Usage

1. Start the server:
```bash
python -m arxiv_mcp_server
```

2. Configure Claude Desktop to use the server:

Add to claude_desktop_config.json:
```json
{
  "mcpServers": {
    "arxiv": {
      "command": "python",
      "args": ["-m", "arxiv_mcp_server"]
    }
  }
}
```

## API

### Tools

1. `search_papers`
   - Search arXiv papers with filtering options
   - Parameters:
     - query: Search query string
     - max_results: Maximum number of results (1-50)
     - date_from: Filter papers from date (YYYY-MM-DD)
     - categories: List of arXiv categories

2. `analyze_paper`
   - Get detailed analysis of a specific paper
   - Parameters:
     - paper_id: arXiv paper ID

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License