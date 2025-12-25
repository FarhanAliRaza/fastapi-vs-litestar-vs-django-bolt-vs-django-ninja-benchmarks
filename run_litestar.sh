#!/bin/bash
# Run Litestar benchmark server
# Port: 8002

cd "$(dirname "$0")"

echo "Starting Litestar on port 8002..."
exec uvicorn litestar_app:app --host 0.0.0.0 --port 8002 --workers 1 --no-access-log
