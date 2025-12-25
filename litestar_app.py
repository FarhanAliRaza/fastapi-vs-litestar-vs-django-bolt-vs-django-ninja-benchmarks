"""
Litestar Benchmark Application

4 endpoints:
1. GET /json-1k     - Returns ~1KB JSON response
2. GET /json-10k    - Returns ~10KB JSON response
3. GET /db          - 10 reads from SQLite database
4. GET /slow        - Mock API that takes 2 seconds to respond
"""

from __future__ import annotations

import asyncio
from typing import Any

from litestar import Litestar, get
from litestar.di import Provide
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from shared.data import JSON_1K, JSON_10K
from shared.models import Base, User, UserResponse


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./benchmark.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """Dependency to get database session."""
    async with async_session() as session:
        yield session


async def seed_database():
    """Seed database with 10 users if empty."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is None:
            users = [
                User(
                    username=f"user{i:02d}",
                    email=f"user{i:02d}@example.com",
                    first_name=f"First{i}",
                    last_name=f"Last{i}",
                )
                for i in range(10)
            ]
            session.add_all(users)
            await session.commit()
            print("[litestar] Seeded 10 users")


async def on_startup():
    """Startup hook - seed database."""
    await seed_database()


@get("/json-1k")
async def json_1k() -> list[dict[str, Any]]:
    """Return ~1KB JSON response."""
    return JSON_1K


@get("/json-10k")
async def json_10k() -> list[dict[str, Any]]:
    """Return ~10KB JSON response."""
    return JSON_10K


@get("/db", dependencies={"db": Provide(get_db)})
async def db_read(db: AsyncSession) -> list[UserResponse]:
    """Read 10 users from database."""
    stmt = select(User).limit(10)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@get("/slow")
async def slow() -> dict[str, Any]:
    """Mock slow API - 2 second delay."""
    await asyncio.sleep(2)
    return {"status": "ok", "delay_seconds": 2}


app = Litestar(
    route_handlers=[json_1k, json_10k, db_read, slow],
    on_startup=[on_startup],
    openapi_config=None,
)
