"""Mock clients for testing error scenarios."""

from typing import AsyncGenerator, Any

from pydantic import BaseModel

from services.clients.base import BaseClient


MOCK_THINK_RESPONSE = """<think>
Let me analyze this input for sensitive data. The user appears to have
pasted terminal output. I can see what looks like a username "ks73" from
a whoami command. There are also file paths visible that reveal internal
project structure. Let me classify this carefully...

The username is clearly PII. The file paths reveal internal infrastructure.
I should flag both of these.
</think>

{
  "needs_sanitization": true,
  "category": "pii",
  "summary": "Username detected from terminal output",
  "items_detected": ["ks73"]
}"""


class MockThinkingClient(BaseClient):
    """Returns a response wrapped in <think> blocks to test JSON parse errors."""

    def __init__(self):
        self.model = "mock-thinking"
        self.provider = "mock"

    async def complete(self, prompt: str, **kwargs: Any) -> str:
        return MOCK_THINK_RESPONSE

    async def complete_stream(
        self, prompt: str, **kwargs: Any
    ) -> AsyncGenerator[str, None]:
        yield MOCK_THINK_RESPONSE

    async def send_prompt_json(
        self, prompt: str, schema: type[BaseModel], **kwargs: Any
    ) -> dict:
        raise NotImplementedError
