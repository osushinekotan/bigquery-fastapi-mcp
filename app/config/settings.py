import os

from dotenv import load_dotenv

load_dotenv(override=True)


# bigquery config
PROJECT_ID = os.getenv("BQ_PROJECT_ID", "")

# Set to None if BQ_ALLOWED_DATASETS is an empty string, None or ‘*’ (all allowed)
bq_allowed_datasets = os.getenv("BQ_ALLOWED_DATASETS", "")
ALLOWED_DATASETS: set[str] | None = (
    None
    if not bq_allowed_datasets or bq_allowed_datasets == "*"
    else {dataset.strip() for dataset in bq_allowed_datasets.split(",") if dataset.strip()}
)
MAX_BYTES_BILLED = int(os.getenv("BQ_MAX_BYTES_BILLED", "1073741824"))  # Default 1GB
ALLOWED_STATEMENTS: list[str] = ["SELECT"]

# qdrant config
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
EMBEDDING_MODEL_PROVIDER = os.getenv("EMBEDDING_MODEL_PROVIDER", "sentence-transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
EMBEDDING_SIZE = int(os.getenv("EMBEDDING_SIZE", "384"))

# app config
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = os.getenv("APP_PORT", "8000")
