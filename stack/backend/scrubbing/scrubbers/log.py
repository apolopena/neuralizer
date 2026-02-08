"""Log file scrubbing — handles file I/O with path validation."""

from scrubbing.scrubbers.core import (
    LOG_PATTERNS,
    STANDARD_PATTERNS,
    Tokenizer,
    scrub_text,
)
from utils.paths import scrub_sandbox

# Merge pattern sets for comprehensive log scrubbing
MERGED_PATTERNS = {**STANDARD_PATTERNS, **LOG_PATTERNS}


def scrub_log_file(
    input_path: str,
    output_path: str,
    item_types: list[str],
) -> dict:
    """Scrub a log file.

    Path validation happens HERE — MCP doesn't trust the caller.

    Args:
        input_path: Filename under /data/scrub/in
        output_path: Filename under /data/scrub/out
        item_types: Types to scrub (e.g., ["ip", "user", "endpoint"])

    Returns:
        Summary dict with lines_processed, items_scrubbed

    Raises:
        ValueError: If paths escape sandbox
        FileNotFoundError: If input file doesn't exist
    """
    # Validate paths — MCP is the authority
    safe_in = scrub_sandbox.resolve(input_path, "in")
    safe_out = scrub_sandbox.resolve(output_path, "out")

    if not safe_in.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    safe_out.parent.mkdir(parents=True, exist_ok=True)

    tokenizer = Tokenizer()  # Shared across all lines for consistency
    lines_processed = 0
    items_scrubbed = 0
    total_summary: dict[str, int] = {}

    with (
        open(safe_in, encoding="utf-8", errors="replace") as infile,
        open(safe_out, "w", encoding="utf-8") as outfile,
    ):
        for line in infile:
            lines_processed += 1
            # Use merged patterns to catch emails, API keys, etc. in logs
            scrubbed_line, replacements, summary = scrub_text(
                line, item_types, MERGED_PATTERNS, tokenizer
            )
            items_scrubbed += len(replacements)
            for item_type, count in summary.items():
                total_summary[item_type] = total_summary.get(item_type, 0) + count
            outfile.write(scrubbed_line)

    return {
        "lines_processed": lines_processed,
        "items_scrubbed": items_scrubbed,
        "summary": total_summary,
    }
