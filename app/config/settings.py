import os

from dotenv import load_dotenv

load_dotenv(override=True)

PROJECT_ID = os.getenv("BQ_PROJECT_ID", "")
ALLOWED_DATASETS: set[str] = {
    dataset.strip() for dataset in os.getenv("BQ_ALLOWED_DATASETS", "").split(",") if dataset.strip()
}
MAX_BYTES_BILLED = int(os.getenv("BQ_MAX_BYTES_BILLED", "1073741824"))  # Default 1GB

ALLOWED_STATEMENTS: list[str] = ["SELECT"]
