import os
import json
import logging
from datetime import datetime
from collections.abc import Sequence
from typing import Any

import arxiv
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arxiv-server")

class ArxivServer:
    def __init__(self):
        self.app = Server("arxiv-server")
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.list_tools()
        async def list_tools() -> list[Tool]:
            """List available arXiv tools."""
            return [
                Tool(
                    name="search_papers",
                    description="Search arXiv papers with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query (e.g. 'transformer attention')"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results (1-50)",
                                "minimum": 1,
                                "maximum": 50
                            },
                            "categories": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of arXiv categories (e.g. cs.AI, cs.LG)"
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="analyze_paper",
                    description="Get detailed analysis of a specific paper",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "paper_id": {
                                "type": "string",
                                "description": "arXiv paper ID"
                            }
                        },
                        "required": ["paper_id"]
                    }
                )
            ]

        @self.app.call_tool()
        async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | EmbeddedResource]:
            """Handle tool calls for arXiv operations."""
            if name == "search_papers":
                return await self._handle_search(arguments)
            elif name == "analyze_paper":
                return await self._handle_analysis(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_search(self, arguments: dict) -> Sequence[TextContent]:
        """Handle paper search requests."""
        query = arguments["query"]
        max_results = min(int(arguments.get("max_results", 10)), 50)
        
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )

        results = []
        async for paper in client.results(search):
            results.append({
                "id": paper.get_short_id(),
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "abstract": paper.summary,
                "categories": paper.categories,
                "published": paper.published.isoformat(),
                "url": paper.pdf_url
            })

        return [TextContent(type="text", text=json.dumps(results, indent=2))]

    async def _handle_analysis(self, arguments: dict) -> Sequence[TextContent]:
        """Handle detailed paper analysis requests."""
        paper_id = arguments["paper_id"]
        
        client = arxiv.Client()
        search = arxiv.Search(id_list=[paper_id])
        
        papers = list(client.results(search))
        if not papers:
            raise ValueError(f"Paper not found: {paper_id}")
        
        paper = papers[0]
        analysis = {
            "id": paper.get_short_id(),
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "abstract": paper.summary,
            "categories": paper.categories,
            "published": paper.published.isoformat(),
            "url": paper.pdf_url,
            "comment": paper.comment,
            "journal_ref": paper.journal_ref,
            "primary_category": paper.primary_category,
            "links": [link.href for link in paper.links]
        }
        
        return [TextContent(type="text", text=json.dumps(analysis, indent=2))]

    async def run(self):
        """Run the server."""
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                self.app.create_initialization_options()
            )

async def main():
    server = ArxivServer()
    await server.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())