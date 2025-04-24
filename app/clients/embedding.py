from fastapi import Request
from sentence_transformers import SentenceTransformer

from app.config.settings import EMBEDDING_MODEL, EMBEDDING_MODEL_PROVIDER


class EmbeddingClient:
    """
    EmbeddingClient is a wrapper around the SentenceTransformer model.
    It provides methods to initialize the model and get embeddings for text.
    """

    def __init__(
        self,
        model_name: str = EMBEDDING_MODEL,
        model_provider: str = EMBEDDING_MODEL_PROVIDER,
    ):
        self.model_name = model_name
        self.model_provider = model_provider

    def build_model(self):
        """
        Build the embedding model.
        """
        if self.model_provider == "sentence-transformers":
            self.model = SentenceTransformer(self.model_name)
        else:
            raise ValueError(f"Unsupported embedding model provider: {self.model_provider}")

    def embed(self, text: str) -> list[float]:
        if self.model_provider == "sentence-transformers":
            return self.model.encode(text).tolist()
        else:
            raise ValueError(f"Unsupported embedding model provider: {self.model_provider}")


def get_embedding_client(request: Request) -> EmbeddingClient:
    """
    Get the embedding model from the request state.

    Returns:
        SentenceTransformer: The embedding model.
    """
    return request.app.state.embedding_client
