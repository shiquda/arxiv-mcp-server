import pytest
from datetime import datetime, timedelta, timezone
import json

from arxiv_mcp_server.server import ArxivService, SearchParameters

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest.fixture
def service():
    return ArxivService()

@pytest.mark.anyio
async def test_basic_search(service):
    """Test basic paper search functionality."""
    params = SearchParameters(
        query="attention is all you need",
        max_results=1
    )
    result = await service.search_papers(params)
    
    assert result.content_type == "text"
    data = json.loads(result.text)
    
    assert "total_results" in data
    assert "papers" in data
    assert len(data["papers"]) <= 1
    
    paper = data["papers"][0]
    required_fields = ["id", "title", "authors", "abstract", "categories", "published", "url"]
    assert all(key in paper for key in required_fields)

@pytest.mark.anyio
async def test_date_filtered_search(service):
    """Test search with date filtering."""
    date_from = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
    params = SearchParameters(
        query="large language models",
        date_from=date_from,
        max_results=5
    )
    
    result = await service.search_papers(params)
    data = json.loads(result.text)
    papers = data["papers"]
    
    for paper in papers:
        paper_date = datetime.fromisoformat(paper["published"])
        paper_date = paper_date.replace(tzinfo=timezone.utc) if paper_date.tzinfo is None else paper_date
        assert paper_date >= datetime.fromisoformat(date_from).replace(tzinfo=timezone.utc)

@pytest.mark.anyio
async def test_batched_search(service):
    """Test batched paper processing."""
    params = SearchParameters(
        query="neural networks",
        max_results=15,
        batch_size=5
    )
    
    result = await service.search_papers(params)
    data = json.loads(result.text)
    
    assert len(data["papers"]) <= 15
    assert data["total_results"] <= 15

@pytest.mark.anyio
async def test_category_filtered_search(service):
    """Test search with category filtering."""
    params = SearchParameters(
        query="transformers",
        categories=["cs.AI", "cs.LG"],
        max_results=5
    )
    
    result = await service.search_papers(params)
    data = json.loads(result.text)
    papers = data["papers"]
    
    for paper in papers:
        paper_categories = set(paper["categories"])
        assert paper_categories.intersection({"cs.AI", "cs.LG"})

@pytest.mark.anyio
async def test_date_validation(service):
    """Test date validation functionality."""
    with pytest.raises(ValueError, match="Invalid date format"):
        params = SearchParameters(
            query="test",
            date_from="invalid-date"
        )
        await service.search_papers(params)
    
    with pytest.raises(ValueError, match="Start date must be before end date"):
        params = SearchParameters(
            query="test",
            date_from="2024-01-01",
            date_to="2023-01-01"
        )
        await service.search_papers(params)

@pytest.mark.anyio
async def test_analyze_paper(service):
    """Test paper analysis functionality."""
    result = await service.analyze_paper("1706.03762")
    assert result.content_type == "text"
    
    data = json.loads(result.text)
    assert isinstance(data, dict)
    
    required_fields = [
        "id", "title", "authors", "abstract", "categories",
        "published", "url", "primary_category"
    ]
    assert all(key in data for key in required_fields)

@pytest.mark.anyio
async def test_analyze_nonexistent_paper(service):
    """Test error handling for non-existent paper IDs."""
    with pytest.raises(ValueError, match="Paper not found"):
        await service.analyze_paper("0000.00000")