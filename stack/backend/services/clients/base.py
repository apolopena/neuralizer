"""Base client abstraction for AI providers."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any

from pydantic import BaseModel


class BaseClient(ABC):
    """Abstract base class for all AI provider clients."""

    @abstractmethod
    async def complete(self, prompt: str, **kwargs: Any) -> str:
        """Send a completion request and return full response text."""
        raise NotImplementedError

    @abstractmethod
    async def complete_stream(
        self, prompt: str, **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        """Send a streaming completion request and yield text chunks."""
        raise NotImplementedError
        yield ""  # pragma: no cover

    @abstractmethod
    async def send_prompt_json(
        self,
        prompt: str,
        schema: type[BaseModel],
        **kwargs: Any,
    ) -> dict:
        """Send prompt and return validated JSON matching schema."""
        raise NotImplementedError
