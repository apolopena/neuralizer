"""WebSocket endpoint for streaming intercepted prompts to the frontend."""

import logging

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


async def prompt_stream(websocket: WebSocket):
    """Subscribe to Redis prompt_intercept channel and push events to client."""
    await websocket.accept()
    redis = websocket.app.state.redis
    pubsub = redis.pubsub()

    try:
        await pubsub.subscribe("prompt_intercept")
        logger.info("WebSocket client connected to prompt stream")

        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                await websocket.send_text(message["data"])
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected from prompt stream")
    finally:
        await pubsub.unsubscribe("prompt_intercept")
        await pubsub.close()
