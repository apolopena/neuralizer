"""Core scrubbing utilities — Tokenizer and pattern definitions."""

import re


class Tokenizer:
    """Stateful tokenizer for consistent value→token replacement."""

    def __init__(self):
        self.maps: dict[str, dict[str, str]] = {}  # prefix → {value → token}
        self.counters: dict[str, int] = {}

    def tokenize(self, value: str, prefix: str) -> str:
        """Get or create token for a value."""
        if prefix not in self.maps:
            self.maps[prefix] = {}
            self.counters[prefix] = 0

        if value in self.maps[prefix]:
            return self.maps[prefix][value]

        self.counters[prefix] += 1
        token = f"[{prefix}_{self.counters[prefix]}]"
        self.maps[prefix][value] = token
        return token

    @property
    def total_tokens(self) -> int:
        return sum(len(m) for m in self.maps.values())


# Standard patterns (for prompts, not logs)
STANDARD_PATTERNS: dict[str, re.Pattern] = {
    "email": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
    "phone": re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "name": re.compile(r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"),
    "api_key": re.compile(r"\b[a-zA-Z]{2,6}[-_]?[a-zA-Z0-9]{20,}\b"),
    "secret": re.compile(
        r"(?i)(secret|token|password|passwd|pwd|apikey|api_key|auth)"
        r"\s*[=:]\s*['\"]?([^\s'\"]{8,})['\"]?"
    ),
    "bearer": re.compile(r"Bearer\s+[a-zA-Z0-9._-]{20,}"),
    "path": re.compile(r"(?:/[\w.-]+){2,}|~/?[\w.-/]+"),
    "resource_id": re.compile(r"\b[a-z]{2,10}[-:][a-z0-9-]+[-:][a-zA-Z0-9/_-]{10,}\b"),
}

# Log patterns (for log data)
LOG_PATTERNS: dict[str, re.Pattern] = {
    "ip": re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"),
    "private_ip": re.compile(
        r"\b(10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        r"|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
        r"|192\.168\.\d{1,3}\.\d{1,3})\b"
    ),
    "internal_url": re.compile(
        r"https?://[\w.-]+\.(internal|local|corp|lan|private)\b\S*"
    ),
    "timestamp": re.compile(
        r"(\d{4}[-/:]\d{2}[-/:]\d{2}[T\s]\d{2}:\d{2}:\d{2})"
        r"|(\d{2}:\d{2}:\d{2}[,\.]\d{3})"
    ),
    "endpoint": re.compile(r"(?:GET|POST|PUT|DELETE|PATCH)\s+(/\S+)"),
    "user": re.compile(r"(?:user|uid|username)[=:\s]+([a-zA-Z0-9_.-]+)", re.IGNORECASE),
    # Terminal command output patterns (whoami, id, logname)
    "terminal_user": re.compile(
        r"(?:^|\n)(?:❯\s*)?(?:whoami|id|logname)\s*\n([a-zA-Z0-9_.-]+)",
        re.MULTILINE,
    ),
}

# Token prefixes
TOKEN_PREFIX: dict[str, str] = {
    "email": "EMAIL",
    "phone": "PHONE",
    "name": "NAME",
    "api_key": "KEY",
    "secret": "SECRET",
    "bearer": "TOKEN",
    "path": "PATH",
    "resource_id": "RESOURCE",
    "ip": "IP",
    "private_ip": "IP",
    "internal_url": "URL",
    "timestamp": "TIMESTAMP",
    "endpoint": "ENDPOINT",
    "user": "USER",
    "terminal_user": "USER",
}

# Which capture group contains the value to tokenize (default: 0 = full match)
CAPTURE_GROUP: dict[str, int] = {
    "secret": 2,  # (keyword)(value) — want value
    "endpoint": 1,  # GET (/path) — want path only
    "user": 1,  # user=(/value/) — want value only
    "terminal_user": 1,  # whoami\n(username) — want username only
}


def scrub_text(
    text: str,
    item_types: list[str],
    patterns: dict[str, re.Pattern],
    tokenizer: Tokenizer,
) -> tuple[str, list[dict], dict[str, int]]:
    """Core scrub function — extract matches and tokenize using span positions.

    Uses span-based replacement (match positions) instead of global str.replace
    to avoid over-replacing values that appear in non-sensitive contexts.

    Args:
        text: Text to scrub
        item_types: List of item types to find
        patterns: Pattern set to use (STANDARD_PATTERNS or LOG_PATTERNS)
        tokenizer: Shared tokenizer instance

    Returns:
        (scrubbed_text, list of {replacement, item_type}, summary counts by type)
    """
    # Collect matches with their spans
    matches: list[tuple[int, int, str, str]] = []  # (start, end, value, item_type)
    for item_type in item_types:
        pattern = patterns.get(item_type)
        if not pattern:
            continue
        for match in pattern.finditer(text):
            group_idx = CAPTURE_GROUP.get(item_type, 0)
            value = match.group(group_idx)
            if value:  # Guard against None from alternations
                # Get span of the specific capture group
                start, end = match.span(group_idx)
                matches.append((start, end, value, item_type))

    # Sort by span length descending (longest match wins for overlaps)
    matches.sort(key=lambda x: x[1] - x[0], reverse=True)

    # Select non-overlapping matches (longest first)
    selected: list[tuple[int, int, str, str]] = []
    for start, end, value, item_type in matches:
        # Check if this span overlaps with any already-selected span
        overlaps = any(
            not (end <= sel_start or start >= sel_end)
            for sel_start, sel_end, _, _ in selected
        )
        if not overlaps:
            selected.append((start, end, value, item_type))

    # Sort selected by start position descending (replace from end to preserve positions)
    selected.sort(key=lambda x: x[0], reverse=True)

    # Replace using spans (end-to-start preserves positions)
    result = text
    replacements = []
    summary: dict[str, int] = {}

    for start, end, value, item_type in selected:
        prefix = TOKEN_PREFIX.get(item_type, "TOKEN")
        replacement = tokenizer.tokenize(value, prefix)
        result = result[:start] + replacement + result[end:]

        replacements.append(
            {
                "replacement": replacement,
                "item_type": item_type,
            }
        )
        summary[item_type] = summary.get(item_type, 0) + 1

    return result, replacements, summary
