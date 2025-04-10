from fastapi import APIRouter, HTTPException, Query

from app.config.settings import ALLOWED_DATASETS, PROJECT_ID
from app.schemas.bigquery import Table, TableDetails, TableSchema
from app.utils.bigquery_client import get_client

router = APIRouter()


@router.get("/tables", response_model=list[Table])
async def list_tables(dataset_id: str | None = Query(None, description="Filter tables by dataset ID")):
    """
    List tables in BigQuery project, optionally filtered by dataset.

    Args:
        dataset_id: Optional dataset ID to filter tables
    """
    try:
        client = get_client()

        # Check if dataset is allowed if filtering is applied
        if dataset_id and ALLOWED_DATASETS and dataset_id not in ALLOWED_DATASETS:
            raise HTTPException(status_code=403, detail=f"Access to dataset '{dataset_id}' is not allowed")

        tables = []

        # List tables based on dataset filter
        if dataset_id:
            dataset_ref = client.dataset(dataset_id)
            bq_tables = list(client.list_tables(dataset_ref))

            for table in bq_tables:
                tables.append(Table(table_id=table.table_id, dataset_id=dataset_id))
        else:
            # If no dataset specified, list tables from all allowed datasets
            datasets_to_query = (
                ALLOWED_DATASETS if ALLOWED_DATASETS else [ds.dataset_id for ds in client.list_datasets()]
            )

            for ds_id in datasets_to_query:
                dataset_ref = client.dataset(ds_id)
                bq_tables = list(client.list_tables(dataset_ref))

                for table in bq_tables:
                    tables.append(Table(table_id=table.table_id, dataset_id=ds_id))

        return tables
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")


@router.get("/tables/{dataset_id}/{table_id}", response_model=TableDetails)
async def describe_table(dataset_id: str, table_id: str):
    """
    Get detailed information about a specific table using INFORMATION_SCHEMA.

    Args:
        dataset_id: Dataset ID
        table_id: Table ID
    """
    try:
        # Check if dataset is allowed
        if ALLOWED_DATASETS and dataset_id not in ALLOWED_DATASETS:
            raise HTTPException(status_code=403, detail=f"Access to dataset '{dataset_id}' is not allowed")

        client = get_client()

        # Query INFORMATION_SCHEMA.TABLES for table metadata
        schema_query = f"""
        SELECT
          table_name,
          table_type,
          creation_time,
          last_modified_time,
          row_count,
          size_bytes,
          description
        FROM
          `{PROJECT_ID}.{dataset_id}.INFORMATION_SCHEMA.TABLES`
        WHERE
          table_name = '{table_id}'
        """

        table_info = None
        for row in client.query(schema_query).result():
            table_info = row
            break

        if not table_info:
            raise HTTPException(status_code=404, detail=f"Table {dataset_id}.{table_id} not found")

        # Get table schema
        table_ref = client.dataset(dataset_id).table(table_id)
        table = client.get_table(table_ref)

        schema = []
        for field in table.schema:
            schema.append(
                TableSchema(name=field.name, type=field.field_type, mode=field.mode, description=field.description)
            )

        # Create response object
        table_details = TableDetails(
            table_id=table_id,
            dataset_id=dataset_id,
            description=table_info.description,
            schema=schema,
            row_count=table_info.row_count,
            size_bytes=table_info.size_bytes,
            created=table_info.creation_time.isoformat() if table_info.creation_time else None,
            last_modified=table_info.last_modified_time.isoformat() if table_info.last_modified_time else None,
        )

        return table_details

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error describing table: {str(e)}")
