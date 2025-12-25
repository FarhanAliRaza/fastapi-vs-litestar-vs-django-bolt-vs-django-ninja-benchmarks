# Framework Benchmark Results

**Date:** 2025-12-25 20:02:19

## Configuration

- Connections: 100
- Duration: 10s per endpoint
- Warmup: 1000 requests
- Runs: 1 (best result taken)

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
| django-bolt | 27,352 | 0.00ms | 0.00ms | 0 |
| litestar | 21,782 | 0.00ms | 0.00ms | 0 |
| fastapi | 9,652 | 0.01ms | 0.00ms | 0 |
| django-ninja | 2,256 | 0.04ms | 0.00ms | 0 |

### /json-10k

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| django-bolt | 21,132 | 0.00ms | 0.00ms | 0 |
| litestar | 17,861 | 0.01ms | 0.00ms | 0 |
| fastapi | 2,118 | 0.05ms | 0.00ms | 0 |
| django-ninja | 2,020 | 0.05ms | 0.00ms | 0 |

### /db

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| django-bolt | 3,277 | 0.03ms | 0.00ms | 0 |
| litestar | 1,022 | 0.10ms | 0.00ms | 0 |
| fastapi | 1,018 | 0.10ms | 0.00ms | 0 |
| django-ninja | 695 | 0.14ms | 0.00ms | 0 |

## Summary (RPS by Endpoint)

| Framework | /json-1k | /json-10k | /db |
|-----------|--------:|--------:|--------:|
| django-ninja | 2,256 | 2,020 | 695 |
| django-bolt | 27,352 | 21,132 | 3,277 |
| fastapi | 9,652 | 2,118 | 1,018 |
| litestar | 21,782 | 17,861 | 1,022 |
