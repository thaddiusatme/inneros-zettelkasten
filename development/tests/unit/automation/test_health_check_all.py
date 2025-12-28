"""TDD RED Phase: Enhanced tests for standalone check_all() function.

Issue #50: Shared Health Module - Tests for PID file detection,
stale PID handling, missing config, and performance requirements.

These tests verify that check_all() works without a daemon instance
and handles edge cases robustly.
"""

import os
import time
from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch


def _write_daemon_registry_with_pid(tmp_path: Path) -> Path:
    """Create daemon_registry.yaml with PID file configuration.

    This simulates the Python daemon configuration that uses PID files
    for detection instead of ps aux script path matching.
    """
    config_dir = tmp_path / ".automation" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    registry_path = config_dir / "daemon_registry.yaml"
    registry_path.write_text(
        """
daemons:
  - name: inneros_daemon
    script_path: development/src/automation/daemon.py
    pid_file: ~/.inneros/daemon.pid
    log_path: .automation/logs/daemon.log
""".lstrip()
    )
    return tmp_path


def _write_empty_daemon_registry(tmp_path: Path) -> Path:
    """Create empty daemon_registry.yaml."""
    config_dir = tmp_path / ".automation" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    registry_path = config_dir / "daemon_registry.yaml"
    registry_path.write_text("daemons: []\n")
    return tmp_path


class TestCheckAllPIDFileDetection:
    """Tests for PID file-based daemon detection in check_all().

    These tests verify the critical path where check_all() must inspect
    PID files to determine if the daemon is running without requiring
    a daemon instance.
    """

    def test_check_all_daemon_running_via_pid_file(self, tmp_path: Path) -> None:
        """When PID file exists and process is running, report daemon as running.

        RED Phase: This test verifies that check_all() correctly detects
        a running daemon using PID file inspection.
        """
        repo_root = _write_daemon_registry_with_pid(tmp_path)

        # Create fake PID file with current process ID (guaranteed to exist)
        pid_dir = tmp_path / ".inneros"
        pid_dir.mkdir(parents=True, exist_ok=True)
        pid_file = pid_dir / "daemon.pid"
        pid_file.write_text(str(os.getpid()))

        from src.automation.system_health import check_all

        # Mock DaemonDetector to simulate running daemon detection
        with patch(
            "src.automation.system_health.DaemonDetector"
        ) as MockDetector, patch(
            "src.automation.system_health.LogParser"
        ) as MockParser:
            detector = MockDetector.return_value
            detector.check_daemon_by_pid_file.return_value = {
                "running": True,
                "pid": os.getpid(),
            }

            parser = MockParser.return_value
            parser.parse_last_run.return_value = {
                "status": "success",
                "timestamp": "2025-12-27 19:00:00",
                "error_message": None,
            }

            result: Dict[str, Any] = check_all(repo_root=repo_root)

        assert result["overall_status"] == "OK"
        assert len(result["automations"]) == 1
        assert result["automations"][0]["running"] is True
        assert result["automations"][0]["name"] == "inneros_daemon"

    def test_check_all_daemon_stopped_pid_file_missing(self, tmp_path: Path) -> None:
        """When PID file is missing, report daemon as not running.

        RED Phase: This test verifies that check_all() correctly handles
        the case where no PID file exists (daemon never started or cleanly stopped).
        """
        repo_root = _write_daemon_registry_with_pid(tmp_path)
        # Note: We do NOT create a PID file

        from src.automation.system_health import check_all

        with patch.object(Path, "home", return_value=tmp_path), patch(
            "src.automation.system_health.LogParser"
        ) as MockParser:
            parser = MockParser.return_value
            parser.parse_last_run.return_value = {
                "status": "success",
                "timestamp": "2025-12-27 18:00:00",
                "error_message": None,
            }

            result: Dict[str, Any] = check_all(repo_root=repo_root)

        # With missing PID file, daemon should be not running but last run was success
        # Overall status should be WARNING (not running but no error)
        assert result["overall_status"] == "WARNING"
        assert len(result["automations"]) == 1
        assert result["automations"][0]["running"] is False

    def test_check_all_stale_pid_process_not_running(self, tmp_path: Path) -> None:
        """When PID file exists but process is not running, report as stale.

        RED Phase: This test verifies that check_all() correctly detects
        a stale PID file (daemon crashed without cleanup).
        """
        repo_root = _write_daemon_registry_with_pid(tmp_path)

        # Create PID file with non-existent process ID
        pid_dir = tmp_path / ".inneros"
        pid_dir.mkdir(parents=True, exist_ok=True)
        pid_file = pid_dir / "daemon.pid"
        # Use a very high PID that is unlikely to exist
        pid_file.write_text("999999999")

        from src.automation.system_health import check_all

        with patch.object(Path, "home", return_value=tmp_path), patch(
            "src.automation.system_health.LogParser"
        ) as MockParser:
            parser = MockParser.return_value
            parser.parse_last_run.return_value = {
                "status": "success",
                "timestamp": "2025-12-27 17:00:00",
                "error_message": None,
            }

            result: Dict[str, Any] = check_all(repo_root=repo_root)

        # Stale PID means daemon is not running
        assert result["automations"][0]["running"] is False
        # Overall status should reflect the non-running state
        assert result["overall_status"] in ("WARNING", "ERROR")


