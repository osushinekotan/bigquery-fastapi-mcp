from fastapi import APIRouter, Depends, HTTPException, Query
from google.cloud import bigquery

from app.clients.bigquery import get_bigquery_client
from app.config.settings import ALLOWED_DATASETS, PROJECT_ID
from app.schemas.bigquery import ColumnDetails, Table, TableDetails

router = APIRouter()


@router.get("/tables", response_model=list[Table], operation_id="list_bigquery_tables")
async def list_tables(
    dataset_id: str | None = Query(None, description="Filter tables by dataset ID"),
    client: bigquery.Client = Depends(get_bigquery_client),
):
    """
    List tables in BigQuery project, optionally filtered by dataset.

    Args:
        dataset_id: Optional dataset ID to filter tables
    """
    try:
        # Check if dataset is allowed if filtering is applied
        if dataset_id and ALLOWED_DATASETS is not None and dataset_id not in ALLOWED_DATASETS:
            raise HTTPException(status_code=403, detail=f"Access to dataset '{dataset_id}' is not allowed")

        tables = []

        # List tables based on dataset filter
        if dataset_id:
            dataset_ref = client.dataset(dataset_id)
            bq_tables = list(client.list_tables(dataset_ref))
            print(f"# bq_tables: {len(bq_tables)}")

            for table in bq_tables:
                tables.append(Table(table_id=table.table_id, dataset_id=dataset_id))
        else:
            # If no dataset specified, list tables from all allowed datasets
            datasets_to_query = (
                ALLOWED_DATASETS if ALLOWED_DATASETS is not None else [ds.dataset_id for ds in client.list_datasets()]
            )

            for ds_id in datasets_to_query:
                dataset_ref = client.dataset(ds_id)
                bq_tables = list(client.list_tables(dataset_ref))
                print(f"# bq_tables: {len(bq_tables)}")

                for table in bq_tables:
                    tables.append(Table(table_id=table.table_id, dataset_id=ds_id))

        return tables
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error listing tables: {str(e)}")


@router.get("/tables/{dataset_id}/{table_id}", response_model=TableDetails, operation_id="describe_bigquery_table")
async def describe_table(dataset_id: str, table_id: str, client: bigquery.Client = Depends(get_bigquery_client)):
    """
    Get detailed information about a specific table using INFORMATION_SCHEMA.

    Args:
        dataset_id: Dataset ID
        table_id: Table ID
    """
    try:
        # Check if dataset is allowed
        if ALLOWED_DATASETS is not None and dataset_id not in ALLOWED_DATASETS:
            raise HTTPException(status_code=403, detail=f"Access to dataset '{dataset_id}' is not allowed")

        # Query INFORMATION_SCHEMA.TABLES for table metadata
        schema_query = f"""
        SELECT
          DATE(TIMESTAMP_MILLIS(creation_time)) AS creation_date,
          DATE(TIMESTAMP_MILLIS(last_modified_time)) AS last_modified_date,
          row_count,
          size_bytes
        FROM
          `{PROJECT_ID}.{dataset_id}.__TABLES__`
        WHERE
          table_id = '{table_id}'
        """

        table_info = None
        for row in client.query(schema_query).result():
            table_info = row
            break

        if not table_info:
            raise HTTPException(status_code=404, detail=f"Table {dataset_id}.{table_id} not found")

        # Get column details
        column_query = f"""
        SELECT
            column_name,
            is_nullable,
            data_type,
            is_partitioning_column
        FROM `{PROJECT_ID}.{dataset_id}`.INFORMATION_SCHEMA.COLUMNS
        WHERE table_name = '{table_id}'
        """
        column_details = client.query(column_query).result()
        columns = []
        for row in column_details:
            columns.append(
                ColumnDetails(
                    column_name=row.column_name,
                    is_nullable=row.is_nullable,
                    data_type=row.data_type,
                    is_partitioning_column=row.is_partitioning_column,
                )
            )

        # Create response object
        table_details = TableDetails(
            table_id=table_id,
            dataset_id=dataset_id,
            columns=columns,
            row_count=table_info.row_count,
            size_bytes=table_info.size_bytes,
            size_gbytes=table_info.size_bytes / (1024 * 1024 * 1024),
            created=str(table_info.creation_date) if table_info.creation_date else None,
            last_modified=str(table_info.last_modified_date) if table_info.last_modified_date else None,
        )

        return table_details

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error describing table: {str(e)}")
