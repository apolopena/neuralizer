"""LLM client for local llama.cpp inference."""

import json
import logging
import os
from typing import AsyncGenerator, Any

import httpx
from pydantic import BaseModel

from services.clients.base import BaseClient

logger = logging.getLogger(__name__)

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://llm:8080")


LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "15"))


class LlamaCppClient(BaseClient):
    """Client for llama.cpp server with OpenAI-compatible API."""

    def __init__(self):
        self.base_url = LLM_BASE_URL
        self.model = "local"
        self.provider = "llama.cpp"

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Send a chat completion and return the response text."""
        messages = kwargs.pop("messages", None)
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        body = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.3),
        }

        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            resp = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json=body,
                headers={"Content-Type": "application/json"},
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def complete_stream(
        self, prompt: str, **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Streaming completion."""
        # Not needed for detection, fallback to oneshot
        result = await self.complete(prompt, **kwargs)
        yield result

    async def send_prompt_json(
        self, prompt: str, schema: type[BaseModel], **kwargs: Any
    ) -> dict:
        """Send prompt expecting JSON response, validate against schema."""
        raw = await self.complete(prompt, **kwargs)
        # Strip markdown fences if present
        text = raw.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        parsed = json.loads(text)
        validated = schema.model_validate(parsed)
        return validated.model_dump()
