"""Neuralizer agent — intercepts and classifies prompts for sanitization.

Uses the local LLM to detect PII, credentials, log files, and other
sensitive data. Does not yet sanitize — only detects and reports.
"""

import json
import logging
from typing import Any

from services.agents.base import BaseAgent
from services.prompts.neuralizer import (
    build_detect_prompt,
    build_panel_response,
    build_status_response,
)

logger = logging.getLogger(__name__)


class Neuralizer(BaseAgent):
    """Prompt sanitization agent.

    Calls the LLM with a detection system prompt to classify
    whether user input contains sensitive data.
    """

    async def detect(self, text: str) -> dict:
        """Quick detection pass — classify content without full agent flow.

        Used by routes for determining which MCP tool to call.

        Args:
            text: Content to analyze

        Returns:
            {needs_sanitization, category, item_types, summary}
        """
        messages = build_detect_prompt(text)

        try:
            raw = await self.client.complete(text, messages=messages, temperature=0.3)
            detection = json.loads(raw)
            logger.info(f"Neuralizer detection: {detection}")

            # Ensure item_types is present (may be missing in old prompt format)
            if "item_types" not in detection:
                # Map items_detected to item_types based on category
                detection["item_types"] = self._infer_item_types(detection)

            return detection
        except Exception as e:
            logger.error(f"Neuralizer detection failed: {e}")
            # Fail-closed: treat detection failure as requiring sanitization
            # Routes will check category=="error" and block the request
            return {
                "needs_sanitization": True,
                "category": "error",
                "item_types": [],
                "summary": f"Detection failed: {e}",
            }

    def _infer_item_types(self, detection: dict) -> list[str]:
        """Infer item_types from category when not explicitly provided."""
        category = detection.get("category", "")

        # Map categories to default item types
        category_defaults = {
            "pii": ["email", "phone", "name"],
            "credentials": ["api_key", "secret", "bearer"],
            "log_file": [
                "ip",
                "private_ip",
                "internal_url",
                "timestamp",
                "endpoint",
                "user",
            ],
            "code_secrets": ["api_key", "secret", "path"],
            "infrastructure": ["ip", "internal_url", "resource_id"],
        }

        return category_defaults.get(category, [])

    async def _execute(self, prompt: str, **kwargs: Any) -> dict:
        """Classify and respond to the prompt.

        Args:
            prompt: The intercepted user prompt.

        Returns:
            Dict with 'panel' (left pane detail) and 'status' (right pane brief).
        """
        logger.info(f"Neuralizer processing: {prompt[:80]}...")

        messages = build_detect_prompt(prompt)

        raw = None
        try:
            raw = await self.client.complete(prompt, messages=messages, temperature=0.3)
            detection = json.loads(raw)
            logger.info(f"Neuralizer detection: {detection}")
        except Exception as e:
            error_type = type(e).__name__
            error_detail = str(e) or ""
            logger.error(f"Neuralizer detection failed: {error_type}: {error_detail}")

            # Human-readable error explanations
            if "Timeout" in error_type or "timeout" in error_detail:
                explanation = (
                    "The LLM took too long to respond. "
                    "This usually means the model is overloaded or "
                    "the thinking model is spending too long reasoning. "
                    "Try increasing LLM_TIMEOUT in .env or switching to a non-thinking model."
                )
            elif "Connection" in error_type or "connect" in error_detail.lower():
                explanation = (
                    "Could not connect to the LLM service. "
                    "Check that the llm container is running: "
                    "docker compose ps llm"
                )
            elif "JSONDecode" in error_type:
                explanation = (
                    "The LLM responded but not with valid JSON. "
                    "This happens when thinking models wrap output in <think> blocks. "
                    "Switch to a non-thinking model (e.g., Qwen3-4B-Instruct).\n\n"
                    f"Parse error: {error_detail}"
                )
            else:
                explanation = f"{error_type}: {error_detail}"

            raw_preview = raw[:500] if raw else "No response received from LLM."

            return {
                "panel": (
                    f"❌ Detection failed\n\n"
                    f"Prompt: {prompt}\n\n"
                    f"What happened: {explanation}\n\n"
                    f"Raw LLM response:\n{raw_preview}"
                ),
                "status": "❌ Detection failed — see left panel for details.",
                "detection": {"category": "error"},
            }

        return {
            "panel": build_panel_response(prompt, detection),
            "status": build_status_response(detection),
            "detection": detection,
        }
