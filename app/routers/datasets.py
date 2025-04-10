from fastapi import APIRouter, HTTPException

from app.config.settings import ALLOWED_DATASETS
from app.schemas.bigquery import Dataset
from app.utils.bigquery_client import get_client

router = APIRouter()


@router.get("/datasets", response_model=list[Dataset])
async def list_datasets():
    """
    List all datasets in the BigQuery project.

    If ALLOWED_DATASETS is configured, only returns those datasets.
    """
    try:
        client = get_client()
        datasets = list(client.list_datasets())
        print(f"# datasets: {len(datasets)}")

        if not datasets:
            return []

        result = []
        for dataset in datasets:
            dataset_id = dataset.dataset_id

            # Filter by allowed datasets if configured
            if ALLOWED_DATASETS and dataset_id not in ALLOWED_DATASETS:
                continue

            result.append(Dataset(dataset_id=dataset_id, friendly_name=dataset.friendly_name))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing datasets: {str(e)}")


@router.get("/datasets/allowed_datasets", response_model=list[Dataset])
def get_allowed_datasets():
    """
    Returns the allowed datasets configured in the environment.
    """
    try:
        if not ALLOWED_DATASETS:
            return []

        result = []
        for dataset_id in ALLOWED_DATASETS:
            result.append(Dataset(dataset_id=dataset_id))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving allowed datasets: {str(e)}")
