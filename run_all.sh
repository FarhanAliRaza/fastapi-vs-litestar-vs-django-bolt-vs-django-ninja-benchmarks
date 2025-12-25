#!/bin/bash
# Run all benchmark servers and execute benchmark
# This script manages all server processes

set -e

cd "$(dirname "$0")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# PID file to track servers
PID_FILE=".benchmark_pids"

cleanup() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    if [ -f "$PID_FILE" ]; then
        while read pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
    echo -e "${GREEN}Cleanup complete${NC}"
}

trap cleanup EXIT INT TERM

echo -e "${GREEN}=== Framework Benchmark ===${NC}"
echo ""

# Check if bombardier is installed
if ! command -v bombardier &> /dev/null; then
    echo -e "${RED}ERROR: bombardier not found${NC}"
    echo "Install with: go install github.com/codesenberg/bombardier@latest"
    exit 1
fi

# Clear old PIDs
rm -f "$PID_FILE"

# Start FastAPI
echo -e "${YELLOW}Starting FastAPI on port 8001...${NC}"
uv run uvicorn fastapi_app:app --host 0.0.0.0 --port 8001 --workers 1 --no-access-log &
echo $! >> "$PID_FILE"

# Start Litestar
echo -e "${YELLOW}Starting Litestar on port 8002...${NC}"
uv run uvicorn litestar_app:app --host 0.0.0.0 --port 8002 --workers 1 --no-access-log &
echo $! >> "$PID_FILE"

# Start Django Ninja
echo -e "${YELLOW}Starting Django Ninja on port 8003...${NC}"
uv run uvicorn django_project.asgi:application --host 0.0.0.0 --port 8003 --workers 1 --no-access-log &
echo $! >> "$PID_FILE"

# Start Django Bolt
echo -e "${YELLOW}Starting Django Bolt on port 8004...${NC}"
uv run python manage.py runbolt --host 0.0.0.0 --port 8004 --processes 1 &
echo $! >> "$PID_FILE"

# Wait for servers to start
echo ""
echo -e "${YELLOW}Waiting for servers to start...${NC}"
sleep 5

# Verify servers are running
check_server() {
    local name=$1
    local port=$2
    local prefix=$3
    if curl -s "http://127.0.0.1:${port}${prefix}/json-1k" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name (port $port)"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name (port $port) - NOT RESPONDING"
        return 1
    fi
}

echo ""
echo "Checking servers:"
all_ok=true
check_server "FastAPI" 8001 "" || all_ok=false
check_server "Litestar" 8002 "" || all_ok=false
check_server "Django Ninja" 8003 "/ninja" || all_ok=false
check_server "Django Bolt" 8004 "" || all_ok=false

if [ "$all_ok" = false ]; then
    echo ""
    echo -e "${RED}Some servers failed to start. Check the logs above.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}All servers running!${NC}"
echo ""

# Run benchmark
echo -e "${YELLOW}Running benchmark...${NC}"
echo ""
uv run python bench.py "$@"

echo ""
echo -e "${GREEN}Benchmark complete!${NC}"
