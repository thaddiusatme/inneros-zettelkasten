#!/usr/bin/env python3
"""
Repair Orphaned Notes - Fix notes stuck with ai_processed=true + status=inbox

Problem: 77 notes have been AI processed but their status wasn't updated to 'promoted',
causing them to remain in Inbox/ instead of moving to their type-specific directories.

Solution: Update status to 'promoted', add processed_date, and move files using
NoteLifecycleManager.promote_note().

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
    Find notes with ai_processed=true AND status=inbox.
    
    These are "orphaned" - AI has processed them but they weren't promoted.
    
    Returns:
        List of dicts with note info: path, type, title, quality_score
    """
    orphaned = []
    
    if not inbox_dir.exists():
        print(f"❌ Inbox directory not found: {inbox_dir}")
        return orphaned
    
    for note_path in inbox_dir.glob("*.md"):
        try:
            content = note_path.read_text(encoding='utf-8')
            frontmatter, body = parse_frontmatter(content)
            
            # Check if note is orphaned
            ai_processed = frontmatter.get('ai_processed', False)
            status = frontmatter.get('status', 'inbox')
            
            if ai_processed and status == 'inbox':
                # Extract note info
                note_type = frontmatter.get('type', 'fleeting')
                quality_score = frontmatter.get('quality_score', 0.0)
                
                # Extract title from first heading or filename
                title = note_path.stem
                for line in body.split('\n'):
                    if line.startswith('# '):
                        title = line[2:].strip()
                        break
                
                orphaned.append({
                    'path': note_path,
                    'type': note_type,
                    'title': title[:50],  # Truncate long titles
                    'quality_score': quality_score,
                    'filename': note_path.name
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
    print("=" * 100)
    print(f"{'Type':<12} {'Quality':<10} {'Title':<50} {'Filename':<28}")
    print("=" * 100)
    
    # Group by type for better visualization
    by_type = {}
    for note in orphaned:
        note_type = note['type']
        by_type.setdefault(note_type, []).append(note)
    
    for note_type in ['permanent', 'literature', 'fleeting']:
        notes = by_type.get(note_type, [])
        if notes:
            for note in notes:
                quality = f"{note['quality_score']:.2f}" if note['quality_score'] else "N/A"
                print(f"{note_type:<12} {quality:<10} {note['title']:<50} {note['filename']:<28}")
    
    print("=" * 100)
    print(f"\nSummary by type:")
    for note_type, notes in by_type.items():
        print(f"  - {note_type}: {len(notes)} notes")


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
