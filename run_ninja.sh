#!/bin/bash
# Run Django Ninja benchmark server
# Port: 8003

cd "$(dirname "$0")"

echo "Starting Django Ninja on port 8003..."
exec uvicorn django_project.asgi:application --host 0.0.0.0 --port 8003 --workers 1 --no-access-log
