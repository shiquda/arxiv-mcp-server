# ArXiv Search Service

A powerful and flexible service for searching and analyzing arXiv papers. This tool provides both a Python API and a command-line interface for easy access to arXiv's research paper repository.

## Installation

The recommended installation method uses uv:

```bash
uv pip install git+https://github.com/blazickjp/arxiv-mcp-server.git
```

For development installation with test dependencies:

```bash
# Clone the repository
git clone https://github.com/blazickjp/arxiv-mcp-server.git
cd arxiv-mcp-server

# Create and activate a virtual environment using uv
uv venv
source .venv/bin/activate

# Install the package in development mode with test dependencies
uv pip install -e ".[test]"
```

## Command Line Usage

The package provides a command-line tool `arxiv-search` with two main commands:

### Search for Papers

```bash
# Basic search
arxiv-search search "attention is all you need"

# Advanced search with filters
arxiv-search search "transformer architecture" \
    --max-results 20 \
    --date-from 2023-01-01 \
    --categories cs.AI cs.LG \
    --batch-size 10
```

### Analyze a Specific Paper

```bash
arxiv-search analyze 1706.03762
```

## Python API Usage

The package can also be used as a Python library:

```python
import asyncio
from arxiv_mcp_server.server import ServiceFactory, SearchParameters

async def main():
    # Create service instance
    service = ServiceFactory.create_service()
    
    # Search for papers
    params = SearchParameters(
        query="attention is all you need",
        max_results=5,
        categories=["cs.AI", "cs.LG"]
    )
    result = await service.search_papers(params)
    print(result.text)
    
    # Analyze a specific paper
    analysis = await service.analyze_paper("1706.03762")
    print(analysis.text)

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

To run the tests:

```bash
# Install test dependencies
uv pip install -e ".[test]"

# Run tests
python -m pytest
```

## Features

- Full-text search across arXiv papers
- Date-based filtering
- Category filtering
- Batch processing for efficient retrieval
- Detailed paper analysis
- Asynchronous operation for better performance
- Command-line interface for easy access
- Python API for integration into other projects

## License

MIT License