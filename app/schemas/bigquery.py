from typing import Any

from pydantic import BaseModel


class Dataset(BaseModel):
    dataset_id: str
    friendly_name: str | None = None


class Table(BaseModel):
    table_id: str
    dataset_id: str


class TableSchema(BaseModel):
    name: str
    type: str
    mode: str | None = None
    description: str | None = None


class ColumnDetails(BaseModel):
    column_name: str
    is_nullable: str
    data_type: str
    is_partitioning_column: str


class TableDetails(BaseModel):
    table_id: str
    dataset_id: str
    description: str | None = None
    columns: list[ColumnDetails] | None = None
    row_count: int | None = None
    size_bytes: int | None = None
    size_gbytes: float | None = None
    created: str | None = None
    last_modified: str | None = None


class QueryRequest(BaseModel):
    query: str
    dry_run: bool = True


class QueryResult(BaseModel):
    rows: list[dict[str, Any]]
    total_rows: int
    schemas: list[TableSchema]
    bytes_processed: int
    gbytes_processed: float
    job_id: str | None = None
    statement_type: str | None = None
    referenced_tables: list[str] | None = None
