"""RED phase: DirectoryOrganizer Execution Integration with metadata flow-through."""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import yaml


def test_execute_approved_moves_with_metadata_flow(tmp_path, monkeypatch):
    """Execute approved moves via DirectoryOrganizer with metadata preserved in execution report."""

    # Setup: Create approved decisions YAML with 3 approved entries
    approved_decisions = tmp_path / "cleanup-decisions-20251022-120000.yaml"
    approved_content = """items:
  - source: Projects/ACTIVE/draft-todo.md
    destination: Projects/COMPLETED-2025-10/draft-todo.md
    rationale: Archive project documentation into monthly completion folder.
    status: approved
  - source: development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md
    destination: Projects/REFERENCE/youtube-integration-maintenance.md
    rationale: Promote development documentation into reference library.
    status: approved
  - source: .automation/scripts/audit_design_flaws.sh
    destination: development/src/automation/tools/audit_design_flaws.sh
    rationale: Promote vetted automation script into callable tooling bundle for CLI reuse.
    trigger: schedule
    monitoring: cron-log
    status: approved
"""
    approved_decisions.write_text(approved_content)

    # Setup: Mock DirectoryOrganizer
    mock_organizer = Mock()
    mock_organizer.execute_moves.return_value = {
        "moves_executed": 3,
        "files_processed": 3,
        "backup_created": True,
        "backup_path": str(tmp_path / "backup-20251022-120000"),
        "execution_time_seconds": 2.5,
        "status": "success",
        "validation_results": {
            "total_moves_planned": 3,
            "conflicts_detected": 0,
            "unknown_types": 0,
            "malformed_files": 0,
        },
    }

    # Mock DirectoryOrganizer constructor
    def mock_organizer_init(*args, **kwargs):
        return mock_organizer

    monkeypatch.setattr(
        "src.automation.cleanup_executor.DirectoryOrganizer",
        mock_organizer_init,
    )

    # Execute cleanup executor
    from src.automation import cleanup_executor

    execution_report = cleanup_executor.execute_approved_moves(
        approved_decisions_path=approved_decisions,
        vault_root=tmp_path,
    )

    # Verify DirectoryOrganizer.execute_moves() was called
    assert mock_organizer.execute_moves.called

    # Verify execution report contains move count
    assert execution_report["moves_executed"] == 3
    assert execution_report["files_processed"] == 3
    assert execution_report["status"] == "success"

    # Verify metadata preserved in execution report
    assert "items" in execution_report
    assert len(execution_report["items"]) == 3

    # Verify each item retains metadata
    items = execution_report["items"]
    assert items[0]["source"] == "Projects/ACTIVE/draft-todo.md"
    assert items[0]["destination"] == "Projects/COMPLETED-2025-10/draft-todo.md"
    assert items[0]["status"] == "completed"

    assert items[1]["source"] == "development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md"
    assert items[1]["destination"] == "Projects/REFERENCE/youtube-integration-maintenance.md"
    assert items[1]["status"] == "completed"

    # Verify automation asset metadata preserved
    assert items[2]["trigger"] == "schedule"
    assert items[2]["monitoring"] == "cron-log"
    assert items[2]["status"] == "completed"

    # Verify execution report persisted to timestamped YAML
    review_queue = tmp_path / ".automation" / "review_queue"
    assert review_queue.exists()

    execution_reports = list(review_queue.glob("cleanup-execution-*.yaml"))
    assert len(execution_reports) == 1

    # Verify persisted report contains all metadata
    persisted_data = yaml.safe_load(execution_reports[0].read_text())
    assert persisted_data["moves_executed"] == 3
    assert persisted_data["status"] == "success"
    assert "items" in persisted_data
    assert len(persisted_data["items"]) == 3

    # Verify metadata in persisted report
    persisted_items = persisted_data["items"]
    assert persisted_items[2]["trigger"] == "schedule"
    assert persisted_items[2]["monitoring"] == "cron-log"
