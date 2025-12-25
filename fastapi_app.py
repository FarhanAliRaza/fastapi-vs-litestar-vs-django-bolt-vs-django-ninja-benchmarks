"""
FastAPI Benchmark Application

4 endpoints:
1. GET /json-1k     - Returns ~1KB JSON response
2. GET /json-10k    - Returns ~10KB JSON response
3. GET /db          - 10 reads from SQLite database
4. GET /slow        - Mock API that takes 2 seconds to respond
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import test_data
from shared.models import Base, User, UserResponse


# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./benchmark.db"
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
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
            print("[fastapi] Seeded 10 users")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - seed database on startup."""
    await seed_database()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/json-1k")
async def json_1k():
    """Return ~1KB JSON response."""
    return test_data.JSON_1K


@app.get("/json-10k")
async def json_10k():
    """Return ~10KB JSON response."""
    return test_data.JSON_10K


@app.get("/db", response_model=list[UserResponse])
async def db_read(db: AsyncSession = Depends(get_db)):
    """Read 10 users from database."""
    stmt = select(User).limit(10)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return users


@app.get("/slow")
async def slow():
    """Mock slow API - 2 second delay."""
    await asyncio.sleep(2)
    return {"status": "ok", "delay_seconds": 2}
