"""
Django Ninja Benchmark API

4 endpoints:
1. GET /json-1k     - Returns ~1KB JSON response
2. GET /json-10k    - Returns ~10KB JSON response
3. GET /db          - 10 reads from SQLite database
4. GET /slow        - Mock API that takes 2 seconds to respond
"""

from __future__ import annotations

import asyncio
from typing import List

from ninja import NinjaAPI, Schema

from django_project.users.models import BenchmarkUser

import sys
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])
import test_data


api = NinjaAPI(urls_namespace="ninja")


class UserSchema(Schema):
    """User response schema."""

    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool


@api.get("/json-1k")
async def json_1k(request):
    """Return ~1KB JSON response."""
    return test_data.JSON_1K


@api.get("/json-10k")
async def json_10k(request):
    """Return ~10KB JSON response."""
    return test_data.JSON_10K


@api.get("/db", response=List[UserSchema])
async def db_read(request):
    """Read 10 users from database."""
    users = []
    async for user in BenchmarkUser.objects.all()[:10]:
        users.append(user)
    return users


@api.get("/slow")
async def slow(request):
    """Mock slow API - 2 second delay."""
    await asyncio.sleep(2)
    return {"status": "ok", "delay_seconds": 2}
