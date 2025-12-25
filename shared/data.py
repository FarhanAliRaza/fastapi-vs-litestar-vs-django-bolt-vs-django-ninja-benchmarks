"""
Shared test data for framework benchmarks.

Provides consistent data across all frameworks for fair comparison:
- JSON_1K: ~1KB JSON response
- JSON_10K: ~10KB JSON response
- Mock slow endpoint (2 second delay)
- Database with 10 users for ORM tests
"""

from __future__ import annotations

import json


def _generate_json_items(target_size_bytes: int) -> list[dict]:
    """Generate a list of items to approximately match target size."""
    items = []
    i = 0
    while True:
        item = {
            "id": i,
            "name": f"Item {i}",
            "description": f"This is a description for item number {i}",
            "price": round(10.99 + i * 0.1, 2),
            "category": f"category_{i % 10}",
            "in_stock": i % 3 != 0,
            "tags": [f"tag_{j}" for j in range(i % 5 + 1)],
        }
        items.append(item)
        # Check size after serialization
        current_size = len(json.dumps(items))
        if current_size >= target_size_bytes:
            break
        i += 1
    return items


# Pre-generate JSON data at module load (consistent across all requests)
JSON_1K: list[dict] = _generate_json_items(1024)
JSON_10K: list[dict] = _generate_json_items(10240)

# Validate sizes
_json_1k_size = len(json.dumps(JSON_1K))
_json_10k_size = len(json.dumps(JSON_10K))

print(f"[benchmark] JSON_1K size: {_json_1k_size} bytes ({len(JSON_1K)} items)")
print(f"[benchmark] JSON_10K size: {_json_10k_size} bytes ({len(JSON_10K)} items)")
