#!/usr/bin/env python3
"""
Execute Root Directory Archival - Knowledge Base Cleanup Phase 2

Moves approved files from root to appropriate archive locations.
Only handles clear archival candidates (session, phase, completion docs).

Safety features:
- Dry-run mode by default
- Creates destination directories
- Uses git mv for tracked files
- Comprehensive logging
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List
import subprocess
import shutil


class RootDirectoryArchiver:
    """Execute root directory archival moves."""
    
    # Clear archival decisions (from TT-10 analysis)
    ARCHIVAL_PLAN = {
        'session_state': {
            'files': [
                'NEXT_SESSION_AUTOMATION.md',
                'NEXT_SESSION_PROMPT.md',
                'CURRENT-STATE-2025-10-19.md',
                'NEXT_CHAT_PROMPT.md',
            ],
            'destination': 'Projects/COMPLETED-2025-10/',
        },
        'phase_docs': {
            'files': [
                'PHASE-2.2-COMPLETION-ASSESSMENT.md',
                'PHASE-3-PREP.md',
                'DEMO-PHASE-2.2.sh',
                'PHASE2-COMPLETE-SUMMARY.md',
                'QUICK-START-PHASE-2.2.md',
            ],
            'destination': 'Projects/COMPLETED-2025-10/',
        },
        'completion_docs': {
            'files': [
                'INBOX-PROCESSING-FIX-SUMMARY.md',
            ],
            'destination': 'Projects/COMPLETED-2025-10/',
        },
        'metrics': {
            'files': [
                'orphan-metrics.md',
                'orphan-metrics.json',
                'analytics_report.json',
            ],
            'destination': 'Projects/COMPLETED-2025-10/metrics/',
        },
    }
    
    # Files to delete (logs + empty files)
    DELETE_CANDIDATES = [
        'integration-test-results.log',
        'complete_integration_demo.log',
        'unit-test-profile.log',
        'distribution-test-profile.log',
        'Pasted image 20250729144519.png.md',
        'watcher.log',
    ]
    
    def __init__(self, root_dir: Path, dry_run: bool = True):
        """Initialize archiver."""
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.results = {
            'moved': [],
            'deleted': [],
            'errors': [],
        }
    
    def execute(self) -> Dict:
        """Execute archival plan."""
        print(f"{'🔍 DRY-RUN MODE' if self.dry_run else '🚀 EXECUTION MODE'}")
        print(f"   Root: {self.root_dir}")
        print()
        
        # Create destination directories
        self._create_destinations()
        
        # Execute moves
        self._execute_moves()
        
        # Execute deletions
        self._execute_deletions()
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _create_destinations(self) -> None:
        """Create destination directories if they don't exist."""
        destinations = set()
        for category, plan in self.ARCHIVAL_PLAN.items():
            destinations.add(plan['destination'])
        
        for dest in destinations:
            dest_path = self.root_dir / dest
            
            if not dest_path.exists():
                print(f"📁 Creating: {dest}")
                if not self.dry_run:
                    dest_path.mkdir(parents=True, exist_ok=True)
    
    def _execute_moves(self) -> None:
        """Execute file moves."""
        print("\n📦 Archiving Files:")
        
        for category, plan in self.ARCHIVAL_PLAN.items():
            destination = plan['destination']
            
            for filename in plan['files']:
                source_path = self.root_dir / filename
                dest_path = self.root_dir / destination / filename
                
                if not source_path.exists():
                    print(f"  ⚠️  Not found: {filename}")
                    self.results['errors'].append({
                        'file': filename,
                        'error': 'File not found',
                    })
                    continue
                
                # Check if file is tracked by git
                is_tracked = self._is_git_tracked(filename)
                
                if self.dry_run:
                    print(f"  → {filename}")
                    print(f"    Destination: {destination}")
                    print(f"    Method: {'git mv' if is_tracked else 'mv'}")
                else:
                    try:
                        if is_tracked:
                            # Use git mv to preserve history
                            subprocess.run(
                                ['git', 'mv', str(source_path), str(dest_path)],
                                cwd=self.root_dir,
                                check=True,
                                capture_output=True,
                            )
                        else:
                            # Regular move
                            shutil.move(str(source_path), str(dest_path))
                        
                        print(f"  ✅ Moved: {filename} → {destination}")
                        self.results['moved'].append({
                            'file': filename,
                            'destination': destination,
                            'method': 'git mv' if is_tracked else 'mv',
                        })
                    
                    except Exception as e:
                        print(f"  ❌ Error moving {filename}: {e}")
                        self.results['errors'].append({
                            'file': filename,
                            'error': str(e),
                        })
    
    def _execute_deletions(self) -> None:
        """Execute file deletions."""
        print("\n🗑️  Deleting Files:")
        
        for filename in self.DELETE_CANDIDATES:
            file_path = self.root_dir / filename
            
            if not file_path.exists():
                print(f"  ⚠️  Not found: {filename}")
                continue
            
            if self.dry_run:
                print(f"  → {filename}")
            else:
                try:
                    file_path.unlink()
                    print(f"  ✅ Deleted: {filename}")
                    self.results['deleted'].append(filename)
                
                except Exception as e:
                    print(f"  ❌ Error deleting {filename}: {e}")
                    self.results['errors'].append({
                        'file': filename,
                        'error': str(e),
                    })
    
    def _is_git_tracked(self, filename: str) -> bool:
        """Check if file is tracked by git."""
        try:
            result = subprocess.run(
                ['git', 'ls-files', '--error-unmatch', filename],
                cwd=self.root_dir,
                capture_output=True,
                check=False,
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _print_summary(self) -> None:
        """Print execution summary."""
        print("\n📊 Summary:")
        
        if self.dry_run:
            total_moves = sum(len(plan['files']) for plan in self.ARCHIVAL_PLAN.values())
            total_deletes = len(self.DELETE_CANDIDATES)
            print(f"   Would move: {total_moves} files")
            print(f"   Would delete: {total_deletes} files")
            print(f"   Total operations: {total_moves + total_deletes}")
        else:
            print(f"   Moved: {len(self.results['moved'])} files")
            print(f"   Deleted: {len(self.results['deleted'])} files")
            print(f"   Errors: {len(self.results['errors'])}")
            
            if self.results['errors']:
                print("\n❌ Errors:")
                for error in self.results['errors']:
                    print(f"   - {error['file']}: {error['error']}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Execute root directory archival'
    )
    parser.add_argument(
        '--root-dir',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Repository root directory (default: parent of development/)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing (default: true)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute archival (modifies filesystem)'
    )
    
    args = parser.parse_args()
    
    # Determine execution mode: execute mode only if --execute flag provided
    dry_run = not args.execute
    
    print("🔧 Root Directory Archival - InnerOS Zettelkasten")
    print()
    
    # Execute
    archiver = RootDirectoryArchiver(root_dir=args.root_dir, dry_run=dry_run)
    results = archiver.execute()
    
    print()
    if dry_run:
        print("⚠️  DRY-RUN mode - No files were modified")
        print("   Run with --execute to apply changes")
    else:
        print("✅ Archival complete")
        print(f"   Commit changes with: git add -A && git commit")
    
    return 0 if not results['errors'] else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
