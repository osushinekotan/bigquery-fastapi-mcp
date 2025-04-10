from fastapi import APIRouter, HTTPException
from google.cloud import bigquery

from app.config.settings import ALLOWED_DATASETS, MAX_BYTES_BILLED
from app.schemas.bigquery import QueryRequest, QueryResult, TableSchema
from app.utils.bigquery_client import get_client
from app.utils.query_validator import is_read_only_query, validate_dataset_references

router = APIRouter()


@router.post("/query", response_model=QueryResult)
async def execute_query(query_request: QueryRequest):
    """
    Execute a BigQuery query with validation.

    Args:
        query_request: The query request containing the SQL and options
    """
    try:
        # Validate query is read-only
        is_valid, reason = is_read_only_query(query_request.query)
        if not is_valid:
            raise HTTPException(status_code=403, detail=f"Query validation failed: {reason}")

        # Validate dataset references
        if ALLOWED_DATASETS:
            is_valid, reason = validate_dataset_references(query_request.query, ALLOWED_DATASETS)
            if not is_valid:
                raise HTTPException(status_code=403, detail=f"Dataset validation failed: {reason}")

        client = get_client()

        # Configure job options
        job_config = bigquery.QueryJobConfig()
        job_config.maximum_bytes_billed = MAX_BYTES_BILLED
        if query_request.dry_run:
            job_config.dry_run = True

        # Execute the query
        query_job = client.query(query_request.query, job_config=job_config)

        if query_request.dry_run:
            # For dry run, return estimated bytes
            return QueryResult(
                rows=[],
                total_rows=0,
                schema=[],
                bytes_processed=query_job.total_bytes_processed,
                job_id=query_job.job_id,
            )

        # Wait for the query to complete
        results = query_job.result()

        # Extract schema information
        schema = []
        for field in results.schema:
            schema.append(
                TableSchema(name=field.name, type=field.field_type, mode=field.mode, description=field.description)
            )

        # Convert results to dicts
        rows = [dict(row.items()) for row in results]

        # Return formatted results
        return QueryResult(
            rows=rows,
            total_rows=len(rows),
            schema=schema,
            bytes_processed=query_job.total_bytes_processed,
            job_id=query_job.job_id,
        )

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Error executing query: {str(e)}")
