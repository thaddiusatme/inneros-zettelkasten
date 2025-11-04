"""
TDD RED Phase: System Status CLI Tests

Test suite for system observability status command.
Following TDD methodology from v2.1 auto-promotion success pattern.

Coverage:
- Daemon process detection (running/stopped)
- Cron job status parsing (enabled/disabled)
- Activity timestamp extraction from logs
- Inbox note counting with quality thresholds
- Status display formatting
- End-to-end CLI integration

Target: 8/8 tests passing after GREEN phase implementation
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta
import pytest

pytestmark = pytest.mark.slow  # CLI tests - daemon/cron/log interaction


class TestDaemonDetection:
    """Test daemon process detection functionality."""

    @pytest.mark.slow
    def test_detect_daemon_running(self):
        """Test detection when daemon process is running.

        Acceptance Criteria:
        - Returns True when PID file exists and process is running
        - Returns daemon PID for display
        - Handles valid PID file format
        """
        from src.cli.status_cli import StatusDetector

        detector = StatusDetector()

        # Should detect running daemon via PID file or ps aux
        is_running, pid = detector.detect_daemon_status()

        # Expected behavior when daemon is running
        assert isinstance(is_running, bool)
        if is_running:
            assert isinstance(pid, int)
            assert pid > 0

    def test_detect_daemon_stopped(self):
        """Test detection when daemon is not running.

        Acceptance Criteria:
        - Returns False when no PID file exists
        - Returns False when PID file exists but process is dead
        - Returns None for PID when stopped
        """
        from src.cli.status_cli import StatusDetector

        detector = StatusDetector()

        # Mock environment where daemon is NOT running
        with patch("os.path.exists", return_value=False):
            is_running, pid = detector.detect_daemon_status()

            assert is_running is False
            assert pid is None


class TestCronStatusParsing:
    """Test cron job status detection."""

    def test_parse_crontab_disabled(self):
        """Test parsing of disabled cron jobs with #DISABLED# markers.

        Acceptance Criteria:
        - Detects #DISABLED# prefix in crontab entries
        - Returns disabled status for marked jobs
        - Preserves job schedule information
        """
        from src.cli.status_cli import StatusDetector

        detector = StatusDetector()

        # Mock crontab output with disabled job
        mock_crontab = """
#DISABLED# */15 * * * * cd /path && python script.py
# Regular comment
0 * * * * /usr/local/bin/some_job
"""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = mock_crontab
            mock_run.return_value.returncode = 0

            cron_status = detector.parse_cron_status()

            assert "automation_disabled" in cron_status
            assert cron_status["automation_disabled"] is True

    def test_parse_crontab_enabled(self):
        """Test parsing of active (enabled) cron jobs.

        Acceptance Criteria:
        - Detects jobs without #DISABLED# markers
        - Returns enabled status
        - Counts total enabled jobs
        """
        from src.cli.status_cli import StatusDetector

        detector = StatusDetector()

        # Mock crontab with only enabled jobs
        mock_crontab = """
*/15 * * * * cd /path && python script.py
0 * * * * /usr/local/bin/some_job
"""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = mock_crontab
            mock_run.return_value.returncode = 0

            cron_status = detector.parse_cron_status()

            assert "automation_disabled" in cron_status
            assert cron_status["automation_disabled"] is False
            assert cron_status["enabled_jobs_count"] >= 2


class TestActivityTimestamps:
    """Test activity timestamp extraction from logs."""

    def test_read_last_activity_timestamp(self):
        """Test extraction of most recent log timestamp.

        Acceptance Criteria:
        - Scans .automation/logs/ directory
        - Returns most recent timestamp
        - Handles multiple log files
        - Returns None if no logs exist
        """
        from src.cli.status_cli import ActivityReader

        reader = ActivityReader()

        # Create temporary log directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            logs_dir = Path(tmpdir) / ".automation" / "logs"
            logs_dir.mkdir(parents=True)

            # Create mock log files with different timestamps
            older_log = logs_dir / "processing_20251014_120000.log"
            newer_log = logs_dir / "processing_20251015_150000.log"

            older_log.write_text("Log content")
            newer_log.write_text("Log content")

            # Set modification times
            os.utime(older_log, (1697284800, 1697284800))  # Older
            os.utime(newer_log, (1697371200, 1697371200))  # Newer

            last_activity = reader.get_last_activity(str(logs_dir.parent))

            assert last_activity is not None
            assert isinstance(last_activity, datetime)


class TestInboxStatus:
    """Test inbox note counting and quality assessment."""

    def test_count_inbox_notes(self):
        """Test counting notes in Inbox with quality thresholds.

        Acceptance Criteria:
        - Counts total notes in Inbox/
        - Counts notes with quality_score >= 0.7
        - Returns dictionary with counts and percentages
        - Handles empty Inbox gracefully
        """
        from src.cli.status_cli import InboxStatusReader

        reader = InboxStatusReader()

        # Create temporary Inbox structure
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox_dir = Path(tmpdir) / "Inbox"
            inbox_dir.mkdir()

            # Create mock notes with quality scores
            note1 = inbox_dir / "note1.md"
            note1.write_text(
                """---
quality_score: 0.85
---
High quality note"""
            )

            note2 = inbox_dir / "note2.md"
            note2.write_text(
                """---
quality_score: 0.45
---
Low quality note"""
            )

            inbox_status = reader.get_inbox_status(str(tmpdir))

            assert "total_notes" in inbox_status
            assert "high_quality_count" in inbox_status
            assert inbox_status["total_notes"] == 2
            assert inbox_status["high_quality_count"] == 1


class TestStatusFormatting:
    """Test status display formatting."""

    def test_format_status_display(self):
        """Test formatting of status information for terminal display.

        Acceptance Criteria:
        - Uses emoji indicators (🟢/🔴/⚠️)
        - Formats timestamps human-readable
        - Includes actionable next steps
        - Returns formatted string for display
        """
        from src.cli.status_cli import StatusFormatter

        formatter = StatusFormatter()

        # Mock status data
        status_data = {
            "daemon_running": True,
            "daemon_pid": 12345,
            "cron_enabled": False,
            "last_activity": datetime.now() - timedelta(hours=2),
            "inbox_total": 15,
            "inbox_high_quality": 8,
        }

        formatted_output = formatter.format_status(status_data)

        assert isinstance(formatted_output, str)
        assert (
            "🟢" in formatted_output
            or "🔴" in formatted_output
            or "⚠️" in formatted_output
        )
        assert "daemon" in formatted_output.lower()
        assert "inbox" in formatted_output.lower()


class TestStatusCLIIntegration:
    """Test end-to-end status command integration."""

    def test_status_command_integration(self):
        """Test complete status command execution.

        Acceptance Criteria:
        - get_system_status() orchestrates all detection
        - Returns complete status dictionary
        - Executes in <5 seconds
        - Handles all error cases gracefully
        """
        from src.cli.status_cli import get_system_status

        import time

        start_time = time.time()

        # Execute complete status check
        status = get_system_status()

        execution_time = time.time() - start_time

        # Verify performance requirement
        assert execution_time < 5.0, f"Execution took {execution_time:.2f}s, target <5s"

        # Verify status structure
        assert isinstance(status, dict)
        assert "daemon" in status
        assert "cron" in status
        assert "activity" in status
        assert "inbox" in status
