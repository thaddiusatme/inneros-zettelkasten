"""TDD RED Phase: Tests for LogAggregator.

Issue #67: inneros-status should aggregate handler logs for true last-activity.

The LogAggregator must:
1. Scan multiple handler log files (youtube_handler_*, screenshot_handler_*, etc.)
2. Use bounded reading (tail last N lines) to avoid reading multi-MB logs fully
3. Find the most recent timestamp and status across all logs
4. Return per-handler activity with source log file attribution
"""

from pathlib import Path

import pytest

pytestmark = pytest.mark.ci


class TestLogAggregatorMultiFileSelection:
    """Tests verifying correct most-recent selection across multiple log files."""

    def test_aggregator_selects_newest_timestamp_across_handler_logs(
        self, tmp_path: Path
    ) -> None:
        """Given multiple handler logs, aggregator should return the newest activity."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)

        # Older log
        (logs_dir / "youtube_handler_2025-12-18.log").write_text(
            "2025-12-18 10:00:00 [INFO] YouTubeFeatureHandler: Processing complete\n"
            "2025-12-18 10:00:01 [INFO] YouTubeFeatureHandler: SUCCESS - 5 notes processed\n"
        )
        # Newer log (should be selected)
        (logs_dir / "youtube_handler_2025-12-19.log").write_text(
            "2025-12-19 14:30:00 [INFO] YouTubeFeatureHandler: Processing complete\n"
            "2025-12-19 14:30:01 [INFO] YouTubeFeatureHandler: SUCCESS - 3 notes processed\n"
        )

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_handler_activity("youtube_handler")

        assert result["last_timestamp"] == "2025-12-19 14:30:01"
        assert result["status"] == "success"
        assert "youtube_handler_2025-12-19.log" in result["source_log"]

    def test_aggregator_handles_multiple_handler_types(self, tmp_path: Path) -> None:
        """Aggregator should track activity for different handler types separately."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)

        # YouTube handler log
        (logs_dir / "youtube_handler_2025-12-19.log").write_text(
            "2025-12-19 14:00:00 [INFO] YouTubeFeatureHandler: SUCCESS - 3 notes\n"
        )
        # Screenshot handler log (newer)
        (logs_dir / "screenshot_handler_2025-12-19.log").write_text(
            "2025-12-19 15:00:00 [INFO] ScreenshotHandler: SUCCESS - 10 images\n"
        )
        # Smart link handler log
        (logs_dir / "smart_link_handler_2025-12-19.log").write_text(
            "2025-12-19 13:00:00 [INFO] SmartLinkHandler: SUCCESS - 5 links inserted\n"
        )

        aggregator = LogAggregator(logs_dir)
        all_activity = aggregator.get_all_handler_activity()

        assert len(all_activity) >= 3
        assert "youtube_handler" in all_activity
        assert "screenshot_handler" in all_activity
        assert "smart_link_handler" in all_activity

        # Each handler should have its own most recent timestamp
        assert (
            all_activity["youtube_handler"]["last_timestamp"] == "2025-12-19 14:00:00"
        )
        assert (
            all_activity["screenshot_handler"]["last_timestamp"]
            == "2025-12-19 15:00:00"
        )
        assert (
            all_activity["smart_link_handler"]["last_timestamp"]
            == "2025-12-19 13:00:00"
        )

    def test_aggregator_identifies_overall_most_recent_activity(
        self, tmp_path: Path
    ) -> None:
        """Aggregator should identify the single most recent activity across all handlers."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)

        (logs_dir / "youtube_handler_2025-12-19.log").write_text(
            "2025-12-19 10:00:00 [INFO] YouTubeFeatureHandler: SUCCESS\n"
        )
        (logs_dir / "screenshot_handler_2025-12-19.log").write_text(
            "2025-12-19 16:30:00 [INFO] ScreenshotHandler: SUCCESS\n"  # Most recent
        )
        (logs_dir / "smart_link_handler_2025-12-19.log").write_text(
            "2025-12-19 12:00:00 [INFO] SmartLinkHandler: SUCCESS\n"
        )

        aggregator = LogAggregator(logs_dir)
        overall = aggregator.get_overall_last_activity()

        assert overall["handler"] == "screenshot_handler"
        assert overall["last_timestamp"] == "2025-12-19 16:30:00"
        assert overall["status"] == "success"


class TestLogAggregatorGracefulDegradation:
    """Tests verifying graceful handling of missing/empty logs."""

    def test_aggregator_returns_no_data_when_logs_missing(self, tmp_path: Path) -> None:
        """When no log files exist, aggregator should return graceful 'no data' response."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)
        # No log files created

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_handler_activity("youtube_handler")

        assert result["status"] == "no_data"
        assert result["last_timestamp"] is None
        assert "no log files found" in result.get("message", "").lower()

    def test_aggregator_handles_empty_log_file(self, tmp_path: Path) -> None:
        """Empty log files should not cause crashes."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)
        (logs_dir / "youtube_handler_2025-12-19.log").write_text("")

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_handler_activity("youtube_handler")

        assert result["status"] == "no_data"
        assert result["last_timestamp"] is None

    def test_aggregator_handles_malformed_log_lines(self, tmp_path: Path) -> None:
        """Malformed log lines should be skipped without crashing."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)
        (logs_dir / "youtube_handler_2025-12-19.log").write_text(
            "This is not a valid log line\n"
            "Neither is this one\n"
            "2025-12-19 14:00:00 [INFO] Valid line: SUCCESS\n"
            "Another garbage line\n"
        )

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_handler_activity("youtube_handler")

        # Should still extract the valid line
        assert result["last_timestamp"] == "2025-12-19 14:00:00"
        assert result["status"] == "success"

    def test_aggregator_handles_nonexistent_logs_directory(
        self, tmp_path: Path
    ) -> None:
        """Non-existent logs directory should return graceful error."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        # Directory not created

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_all_handler_activity()

        assert result == {} or "error" in str(result).lower()


class TestLogAggregatorBoundedReading:
    """Tests verifying bounded log reading (no full-file read of multi-MB logs)."""

    def test_aggregator_only_reads_tail_of_large_log(self, tmp_path: Path) -> None:
        """Aggregator should only read last N lines, not entire multi-MB file."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)

        # Create a log with many lines - only last lines should be read
        old_lines = [
            f"2025-12-19 0{i}:00:00 [INFO] Old activity line {i}\n" for i in range(100)
        ]
        recent_line = (
            "2025-12-19 23:59:59 [INFO] YouTubeFeatureHandler: SUCCESS - final\n"
        )

        (logs_dir / "youtube_handler_2025-12-19.log").write_text(
            "".join(old_lines) + recent_line
        )

        aggregator = LogAggregator(logs_dir, tail_lines=50)
        result = aggregator.get_handler_activity("youtube_handler")

        # Should find the most recent line
        assert result["last_timestamp"] == "2025-12-19 23:59:59"
        assert result["status"] == "success"

    def test_aggregator_respects_configurable_tail_limit(self, tmp_path: Path) -> None:
        """Tail line limit should be configurable."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)

        # Create log where important line is beyond small tail limit
        lines = [f"2025-12-19 {i:02d}:00:00 [INFO] Line {i}\n" for i in range(20)]
        (logs_dir / "youtube_handler_2025-12-19.log").write_text("".join(lines))

        # With tail_lines=5, should only see lines 15-19
        aggregator = LogAggregator(logs_dir, tail_lines=5)
        result = aggregator.get_handler_activity("youtube_handler")

        # Should find most recent in tail
        assert result["last_timestamp"] == "2025-12-19 19:00:00"


class TestLogAggregatorStatusDetection:
    """Tests for status detection (success/failure) from log content."""

    def test_aggregator_detects_success_status(self, tmp_path: Path) -> None:
        """SUCCESS keyword should be detected as success status."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)
        (logs_dir / "youtube_handler_2025-12-19.log").write_text(
            "2025-12-19 14:00:00 [INFO] YouTubeFeatureHandler: SUCCESS - 5 notes\n"
        )

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_handler_activity("youtube_handler")

        assert result["status"] == "success"

    def test_aggregator_detects_failure_status(self, tmp_path: Path) -> None:
        """ERROR/FAILED keywords should be detected as failed status."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)
        (logs_dir / "screenshot_handler_2025-12-19.log").write_text(
            "2025-12-19 14:00:00 [ERROR] ScreenshotHandler: FAILED - OneDrive unavailable\n"
        )

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_handler_activity("screenshot_handler")

        assert result["status"] == "failed"
        assert "OneDrive unavailable" in result.get("error_snippet", "")

    def test_aggregator_extracts_error_snippet(self, tmp_path: Path) -> None:
        """When status is failed, aggregator should extract error snippet."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)
        (logs_dir / "smart_link_handler_2025-12-19.log").write_text(
            "2025-12-19 14:00:00 [INFO] Processing started\n"
            "2025-12-19 14:00:05 [ERROR] Connection timeout after 30s\n"
            "2025-12-19 14:00:06 [ERROR] SmartLinkHandler: FAILED\n"
        )

        aggregator = LogAggregator(logs_dir)
        result = aggregator.get_handler_activity("smart_link_handler")

        assert result["status"] == "failed"
        assert "timeout" in result.get("error_snippet", "").lower()


class TestLogAggregatorIntegration:
    """Integration tests for LogAggregator with system_health.py."""

    def test_aggregator_output_compatible_with_check_all_format(
        self, tmp_path: Path
    ) -> None:
        """Aggregator output should be compatible with check_all() return format."""
        from src.automation.log_aggregator import LogAggregator

        logs_dir = tmp_path / ".automation" / "logs"
        logs_dir.mkdir(parents=True)
        (logs_dir / "youtube_handler_2025-12-19.log").write_text(
            "2025-12-19 14:00:00 [INFO] YouTubeFeatureHandler: SUCCESS\n"
        )

        aggregator = LogAggregator(logs_dir)
        activity = aggregator.get_handler_activity("youtube_handler")

        # Must have keys compatible with _build_automation_entry format
        assert "last_timestamp" in activity
        assert "status" in activity
        assert "source_log" in activity

        # Status must be one of: success, failed, unknown, no_data
        assert activity["status"] in ["success", "failed", "unknown", "no_data"]
