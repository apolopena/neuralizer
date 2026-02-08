"""Open WebUI schema compatibility tests."""


class TestOpenWebuiCompatibility:
    def test_openwebui_schema_compatibility(self):
        """Upload response matches expected {status, id, filename, data, meta} structure."""
        from routes.files import _fake_openwebui_response

        response = _fake_openwebui_response("test123", "example.txt", "scrubbed")

        # Validate required fields
        assert response["status"] is True
        assert "id" in response
        assert response["filename"] == "example.txt"
        assert "data" in response
        assert response["data"]["content"] == ""  # Empty = no RAG
        assert "meta" in response

    def test_process_false_bypasses_rag(self):
        """Fake response with empty content prevents RAG embedding."""
        from routes.files import _fake_openwebui_response

        response = _fake_openwebui_response("test123", "example.txt", "clean")

        # Empty content should signal "no RAG processing"
        assert response["data"]["content"] == ""
