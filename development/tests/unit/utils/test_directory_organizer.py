#!/usr/bin/env python3
"""
Tests for directory organizer backup system.
Following TDD methodology: Red → Green → Refactor.

This module tests the Safety-First Directory Organization system with
emphasis on backup creation and rollback capabilities.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from utils.directory_organizer import DirectoryOrganizer, BackupError


class TestDirectoryOrganizerBackup(unittest.TestCase):
    """Test backup system functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.test_dir) / "test_vault"
        self.backup_root = Path(self.test_dir) / "backups"
        
        # Create test vault structure
        self.vault_root.mkdir(parents=True)
        self.backup_root.mkdir(parents=True)
        
        # Create test files and directories in vault
        self._create_test_vault_structure()
        
        self.organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(self.backup_root)
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def _create_test_vault_structure(self):
        """Create a realistic test vault structure."""
        # Create directories
        dirs = ["Inbox", "Permanent Notes", "Fleeting Notes", "Literature Notes", "Media"]
        for dir_name in dirs:
            (self.vault_root / dir_name).mkdir()
        
        # Create test files
        test_files = {
            "Inbox/test-note-1.md": "# Test Note 1\n\n---\ntype: permanent\n---\n\nContent here.",
            "Inbox/test-note-2.md": "# Test Note 2\n\n---\ntype: literature\n---\n\n[[test-note-1]]",
            "Permanent Notes/existing-permanent.md": "# Existing\n\n---\ntype: permanent\n---\n\nContent.",
            "Media/image.png": "fake image content",
            ".obsidian/config.json": '{"theme": "dark"}',
            ".hidden-file": "hidden content"
        }
        
        for file_path, content in test_files.items():
            full_path = self.vault_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def test_create_timestamped_backup_creates_directory(self):
        """RED: Test that backup creates timestamped directory."""
        # This should fail because DirectoryOrganizer doesn't exist yet
        backup_path = self.organizer.create_backup()
        
        # Verify backup directory exists
        self.assertTrue(Path(backup_path).exists())
        self.assertTrue(Path(backup_path).is_dir())
        
        # Verify timestamp format: knowledge-YYYYMMDD-HHMMSS
        backup_name = Path(backup_path).name
        self.assertRegex(backup_name, r"^knowledge-\d{8}-\d{6}$")
    
    def test_backup_contains_all_vault_files(self):
        """RED: Test that backup contains all files from vault."""
        backup_path = self.organizer.create_backup()
        
        # Check that all original files exist in backup
        original_files = list(self.vault_root.rglob("*"))
        original_files = [f for f in original_files if f.is_file()]
        
        for original_file in original_files:
            relative_path = original_file.relative_to(self.vault_root)
            backup_file = Path(backup_path) / relative_path
            
            self.assertTrue(backup_file.exists(), f"Missing backup file: {relative_path}")
            self.assertEqual(
                original_file.read_text(),
                backup_file.read_text(),
                f"Content mismatch in: {relative_path}"
            )
    
    def test_backup_includes_hidden_files(self):
        """RED: Test that backup includes hidden files and directories."""
        backup_path = self.organizer.create_backup()
        
        # Check hidden files are backed up
        hidden_file = Path(backup_path) / ".hidden-file"
        obsidian_config = Path(backup_path) / ".obsidian" / "config.json"
        
        self.assertTrue(hidden_file.exists(), "Hidden file not backed up")
        self.assertTrue(obsidian_config.exists(), "Hidden directory not backed up")
        
        # Verify content
        self.assertEqual(hidden_file.read_text(), "hidden content")
        self.assertEqual(obsidian_config.read_text(), '{"theme": "dark"}')
    
    def test_backup_preserves_directory_structure(self):
        """RED: Test that backup preserves exact directory structure."""
        backup_path = self.organizer.create_backup()
        
        # Check directory structure is preserved
        expected_dirs = ["Inbox", "Permanent Notes", "Fleeting Notes", "Literature Notes", "Media", ".obsidian"]
        
        for dir_name in expected_dirs:
            backup_dir = Path(backup_path) / dir_name
            self.assertTrue(backup_dir.exists(), f"Missing directory: {dir_name}")
            self.assertTrue(backup_dir.is_dir(), f"Not a directory: {dir_name}")
    
    def test_backup_returns_correct_path(self):
        """RED: Test that backup returns correct timestamped path."""
        # Capture time before backup
        before = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        backup_path = self.organizer.create_backup()
        
        # Capture time after backup  
        after = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # Verify path format and location
        expected_parent = str(self.backup_root)
        self.assertTrue(backup_path.startswith(expected_parent))
        
        backup_name = Path(backup_path).name
        timestamp = backup_name.replace("knowledge-", "")
        
        # Verify timestamp is between before and after (rough check)
        self.assertTrue(before <= timestamp <= after or timestamp >= before)
    
    def test_backup_error_on_invalid_vault(self):
        """RED: Test that backup raises error for invalid vault."""
        with self.assertRaises(BackupError):
            DirectoryOrganizer(
                vault_root="/nonexistent/path",
                backup_root=str(self.backup_root)
            )
    
    def test_backup_error_on_invalid_backup_root(self):
        """RED: Test that backup raises error for invalid backup root."""
        invalid_organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root="/nonexistent/readonly/path"
        )
        
        with self.assertRaises(BackupError):
            invalid_organizer.create_backup()
    
    def test_multiple_backups_have_different_timestamps(self):
        """RED: Test that multiple backups create different timestamps."""
        import time
        
        backup1 = self.organizer.create_backup()
        time.sleep(1)  # Ensure different timestamp
        backup2 = self.organizer.create_backup()
        
        self.assertNotEqual(backup1, backup2)
        self.assertTrue(Path(backup1).exists())
        self.assertTrue(Path(backup2).exists())


class TestDirectoryOrganizerRollback(unittest.TestCase):
    """Test rollback functionality."""
    
    def setUp(self):
        """Set up test fixtures for rollback tests."""
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.test_dir) / "test_vault"
        self.backup_root = Path(self.test_dir) / "backups"
        
        self.vault_root.mkdir(parents=True)
        self.backup_root.mkdir(parents=True)
        
        # Create initial state
        test_file = self.vault_root / "test.md" 
        test_file.write_text("original content")
        
        self.organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(self.backup_root)
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def test_rollback_restores_from_backup(self):
        """RED: Test that rollback restores vault from backup."""
        # Create backup
        backup_path = self.organizer.create_backup()
        
        # Modify vault (simulate failed operation)
        test_file = self.vault_root / "test.md"
        test_file.write_text("modified content")
        
        # Add new file that shouldn't exist after rollback
        new_file = self.vault_root / "new.md"
        new_file.write_text("new content")
        
        # Rollback
        self.organizer.rollback(backup_path)
        
        # Verify restoration
        self.assertEqual(test_file.read_text(), "original content")
        self.assertFalse(new_file.exists())
    
    def test_rollback_error_on_invalid_backup_path(self):
        """RED: Test rollback raises error for invalid backup path."""
        with self.assertRaises(BackupError):
            self.organizer.rollback("/nonexistent/backup/path")


if __name__ == "__main__":
    unittest.main()
