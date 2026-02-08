"""OpenAI-compatible proxy that intercepts prompts via Neuralizer agent."""

import json
import logging
import os

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from services.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1")

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://llm:8080")
SCRUB_PROMPT_LIMIT = int(os.getenv("SCRUB_PROMPT_LIMIT_KB", "32")) * 1024


class ModeRequest(BaseModel):
    scrubbing: bool


@router.get("/mode")
async def get_mode(request: Request):
    """Return current scrubbing mode."""
    return {"scrubbing": request.app.state.scrubbing_enabled}


@router.post("/mode")
async def set_mode(request: Request, body: ModeRequest):
    """Toggle scrubbing mode."""
    request.app.state.scrubbing_enabled = body.scrubbing
    logger.info(f"Scrubbing mode set to: {body.scrubbing}")
    return {"scrubbing": request.app.state.scrubbing_enabled}


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
    """Intercept chat completion, run through Neuralizer, scrub if needed.

    Note: Router has prefix="/v1", so full path is /v1/chat/completions.
    """
    body = await request.json()
    redis = request.app.state.redis
    neuralizer = request.app.state.neuralizer

    # Passthrough if scrubbing disabled
    if not request.app.state.scrubbing_enabled:
        return await _proxy_to_llm(body)

    # Extract last user message
    messages = body.get("messages", [])
    user_messages = [m for m in messages if m.get("role") == "user"]
    prompt_text = user_messages[-1]["content"] if user_messages else ""

    # Size limit
    prompt_size = len(prompt_text.encode("utf-8"))
    if prompt_size > SCRUB_PROMPT_LIMIT:
        return _error_response(
            body,
            f"Content too large ({prompt_size // 1024} KB). "
            f"Maximum is {SCRUB_PROMPT_LIMIT // 1024} KB. "
            "Use file upload for large files.",
        )

    # Publish "Processing..." for frontend loader
    await redis.publish(
        "prompt_intercept",
        json.dumps({"prompt": prompt_text, "sanitized": "", "status": "Processing..."}),
    )

    # Detection
    detection = await neuralizer.detect(prompt_text)
    category = detection.get("category", "")

    # Fail-closed: detection errors block the request
    if category == "error":
        error_msg = detection.get("summary", "Detection failed")
        await _publish_to_panel(
            redis, prompt_text, detection, prompt_text, [], warning=error_msg
        )
        return _error_response(
            body, f"Detection failed: {error_msg}. Content blocked for safety."
        )

    if not detection.get("needs_sanitization", False):
        # Clean — publish and return status
        await _publish_to_panel(redis, prompt_text, detection, prompt_text, [])
        return _status_response(body, "clean", "No sensitive content detected.")

    item_types = detection.get("item_types", [])

    # Empty item_types = detection incomplete, no action, report to both panes
    if not item_types:
        logger.warning(
            f"Detection flagged needs_sanitization but returned empty item_types: {detection}"
        )
        await _publish_to_panel(
            redis,
            prompt_text,
            detection,
            prompt_text,
            [],
            warning="Detection incomplete: no item types returned",
        )
        return _status_response(
            body,
            "warning",
            "Detection incomplete — content not scrubbed. Please review.",
        )

    mcp = await get_mcp_client()

    # For log data: use ALL log + standard patterns (catches emails, API keys in logs)
    # For other prompts: use ALL standard patterns
    # Detection determines category, but we scrub with all patterns for that category
    # Always use all patterns (log + standard) to catch everything
    # Detection categorizes content, but we scrub comprehensively
    all_patterns = [
        "ip",
        "private_ip",
        "internal_url",
        "timestamp",
        "endpoint",
        "user",
        "terminal_user",  # log
        "email",
        "phone",
        "name",
        "api_key",
        "secret",
        "bearer",
        "path",
        "resource_id",  # standard
    ]
    result = await mcp.scrub_log_as_prompt(prompt_text, all_patterns)

    sanitized = result["sanitized_text"]
    replacements = result["replacements"]
    summary = result["summary"]  # Counts by item_type, e.g. {"email": 2, "ip": 1}

    # Publish to panel
    await _publish_to_panel(
        redis, prompt_text, detection, sanitized, replacements, summary=summary
    )

    # Return status to Open WebUI
    return _status_response(body, "scrubbed", f"{len(replacements)} items tokenized.")


async def _publish_to_panel(
    redis,
    original: str,
    detection: dict,
    sanitized: str,
    replacements: list,
    summary: dict = None,
    warning: str = None,
):
    """Publish result to panel via Redis.

    Both original and sanitized are published for side-by-side comparison.
    This is a local tool — privacy is not a concern.

    Required fields: {prompt, sanitized, status}
    Extra metadata included for future use.
    """
    category = detection.get("category", "clean")
    needs_sanitization = detection.get("needs_sanitization", False)

    # Build status string for frontend display
    if warning:
        status = f"⚠️ Warning: {warning}"
    elif category == "error":
        status = "❌ Error"
    elif not needs_sanitization:
        status = f"🛡️ {category.replace('_', ' ').title()}"
    else:
        # Scrubbed - show category and count
        count = len(replacements)
        status = f"🛡️ {category.replace('_', ' ').title()} — {count} item{'s' if count != 1 else ''} scrubbed"
        if summary:
            # Add breakdown: "email: 2, ip: 1"
            breakdown = ", ".join(f"{k}: {v}" for k, v in summary.items())
            status += f" ({breakdown})"

    payload = {
        # Required by frontend
        "prompt": original,
        "sanitized": sanitized,
        "status": status,
        # Extra metadata
        "type": "prompt_result",
        "detection": {
            "category": category,
            "needs_sanitization": needs_sanitization,
        },
        "replacement_count": len(replacements),
        "summary": summary or {},
    }
    if warning:
        payload["warning"] = warning
    await redis.publish("prompt_intercept", json.dumps(payload))


def _status_response(body: dict, status: str, message: str) -> dict | StreamingResponse:
    """Return status message to Open WebUI (not an LLM response).

    Handles both streaming and non-streaming requests.
    """
    content = f"🛡️ [{status.upper()}] {message}"
    model = body.get("model", "unknown")

    # Handle streaming requests (Open WebUI commonly uses stream=true)
    if body.get("stream", False):
        # Use proper chat.completion.chunk format with delta
        chunk_payload = {
            "id": "neuralizer",
            "object": "chat.completion.chunk",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
        }
        chunk = "data: " + json.dumps(chunk_payload) + "\n\ndata: [DONE]\n\n"
        return StreamingResponse(
            iter([chunk]),
            media_type="text/event-stream",
        )

    # Non-streaming: use chat.completion format with message
    return {
        "id": "neuralizer",
        "object": "chat.completion",
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }


def _error_response(body: dict, message: str) -> dict | StreamingResponse:
    """Return error message to Open WebUI."""
    return _status_response(body, "error", message)


@router.get("/models")
async def list_models():
    """Proxy model list from LLM so Open WebUI can discover available models."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{LLM_BASE_URL}/v1/models")
        return resp.json()
