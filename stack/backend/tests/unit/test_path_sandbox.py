"""PathSandbox utility tests."""

import tempfile
from pathlib import Path

import pytest

from utils.paths import PathSandbox


class TestPathSandbox:
    def test_resolve_valid_path(self):
        """Valid paths within sandbox resolve correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = PathSandbox(Path(tmpdir))
            result = sandbox.resolve("test.txt")
            assert result == Path(tmpdir) / "test.txt"

    def test_resolve_with_subdir(self):
        """Paths with subdir resolve to subdir."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = PathSandbox(Path(tmpdir))
            result = sandbox.resolve("test.txt", "in")
            assert result == Path(tmpdir) / "in" / "test.txt"

    def test_reject_path_traversal(self):
        """Path traversal attempts raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = PathSandbox(Path(tmpdir))
            with pytest.raises(ValueError, match="escapes sandbox"):
                sandbox.resolve("../outside.txt")

    def test_reject_absolute_path(self):
        """Absolute paths that escape sandbox raise ValueError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = PathSandbox(Path(tmpdir))
            with pytest.raises(ValueError, match="escapes sandbox"):
                sandbox.resolve("/etc/passwd")

    def test_nested_path_allowed(self):
        """Nested paths within sandbox are allowed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sandbox = PathSandbox(Path(tmpdir))
            result = sandbox.resolve("subdir/deep/file.txt")
            assert result == Path(tmpdir) / "subdir" / "deep" / "file.txt"
