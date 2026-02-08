"""Regex pattern matching and capture group tests."""

from mcp.scrubbers.core import CAPTURE_GROUP, LOG_PATTERNS, STANDARD_PATTERNS


class TestStandardPatterns:
    def test_email_matches(self):
        pattern = STANDARD_PATTERNS["email"]
        assert pattern.search("Contact: user@example.com")
        assert pattern.search("test.name@sub.domain.org")
        assert not pattern.search("not an email")

    def test_phone_matches(self):
        pattern = STANDARD_PATTERNS["phone"]
        assert pattern.search("Call 555-123-4567")
        assert pattern.search("555.123.4567")
        assert pattern.search("5551234567")

    def test_name_matches(self):
        pattern = STANDARD_PATTERNS["name"]
        assert pattern.search("Hello John Smith")
        assert not pattern.search("hello john smith")  # lowercase

    def test_api_key_matches(self):
        pattern = STANDARD_PATTERNS["api_key"]
        # Pattern: 2-6 letters + optional separator + 20+ alphanumeric
        assert pattern.search("sk-1234567890abcdefghij")
        assert pattern.search("sk-1234567890abcdefghijklmnop")
        assert pattern.search("APISECRET1234567890abcdefghij")

    def test_secret_pattern_captures_value_group(self):
        """Secret pattern extracts value (group 2), not full match."""
        pattern = STANDARD_PATTERNS["secret"]
        match = pattern.search("password=supersecret123")
        assert match
        assert match.group(CAPTURE_GROUP.get("secret", 0)) == "supersecret123"

    def test_bearer_matches(self):
        pattern = STANDARD_PATTERNS["bearer"]
        assert pattern.search(
            "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        )

    def test_path_matches(self):
        pattern = STANDARD_PATTERNS["path"]
        assert pattern.search("/home/user/documents")
        assert pattern.search("~/projects/myapp")

    def test_resource_id_matches(self):
        pattern = STANDARD_PATTERNS["resource_id"]
        # Pattern matches prefix:org:id format (10+ char final segment)
        assert pattern.search("proj:myorg:res_abc123def456")
        assert pattern.search("stripe:acct:cus_1234567890ab")


class TestLogPatterns:
    def test_ip_matches(self):
        pattern = LOG_PATTERNS["ip"]
        assert pattern.search("Request from 192.168.1.1")
        assert pattern.search("10.0.0.1")
        # Note: Pattern matches syntactically valid IPs (1-3 digits per octet)
        # Semantic validation (0-255 range) is out of scope for regex scrubbing

    def test_private_ip_matches_rfc1918(self):
        pattern = LOG_PATTERNS["private_ip"]
        assert pattern.search("10.0.0.1")
        assert pattern.search("172.16.0.1")
        assert pattern.search("192.168.1.1")
        assert not pattern.search("8.8.8.8")

    def test_internal_url_matches(self):
        pattern = LOG_PATTERNS["internal_url"]
        assert pattern.search("https://api.internal/v1/users")
        assert pattern.search("http://db.local:5432")
        assert pattern.search("https://jenkins.corp/job/build")

    def test_timestamp_alternations_no_crash(self):
        """Timestamp alternations return valid match, no None crash."""
        pattern = LOG_PATTERNS["timestamp"]
        match = pattern.search("2024-01-15T10:30:45")
        assert match
        # Should have at least one non-None group
        assert any(g is not None for g in match.groups())

    def test_endpoint_pattern_captures_path(self):
        """Endpoint pattern extracts path (group 1), not 'GET /path'."""
        pattern = LOG_PATTERNS["endpoint"]
        match = pattern.search("GET /api/v1/users")
        assert match
        assert match.group(CAPTURE_GROUP.get("endpoint", 0)) == "/api/v1/users"

    def test_user_pattern_captures_username(self):
        """User pattern extracts username (group 1), not 'user=john'."""
        pattern = LOG_PATTERNS["user"]
        match = pattern.search("user=johndoe")
        assert match
        assert match.group(CAPTURE_GROUP.get("user", 0)) == "johndoe"
