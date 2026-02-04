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
                "status": f"❌ Detection failed — see left panel for details.",
                "detection": {"category": "error"},
            }

        return {
            "panel": build_panel_response(prompt, detection),
            "status": build_status_response(detection),
            "detection": detection,
        }
