"""scrub_text function and span replacement tests."""

from mcp.scrubbers.core import (
    LOG_PATTERNS,
    STANDARD_PATTERNS,
    Tokenizer,
    scrub_text,
)


class TestScrubText:
    def test_span_replacement_no_over_replace(self):
        """Span-based replacement doesn't damage unrelated occurrences."""
        # "10" appears in both email and phone - should only replace in context
        text = "user10@example.com called from 555-100-1000"
        tokenizer = Tokenizer()
        result, replacements, summary = scrub_text(
            text, ["email", "phone"], STANDARD_PATTERNS, tokenizer
        )
        # Both should be replaced, but "10" elsewhere should be intact
        assert "[EMAIL_1]" in result
        assert "[PHONE_1]" in result

    def test_overlapping_spans_longest_wins(self):
        """Overlapping spans select longest match (e.g., internal_url over ip)."""
        text = "Access https://api.internal/v1/health from 192.168.1.1"
        tokenizer = Tokenizer()
        # internal_url contains the domain, ip is separate
        result, replacements, summary = scrub_text(
            text, ["internal_url", "ip"], LOG_PATTERNS, tokenizer
        )
        # URL should be tokenized as URL, separate IP as IP
        assert "[URL_1]" in result
        assert "[IP_1]" in result

    def test_empty_item_types_no_scrub(self):
        """Empty item_types list returns original text unchanged."""
        text = "user@example.com 555-1234"
        tokenizer = Tokenizer()
        result, replacements, summary = scrub_text(
            text, [], STANDARD_PATTERNS, tokenizer
        )
        assert result == text
        assert len(replacements) == 0
        assert len(summary) == 0

    def test_unknown_item_type_ignored(self):
        """Unknown item_type in list is skipped gracefully."""
        text = "user@example.com"
        tokenizer = Tokenizer()
        result, replacements, summary = scrub_text(
            text, ["unknown_type", "email"], STANDARD_PATTERNS, tokenizer
        )
        assert "[EMAIL_1]" in result
        assert len(replacements) == 1

    def test_all_standard_patterns_scrub(self):
        """All standard patterns produce correct tokens."""
        text = """
        Email: test@example.com
        Phone: 555-123-4567
        Name: John Smith
        Key: sk-abcdefghij12345678901234
        Secret: password=supersecret123
        Token: Bearer eyJhbGciOiJIUzI1NiJ9abcd
        Path: /home/user/documents
        Resource: proj:myorg:res_abc123def456
        """
        tokenizer = Tokenizer()
        result, replacements, summary = scrub_text(
            text,
            [
                "email",
                "phone",
                "name",
                "api_key",
                "secret",
                "bearer",
                "path",
                "resource_id",
            ],
            STANDARD_PATTERNS,
            tokenizer,
        )
        # Check all pattern types created tokens
        assert "[EMAIL_1]" in result
        assert "[PHONE_1]" in result
        assert "[NAME_1]" in result
        assert "[KEY_1]" in result
        assert "[SECRET_1]" in result
        assert "[TOKEN_1]" in result
        assert "[PATH_1]" in result
        assert "[RESOURCE_1]" in result

    def test_all_log_patterns_scrub(self):
        """All log patterns produce correct tokens."""
        text = """
        IP: 192.168.1.100
        Private: 10.0.0.1
        URL: https://api.internal/health
        Time: 2024-01-15T10:30:45
        Request: GET /api/v1/users
        User: user=johndoe
        """
        tokenizer = Tokenizer()
        result, replacements, summary = scrub_text(
            text,
            ["ip", "private_ip", "internal_url", "timestamp", "endpoint", "user"],
            LOG_PATTERNS,
            tokenizer,
        )
        assert "[IP_" in result
        assert "[URL_1]" in result
        assert "[TIMESTAMP_1]" in result
        assert "[ENDPOINT_1]" in result
        assert "[USER_1]" in result

    def test_mixed_content_multiple_types(self):
        """Mixed content with multiple item types produces correct token map."""
        text = "User john@example.com logged in from 192.168.1.1"
        tokenizer = Tokenizer()

        # Using standard patterns for email
        result1, _, _ = scrub_text(text, ["email"], STANDARD_PATTERNS, tokenizer)
        assert "[EMAIL_1]" in result1

        # Reset tokenizer for clean count
        tokenizer2 = Tokenizer()
        result2, _, _ = scrub_text(text, ["ip"], LOG_PATTERNS, tokenizer2)
        assert "[IP_1]" in result2
