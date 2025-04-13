import os

from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("BQ_PROJECT_ID", "")

# Set to None if BQ_ALLOWED_DATASETS is an empty string, None or ‘*’ (all allowed)
bq_allowed_datasets = os.getenv("BQ_ALLOWED_DATASETS", "")
BQ_ALLOWED_DATASETS: set[str] | None = (
    None
    if not bq_allowed_datasets or bq_allowed_datasets == "*"
    else {dataset.strip() for dataset in bq_allowed_datasets.split(",") if dataset.strip()}
)
MAX_BYTES_BILLED = int(os.getenv("BQ_MAX_BYTES_BILLED", "1073741824"))  # Default 1GB

ALLOWED_STATEMENTS: list[str] = ["SELECT"]

# TAVILY API
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# app config
MCP_BASE_URL = os.getenv("MCP_BASE_URL")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = os.getenv("APP_PORT", "8000")
