"""RED phase: Decision log YAML generation from inventory records."""

import pytest
from pathlib import Path


def test_decision_log_generates_from_inventory(tmp_path):
    """Transform inventory records into executable move decisions with metadata."""
    inventory_yaml = tmp_path / "inventory.yaml"
    decision_log = tmp_path / "decisions.yaml"

    # Sample inventory with 4 records: project doc, dev doc, automation script, review queue
    inventory_content = """items:
  - source: Projects/ACTIVE/draft-todo.md
    destination: Projects/COMPLETED-2025-10/draft-todo.md
    rationale: Archive project documentation into monthly completion folder.
  - source: development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md
    destination: Projects/REFERENCE/youtube-integration-maintenance.md
    rationale: Promote development documentation into reference library.
  - source: .automation/scripts/audit_design_flaws.sh
    destination: development/src/automation/tools/audit_design_flaws.sh
    rationale: Promote vetted automation script into callable tooling bundle for CLI reuse.
    monitoring: cron-log
    trigger: schedule
  - source: .automation/review_queue/fleeting_triage_2025-09-28_08-03-58.md
    destination: Projects/REFERENCE/review-queue/automation-reports/fleeting_triage_2025-09-28_08-03-58.md
    rationale: Archive automation report into reference library for retrospectives.
"""
    inventory_yaml.write_text(inventory_content)

    from src.automation import cleanup_decision_log

    cleanup_decision_log.generate_decision_log(
        inventory_path=inventory_yaml,
        decision_log_path=decision_log,
    )

    data = decision_log.read_text()

    # Verify decision log structure
    assert "items:" in data
    assert "status: pending" in data

    # Verify all 4 records transformed
    assert "Projects/ACTIVE/draft-todo.md" in data
    assert "development/docs/YOUTUBE-INTEGRATION-MAINTENANCE.md" in data
    assert ".automation/scripts/audit_design_flaws.sh" in data
    assert ".automation/review_queue/fleeting_triage_2025-09-28_08-03-58.md" in data

    # Verify destinations preserved
    assert "Projects/COMPLETED-2025-10/draft-todo.md" in data
    assert "Projects/REFERENCE/youtube-integration-maintenance.md" in data
    assert "development/src/automation/tools/audit_design_flaws.sh" in data
    assert "Projects/REFERENCE/review-queue/automation-reports/fleeting_triage_2025-09-28_08-03-58.md" in data

    # Verify metadata preserved for automation assets
    assert "trigger: schedule" in data
    assert "monitoring: cron-log" in data

    # Verify rationale preserved
    assert "Archive project documentation into monthly completion folder." in data
    assert "Promote development documentation into reference library." in data
