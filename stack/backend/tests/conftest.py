"""Pytest configuration and fixtures."""

import os
import sys
from pathlib import Path

os.environ.setdefault("DEV_MODE", "false")
os.environ.setdefault("LLM_BASE_URL", "http://mock:8080")

import pytest
import pytest_asyncio
from fakeredis import aioredis as fake_aioredis
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, str(Path(__file__).parent.parent))

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def redis_client():
    """Fake Redis for pub/sub tests."""
    client = fake_aioredis.FakeRedis(decode_responses=True)
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()


@pytest_asyncio.fixture
async def app(redis_client):
    """FastAPI app with fake Redis."""
    from main import app as _app

    _app.state.redis = redis_client

    async with AsyncClient(
        transport=ASGITransport(_app), base_url="http://test"
    ) as client:
        yield client
