# BigQuery FastAPI MCP

## Setup

### Prerequisites

- Python 3.11 or higher
- Google Cloud Project with BigQuery enabled
- Service account with BigQuery access

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/bigquery-fastapi-mcp.git
cd bigquery-fastapi-mcp
```

2. Install dependencies

```bash
uv sync
```

3. Create a `.env` file with your configuration

```
BQ_PROJECT_ID=your-gcp-project-id
BQ_ALLOWED_DATASETS=dataset1,dataset2,dataset3
BQ_MAX_BYTES_BILLED=1073741824  # 1GB default
```

4. Set up GCP authentication

```bash
# Either set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Or authenticate using gcloud
gcloud auth application-default login
```

## Running the Application

```bash
uv run uvicorn app.main:app --reload
```

or

```bash
uv run python -m app.main
```

The API will be available at http://localhost:8000

API documentation will be available at http://localhost:8000/docs

## API Endpoints

### Datasets

- `GET /bigquery/datasets` - List all datasets in the project (filtered by allowed datasets)

### Tables

- `GET /bigquery/tables` - List all tables in allowed datasets
- `GET /bigquery/tables?dataset_id=your_dataset` - List tables in a specific dataset
- `GET /bigquery/tables/{dataset_id}/{table_id}` - Get detailed information about a specific table

### Query

- `POST /bigquery/query` - Execute a BigQuery query

Example request body:

```json
{
  "query": "SELECT * FROM `project.dataset.table` LIMIT 10",
  "max_bytes_billed": 1073741824,
  "execute": true
}
```

## Security Features

- Read-only query validation
- Dataset access control
- Maximum billable bytes limit

## Development

The application follows modern Python 3.11 typing conventions and is structured with clean separation of concerns.
