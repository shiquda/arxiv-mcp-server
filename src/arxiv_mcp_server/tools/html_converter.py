"""HTML to Markdown conversion functionality for arXiv papers."""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Tuple
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import ssl
import urllib3
from urllib3.util.ssl_ import create_urllib3_context

logger = logging.getLogger("arxiv-mcp-server")

# Configure to handle SSL issues in some environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ArxivHTMLConverter:
    """Converts arXiv HTML pages to Markdown format."""

    def __init__(self):
        """Initialize the converter with proper SSL context."""
        # Create a custom SSL context that's more permissive
        ctx = create_urllib3_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        self.session = requests.Session()
        # Configure session for potential SSL issues
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _get_arxiv_html_url(self, paper_id: str) -> str:
        """Generate arXiv HTML URL from paper ID."""
        return f"https://arxiv.org/html/{paper_id}"

    def _clean_html_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Clean and extract the main content from arXiv HTML."""
        # Remove navigation, headers, footers, and other non-content elements
        for element in soup(['nav', 'header', 'footer', 'script', 'style', 'aside']):
            element.decompose()

        # Remove specific arXiv navigation elements
        for element in soup.find_all(['div'], class_=['abs-nav', 'leftcolumn', 'rightcolumn']):
            element.decompose()

        # Focus on the main content area
        main_content = soup.find('div', class_='ltx_page_main') or soup.find('main') or soup.find('body')

        if main_content:
            return main_content
        return soup

    def _html_to_markdown(self, html_content: str) -> str:
        """Convert HTML content to clean Markdown."""
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Clean the content
        cleaned_soup = self._clean_html_content(soup)

        # Convert to markdown with custom settings
        markdown_content = md(
            str(cleaned_soup),
            heading_style="ATX",  # Use # style headings
            bullets="-",  # Use - for bullets
            convert=['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong',
                     'em', 'ul', 'ol', 'li', 'blockquote', 'code', 'pre'],
            escape_asterisks=False,
            escape_underscores=False
        )

        # Clean up the markdown
        lines = markdown_content.split('\n')
        cleaned_lines = []

        for line in lines:
            line = line.strip()
            # Skip empty lines that are too frequent
            if line or (cleaned_lines and cleaned_lines[-1]):
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    async def fetch_paper_html(self, paper_id: str) -> Tuple[bool, str]:
        """
        Fetch arXiv paper HTML content and convert to Markdown.

        Args:
            paper_id: The arXiv paper ID

        Returns:
            Tuple of (success: bool, content: str)
            If success is False, content contains the error message
        """
        try:
            url = self._get_arxiv_html_url(paper_id)
            logger.info(f"Fetching HTML for paper {paper_id} from {url}")

            # Make the request in a thread to avoid blocking
            def fetch():
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                return response.text

            html_content = await asyncio.to_thread(fetch)

            # Convert to markdown
            markdown_content = await asyncio.to_thread(self._html_to_markdown, html_content)

            if not markdown_content.strip():
                return False, f"Failed to extract content from HTML for paper {paper_id}"

            logger.info(f"Successfully converted paper {paper_id} to markdown ({len(markdown_content)} chars)")
            return True, markdown_content

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching paper {paper_id}: {str(e)}")
            return False, f"Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Error processing paper {paper_id}: {str(e)}")
            return False, f"Processing error: {str(e)}"

    async def get_or_fetch_paper_content(self, paper_id: str, storage_path: Path) -> Tuple[bool, str]:
        """
        Get paper content from cache or fetch from arXiv HTML.

        Args:
            paper_id: The arXiv paper ID
            storage_path: Path to storage directory

        Returns:
            Tuple of (success: bool, content: str)
        """
        # Check if we have a cached version
        cached_file = storage_path / f"{paper_id}.md"

        if cached_file.exists():
            try:
                async with asyncio.to_thread(open, cached_file, 'r', encoding='utf-8') as f:
                    content = await asyncio.to_thread(f.read)
                logger.info(f"Using cached content for paper {paper_id}")
                return True, content
            except Exception as e:
                logger.warning(f"Error reading cached file for {paper_id}: {e}")

        # Fetch from arXiv HTML
        success, content = await self.fetch_paper_html(paper_id)

        if success:
            # Cache the result
            try:
                storage_path.mkdir(parents=True, exist_ok=True)
                async with asyncio.to_thread(open, cached_file, 'w', encoding='utf-8') as f:
                    await asyncio.to_thread(f.write, content)
                logger.info(f"Cached content for paper {paper_id}")
            except Exception as e:
                logger.warning(f"Error caching content for {paper_id}: {e}")

        return success, content
