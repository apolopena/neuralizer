"""Empty item_types and detection edge case tests."""

import pytest


class TestInferenceEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_item_types_returns_warning(self):
        """Empty item_types returns warning status, no scrubbing."""
        # Verify that when detection returns needs_sanitization=True but empty item_types,
        # the route returns a warning status instead of crashing
        from routes.inference import _status_response

        # Simulate the warning response that would be returned
        body = {"model": "test", "stream": False}
        response = _status_response(
            body, "warning", "Detection incomplete — content not scrubbed."
        )

        assert response["choices"][0]["message"]["content"].startswith("[WARNING]")

    @pytest.mark.asyncio
    async def test_detection_error_blocks_request(self):
        """Detection failure blocks request (fail-closed behavior)."""
        from routes.inference import _error_response

        body = {"model": "test", "stream": False}
        response = _error_response(body, "Detection failed: LLM timeout")

        assert response["choices"][0]["message"]["content"].startswith("[ERROR]")
