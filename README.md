# FastAPI for MCP Servers

## Setup

1. Clone the repository

```bash
git clone https://github.com/osushinekotan/fastapi-mcp-servers
cd fastapi-mcp-servers
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
