#!/usr/bin/env python3
"""
REFACTOR Phase verification - Test that extracted utilities work correctly.
Verifies facade pattern maintains compatibility while delegating to utilities.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cli.dashboard_cli import (
    DashboardLauncher,
    TerminalDashboardLauncher,
    DashboardOrchestrator,
)
from src.cli.dashboard_utils import (
    WebDashboardLauncher,
    LiveDashboardLauncher,
    OutputFormatter,
)


def test_dashboard_launcher_facade():
    """Test that DashboardLauncher facade delegates to utility."""
    print("Testing DashboardLauncher facade...")

    launcher = DashboardLauncher(vault_path=".")

    # Should delegate to WebDashboardLauncher
    assert hasattr(launcher, "launcher"), "Should have launcher attribute"
    assert isinstance(
        launcher.launcher, WebDashboardLauncher
    ), "Should use WebDashboardLauncher"

    # Mock subprocess to test launch logic
    with patch("subprocess.Popen") as mock_popen:
        mock_process = Mock()
        mock_process.poll.return_value = None  # Running
        mock_popen.return_value = mock_process

        result = launcher.launch()

        assert isinstance(result, dict), "Should return dict"
        assert "success" in result, "Should have success key"

    print("✅ DashboardLauncher facade verified")
    return True


def test_terminal_dashboard_launcher_facade():
    """Test that TerminalDashboardLauncher facade delegates to utility."""
    print("Testing TerminalDashboardLauncher facade...")

    launcher = TerminalDashboardLauncher(daemon_url="http://localhost:8080")

    # Should delegate to LiveDashboardLauncher
    assert hasattr(launcher, "launcher"), "Should have launcher attribute"
    assert isinstance(
        launcher.launcher, LiveDashboardLauncher
    ), "Should use LiveDashboardLauncher"
    assert launcher.daemon_url == "http://localhost:8080", "Should store daemon URL"

    # Mock subprocess to test launch logic
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = Mock(returncode=0)

        result = launcher.launch()

        assert isinstance(result, dict), "Should return dict"
        assert "success" in result, "Should have success key"

    print("✅ TerminalDashboardLauncher facade verified")
    return True


def test_output_formatter_utility():
    """Test that OutputFormatter utility works correctly."""
    print("Testing OutputFormatter utility...")

    # Test success formatting
    success_result = {
        "success": True,
        "message": "Dashboard launched",
        "url": "http://localhost:8000",
        "mode": "web",
    }

    message = OutputFormatter.format_success(success_result)
    assert "✅" in message, "Should have success emoji"
    assert "http://localhost:8000" in message, "Should include URL"
    assert "Ctrl+C" in message, "Should include stop instructions"

    # Test error formatting
    error_result = {"success": False, "message": "Failed to launch", "error": True}

    message = OutputFormatter.format_error(error_result)
    assert "❌" in message, "Should have error emoji"
    assert "Failed to launch" in message, "Should include error message"

    print("✅ OutputFormatter utility verified")
    return True


def test_dashboard_orchestrator():
    """Test that DashboardOrchestrator works with facades."""
    print("Testing DashboardOrchestrator with facades...")

    orchestrator = DashboardOrchestrator(vault_path=".")

    # Should have facade launchers
    assert hasattr(orchestrator, "web_launcher"), "Should have web_launcher"
    assert hasattr(orchestrator, "terminal_launcher"), "Should have terminal_launcher"
    assert isinstance(
        orchestrator.web_launcher, DashboardLauncher
    ), "Should use DashboardLauncher"
    assert isinstance(
        orchestrator.terminal_launcher, TerminalDashboardLauncher
    ), "Should use TerminalDashboardLauncher"

    # Mock the underlying utilities
    with patch.object(orchestrator.web_launcher.launcher, "launch") as mock_web:
        mock_web.return_value = {"success": True}

        result = orchestrator.run(live_mode=False)

        assert isinstance(result, dict), "Should return dict"
        assert result.get("mode") == "web", "Should set mode to web"
        assert mock_web.called, "Should call web launcher"

    with patch.object(
        orchestrator.terminal_launcher.launcher, "launch"
    ) as mock_terminal:
        mock_terminal.return_value = {"success": True}

        result = orchestrator.run(live_mode=True)

        assert isinstance(result, dict), "Should return dict"
        assert result.get("mode") == "live", "Should set mode to live"
        assert mock_terminal.called, "Should call terminal launcher"

    print("✅ DashboardOrchestrator integration verified")
    return True


def test_loc_compliance():
    """Test that main file meets ADR-001 LOC target."""
    print("Testing ADR-001 LOC compliance...")

    main_file = Path(__file__).parent.parent / "src" / "cli" / "dashboard_cli.py"
    utils_file = Path(__file__).parent.parent / "src" / "cli" / "dashboard_utils.py"

    with open(main_file) as f:
        main_loc = len(f.readlines())

    with open(utils_file) as f:
        utils_loc = len(f.readlines())

    print(f"   Main file: {main_loc} LOC")
    print(f"   Utils file: {utils_loc} LOC")
    print(f"   Total: {main_loc + utils_loc} LOC")

    assert main_loc < 200, f"Main file should be <200 LOC, got {main_loc}"

    print("✅ ADR-001 compliance verified")
    return True


def main():
    """Run all REFACTOR phase verifications."""
    print("=" * 60)
    print("REFACTOR PHASE VERIFICATION")
    print("=" * 60)
    print()

    failures = []

    tests = [
        ("DashboardLauncher facade", test_dashboard_launcher_facade),
        ("TerminalDashboardLauncher facade", test_terminal_dashboard_launcher_facade),
        ("OutputFormatter utility", test_output_formatter_utility),
        ("DashboardOrchestrator integration", test_dashboard_orchestrator),
        ("ADR-001 LOC compliance", test_loc_compliance),
    ]

    for test_name, test_func in tests:
        try:
            if not test_func():
                failures.append(f"{test_name} verification failed")
        except Exception as e:
            failures.append(f"{test_name} error: {e}")
            print(f"❌ {test_name} failed: {e}")

    print()
    print("=" * 60)

    if failures:
        print("❌ REFACTOR PHASE VERIFICATION FAILED")
        for failure in failures:
            print(f"  - {failure}")
        return False
    else:
        print("✅ REFACTOR PHASE VERIFICATION COMPLETE")
        print()
        print("Summary:")
        print("  - DashboardLauncher: Facade pattern working ✅")
        print("  - TerminalDashboardLauncher: Facade pattern working ✅")
        print("  - OutputFormatter: Utility extraction successful ✅")
        print("  - DashboardOrchestrator: Integration verified ✅")
        print("  - ADR-001: <200 LOC target met ✅")
        print()
        print("Status: REFACTOR phase complete, ready for commit and lessons learned")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
