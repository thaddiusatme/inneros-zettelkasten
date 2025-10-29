"""
CLI Import Smoke Tests

PURPOSE: Prevent ModuleNotFoundError issues like the daemon_cli.py bug
SCOPE: Verify all CLI modules can be imported as modules (python -m)

These tests catch:
- Incorrect absolute imports (e.g., 'from development.src...')
- Missing relative imports
- Circular import issues
- Missing dependencies

Created: 2025-10-16 (after daemon_cli import bug discovered)
"""

import pytest
import sys
import subprocess
from pathlib import Path


class TestCLIModuleImports:
    """Test that all CLI modules can be imported as Python modules."""

    def test_daemon_cli_imports_as_module(self):
        """Verify daemon_cli can be imported (catches 'from development.src' bugs)."""
        result = subprocess.run(
            [sys.executable, "-c", "from src.cli import daemon_cli"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "ModuleNotFoundError" not in result.stderr
        assert "No module named" not in result.stderr

    def test_dashboard_cli_imports_as_module(self):
        """Verify dashboard_cli can be imported."""
        result = subprocess.run(
            [sys.executable, "-c", "from src.cli import dashboard_cli"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "ModuleNotFoundError" not in result.stderr

    def test_status_cli_imports_as_module(self):
        """Verify status_cli can be imported."""
        result = subprocess.run(
            [sys.executable, "-c", "from src.cli import status_cli"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "ModuleNotFoundError" not in result.stderr

    def test_terminal_dashboard_imports_as_module(self):
        """Verify terminal_dashboard can be imported."""
        result = subprocess.run(
            [sys.executable, "-c", "from src.cli import terminal_dashboard"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"
        assert "ModuleNotFoundError" not in result.stderr


class TestCLIUtilityImports:
    """Test that all CLI utility modules can be imported."""

    def test_daemon_cli_utils_imports(self):
        """Verify daemon_cli_utils imports correctly."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.cli.daemon_cli_utils import DaemonStarter",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"

    def test_dashboard_utils_imports(self):
        """Verify dashboard_utils imports correctly."""
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from src.cli.dashboard_utils import DashboardDaemonIntegration",
            ],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"

    def test_status_utils_imports(self):
        """Verify status_utils imports correctly."""
        result = subprocess.run(
            [sys.executable, "-c", "from src.cli.status_utils import DaemonDetector"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
        )

        assert result.returncode == 0, f"Import failed: {result.stderr}"


class TestCLIModuleExecution:
    """Test that CLI modules can be executed with -m flag."""

    def test_daemon_cli_can_run_as_module(self):
        """Verify 'python -m src.cli.daemon_cli' works (the actual way inneros calls it)."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.daemon_cli", "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
            cwd=str(Path(__file__).parent.parent.parent.parent),
        )

        # Should show help, not crash with ModuleNotFoundError
        assert (
            "ModuleNotFoundError" not in result.stderr
        ), f"Module error: {result.stderr}"
        assert "daemon" in result.stdout.lower() or result.returncode == 0

    def test_dashboard_cli_can_run_as_module(self):
        """Verify 'python -m src.cli.dashboard_cli' works."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.dashboard_cli", "--help"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
            cwd=str(Path(__file__).parent.parent.parent.parent),
        )

        assert (
            "ModuleNotFoundError" not in result.stderr
        ), f"Module error: {result.stderr}"
        assert "dashboard" in result.stdout.lower() or result.returncode == 0


class TestNoAbsoluteImports:
    """Test that CLI modules don't use absolute 'development' imports."""

    def test_daemon_cli_no_development_imports(self):
        """Check that daemon_cli.py doesn't import 'from development.src...'"""
        daemon_cli_path = (
            Path(__file__).parent.parent.parent.parent / "src" / "cli" / "daemon_cli.py"
        )
        content = daemon_cli_path.read_text()

        # Should NOT have absolute imports
        assert (
            "from development.src" not in content
        ), "daemon_cli.py contains absolute 'development' imports - use relative imports!"
        assert (
            "import development.src" not in content
        ), "daemon_cli.py contains absolute 'development' imports - use relative imports!"

    def test_dashboard_cli_no_development_imports(self):
        """Check that dashboard_cli.py doesn't import 'from development.src...'"""
        dashboard_cli_path = (
            Path(__file__).parent.parent.parent.parent
            / "src"
            / "cli"
            / "dashboard_cli.py"
        )
        content = dashboard_cli_path.read_text()

        assert (
            "from development.src" not in content
        ), "dashboard_cli.py contains absolute 'development' imports - use relative imports!"

    def test_all_cli_files_use_relative_imports(self):
        """Check all CLI files use relative imports, not absolute 'development' paths."""
        cli_dir = Path(__file__).parent.parent.parent.parent / "src" / "cli"

        for py_file in cli_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            content = py_file.read_text()
            assert (
                "from development.src" not in content
            ), f"{py_file.name} contains absolute 'development' imports!"
            assert (
                "import development.src" not in content
            ), f"{py_file.name} contains absolute 'development' imports!"


class TestCLIIntegration:
    """Integration tests for actual CLI usage patterns."""

    def test_inneros_wrapper_can_call_daemon_cli(self):
        """Test that our wrapper script pattern works (what inneros command does)."""
        # This simulates what happens when user runs: inneros daemon status
        result = subprocess.run(
            [sys.executable, "-m", "src.cli.daemon_cli", "status"],
            capture_output=True,
            text=True,
            env={"PYTHONPATH": str(Path(__file__).parent.parent.parent.parent)},
            cwd=str(Path(__file__).parent.parent.parent.parent),
            timeout=5,
        )

        # Should not crash with import errors (may fail with "daemon not running" which is fine)
        assert "ModuleNotFoundError" not in result.stderr
        assert "No module named" not in result.stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
