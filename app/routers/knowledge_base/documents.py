import uuid

from fastapi import APIRouter, Depends, HTTPException
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.clients.embedding import get_embedding_client
from app.clients.qdrant import get_qdrant_client
from app.schemas.knowledge_base import Document, DocumentResponse, SearchRequest, SearchResponse

router = APIRouter()


@router.post("/{collection_name}/documents", response_model=Document, operation_id="add_document")
async def add_document(
    collection_name: str,
    document: Document,
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
    embedding_client=Depends(get_embedding_client),
):
    """
    Add a document to the knowledge base.

    Args:
        document: Document to be added
    """
    try:
        payload = {"text": document.text}
        if document.metadata is not None:
            payload["metadata"] = document.metadata

        document_id = str(uuid.uuid4())
        vector = embedding_client.embed(document.text)
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=document_id,
                    vector=vector,
                    payload=payload,
                )
            ],
        )

        return document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding document: {str(e)}")


@router.post("/{collection_name}/search", response_model=SearchResponse, operation_id="search_documents")
async def search_documents(
    collection_name: str,
    request: SearchRequest,
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
    embedding_client=Depends(get_embedding_client),
):
    """
    Search for documents in the knowledge base.

    Args:
        request: Search request containing the query and optional filters
    """
    try:
        query_vector = embedding_client.embed(request.query)
        search_params = {"collection_name": collection_name, "query_vector": query_vector, "limit": request.limit}

        if request.filter is not None:
            filter_conditions = []
            for key, value in request.filter.items():
                filter_conditions.append(
                    models.FieldCondition(key=f"metadata.{key}", match=models.MatchValue(value=value))
                )

            if filter_conditions:
                search_params["filter"] = models.Filter(must=filter_conditions)

        search_results = qdrant_client.search(**search_params)

        documents = []
        for result in search_results:
            print(f"# result: {result}")
            doc = DocumentResponse(
                id=result.id,
                text=result.payload.get("text", ""),
                metadata=result.payload.get("metadata", {}),
                score=result.score,
            )
            documents.append(doc)

        return SearchResponse(results=documents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching documents: {str(e)}")


@router.delete("/{collection_name}/documents/{document_id}", operation_id="delete_document")
async def delete_document(
    collection_name: str,
    document_id: str,
    qdrant_client: QdrantClient = Depends(get_qdrant_client),
):
    """
    Delete a document from the knowledge base.

    Args:
        document_id: ID of the document to be deleted
    """
    try:
        qdrant_client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=[document_id]),
        )
        return {"status": "success", "message": f"Document '{document_id}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")
