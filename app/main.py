from fastapi import FastAPI

from app.routers import datasets, query, tables

app = FastAPI(
    title="BigQuery API",
    description="API for interacting with Google BigQuery",
    version="0.1.0",
)

app.include_router(datasets.router, prefix="/bigquery", tags=["datasets"])
app.include_router(tables.router, prefix="/bigquery", tags=["tables"])
app.include_router(query.router, prefix="/bigquery", tags=["query"])


@app.get("/")
async def root():
    return {"message": "Welcome to BigQuery FastAPI"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
