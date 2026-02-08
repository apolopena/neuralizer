"""FastMCP server exposing scrubbing tools via stdio transport."""

from fastmcp import FastMCP

from scrubbing.scrubbers.core import (
    LOG_PATTERNS,
    STANDARD_PATTERNS,
    Tokenizer,
    scrub_text,
)
from scrubbing.scrubbers.log import scrub_log_file

mcp = FastMCP("neuralizer-scrub")


@mcp.tool()
def scrub_prompt(text: str, item_types: list[str]) -> dict:
    """Scrub a prompt using standard patterns.

    Args:
        text: Prompt text
        item_types: From Neuralizer detection (e.g., ["email", "phone", "name"])

    Returns:
        {sanitized_text, replacements, summary}
    """
    sanitized, replacements, summary = scrub_text(
        text, item_types, STANDARD_PATTERNS, Tokenizer()
    )
    return {
        "sanitized_text": sanitized,
        "replacements": replacements,
        "summary": summary,
    }


@mcp.tool()
def scrub_log_as_prompt(text: str, item_types: list[str]) -> dict:
    """Scrub log data that arrived as a prompt.

    Uses merged pattern set (LOG_PATTERNS + STANDARD_PATTERNS) to catch
    emails, API keys, and other sensitive data commonly found in logs.

    Args:
        text: Log text pasted into prompt
        item_types: From Neuralizer detection (e.g., ["ip", "endpoint", "user", "email", "api_key"])

    Returns:
        {sanitized_text, replacements, summary}
    """
    # Merge pattern sets for comprehensive log scrubbing
    merged_patterns = {**STANDARD_PATTERNS, **LOG_PATTERNS}
    sanitized, replacements, summary = scrub_text(
        text, item_types, merged_patterns, Tokenizer()
    )
    return {
        "sanitized_text": sanitized,
        "replacements": replacements,
        "summary": summary,
    }


@mcp.tool()
def scrub_log_as_file(input_path: str, output_path: str, item_types: list[str]) -> dict:
    """Scrub a log file.

    Path validation happens HERE — MCP doesn't trust the caller.

    Args:
        input_path: Filename under /data/scrub/in
        output_path: Filename under /data/scrub/out
        item_types: Types to scrub (e.g., ["ip", "user", "endpoint"])

    Returns:
        {lines_processed, items_scrubbed}
    """
    return scrub_log_file(input_path, output_path, item_types)


if __name__ == "__main__":
    mcp.run(transport="stdio")
