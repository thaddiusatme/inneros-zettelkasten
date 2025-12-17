"""RED Phase: Test that Makefile has a smoke target for usability validation.

The smoke target should:
1. Exist in the Makefile
2. Be listed in .PHONY
3. Run core daily commands in sequence
4. Complete in under 60 seconds (design goal)

TDD Iteration 2: P1-USABILITY make smoke
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent.parent
MAKEFILE_PATH = REPO_ROOT / "Makefile"


class TestMakefileSmokeTarget:
    """Verify Makefile has smoke target for usability validation."""

    def test_smoke_target_exists(self):
        """Makefile should have a smoke: target."""
        content = MAKEFILE_PATH.read_text()
        assert re.search(
            r"^smoke:", content, re.MULTILINE
        ), "Makefile must have a 'smoke:' target for usability validation"

    def test_smoke_in_phony(self):
        """smoke should be listed in .PHONY."""
        content = MAKEFILE_PATH.read_text()
        phony_line = re.search(r"^\.PHONY:(.+)$", content, re.MULTILINE)
        assert phony_line, ".PHONY declaration not found"
        assert "smoke" in phony_line.group(1), "smoke must be listed in .PHONY targets"

    def test_smoke_runs_status(self):
        """smoke target should run make status."""
        content = MAKEFILE_PATH.read_text()
        smoke_match = re.search(
            r"^smoke:.*?(?=^[a-z]|\Z)", content, re.MULTILINE | re.DOTALL
        )
        assert smoke_match, "smoke target not found"
        smoke_block = smoke_match.group(0)
        assert "status" in smoke_block.lower(), "smoke target must run status command"

    def test_smoke_runs_review(self):
        """smoke target should run make review (or similar)."""
        content = MAKEFILE_PATH.read_text()
        smoke_match = re.search(
            r"^smoke:.*?(?=^[a-z]|\Z)", content, re.MULTILINE | re.DOTALL
        )
        assert smoke_match, "smoke target not found"
        smoke_block = smoke_match.group(0)
        assert "review" in smoke_block.lower(), "smoke target must run review command"

    def test_smoke_runs_fleeting(self):
        """smoke target should run make fleeting."""
        content = MAKEFILE_PATH.read_text()
        smoke_match = re.search(
            r"^smoke:.*?(?=^[a-z]|\Z)", content, re.MULTILINE | re.DOTALL
        )
        assert smoke_match, "smoke target not found"
        smoke_block = smoke_match.group(0)
        assert (
            "fleeting" in smoke_block.lower()
        ), "smoke target must run fleeting command"
