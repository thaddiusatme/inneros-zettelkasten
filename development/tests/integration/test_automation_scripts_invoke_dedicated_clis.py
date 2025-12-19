"""Integration tests: Automation scripts invoke dedicated CLIs (Issue #39).

These tests verify that automation shell scripts in .automation/scripts/ correctly
call dedicated CLIs instead of the deprecated workflow_demo.py, per ADR-004.

Testing strategy: Parse script content and assert expected CLI invocation patterns.
This approach is stable (no external dependencies) and catches regressions early.
"""

from pathlib import Path
import re

import pytest

# Repository paths
REPO_ROOT = Path(__file__).resolve().parents[3]
AUTOMATION_SCRIPTS_DIR = REPO_ROOT / ".automation" / "scripts"

# Scripts to validate (must NOT call workflow_demo.py)
SCRIPTS_TO_VALIDATE = [
    "health_monitor.sh",
    "weekly_deep_analysis.sh",
    "process_inbox_workflow.sh",
    "automated_screenshot_import.sh",
    "supervised_inbox_processing.sh",
]

# Expected CLI references per script (script_name -> list of expected CLI patterns)
EXPECTED_CLI_PATTERNS = {
    "health_monitor.sh": [
        r"core_workflow_cli\.py",
    ],
    "weekly_deep_analysis.sh": [
        r"core_workflow_cli\.py",
        r"backup_cli\.py",
        r"fleeting_cli\.py",
        r"weekly_review_cli\.py",
        r"connections_demo\.py",
    ],
    "process_inbox_workflow.sh": [
        r"core_workflow_cli\.py",
        r"backup_cli\.py",
        r"screenshot_cli\.py",
        r"fleeting_cli\.py",
        r"connections_demo\.py",
    ],
    "automated_screenshot_import.sh": [
        r"core_workflow_cli\.py",
        r"backup_cli\.py",
        r"screenshot_cli\.py",
    ],
    "supervised_inbox_processing.sh": [
        r"core_workflow_cli\.py",
        r"backup_cli\.py",
        r"connections_demo\.py",
    ],
}


class TestAutomationScriptsInvokeDedicatedCLIs:
    """Verify automation scripts follow ADR-004 CLI Layer Extraction."""

    @pytest.fixture
    def script_contents(self) -> dict[str, str]:
        """Load all automation script contents."""
        contents = {}
        for script_name in SCRIPTS_TO_VALIDATE:
            script_path = AUTOMATION_SCRIPTS_DIR / script_name
            if script_path.exists():
                contents[script_name] = script_path.read_text()
            else:
                contents[script_name] = ""
        return contents

    # -------------------------------------------------------------------------
    # P0: No script calls workflow_demo.py
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize("script_name", SCRIPTS_TO_VALIDATE)
    def test_script_does_not_call_workflow_demo(
        self, script_contents: dict[str, str], script_name: str
    ) -> None:
        """Script must NOT reference deprecated workflow_demo.py."""
        content = script_contents[script_name]
        assert content, f"Script not found: {script_name}"

        # Filter out comment-only matches by checking each line
        actual_invocations = []
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue  # Skip comment lines
            if "workflow_demo.py" in line:
                actual_invocations.append(line.strip())

        assert (
            not actual_invocations
        ), f"{script_name} still calls workflow_demo.py:\n" + "\n".join(
            actual_invocations
        )

    # -------------------------------------------------------------------------
    # P0: Scripts reference expected dedicated CLIs
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize("script_name", SCRIPTS_TO_VALIDATE)
    def test_script_references_expected_clis(
        self, script_contents: dict[str, str], script_name: str
    ) -> None:
        """Script must reference expected dedicated CLIs per ADR-004 mapping."""
        content = script_contents[script_name]
        assert content, f"Script not found: {script_name}"

        expected_patterns = EXPECTED_CLI_PATTERNS.get(script_name, [])
        missing_patterns = []

        for pattern in expected_patterns:
            if not re.search(pattern, content):
                missing_patterns.append(pattern)

        assert (
            not missing_patterns
        ), f"{script_name} missing expected CLI references:\n" + "\n".join(
            f"  - {p}" for p in missing_patterns
        )

    # -------------------------------------------------------------------------
    # P0: Scripts have ADR-004 comment marker
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize("script_name", SCRIPTS_TO_VALIDATE)
    def test_script_has_adr004_comment(
        self, script_contents: dict[str, str], script_name: str
    ) -> None:
        """Script should have comment indicating ADR-004 CLI Layer Extraction."""
        content = script_contents[script_name]
        assert content, f"Script not found: {script_name}"

        # Look for the standard comment marker
        adr_pattern = r"ADR-004.*CLI.*Layer.*Extraction|Issue\s*#39"
        assert re.search(
            adr_pattern, content, re.IGNORECASE
        ), f"{script_name} missing ADR-004/Issue #39 comment marker"

    # -------------------------------------------------------------------------
    # P1: Validate CLI variable definitions follow standard pattern
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize("script_name", SCRIPTS_TO_VALIDATE)
    def test_script_cli_definitions_use_python_variable(
        self, script_contents: dict[str, str], script_name: str
    ) -> None:
        """CLI variable definitions should use $PYTHON for consistency."""
        content = script_contents[script_name]
        assert content, f"Script not found: {script_name}"

        # Look for CLI variable definitions like: CORE_CLI="$PYTHON ..."
        cli_def_pattern = r'^\s*\w+_CLI="\$PYTHON'
        cli_definitions = re.findall(cli_def_pattern, content, re.MULTILINE)

        # Should have at least one CLI definition using $PYTHON
        assert (
            cli_definitions
        ), f"{script_name} should define CLI variables using $PYTHON pattern"


class TestAutomationScriptsExist:
    """Verify expected automation scripts exist."""

    @pytest.mark.parametrize("script_name", SCRIPTS_TO_VALIDATE)
    def test_script_exists(self, script_name: str) -> None:
        """Expected automation script must exist."""
        script_path = AUTOMATION_SCRIPTS_DIR / script_name
        assert script_path.exists(), f"Script not found: {script_path}"

    @pytest.mark.parametrize("script_name", SCRIPTS_TO_VALIDATE)
    def test_script_is_executable(self, script_name: str) -> None:
        """Automation scripts should be executable."""
        script_path = AUTOMATION_SCRIPTS_DIR / script_name
        if script_path.exists():
            # Check if file has execute permission
            import os

            assert os.access(
                script_path, os.X_OK
            ), f"{script_name} should be executable (chmod +x)"
