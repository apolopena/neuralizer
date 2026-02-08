"""NeurALIzer backend FastAPI application."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis

from routes.config import router as config_router
from routes.files import router as files_router
from routes.health import router as health_router
from routes.inference import router as inference_router
from services.activity_monitor import AgentActivityMonitor
from services.agents.neuralizer import Neuralizer
from services.clients.llm import LlamaCppClient
from services.mcp_client import get_mcp_client, shutdown_mcp_client
from websockets.prompt_stream import prompt_stream

DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — connect/disconnect Redis, start/stop MCP."""
    redis_host = os.getenv("REDIS_HOST", "redis")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))

    try:
        # Scrubbing mode (default ON)
        app.state.scrubbing_enabled = True

        # Redis
        redis = Redis(host=redis_host, port=redis_port, decode_responses=True)
        await redis.ping()
        app.state.redis = redis
        logger.info(f"Connected to Redis at {redis_host}:{redis_port}")

        # Activity monitor
        app.state.monitor = AgentActivityMonitor(redis)

        # LLM client singleton
        app.state.llm_client = LlamaCppClient()

        # Neuralizer singleton (uses LLM client)
        app.state.neuralizer = Neuralizer(
            client=app.state.llm_client,
            monitor=app.state.monitor,
        )

        # Start MCP subprocess
        app.state.mcp = await get_mcp_client()
        logger.info("MCP client started")

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

    # Clean shutdown
    await shutdown_mcp_client()
    logger.info("MCP client stopped")
    await redis.close()
    logger.info("Redis connection closed")


app = FastAPI(
    title="NeurALIzer Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# Add debug middleware if DEV_MODE
if DEV_MODE:
    from middleware.trace import trace_middleware

    app.middleware("http")(trace_middleware)
    logger.info("Debug trace middleware enabled (DEV_MODE=true)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://localhost"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(health_router)
app.include_router(inference_router)
app.include_router(files_router)
app.include_router(config_router)
app.websocket("/ws/prompts")(prompt_stream)

# Debug WebSocket (only in DEV_MODE)
if DEV_MODE:
    from websockets.debug_stream import debug_stream

    app.websocket("/ws/debug")(debug_stream)
