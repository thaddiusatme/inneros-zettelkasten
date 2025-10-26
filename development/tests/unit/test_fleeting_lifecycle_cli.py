"""
Unit tests for the fleeting note lifecycle CLI functionality.
"""

import pytest
import tempfile
import shutil
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))



class TestFleetingHealthCLI:
    """Test cases for --fleeting-health CLI command."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        self.cli_script = Path(__file__).parent.parent.parent / "src" / "cli" / "workflow_demo.py"

        # Create basic vault structure
        (self.vault_path / "knowledge" / "Fleeting Notes").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Inbox").mkdir(parents=True)

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_fleeting_health_argument_parsing(self):
        """Test that --fleeting-health argument is properly parsed."""
        # This test will fail until we add the argument to the parser
        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-health"
        ], capture_output=True, text=True)

        # Should not fail with "unrecognized arguments" error
        assert "unrecognized arguments" not in result.stderr
        assert result.returncode == 0

    def test_fleeting_health_basic_output(self):
        """Test basic fleeting health report output format."""
        # Create some test fleeting notes
        self._create_test_fleeting_note("old-note.md", days_ago=100)
        self._create_test_fleeting_note("recent-note.md", days_ago=5)

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-health"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = result.stdout

        # Should contain health report sections
        assert "FLEETING NOTES HEALTH REPORT" in output
        assert "Health Status:" in output
        assert "Total Notes:" in output
        assert "AGE DISTRIBUTION" in output
        assert "RECOMMENDATIONS" in output

    def test_fleeting_health_with_json_format(self):
        """Test fleeting health report with JSON output format."""
        self._create_test_fleeting_note("test-note.md", days_ago=10)

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-health", "--format", "json"
        ], capture_output=True, text=True)

        assert result.returncode == 0

        # Should be valid JSON
        try:
            data = json.loads(result.stdout)
            assert "health_status" in data
            assert "total_count" in data
            assert "age_distribution" in data
            assert "recommendations" in data
        except json.JSONDecodeError:
            pytest.fail("Output should be valid JSON")

    def test_fleeting_health_empty_vault(self):
        """Test fleeting health report with no fleeting notes."""
        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-health"
        ], capture_output=True, text=True)

        assert result.returncode == 0
        output = result.stdout

        # Should handle empty vault gracefully
        assert "Total Notes: 0" in output
        assert "HEALTHY" in output

    def test_fleeting_health_performance(self):
        """Test that fleeting health command completes within performance target."""
        # Create multiple test notes
        for i in range(10):
            self._create_test_fleeting_note(f"note-{i}.md", days_ago=i*10)

        start_time = datetime.now()

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-health"
        ], capture_output=True, text=True)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        assert result.returncode == 0
        # Performance target: <3 seconds for 100+ notes (we're testing with 10)
        assert duration < 3.0, f"Command took {duration:.2f}s, should be <3s"

    def test_fleeting_health_with_export(self):
        """Test fleeting health report with export functionality."""
        self._create_test_fleeting_note("test-note.md", days_ago=30)
        export_path = self.vault_path / "health-report.md"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            str(self.vault_path), "--fleeting-health", "--export", str(export_path)
        ], capture_output=True, text=True)

        assert result.returncode == 0
        assert export_path.exists()

        # Exported file should contain health report
        content = export_path.read_text()
        assert "FLEETING NOTES HEALTH REPORT" in content

    def test_fleeting_health_error_handling(self):
        """Test error handling for invalid vault paths."""
        invalid_path = "/nonexistent/path"

        result = subprocess.run([
            sys.executable, str(self.cli_script),
            invalid_path, "--fleeting-health"
        ], capture_output=True, text=True)

        # Should handle errors gracefully (not crash)
        # Return code may be non-zero, but should not be a Python traceback
        assert "Traceback" not in result.stderr

    def _create_test_fleeting_note(self, filename: str, days_ago: int = 0):
        """Helper method to create test fleeting notes."""
        note_path = self.vault_path / "knowledge" / "Fleeting Notes" / filename
        created_date = datetime.now() - timedelta(days=days_ago)

        content = f"""---
type: fleeting
created: {created_date.strftime('%Y-%m-%d %H:%M')}
status: inbox
tags: [test-note]
---

# Test Note

This is a test fleeting note created {days_ago} days ago.
"""

        note_path.write_text(content)

        # Set file modification time to match created date
        import os
        timestamp = created_date.timestamp()
        os.utime(note_path, (timestamp, timestamp))


class TestFleetingHealthIntegration:
    """Integration tests for fleeting health CLI with WorkflowManager."""

    def test_cli_output_formatting_matches_other_commands(self):
        """Test that fleeting health output follows established CLI formatting patterns."""
        with tempfile.TemporaryDirectory() as temp_dir:
            vault_path = Path(temp_dir)
            (vault_path / "knowledge").mkdir()

            cli_script = Path(__file__).parent.parent.parent / "src" / "cli" / "workflow_demo.py"

            # Test fleeting health output
            result = subprocess.run([
                sys.executable, str(cli_script),
                str(vault_path), "--fleeting-health"
            ], capture_output=True, text=True)

            output = result.stdout

            # Should follow established patterns from other commands
            # Headers should use consistent formatting
            assert "=" in output  # Header formatting
            assert "🔄" in output or "📊" in output  # Section emojis
            assert result.returncode == 0
