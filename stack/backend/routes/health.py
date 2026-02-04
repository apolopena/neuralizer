import os

import httpx
from fastapi import APIRouter, Request

router = APIRouter()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://llm:8080")


@router.get("/health")
async def health(request: Request):
    """Health check with dependency status for Redis and LLM."""
    redis_ok = False
    llm_ok = False

    # Check Redis
    try:
        await request.app.state.redis.ping()
        redis_ok = True
    except Exception:
        pass

    # Check LLM
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{LLM_BASE_URL}/health")
            llm_ok = resp.status_code == 200
    except Exception:
        pass

    all_ok = redis_ok and llm_ok
    return {
        "status": "ok" if all_ok else "degraded",
        "services": {
            "redis": "ok" if redis_ok else "unavailable",
            "llm": "ok" if llm_ok else "unavailable",
        },
    }
