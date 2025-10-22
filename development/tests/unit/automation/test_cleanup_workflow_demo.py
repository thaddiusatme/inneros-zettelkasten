"""RED phase: End-to-end cleanup workflow demo with real automation assets."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import yaml


def test_end_to_end_cleanup_workflow_demo(tmp_path, monkeypatch):
    """Execute complete workflow: inventory → decision log → CLI review → execution.
    
    Demonstrates full cleanup workflow with 3 real automation assets:
    1. Project doc (Projects/ACTIVE/draft-todo.md → Projects/COMPLETED-2025-10/)
    2. Dev doc (development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md → Projects/REFERENCE/)
    3. Automation script (.automation/scripts/audit_design_flaws.md → development/src/automation/tools/)
    
    Validates metadata flow-through (trigger, monitoring) and execution report persistence.
    """

    # Setup: Create temporary vault with 4 test automation assets
    vault_root = tmp_path / "test_vault"
    vault_root.mkdir()

    # Asset 1: Project doc
    projects_active = vault_root / "Projects" / "ACTIVE"
    projects_active.mkdir(parents=True)
    project_doc = projects_active / "draft-todo.md"
    project_doc.write_text(
        """---
type: permanent
created: 2025-10-01
---
# Draft TODO

Project documentation for archival.
"""
    )

    # Asset 2: Dev doc
    dev_docs = vault_root / "development" / "docs"
    dev_docs.mkdir(parents=True)
    dev_doc = dev_docs / "YOUTUBE-INTEGRATION-MAINTENANCE.md"
    dev_doc.write_text(
        """---
type: permanent
created: 2025-10-01
---
# YouTube Integration Maintenance

Development documentation for promotion to reference.
"""
    )

    # Asset 3: Automation script (as markdown for inventory scanning)
    automation_scripts = vault_root / ".automation" / "scripts"
    automation_scripts.mkdir(parents=True)
    automation_script = automation_scripts / "audit_design_flaws.md"
    automation_script.write_text(
        """---
type: permanent
created: 2025-10-01
---
# Audit Design Flaws Script

Automation script for design flaw auditing.
"""
    )


    # Mock the cleanup workflow components
    mock_inventory = {
        "items": [
            {
                "source": "Projects/ACTIVE/draft-todo.md",
                "destination": "Projects/COMPLETED-2025-10/draft-todo.md",
                "rationale": "Archive project documentation into monthly completion folder.",
            },
            {
                "source": "development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md",
                "destination": "Projects/REFERENCE/youtube-integration-maintenance.md",
                "rationale": "Promote development documentation into reference library.",
            },
            {
                "source": ".automation/scripts/audit_design_flaws.md",
                "destination": "development/src/automation/tools/audit_design_flaws.md",
                "rationale": "Promote vetted automation script into callable tooling bundle for CLI reuse.",
                "trigger": "schedule",
                "monitoring": "cron-log",
            },
        ]
    }

    mock_decision_log = {
        "items": [
            {
                "source": "Projects/ACTIVE/draft-todo.md",
                "destination": "Projects/COMPLETED-2025-10/draft-todo.md",
                "rationale": "Archive project documentation into monthly completion folder.",
                "status": "pending",
            },
            {
                "source": "development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md",
                "destination": "Projects/REFERENCE/youtube-integration-maintenance.md",
                "rationale": "Promote development documentation into reference library.",
                "status": "pending",
            },
            {
                "source": ".automation/scripts/audit_design_flaws.md",
                "destination": "development/src/automation/tools/audit_design_flaws.md",
                "rationale": "Promote vetted automation script into callable tooling bundle for CLI reuse.",
                "trigger": "schedule",
                "monitoring": "cron-log",
                "status": "pending",
            },
        ]
    }

    mock_approved_decisions = {
        "items": [
            {
                "source": "Projects/ACTIVE/draft-todo.md",
                "destination": "Projects/COMPLETED-2025-10/draft-todo.md",
                "rationale": "Archive project documentation into monthly completion folder.",
                "status": "approved",
            },
            {
                "source": "development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md",
                "destination": "Projects/REFERENCE/youtube-integration-maintenance.md",
                "rationale": "Promote development documentation into reference library.",
                "status": "approved",
            },
            {
                "source": ".automation/scripts/audit_design_flaws.md",
                "destination": "development/src/automation/tools/audit_design_flaws.md",
                "rationale": "Promote vetted automation script into callable tooling bundle for CLI reuse.",
                "trigger": "schedule",
                "monitoring": "cron-log",
                "status": "approved",
            },
        ]
    }

    mock_execution_result = {
        "moves_executed": 3,
        "files_processed": 3,
        "backup_created": True,
        "backup_path": str(vault_root / "backup-20251022-120000"),
        "execution_time_seconds": 1.5,
        "status": "success",
        "validation_results": {
            "total_moves_planned": 3,
            "conflicts_detected": 0,
            "unknown_types": 0,
            "malformed_files": 0,
        },
    }

    # Mock DirectoryOrganizer.execute_moves()
    mock_organizer = Mock()
    mock_organizer.execute_moves.return_value = mock_execution_result

    def mock_organizer_init(*args, **kwargs):
        return mock_organizer

    monkeypatch.setattr(
        "src.automation.cleanup_executor.DirectoryOrganizer",
        mock_organizer_init,
    )

    # Import and run the demo
    from src.automation import cleanup_workflow_demo

    demo_result = cleanup_workflow_demo.run_cleanup_workflow_demo(vault_root=vault_root)

    # Assertions: Verify complete workflow execution
    assert demo_result["workflow_status"] == "success"
    assert demo_result["moves_executed"] == 3
    assert demo_result["files_processed"] == 3

    # Verify execution report generated with metadata preserved
    assert "execution_report" in demo_result
    execution_report = demo_result["execution_report"]
    assert execution_report["moves_executed"] == 3
    assert execution_report["status"] == "success"

    # Verify all 3 items in execution report
    assert len(execution_report["items"]) == 3

    # Verify metadata flow-through for automation script (item 2)
    automation_item = execution_report["items"][2]
    assert automation_item["source"] == ".automation/scripts/audit_design_flaws.md"
    assert automation_item["destination"] == "development/src/automation/tools/audit_design_flaws.md"
    assert automation_item["trigger"] == "schedule"
    assert automation_item["monitoring"] == "cron-log"
    assert automation_item["status"] == "completed"

    # Verify execution report persisted to timestamped YAML
    review_queue_dir = vault_root / ".automation" / "review_queue"
    execution_reports = list(review_queue_dir.glob("cleanup-execution-*.yaml"))
    assert len(execution_reports) == 1

    # Verify persisted report contains all metadata
    persisted_data = yaml.safe_load(execution_reports[0].read_text())
    assert persisted_data["moves_executed"] == 3
    assert persisted_data["status"] == "success"
    assert len(persisted_data["items"]) == 3

    # Verify audit trail with move statuses
    assert "audit_trail" in demo_result
    audit_trail = demo_result["audit_trail"]
    assert audit_trail["total_moves"] == 3
    assert audit_trail["completed_moves"] == 3
    assert audit_trail["failed_moves"] == 0

    # Verify backup path captured for rollback
    assert "backup_path" in demo_result
    assert demo_result["backup_path"] is not None
