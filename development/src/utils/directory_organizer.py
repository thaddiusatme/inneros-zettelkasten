#!/usr/bin/env python3
"""
Directory Organizer - Safety-First Directory Organization System

This module provides backup and rollback functionality for safely reorganizing
Zettelkasten directories while preserving link integrity.

Safety-First Principles:
- No operations without backup  
- All links preserved during moves
- Rollback capability for failed operations
- Comprehensive validation at each step

Usage:
    from utils.directory_organizer import DirectoryOrganizer
    
    # Initialize with vault and backup paths
    organizer = DirectoryOrganizer("/path/to/vault", "/path/to/backups")
    
    # Create timestamped backup
    backup_path = organizer.create_backup()
    
    # Rollback if needed
    organizer.rollback(backup_path)

Example:
    # Safety-first workflow
    organizer = DirectoryOrganizer("./knowledge", "./backups")
    
    try:
        # Always backup before operations
        backup_path = organizer.create_backup()
        print(f"Backup created: {backup_path}")
        
        # Perform risky operations here...
        
    except Exception as e:
        # Rollback on any failure
        organizer.rollback(backup_path)
        raise

Author: InnerOS Zettelkasten Team
Version: 1.0.0 (P0-1 TDD Implementation)
"""

import shutil
import logging
import json
import yaml
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any


class BackupError(Exception):
    """Raised when backup operations fail."""
    pass


@dataclass
class MoveOperation:
    """Represents a planned file move operation."""
    source: Path
    target: Path
    reason: str


@dataclass 
class MovePlan:
    """Represents a complete dry run plan for directory organization."""
    moves: List[MoveOperation]
    conflicts: List[str]
    unknown_types: List[Path]
    malformed_files: List[Path]
    summary: Dict[str, Any]


