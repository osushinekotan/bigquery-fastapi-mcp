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

## Running the Application

**local**

```bash
docker compose up qdrant
uv run uvicorn app.main:app --reload
```

or

```bash
docker compose up qdrant
uv run python -m app.main
```

## MCP Client

### open-webui

https://docs.openwebui.com/

```bash
DATA_DIR=~/.open-webui uvx --python 3.11 open-webui@latest serve
```

or

```bash
docker run -d -p 8080:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui --restart always ghcr.io/open-webui/open-webui:main
```

Open WebUI at http://localhost:8080

run `mcpo`

```bash
uvx mcpo --port 8000 --server-type "sse" -- http://127.0.0.1:8001/mcp
```
