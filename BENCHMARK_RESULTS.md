# Framework Benchmark Results

**Date:** 2026-02-23 00:11:27

## Configuration

- Connections: 100
- Duration: 10s per endpoint
- Warmup: 1000 requests
- Runs: 3 (best result taken)

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/json-1k` | ~1KB JSON response |
| `/json-10k` | ~10KB JSON response |
| `/db` | 10 database reads |
| `/slow` | 2 second mock delay |

## Results

### /json-1k

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| litestar | 30,925 | 0.00ms | 0.00ms | 0 |
| django-bolt | 22,979 | 0.00ms | 0.00ms | 0 |
| fastapi | 20,568 | 0.00ms | 0.00ms | 0 |

### /json-10k

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| litestar | 19,708 | 0.01ms | 0.00ms | 0 |
| django-bolt | 18,274 | 0.01ms | 0.00ms | 0 |
| fastapi | 8,954 | 0.01ms | 0.00ms | 0 |

### /db

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| django-bolt | 3,154 | 0.03ms | 0.00ms | 0 |
| litestar | 1,135 | 0.09ms | 0.00ms | 0 |
| fastapi | 1,083 | 0.09ms | 0.00ms | 0 |

## Summary (RPS by Endpoint)

| Framework | /json-1k | /json-10k | /db |
|-----------|--------:|--------:|--------:|
| django-bolt | 22,979 | 18,274 | 3,154 |
| fastapi | 20,568 | 8,954 | 1,083 |
| litestar | 30,925 | 19,708 | 1,135 |
