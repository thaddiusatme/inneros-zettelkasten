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