class DirectoryOrganizer:
    """
    Safety-first directory organization system.
    
    Provides backup, move, and rollback capabilities for Zettelkasten
    directory organization while ensuring link integrity.
    
    Features:
    - Timestamped backups with collision prevention
    - Comprehensive error handling and logging
    - Rollback capabilities for failed operations
    - Validation of all operations
    - Preserves symlinks and hidden files
    """
    
    def __init__(self, vault_root: str, backup_root: str = None):
        """
        Initialize directory organizer.
        
        Args:
            vault_root: Path to the Zettelkasten vault root
            backup_root: Path to backup directory (defaults to vault_root/backups)
            
        Raises:
            BackupError: If vault root doesn't exist or isn't accessible
        """
        self.vault_root = Path(vault_root)
        self.backup_root = Path(backup_root) if backup_root else self.vault_root.parent / "backups"
        
        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.DirectoryOrganizer")
        
        # Validate vault exists
        if not self.vault_root.exists():
            error_msg = f"Vault root does not exist: {self.vault_root}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
            
        if not self.vault_root.is_dir():
            error_msg = f"Vault root is not a directory: {self.vault_root}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
            
        self.logger.info(f"DirectoryOrganizer initialized for vault: {self.vault_root}")
        self.logger.debug(f"Backup directory: {self.backup_root}")
    
    def create_backup(self) -> str:
        """
        Create timestamped backup of entire vault.
        
        Creates a complete copy of the vault with timestamp-based naming
        to ensure uniqueness. Preserves all files, symlinks, and hidden content.
        
        Returns:
            str: Path to created backup directory
            
        Raises:
            BackupError: If backup creation fails
        """
        # Generate timestamp with collision prevention
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"knowledge-{timestamp}"
        backup_path = self.backup_root / backup_name
        
        # Handle potential timestamp collision (rare but possible)
        collision_counter = 0
        while backup_path.exists():
            collision_counter += 1
            backup_name = f"knowledge-{timestamp}-{collision_counter:02d}"
            backup_path = self.backup_root / backup_name
            
        self.logger.info(f"Creating backup: {backup_path}")
        
        try:
            # Ensure backup root exists with proper permissions
            self.backup_root.mkdir(parents=True, exist_ok=True)
            
            # Validate backup root is writable
            if not self.backup_root.is_dir():
                raise BackupError(f"Cannot create backup directory: {self.backup_root}")
            
            # Count files for progress logging
            file_count = sum(1 for _ in self.vault_root.rglob("*") if _.is_file())
            self.logger.info(f"Backing up {file_count} files from vault")
            
            # Create backup using shutil.copytree with comprehensive options
            shutil.copytree(
                src=self.vault_root,
                dst=backup_path,
                symlinks=True,  # Preserve symlinks
                ignore_dangling_symlinks=True,  # Skip broken symlinks
                dirs_exist_ok=False  # Fail if backup already exists
            )
            
            # Verify backup integrity
            backup_file_count = sum(1 for _ in backup_path.rglob("*") if _.is_file())
            
            if backup_file_count != file_count:
                self.logger.warning(f"File count mismatch: original={file_count}, backup={backup_file_count}")
            else:
                self.logger.info(f"Backup created successfully: {backup_file_count} files copied")
            
            return str(backup_path)
            
        except PermissionError as e:
            error_msg = f"Permission denied creating backup: {e}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
            
        except OSError as e:
            error_msg = f"Failed to create backup: {e}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
            
        except Exception as e:
            error_msg = f"Unexpected error during backup: {e}"
            self.logger.error(error_msg)
            # Cleanup partial backup on failure
            if backup_path.exists():
                try:
                    shutil.rmtree(backup_path)
                    self.logger.info("Cleaned up partial backup after failure")
                except Exception as cleanup_error:
                    self.logger.warning(f"Failed to cleanup partial backup: {cleanup_error}")
            raise BackupError(error_msg)
    
    def rollback(self, backup_path: str) -> None:
        """
        Rollback vault to previous backup state.
        
        Completely replaces the current vault with the contents of the specified
        backup. This is a destructive operation - use with caution!
        
        Args:
            backup_path: Path to backup directory to restore from
            
        Raises:
            BackupError: If rollback fails
        """
        backup_path_obj = Path(backup_path)
        
        # Comprehensive validation of backup
        if not backup_path_obj.exists():
            error_msg = f"Backup path does not exist: {backup_path}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
            
        if not backup_path_obj.is_dir():
            error_msg = f"Backup path is not a directory: {backup_path}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
            
        # Validate backup contents look reasonable
        backup_file_count = sum(1 for _ in backup_path_obj.rglob("*") if _.is_file())
        if backup_file_count == 0:
            error_msg = f"Backup appears empty (no files found): {backup_path}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
            
        self.logger.info(f"Rolling back vault to backup: {backup_path}")
        self.logger.info(f"Backup contains {backup_file_count} files")
        
        # Create emergency backup of current state before rollback
        emergency_backup = None
        try:
            if self.vault_root.exists():
                current_file_count = sum(1 for _ in self.vault_root.rglob("*") if _.is_file())
                self.logger.info(f"Creating emergency backup of current state ({current_file_count} files)")
                
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                emergency_backup_name = f"emergency-before-rollback-{timestamp}"
                emergency_backup = self.backup_root / emergency_backup_name
                
                shutil.copytree(
                    src=self.vault_root,
                    dst=emergency_backup,
                    symlinks=True,
                    ignore_dangling_symlinks=True
                )
                self.logger.info(f"Emergency backup created: {emergency_backup}")
        
        except Exception as e:
            self.logger.warning(f"Failed to create emergency backup: {e}")
            # Continue with rollback despite emergency backup failure
        
        try:
            # Remove current vault if it exists
            if self.vault_root.exists():
                self.logger.info("Removing current vault contents")
                shutil.rmtree(self.vault_root)
            
            # Restore from backup
            self.logger.info("Restoring from backup")
            shutil.copytree(
                src=backup_path_obj,
                dst=self.vault_root,
                symlinks=True,
                ignore_dangling_symlinks=True
            )
            
            # Verify rollback integrity
            restored_file_count = sum(1 for _ in self.vault_root.rglob("*") if _.is_file())
            
            if restored_file_count != backup_file_count:
                self.logger.warning(f"File count mismatch after rollback: backup={backup_file_count}, restored={restored_file_count}")
            else:
                self.logger.info(f"Rollback completed successfully: {restored_file_count} files restored")
            
            # Clean up emergency backup on successful rollback
            if emergency_backup and emergency_backup.exists():
                try:
                    shutil.rmtree(emergency_backup)
                    self.logger.info("Cleaned up emergency backup after successful rollback")
                except Exception as cleanup_error:
                    self.logger.warning(f"Failed to cleanup emergency backup: {cleanup_error}")
            
        except Exception as e:
            error_msg = f"Failed to rollback vault: {e}"
            self.logger.error(error_msg)
            
            # If emergency backup exists, mention it
            if emergency_backup and emergency_backup.exists():
                self.logger.error(f"Emergency backup available at: {emergency_backup}")
            
            raise BackupError(error_msg)
    
    def plan_moves(self) -> MovePlan:
        """
        Plan directory organization moves without executing them.
        
        Analyzes vault structure and identifies files that need to be moved
        based on their type field in YAML frontmatter. Returns a complete
        plan without making any file system changes.
        
        This method provides the critical dry-run functionality that ensures
        safe directory organization by allowing preview of all planned changes
        before execution.
        
        Returns:
            MovePlan: Complete plan with moves, issues, and summary
            
        Raises:
            BackupError: If vault analysis fails
        """
        self.logger.info("Starting dry run analysis of vault structure")
        
        moves = []
        unknown_types = []
        malformed_files = []
        conflicts = []
        
        # Type to directory mapping
        type_to_dir = {
            'permanent': 'Permanent Notes',
            'literature': 'Literature Notes',
            'fleeting': 'Fleeting Notes'
        }
        
        # Scan all markdown files with comprehensive error handling
        total_files = 0
        processed_files = 0
        
        try:
            # Get list of all markdown files first for progress tracking
            md_files = list(self.vault_root.rglob("*.md"))
            total_files = len(md_files)
            self.logger.info(f"Analyzing {total_files} markdown files in vault")
            
            for md_file in md_files:
                processed_files += 1
                current_dir = md_file.parent.name
                
                try:
                    # Parse YAML frontmatter with enhanced error handling
                    try:
                        content = md_file.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        self.logger.warning(f"Unable to decode file as UTF-8: {md_file}")
                        malformed_files.append(md_file)
                        continue
                    
                    if not content.strip():
                        self.logger.debug(f"Skipping empty file: {md_file}")
                        continue
                        
                    if not content.startswith('---'):
                        self.logger.debug(f"No YAML frontmatter: {md_file}")
                        continue  # No frontmatter
                    
                    # Extract YAML section with better error handling
                    try:
                        yaml_end = content.index('\n---\n', 4)
                        yaml_content = content[4:yaml_end]
                        
                        if not yaml_content.strip():
                            self.logger.debug(f"Empty YAML frontmatter: {md_file}")
                            continue
                            
                        metadata = yaml.safe_load(yaml_content)
                        
                    except ValueError as e:
                        self.logger.debug(f"YAML format error in {md_file}: {e}")
                        malformed_files.append(md_file)
                        continue
                    except yaml.YAMLError as e:
                        self.logger.debug(f"YAML parsing error in {md_file}: {e}")
                        malformed_files.append(md_file)
                        continue
                    
                    # Validate metadata structure
                    if not isinstance(metadata, dict):
                        self.logger.debug(f"YAML not a dictionary in {md_file}")
                        malformed_files.append(md_file)
                        continue
                        
                    if 'type' not in metadata:
                        self.logger.debug(f"No 'type' field in {md_file}")
                        continue  # No type field
                        
                    file_type = metadata['type']
                    
                    # Validate type field value
                    if not isinstance(file_type, str) or not file_type.strip():
                        self.logger.debug(f"Invalid type value in {md_file}: {file_type}")
                        malformed_files.append(md_file)
                        continue
                    
                    file_type = file_type.strip().lower()
                    
                    # Check if type is known
                    if file_type not in type_to_dir:
                        self.logger.debug(f"Unknown type '{file_type}' in {md_file}")
                        unknown_types.append(md_file)
                        continue
                    
                    # Check if file is already in correct directory
                    target_dir = type_to_dir[file_type]
                    if current_dir == target_dir:
                        self.logger.debug(f"File already in correct location: {md_file}")
                        continue  # Already in correct location
                    
                    # Check for potential target conflicts
                    target_path = self.vault_root / target_dir / md_file.name
                    if target_path.exists():
                        conflict_msg = f"Target already exists: {target_path}"
                        self.logger.warning(conflict_msg)
                        conflicts.append(conflict_msg)
                        continue
                    
                    # Plan the move
                    move_op = MoveOperation(
                        source=md_file,
                        target=target_path,
                        reason=f"type: {file_type}"
                    )
                    moves.append(move_op)
                    self.logger.debug(f"Planned move: {md_file.name} → {target_dir}")
                    
                except PermissionError as e:
                    self.logger.warning(f"Permission denied accessing {md_file}: {e}")
                    malformed_files.append(md_file)
                except Exception as e:
                    self.logger.warning(f"Unexpected error processing {md_file}: {e}")
                    malformed_files.append(md_file)
                    
        except Exception as e:
            error_msg = f"Critical error during vault analysis: {e}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)
        
        # Generate comprehensive summary with enhanced metadata
        files_processed = processed_files
        files_with_frontmatter = len(moves) + len(unknown_types) + len(malformed_files)
        files_correctly_placed = total_files - files_with_frontmatter
        
        summary = {
            'total_moves': len(moves),
            'unknown_types': len(unknown_types),
            'malformed_files': len(malformed_files),
            'conflicts': len(conflicts),
            'total_files_analyzed': total_files,
            'files_processed': files_processed,
            'files_with_frontmatter': files_with_frontmatter,
            'files_correctly_placed': files_correctly_placed,
            'analysis_complete': True
        }
        
        plan = MovePlan(
            moves=moves,
            conflicts=conflicts,
            unknown_types=unknown_types,
            malformed_files=malformed_files,
            summary=summary
        )
        
        # Enhanced completion logging
        self.logger.info("Dry run analysis complete:")
        self.logger.info(f"  - {total_files} total files analyzed")
        self.logger.info(f"  - {len(moves)} moves planned")
        self.logger.info(f"  - {len(unknown_types)} files with unknown types")
        self.logger.info(f"  - {len(malformed_files)} files with malformed YAML")
        self.logger.info(f"  - {len(conflicts)} potential conflicts detected")
        self.logger.info(f"  - {files_correctly_placed} files already correctly placed")
        
        if len(conflicts) > 0:
            self.logger.warning("Conflicts detected! Manual review required before execution.")
        
        return plan
    
    def generate_move_report(self, move_plan: MovePlan, format: str = 'markdown') -> str:
        """
        Generate a report of the planned moves.
        
        Args:
            move_plan: The move plan to generate report for
            format: Output format ('json' or 'markdown')
            
        Returns:
            str: Formatted report
        """
        if format == 'json':
            return self._generate_json_report(move_plan)
        elif format == 'markdown':
            return self._generate_markdown_report(move_plan)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _generate_json_report(self, move_plan: MovePlan) -> str:
        """Generate JSON format report."""
        report_data = {
            'summary': move_plan.summary,
            'moves': [
                {
                    'source': str(move.source),
                    'target': str(move.target),
                    'reason': move.reason
                }
                for move in move_plan.moves
            ],
            'issues': {
                'unknown_types': [str(f) for f in move_plan.unknown_types],
                'malformed_files': [str(f) for f in move_plan.malformed_files],
                'conflicts': move_plan.conflicts
            }
        }
        return json.dumps(report_data, indent=2)
    
    def _generate_markdown_report(self, move_plan: MovePlan) -> str:
        """Generate comprehensive Markdown format report."""
        from datetime import datetime
        
        lines = [
            '# Directory Organization Plan',
            '',
            f'**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f'**Vault**: {self.vault_root}',
            '',
            '## Summary',
            f'- **Total files analyzed**: {move_plan.summary.get("total_files_analyzed", "N/A")}',
            f'- **Files with frontmatter**: {move_plan.summary.get("files_with_frontmatter", "N/A")}',
            f'- **Files correctly placed**: {move_plan.summary.get("files_correctly_placed", "N/A")}',
            f'- **Total moves planned**: {move_plan.summary["total_moves"]}',
            f'- **Unknown types**: {move_plan.summary["unknown_types"]}',
            f'- **Malformed files**: {move_plan.summary["malformed_files"]}',
            f'- **Conflicts detected**: {move_plan.summary["conflicts"]}',
            '',
            '## Planned Moves',
            ''
        ]
        
        if move_plan.moves:
            lines.extend([
                '| Current Path | Target Path | Reason |',
                '|--------------|-------------|--------|'
            ])
            
            for move in move_plan.moves:
                source_rel = move.source.relative_to(self.vault_root)
                target_rel = move.target.relative_to(self.vault_root)
                lines.append(f'| {source_rel} | {target_rel} | {move.reason} |')
        else:
            lines.append('*No moves needed - all files are properly organized!*')
        
        if move_plan.unknown_types:
            lines.extend(['', '## Unknown Types', ''])
            for file_path in move_plan.unknown_types:
                rel_path = file_path.relative_to(self.vault_root)
                lines.append(f'- {rel_path}')
        
        if move_plan.malformed_files:
            lines.extend(['', '## Malformed Files', ''])
            for file_path in move_plan.malformed_files:
                rel_path = file_path.relative_to(self.vault_root)
                lines.append(f'- {rel_path}')
        
        if move_plan.conflicts:
            lines.extend(['', '## Conflicts ⚠️', ''])
            lines.append('**These conflicts must be resolved before executing moves:**')
            lines.append('')
            for conflict in move_plan.conflicts:
                lines.append(f'- {conflict}')
        
        # Add safety notice
        if move_plan.moves or move_plan.conflicts:
            lines.extend([
                '',
                '---',
                '',
                '**⚠️ SAFETY NOTICE**: This is a dry run report. No files have been moved.',
                'Always create a backup before executing any file moves!',
                ''
            ])
        
        return '\n'.join(lines)
