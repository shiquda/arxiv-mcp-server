"""Resource management and storage for arXiv papers."""

from pathlib import Path
from typing import List, Dict, Optional
import arxiv
import pymupdf4llm
import aiofiles
import logging
import asyncio
from dataclasses import dataclass
from datetime import datetime
import mcp.types as types
from mcp.server import AnyUrl
from .config import Settings

logger = logging.getLogger("arxiv-mcp-server")


@dataclass
class ConversionStatus:
    """Track the status of a PDF to Markdown conversion."""
    paper_id: str
    status: str  # 'pending', 'converting', 'completed', 'failed'
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class PaperManager:
    """Manages the storage, retrieval, and resource handling of arXiv papers."""

    def __init__(self):
        """Initialize the paper management system."""
        settings