"""
Unit tests for the fleeting note triage CLI functionality.
TDD RED Phase: All tests designed to fail until --fleeting-triage is implemented.
"""

import pytest
import tempfile
import shutil
import subprocess
import sys
import json
from pathlib import Path

# Direct testing approach - no mocking needed for CLI integration tests

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestFleetingTriageCLI:
    """Test cases for --fleeting-triage CLI command."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        self.cli_script = (
            Path(__file__).parent.parent.parent / "src" / "cli" / "workflow_demo.py"
        )

        # Create basic vault structure
        (self.vault_path / "knowledge" / "Fleeting Notes").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Inbox").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Permanent Notes").mkdir(parents=True)

        # Create sample fleeting notes for testing
        self._create_sample_fleeting_notes()

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def _create_sample_fleeting_notes(self):
        """Create sample fleeting notes for testing."""
        fleeting_dir = self.vault_path / "knowledge" / "Fleeting Notes"

        # High quality note (should be recommended for promotion)
        high_quality_note = fleeting_dir / "high-quality-note.md"
        high_quality_note.write_text(
            """---
type: fleeting
created: 2025-09-10 14:30
status: inbox
tags: [ai, productivity]
---

# High Quality AI Insight

This note contains substantial content about AI productivity patterns. It has multiple connections to [[permanent-note-1]] and [[permanent-note-2]], demonstrates clear thinking, and provides actionable insights.

The content is well-structured with evidence and examples. This represents the kind of fleeting note that should be promoted to permanent status.
"""
        )

        # Medium quality note (needs review)
        medium_quality_note = fleeting_dir / "medium-quality-note.md"
        medium_quality_note.write_text(
            """---
type: fleeting
created: 2025-09-12 10:15
status: inbox
tags: [notes]
---

# Medium Quality Note

Some interesting ideas here but needs development. Links to [[related-topic]] but could use more depth.
"""
        )

        # Low quality note (should be archived or enhanced)
        low_quality_note = fleeting_dir / "low-quality-note.md"
        low_quality_note.write_text(
            """---
type: fleeting
created: 2025-09-15 16:45
status: inbox
---

# Quick thought

Just a quick idea. Not much detail.
"""
        )

    def test_fleeting_triage_argument_parsing(self):
        """Test that --fleeting-triage argument is properly parsed."""
        # RED PHASE: This test will fail until we add --fleeting-triage to the parser
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
            ],
            capture_output=True,
            text=True,
        )

        # Should not fail with "unrecognized arguments" error
        assert (
            "unrecognized arguments" not in result.stderr
        ), f"Unexpected error: {result.stderr}"
        assert (
            result.returncode == 0
        ), f"Command failed with code {result.returncode}: {result.stderr}"

    def test_fleeting_triage_basic_output(self):
        """Test basic triage output format and content."""
        # RED PHASE: This test will fail until triage functionality is implemented
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout

        # Verify expected output sections
        assert "FLEETING NOTES TRIAGE REPORT" in output
        assert "QUALITY ASSESSMENT" in output
        assert "TRIAGE RECOMMENDATIONS" in output
        assert "BATCH PROCESSING RESULTS" in output

        # Verify quality scoring is present
        assert (
            "High Quality" in output
            or "Medium Quality" in output
            or "Low Quality" in output
        )

        # Verify recommendations are actionable
        assert (
            "Promote to Permanent" in output
            or "Needs Enhancement" in output
            or "Consider Archiving" in output
        )

    def test_fleeting_triage_with_quality_threshold(self):
        """Test triage with --min-quality threshold filtering."""
        # RED PHASE: This test will fail until quality threshold functionality is implemented
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
                "--min-quality",
                "0.7",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout

        # Should only show high-quality notes meeting threshold
        assert "Quality threshold: 0.7" in output
        assert "filtered by quality threshold" in output

    def test_fleeting_triage_json_format(self):
        """Test triage output in JSON format."""
        # RED PHASE: This test will fail until JSON format is implemented
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0

        # Parse JSON output
        try:
            triage_data = json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON output: {e}\nOutput: {result.stdout}")

        # Verify JSON structure
        assert "total_notes_processed" in triage_data
        assert "quality_distribution" in triage_data
        assert "recommendations" in triage_data
        assert "processing_time" in triage_data

        # Verify recommendations have required fields
        for rec in triage_data["recommendations"]:
            assert "note_path" in rec
            assert "quality_score" in rec
            assert "action" in rec
            assert "rationale" in rec

    def test_fleeting_triage_export_functionality(self):
        """Test export triage results to markdown file."""
        # RED PHASE: This test will fail until export functionality is implemented
        export_file = self.vault_path / "triage-results.md"

        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
                "--export",
                str(export_file),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert export_file.exists(), "Export file was not created"

        # Verify export file content
        export_content = export_file.read_text()
        assert "# Fleeting Notes Triage Report" in export_content
        assert "Quality Assessment" in export_content
        assert "Recommendations" in export_content
        assert "Generated on" in export_content

    def test_fleeting_triage_batch_processing_performance(self):
        """Test that batch processing meets performance targets (<10s for 100+ notes)."""
        # RED PHASE: This test will fail until batch processing is optimized
        import time

        # Create additional notes to test batch processing
        fleeting_dir = self.vault_path / "knowledge" / "Fleeting Notes"
        for i in range(20):  # Create 20 additional notes (23 total with setup)
            note_file = fleeting_dir / f"batch-test-note-{i}.md"
            note_file.write_text(
                f"""---
