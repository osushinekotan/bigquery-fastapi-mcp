from fastapi import APIRouter, Depends, HTTPException
from google.cloud import bigquery

from app.clients.bigquery import get_bigquery_client
from app.config.settings import ALLOWED_DATASETS
from app.schemas.bigquery import Dataset

router = APIRouter()


@router.get("/list_datasets", response_model=list[Dataset], operation_id="list_bigquery_datasets")
def list_datasets(client: bigquery.Client = Depends(get_bigquery_client)):
    """
    List all datasets in the BigQuery project.

    If ALLOWED_DATASETS is configured, only returns those datasets.
    """
    try:
        datasets = list(client.list_datasets())
        print(f"# datasets: {len(datasets)}")

        if not datasets:
            return []

        result = []
        for dataset in datasets:
            dataset_id = dataset.dataset_id

            # Filter by allowed datasets if configured
            if ALLOWED_DATASETS is not None and dataset_id not in ALLOWED_DATASETS:
                continue

            result.append(Dataset(dataset_id=dataset_id, friendly_name=dataset.friendly_name))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing datasets: {str(e)}")


@router.get("/allowed_datasets", response_model=list[Dataset], operation_id="get_allowed_bigquery_datasets")
def get_allowed_datasets():
    """
    Returns the allowed datasets configured in the environment.
    """
    try:
        if not ALLOWED_DATASETS:
            return [Dataset(dataset_id="*", friendly_name="All datasets allowed")]

        result = []
        for dataset_id in ALLOWED_DATASETS:
            result.append(Dataset(dataset_id=dataset_id))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving allowed datasets: {str(e)}")
