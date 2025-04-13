from typing import Any

from pydantic import BaseModel, Field


class TavilySearchRequest(BaseModel):
    query: str
    max_results: int = 5
    # TODO: consider removing these options
    # include_answer: bool = True
    # include_raw_content: bool = False
    # include_images: bool = False
    # search_depth: str = "basic"


class TavilyExtractRequest(BaseModel):
    urls: list[str]
    # include_images: bool = False


class TavilySearchResult(BaseModel):
    query: str
    results: list[dict[str, Any]] = Field(default_factory=list)
    # images: list[dict[str, Any]] | None = Field(default_factory=list)
    # answer: str | None = None
    # follow_up_questions: list[str] | None = None


class TavilyExtractResult(BaseModel):
    results: list[dict[str, Any]] = Field(default_factory=list)
