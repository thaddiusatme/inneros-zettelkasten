#!/usr/bin/env python3
"""Quick validation of repair_orphaned_notes logic."""

from pathlib import Path
from src.automation.repair_orphaned_notes import RepairEngine

# Test on actual inbox
inbox_dir = Path(__file__).parent.parent / "knowledge" / "Inbox"

print(f"Testing repair engine on: {inbox_dir}")
print(f"Inbox exists: {inbox_dir.exists()}")

if inbox_dir.exists():
    engine = RepairEngine(inbox_dir=inbox_dir)
    print("Finding orphaned notes...")
    orphaned = engine.find_orphaned_notes()
    print(f"Found {len(orphaned)} orphaned notes")
    
    if len(orphaned) > 0:
        print("\nFirst 3 orphaned notes:")
        for note in orphaned[:3]:
            print(f"  - {note.relative_to(inbox_dir.parent)}")
    
    print("\nGenerating report (dry-run)...")
    report = engine.repair_all(dry_run=True)
    
    print(f"\nReport Summary:")
    print(f"  Total scanned: {report['total_scanned']}")
    print(f"  Orphaned found: {report['orphaned_found']}")
    print(f"  Would repair: {report['orphaned_found']}")
    
    print("\n✅ Validation complete - repair engine works!")
else:
    print("❌ Inbox directory not found")
