"""OpenAI-compatible proxy that intercepts prompts via Neuralizer agent."""

import json
import logging
import os

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.agents.neuralizer import Neuralizer
from services.clients.llm import LlamaCppClient
from services.clients.mock import MockThinkingClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://llm:8080")

# Scrubbing mode — when False, requests pass through to LLM directly
_scrubbing_enabled = True


class ModeRequest(BaseModel):
    scrubbing: bool


@router.get("/mode")
async def get_mode():
    """Return current scrubbing mode."""
    return {"scrubbing": _scrubbing_enabled}


@router.post("/mode")
async def set_mode(body: ModeRequest):
    """Toggle scrubbing mode."""
    global _scrubbing_enabled
    _scrubbing_enabled = body.scrubbing
    logger.info(f"Scrubbing mode set to: {_scrubbing_enabled}")
    return {"scrubbing": _scrubbing_enabled}


async def _proxy_to_llm(body: dict) -> StreamingResponse | dict:
    """Pass request through to LLM without interception."""
    stream = body.get("stream", False)

    if stream:

        async def stream_response():
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    "POST",
                    f"{LLM_BASE_URL}/v1/chat/completions",
                    json=body,
                ) as resp:
                    async for chunk in resp.aiter_bytes():
                        yield chunk

        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream",
        )

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{LLM_BASE_URL}/v1/chat/completions",
            json=body,
        )
        return resp.json()


@router.post("/chat/completions")
async def chat_completions(request: Request):
    """Intercept chat completion, run through Neuralizer agent."""
    body = await request.json()

    # Free chat mode — pass through to LLM directly
    if not _scrubbing_enabled:
        return await _proxy_to_llm(body)

    redis = request.app.state.redis
    monitor = request.app.state.monitor

    # Extract the last user message
    messages = body.get("messages", [])
    user_messages = [m for m in messages if m.get("role") == "user"]
    prompt_text = user_messages[-1]["content"] if user_messages else ""

    # Immediately notify left pane that we received the prompt
    await redis.publish(
        "prompt_intercept",
        json.dumps(
            {
                "prompt": prompt_text,
                "sanitized": "",
                "status": "Processing...",
            }
        ),
    )

    # Run through Neuralizer agent with local LLM
    client = LlamaCppClient()
    agent = Neuralizer(client=client, monitor=monitor)
    result = await agent.run(
        session_id="proxy",
        prompt=prompt_text,
    )

    # Result is a dict with 'panel', 'status', 'detection'
    panel_text = (
        result.get("panel", prompt_text) if isinstance(result, dict) else str(result)
    )
    status_text = result.get("status", "") if isinstance(result, dict) else str(result)
    detection = result.get("detection", {}) if isinstance(result, dict) else {}

    # Update left pane with final result
    await redis.publish(
        "prompt_intercept",
        json.dumps(
            {
                "prompt": prompt_text,
                "sanitized": panel_text,
                "status": detection.get("category", "clean").replace("_", " ").title(),
            }
        ),
    )

    # Return brief status to Open WebUI (right pane)
    model = body.get("model", "unknown")
    placeholder = {
        "id": "intercepted",
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": status_text,
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }

    stream = body.get("stream", False)
    if stream:
        chunk = "data: " + json.dumps(placeholder) + "\n\ndata: [DONE]\n\n"
        return StreamingResponse(
            iter([chunk]),
            media_type="text/event-stream",
        )

    return placeholder


@router.post("/test/think-error")
async def test_think_error(request: Request):
    """Test endpoint: simulate a thinking model JSON parse error."""
    redis = request.app.state.redis
    monitor = request.app.state.monitor
    prompt_text = "❯ whoami\nks73\n~/repos/work/neuralizer"

    await redis.publish(
        "prompt_intercept",
        json.dumps(
            {
                "prompt": prompt_text,
                "sanitized": "",
                "status": "Processing...",
            }
        ),
    )

    client = MockThinkingClient()
    agent = Neuralizer(client=client, monitor=monitor)
    result = await agent.run(session_id="test", prompt=prompt_text)

    panel_text = (
        result.get("panel", prompt_text) if isinstance(result, dict) else str(result)
    )
    status_text = result.get("status", "") if isinstance(result, dict) else str(result)
    detection = result.get("detection", {}) if isinstance(result, dict) else {}

    await redis.publish(
        "prompt_intercept",
        json.dumps(
            {
                "prompt": prompt_text,
                "sanitized": panel_text,
                "status": detection.get("category", "clean").replace("_", " ").title(),
            }
        ),
    )

    return {"status": status_text, "panel": panel_text}


@router.get("/models")
async def list_models():
    """Proxy model list from LLM so Open WebUI can discover available models."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LLM_BASE_URL}/v1/models")
        return resp.json()
