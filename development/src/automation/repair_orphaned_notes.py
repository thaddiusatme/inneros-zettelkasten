"""
Orphaned Notes Repair Engine - Knowledge Base Cleanup Phase 2

Fixes notes with ai_processed: true but status: inbox by:
- Updating status to 'promoted'
- Adding processed_date timestamp
- Preserving all other frontmatter

Part of TDD iteration for Knowledge Base Cleanup.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import yaml
import re


def detect_orphaned_notes(note_path: Path) -> bool:
    """
    Detect if a note is orphaned (ai_processed but status still 'inbox').
    
    Parameters
    ----------
    note_path : Path
        Path to the markdown note to check
    
    Returns
    -------
    bool
        True if note is orphaned, False otherwise
    """
    try:
        content = note_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            return False
        
        frontmatter = yaml.safe_load(match.group(1)) or {}
        
        # Check conditions for orphaned note
        status = frontmatter.get('status', '')
        ai_processed = frontmatter.get('ai_processed', False)
        
        # Orphaned if: ai_processed is truthy AND status is 'inbox'
        return bool(ai_processed) and status == 'inbox'
    
    except Exception:
        return False


def repair_note_status(note_path: Path, dry_run: bool = False) -> Dict:
    """
    Repair an orphaned note by updating status to 'promoted'.
    
    Parameters
    ----------
    note_path : Path
        Path to the note to repair
    dry_run : bool
        If True, don't actually modify the file
    
    Returns
    -------
    Dict
        Result dictionary with success, old_status, new_status, etc.
    """
    try:
        content = note_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not match:
            return {
                'success': False,
                'error': 'No frontmatter found'
            }
        
        frontmatter_str = match.group(1)
        body = match.group(2)
        
        # Parse frontmatter
        frontmatter = yaml.safe_load(frontmatter_str) or {}
        
        old_status = frontmatter.get('status', 'unknown')
        
        # Update status and add processed_date
        frontmatter['status'] = 'promoted'
        processed_date = datetime.now().isoformat()
        frontmatter['processed_date'] = processed_date
        
        result = {
            'success': True,
            'old_status': old_status,
            'new_status': 'promoted',
            'processed_date': processed_date,
            'dry_run': dry_run,
            'path': str(note_path)
        }
        
        # If not dry-run, write the updated content
        if not dry_run:
            # Rebuild the file
            new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            new_content = f"---\n{new_frontmatter}---\n{body}"
            note_path.write_text(new_content, encoding='utf-8')
        
        return result
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'path': str(note_path)
        }


class RepairEngine:
    """
    Orchestrates batch repair of orphaned notes in a directory.
    """
    
    def __init__(self, inbox_dir: Path):
        """
        Initialize the repair engine.
        
        Parameters
        ----------
        inbox_dir : Path
            Path to the inbox directory to scan
        """
        self.inbox_dir = inbox_dir
    
    def find_orphaned_notes(self) -> List[Path]:
        """
        Scan inbox directory for orphaned notes.
        
        Returns
        -------
        List[Path]
            List of paths to orphaned notes
        """
        orphaned = []
        
        if not self.inbox_dir.exists():
            return orphaned
        
        for note_path in self.inbox_dir.glob('**/*.md'):
            if detect_orphaned_notes(note_path):
                orphaned.append(note_path)
        
        return orphaned
    
    def repair_all(self, dry_run: bool = True) -> Dict:
        """
        Repair all orphaned notes in the inbox.
        
        Parameters
        ----------
        dry_run : bool
            If True, don't actually modify files
        
        Returns
        -------
        Dict
            Comprehensive repair report
        """
        all_notes = list(self.inbox_dir.glob('**/*.md')) if self.inbox_dir.exists() else []
        orphaned_notes = self.find_orphaned_notes()
        
        results = []
        repaired_count = 0
        error_count = 0
        
        for note_path in orphaned_notes:
            result = repair_note_status(note_path, dry_run=dry_run)
            results.append(result)
            
            if result['success']:
                if not dry_run:
                    repaired_count += 1
            else:
                error_count += 1
        
        return {
            'total_scanned': len(all_notes),
            'orphaned_found': len(orphaned_notes),
            'repaired': repaired_count,
            'errors': error_count,
            'dry_run': dry_run,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }


def generate_repair_report(report_data: Dict, output_file: Path) -> None:
    """
    Generate a YAML repair report.
    
    Parameters
    ----------
    report_data : Dict
        Report data dictionary
    output_file : Path
        Path to write the YAML report
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        yaml.dump(report_data, f, default_flow_style=False, sort_keys=False)


def main():
    """Main entry point for CLI usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Repair orphaned notes (ai_processed: true, status: inbox)'
    )
    parser.add_argument(
        '--inbox-dir',
        type=Path,
        default=Path('knowledge/Inbox'),
        help='Path to inbox directory (default: knowledge/Inbox)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute repairs (modifies files)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output path for repair report YAML'
    )
    
    args = parser.parse_args()
    
    # Determine dry_run mode
    dry_run = not args.execute or args.dry_run
    
    print("🔧 Orphaned Notes Repair Engine")
    print(f"   Mode: {'DRY-RUN (preview only)' if dry_run else 'EXECUTE (will modify files)'}")
    print(f"   Inbox: {args.inbox_dir}")
    print()
    
    # Run repair
    engine = RepairEngine(inbox_dir=args.inbox_dir)
    report = engine.repair_all(dry_run=dry_run)
    
    # Print summary
    print("📊 Repair Summary")
    print(f"   Total notes scanned: {report['total_scanned']}")
    print(f"   Orphaned notes found: {report['orphaned_found']}")
    print(f"   Successfully repaired: {report['repaired']}")
    print(f"   Errors: {report['errors']}")
    print()
    
    if dry_run:
        print("⚠️  DRY-RUN mode - No files were modified")
        print("   Run with --execute to apply changes")
    else:
        print("✅ Repairs applied successfully")
    print()
    
    # Save report if requested
    if args.output:
        generate_repair_report(report, args.output)
        print(f"💾 Report saved to: {args.output}")
    else:
        # Default output location
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        default_output = Path('.automation/review_queue') / f'repair-report-{timestamp}.yaml'
        generate_repair_report(report, default_output)
        print(f"💾 Report saved to: {default_output}")
    
    return 0 if report['errors'] == 0 else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
