"""Simple file mover for cleanup workflow - executes explicit source → destination moves."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from datetime import datetime
import shutil
import yaml


def execute_cleanup_moves(
    *,
    approved_decisions_path: Path | str,
    vault_root: Path | str,
    create_backup: bool = True,
) -> dict[str, Any]:
    """Execute explicit file moves from approved decisions YAML.

    Parameters
    ----------
    approved_decisions_path:
        Path to approved decisions YAML.
    vault_root:
        Root path of the vault.
    create_backup:
        Whether to create a timestamped backup before moving files.

    Returns
    -------
    dict:
        Execution report with moves_executed, backup_path, status, items.
    """

    approved_decisions_path = Path(approved_decisions_path)
    vault_root = Path(vault_root)

    # Parse approved decisions
    approved_data = yaml.safe_load(approved_decisions_path.read_text())
    items = [
        item
        for item in approved_data.get("items", [])
        if item.get("status") == "approved"
    ]

    start_time = datetime.now()

    # Create backup if requested
    backup_path = None
    if create_backup:
        backup_path = _create_backup(vault_root)

    # Execute moves
    execution_items = []
    moves_executed = 0

    for item in items:
        source = vault_root / item["source"]
        destination = vault_root / item["destination"]

        try:
            # Create destination directory if needed
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(source), str(destination))

            execution_items.append(
                {
                    "source": item["source"],
                    "destination": item["destination"],
                    "rationale": item.get("rationale", ""),
                    "status": "completed",
                    **{k: v for k, v in item.items() if k in ["trigger", "monitoring"]},
                }
            )
            moves_executed += 1

        except Exception as e:
            execution_items.append(
                {
                    "source": item["source"],
                    "destination": item["destination"],
                    "rationale": item.get("rationale", ""),
                    "status": "failed",
                    "error": str(e),
                }
            )

    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()

    # Build execution report
    execution_report = {
        "timestamp": start_time.strftime("%Y%m%d-%H%M%S"),
        "moves_executed": moves_executed,
        "files_processed": moves_executed,
        "backup_created": backup_path is not None,
        "backup_path": str(backup_path) if backup_path else None,
        "execution_time_seconds": execution_time,
        "status": "success" if moves_executed == len(items) else "partial_success",
        "items": execution_items,
    }

    return execution_report


def _create_backup(vault_root: Path) -> Path:
    """Create timestamped backup of vault."""

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = Path.home() / "backups"
    backup_root.mkdir(parents=True, exist_ok=True)

    backup_path = backup_root / f"inneros-zettelkasten-{timestamp}"

    # Copy vault to backup (exclude large directories)
    exclude_patterns = {
        "backups",
        ".git",
        "web_ui_env",
        ".venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".embedding_cache",
        "development",
    }

    def should_exclude(path: Path) -> bool:
        return any(pattern in path.parts for pattern in exclude_patterns)

    shutil.copytree(
        vault_root,
        backup_path,
        ignore=lambda dir, files: [f for f in files if should_exclude(Path(dir) / f)],
        symlinks=True,
    )

    return backup_path
