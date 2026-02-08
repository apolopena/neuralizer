"""MCP subprocess client edge case tests."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class TestMCPClient:
    @pytest.mark.asyncio
    async def test_stderr_devnull_configured(self):
        """Verify stderr=DEVNULL is configured to prevent buffer deadlock."""
        from services.mcp_client import MCPClient

        client = MCPClient()

        with patch(
            "asyncio.create_subprocess_exec", new_callable=AsyncMock
        ) as mock_exec:
            mock_process = AsyncMock()
            mock_exec.return_value = mock_process

            await client.start()

            # Verify stderr=DEVNULL was passed
            call_kwargs = mock_exec.call_args.kwargs
            assert call_kwargs.get("stderr") == asyncio.subprocess.DEVNULL

    @pytest.mark.asyncio
    async def test_timeout_raises_error(self):
        """Tool call exceeding timeout raises RuntimeError."""
        from services.mcp_client import MCPClient

        client = MCPClient()

        # Mock subprocess that never responds
        mock_process = MagicMock()
        mock_process.returncode = None
        mock_process.stdin = AsyncMock()
        mock_process.stdout = AsyncMock()
        mock_process.stdout.readline = AsyncMock(side_effect=asyncio.TimeoutError)
        mock_process.kill = MagicMock()
        mock_process.wait = AsyncMock()

        client._process = mock_process

        with pytest.raises(RuntimeError, match="timed out"):
            await client.call_tool("scrub_prompt", {"text": "test", "item_types": []})

    @pytest.mark.asyncio
    async def test_auto_restart_after_crash(self):
        """Client auto-restarts subprocess on next call after crash."""
        from services.mcp_client import MCPClient

        client = MCPClient()
        start_count = 0

        async def mock_start():
            nonlocal start_count
            start_count += 1

        client.start = mock_start

        # Simulate crashed process
        mock_process = MagicMock()
        mock_process.returncode = 1  # Non-None = exited
        client._process = mock_process

        # Should trigger restart
        try:
            await client.call_tool("test", {})
        except Exception:
            pass

        assert start_count > 0
