"""End-to-end cleanup workflow demo orchestrating inventory → decision log → review → execution.

Demonstrates complete workflow with real automation assets, validating metadata
flow-through and enabling production deployment with audit trail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime

from src.automation.cleanup_inventory import generate_inventory
from src.automation.cleanup_decision_log import generate_decision_log
from src.automation.cleanup_executor import execute_approved_moves


def run_cleanup_workflow_demo(*, vault_root: Path | str) -> dict[str, Any]:
    """Execute complete cleanup workflow demo with 3 real automation assets.

    Parameters
    ----------
    vault_root:
        Root path of the vault to organize.

    Returns
    -------
    dict:
        Demo result with workflow_status, moves_executed, execution_report, audit_trail, backup_path.
    """

    vault_root = _coerce_path(vault_root)

    # Step 1: Setup automation directories
    automation_dir = WorkflowSetup.prepare_automation_dir(vault_root)

    # Step 2: Generate inventory from vault
    inventory_path = WorkflowOrchestrator.generate_inventory(vault_root, automation_dir)

    # Step 3: Generate decision log from inventory
    decision_log_path = WorkflowOrchestrator.generate_decision_log(
        inventory_path, automation_dir
    )

    # Step 4: Mock CLI review approval (all approved)
    approved_decisions_path = WorkflowOrchestrator.mock_cli_review(decision_log_path)

    # Step 5: Execute approved moves
    execution_report = execute_approved_moves(
        approved_decisions_path=approved_decisions_path,
        vault_root=vault_root,
    )

    # Step 6: Build audit trail
    audit_trail = AuditTrailBuilder.build(execution_report)

    # Step 7: Build demo result
    demo_result = DemoResultBuilder.build(execution_report, audit_trail)

    return demo_result


class WorkflowSetup:
    """Setup automation directories for workflow execution."""

    @staticmethod
    def prepare_automation_dir(vault_root: Path) -> Path:
        """Create and return automation review queue directory."""
        automation_dir = vault_root / ".automation" / "review_queue"
        automation_dir.mkdir(parents=True, exist_ok=True)
        return automation_dir


class WorkflowOrchestrator:
    """Orchestrate complete cleanup workflow stages."""

    @staticmethod
    def generate_inventory(vault_root: Path, automation_dir: Path) -> Path:
        """Generate inventory YAML from vault sources."""
        inventory_path = automation_dir / f"cleanup-inventory-{_timestamp()}.yaml"
        sources = _collect_sources(vault_root)
        generate_inventory(
            vault_root=vault_root,
            inventory_path=inventory_path,
            sources=sources,
        )
        return inventory_path

    @staticmethod
    def generate_decision_log(inventory_path: Path, automation_dir: Path) -> Path:
        """Generate decision log YAML from inventory."""
        decision_log_path = automation_dir / f"cleanup-decisions-{_timestamp()}.yaml"
        generate_decision_log(
            inventory_path=inventory_path,
            decision_log_path=decision_log_path,
        )
        return decision_log_path

    @staticmethod
    def mock_cli_review(decision_log_path: Path) -> Path:
        """Mock CLI review by approving all pending decisions."""
        import yaml

        # Read decision log
        decision_log_data = yaml.safe_load(decision_log_path.read_text())
        items = decision_log_data.get("items", [])

        # Approve all items
        for item in items:
            item["status"] = "approved"

        # Persist as approved decisions
        approved_decisions_path = decision_log_path.parent / (
            f"cleanup-decisions-{_timestamp()}.yaml"
        )
        approved_decisions_path.write_text(
            yaml.dump({"items": items}, default_flow_style=False)
        )

        return approved_decisions_path


class AuditTrailBuilder:
    """Build audit trail from execution report."""

    @staticmethod
    def build(execution_report: dict[str, Any]) -> dict[str, Any]:
        """Build audit trail with move statuses and metadata."""
        items = execution_report.get("items", [])
        completed_moves = sum(1 for item in items if item.get("status") == "completed")
        failed_moves = sum(1 for item in items if item.get("status") == "failed")

        return {
            "total_moves": len(items),
            "completed_moves": completed_moves,
            "failed_moves": failed_moves,
            "execution_time_seconds": execution_report.get("execution_time_seconds", 0),
            "backup_path": execution_report.get("backup_path"),
            "moves": [
                {
                    "source": item.get("source"),
                    "destination": item.get("destination"),
                    "status": item.get("status"),
                    "trigger": item.get("trigger"),
                    "monitoring": item.get("monitoring"),
                }
                for item in items
            ],
        }


class DemoResultBuilder:
    """Build final demo result with workflow status and metadata."""

    @staticmethod
    def build(
        execution_report: dict[str, Any],
        audit_trail: dict[str, Any],
    ) -> dict[str, Any]:
        """Build demo result with execution report and audit trail."""
        return {
            "workflow_status": execution_report.get("status", "unknown"),
            "moves_executed": execution_report.get("moves_executed", 0),
            "files_processed": execution_report.get("files_processed", 0),
            "execution_report": execution_report,
            "audit_trail": audit_trail,
            "backup_path": execution_report.get("backup_path"),
        }


def _collect_sources(vault_root: Path) -> list[str]:
    """Collect all markdown files from vault directories."""

    sources = []

    # Scan key directories
    for directory in [
        vault_root / "Projects" / "ACTIVE",
        vault_root / "development" / "docs",
        vault_root / ".automation" / "scripts",
        vault_root / ".automation" / "review_queue",
    ]:
        if directory.exists():
            for md_file in directory.rglob("*.md"):
                try:
                    relative_path = md_file.relative_to(vault_root)
                    sources.append(str(relative_path))
                except ValueError:
                    pass

    return sources


def _timestamp() -> str:
    """Generate timestamp for file naming."""
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def _coerce_path(path: Path | str) -> Path:
    return path if isinstance(path, Path) else Path(path)
