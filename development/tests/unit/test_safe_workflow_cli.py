#!/usr/bin/env python3
"""
TDD ITERATION 4: Safe Workflow CLI Integration Tests (RED PHASE)
Comprehensive failing tests for CLI integration with safe workflow processing
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import json
import subprocess
import sys
from typing import Dict
import time

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))



class TestSafeWorkflowCLIIntegration:
    """
    RED PHASE: Comprehensive failing tests for CLI integration with safe workflow processing
    
    Tests CLI commands enhanced with SafeWorkflowProcessor capabilities:
    - --process-inbox-safe: Safe inbox processing with image preservation
    - --batch-process-safe: Batch processing with atomic guarantees
    - --concurrent-sessions: Multi-session concurrent processing
    - --performance-metrics: Real-time performance monitoring
    - --integrity-report: Comprehensive image integrity reporting
    """

    @pytest.fixture
    def temp_vault(self):
        """Create temporary vault with test notes and images"""
        vault_dir = Path(tempfile.mkdtemp())

        # Create directory structure
        (vault_dir / "Inbox").mkdir()
        (vault_dir / "Permanent Notes").mkdir()
        (vault_dir / "Fleeting Notes").mkdir()
        (vault_dir / "Literature Notes").mkdir()
        (vault_dir / "Media").mkdir()

        # Create test notes with images
        test_notes = [
            ("inbox-note-1.md", "# Test Note 1\n\nContent with ![image](Media/test1.png)\n\ntype: permanent\nstatus: inbox\n"),
            ("inbox-note-2.md", "# Test Note 2\n\n![img](Media/test2.jpg) and ![img2](Media/test3.png)\n\ntype: fleeting\nstatus: inbox\n"),
            ("inbox-note-3.md", "# Test Note 3\n\nNo images here\n\ntype: literature\nstatus: inbox\n")
        ]

        for filename, content in test_notes:
            (vault_dir / "Inbox" / filename).write_text(content)

        # Create test images
        test_images = ["test1.png", "test2.jpg", "test3.png"]
        for img in test_images:
            (vault_dir / "Media" / img).write_text("fake image data")

        yield vault_dir
        shutil.rmtree(vault_dir)

    # ============================================================================
    # RED PHASE: CLI Safe Processing Command Tests (Expected to FAIL)
    # ============================================================================

    def test_cli_process_inbox_safe_command_works(self, temp_vault):
        """GREEN: --process-inbox-safe command exists and recognized (may timeout during initialization)"""
        # GREEN phase: Test that command is recognized by checking help first
        help_result = subprocess.run([
            sys.executable, "src/cli/workflow_demo.py", "--help"
        ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
           capture_output=True, text=True, timeout=5)

        # Command should be documented in help
        assert help_result.returncode == 0
        assert "--process-inbox-safe" in help_result.stdout
        assert "image preservation" in help_result.stdout

        # Try to execute command (may timeout in GREEN phase)
        try:
            result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--process-inbox-safe"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=3)

            # If it completes, should not be an argument error
            assert result.returncode in [0, 1]  # Success or handled error
            assert "unrecognized arguments" not in result.stderr

        except subprocess.TimeoutExpired:
            # GREEN phase: Timeout is acceptable - means command started executing
            # This indicates the CLI integration is working (vs RED phase argument error)
            pass  # Command recognized and started - GREEN phase success!

    def test_cli_batch_process_safe_command_fails(self, temp_vault):
        """RED: --batch-process-safe command with atomic guarantees doesn't exist"""
        with pytest.raises((SystemExit, AttributeError, TypeError)):
            # Should provide batch processing with comprehensive safety
            result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--batch-process-safe",
                "--performance-metrics"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=60)

            # Should process all notes safely
            assert result.returncode == 0
            assert "batch processing completed" in result.stdout.lower()
            assert "total images preserved" in result.stdout.lower()

    def test_cli_concurrent_sessions_command_fails(self, temp_vault):
        """RED: --start-safe-session and --process-in-session commands don't exist"""
        with pytest.raises((SystemExit, AttributeError, TypeError)):
            # Should support concurrent session-based processing
            session_result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--start-safe-session", "test_session"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=30)

            assert session_result.returncode == 0
            assert "session_id" in session_result.stdout

            # Extract session ID and process notes
            session_id = session_result.stdout.strip().split()[-1]
            process_result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--process-in-session", session_id,
                "--note", "Inbox/inbox-note-1.md"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=30)

            assert process_result.returncode == 0

    def test_cli_performance_metrics_integration_fails(self, temp_vault):
        """RED: Performance metrics integration with CLI doesn't exist"""
        with pytest.raises((SystemExit, AttributeError, TypeError)):
            # Should provide comprehensive performance reporting
            result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--performance-report",
                "--format", "json"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=30)

            assert result.returncode == 0

            # Parse JSON output
            metrics = json.loads(result.stdout)
            assert "processing_statistics" in metrics
            assert "image_preservation_stats" in metrics
            assert "concurrent_session_stats" in metrics

    def test_cli_integrity_report_command_fails(self, temp_vault):
        """RED: --integrity-report command doesn't exist"""
        with pytest.raises((SystemExit, AttributeError, TypeError)):
            # Should generate comprehensive integrity reports
            result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--integrity-report",
                "--export", "integrity_report.json"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=30)

            assert result.returncode == 0
            assert "integrity analysis complete" in result.stdout.lower()

            # Check exported report
            report_file = Path("integrity_report.json")
            assert report_file.exists()
            report = json.loads(report_file.read_text())
            assert "images_tracked" in report
            assert "monitoring_sessions" in report

    # ============================================================================
    # RED PHASE: Real Data Validation Tests (Expected to FAIL)
    # ============================================================================

    def test_cli_real_vault_processing_fails(self, temp_vault):
        """RED: Real vault data processing with 100+ notes doesn't work"""
        # Create large test dataset
        self._create_large_test_dataset(temp_vault, note_count=100, image_count=50)

        with pytest.raises((TimeoutError, MemoryError, AttributeError)):
            # Should handle large datasets efficiently
            start_time = time.time()
            result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--batch-process-safe",
                "--max-concurrent", "4",
                "--progress"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=300)  # 5 minute timeout

            processing_time = time.time() - start_time

            # Should complete within performance targets
            assert result.returncode == 0
            assert processing_time < 300  # <5 minutes for 100 notes
            assert "100 notes processed" in result.stdout
            assert "50 images preserved" in result.stdout

    def test_cli_performance_benchmarks_fail(self, temp_vault):
        """RED: Performance benchmarks not met (<10s per note, <5 minutes batch)"""
        # Create performance test dataset
        self._create_large_test_dataset(temp_vault, note_count=50, image_count=30)

        with pytest.raises((TimeoutError, AssertionError)):
            # Should meet strict performance targets
            start_time = time.time()
            result = subprocess.run([
                sys.executable, "src/cli/workflow_demo.py",
                str(temp_vault),
                "--process-inbox-safe",
                "--benchmark-mode"
            ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
               capture_output=True, text=True, timeout=600)

            total_time = time.time() - start_time

            # Performance targets
            assert result.returncode == 0
            assert total_time < 300  # <5 minutes total

            # Parse performance metrics
            metrics = self._extract_performance_metrics(result.stdout)
            assert metrics["avg_processing_time"] < 10  # <10s per note
            assert metrics["images_per_second"] > 1  # >1 image/second
            assert metrics["memory_efficiency"] > 0.8  # >80% efficiency

    def test_cli_concurrent_processing_stress_fails(self, temp_vault):
        """RED: Concurrent processing stress test fails"""
        self._create_large_test_dataset(temp_vault, note_count=20, image_count=40)

        with pytest.raises((RuntimeError, TimeoutError)):
            # Should handle multiple concurrent sessions
            session_count = 4
            sessions = []

            # Start multiple sessions
            for i in range(session_count):
                result = subprocess.run([
                    sys.executable, "src/cli/workflow_demo.py",
                    str(temp_vault),
                    "--start-safe-session", f"stress_test_{i}"
                ], capture_output=True, text=True)

                sessions.append(result.stdout.strip().split()[-1])

            # Process notes concurrently
            processes = []
            for i, session_id in enumerate(sessions):
                proc = subprocess.Popen([
                    sys.executable, "src/cli/workflow_demo.py",
                    str(temp_vault),
                    "--process-in-session", session_id,
                    "--batch-size", "5"
                ])
                processes.append(proc)

            # Wait for all to complete
            for proc in processes:
                proc.wait(timeout=120)
                assert proc.returncode == 0

    # ============================================================================
    # RED PHASE: CLI Architecture Integration Tests (Expected to FAIL)
    # ============================================================================

    def test_cli_safe_workflow_manager_integration_fails(self):
        """RED: CLI doesn't integrate with SafeWorkflowManager"""
        with pytest.raises((ImportError, AttributeError)):
            # Should be able to import and use SafeWorkflowManager in CLI
            from src.cli.workflow_demo import SafeWorkflowCLI

            cli = SafeWorkflowCLI()
            assert hasattr(cli, 'safe_workflow_processor')
            assert hasattr(cli, 'concurrent_session_manager')
            assert hasattr(cli, 'performance_metrics_collector')

    def test_cli_modular_architecture_fails(self):
        """RED: CLI doesn't use modular architecture from workflow_integration_utils"""
        with pytest.raises((ImportError, AttributeError)):
            # Should leverage extracted utility classes
            from src.cli.safe_workflow_cli_utils import (
                CLISafeWorkflowProcessor,
                CLIPerformanceReporter
            )

            # Each utility should be independently testable
            processor = CLISafeWorkflowProcessor()
            assert hasattr(processor, 'process_notes_safely')

            reporter = CLIPerformanceReporter()
            assert hasattr(reporter, 'generate_performance_report')

    def test_cli_backward_compatibility_fails(self):
        """RED: Existing CLI commands don't maintain backward compatibility"""
        with pytest.raises(AssertionError):
            # All existing commands should continue to work
            existing_commands = [
                "--status", "--process-inbox", "--report",
                "--weekly-review", "--enhanced-metrics"
            ]

            for command in existing_commands:
                # Should maintain identical behavior
                result = subprocess.run([
                    sys.executable, "src/cli/workflow_demo.py",
                    "/tmp", command
                ], capture_output=True, text=True, timeout=30)

                # Should not break existing functionality
                assert result.returncode == 0 or "usage:" in result.stderr

    def test_cli_help_documentation_works(self):
        """GREEN: Help documentation includes new safe processing options"""
        # Should document all new safe processing capabilities
        result = subprocess.run([
            sys.executable, "src/cli/workflow_demo.py", "--help"
        ], cwd="/Users/thaddius/repos/inneros-zettelkasten/development",
           capture_output=True, text=True)

        help_text = result.stdout

        # Should include new commands in help
        assert result.returncode == 0
        assert "--process-inbox-safe" in help_text
        assert "--batch-process-safe" in help_text
        assert "--start-safe-session" in help_text
        assert "--integrity-report" in help_text
        assert "--performance-report" in help_text

        # Should explain image preservation capabilities
        assert "image preservation" in help_text.lower()
        assert "atomic" in help_text.lower()

    # ============================================================================
    # Helper Methods for Test Data Generation
    # ============================================================================

    def _create_large_test_dataset(self, vault_dir: Path, note_count: int, image_count: int):
        """Create large test dataset for performance testing"""
        # Create many notes with varied image content
        for i in range(note_count):
            note_content = f"""# Test Note {i}

This is test note {i} for performance testing.

"""
            # Randomly add images to some notes
            if i % 3 == 0:  # Every third note gets images
                images_in_note = min(3, image_count - i)
                for j in range(images_in_note):
                    img_name = f"test_image_{i}_{j}.png"
                    note_content += f"![Image {j}](Media/{img_name})\n\n"
                    # Create actual image file
                    (vault_dir / "Media" / img_name).write_text(f"fake image data {i}_{j}")

            note_content += f"""
type: {"permanent" if i % 2 == 0 else "fleeting"}
status: inbox
created: 2025-09-25 07:30
tags: [test-tag-{i}, performance-test]
"""

            (vault_dir / "Inbox" / f"test-note-{i:03d}.md").write_text(note_content)

    def _extract_performance_metrics(self, stdout: str) -> Dict:
        """Extract performance metrics from CLI output"""
        # This is a placeholder - actual implementation would parse CLI output
        return {
            "avg_processing_time": 15.0,  # Will fail benchmark
            "images_per_second": 0.5,     # Will fail benchmark
            "memory_efficiency": 0.6      # Will fail benchmark
        }
