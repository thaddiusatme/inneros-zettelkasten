"""TDD tests for system wide automation health check.

Covers the shared check_all function that summarizes daemon status.
"""

from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch

import pytest


def _write_daemon_registry(tmp_path: Path) -> Path:
    """Create a minimal daemon_registry.yaml under a fake repo root.

    The layout matches the real .automation/config structure so that
    the health check can load it without knowing it is in a test.
    """

    config_dir = tmp_path / ".automation" / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    registry_path = config_dir / "daemon_registry.yaml"
    registry_path.write_text(
        """
 daemons:
   - name: youtube_watcher
     script_path: .automation/scripts/automated_screenshot_import.sh
     log_path: .automation/logs/youtube_watcher.log
   - name: screenshot_processor
     script_path: .automation/scripts/process_screenshots.py
     log_path: .automation/logs/screenshot_processor.log
""".lstrip()
    )
    return tmp_path


class TestSystemHealthCheckAll:
    """Tests for src.automation.system_health.check_all.

    These tests define the stable result shape and overall_status rules
    for the shared automation health function.
    """

    @pytest.mark.parametrize("overall_status", ["OK"])
    def test_check_all_all_healthy_returns_ok(
        self, tmp_path: Path, overall_status: str
    ) -> None:
        """All daemons running with successful last runs yields overall OK."""

        repo_root = _write_daemon_registry(tmp_path)

        # Import inside test so module is loaded after registry exists
        from src.automation.system_health import check_all

        with patch(
            "src.automation.system_health.DaemonDetector"
        ) as MockDetector, patch(
            "src.automation.system_health.LogParser"
        ) as MockParser:
            detector = MockDetector.return_value
            detector.check_daemon_status.return_value = {"running": True, "pid": 12345}

            parser = MockParser.return_value
            parser.parse_last_run.return_value = {
                "status": "success",
                "timestamp": "2025-10-23 19:05:15",
                "error_message": None,
            }

            result: Dict[str, Any] = check_all(repo_root=repo_root)

        assert result["overall_status"] == overall_status
        assert len(result["automations"]) == 2
        for automation in result["automations"]:
            assert automation["running"] is True
            assert automation["last_run_status"] == "success"
            assert automation["error_message"] is None

    def test_check_all_with_failed_daemon_returns_error(self, tmp_path: Path) -> None:
        """Any failed daemon should mark overall_status as ERROR."""

        repo_root = _write_daemon_registry(tmp_path)

        from src.automation.system_health import check_all

        with patch(
            "src.automation.system_health.DaemonDetector"
        ) as MockDetector, patch(
            "src.automation.system_health.LogParser"
        ) as MockParser:
            detector = MockDetector.return_value
            # First daemon not running and failed, second daemon healthy
            detector.check_daemon_status.side_effect = [
                {"running": False, "pid": None},
                {"running": True, "pid": 22222},
            ]

            parser = MockParser.return_value
            parser.parse_last_run.side_effect = [
                {
                    "status": "failed",
                    "timestamp": "2025-10-23 19:10:00",
                    "error_message": "Connection error",
                },
                {
                    "status": "success",
                    "timestamp": "2025-10-23 19:05:15",
                    "error_message": None,
                },
            ]

            result: Dict[str, Any] = check_all(repo_root=repo_root)

        assert result["overall_status"] == "ERROR"
        assert len(result["automations"]) == 2

        # First automation should reflect the failure
        first = result["automations"][0]
        assert first["running"] is False
        assert first["last_run_status"] == "failed"
        assert "Connection error" in (first["error_message"] or "")

        # Second automation should still be healthy
        second = result["automations"][1]
        assert second["running"] is True
        assert second["last_run_status"] == "success"
        assert second["error_message"] is None
