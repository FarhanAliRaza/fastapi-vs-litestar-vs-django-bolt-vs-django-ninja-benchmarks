#!/bin/bash
# Run Django Bolt benchmark server
# Port: 8004

cd "$(dirname "$0")"

echo "Starting Django Bolt on port 8004..."
exec python manage.py runbolt --host 0.0.0.0 --port 8004 --processes 1
