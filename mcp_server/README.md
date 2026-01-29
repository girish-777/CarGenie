## CarGenie MCP Server

This folder contains a **Model Context Protocol (MCP)** server that exposes CarGenie backend capabilities as callable tools (for MCP hosts like Cursor/Claude Desktop).

### What it does

- Runs as a separate process.
- Communicates over **stdin/stdout** using JSON-RPC style messages.
- Calls your local FastAPI backend (default: `http://localhost:8000`) to fulfill tool requests.

### Tools exposed

- **`search_cars`**: Calls `GET /api/v1/cars/` with filters.
- **`get_car_details`**: Calls `GET /api/v1/cars/{car_id}`.
- **`get_recommendations`**: Calls `GET /api/v1/recommendations?n_results=...` (optionally with auth).

### Prerequisites

- Backend running locally:
  - `python -m uvicorn app.main:app --reload` (from `backend/`)
- Install dependencies:
  - `pip install -r requirements.txt`

### Configuration

The MCP server reads:

- **`CARGENIE_BACKEND_URL`** (optional)
  - default: `http://localhost:8000`

Example:

```bash
set CARGENIE_BACKEND_URL=http://localhost:8000
```

### Run

From the repo root:

```bash
python -m mcp_server
```

Or:

```bash
python -m mcp_server.server
```

### Notes

- If you pass a `user_token` argument to tools that support it, the server forwards it as:
  - `Authorization: Bearer <token>`
- Keep this server **local** unless you add authentication + hardening.

