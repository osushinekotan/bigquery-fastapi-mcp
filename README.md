# BigQuery & Tavily FastAPI MCP

A lightweight, secure API & MCP for accessing and querying Google BigQuery datasets and Tavily search

## FastAPI

### Features

- Read-only access to BigQuery datasets and tables
- Security features including query validation and dataset access control
- Full support for standard BigQuery queries with cost control
- Tavily search and web content extraction capabilities
- RESTful API with comprehensive documentation

### Setup

#### Prerequisites

- Python 3.11 or higher
- Google Cloud Project with BigQuery enabled
- Service account with BigQuery access
- Tavily API key for search functionality

#### Installation

1. Clone the repository

```bash
git clone https://github.com/osushinekotan/bigquery-fastapi-mcp
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
TAVILY_API_KEY=your-tavily-api-key
APP_HOST=127.0.0.1
APP_PORT=8000
```

4. Set up GCP authentication

```bash
# Either set the environment variable
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json

# Or authenticate using gcloud
gcloud auth application-default login
```

### Running the Application

```bash
uv run uvicorn app.main:app --reload
```

or

```bash
uv run python -m app.main
```

The API will be available at http://localhost:8000

API documentation will be available at http://localhost:8000/docs

### API Endpoints

#### Health Check

- `GET /health/health` - Verify the API is running

#### BigQuery Datasets

- `GET /bigquery/list_datasets` - List all datasets in the project (filtered by allowed datasets)
- `GET /bigquery/allowed_datasets` - Get configured allowed datasets

#### BigQuery Tables

- `GET /bigquery/tables` - List all tables in allowed datasets
- `GET /bigquery/tables?dataset_id=your_dataset` - List tables in a specific dataset
- `GET /bigquery/tables/{dataset_id}/{table_id}` - Get detailed information about a specific table

#### BigQuery Query

- `POST /bigquery/query` - Execute a BigQuery query

Example request body:

```json
{
  "query": "SELECT * FROM `project.dataset.table` LIMIT 10",
  "dry_run": true
}
```

#### Tavily Search

- `POST /search/search` - Search the web using Tavily

Example request body:

```json
{
  "query": "latest developments in AI",
  "max_results": 5
}
```

#### Tavily Extract

- `POST /search/extract` - Extract content from web URLs

Example request body:

```json
{
  "urls": ["https://example.com/article1", "https://example.com/article2"]
}
```

### Security Features

- Read-only query validation (only SELECT statements are allowed)
- Dataset access control through environment configuration
- Maximum billable bytes limit with configurable thresholds

## MCP server

https://github.com/tadata-org/fastapi_mcp

### Connecting to the MCP Server using SSE

Once your FastAPI app with MCP integration is running, you can connect to it with any MCP client supporting SSE, such as Cursor:

1. Run your application.

2. In Cursor -> Settings -> MCP, use the URL of your MCP server endpoint (e.g., `http://localhost:8000/mcp`) as sse.

3. Cursor will discover all available tools and resources automatically.

### Connecting to the MCP Server using [mcp-proxy stdio](https://github.com/sparfenyuk/mcp-proxy?tab=readme-ov-file#1-stdio-to-sse)

If your MCP client does not support SSE, for example Claude Desktop:

1. Run your application.

2. Install [mcp-proxy](https://github.com/sparfenyuk/mcp-proxy?tab=readme-ov-file#installing-via-pypi), for example: `uv tool install mcp-proxy`.

3. Add in Claude Desktop MCP config file (`claude_desktop_config.json`):

On Windows:

```json
{
  "mcpServers": {
    "my-api-mcp-proxy": {
      "command": "mcp-proxy",
      "args": ["http://127.0.0.1:8000/mcp"]
    }
  }
}
```

On MacOS:

Find the path to mcp-proxy by running in Terminal: `which mcp-proxy`.

```json
{
  "mcpServers": {
    "my-api-mcp-proxy": {
      "command": "/Full/Path/To/Your/Executable/mcp-proxy",
      "args": ["http://127.0.0.1:8000/mcp"]
    }
  }
}
```

Find the path to mcp-proxy by running in Terminal: `which uvx`.

```json
{
  "mcpServers": {
    "my-api-mcp-proxy": {
      "command": "/Full/Path/To/Your/uvx",
      "args": ["mcp-proxy", "http://127.0.0.1:8000/mcp"]
    }
  }
}
```

4. Claude Desktop will discover all available tools and resources automatically
