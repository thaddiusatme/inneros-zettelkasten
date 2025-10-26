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
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set, Tuple, Optional

# Image linking system integration
try:
    from .image_link_manager import ImageLinkManager
    IMAGE_LINK_SUPPORT = True
except ImportError:
    IMAGE_LINK_SUPPORT = False


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
class WikiLink:
    """Represents a wiki-style link found in markdown content."""
    original_text: str  # Full link text: [[Note Name|Display Text]]
    target_note: str    # The note being referenced: "Note Name"
    display_text: str   # Display text if provided, else same as target_note
    is_embed: bool      # True for ![[embeds]], False for [[links]]
    line_number: int    # Line number where link was found
    start_pos: int      # Character position on the line
    end_pos: int        # End character position


@dataclass
class LinkUpdate:
    """Represents a planned link update operation."""
    file_path: Path
    old_link: WikiLink
    new_target: str     # New target note name after move
    new_link_text: str  # Complete new link text


@dataclass
class LinkIndex:
    """Complete index of all wiki-links in the vault."""
    links_by_file: Dict[Path, List[WikiLink]] = field(default_factory=dict)
    links_to_file: Dict[str, Set[Path]] = field(default_factory=dict)
    broken_links: Set[Tuple[Path, str]] = field(default_factory=set)


