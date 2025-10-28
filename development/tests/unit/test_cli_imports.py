"""
Test that CLI tools can be imported and run after directory reorganization.
"""

import subprocess
import sys
from pathlib import Path


class TestCLIImports:
    """Test CLI tool imports work correctly."""

    def test_analytics_demo_help(self):
        """Test analytics_demo.py can show help."""
        result = subprocess.run(
            [sys.executable, "development/src/cli/analytics_demo.py", "--help"],
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Analytics Demo" in result.stdout or "usage:" in result.stdout

    def test_workflow_demo_help(self):
        """Test workflow_demo.py can show help."""
        result = subprocess.run(
            [sys.executable, "development/src/cli/workflow_demo.py", "--help"],
            cwd=Path(__file__).parent.parent.parent.parent,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Workflow Demo" in result.stdout or "usage:" in result.stdout
