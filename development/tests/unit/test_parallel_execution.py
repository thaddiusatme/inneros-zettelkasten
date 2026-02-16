"""
Tests for Issue #94: Parallel test execution with pytest-xdist.

RED Phase: Verify xdist is importable and -n flag is accepted.
"""

import subprocess
import sys


class TestXdistAvailability:
    """pytest-xdist must be installed and importable."""

    def test_xdist_is_importable(self):
        """pytest-xdist package should be importable."""
        import xdist  # noqa: F401

    def test_xdist_plugin_registered(self):
        """pytest-xdist plugin should be registered with pytest."""
        import pytest

        pm = pytest.importorskip("xdist").plugin
        assert pm is not None

    def test_n_flag_accepted_by_pytest(self):
        """pytest should accept the -n flag without error."""
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--co",
                "-n",
                "0",
                "-q",
                "development/tests/unit/test_parallel_execution.py::TestXdistAvailability::test_xdist_is_importable",
            ],
            capture_output=True,
            text=True,
            cwd="/Users/thaddius/repos/inneros-zettelkasten",
            env={**__import__("os").environ, "PYTHONPATH": "development"},
        )
        assert result.returncode == 0, f"pytest rejected -n flag: {result.stderr}"


class TestParallelSafety:
    """Tests should not break under parallel execution."""

    def test_no_shared_global_state_mutation(self):
        """Placeholder: verify no global state issues under -n auto."""
        # This test exists to be run WITH -n auto to detect isolation issues.
        # If it passes sequentially AND in parallel, no global state problem.
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmpdir:
            marker = Path(tmpdir) / "parallel_safe.txt"
            marker.write_text("ok")
            assert marker.read_text() == "ok"
