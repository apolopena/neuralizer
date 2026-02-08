"""Debug WebSocket — streams trace events in DEV_MODE."""

import logging
import os

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
DEV_MODE = os.getenv("DEV_MODE", "false").lower() == "true"


async def debug_stream(websocket: WebSocket):
    """Subscribe to debug_traces channel and push to client."""
    if not DEV_MODE:
        await websocket.close(code=4000, reason="Debug mode not enabled")
        return

    await websocket.accept()
    redis = websocket.app.state.redis
    pubsub = redis.pubsub()

    try:
        await pubsub.subscribe("debug_traces")
        logger.info("Debug WebSocket client connected")

        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        logger.info("Debug WebSocket client disconnected")
    finally:
        await pubsub.unsubscribe("debug_traces")
        await pubsub.close()
