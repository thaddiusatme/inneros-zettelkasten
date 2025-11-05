"""TDD RED Phase: Automation CLI Migration Tests (Issue #39)

These tests ensure automation shell scripts are calling the new dedicated CLI
entrypoints rather than the deprecated workflow_demo.py interface per ADR-004.

RED Phase expectation:
- automated_screenshot_import.sh still references workflow_demo.py, so the
  dedicated CLI path assertion should fail until the script is migrated.
"""

from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent


class TestAutomationCLIMigration:
    """Verify automation scripts are migrated to dedicated CLI entrypoints."""

    def test_screenshot_import_script_uses_dedicated_cli(self):
        """RED: automated_screenshot_import.sh should invoke screenshot_processor CLI."""

        script_path = REPO_ROOT / ".automation" / "scripts" / "automated_screenshot_import.sh"
        script_contents = script_path.read_text(encoding="utf-8")

        assert (
            "development/src/cli/screenshot_cli.py" in script_contents
        ), "automation script missing dedicated screenshot CLI path"

        assert (
            "workflow_demo.py" not in script_contents
        ), "automation script should not reference deprecated workflow_demo.py"

    def test_supervised_inbox_script_uses_core_workflow_cli(self):
        """RED: supervised_inbox_processing.sh should invoke core_workflow_cli.py process-inbox."""

        script_path = REPO_ROOT / ".automation" / "scripts" / "supervised_inbox_processing.sh"
        script_contents = script_path.read_text(encoding="utf-8")

        assert (
            "development/src/cli/core_workflow_cli.py" in script_contents
        ), "automation script missing dedicated core_workflow_cli path"

        assert (
            "workflow_demo.py" not in script_contents
        ), "automation script should not reference deprecated workflow_demo.py"

    def test_weekly_deep_analysis_script_uses_dedicated_clis(self):
        """RED: weekly_deep_analysis.sh should invoke dedicated CLIs (fleeting_cli, weekly_review_cli, etc.)."""

        script_path = REPO_ROOT / ".automation" / "scripts" / "weekly_deep_analysis.sh"
        script_contents = script_path.read_text(encoding="utf-8")

        # Should reference multiple dedicated CLIs
        assert (
            "development/src/cli/fleeting_cli.py" in script_contents
        ), "automation script missing dedicated fleeting_cli path"

        assert (
            "development/src/cli/weekly_review_cli.py" in script_contents
        ), "automation script missing dedicated weekly_review_cli path"

        # Should not reference deprecated CLI
        assert (
            "workflow_demo.py" not in script_contents
        ), "automation script should not reference deprecated workflow_demo.py"

    def test_process_inbox_workflow_script_uses_core_workflow_cli(self):
        """RED: process_inbox_workflow.sh should invoke core_workflow_cli.py process-inbox."""

        script_path = REPO_ROOT / ".automation" / "scripts" / "process_inbox_workflow.sh"
        script_contents = script_path.read_text(encoding="utf-8")

        # Verify dedicated CLI paths are present
        assert (
            "development/src/cli/core_workflow_cli.py" in script_contents
        ), "automation script missing dedicated core_workflow_cli path"

        assert (
            "development/src/cli/safe_workflow_cli.py" in script_contents
        ), "automation script missing dedicated safe_workflow_cli path"

        assert (
            "development/src/cli/fleeting_cli.py" in script_contents
        ), "automation script missing dedicated fleeting_cli path"

        assert (
            "development/src/cli/connections_demo.py" in script_contents
        ), "automation script missing dedicated connections_demo path"

        # Verify migration note is present
        assert (
            "Migration note: Dedicated CLI migration completed" in script_contents
        ), "automation script missing migration completion note"

        # TEMPORARY: Allow workflow_demo.py ONLY for evening-screenshots (pending extraction)
        # This is documented with TODO comments in the script
        if "workflow_demo.py" in script_contents:
            assert (
                "WORKFLOW_DEMO_CLI" in script_contents
            ), "workflow_demo.py usage must be through WORKFLOW_DEMO_CLI variable"
            assert (
                "TEMPORARY: evening-screenshots not yet extracted" in script_contents
            ), "workflow_demo.py usage must be documented as TEMPORARY"
            assert (
                "--evening-screenshots" in script_contents
            ), "workflow_demo.py should only be used for evening-screenshots"

    def test_health_monitor_script_uses_core_workflow_cli(self):
        """RED: health_monitor.sh should invoke core_workflow_cli.py status."""

        script_path = REPO_ROOT / ".automation" / "scripts" / "health_monitor.sh"
        script_contents = script_path.read_text(encoding="utf-8")

        # Should reference dedicated CLI for status command
        assert (
            "development/src/cli/core_workflow_cli.py" in script_contents
        ), "automation script missing dedicated core_workflow_cli path"

        # Should not reference deprecated CLI
        assert (
            "workflow_demo.py" not in script_contents
        ), "automation script should not reference deprecated workflow_demo.py"

        # Should have migration trace message
        assert (
            "Migration note:" in script_contents
            or "MIGRATION:" in script_contents
        ), "automation script missing migration completion note"
