from fastapi import Request
from google.cloud import bigquery

from app.config.settings import PROJECT_ID


def init_bigquery_client():
    """
    Initializes the BigQuery client.

    This function is called when the application starts to ensure that the BigQuery client
    is ready for use throughout the application.

    Returns:
        bigquery.Client: The initialized BigQuery client.
    """
    return bigquery.Client(project=PROJECT_ID)


def get_bigquery_client(request: Request) -> bigquery.Client:
    return request.app.state.bigquery_client
