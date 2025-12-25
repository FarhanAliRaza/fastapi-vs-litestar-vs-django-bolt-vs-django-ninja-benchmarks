# Framework Benchmark

Compares 4 Python web frameworks with identical endpoints:

- **FastAPI** - ASGI framework with Pydantic
- **Litestar** - High-performance ASGI framework
- **Django Ninja** - Django + Pydantic API framework
- **Django Bolt** - Rust-powered Django API framework

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/json-1k` | Returns ~1KB JSON response |
| `/json-10k` | Returns ~10KB JSON response |
| `/db` | 10 reads from SQLite database |
| `/slow` | Mock API with 2 second delay |

## Requirements

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- [bombardier](https://github.com/codesenberg/bombardier) HTTP benchmarking tool

Install bombardier:
```bash
go install github.com/codesenberg/bombardier@latest
```

## Quick Start

```bash
# Setup (run once)
./setup.sh

# Run all benchmarks
./run_all.sh

# Or with custom options
./run_all.sh -c 200 -d 15 -r 5
```

## Manual Usage

### 1. Setup
```bash
./setup.sh
```

### 2. Start Servers (in separate terminals)
```bash
./run_fastapi.sh   # Port 8001
./run_litestar.sh  # Port 8002
./run_ninja.sh     # Port 8003
./run_bolt.sh      # Port 8004
```

### 3. Run Benchmark
```bash
uv run python bench.py
```

### Benchmark Options
```
-c, --connections  Concurrent connections (default: 100)
-d, --duration     Duration per endpoint in seconds (default: 10)
-w, --warmup       Warmup requests (default: 1000)
-r, --runs         Runs per endpoint (default: 3)
-o, --output       Output file (default: BENCHMARK_RESULTS.md)
--frameworks       Frameworks to benchmark (default: all)
```

## Best Practices Followed

1. **Warmup**: 1000 requests before each benchmark
2. **Multiple runs**: 3 runs per endpoint, best result taken
3. **Controlled concurrency**: 100 concurrent connections by default
4. **Same hardware**: All frameworks run on the same machine
5. **Same database**: SQLite for consistency
6. **No access logging**: Disabled to reduce overhead
7. **Multi-worker**: 4 workers for each framework

## Server Ports

| Framework | Port |
|-----------|------|
| FastAPI | 8001 |
| Litestar | 8002 |
| Django Ninja | 8003 |
| Django Bolt | 8004 |
