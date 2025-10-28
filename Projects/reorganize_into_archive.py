#!/usr/bin/env python3
"""
Projects Directory Reorganization Script
Moves COMPLETED-* and DEPRECATED folders INTO Archive/ for cleaner organization
Follows safety-first principles with dry-run mode and comprehensive logging
"""

import shutil
from pathlib import Path
from datetime import datetime
import sys

# Color codes for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(message: str):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_info(message: str):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_error(message: str):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


class ProjectsReorganizer:
    """Moves COMPLETED-* and DEPRECATED folders into Archive/ for cleaner structure"""
    
    def __init__(self, projects_root: Path, dry_run: bool = True):
        self.projects_root = projects_root
        self.archive_dir = projects_root / "Archive"
        self.dry_run = dry_run
        self.stats = {
            'dirs_moved': 0,
            'errors': 0
        }
    
    def ensure_archive_exists(self):
        """Ensure Archive directory exists"""
        if not self.archive_dir.exists():
            if self.dry_run:
                print_info(f"Would create Archive/ directory")
            else:
                self.archive_dir.mkdir(parents=True, exist_ok=True)
                print_success(f"Created Archive/ directory")
    
    def move_directory(self, source: Path, target: Path):
        """Move entire directory with contents"""
        try:
            if target.exists():
                print_error(f"Target already exists: {target.relative_to(self.projects_root)}")
                print_warning(f"Skipping to prevent overwrite")
                self.stats['errors'] += 1
                return False
            
            if self.dry_run:
                print_info(f"Would move: {source.name}/")
                print_info(f"  From: {source.relative_to(self.projects_root)}")
                print_info(f"  To:   {target.relative_to(self.projects_root)}")
            else:
                shutil.move(str(source), str(target))
                print_success(f"Moved: {source.name}/ → Archive/{source.name}/")
            
            self.stats['dirs_moved'] += 1
            return True
            
        except Exception as e:
            print_error(f"Error moving {source.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def reorganize(self):
        """Execute reorganization"""
        print_header("Projects Directory Reorganization")
        print_info(f"Projects Root: {self.projects_root}")
        print_info(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTION'}\n")
        
        # Ensure Archive exists
        self.ensure_archive_exists()
        
        print_header("Moving ADRs to ACTIVE/")
        
        # Move ADRs from Archive to ACTIVE
        adrs_source = self.archive_dir / "adrs-2025"
        adrs_target = self.projects_root / "ACTIVE" / "adrs-2025"
        if adrs_source.exists():
            self.move_directory(adrs_source, adrs_target)
        else:
            print_warning("adrs-2025/ not found in Archive/")
        
        print_header("Moving Historical Folders into Archive/")
        
        # Folders to move into Archive
        folders_to_move = [
            "COMPLETED-2025-08",
            "COMPLETED-2025-09",
            "COMPLETED-2025-10",
            "DEPRECATED"
        ]
        
        for folder_name in folders_to_move:
            source = self.projects_root / folder_name
            if source.exists() and source.is_dir():
                target = self.archive_dir / folder_name
                self.move_directory(source, target)
            else:
                print_warning(f"Folder not found: {folder_name}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print operation summary"""
        print_header("REORGANIZATION SUMMARY")
        
        mode = "DRY RUN" if self.dry_run else "EXECUTION"
        print(f"Mode: {Colors.BOLD}{mode}{Colors.ENDC}\n")
        
        print(f"Directories moved:  {Colors.OKGREEN}{self.stats['dirs_moved']}{Colors.ENDC}")
        
        if self.stats['errors'] > 0:
            print(f"Errors encountered: {Colors.FAIL}{self.stats['errors']}{Colors.ENDC}")
        else:
            print(f"Errors encountered: {Colors.OKGREEN}0{Colors.ENDC}")
        
        if self.dry_run:
            print(f"\n{Colors.WARNING}{Colors.BOLD}This was a DRY RUN - no changes were made{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Run with --execute flag to perform actual reorganization{Colors.ENDC}")
        else:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✨ Reorganization complete!{Colors.ENDC}")
            print(f"\n{Colors.BOLD}Final Structure:{Colors.ENDC}")
            print("Projects/")
            print("├── ACTIVE/")
            print("│   └── adrs-2025/ (active ADRs)")
            print("├── Archive/")
            print("│   ├── COMPLETED-2025-08/")
            print("│   ├── COMPLETED-2025-09/")
            print("│   ├── COMPLETED-2025-10/")
            print("│   └── DEPRECATED/")
            print("├── REFERENCE/")
            print("└── TEMPLATES/")


def main():
    """Main entry point"""
    # Determine execution mode
    dry_run = "--execute" not in sys.argv
    
    # Get projects directory
    script_dir = Path(__file__).parent
    projects_root = script_dir
    
    # Validate directory structure
    if not projects_root.exists():
        print_error("Projects directory not found!")
        sys.exit(1)
    
    # Run reorganization
    reorganizer = ProjectsReorganizer(projects_root, dry_run=dry_run)
    reorganizer.reorganize()
    
    # Exit code based on errors
    sys.exit(0 if reorganizer.stats['errors'] == 0 else 1)


if __name__ == "__main__":
    main()
