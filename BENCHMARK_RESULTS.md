# Framework Benchmark Results

**Date:** 2026-03-09 21:40:40

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
| django-bolt | 29,680 | 0.00ms | 0.00ms | 0 |
| litestar | 27,427 | 0.00ms | 0.00ms | 0 |

### /json-10k

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| django-bolt | 22,179 | 0.00ms | 0.00ms | 0 |
| litestar | 21,361 | 0.00ms | 0.00ms | 0 |

### /db

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| django-bolt | 2,712 | 0.04ms | 0.00ms | 0 |
| litestar | 1,092 | 0.09ms | 0.00ms | 0 |

## Summary (RPS by Endpoint)

| Framework | /json-1k | /json-10k | /db |
|-----------|--------:|--------:|--------:|
| django-bolt | 29,680 | 22,179 | 2,712 |
| litestar | 27,427 | 21,361 | 1,092 |
