"""Tokenizer class tests."""

from mcp.scrubbers.core import Tokenizer


class TestTokenizer:
    def test_same_value_same_token(self):
        """Same value should always return same token."""
        t = Tokenizer()
        token1 = t.tokenize("test@example.com", "EMAIL")
        token2 = t.tokenize("test@example.com", "EMAIL")
        assert token1 == token2 == "[EMAIL_1]"

    def test_different_values_different_tokens(self):
        """Different values should get different tokens."""
        t = Tokenizer()
        token1 = t.tokenize("a@example.com", "EMAIL")
        token2 = t.tokenize("b@example.com", "EMAIL")
        assert token1 == "[EMAIL_1]"
        assert token2 == "[EMAIL_2]"

    def test_different_prefixes_separate_counters(self):
        """Different prefixes should have separate counters."""
        t = Tokenizer()
        email_token = t.tokenize("a@example.com", "EMAIL")
        phone_token = t.tokenize("555-1234", "PHONE")
        assert email_token == "[EMAIL_1]"
        assert phone_token == "[PHONE_1]"

    def test_total_tokens(self):
        """Total tokens should count all unique values across prefixes."""
        t = Tokenizer()
        t.tokenize("a@example.com", "EMAIL")
        t.tokenize("b@example.com", "EMAIL")
        t.tokenize("555-1234", "PHONE")
        assert t.total_tokens == 3