class TestCheckAllMissingConfig:
    """Tests for handling missing or invalid configuration."""

    def test_check_all_missing_registry_returns_empty(self, tmp_path: Path) -> None:
        """When daemon_registry.yaml is missing, return empty automations.

        RED Phase: This test verifies that check_all() handles missing
        configuration gracefully without raising exceptions.
        """
        # Create repo root without any config
        repo_root = tmp_path / "empty_repo"
        repo_root.mkdir(parents=True, exist_ok=True)

        from src.automation.system_health import check_all

        result: Dict[str, Any] = check_all(repo_root=repo_root)

        assert result["overall_status"] == "OK"
        assert result["automations"] == []

    def test_check_all_empty_registry_returns_ok(self, tmp_path: Path) -> None:
        """When daemon_registry.yaml has no daemons, return OK with empty list."""
        repo_root = _write_empty_daemon_registry(tmp_path)

        from src.automation.system_health import check_all

        result: Dict[str, Any] = check_all(repo_root=repo_root)

        assert result["overall_status"] == "OK"
        assert result["automations"] == []


class TestCheckAllPerformance:
    """Tests for performance requirements."""

    def test_check_all_completes_within_two_seconds(self, tmp_path: Path) -> None:
        """check_all() must complete in <2 seconds.

        RED Phase: This test verifies the performance requirement from
        Issue #50 acceptance criteria.
        """
        repo_root = _write_daemon_registry_with_pid(tmp_path)

        # Create logs directory for LogAggregator
        logs_dir = repo_root / ".automation" / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)

        from src.automation.system_health import check_all

        with patch.object(Path, "home", return_value=tmp_path), patch(
            "src.automation.system_health.LogParser"
        ) as MockParser:
            parser = MockParser.return_value
            parser.parse_last_run.return_value = {
                "status": "success",
                "timestamp": "2025-12-27 19:00:00",
                "error_message": None,
            }

            start_time = time.time()
            result: Dict[str, Any] = check_all(repo_root=repo_root)
            elapsed = time.time() - start_time

        assert elapsed < 2.0, f"check_all() took {elapsed:.2f}s, expected <2s"
        assert "overall_status" in result


class TestCheckAllResultStructure:
    """Tests for the required result structure."""

    def test_check_all_returns_required_keys(self, tmp_path: Path) -> None:
        """check_all() must return overall_healthy (bool), checks (dict), errors (list).

        RED Phase: This test verifies the structured result format from
        Issue #50 requirements.
        """
        repo_root = _write_daemon_registry_with_pid(tmp_path)

        from src.automation.system_health import check_all

        with patch.object(Path, "home", return_value=tmp_path), patch(
            "src.automation.system_health.DaemonDetector"
        ) as MockDetector, patch(
            "src.automation.system_health.LogParser"
        ) as MockParser:
            detector = MockDetector.return_value
            detector.check_daemon_by_pid_file.return_value = {
                "running": True,
                "pid": 1234,
            }

            parser = MockParser.return_value
            parser.parse_last_run.return_value = {
                "status": "success",
                "timestamp": "2025-12-27 19:00:00",
                "error_message": None,
            }

            result: Dict[str, Any] = check_all(repo_root=repo_root)

        # Verify required structure from Issue #50 spec
        # Note: Current implementation uses "overall_status" instead of "overall_healthy"
        # This test will fail, indicating we need to add the new format
        assert "overall_healthy" in result, "Missing 'overall_healthy' key"
        assert isinstance(result["overall_healthy"], bool)
        assert "checks" in result, "Missing 'checks' key"
        assert isinstance(result["checks"], dict)
        assert "errors" in result, "Missing 'errors' key"
        assert isinstance(result["errors"], list)
