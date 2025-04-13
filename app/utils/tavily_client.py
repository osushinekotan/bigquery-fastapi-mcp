from functools import lru_cache

from tavily import TavilyClient

from app.config.settings import TAVILY_API_KEY


@lru_cache
def get_client() -> TavilyClient:
    """
    Creates and returns a Tavily client

    Returns:
        TavilyClient: Tavily client instance
    """
    return TavilyClient(api_key=TAVILY_API_KEY)
