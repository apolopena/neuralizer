"""Path sandboxing utility — prevents path traversal attacks."""

import os
from pathlib import Path


class PathSandbox:
    """Validates paths stay within a root directory."""

    def __init__(self, root: Path):
        self.root = root.resolve()

    def resolve(self, subpath: str, subdir: str = "") -> Path:
        """Resolve path within sandbox.

        Args:
            subpath: User-provided path component
            subdir: Optional subdirectory (e.g., "in", "out")

        Returns:
            Resolved absolute path

        Raises:
            ValueError: If path escapes sandbox
        """
        base = self.root / subdir if subdir else self.root
        target = (base / subpath).resolve()

        if not target.is_relative_to(base):
            raise ValueError(f"Path escapes sandbox: {subpath}")

        return target


# Singleton for scrub data directory
SCRUB_DATA_PATH = Path(os.getenv("SCRUB_DATA_PATH", "/data/scrub"))
scrub_sandbox = PathSandbox(SCRUB_DATA_PATH)
