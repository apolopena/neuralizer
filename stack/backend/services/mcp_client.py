"""Async MCP client for calling scrubbing tools via subprocess."""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Optional

MCP_SERVER_PATH = Path(__file__).parent.parent / "scrubbing" / "server.py"
BACKEND_ROOT = Path(__file__).parent.parent  # stack/backend
TOOL_TIMEOUT = 30  # seconds


class MCPClient:
    """Async stdio-based MCP client for scrubbing tools."""

    def __init__(self):
        self._process: Optional[asyncio.subprocess.Process] = None
        self._request_id = 0
        self._lock = asyncio.Lock()

    async def start(self):
        """Start the MCP server subprocess and initialize."""
        if self._process is not None:
            return

        # Set PYTHONPATH so mcp/server.py can use absolute imports
        env = os.environ.copy()
        env["PYTHONPATH"] = str(BACKEND_ROOT)

        self._process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(MCP_SERVER_PATH),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,  # Drop stderr to avoid buffer deadlock
            env=env,
        )

        # MCP protocol requires initialization handshake
        await self._initialize()

    async def _initialize(self):
        """Send MCP initialize handshake."""
        self._request_id += 1
        init_request = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "neuralizer", "version": "1.0.0"},
            },
        }
        request_bytes = (json.dumps(init_request) + "\n").encode()
        self._process.stdin.write(request_bytes)
        await self._process.stdin.drain()

        # Read initialize response
        response_line = await asyncio.wait_for(
            self._process.stdout.readline(),
            timeout=10,
        )
        response = json.loads(response_line.decode())
        if "error" in response:
            raise RuntimeError(f"MCP initialize failed: {response['error']}")

        # Send initialized notification (no response expected)
        self._request_id += 1
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        self._process.stdin.write((json.dumps(initialized) + "\n").encode())
        await self._process.stdin.drain()

    async def stop(self):
        """Stop the MCP server subprocess."""
        if self._process:
            self._process.terminate()
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self._process.kill()
            self._process = None

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Call an MCP tool and return the result."""
        async with self._lock:
            # Auto-restart if process died
            if not self._process or self._process.returncode is not None:
                self._process = None
                await self.start()

            self._request_id += 1
            request = {
                "jsonrpc": "2.0",
                "id": self._request_id,
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }

            # Send request (restart on closed pipe)
            request_bytes = (json.dumps(request) + "\n").encode()
            try:
                self._process.stdin.write(request_bytes)
                await self._process.stdin.drain()
            except (RuntimeError, BrokenPipeError, ConnectionResetError):
                # Pipe closed - restart and retry once
                self._process = None
                await self.start()
                self._process.stdin.write(request_bytes)
                await self._process.stdin.drain()

            # Read response with timeout
            try:
                response_line = await asyncio.wait_for(
                    self._process.stdout.readline(),
                    timeout=TOOL_TIMEOUT,
                )
            except asyncio.TimeoutError:
                # Kill subprocess to prevent late response corruption on next call
                self._process.kill()
                await self._process.wait()
                self._process = None
                raise RuntimeError(f"MCP tool '{name}' timed out after {TOOL_TIMEOUT}s")

            response = json.loads(response_line.decode())

            # Validate response ID matches request ID
            if response.get("id") != self._request_id:
                raise RuntimeError(
                    f"Response ID mismatch: expected {self._request_id}, "
                    f"got {response.get('id')}"
                )

            if "error" in response:
                raise RuntimeError(response["error"]["message"])

            # MCP wraps tool results in content array
            result = response.get("result", {})
            content = result.get("content", [])
            if content and content[0].get("type") == "text":
                # Parse the JSON text content
                return json.loads(content[0]["text"])
            return result

    async def scrub_prompt(self, text: str, item_types: list[str]) -> dict:
        """Convenience method for scrub_prompt tool."""
        return await self.call_tool(
            "scrub_prompt",
            {
                "text": text,
                "item_types": item_types,
            },
        )

    async def scrub_log_as_prompt(self, text: str, item_types: list[str]) -> dict:
        """Convenience method for scrub_log_as_prompt tool."""
        return await self.call_tool(
            "scrub_log_as_prompt",
            {
                "text": text,
                "item_types": item_types,
            },
        )

    async def scrub_log_as_file(
        self,
        input_path: str,
        output_path: str,
        item_types: list[str],
    ) -> dict:
        """Convenience method for scrub_log_as_file tool."""
        return await self.call_tool(
            "scrub_log_as_file",
            {
                "input_path": input_path,
                "output_path": output_path,
                "item_types": item_types,
            },
        )


# Singleton instance
_client: Optional[MCPClient] = None


async def get_mcp_client() -> MCPClient:
    """Get or create the singleton MCP client."""
    global _client
    if _client is None:
        _client = MCPClient()
        await _client.start()
    return _client


async def shutdown_mcp_client():
    """Shutdown the singleton MCP client."""
    global _client
    if _client is not None:
        await _client.stop()
        _client = None
