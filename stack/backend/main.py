"""NeurALIzer backend FastAPI application."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from routes.health import router as health_router
from routes.inference import router as inference_router
from websockets.prompt_stream import prompt_stream

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — connect/disconnect Redis."""
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    try:
        redis = Redis(host=redis_host, port=redis_port, decode_responses=True)
        await redis.ping()
        app.state.redis = redis
        logger.info(f"Connected to Redis at {redis_host}:{redis_port}")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise

    yield

    await redis.close()
    logger.info("Redis connection closed")


app = FastAPI(
    title="NeurALIzer Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(health_router)
app.include_router(inference_router)
app.websocket("/ws/prompts")(prompt_stream)
