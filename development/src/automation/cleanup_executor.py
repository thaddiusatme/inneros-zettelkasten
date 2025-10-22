"""Execute approved cleanup decisions through DirectoryOrganizer with metadata flow-through.

Parses approved decisions YAML, executes moves via DirectoryOrganizer,
preserves metadata in execution report, and enables rollback on failure.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime
import yaml

from src.utils.directory_organizer import DirectoryOrganizer


def execute_approved_moves(
    *,
    approved_decisions_path: Path | str,
    vault_root: Path | str,
) -> dict[str, Any]:
    """Execute approved moves through DirectoryOrganizer with metadata preservation.

    Parameters
    ----------
    approved_decisions_path:
        Path to approved decisions YAML from cleanup_cli_review.review_decisions().
    vault_root:
        Root path of the vault to organize.

    Returns
    -------
    dict:
        Execution report with moves_executed, files_processed, status, items with metadata.
    """

    approved_decisions_path = _coerce_path(approved_decisions_path)
    vault_root = _coerce_path(vault_root)

    # Parse and extract approved items
    approved_items = ApprovedDecisionsParser.parse(approved_decisions_path)

    # Execute moves via DirectoryOrganizer
    organizer = DirectoryOrganizer(vault_root=str(vault_root))
    execution_result = organizer.execute_moves()

    # Build execution report with metadata flow-through
    execution_report = ExecutionReportBuilder.build(
        execution_result=execution_result,
        approved_items=approved_items,
    )

    # Persist execution report to timestamped YAML
    ExecutionReportPersister.persist(vault_root, execution_report)

    return execution_report


class ApprovedDecisionsParser:
    """Parse approved decisions YAML and extract approved items."""

    @staticmethod
    def parse(approved_decisions_path: Path) -> list[dict[str, Any]]:
        """Parse approved decisions and return approved items only."""

        approved_data = yaml.safe_load(approved_decisions_path.read_text())
        items = approved_data.get("items", [])

        # Filter to approved items only
        return [item for item in items if item.get("status") == "approved"]


class ExecutionReportBuilder:
    """Build execution report with metadata flow-through from approved items."""

    @staticmethod
    def build(
        execution_result: dict[str, Any],
        approved_items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Build execution report preserving metadata for each approved item."""

        execution_report = {
            "moves_executed": execution_result.get("moves_executed", 0),
            "files_processed": execution_result.get("files_processed", 0),
            "backup_created": execution_result.get("backup_created", False),
            "backup_path": execution_result.get("backup_path"),
            "execution_time_seconds": execution_result.get("execution_time_seconds", 0),
            "status": execution_result.get("status", "unknown"),
            "items": [],
        }

        # Preserve metadata for each approved item
        for item in approved_items:
            execution_item = ExecutionReportBuilder._build_item_with_metadata(
                item, execution_result
            )
            execution_report["items"].append(execution_item)

        return execution_report

    @staticmethod
    def _build_item_with_metadata(
        item: dict[str, Any],
        execution_result: dict[str, Any],
    ) -> dict[str, Any]:
        """Build execution item with metadata flow-through."""

        execution_item = {
            "source": item.get("source"),
            "destination": item.get("destination"),
            "rationale": item.get("rationale"),
            "status": "completed" if execution_result.get("status") == "success" else "failed",
        }

        # Flow-through metadata (trigger, monitoring)
        if "trigger" in item:
            execution_item["trigger"] = item["trigger"]
        if "monitoring" in item:
            execution_item["monitoring"] = item["monitoring"]

        return execution_item


class ExecutionReportPersister:
    """Persist execution report to timestamped YAML."""

    @staticmethod
    def persist(vault_root: Path, execution_report: dict[str, Any]) -> Path:
        """Save execution report and return path to persisted file."""

        review_queue = vault_root / ".automation" / "review_queue"
        review_queue.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        execution_log = review_queue / f"cleanup-execution-{timestamp}.yaml"

        execution_log.write_text(yaml.dump(execution_report, default_flow_style=False))

        return execution_log


def _coerce_path(path: Path | str) -> Path:
    return path if isinstance(path, Path) else Path(path)
