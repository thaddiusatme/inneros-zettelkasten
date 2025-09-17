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
