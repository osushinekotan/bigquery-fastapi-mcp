from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from app.clients.bigquery import init_bigquery_client
from app.clients.embedding import EmbeddingClient
from app.clients.qdrant import init_qdrant_client
from app.config.settings import APP_HOST, APP_PORT
from app.routers import health, sequential_thinking
from app.routers.bigquery import datasets, query, tables
from app.routers.knowledge_base import collections, documents


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for the FastAPI application."""
    app.state.bigquery_client = init_bigquery_client()
    app.state.qdrant_client = init_qdrant_client()
    app.state.embedding_client = EmbeddingClient()
    app.state.embedding_client.build_model()
    yield


app = FastAPI(
    title="Servers",
    description="FastAPI for MCP Servers",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(datasets.router, prefix="/bigquery", tags=["bigquery"])
app.include_router(tables.router, prefix="/bigquery", tags=["bigquery"])
app.include_router(query.router, prefix="/bigquery", tags=["bigquery"])
app.include_router(collections.router, prefix="/knowledge-base", tags=["knowledge-base"])
app.include_router(documents.router, prefix="/knowledge-base", tags=["knowledge-base"])
app.include_router(sequential_thinking.router, prefix="/sequential-thinking", tags=["sequential-thinking"])

app.include_router(health.router, prefix="/health", tags=["system"])


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI for MCP Servers"}


mcp = FastApiMCP(
    app,  # Your FastAPI app
    name="Query FastAPI MCP",  # Name for the MCP server
    http_client=httpx.AsyncClient(
        timeout=60,
        base_url=f"http://{APP_HOST}:{APP_PORT}",
    ),  # HTTP client for the MCP server
    exclude_tags=[
        "system",
        "bigquery",
    ],  # Exclude tags from the MCP server
)
mcp.mount()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=APP_HOST, port=int(APP_PORT), reload=True)
