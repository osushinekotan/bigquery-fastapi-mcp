from google.cloud import bigquery

from app.config.settings import PROJECT_ID


def get_client() -> bigquery.Client:
    """
    Creates and returns a BigQuery client

    Returns:
        bigquery.Client: BigQuery client instance
    """
    return bigquery.Client(project=PROJECT_ID)
