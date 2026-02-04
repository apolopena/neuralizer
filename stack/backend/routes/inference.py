"""OpenAI-compatible proxy that intercepts prompts before forwarding to LLM."""

import json
import logging
import os

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://llm:8080")


@router.post("/chat/completions")
async def chat_completions(request: Request):
    """Intercept chat completion, publish to Redis, forward to LLM."""
    body = await request.json()
    redis = request.app.state.redis

    # Extract the last user message for display
    messages = body.get("messages", [])
    user_messages = [m for m in messages if m.get("role") == "user"]
    prompt_text = user_messages[-1]["content"] if user_messages else ""

    # Publish intercepted prompt to Redis for the left pane
    event = json.dumps({
        "prompt": prompt_text,
        "status": "Intercepted. Sanitization TBD.",
    })
    await redis.publish("prompt_intercept", event)
    logger.info(f"Intercepted prompt: {prompt_text[:80]}...")

    # Block inference — return a placeholder response to Open WebUI
    model = body.get("model", "unknown")
    placeholder = {
        "id": "intercepted",
        "object": "chat.completion",
        "model": model,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "[Intercepted] Prompt received by NeurALIzer. Sanitization pending.",
            },
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

    stream = body.get("stream", False)
    if stream:
        # Open WebUI expects SSE format for streaming
        chunk = "data: " + json.dumps(placeholder) + "\n\ndata: [DONE]\n\n"
        return StreamingResponse(
            iter([chunk]),
            media_type="text/event-stream",
        )

    return placeholder


@router.get("/models")
async def list_models():
    """Proxy model list from LLM so Open WebUI can discover available models."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LLM_BASE_URL}/v1/models")
        return resp.json()
