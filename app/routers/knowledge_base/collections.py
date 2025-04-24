from fastapi import APIRouter, Depends, HTTPException
from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.clients.qdrant import get_qdrant_client
from app.config.settings import EMBEDDING_SIZE
from app.schemas.knowledge_base import CollectionInfo

router = APIRouter()


@router.post("/collections/{collection_name}", operation_id="create_collection")
async def create_collection(collection_name: str, client: QdrantClient = Depends(get_qdrant_client)):
    """
    Create a new collection in Qdrant.

    Args:
        collection_name: Name of the collection to create
    """
    try:
        collections = client.get_collections().collections
        if any(collection.name == collection_name for collection in collections):
            raise HTTPException(status_code=400, detail=f"'{collection_name}' is already exists")

        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=EMBEDDING_SIZE,
                distance=models.Distance.COSINE,
            ),
        )

        return {"status": "success", "message": f"Collection '{collection_name}' created successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error creating collection: {str(e)}")


@router.get("/collections", response_model=list[CollectionInfo], operation_id="list_collections")
async def list_collections(client: QdrantClient = Depends(get_qdrant_client)):
    """
    List all collections in Qdrant.
    """
    try:
        collections_info = []
        collections = client.get_collections().collections

        for collection in collections:
            collection_info = client.get_collection(collection_name=collection.name)

            try:
                count_result = client.count(collection_name=collection.name)
                count = count_result.count
            except Exception:
                count = 0

            collections_info.append(
                CollectionInfo(
                    name=collection.name, vector_size=collection_info.config.params.vectors.size, document_count=count
                )
            )

        return collections_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")


@router.delete("/collections/{collection_name}", operation_id="delete_collection")
async def delete_collection(collection_name: str, client: QdrantClient = Depends(get_qdrant_client)):
    """
    Delete a collection in Qdrant.

    Args:
        collection_name: Name of the collection to delete
    """
    try:
        client.delete_collection(collection_name=collection_name)
        return {"status": "success", "message": f"Collection '{collection_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting collection: {str(e)}")
