"""Base agent class for all agents.

- No Agent suffix on class names
- Dependency injection (client and monitor passed in)
- Publishes start/complete/error events
- Supports streaming and oneshot modes
"""

import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from services.activity_monitor import AgentActivityMonitor
from services.clients.base import BaseClient

logger = logging.getLogger(__name__)


def _to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, client: BaseClient, monitor: AgentActivityMonitor):
        self.client = client
        self.monitor = monitor

    @property
    def name(self) -> str:
        """Agent name in snake_case."""
        return _to_snake_case(self.__class__.__name__)

    async def send_prompt_json_with_event(
        self, prompt: str, schema: type[BaseModel], session_id: str, **kwargs: Any
    ) -> dict:
        """Send prompt for JSON with error event publishing on failure."""
        try:
            return await self.client.send_prompt_json(prompt, schema, **kwargs)
        except ValueError as e:
            await self.monitor.publish(
                agent=self.name,
                session_id=session_id,
                model=self.client.model,
                state="parse_error",
                error=str(e)[:100],
            )
            raise

    async def run(self, session_id: str, mode: str = "oneshot", **kwargs: Any) -> Any:
        """Execute the agent with event publishing."""
        thinking = kwargs.get("thinking", False)
        temperature = kwargs.get("temperature", 0.7)

        if thinking:
            temperature = None

        await self.monitor.publish(
            agent=self.name,
            session_id=session_id,
            model=getattr(self.client, "model", "n/a"),
            state="start",
            thinking=thinking,
            temperature=temperature,
            provider=getattr(self.client, "provider", None),
        )

        try:
            if mode == "streaming":
                result = await self._execute_stream(**kwargs)
            else:
                result = await self._execute(**kwargs)

            thinking_content = None
            if isinstance(result, dict) and "thinking" in result:
                thinking_content = result.get("thinking")
                result = result.get("text", result)

            await self.monitor.publish(
                agent=self.name,
                session_id=session_id,
                model=getattr(self.client, "model", "n/a"),
                state="complete",
                output=result if isinstance(result, str) else str(result),
                thinking=thinking_content,
            )

            logger.info(f"{self.name} completed (session {session_id}, mode={mode})")
            return result

        except Exception as e:
            await self.monitor.publish(
                agent=self.name,
                session_id=session_id,
                model=getattr(self.client, "model", "n/a"),
                state="error",
                error=str(e),
            )
            logger.error(f"{self.name} error (session {session_id}): {e}")
            raise

    @abstractmethod
    async def _execute(self, **kwargs: Any) -> Any:
        """Execute the agent's core logic (oneshot mode)."""
        raise NotImplementedError

    async def _execute_stream(self, **kwargs: Any) -> Any:
        """Execute streaming mode. Default falls back to oneshot."""
        logger.warning(
            f"{self.name} does not implement streaming, falling back to oneshot"
        )
        return await self._execute(**kwargs)
