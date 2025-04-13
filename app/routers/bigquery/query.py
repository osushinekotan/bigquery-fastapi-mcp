from fastapi import APIRouter, HTTPException
from google.cloud import bigquery

from app.config.settings import ALLOWED_DATASETS, ALLOWED_STATEMENTS, MAX_BYTES_BILLED
from app.schemas.bigquery import QueryRequest, QueryResult, TableSchema
from app.utils.bigquery_client import get_client

router = APIRouter()


@router.post("/query", response_model=QueryResult)
async def execute_query(query_request: QueryRequest):
    """
    Validate a BigQuery query and optionally execute it.

    Args:
        query_request: The query request containing the SQL and options
    """
    try:
        client = get_client()

        # Always run as dry_run first to validate
        dry_run_job = client.query(
            query_request.query,
            job_config=bigquery.QueryJobConfig(
                dry_run=True,
                use_query_cache=False,
                maximum_bytes_billed=MAX_BYTES_BILLED,
            ),
        )

        # Get statement type and validate if read-only
        statement_type = dry_run_job.statement_type
        if statement_type not in ALLOWED_STATEMENTS:
            raise HTTPException(
                status_code=403,
                detail=f"Query validation failed: Only SELECT queries are allowed. Found: {statement_type}",
            )

        # Get referenced tables and validate allowed datasets
        referenced_tables = dry_run_job.referenced_tables
        if ALLOWED_DATASETS is not None:
            for table in referenced_tables:
                if table.dataset_id not in ALLOWED_DATASETS:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Dataset validation failed: Access to dataset '{table.dataset_id}' is not allowed",
                    )

        # If dry_run=True, return the dry run job result
        if query_request.dry_run is True:
            return QueryResult(
                rows=[],
                total_rows=0,
                schemas=[],
                bytes_processed=dry_run_job.total_bytes_processed,
                gbytes_processed=dry_run_job.total_bytes_processed / (1024 * 1024 * 1024),
                job_id=dry_run_job.job_id,
                referenced_tables=[f"{t.project}.{t.dataset_id}.{t.table_id}" for t in referenced_tables],
                statement_type=statement_type,
            )

        # If dry_run=False, run the actual query
        query_job = client.query(
            query_request.query,
            job_config=bigquery.QueryJobConfig(maximum_bytes_billed=MAX_BYTES_BILLED),
        )

        # Wait for the query to complete
        results = query_job.result()

        # Extract schema information
        schemas = []
        for field in results.schema:
            schemas.append(
                TableSchema(name=field.name, type=field.field_type, mode=field.mode, description=field.description)
            )

        # Convert results to dicts
        rows = [dict(row.items()) for row in results]

        # Return formatted results
        return QueryResult(
            rows=rows,
            total_rows=len(rows),
            schemas=schemas,
            bytes_processed=query_job.total_bytes_processed,
            gbytes_processed=dry_run_job.total_bytes_processed / (1024 * 1024 * 1024),
            job_id=query_job.job_id,
            referenced_tables=[f"{t.project}.{t.dataset_id}.{t.table_id}" for t in referenced_tables],
            statement_type=statement_type,
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")