type: fleeting
created: 2025-09-{10 + (i % 7):02d} 14:30
status: inbox
tags: [test]
---

# Batch Test Note {i}

Content for batch testing note {i}. Some details and thoughts.
"""
            )

        start_time = time.time()
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
            ],
            capture_output=True,
            text=True,
        )
        processing_time = time.time() - start_time

        assert result.returncode == 0
        # Performance target: <10 seconds for 100+ notes (we have ~25 notes, so should be much faster)
        assert (
            processing_time < 5.0
        ), f"Batch processing took {processing_time:.2f}s, should be <5s for ~25 notes"

        # Verify all notes were processed
        output = result.stdout
        assert "23 notes processed" in output or "processed: 23" in output

    def test_fleeting_triage_error_handling(self):
        """Test error handling for invalid inputs and edge cases."""
        # RED PHASE: This test will fail until error handling is implemented

        # Test with non-existent directory
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                "/non/existent/path",
                "--fleeting-triage",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        error_output = (result.stderr + result.stdout).lower()
        assert "directory" in error_output and (
            "not found" in error_output or "does not exist" in error_output
        )

        # Test with invalid quality threshold
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
                "--min-quality",
                "1.5",
            ],
            capture_output=True,
            text=True,
        )

        error_output = (result.stderr + result.stdout).lower()
        assert result.returncode != 0 or "quality threshold" in error_output

    def test_fleeting_triage_integration_with_ai_workflow(self):
        """Test integration with existing AI workflow infrastructure."""
        # This test verifies that the AI workflow integration is functional
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout

        # Verify core AI integration is working
        assert "QUALITY ASSESSMENT" in output
        assert "TRIAGE RECOMMENDATIONS" in output

        # Verify processing metrics are included
        assert "BATCH PROCESSING RESULTS" in output


class TestFleetingTriageIntegration:
    """Integration tests for fleeting triage with existing CLI commands."""

    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.temp_dir)
        self.cli_script = (
            Path(__file__).parent.parent.parent / "src" / "cli" / "workflow_demo.py"
        )

        # Create basic vault structure
        (self.vault_path / "knowledge" / "Fleeting Notes").mkdir(parents=True)
        (self.vault_path / "knowledge" / "Inbox").mkdir(parents=True)

        # Create sample fleeting notes for testing
        self._create_sample_fleeting_notes()

    def _create_sample_fleeting_notes(self):
        """Create sample fleeting notes for testing."""
        fleeting_dir = self.vault_path / "knowledge" / "Fleeting Notes"

        # Create a test note
        test_note = fleeting_dir / "test-note.md"
        test_note.write_text(
            """---
type: fleeting
created: 2025-09-10 14:30
status: inbox
tags: [test]
---

# Test Note

Some content for testing.
"""
        )

    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_triage_does_not_break_existing_commands(self):
        """Test that adding --fleeting-triage doesn't break existing CLI commands."""
        # RED PHASE: This test ensures we don't break existing functionality

        # Test that --fleeting-health still works
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-health",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "FLEETING NOTES HEALTH REPORT" in result.stdout

        # Test that --status still works
        result = subprocess.run(
            [sys.executable, str(self.cli_script), str(self.vault_path), "--status"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "WORKFLOW STATUS" in result.stdout

    def test_triage_follows_cli_output_formatting_patterns(self):
        """Test that triage output follows established CLI formatting patterns."""
        # RED PHASE: This test will fail until formatting is consistent
        result = subprocess.run(
            [
                sys.executable,
                str(self.cli_script),
                str(self.vault_path),
                "--fleeting-triage",
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        output = result.stdout

        # Should follow same formatting patterns as other commands
        assert "=" * 60 in output  # Header formatting
        assert "🔄" in output  # Section emoji formatting
        assert "-" * 40 in output  # Section divider formatting

        # Should use consistent status emojis
        assert any(emoji in output for emoji in ["✅", "⚠️", "🚨", "📄"])
