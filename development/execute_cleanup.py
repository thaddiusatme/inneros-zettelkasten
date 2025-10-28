#!/usr/bin/env python3
"""Execute cleanup workflow with REAL file moves and backup.

This script performs actual file reorganization using DirectoryOrganizer.
Creates timestamped backup before any moves.
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add development to path
sys.path.insert(0, str(Path(__file__).parent))

from src.automation.cleanup_inventory import generate_inventory
from src.automation.cleanup_decision_log import generate_decision_log
from src.automation.cleanup_file_mover import execute_cleanup_moves
import yaml


def main():
    """Execute cleanup workflow with real file moves."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Execute cleanup workflow with real file moves"
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt and proceed automatically"
    )
    args = parser.parse_args()
    
    vault_root = Path(__file__).parent.parent
    automation_dir = vault_root / ".automation" / "review_queue"
    automation_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("🧹 CLEANUP EXECUTION - REAL FILE MOVES")
    print("=" * 80)
    print(f"\n📁 Vault Root: {vault_root}")
    print("\n⚠️  WARNING: This will move files and create a backup.")
    print("    Backup will be created at: backups/inneros-zettelkasten-TIMESTAMP/\n")
    
    # Step 1: Generate inventory
    print("📋 Step 1: Generating inventory...")
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    inventory_path = automation_dir / f"cleanup-inventory-{timestamp}.yaml"
    
    sources = _collect_sources(vault_root)
    generate_inventory(
        vault_root=vault_root,
        inventory_path=inventory_path,
        sources=sources,
    )
    
    # Read inventory to show summary
    inventory_data = yaml.safe_load(inventory_path.read_text())
    total_items = len(inventory_data.get("items", []))
    print(f"   ✅ Found {total_items} files to move")
    
    # Step 2: Generate decision log
    print("\n📝 Step 2: Generating decision log...")
    decision_log_path = automation_dir / f"cleanup-decisions-{timestamp}.yaml"
    generate_decision_log(
        inventory_path=inventory_path,
        decision_log_path=decision_log_path,
    )
    print(f"   ✅ Decision log created")
    
    # Step 3: Auto-approve all (for automated execution)
    print("\n✅ Step 3: Auto-approving all moves...")
    decision_data = yaml.safe_load(decision_log_path.read_text())
    items = decision_data.get("items", [])
    for item in items:
        item["status"] = "approved"
    
    approved_path = automation_dir / f"cleanup-approved-{timestamp}.yaml"
    approved_path.write_text(yaml.dump({"items": items}, default_flow_style=False))
    print(f"   ✅ {len(items)} moves approved")
    
    # Step 4: Show summary and confirm
    print("\n" + "=" * 80)
    print("📊 CLEANUP SUMMARY")
    print("=" * 80)
    print(f"\n🗂️  Files to move: {len(items)}")
    print("\n📁 Sample moves:")
    for item in items[:5]:
        print(f"   • {item['source']}")
        print(f"     → {item['destination']}")
    if len(items) > 5:
        print(f"   ... and {len(items) - 5} more")
    
    print("\n💾 A backup will be created before any files are moved.")
    print("   Location: ~/backups/inneros-zettelkasten-{timestamp}/")
    
    if not args.yes:
        response = input("\n❓ Proceed with cleanup? (yes/no): ").strip().lower()
        if response not in ["yes", "y"]:
            print("\n❌ Cleanup cancelled.")
            return 0
    else:
        print("\n✅ Auto-approved via --yes flag")
    
    # Step 5: Execute moves with cleanup file mover
    print("\n🚀 Step 4: Executing moves...")
    print("   Creating backup...")
    
    # Execute moves from approved decisions
    execution_result = execute_cleanup_moves(
        approved_decisions_path=approved_path,
        vault_root=vault_root,
        create_backup=True,
    )
    
    # Step 6: Generate execution report
    execution_report_path = automation_dir / f"cleanup-execution-{timestamp}.yaml"
    execution_report = {
        "timestamp": timestamp,
        "status": execution_result.get("status", "unknown"),
        "moves_executed": execution_result.get("moves_executed", 0),
        "files_processed": execution_result.get("files_processed", 0),
        "backup_path": str(execution_result.get("backup_path", "")),
        "execution_time_seconds": execution_result.get("execution_time_seconds", 0),
        "items": execution_result.get("items", []),
    }
    
    execution_report_path.write_text(
        yaml.dump(execution_report, default_flow_style=False)
    )
    
    # Display results
    print("\n" + "=" * 80)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 80)
    
    print(f"\n📊 Results:")
    print(f"   • Files moved: {execution_result.get('moves_executed', 0)}")
    print(f"   • Execution time: {execution_result.get('execution_time_seconds', 0):.2f}s")
    print(f"\n💾 Backup location:")
    print(f"   {execution_result.get('backup_path', 'N/A')}")
    print(f"\n📋 Execution report:")
    print(f"   {execution_report_path}")
    
    # Show any errors
    failed_items = [
        item for item in execution_result.get("items", [])
        if item.get("status") == "failed"
    ]
    if failed_items:
        print(f"\n⚠️  {len(failed_items)} moves failed:")
        for item in failed_items[:5]:
            print(f"   • {item['source']}")
    
    return 0


def _collect_sources(vault_root: Path) -> list[str]:
    """Collect all markdown files from vault directories."""
    sources = []
    
    for directory in [
        vault_root / "Projects" / "ACTIVE",
        vault_root / "development" / "docs",
        vault_root / ".automation" / "scripts",
    ]:
        if directory.exists():
            for md_file in directory.rglob("*.md"):
                try:
                    relative_path = md_file.relative_to(vault_root)
                    sources.append(str(relative_path))
                except ValueError:
                    pass
    
    return sources


if __name__ == "__main__":
    sys.exit(main())
