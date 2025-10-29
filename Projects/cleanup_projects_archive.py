#!/usr/bin/env python3
"""
Projects Directory Cleanup Script
Consolidates Archive/ structure into proper COMPLETED-* and DEPRECATED/ folders
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


class ProjectsCleanup:
    """Handles safe cleanup and consolidation of Projects directory structure"""
    
    def __init__(self, projects_root: Path, dry_run: bool = True):
        self.projects_root = projects_root
        self.archive_dir = projects_root / "Archive"
        self.dry_run = dry_run
        self.operations = []
        self.stats = {
            'files_moved': 0,
            'dirs_created': 0,
            'dirs_removed': 0,
            'errors': 0
        }
    
    def ensure_target_dir(self, target_dir: Path):
        """Ensure target directory exists"""
        if not target_dir.exists():
            if self.dry_run:
                print_info(f"Would create directory: {target_dir.relative_to(self.projects_root)}")
            else:
                target_dir.mkdir(parents=True, exist_ok=True)
                print_success(f"Created directory: {target_dir.relative_to(self.projects_root)}")
            self.stats['dirs_created'] += 1
    
    def move_file(self, source: Path, target: Path):
        """Move a file with conflict detection"""
        try:
            if target.exists():
                print_warning(f"Conflict: {target.name} already exists in {target.parent.name}/")
                print_info(f"  Source: {source.relative_to(self.projects_root)}")
                print_info(f"  Target: {target.relative_to(self.projects_root)}")
                print_warning(f"  Skipping to prevent overwrite")
                return False
            
            if self.dry_run:
                print_info(f"Would move: {source.name}")
                print_info(f"  From: {source.parent.relative_to(self.projects_root)}/")
                print_info(f"  To:   {target.parent.relative_to(self.projects_root)}/")
            else:
                self.ensure_target_dir(target.parent)
                shutil.move(str(source), str(target))
                print_success(f"Moved: {source.name} → {target.parent.name}/")
            
            self.stats['files_moved'] += 1
            return True
            
        except Exception as e:
            print_error(f"Error moving {source.name}: {e}")
            self.stats['errors'] += 1
            return False
    
    def move_directory(self, source: Path, target: Path):
        """Move entire directory with contents"""
        try:
            if target.exists():
                print_warning(f"Target directory exists: {target.relative_to(self.projects_root)}")
                print_info(f"Merging contents from: {source.relative_to(self.projects_root)}")
                
                # Move contents individually
                for item in source.iterdir():
                    if item.is_file():
                        self.move_file(item, target / item.name)
                    elif item.is_dir():
                        self.move_directory(item, target / item.name)
            else:
                if self.dry_run:
                    print_info(f"Would move directory: {source.name}/")
                    print_info(f"  From: {source.parent.relative_to(self.projects_root)}/")
                    print_info(f"  To:   {target.parent.relative_to(self.projects_root)}/")
                else:
                    self.ensure_target_dir(target.parent)
                    shutil.move(str(source), str(target))
                    print_success(f"Moved directory: {source.name}/ → {target.parent.name}/")
                
                self.stats['files_moved'] += 1
                
        except Exception as e:
            print_error(f"Error moving directory {source.name}: {e}")
            self.stats['errors'] += 1
    
    def remove_empty_dir(self, dir_path: Path):
        """Remove empty directory"""
        try:
            if not dir_path.exists():
                return
            
            if any(dir_path.iterdir()):
                print_warning(f"Directory not empty, skipping: {dir_path.relative_to(self.projects_root)}")
                return
            
            if self.dry_run:
                print_info(f"Would remove empty directory: {dir_path.relative_to(self.projects_root)}")
            else:
                dir_path.rmdir()
                print_success(f"Removed empty directory: {dir_path.relative_to(self.projects_root)}")
            
            self.stats['dirs_removed'] += 1
            
        except Exception as e:
            print_error(f"Error removing directory {dir_path.name}: {e}")
            self.stats['errors'] += 1
    
    def phase1_consolidate_duplicates(self):
        """Phase 1: Consolidate duplicate completed-* and deprecated-* structures"""
        print_header("PHASE 1: Consolidate Duplicate Structures")
        
        # Archive/completed-2025-09/ → COMPLETED-2025-09/
        source = self.archive_dir / "completed-2025-09"
        target = self.projects_root / "COMPLETED-2025-09"
        if source.exists():
            print_info("Consolidating Archive/completed-2025-09/ → COMPLETED-2025-09/")
            for file in source.glob("*.md"):
                self.move_file(file, target / file.name)
        
        # Archive/deprecated-2025-10/ → DEPRECATED/
        source = self.archive_dir / "deprecated-2025-10"
        target = self.projects_root / "DEPRECATED"
        if source.exists():
            print_info("Consolidating Archive/deprecated-2025-10/ → DEPRECATED/")
            for file in source.glob("*.md"):
                self.move_file(file, target / file.name)
        
        # Keep Archive/adrs-2025/ in place (active reference documents)
        print_info("Keeping Archive/adrs-2025/ in place (active ADRs)")
        # ADRs are ongoing architectural decisions, not completed work
    
    def phase2_reorganize_standalone_files(self):
        """Phase 2: Reorganize Archive standalone files"""
        print_header("PHASE 2: Reorganize Archive Standalone Files")
        
        if not self.archive_dir.exists():
            print_warning("Archive directory doesn't exist, skipping Phase 2")
            return
        
        # Define file mappings
        mappings = {
            # To REFERENCE/
            "automation-coding-discipline.md": self.projects_root / "REFERENCE",
            "executive-report-stakeholders-draft-3.md": self.projects_root / "REFERENCE",
            "inneros-gamification-discovery-manifest.md": self.projects_root / "REFERENCE",
            "logging-monitoring-requirements-automation.md": self.projects_root / "REFERENCE",
            
            # To COMPLETED-2025-09/
            "automation-completion-retrofit-manifest.md": self.projects_root / "COMPLETED-2025-09",
            
            # To COMPLETED-2025-10/
            "workflow-demo-deprecation-plan.md": self.projects_root / "COMPLETED-2025-10",
            "workflow-demo-extraction-status.md": self.projects_root / "COMPLETED-2025-10",
            
            # To DEPRECATED/
            "youtube-official-api-integration-manifest-deprecated-2025-10-09.md": self.projects_root / "DEPRECATED",
        }
        
        for filename, target_dir in mappings.items():
            source = self.archive_dir / filename
            if source.exists():
                self.move_file(source, target_dir / filename)
        
        # Move legacy-manifests/ directory
        source = self.archive_dir / "legacy-manifests"
        target = self.projects_root / "DEPRECATED" / "legacy-manifests"
        if source.exists():
            self.move_directory(source, target)
        
        # Move manifests-2025/ directory
        source = self.archive_dir / "manifests-2025"
        target = self.projects_root / "REFERENCE" / "manifests-2025"
        if source.exists():
            self.move_directory(source, target)
    
    def phase3_remove_empty_directories(self):
        """Phase 3: Remove empty directories"""
        print_header("PHASE 3: Remove Empty Directories")
        
        # Remove COMPLETED-2025-07/ if empty
        self.remove_empty_dir(self.projects_root / "COMPLETED-2025-07")
        
        # Remove Archive subdirectories if empty (keep adrs-2025 as active reference)
        for subdir in ["completed-2025-09", "deprecated-2025-10", 
                      "legacy-manifests", "manifests-2025"]:
            self.remove_empty_dir(self.archive_dir / subdir)
        
        # Finally, try to remove Archive/ if empty
        self.remove_empty_dir(self.archive_dir)
    
    def print_summary(self):
        """Print operation summary"""
        print_header("CLEANUP SUMMARY")
        
        mode = "DRY RUN" if self.dry_run else "EXECUTION"
        print(f"Mode: {Colors.BOLD}{mode}{Colors.ENDC}\n")
        
        print(f"Files moved:        {Colors.OKGREEN}{self.stats['files_moved']}{Colors.ENDC}")
        print(f"Directories created: {Colors.OKCYAN}{self.stats['dirs_created']}{Colors.ENDC}")
        print(f"Directories removed: {Colors.WARNING}{self.stats['dirs_removed']}{Colors.ENDC}")
        
        if self.stats['errors'] > 0:
            print(f"Errors encountered:  {Colors.FAIL}{self.stats['errors']}{Colors.ENDC}")
        else:
            print(f"Errors encountered:  {Colors.OKGREEN}0{Colors.ENDC}")
        
        if self.dry_run:
            print(f"\n{Colors.WARNING}{Colors.BOLD}This was a DRY RUN - no changes were made{Colors.ENDC}")
            print(f"{Colors.OKCYAN}Run with --execute flag to perform actual cleanup{Colors.ENDC}")
    
    def run(self):
        """Execute all cleanup phases"""
        print_header("Projects Directory Cleanup Script")
        print_info(f"Projects Root: {self.projects_root}")
        print_info(f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTION'}\n")
        
        if not self.archive_dir.exists():
            print_error("Archive directory not found!")
            return
        
        try:
            self.phase1_consolidate_duplicates()
            self.phase2_reorganize_standalone_files()
            self.phase3_remove_empty_directories()
            self.print_summary()
            
        except Exception as e:
            print_error(f"Unexpected error during cleanup: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    # Determine execution mode
    dry_run = "--execute" not in sys.argv
    
    # Get projects directory
    script_dir = Path(__file__).parent
    projects_root = script_dir
    
    # Validate directory structure
    if not (projects_root / "Archive").exists():
        print_error("Cannot find Archive/ directory!")
        print_info(f"Expected at: {projects_root / 'Archive'}")
        sys.exit(1)
    
    # Run cleanup
    cleanup = ProjectsCleanup(projects_root, dry_run=dry_run)
    cleanup.run()
    
    # Exit code based on errors
    sys.exit(0 if cleanup.stats['errors'] == 0 else 1)


if __name__ == "__main__":
    main()
