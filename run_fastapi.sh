#!/bin/bash
# Run FastAPI benchmark server
# Port: 8001

cd "$(dirname "$0")"

echo "Starting FastAPI on port 8001..."
exec uv run granian --interface asgi fastapi_app:app --host 0.0.0.0 --port 8001 --workers 1
