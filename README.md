# ArXiv MCP Server

The ArXiv MCP Server is a powerful interface that enables AI models to interact with academic research through the Model Context Protocol (MCP). By integrating with arXiv's extensive research repository, this server allows AI assistants to perform sophisticated paper searches and access full paper content, enhancing their ability to engage with scientific literature.

## Overview

This server implementation focuses on two essential capabilities that bridge the gap between AI models and academic research:

The search functionality provides precise access to arXiv's database, supporting detailed queries with date ranges and category filters. Each query returns comprehensive metadata, enabling AI models to identify relevant research effectively.

The download system transforms papers into MCP resources, storing them locally for efficient access. This architecture ensures that AI models can perform in-depth analysis of research content while maintaining reasonable response times.

## Installation

We recommend using `uv` for installation. For production deployment, install directly from the repository:

```bash
uv pip install git+https://github.com/blazickjp/arxiv-mcp-server.git
```

For development work, install with test dependencies:

```bash
# Clone the repository
git clone https://github.com/blazickjp/arxiv-mcp-server.git
cd arxiv-mcp-server

# Create and activate a virtual environment
uv venv
source .venv/bin/activate

# Install development dependencies
uv pip install -e ".[test]"
```

## Tool Interface

The server exposes two primary tools through the MCP interface:

### Paper Search

The search interface supports comprehensive queries with multiple parameters:

```python
# Example search for recent AI papers
result = await call_tool("search_papers", {
    "query": "transformer architecture applications",
    "max_results": 10,
    "date_from": "2023-01-01",
    "categories": ["cs.AI", "cs.LG"],
})

# The response includes detailed paper metadata
{
    "total_results": 10,
    "papers": [
        {
            "id": "2401.12345",
            "title": "Example Paper Title",
            "authors": ["Author Name"],
            "abstract": "Paper abstract...",
            "categories": ["cs.AI"],
            "published": "2024-01-15T00:00:00Z",
            "resource_uri": "arxiv://2401.12345"
        }
        # ... additional results
    ]
}
```

### Paper Download

The download tool converts papers into accessible resources:

```python
# Download a specific paper
result = await call_tool("download_paper", {
    "paper_id": "2401.12345"
})

# Success response
{
    "status": "success",
    "resource_uri": "arxiv://2401.12345",
    "message": "Paper downloaded successfully"
}
```

After download, papers are available as MCP resources using the URI format: `arxiv://{paper_id}`

## Configuration

The server's behavior can be customized through environment variables:

- `ARXIV_STORAGE_PATH`: Directory path for storing downloaded papers (default: ~/.arxiv-mcp-server/papers)
- `ARXIV_MAX_RESULTS`: Maximum number of search results per query (default: 50)
- `ARXIV_REQUEST_TIMEOUT`: Timeout duration for arXiv API requests (default: 30 seconds)

## Development

The project maintains high code quality standards through comprehensive testing:

```bash
# Run the test suite with coverage reporting
python -m pytest
```

Our test suite includes:
- Unit tests covering individual components
- Integration tests ensuring MCP protocol compliance
- Mock-based tests for external service interactions
- Coverage reporting to maintain test quality

## Technical Architecture

The server implements a modular design with four primary components:

1. Tool Layer: Implements the MCP protocol interface, handling search and download requests
2. Resource Management: Manages paper storage and retrieval operations
3. Service Layer: Coordinates interactions with the arXiv API
4. Configuration: Provides environment-based system configuration

## Dependencies

The server relies on several key Python packages:

- arxiv>=2.1.0: Provides arXiv API integration
- mcp>=1.0.0: Implements the Model Context Protocol
- aiohttp>=3.9.1: Handles asynchronous HTTP operations
- pydantic>=2.8.0: Manages data validation and settings
- python-dateutil>=2.8.2: Provides date parsing capabilities
- aiofiles>=23.2.1: Enables asynchronous file operations

For development, additional dependencies include:
- pytest>=8.0.0: Testing framework
- pytest-asyncio>=0.23.5: Asynchronous test support
- pytest-cov>=4.1.0: Coverage reporting
- pytest-mock>=3.10.0: Mocking utilities

## Contributing

We welcome contributions that enhance the server's capabilities. Contributors should:

1. Ensure all tests pass with no regressions
2. Include tests for new functionality
3. Follow the project's code style guidelines
4. Update documentation to reflect changes
5. Provide clear commit messages explaining modifications

## License

This project is licensed under the MIT License. See the LICENSE file for details.