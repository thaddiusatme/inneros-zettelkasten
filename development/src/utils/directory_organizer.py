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
from pathlib import Path
from datetime import datetime


class BackupError(Exception):
    """Raised when backup operations fail."""
    pass


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
    
    def execute_moves(self, create_backup: bool = True, validate_first: bool = True, rollback_on_error: bool = True, progress_callback=None) -> dict:
        """
        Execute planned directory organization moves safely.
        
        This method performs the actual file moves identified by the dry run system.
        It builds on the P0-1 backup system and P0-2 dry run analysis for safety.
        
        Safety Features:
        - Automatic backup creation before operations
        - Validation of dry run plan before execution
        - Rollback on partial failures
        - Progress reporting and comprehensive logging
        - Conflict detection and prevention
        
        Args:
            create_backup: Whether to create backup before operations (default: True)
            validate_first: Whether to validate dry run before execution (default: True) 
            rollback_on_error: Whether to rollback on partial failures (default: True)
            progress_callback: Optional callback for progress reporting (callable)
            
        Returns:
            dict: Execution results with detailed statistics:
                - moves_executed: Number of successful moves
                - files_processed: Total files processed
                - backup_created: Whether backup was created
                - backup_path: Path to backup (if created)
                - execution_time_seconds: Total execution time
                - status: 'success', 'success_no_moves_needed', or error details
                - validation_results: Summary of pre-execution validation
            
        Raises:
            BackupError: If backup creation, validation, or file operations fail
        """
        self.logger.info("Starting file move execution")
        
        # Step 1: Validate dry run first (if requested)
        if validate_first:
            # Import here to avoid circular dependencies when P0-2 methods added
            try:
                move_plan = self.plan_moves()
            except AttributeError:
                # P0-2 methods not available yet - use minimal planning
                move_plan = self._create_minimal_move_plan()
            
            if move_plan.conflicts:
                error_msg = f"Cannot execute moves: {len(move_plan.conflicts)} conflicts detected"
                self.logger.error(error_msg)
                raise BackupError(error_msg)
            
            if not move_plan.moves:
                self.logger.info("No moves needed - all files are properly organized")
                return {
                    "moves_executed": 0,
                    "files_processed": 0,
                    "backup_created": False,
                    "execution_time_seconds": 0,
                    "status": "success_no_moves_needed",
                    "validation_results": {
                        "total_moves_planned": 0,
                        "conflicts_detected": len(getattr(move_plan, 'conflicts', [])),
                        "unknown_types": len(getattr(move_plan, 'unknown_types', [])),
                        "malformed_files": len(getattr(move_plan, 'malformed_files', []))
                    }
                }
        
        # Step 2: Create backup before operations (if requested)  
        backup_path = None
        if create_backup:
            self.logger.info("Creating backup before file moves")
            backup_path = self.create_backup()
        
        # Step 3: Execute moves safely
        execution_start = datetime.now()
        moves_executed = 0
        files_processed = 0
        
        try:
            # Use move plan if available, otherwise create minimal plan
            if validate_first:
                moves_to_execute = move_plan.moves
            else:
                try:
                    move_plan = self.plan_moves()
                    moves_to_execute = move_plan.moves
                except AttributeError:
                    move_plan = self._create_minimal_move_plan()
                    moves_to_execute = move_plan.moves
            
            self.logger.info(f"Executing {len(moves_to_execute)} file moves")
            
            # Progress tracking setup
            total_moves = len(moves_to_execute)
            
            for i, move in enumerate(moves_to_execute, 1):
                # Ensure target directory exists
                move.target.parent.mkdir(parents=True, exist_ok=True)
                
                # Verify source still exists (race condition protection)
                if not move.source.exists():
                    self.logger.warning(f"Source file no longer exists: {move.source}")
                    continue
                
                # Verify target doesn't exist (conflict protection)
                if move.target.exists():
                    error_msg = f"Target already exists: {move.target}"
                    self.logger.error(error_msg)
                    raise BackupError(error_msg)
                
                # Perform the move with enhanced logging
                self.logger.info(f"Move {i}/{total_moves}: {move.source.name} → {move.target.parent.name}/")
                self.logger.debug(f"Full path: {move.source} → {move.target}")
                
                try:
                    shutil.move(str(move.source), str(move.target))
                    self.logger.debug(f"Successfully moved: {move.source.name}")
                except Exception as move_error:
                    error_msg = f"Failed to move {move.source} to {move.target}: {move_error}"
                    self.logger.error(error_msg)
                    raise BackupError(error_msg)
                
                moves_executed += 1
                files_processed += 1
                
                # Progress callback
                if progress_callback:
                    try:
                        progress_callback(i, total_moves, move.source.name)
                    except Exception as callback_error:
                        self.logger.warning(f"Progress callback failed: {callback_error}")
            
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            self.logger.info(f"Successfully executed {moves_executed} moves in {execution_time:.2f} seconds")
            
            # Enhanced result reporting
            result = {
                "moves_executed": moves_executed,
                "files_processed": files_processed,
                "backup_created": backup_path is not None,
                "backup_path": backup_path,
                "execution_time_seconds": execution_time,
                "status": "success",
                "validation_results": {
                    "total_moves_planned": len(moves_to_execute),
                    "conflicts_detected": len(getattr(move_plan, 'conflicts', [])),
                    "unknown_types": len(getattr(move_plan, 'unknown_types', [])),
                    "malformed_files": len(getattr(move_plan, 'malformed_files', []))
                }
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error during file move execution: {e}")
            
            # Rollback on error if requested and backup exists
            if rollback_on_error and backup_path:
                self.logger.info("Rolling back due to execution error")
                try:
                    self.rollback(backup_path)
                    self.logger.info("Rollback completed successfully")
                except Exception as rollback_error:
                    self.logger.error(f"Rollback failed: {rollback_error}")
            
            raise BackupError(f"File move execution failed: {e}")
    
    def _create_minimal_move_plan(self):
        """
        Create minimal move plan for P1-1 GREEN phase.
        
        This is a simplified version for when P0-2 methods aren't available yet.
        It finds basic type mismatches and creates minimal move operations.
        """
        # Import dataclasses inline
        from dataclasses import dataclass
        from typing import List, Dict, Any
        
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
        
        moves = []
        conflicts = []
        unknown_types = []
        malformed_files = []
        
        # Type to directory mapping
        type_to_dir = {
            'permanent': 'Permanent Notes',
            'literature': 'Literature Notes',
            'fleeting': 'Fleeting Notes'
        }
        
        # Scan Inbox for misplaced files
        inbox_path = self.vault_root / "Inbox"
        if inbox_path.exists():
            for md_file in inbox_path.glob("*.md"):
                try:
                    content = md_file.read_text(encoding='utf-8')
                    
                    # Extract frontmatter type (simple parsing)
                    if content.startswith("---"):
                        frontmatter_end = content.find("---", 3)
                        if frontmatter_end > 0:
                            frontmatter = content[3:frontmatter_end]
                            for line in frontmatter.split('\n'):
                                if line.startswith('type:'):
                                    file_type = line.split(':', 1)[1].strip().lower()
                                    
                                    if file_type in type_to_dir:
                                        target_dir = self.vault_root / type_to_dir[file_type]
                                        target_path = target_dir / md_file.name
                                        
                                        # Check for conflicts
                                        if target_path.exists():
                                            conflicts.append(f"Target already exists: {target_path}")
                                        else:
                                            moves.append(MoveOperation(
                                                source=md_file,
                                                target=target_path,
                                                reason=f"Type '{file_type}' belongs in {type_to_dir[file_type]}/"
                                            ))
                                    else:
                                        unknown_types.append(md_file)
                                    break
                            
                except Exception:
                    malformed_files.append(md_file)
        
        return MovePlan(
            moves=moves,
            conflicts=conflicts,
            unknown_types=unknown_types,
            malformed_files=malformed_files,
            summary={
                "total_moves": len(moves),
                "conflicts": len(conflicts),
                "unknown_types": len(unknown_types),
                "malformed_files": len(malformed_files)
            }
        )