@dataclass
class MovePlan:
    """Represents a complete dry run plan for directory organization."""
    moves: List[MoveOperation]
    conflicts: List[str]
    unknown_types: List[Path]
    malformed_files: List[Path]
    summary: Dict[str, Any]
    link_updates: List[LinkUpdate] = field(default_factory=list)  # P0-3 extension


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

    def __init__(self, vault_root: str, backup_root: str = None, exclude_patterns: list = None):
        """
        Initialize directory organizer with path containment guardrails and exclude rules.
        
        Args:
            vault_root: Path to the Zettelkasten vault root
            backup_root: Path to backup directory (defaults to ~/backups/{vault_name})
            exclude_patterns: List of directory/file patterns to exclude from backups
                            (defaults to ['backups', '.git', '*_env', '*.venv'])
            
        Raises:
            BackupError: If vault root doesn't exist, isn't accessible, or backup_root
                        is inside vault_root (prevents recursive backup nesting)
        """
        self.vault_root = Path(vault_root).resolve()  # Resolve for accurate path comparison

        # Set default backup root to external location (~/backups/{vault_name})
        if backup_root:
            self.backup_root = Path(backup_root).resolve()
        else:
            # Default: ~/backups/{vault_name}/ - external to any vault
            vault_name = self.vault_root.name or "vault"
            self.backup_root = Path.home() / "backups" / vault_name

        # Set default exclude patterns for heavy/derived directories
        if exclude_patterns is not None:
            self.exclude_patterns = exclude_patterns
        else:
            self.exclude_patterns = [
                'backups',         # Recursive backup prevention
                '.git',           # Version control data
                '*_env',          # Python virtual environments (web_ui_env, venv, etc.)
                '*.venv',         # Alternative venv naming
                '__pycache__',    # Python cache
                'node_modules',   # JavaScript dependencies
                '.pytest_cache',  # Test cache
                '.embedding_cache' # AI embedding cache
            ]

        # Setup logging
        self.logger = logging.getLogger(f"{__name__}.DirectoryOrganizer")

        # Image linking system integration (TDD Iteration 10)
        self.image_manager: Optional['ImageLinkManager'] = None
        if IMAGE_LINK_SUPPORT:
            try:
                self.image_manager = ImageLinkManager(base_path=self.vault_root)
                self.logger.info("Image link preservation enabled")
            except Exception as e:
                self.logger.warning(f"Could not initialize image link manager: {e}")

        # P0 Guardrail: Prevent recursive backup nesting
        self._validate_backup_path_not_nested()

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

    def _validate_backup_path_not_nested(self) -> None:
        """
        Validate that backup_root is not inside vault_root.
        
        This critical guardrail prevents recursive backup nesting which causes
        exponential storage growth and system instability.
        
        Raises:
            BackupError: If backup_root is inside vault_root (nested paths)
        """
        try:
            # Check if backup_root is inside vault_root using path resolution
            vault_resolved = self.vault_root.resolve()
            backup_resolved = self.backup_root.resolve()

            # Try to create relative path from vault to backup
            # If successful and doesn't start with '..', backup is inside vault
            try:
                relative_path = backup_resolved.relative_to(vault_resolved)
                # If we get here without exception, backup is inside vault
                error_msg = (
                    f"CRITICAL: Backup target is inside source vault, which would cause "
                    f"recursive backup nesting and exponential storage growth.\n"
                    f"Vault: {vault_resolved}\n"
                    f"Backup: {backup_resolved}\n"
                    f"Relative path: {relative_path}\n\n"
                    f"SOLUTION: Use external backup location such as:\n"
                    f"  ~/backups/{vault_resolved.name}/\n"
                    f"  {vault_resolved.parent}/backups/\n"
                    f"  /external/storage/backups/"
                )
                self.logger.error(error_msg)
                raise BackupError(error_msg)

            except ValueError:
                # relative_to() raises ValueError when paths don't have common base
                # This means backup is external to vault (good!)
                pass

        except Exception as e:
            if isinstance(e, BackupError):
                raise  # Re-raise our specific backup errors

            # For other errors, log and raise as backup error
            error_msg = f"Failed to validate backup path safety: {e}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)

    def _create_ignore_function(self):
        """
        Create ignore function for shutil.copytree based on exclude patterns.
        
        Returns:
            Callable: Function that takes (dir, files) and returns files to ignore
        """
        import fnmatch

        def ignore_function(dir_path, filenames):
            """Ignore function for shutil.copytree."""
            ignored = []

            try:
                base_relative_path = Path(dir_path).relative_to(self.vault_root)
            except ValueError:
                # dir_path is outside vault_root, shouldn't happen but handle gracefully
                self.logger.warning(f"Directory outside vault during backup: {dir_path}")
                return []

            for filename in filenames:
                # Check each exclude pattern
                for pattern in self.exclude_patterns:
                    # Check against just the filename
                    if fnmatch.fnmatch(filename, pattern):
                        ignored.append(filename)
                        break

                    # Check against the relative path from vault root
                    relative_path = base_relative_path / filename
                    if fnmatch.fnmatch(str(relative_path), pattern):
                        ignored.append(filename)
                        break

                    # Check against relative path with wildcard support
                    if fnmatch.fnmatch(str(relative_path), f"*/{pattern}"):
                        ignored.append(filename)
                        break

            if ignored:
                self.logger.debug(f"Excluding from backup in {base_relative_path}: {ignored}")

            return ignored

        return ignore_function

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

            # Count files for progress logging (before exclusions)
            file_count = sum(1 for _ in self.vault_root.rglob("*") if _.is_file())
            self.logger.info(f"Backing up {file_count} files from vault (before exclusions)")
            self.logger.info(f"Exclude patterns: {self.exclude_patterns}")

            # Create backup using shutil.copytree with exclude patterns
            ignore_func = self._create_ignore_function()
            shutil.copytree(
                src=self.vault_root,
                dst=backup_path,
                symlinks=True,  # Preserve symlinks
                ignore_dangling_symlinks=True,  # Skip broken symlinks
                ignore=ignore_func,  # Apply exclude patterns
                dirs_exist_ok=False  # Fail if backup already exists
            )

            # Verify backup integrity (count files in backup)
            backup_file_count = sum(1 for _ in backup_path.rglob("*") if _.is_file())
            excluded_count = file_count - backup_file_count

            self.logger.info(f"Backup created successfully: {backup_file_count} files copied ({excluded_count} excluded)")

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
            # Use comprehensive P0-2 dry run analysis
            move_plan = self.plan_moves()

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
                move_plan = self.plan_moves()
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

                # TDD Iteration 10: Preserve image links before move
                if self.image_manager and move.source.suffix == '.md':
                    try:
                        content = move.source.read_text(encoding='utf-8')
                        updated_content = self.image_manager.update_image_links_for_move(
                            content, move.source, move.target
                        )
                        move.source.write_text(updated_content, encoding='utf-8')
                        self.logger.debug(f"Updated image links for: {move.source.name}")
                    except Exception as img_error:
                        self.logger.warning(f"Could not update image links in {move.source}: {img_error}")
                        # Continue with move even if image link update fails

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

    def plan_moves(self) -> MovePlan:
        """
        Plan directory organization moves without executing them.
        
        Analyzes all markdown files in the vault and creates a comprehensive
        plan for organizing files based on their type field. Uses robust YAML
        parsing and provides detailed conflict detection and reporting.
        
        P0-2 Features:
        - Comprehensive YAML frontmatter parsing with error handling
        - Type-based move planning (permanent/literature/fleeting → correct directories)
        - Conflict detection prevents file overwrites
        - Enhanced metadata with analysis statistics
        - Dual report generation capability (JSON/Markdown)
        
        Returns:
            MovePlan: Complete analysis with moves, conflicts, and statistics
            
        Raises:
            BackupError: If vault analysis fails
        """
        self.logger.info("Starting comprehensive dry run analysis")

        moves = []
        conflicts = []
        unknown_types = []
        malformed_files = []

        # Enhanced type to directory mapping
        type_to_dir = {
            'permanent': 'Permanent Notes',
            'literature': 'Literature Notes',
            'fleeting': 'Fleeting Notes'
        }

        # Statistics tracking
        total_files = 0
        files_with_frontmatter = 0
        correctly_placed_files = 0

        try:
            # Scan all directories for markdown files
            directories_to_scan = [
                self.vault_root / "Inbox",
                self.vault_root / "Permanent Notes",
                self.vault_root / "Literature Notes",
                self.vault_root / "Fleeting Notes"
            ]

            for directory in directories_to_scan:
                if not directory.exists():
                    self.logger.info(f"Directory does not exist, will be created: {directory}")
                    continue

                self.logger.debug(f"Scanning directory: {directory}")

                for md_file in directory.glob("*.md"):
                    total_files += 1

                    try:
                        content = md_file.read_text(encoding='utf-8')
                    except UnicodeDecodeError:
                        self.logger.warning(f"Unable to decode file as UTF-8: {md_file}")
                        malformed_files.append(md_file)
                        continue
                    except PermissionError:
                        self.logger.warning(f"Permission denied reading file: {md_file}")
                        malformed_files.append(md_file)
                        continue

                    # Parse YAML frontmatter with comprehensive error handling
                    frontmatter_data = self._parse_frontmatter(content, md_file)

                    if frontmatter_data is None:
                        # No frontmatter or parsing failed
                        continue

                    files_with_frontmatter += 1

                    # Extract and validate type field
                    file_type = frontmatter_data.get('type', '').strip().lower()

                    if not isinstance(file_type, str) or not file_type:
                        self.logger.debug(f"Invalid type value in {md_file}: {file_type}")
                        malformed_files.append(md_file)
                        continue

                    # Check if file needs to be moved
                    current_dir = md_file.parent.name
                    expected_dir = type_to_dir.get(file_type)

                    if file_type not in type_to_dir:
                        unknown_types.append(md_file)
                        continue

                    if current_dir == expected_dir:
                        correctly_placed_files += 1
                        continue

                    # File needs to be moved
                    target_dir = self.vault_root / expected_dir
                    target_path = target_dir / md_file.name

                    # Check for conflicts
                    if target_path.exists():
                        conflict_msg = f"Target already exists: {target_path}"
                        self.logger.warning(conflict_msg)
                        conflicts.append(conflict_msg)
                        continue

                    # Create move operation
                    move_reason = f"Type '{file_type}' belongs in {expected_dir}/"
                    moves.append(MoveOperation(
                        source=md_file,
                        target=target_path,
                        reason=move_reason
                    ))

                    self.logger.debug(f"Planned move: {md_file.name} → {expected_dir}/")

            # Generate comprehensive summary
            summary = {
                "total_files": total_files,
                "files_with_frontmatter": files_with_frontmatter,
                "correctly_placed_files": correctly_placed_files,
                "total_moves": len(moves),
                "conflicts": len(conflicts),
                "unknown_types": len(unknown_types),
                "malformed_files": len(malformed_files),
                "vault_root": str(self.vault_root),
                "analysis_timestamp": datetime.now().isoformat()
            }

            # P0-3: Add link preservation analysis
            link_updates = []
            if moves:  # Only scan links if there are moves to process
                self.logger.info("Analyzing wiki-link preservation requirements")
                try:
                    link_index = self.scan_wiki_links()

                    # Create temporary move plan for link analysis
                    temp_move_plan = MovePlan(
                        moves=moves,
                        conflicts=conflicts,
                        unknown_types=unknown_types,
                        malformed_files=malformed_files,
                        summary=summary
                    )

                    link_updates = self.plan_link_updates(temp_move_plan, link_index)

                    # Update summary with link information
                    summary.update({
                        "total_links_scanned": sum(len(links) for links in link_index.links_by_file.values()),
                        "broken_links_detected": len(link_index.broken_links),
                        "link_updates_planned": len(link_updates)
                    })

                except Exception as link_error:
                    self.logger.warning(f"Link analysis failed: {link_error}")
                    # Continue without link updates rather than failing completely

            self.logger.info(f"Dry run analysis complete: {len(moves)} moves planned, {len(conflicts)} conflicts detected, {len(link_updates)} link updates planned")

            return MovePlan(
                moves=moves,
                conflicts=conflicts,
                unknown_types=unknown_types,
                malformed_files=malformed_files,
                summary=summary,
                link_updates=link_updates
            )

        except Exception as e:
            error_msg = f"Failed to analyze vault for directory organization: {e}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)

    def _parse_frontmatter(self, content: str, file_path: Path) -> Dict[str, Any]:
        """
        Parse YAML frontmatter from markdown content with comprehensive error handling.
        
        Args:
            content: Raw markdown file content
            file_path: Path to file (for error logging)
            
        Returns:
            Dict of frontmatter data, or None if parsing fails
        """
        if not content.startswith("---"):
            return None

        # Find end of frontmatter
        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            self.logger.debug(f"No frontmatter end marker found in {file_path}")
            return None

        frontmatter_raw = content[3:frontmatter_end].strip()

        if not frontmatter_raw:
            self.logger.debug(f"Empty frontmatter in {file_path}")
            return None

        try:
            # Parse YAML frontmatter
            frontmatter_data = yaml.safe_load(frontmatter_raw)

            if not isinstance(frontmatter_data, dict):
                self.logger.warning(f"Frontmatter is not a dictionary in {file_path}")
                return None

            return frontmatter_data

        except yaml.YAMLError as e:
            self.logger.warning(f"YAML parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.warning(f"Unexpected error parsing frontmatter in {file_path}: {e}")
            return None

    def generate_dry_run_report(self, move_plan: MovePlan, format: str = "markdown") -> str:
        """
        Generate comprehensive dry run report in specified format.
        
        Args:
            move_plan: MovePlan object from plan_moves()
            format: Output format ('markdown' or 'json')
            
        Returns:
            Formatted report string
        """
        if format.lower() == "json":
            return self._generate_json_report(move_plan)
        else:
            return self._generate_markdown_report(move_plan)

    def _generate_json_report(self, move_plan: MovePlan) -> str:
        """Generate JSON format report."""
        report_data = {
            "summary": move_plan.summary,
            "moves": [
                {
                    "source": str(move.source.relative_to(self.vault_root)),
                    "target": str(move.target.relative_to(self.vault_root)),
                    "reason": move.reason
                } for move in move_plan.moves
            ],
            "conflicts": move_plan.conflicts,
            "unknown_types": [str(path.relative_to(self.vault_root)) for path in move_plan.unknown_types],
            "malformed_files": [str(path.relative_to(self.vault_root)) for path in move_plan.malformed_files]
        }

        return json.dumps(report_data, indent=2, ensure_ascii=False)

    def _generate_markdown_report(self, move_plan: MovePlan) -> str:
        """Generate Markdown format report."""
        lines = [
            '# Directory Organization Dry Run Report',
            '',
            f'**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            f'**Vault**: {move_plan.summary["vault_root"]}',
            '',
            '## Summary',
            '',
            f'- **Total files analyzed**: {move_plan.summary["total_files"]}',
            f'- **Files with frontmatter**: {move_plan.summary["files_with_frontmatter"]}',
            f'- **Correctly placed files**: {move_plan.summary["correctly_placed_files"]}',
            f'- **Moves planned**: {move_plan.summary["total_moves"]}',
            f'- **Conflicts detected**: {move_plan.summary["conflicts"]}',
            f'- **Unknown types**: {move_plan.summary["unknown_types"]}',
            f'- **Malformed files**: {move_plan.summary["malformed_files"]}',
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

    def scan_wiki_links(self) -> LinkIndex:
        """
        Scan entire vault for wiki-style links and create comprehensive index.
        
        P0-3 Features:
        - Comprehensive regex patterns for all wiki-link variants
        - Support for [[Note]], [[Note|Alias]], [[Note#Heading]], ![[Embed]]
        - Line-by-line scanning with position tracking
        - Broken link detection and reporting
        - Bidirectional link mapping (file → links, target → referencing files)
        
        Returns:
            LinkIndex: Complete index of all wiki-links in vault
            
        Raises:
            BackupError: If link scanning fails
        """
        self.logger.info("Starting comprehensive wiki-link scanning")

        # Comprehensive regex patterns for all wiki-link variants
        wiki_link_patterns = [
            # Standard links: [[Note Name]], [[Note Name|Display Text]]
            r'(?P<embed>!?)\[\[(?P<target>[^\]|#]+?)(?:#(?P<heading>[^\]|]*?))?(?:\|(?P<display>[^\]]*?))?\]\]',
        ]

        link_index = LinkIndex()

        try:
            # Get all markdown files in vault
            all_md_files = list(self.vault_root.rglob("*.md"))
            self.logger.info(f"Scanning {len(all_md_files)} files for wiki-links")

            for md_file in all_md_files:
                try:
                    content = md_file.read_text(encoding='utf-8')
                    file_links = self._extract_wiki_links(content, md_file, wiki_link_patterns)

                    if file_links:
                        link_index.links_by_file[md_file] = file_links

                        # Build reverse index (target → referencing files)
                        for link in file_links:
                            target_key = self._normalize_link_target(link.target_note)

                            if target_key not in link_index.links_to_file:
                                link_index.links_to_file[target_key] = set()
                            link_index.links_to_file[target_key].add(md_file)

                            # Check if target exists
                            if not self._find_target_file(link.target_note):
                                link_index.broken_links.add((md_file, link.target_note))

                except Exception as e:
                    self.logger.warning(f"Failed to scan links in {md_file}: {e}")

            # Log statistics
            total_links = sum(len(links) for links in link_index.links_by_file.values())
            self.logger.info(f"Link scanning complete: {total_links} links found, {len(link_index.broken_links)} broken links detected")

            return link_index

        except Exception as e:
            error_msg = f"Failed to scan wiki-links: {e}"
            self.logger.error(error_msg)
            raise BackupError(error_msg)

    def _extract_wiki_links(self, content: str, file_path: Path, patterns: List[str]) -> List[WikiLink]:
        """Extract wiki-links from file content using regex patterns."""
        links = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern in patterns:
                for match in re.finditer(pattern, line):
                    embed_marker = match.group('embed')
                    target_note = match.group('target').strip()
                    heading = match.group('heading') if 'heading' in match.groupdict() and match.group('heading') else ""
                    display_text = match.group('display') if 'display' in match.groupdict() and match.group('display') else target_note

                    # Include heading in target if present
                    full_target = f"{target_note}#{heading}" if heading else target_note

                    wiki_link = WikiLink(
                        original_text=match.group(0),
                        target_note=target_note,
                        display_text=display_text.strip(),
                        is_embed=bool(embed_marker),
                        line_number=line_num,
                        start_pos=match.start(),
                        end_pos=match.end()
                    )

                    links.append(wiki_link)
                    self.logger.debug(f"Found link in {file_path.name}:{line_num}: {wiki_link.original_text}")

        return links

    def _normalize_link_target(self, target: str) -> str:
        """Normalize link target for consistent matching."""
        # Remove .md extension if present
        if target.endswith('.md'):
            target = target[:-3]

        # Split on # to handle headings
        target = target.split('#')[0]

        return target.strip().lower()

    def _find_target_file(self, target_note: str) -> Path:
        """Find the actual file that corresponds to a link target."""
        normalized_target = self._normalize_link_target(target_note)

        # Search for files with matching names
        for md_file in self.vault_root.rglob("*.md"):
            file_stem = md_file.stem.lower()

            # Direct name match
            if file_stem == normalized_target:
                return md_file

            # Handle files with prefixes (like fleeting-20250816-note-name)
            if file_stem.endswith(f"-{normalized_target}"):
                return md_file

        return None

    def plan_link_updates(self, move_plan: MovePlan, link_index: LinkIndex) -> List[LinkUpdate]:
        """
        Plan link updates for files that will be moved.
        
        Analyzes which links need to be updated when files are moved to maintain
        link integrity throughout the vault.
        
        Args:
            move_plan: Plan containing files to be moved
            link_index: Current link index of the vault
            
        Returns:
            List of LinkUpdate operations needed to preserve link integrity
        """
        link_updates = []

        # Create mapping of old path → new path for moved files
        move_mapping = {str(move.source): str(move.target) for move in move_plan.moves}

        self.logger.info(f"Planning link updates for {len(move_plan.moves)} file moves")

        for move in move_plan.moves:
            old_name = move.source.stem
            new_name = move.target.stem

            # If filename changes, update all links pointing to this file
            if old_name != new_name:
                normalized_old = self._normalize_link_target(old_name)

                if normalized_old in link_index.links_to_file:
                    referencing_files = link_index.links_to_file[normalized_old]

                    for ref_file in referencing_files:
                        if ref_file in link_index.links_by_file:
                            for link in link_index.links_by_file[ref_file]:
                                if self._normalize_link_target(link.target_note) == normalized_old:
                                    # Plan link update
                                    new_link_text = self._generate_updated_link_text(link, new_name)

                                    link_update = LinkUpdate(
                                        file_path=ref_file,
                                        old_link=link,
                                        new_target=new_name,
                                        new_link_text=new_link_text
                                    )

                                    link_updates.append(link_update)
                                    self.logger.debug(f"Planned link update in {ref_file.name}: {link.original_text} → {new_link_text}")

        self.logger.info(f"Planned {len(link_updates)} link updates to preserve integrity")
        return link_updates

    def _generate_updated_link_text(self, old_link: WikiLink, new_target: str) -> str:
        """Generate updated link text with new target."""
        embed_prefix = "!" if old_link.is_embed else ""

        if old_link.display_text and old_link.display_text != old_link.target_note:
            # Preserve custom display text
            return f"{embed_prefix}[[{new_target}|{old_link.display_text}]]"
        else:
            # Standard link without custom display
            return f"{embed_prefix}[[{new_target}]]"

    def validate_move_integrity(self, backup_path: str = None) -> Dict[str, Any]:
        """
        Validate the integrity of the vault after moves have been executed.
        
        P1-2 Features:
        - Post-move link integrity checking
        - Broken link detection and reporting
        - File system validation
        - Optional auto-rollback on validation failure
        
        Args:
            backup_path: Path to backup for rollback if validation fails
            
        Returns:
            Dict with validation results and recommendations
            
        Raises:
            BackupError: If validation fails and rollback is unsuccessful
        """
        self.logger.info("Starting post-move integrity validation")

        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "vault_path": str(self.vault_root),
            "backup_path": backup_path,
            "validation_passed": False,
            "errors_found": [],
            "warnings_found": [],
            "link_integrity": {},
            "file_system_integrity": {},
            "recommendations": []
        }

        try:
            # Step 1: Validate file system integrity
            fs_validation = self._validate_file_system_integrity()
            validation_results["file_system_integrity"] = fs_validation

            if fs_validation["errors"]:
                validation_results["errors_found"].extend(fs_validation["errors"])

            # Step 2: Validate link integrity
            link_validation = self._validate_link_integrity()
            validation_results["link_integrity"] = link_validation

            if link_validation["broken_links"]:
                validation_results["warnings_found"].append(
                    f"Found {len(link_validation['broken_links'])} broken links"
                )

            # Step 3: Check for critical issues
            critical_errors = [error for error in validation_results["errors_found"]
                             if "critical" in error.lower() or "missing" in error.lower()]

            # Step 4: Determine overall validation status
            if not validation_results["errors_found"]:
                validation_results["validation_passed"] = True
                validation_results["recommendations"].append("✅ All validations passed successfully")
            else:
                validation_results["validation_passed"] = False
                validation_results["recommendations"].append("⚠️ Validation issues detected - review recommended")

                if critical_errors and backup_path:
                    validation_results["recommendations"].append("🔄 Critical issues found - rollback recommended")

            # Log validation summary
            self.logger.info(f"Validation complete: {'PASSED' if validation_results['validation_passed'] else 'FAILED'}")
            self.logger.info(f"Errors: {len(validation_results['errors_found'])}, Warnings: {len(validation_results['warnings_found'])}")

            return validation_results

        except Exception as e:
            error_msg = f"Validation process failed: {e}"
            self.logger.error(error_msg)
            validation_results["errors_found"].append(error_msg)
            validation_results["validation_passed"] = False
            return validation_results

    def _validate_file_system_integrity(self) -> Dict[str, Any]:
        """Validate file system integrity after moves."""
        fs_results = {
            "total_files_checked": 0,
            "readable_files": 0,
            "unreadable_files": 0,
            "errors": [],
            "warnings": []
        }

        try:
            # Check all markdown files are readable
            for md_file in self.vault_root.rglob("*.md"):
                fs_results["total_files_checked"] += 1

                try:
                    # Test file readability
                    content = md_file.read_text(encoding='utf-8')

                    # Basic content validation
                    if len(content.strip()) == 0:
                        fs_results["warnings"].append(f"Empty file detected: {md_file}")

                    fs_results["readable_files"] += 1

                except Exception as e:
                    fs_results["unreadable_files"] += 1
                    fs_results["errors"].append(f"Cannot read file {md_file}: {e}")

            # Check directory structure
            expected_dirs = ["Inbox", "Permanent Notes", "Literature Notes", "Fleeting Notes"]
            for dir_name in expected_dirs:
                dir_path = self.vault_root / dir_name
                if not dir_path.exists():
                    fs_results["warnings"].append(f"Expected directory missing: {dir_name}")
                elif not dir_path.is_dir():
                    fs_results["errors"].append(f"Path exists but is not directory: {dir_name}")

            self.logger.info(f"File system validation: {fs_results['readable_files']}/{fs_results['total_files_checked']} files readable")

        except Exception as e:
            fs_results["errors"].append(f"File system validation failed: {e}")

        return fs_results

    def _validate_link_integrity(self) -> Dict[str, Any]:
        """Validate wiki-link integrity after moves."""
        link_results = {
            "total_links_checked": 0,
            "valid_links": 0,
            "broken_links": [],
            "link_statistics": {}
        }

        try:
            # Scan for current link status
            link_index = self.scan_wiki_links()

            link_results["total_links_checked"] = sum(len(links) for links in link_index.links_by_file.values())
            link_results["valid_links"] = link_results["total_links_checked"] - len(link_index.broken_links)

            # Convert broken links to readable format
            for file_path, target in link_index.broken_links:
                relative_path = file_path.relative_to(self.vault_root)
                link_results["broken_links"].append({
                    "file": str(relative_path),
                    "broken_target": target
                })

            # Generate statistics
            link_results["link_statistics"] = {
                "files_with_links": len(link_index.links_by_file),
                "unique_targets": len(link_index.links_to_file),
                "broken_link_percentage": round(
                    (len(link_index.broken_links) / max(link_results["total_links_checked"], 1)) * 100, 2
                )
            }

            self.logger.info(f"Link validation: {link_results['valid_links']}/{link_results['total_links_checked']} links valid")

        except Exception as e:
            self.logger.error(f"Link validation failed: {e}")
            # Don't fail validation entirely if link scanning fails

        return link_results

    def execute_with_validation(self,
                              create_backup: bool = True,
                              validate_after: bool = True,
                              auto_rollback: bool = True,
                              progress_callback=None) -> Dict[str, Any]:
        """
        Execute moves with comprehensive post-move validation and auto-rollback.
        
        P1-2 Enhanced Features:
        - Executes file moves using existing P1-1 system
        - Performs comprehensive post-move validation
        - Auto-rollback on validation failure (if enabled)
        - Detailed reporting of validation results
        
        Args:
            create_backup: Whether to create backup before operations
            validate_after: Whether to validate after execution  
            auto_rollback: Whether to auto-rollback on validation failure
            progress_callback: Optional progress reporting callback
            
        Returns:
            Dict with execution and validation results
        """
        self.logger.info("Starting execution with validation (P1-2)")

        # Step 1: Execute moves using existing P1-1 system
        execution_result = self.execute_moves(
            create_backup=create_backup,
            validate_first=True,
            rollback_on_error=True,
            progress_callback=progress_callback
        )

        # Step 2: Perform post-move validation if requested
        validation_result = None
        if validate_after and execution_result["status"] == "success":
            self.logger.info("Performing post-move validation")

            backup_path = execution_result.get("backup_path")
            validation_result = self.validate_move_integrity(backup_path)

            # Step 3: Auto-rollback on validation failure
            if not validation_result["validation_passed"] and auto_rollback and backup_path:
                critical_errors = [error for error in validation_result["errors_found"]
                                 if "critical" in error.lower()]

                if critical_errors:
                    self.logger.warning("Critical validation errors detected - initiating auto-rollback")
                    try:
                        self.rollback(backup_path)
                        execution_result["status"] = "rolled_back_due_to_validation_failure"
                        execution_result["rollback_reason"] = "Critical validation errors detected"
                    except Exception as rollback_error:
                        self.logger.error(f"Auto-rollback failed: {rollback_error}")
                        execution_result["status"] = "validation_failed_rollback_failed"
                        execution_result["rollback_error"] = str(rollback_error)

        # Combine results
        combined_result = execution_result.copy()
        combined_result["validation_performed"] = validate_after
        if validation_result:
            combined_result["validation_results"] = validation_result

        return combined_result

    def list_backups(self) -> List[Path]:
        """
        List all backup directories, sorted from newest to oldest.
        
        Returns:
            List[Path]: Backup directories sorted by timestamp (newest first)
        """
        backup_root = Path(self.backup_root)
        if not backup_root.exists():
            return []

        # Find all directories that match the backup naming pattern
        backup_pattern = re.compile(r"^knowledge-\d{8}-\d{6}$")
        backup_dirs = []

        for item in backup_root.iterdir():
            if item.is_dir() and backup_pattern.match(item.name):
                backup_dirs.append(item)

        # Sort by name (which sorts by timestamp since format is YYYYMMDD-HHMMSS)
        # Reverse to get newest first
        backup_dirs.sort(key=lambda x: x.name, reverse=True)

        return backup_dirs

    def prune_backups(self, keep: int, dry_run: bool = False) -> Dict[str, Any]:
        """
        Remove old backup directories, keeping only the most recent N backups.
        
        Args:
            keep: Number of most recent backups to keep
            dry_run: If True, return plan without deleting anything
            
        Returns:
            Dict with pruning plan and results
            
        Raises:
            BackupError: If backup operations fail
        """
        if keep < 0:
            raise BackupError(f"Keep count must be non-negative, got: {keep}")

        self.logger.info(f"Pruning backups: keeping {keep} most recent")

        backups = self.list_backups()

        # Determine which backups to keep and which to prune
        to_keep = backups[:keep] if keep <= len(backups) else backups
        to_prune = backups[keep:] if keep < len(backups) else []

        plan = {
            "plan": True,
            "keep": keep,
            "found": len(backups),
            "to_keep": to_keep,
            "to_prune": to_prune,
            "deleted": [],
            "errors": []
        }

        if dry_run:
            self.logger.info(f"Dry run: would delete {len(to_prune)} backup(s)")
            return plan

        # Actual deletion logic
        deleted_count = 0
        for backup_path in to_prune:
            try:
                backup_size = self._get_directory_size(backup_path)
                self.logger.info(f"Deleting backup: {backup_path.name} ({backup_size:.2f} MB)")

                shutil.rmtree(backup_path)
                plan["deleted"].append({
                    "path": str(backup_path),
                    "name": backup_path.name,
                    "size_mb": backup_size
                })
                deleted_count += 1

            except Exception as e:
                error_msg = f"Failed to delete {backup_path}: {e}"
                self.logger.error(error_msg)
                plan["errors"].append(error_msg)

        plan["deleted_count"] = deleted_count
        plan["success"] = len(plan["errors"]) == 0

        if plan["success"]:
            self.logger.info(f"Successfully pruned {deleted_count} backup(s)")
        else:
            self.logger.warning(f"Pruning completed with {len(plan['errors'])} error(s)")

        return plan

    def _get_directory_size(self, directory: Path) -> float:
        """
        Calculate the total size of a directory in megabytes.
        
        Args:
            directory: Directory path to measure
            
        Returns:
            Size in megabytes
        """
        import os
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    file_path = Path(dirpath) / filename
                    if file_path.exists():
                        total_size += file_path.stat().st_size
        except Exception:
            # If we can't calculate size, return 0
            pass

        return total_size / (1024 * 1024)  # Convert bytes to MB
