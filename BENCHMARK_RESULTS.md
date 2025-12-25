# Framework Benchmark Results

**Date:** 2025-12-25 19:35:43

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
| django-bolt | 27,009 | 0.00ms | 0.00ms | 0 |
| litestar | 21,638 | 0.00ms | 0.00ms | 0 |
| fastapi | 8,017 | 0.01ms | 0.00ms | 0 |
| django-ninja | 2,422 | 0.04ms | 0.00ms | 0 |

### /json-10k

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| django-bolt | 20,298 | 0.00ms | 0.00ms | 0 |
| litestar | 15,926 | 0.01ms | 0.00ms | 0 |
| django-ninja | 2,116 | 0.05ms | 0.00ms | 0 |
| fastapi | 1,545 | 0.06ms | 0.00ms | 0 |

### /db

| Framework | RPS | Latency (avg) | Latency (p99) | Errors |
|-----------|----:|-------------:|-------------:|-------:|
| django-bolt | 3,377 | 0.03ms | 0.00ms | 0 |
| fastapi | 1,023 | 0.10ms | 0.00ms | 0 |
| litestar | 1,016 | 0.10ms | 0.00ms | 0 |
| django-ninja | 706 | 0.14ms | 0.00ms | 0 |

## Summary (RPS by Endpoint)

| Framework | /json-1k | /json-10k | /db |
|-----------|--------:|--------:|--------:|
| django-ninja | 2,422 | 2,116 | 706 |
| litestar | 21,638 | 15,926 | 1,016 |
| fastapi | 8,017 | 1,545 | 1,023 |
| django-bolt | 27,009 | 20,298 | 3,377 |
