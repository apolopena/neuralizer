"""End-to-end file upload flow tests."""

import pytest


class TestFileUploadFlow:
    @pytest.mark.asyncio
    async def test_text_file_upload_scrub_flow(self):
        """File upload → detect → scrub_log_as_file → download available."""
        pytest.skip("Requires full app context with Neuralizer and MCP")

    @pytest.mark.asyncio
    async def test_non_text_file_rejected(self):
        """Non-text MIME types are rejected with 415."""
        pytest.skip("Requires full app context with file upload endpoint")

    @pytest.mark.asyncio
    async def test_oversized_file_rejected(self):
        """Files exceeding limit are rejected with 413."""
        pytest.skip("Requires full app context with file upload endpoint")
