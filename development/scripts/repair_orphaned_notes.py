#!/usr/bin/env python3
"""
Repair Orphaned Notes - Fix notes stuck in Inbox with incorrect status/location

Problems Fixed:
  1. Notes with ai_processed=true but status=inbox (needs status update + move)
  2. Notes with status=promoted but still in Inbox (needs move only)

Both issues indicate broken auto-promotion workflow where status updates and file 
moves got decoupled. This script fixes both using NoteLifecycleManager.promote_note()
which atomically handles status updates, validation, and file moves.

Usage:
    # Preview what will be fixed (dry-run, default)
    python scripts/repair_orphaned_notes.py /path/to/vault

    # Apply fixes with backup
    python scripts/repair_orphaned_notes.py /path/to/vault --apply

    # Skip backup (not recommended)
    python scripts/repair_orphaned_notes.py /path/to/vault --apply --no-backup
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import shutil

# Add development to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai.note_lifecycle_manager import NoteLifecycleManager
from src.utils.frontmatter import parse_frontmatter


def find_orphaned_notes(inbox_dir: Path) -> List[Dict]:
    """
    Find two types of orphaned notes in Inbox:
    
    Type 1: ai_processed=true AND status=inbox (needs status update + move)
    Type 2: status=promoted but still in Inbox (needs move only)
    
    Returns:
        List of dicts with note info: path, type, title, quality_score, orphan_type
    """
    orphaned = []
    
    if not inbox_dir.exists():
        print(f"❌ Inbox directory not found: {inbox_dir}")
        return orphaned
    
    for note_path in inbox_dir.glob("*.md"):
        try:
            content = note_path.read_text(encoding='utf-8')
            frontmatter, body = parse_frontmatter(content)
            
            # Extract common fields
            note_type = frontmatter.get('type', 'fleeting')
            quality_score = frontmatter.get('quality_score', 0.0)
            ai_processed = frontmatter.get('ai_processed', False)
            status = frontmatter.get('status', 'inbox')
            
            # Extract title from first heading or filename
            title = note_path.stem
            for line in body.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            
            orphan_type = None
            
            # Type 1: AI processed but status never updated
            if ai_processed and status == 'inbox':
                orphan_type = 'needs_status_update'
            
            # Type 2: Status says promoted but file never moved
            elif status == 'promoted':
                orphan_type = 'needs_file_move'
            
            # Add to orphaned list if matches either type
            if orphan_type:
                orphaned.append({
                    'path': note_path,
                    'type': note_type,
                    'title': title[:50],  # Truncate long titles
                    'quality_score': quality_score,
                    'filename': note_path.name,
                    'orphan_type': orphan_type,
                    'status': status
                })
        
        except Exception as e:
            print(f"⚠️  Error reading {note_path.name}: {e}")
            continue
    
    return orphaned


def create_backup(vault_dir: Path) -> Path:
    """
    Create timestamped backup of vault before applying fixes.
    
    Returns:
        Path to backup directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = Path.home() / "backups"
    backup_root.mkdir(exist_ok=True)
    
    backup_dir = backup_root / f"{vault_dir.name}_repair_orphaned_{timestamp}"
    
    print(f"📦 Creating backup: {backup_dir}")
    shutil.copytree(vault_dir, backup_dir, ignore=shutil.ignore_patterns(
        '.git', '__pycache__', '*.pyc', '.DS_Store', 'node_modules',
        '.venv', 'venv', '.automation/cache', '.automation/logs'
    ))
    
    return backup_dir


def display_preview_table(orphaned: List[Dict]):
    """Display preview table of notes to be fixed."""
    if not orphaned:
        print("✅ No orphaned notes found!")
        return
    
    print(f"\n📊 Found {len(orphaned)} orphaned notes:\n")
    print("=" * 120)
    print(f"{'Type':<12} {'Status':<10} {'Issue':<25} {'Title':<45} {'Filename':<28}")
    print("=" * 120)
    
    # Group by orphan_type for better visualization
    by_orphan_type = {}
    for note in orphaned:
        orphan_type = note['orphan_type']
        by_orphan_type.setdefault(orphan_type, []).append(note)
    
    # Display Type 1 first (needs status update)
    if 'needs_status_update' in by_orphan_type:
        for note in by_orphan_type['needs_status_update']:
            issue = "ai_processed → no status"
            print(f"{note['type']:<12} {note['status']:<10} {issue:<25} {note['title']:<45} {note['filename']:<28}")
    
    # Display Type 2 (needs file move)
    if 'needs_file_move' in by_orphan_type:
        for note in by_orphan_type['needs_file_move']:
            issue = "status:promoted → not moved"
            print(f"{note['type']:<12} {note['status']:<10} {issue:<25} {note['title']:<45} {note['filename']:<28}")
    
    print("=" * 120)
    print(f"\nSummary by issue type:")
    print(f"  - Needs status update + move: {len(by_orphan_type.get('needs_status_update', []))} notes")
    print(f"  - Needs file move only: {len(by_orphan_type.get('needs_file_move', []))} notes")
    
    # Also show breakdown by note type
    by_note_type = {}
    for note in orphaned:
        note_type = note['type']
        by_note_type.setdefault(note_type, []).append(note)
    print(f"\nBreakdown by note type:")
    for note_type in sorted(by_note_type.keys()):
        print(f"  - {note_type}: {len(by_note_type[note_type])} notes")


