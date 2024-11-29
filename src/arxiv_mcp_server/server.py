import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import asyncio

import arxiv
from dateutil import parser as date_parser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("arxiv-server")


@dataclass
class SearchParameters:
    """Parameters for arXiv paper search."""

    query: str
    max_results: int = 10
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    categories: List[str] = None
    batch_size: int = 10


@dataclass
class ToolResponse:
    """Standard response format for tool operations."""

    content_type: str = "text"
    text: str = ""


class ArxivService:
    """Core service for interacting with arXiv."""

    def __init__(self):
        """Initialize the arXiv service."""
        self.client = arxiv.Client()

    def _make_timezone_aware(self, dt: datetime) -> datetime:
        """Convert naive datetime to timezone-aware."""
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt

    def _validate_dates(
        self, date_from: Optional[str], date_to: Optional[str]
    ) -> tuple[Optional[datetime], Optional[datetime]]:
        """Validate and parse date strings."""
        try:
            start_date = date_parser.parse(date_from) if date_from else None
            end_date = (
                date_parser.parse(date_to) if date_to else datetime.now(timezone.utc)
            )

            # Make dates timezone-aware
            if start_date:
                start_date = self._make_timezone_aware(start_date)
            if end_date:
                end_date = self._make_timezone_aware(end_date)

            if start_date and end_date and start_date > end_date:
                raise ValueError("Start date must be before end date")

            return start_date, end_date
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid date format: {str(e)}")

    async def _process_batch(self, papers: List[arxiv.Result]) -> List[Dict[str, Any]]:
        """Process a batch of papers concurrently."""

        async def process_paper(paper: arxiv.Result) -> Dict[str, Any]:
            return {
                "id": paper.get_short_id(),
                "title": paper.title,
                "authors": [author.name for author in paper.authors],
                "abstract": paper.summary,
                "categories": paper.categories,
                "published": paper.published.isoformat(),
                "url": paper.pdf_url,
            }

        tasks = [process_paper(paper) for paper in papers]
        return await asyncio.gather(*tasks)

    async def search_papers(self, params: SearchParameters) -> ToolResponse:
        """Search for papers on arXiv with the given parameters."""
        try:
            max_results = min(int(params.max_results), 50)
            batch_size = min(int(params.batch_size), 20)

            start_date, end_date = self._validate_dates(
                params.date_from, params.date_to
            )

            # Build query with category filter if provided
            query = params.query
            if params.categories:
                category_filter = " OR ".join(f"cat:{cat}" for cat in params.categories)
                query = f"({query}) AND ({category_filter})"

            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
            )

            results = []
            current_batch = []

            for paper in self.client.results(search):
                # Ensure paper's published date is timezone-aware
                paper_date = self._make_timezone_aware(paper.published)

                if start_date and paper_date < start_date:
                    continue
                if end_date and paper_date > end_date:
                    continue

                current_batch.append(paper)

                if len(current_batch) >= batch_size:
                    batch_results = await self._process_batch(current_batch)
                    results.extend(batch_results)
                    current_batch = []

                    if len(results) >= max_results:
                        break

            # Process any remaining papers
            if current_batch:
                batch_results = await self._process_batch(current_batch)
                results.extend(batch_results)

            # Trim to max_results if needed
            results = results[:max_results]

            response_data = {"total_results": len(results), "papers": results}

            return ToolResponse(
                content_type="text", text=json.dumps(response_data, indent=2)
            )

        except Exception as e:
            logger.error(f"Error during paper search: {str(e)}")
            raise

    async def analyze_paper(self, paper_id: str) -> ToolResponse:
        """Get detailed analysis of a specific paper."""
        try:
            search = arxiv.Search(id_list=[paper_id])
            papers = list(self.client.results(search))

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
                "links": [link.href for link in paper.links],
            }

            return ToolResponse(
                content_type="text", text=json.dumps(analysis, indent=2)
            )

        except Exception as e:
            logger.error(f"Error analyzing paper: {str(e)}")
            raise


class ServiceFactory:
    """Factory for creating service instances."""

    @staticmethod
    def create_service() -> ArxivService:
        """Create and configure a new ArxivService instance."""
        return ArxivService()


async def main():
    """Main entry point for running the service directly."""
    service = ServiceFactory.create_service()

    try:
        # Search papers
        search_params = SearchParameters(
            query="attention is all you need", max_results=5
        )
        search_result = await service.search_papers(search_params)
        print("Search Results:")
        print(search_result.text)

        # Analyze specific paper
        analysis_result = await service.analyze_paper("1706.03762")
        print("\nPaper Analysis:")
        print(analysis_result.text)

    except Exception as e:
        logger.error(f"Error in main: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
