"""
System Observability Phase 2: Dashboard Launcher - TDD RED Phase

Comprehensive test suite for dashboard launching functionality.
Tests for web UI dashboard, live terminal mode, process detection, and error handling.

TDD Iteration 1 - RED Phase: All tests should FAIL initially
Following proven patterns from Phase 1 status CLI success.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.cli.dashboard_cli import (
    DashboardLauncher,
    TerminalDashboardLauncher,
    DashboardOrchestrator,
)


class TestDashboardLauncher:
    """Test suite for web UI dashboard launcher."""

    def test_launch_workflow_dashboard_starts_subprocess(self):
        """RED: Should start workflow_dashboard.py as subprocess."""
        launcher = DashboardLauncher(vault_path=".")

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None  # Running
            mock_popen.return_value = mock_process

            result = launcher.launch()

            assert result["success"] is True
            assert "process" in result
            mock_popen.assert_called_once()

    def test_launch_detects_already_running_dashboard(self):
        """RED: Should detect if dashboard is already running."""
        launcher = DashboardLauncher(vault_path=".")

        with patch("subprocess.Popen") as mock_popen:
            # First launch succeeds
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            launcher.launch()

            # Second launch should detect running process
            result = launcher.launch()

            assert result["success"] is False
            assert "already running" in result.get("message", "").lower()

    def test_launch_provides_dashboard_url(self):
        """RED: Should provide dashboard URL in result."""
        launcher = DashboardLauncher(vault_path=".")

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            result = launcher.launch()

            assert "url" in result or "message" in result
            # URL should be in result or message

    def test_launch_handles_missing_dashboard_file(self):
        """RED: Should handle gracefully if workflow_dashboard.py is missing."""
        launcher = DashboardLauncher(vault_path=".")

        with patch(
            "subprocess.Popen", side_effect=FileNotFoundError("Dashboard not found")
        ):
            result = launcher.launch()

            assert result["success"] is False
            assert "error" in result or "message" in result


class TestTerminalDashboardLauncher:
    """Test suite for live terminal dashboard launcher."""

    def test_launch_live_dashboard_starts_subprocess(self):
        """RED: Should start terminal_dashboard.py as subprocess."""
        launcher = TerminalDashboardLauncher(daemon_url="http://localhost:8080")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            result = launcher.launch()

            assert result["success"] is True
            mock_run.assert_called_once()

    def test_launch_live_passes_daemon_url(self):
        """RED: Should pass daemon URL to terminal dashboard."""
        launcher = TerminalDashboardLauncher(daemon_url="http://localhost:9999")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            launcher.launch()

            # Check that URL is passed to subprocess
            call_args = mock_run.call_args
            assert any(
                "9999" in str(arg)
                for arg in call_args[0] + tuple(call_args[1].values())
            )

    def test_launch_live_handles_keyboard_interrupt(self):
        """RED: Should handle Ctrl+C gracefully."""
        launcher = TerminalDashboardLauncher(daemon_url="http://localhost:8080")

        with patch("subprocess.run", side_effect=KeyboardInterrupt()):
            result = launcher.launch()

            assert result["success"] is True  # Graceful exit
            assert (
                "stopped" in result.get("message", "").lower()
                or "interrupted" in result.get("message", "").lower()
            )


class TestDashboardOrchestrator:
    """Test suite for dashboard command orchestration."""

    def test_default_launches_web_dashboard(self):
        """RED: Default command should launch web UI dashboard."""
        orchestrator = DashboardOrchestrator(vault_path=".")

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            result = orchestrator.run(live_mode=False)

            assert result["success"] is True
            assert (
                result.get("mode") == "web"
                or "workflow" in result.get("message", "").lower()
            )

    def test_live_flag_launches_terminal_dashboard(self):
        """RED: --live flag should launch terminal dashboard."""
        orchestrator = DashboardOrchestrator(vault_path=".")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(returncode=0)

            result = orchestrator.run(live_mode=True)

            assert result["success"] is True
            assert (
                result.get("mode") == "live"
                or "terminal" in result.get("message", "").lower()
            )

    def test_displays_clear_user_feedback(self):
        """RED: Should display clear instructions to user."""
        orchestrator = DashboardOrchestrator(vault_path=".")

        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = None
            mock_popen.return_value = mock_process

            result = orchestrator.run(live_mode=False)

            # Should have user-friendly message
            assert "message" in result or "url" in result

    def test_integration_with_status_utils(self):
        """RED: Should integrate with existing status utilities for daemon detection."""
        orchestrator = DashboardOrchestrator(vault_path=".")

        # Should be able to detect daemon status for live mode
        daemon_status = orchestrator.check_daemon_status()

        assert isinstance(daemon_status, dict)
        assert "running" in daemon_status or "available" in daemon_status


class TestErrorHandling:
    """Test suite for error handling scenarios."""

    def test_handles_permission_denied(self):
        """RED: Should handle permission errors gracefully."""
        launcher = DashboardLauncher(vault_path=".")

        with patch("subprocess.Popen", side_effect=PermissionError("Access denied")):
            result = launcher.launch()

            assert result["success"] is False
            assert "permission" in result.get("message", "").lower()

    def test_handles_port_conflicts(self):
        """RED: Should detect and report port conflicts."""
        launcher = DashboardLauncher(vault_path=".")

        # Simulate port already in use
        with patch("subprocess.Popen") as mock_popen:
            mock_process = Mock()
            mock_process.poll.return_value = 1  # Exited immediately
            mock_popen.return_value = mock_process

            result = launcher.launch()

            # Should detect that process exited (possibly port conflict)
            assert "error" in result or result.get("success") is False


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
