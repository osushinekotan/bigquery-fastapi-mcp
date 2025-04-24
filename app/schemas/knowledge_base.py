from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    text: str = Field(..., description="Document text content")
    metadata: dict[str, Any] | None = Field(
        None, description="Metadata about the document in key-value pairs. Optional."
    )


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(10, description="Maximum number of documents to return")
    filter: dict[str, Any] | None = Field(
        None,
        description="Filter based on metadata. 'metadata' is a dictionary with key-value pairs, "
        "e.g., {'metadata': {'publish_date': '2023-05-20'}}",
    )


class DocumentResponse(BaseModel):
    id: str = Field(..., description="Document ID")
    text: str = Field(..., description="Document text content")
    metadata: dict[str, Any] | None = Field(
        None, description="Metadata about the document in key-value pairs. Optional."
    )
    score: float = Field(..., description="Similarity score of the document in the search results.")


class SearchResponse(BaseModel):
    results: list[DocumentResponse] = Field(..., description="Search result documents")


class CollectionInfo(BaseModel):
    name: str
    vector_size: int
    document_count: int
    created_at: datetime | None = None
