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
development_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(development_dir / "src"))
sys.path.insert(0, str(development_dir))

from src.utils.directory_organizer import DirectoryOrganizer, BackupError


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


class TestDirectoryOrganizerExecution(unittest.TestCase):
    """Test P1-1 actual file move execution functionality."""
    
    def setUp(self):
        """Set up test fixtures for file execution tests."""
        # Create temporary directories for testing
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.test_dir) / "test_vault"
        self.backup_root = Path(self.test_dir) / "backups"
        
        # Create test vault structure with Zettelkasten directories
        self.vault_root.mkdir(parents=True)
        self.backup_root.mkdir(parents=True)
        
        # Create standard Zettelkasten directory structure
        (self.vault_root / "Inbox").mkdir()
        (self.vault_root / "Permanent Notes").mkdir()
        (self.vault_root / "Literature Notes").mkdir()
        (self.vault_root / "Fleeting Notes").mkdir()
        
        # Create misplaced files in Inbox that need moving
        self._create_misplaced_files_for_execution()
        
        self.organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(self.backup_root)
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def _create_misplaced_files_for_execution(self):
        """Create test files that need actual moving."""
        # Permanent note in Inbox (should move to Permanent Notes/)
        permanent_file = self.vault_root / "Inbox" / "permanent-in-inbox.md"
        permanent_file.write_text("""---
type: permanent
title: Test Permanent Note
created: 2025-09-16 10:30
---

This is a permanent note that should be moved.""")
        
        # Literature note in Inbox (should move to Literature Notes/)
        literature_file = self.vault_root / "Inbox" / "literature-in-inbox.md"
        literature_file.write_text("""---
type: literature
title: Test Literature Note
source: https://example.com
---

This is a literature note that should be moved.""")
        
        # Fleeting note in Inbox (should move to Fleeting Notes/)
        fleeting_file = self.vault_root / "Inbox" / "fleeting-in-inbox.md"
        fleeting_file.write_text("""---
type: fleeting
title: Test Fleeting Note
---

This is a fleeting note that should be moved.""")
        
        # Already correctly placed note (should not move)
        correct_file = self.vault_root / "Permanent Notes" / "already-correct.md"
        correct_file.write_text("""---
type: permanent
title: Already Correct Note
---

This note is already in the correct directory.""")
    
    def test_execute_moves_files_to_correct_directories(self):
        """GREEN: Test that execute_moves() actually moves files based on type."""
        # Execute moves with backup disabled for cleaner test
        result = self.organizer.execute_moves(create_backup=False)
        
        # Verify files were moved to correct directories
        self.assertTrue((self.vault_root / "Permanent Notes" / "permanent-in-inbox.md").exists())
        self.assertTrue((self.vault_root / "Literature Notes" / "literature-in-inbox.md").exists()) 
        self.assertTrue((self.vault_root / "Fleeting Notes" / "fleeting-in-inbox.md").exists())
        
        # Verify files no longer in Inbox
        self.assertFalse((self.vault_root / "Inbox" / "permanent-in-inbox.md").exists())
        self.assertFalse((self.vault_root / "Inbox" / "literature-in-inbox.md").exists())
        self.assertFalse((self.vault_root / "Inbox" / "fleeting-in-inbox.md").exists())
        
        # Verify result stats
        self.assertEqual(result["moves_executed"], 3)
        self.assertEqual(result["status"], "success")
    
    def test_execute_moves_creates_backup_before_operations(self):
        """GREEN: Test that execute_moves() creates backup before moving files."""
        result = self.organizer.execute_moves(create_backup=True)
        
        # Verify backup was created
        self.assertTrue(result["backup_created"])
        self.assertIsNotNone(result["backup_path"])
        
        # Verify backup path exists and contains backup
        backup_path = Path(result["backup_path"])
        self.assertTrue(backup_path.exists())
        self.assertTrue((backup_path / "Inbox" / "permanent-in-inbox.md").exists())
    
    def test_execute_moves_preserves_file_content(self):
        """GREEN: Test that file content is preserved during moves."""
        # Get original content
        original_content = (self.vault_root / "Inbox" / "permanent-in-inbox.md").read_text()
        
        # Execute moves
        self.organizer.execute_moves(create_backup=False)
        
        # Verify content preserved
        moved_content = (self.vault_root / "Permanent Notes" / "permanent-in-inbox.md").read_text()
        self.assertEqual(original_content, moved_content)
        self.assertIn("This is a permanent note that should be moved", moved_content)
    
    def test_execute_moves_handles_target_directory_creation(self):
        """GREEN: Test that execute_moves() creates target directories if needed."""
        # Remove a directory to test creation
        shutil.rmtree(self.vault_root / "Permanent Notes")
        
        # Execute moves
        result = self.organizer.execute_moves(create_backup=False)
        
        # Verify directory was created and file moved
        self.assertTrue((self.vault_root / "Permanent Notes").exists())
        self.assertTrue((self.vault_root / "Permanent Notes" / "permanent-in-inbox.md").exists())
        self.assertEqual(result["moves_executed"], 3)
    
    def test_execute_moves_reports_progress_and_results(self):
        """GREEN: Test that execute_moves() returns detailed execution results."""
        result = self.organizer.execute_moves(create_backup=False)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn("moves_executed", result)
        self.assertIn("files_processed", result)
        self.assertIn("execution_time_seconds", result)
        self.assertIn("status", result)
        
        # Verify result values
        self.assertEqual(result["moves_executed"], 3)
        self.assertEqual(result["files_processed"], 3)
        self.assertEqual(result["status"], "success")
        self.assertGreaterEqual(result["execution_time_seconds"], 0)
    
    def test_execute_moves_validates_operations_before_execution(self):
        """GREEN: Test that execute_moves() validates dry run before execution."""
        # This should work normally
        result = self.organizer.execute_moves(validate_first=True, create_backup=False)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["moves_executed"], 3)
    
    def test_execute_moves_rollback_on_partial_failure(self):
        """GREEN: Test that execute_moves() rolls back on partial failures."""
        # Create conflict scenario - add file to target that will cause conflict
        conflict_file = self.vault_root / "Permanent Notes" / "permanent-in-inbox.md"
        conflict_file.write_text("Conflict content")
        
        # Execute moves should fail due to conflict
        with self.assertRaises(BackupError):
            self.organizer.execute_moves(rollback_on_error=True, create_backup=True)


if __name__ == "__main__":
    unittest.main()
