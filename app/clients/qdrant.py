from fastapi import Request
from qdrant_client import QdrantClient

from app.config.settings import QDRANT_HOST, QDRANT_PORT


def init_qdrant_client():
    """
    Initializes the Qdrant client.

    Returns:
        QdrantClient: The initialized Qdrant client.
    """
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)


def get_qdrant_client(request: Request) -> QdrantClient:
    """
    Get the Qdrant client from the request state.

    Args:
        request (Request): The FastAPI request object.

    Returns:
        QdrantClient: The Qdrant client.
    """
    return request.app.state.qdrant_client