def repair_orphaned_notes(vault_dir: Path, apply: bool = False, skip_backup: bool = False) -> Dict:
    """
    Main repair function.
    
    Args:
        vault_dir: Path to vault root
        apply: If True, apply fixes. If False, dry-run preview only.
        skip_backup: If True, skip backup creation (not recommended)
    
    Returns:
        Result dict with counts and errors
    """
    inbox_dir = vault_dir / "Inbox"
    
    print(f"🔍 Scanning for orphaned notes in: {inbox_dir}\n")
    
    # Find orphaned notes
    orphaned = find_orphaned_notes(inbox_dir)
    
    # Display preview
    display_preview_table(orphaned)
    
    if not orphaned:
        return {'fixed': 0, 'errors': 0, 'skipped': 0}
    
    # Dry-run mode
    if not apply:
        print(f"\n💡 This was a DRY-RUN preview. No files were modified.")
        print(f"   To apply fixes, run with --apply flag:")
        print(f"   python scripts/repair_orphaned_notes.py {vault_dir} --apply")
        return {'fixed': 0, 'errors': 0, 'skipped': len(orphaned)}
    
    # Apply mode - create backup first
    if not skip_backup:
        backup_dir = create_backup(vault_dir)
        print(f"✅ Backup created: {backup_dir}\n")
    else:
        print("⚠️  Skipping backup (--no-backup flag)\n")
    
    # Initialize NoteLifecycleManager
    manager = NoteLifecycleManager(base_dir=vault_dir)
    
    # Apply fixes
    print(f"\n🔧 Applying fixes to {len(orphaned)} notes...\n")
    
    fixed_count = 0
    error_count = 0
    
    for note in orphaned:
        note_path = note['path']
        print(f"  Fixing: {note['filename']} ({note['type']})... ", end='')
        
        result = manager.promote_note(note_path)
        
        if result.get('promoted'):
            print(f"✅ Moved to {Path(result['destination_dir']).name}/")
            fixed_count += 1
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ Error: {error_msg}")
            error_count += 1
    
    print(f"\n📊 Repair Summary:")
    print(f"  ✅ Fixed: {fixed_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"  📦 Backup: {backup_dir if not skip_backup else 'Skipped'}")
    
    return {'fixed': fixed_count, 'errors': error_count, 'backup': str(backup_dir) if not skip_backup else None}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Repair orphaned notes (ai_processed=true + status=inbox)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview (dry-run)
  python scripts/repair_orphaned_notes.py /Users/user/vault

  # Apply fixes with backup
  python scripts/repair_orphaned_notes.py /Users/user/vault --apply

  # Apply without backup (not recommended)
  python scripts/repair_orphaned_notes.py /Users/user/vault --apply --no-backup
        """
    )
    
    parser.add_argument('vault_dir', type=Path, help='Path to vault root directory')
    parser.add_argument('--apply', action='store_true', 
                       help='Apply fixes (default is dry-run preview only)')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip backup creation (not recommended)')
    
    args = parser.parse_args()
    
    # Validate vault directory
    if not args.vault_dir.exists():
        print(f"❌ Error: Vault directory not found: {args.vault_dir}")
        sys.exit(1)
    
    if not (args.vault_dir / "Inbox").exists():
        print(f"❌ Error: Inbox directory not found in vault: {args.vault_dir / 'Inbox'}")
        sys.exit(1)
    
    # Run repair
    print("=" * 100)
    print("  REPAIR ORPHANED NOTES - Fix ai_processed=true + status=inbox")
    print("=" * 100)
    print()
    
    result = repair_orphaned_notes(
        vault_dir=args.vault_dir,
        apply=args.apply,
        skip_backup=args.no_backup
    )
    
    # Exit code based on results
    if result['errors'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
