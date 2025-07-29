"""Get paper content functionality for the arXiv MCP server."""

import json
from pathlib import Path
from typing import Dict, Any, List
import mcp.types as types
from ..config import Settings
from .html_converter import ArxivHTMLConverter

settings = Settings()
html_converter = ArxivHTMLConverter()

read_tool = types.Tool(
    name="get_paper",
    description="Get the full content of an arXiv paper in markdown format from HTML source",
    inputSchema={
        "type": "object",
        "properties": {
            "paper_id": {
                "type": "string",
                "description": "The arXiv ID of the paper to get (e.g., '1706.03762')",
            }
        },
        "required": ["paper_id"],
    },
)


def list_papers() -> list[str]:
    """List all cached paper IDs."""
    return [p.stem for p in Path(settings.STORAGE_PATH).glob("*.md")]


async def handle_read_paper(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle requests to get a paper's content from arXiv HTML."""
    try:
        paper_id = arguments["paper_id"]

        # Use the HTML converter to get paper content
        success, content = await html_converter.get_or_fetch_paper_content(
            paper_id, Path(settings.STORAGE_PATH)
        )

        if not success:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "status": "error",
                            "message": f"Failed to get paper {paper_id}: {content}",
                        }
                    ),
                )
            ]

        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "success",
                        "paper_id": paper_id,
                        "content": content,
                        "source": "arXiv HTML",
                        "cached": Path(settings.STORAGE_PATH, f"{paper_id}.md").exists()
                    }
                ),
            )
        ]

    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "status": "error",
                        "message": f"Error getting paper: {str(e)}",
                    }
                ),
            )
        ]
