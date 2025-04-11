import httpx
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

from app.config.settings import APP_HOST, APP_PORT, MCP_BASE_URL
from app.routers import datasets, health, query, tables

app = FastAPI(
    title="Read Only BigQuery API",
    description="API for querying BigQuery datasets and tables",
    version="0.1.0",
)

app.include_router(datasets.router, prefix="/bigquery", tags=["datasets"])
app.include_router(tables.router, prefix="/bigquery", tags=["tables"])
app.include_router(query.router, prefix="/bigquery", tags=["query"])
app.include_router(health.router, prefix="/bigquery", tags=["health"])


@app.get("/")
async def root():
    return {"message": "Welcome to BigQuery FastAPI"}


# Add MCP server to the FastAPI app
mcp = FastApiMCP(
    app,  # Your FastAPI app
    name="BigQuery FastAPI MCP",  # Name for the MCP server
    base_url=MCP_BASE_URL or f"http://{APP_HOST}:{APP_PORT}",  # Base URL for the MCP server
    http_client=httpx.AsyncClient(timeout=60),
)
mcp.mount()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=APP_HOST, port=int(APP_PORT), reload=True)
