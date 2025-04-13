from fastapi import APIRouter, HTTPException

from app.schemas.search import (
    TavilyExtractRequest,
    TavilyExtractResult,
    TavilySearchRequest,
    TavilySearchResult,
)
from app.utils.tavily_client import get_client

router = APIRouter()


@router.post("/search", response_model=TavilySearchResult)
async def search(request: TavilySearchRequest):
    """
    Search the web using Tavily search API

    Args:
        request: The search request containing query and options
    """
    try:
        client = get_client()

        response = client.search(
            query=request.query,
            max_results=request.max_results,
            include_answer=request.include_answer,
            include_raw_content=request.include_raw_content,
            include_images=request.include_images,
            search_depth=request.search_depth,
        )

        return TavilySearchResult(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


@router.post("/extract", response_model=list[TavilyExtractResult])
async def extract(request: TavilyExtractRequest):
    """
    Extract content from URLs using Tavily extract API

    Args:
        request: The extract request containing URLs and options
    """
    try:
        client = get_client()

        params = {
            "urls": request.urls,
            "include_raw_content": request.include_raw_content,
        }

        if request.max_tokens:
            params["max_tokens"] = request.max_tokens

        results = client.extract(**params)

        if not isinstance(results, list):
            results = [results]

        return [TavilyExtractResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting content: {str(e)}")
