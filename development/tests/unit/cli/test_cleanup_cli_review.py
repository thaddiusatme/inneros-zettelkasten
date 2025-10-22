"""RED phase: CLI decision review with user confirmation and persistence."""

import pytest
from pathlib import Path
from io import StringIO
import sys


def test_cli_review_decisions_displays_pending_moves(tmp_path, monkeypatch):
    """Display pending moves with metadata, collect user confirmation, persist approved decisions."""

    # Setup: Create decision log YAML with 4 pending entries
    decision_log = tmp_path / "decisions.yaml"
    decision_content = """items:
  - source: Projects/ACTIVE/draft-todo.md
    destination: Projects/COMPLETED-2025-10/draft-todo.md
    rationale: Archive project documentation into monthly completion folder.
    status: pending
  - source: development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md
    destination: Projects/REFERENCE/youtube-integration-maintenance.md
    rationale: Promote development documentation into reference library.
    status: pending
  - source: .automation/scripts/audit_design_flaws.sh
    destination: development/src/automation/tools/audit_design_flaws.sh
    rationale: Promote vetted automation script into callable tooling bundle for CLI reuse.
    trigger: schedule
    monitoring: cron-log
    status: pending
  - source: .automation/review_queue/fleeting_triage_2025-09-28_08-03-58.md
    destination: Projects/REFERENCE/review-queue/automation-reports/fleeting_triage_2025-09-28_08-03-58.md
    rationale: Archive automation report into reference library for retrospectives.
    status: pending
"""
    decision_log.write_text(decision_content)

    # Mock user input: approve 3 moves, skip 1
    user_responses = ["approve", "approve", "skip", "approve"]
    response_iter = iter(user_responses)

    def mock_input(prompt):
        return next(response_iter)

    monkeypatch.setattr("builtins.input", mock_input)

    # Capture CLI output
    from src.cli import cleanup_cli_review

    output = StringIO()
    monkeypatch.setattr("sys.stdout", output)

    # Execute CLI review
    cleanup_cli_review.review_decisions(decision_log_path=decision_log)

    # Verify output displays all 4 moves
    output_text = output.getvalue()
    assert "Projects/ACTIVE/draft-todo.md" in output_text
    assert "development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md" in output_text
    assert ".automation/scripts/audit_design_flaws.sh" in output_text
    assert ".automation/review_queue/fleeting_triage_2025-09-28_08-03-58.md" in output_text

    # Verify metadata displayed for automation assets
    assert "Trigger: schedule" in output_text
    assert "Monitoring: cron-log" in output_text

    # Verify rationale displayed
    assert "Archive project documentation" in output_text
    assert "Promote development documentation" in output_text

    # Verify decision log updated with user choices
    import yaml

    updated_data = yaml.safe_load(decision_log.read_text())
    items = updated_data["items"]

    assert items[0]["status"] == "approved"  # First move approved
    assert items[1]["status"] == "approved"  # Second move approved
    assert items[2]["status"] == "skipped"   # Third move skipped
    assert items[3]["status"] == "approved"  # Fourth move approved

    # Verify approved decisions persisted to timestamped file
    review_queue = tmp_path / ".automation" / "review_queue"
    assert review_queue.exists()

    decision_files = list(review_queue.glob("cleanup-decisions-*.yaml"))
    assert len(decision_files) == 1

    approved_data = yaml.safe_load(decision_files[0].read_text())
    approved_items = approved_data["items"]

    # Only 3 approved items in persistence file
    assert len(approved_items) == 3
    assert all(item["status"] == "approved" for item in approved_items)
