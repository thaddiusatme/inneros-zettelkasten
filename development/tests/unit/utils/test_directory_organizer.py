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

        # Verify path format and location (should use the organizer's backup_root)
        expected_parent = str(self.organizer.backup_root)  # Use organizer's actual backup root
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


class TestDirectoryOrganizerGuardrails(unittest.TestCase):
    """Test P0 backup nesting guardrails."""

    def setUp(self):
        """Set up test fixtures for guardrail tests."""
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.test_dir) / "test_vault"
        self.vault_root.mkdir(parents=True)

        # Create a test file in vault
        test_file = self.vault_root / "test.md"
        test_file.write_text("test content")

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def test_backup_refuses_nested_target_inside_vault(self):
        """RED: Test backup refuses when backup_root is inside vault_root."""
        # Create backup root INSIDE the vault (this should be prevented)
        nested_backup_root = self.vault_root / "backups"

        with self.assertRaises(BackupError) as context:
            DirectoryOrganizer(
                vault_root=str(self.vault_root),
                backup_root=str(nested_backup_root)
            )

        self.assertIn("backup target is inside source", str(context.exception).lower())
        self.assertIn("recursive", str(context.exception).lower())

    def test_backup_refuses_nested_target_in_subdirectory(self):
        """RED: Test backup refuses when backup_root is in any vault subdirectory."""
        # Create backup root inside a vault subdirectory
        inbox_dir = self.vault_root / "Inbox"
        inbox_dir.mkdir()
        nested_backup_root = inbox_dir / "my_backups"

        with self.assertRaises(BackupError) as context:
            DirectoryOrganizer(
                vault_root=str(self.vault_root),
                backup_root=str(nested_backup_root)
            )

        self.assertIn("backup target is inside source", str(context.exception).lower())

    def test_backup_allows_external_backup_root(self):
        """RED: Test backup allows backup_root outside vault (should pass)."""
        # Create backup root OUTSIDE the vault (this should work)
        external_backup_root = Path(self.test_dir) / "external_backups"

        # This should NOT raise an exception
        organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(external_backup_root)
        )

        # Should be able to create backup successfully
        backup_path = organizer.create_backup()
        self.assertTrue(Path(backup_path).exists())

    def test_backup_allows_sibling_backup_root(self):
        """RED: Test backup allows backup_root as sibling to vault."""
        # Create backup root as sibling to vault (this should work)
        sibling_backup_root = Path(self.test_dir) / "backups"

        # This should NOT raise an exception
        organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(sibling_backup_root)
        )

        # Should be able to create backup successfully
        backup_path = organizer.create_backup()
        self.assertTrue(Path(backup_path).exists())

    def test_default_backup_root_is_external(self):
        """RED: Test default backup root is external to vault."""
        # Create organizer with default backup root (should use external default)
        organizer = DirectoryOrganizer(vault_root=str(self.vault_root))

        # Default should be ~/backups/{vault_name}/ or similar external path
        self.assertFalse(str(organizer.backup_root).startswith(str(self.vault_root)))

        # Should be able to create backup successfully
        backup_path = organizer.create_backup()
        self.assertTrue(Path(backup_path).exists())


class TestDirectoryOrganizerExcludes(unittest.TestCase):
    """Test P0 backup exclude rules functionality."""

    def setUp(self):
        """Set up test fixtures for exclude rules tests."""
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.test_dir) / "test_vault"
        self.backup_root = Path(self.test_dir) / "external_backups"

        self.vault_root.mkdir(parents=True)
        self.backup_root.mkdir(parents=True)

        # Create test vault with directories that should be excluded
        self._create_vault_with_excludable_content()

        self.organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(self.backup_root)
        )

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)

    def _create_vault_with_excludable_content(self):
        """Create vault with content that should/shouldn't be backed up."""
        # Content that SHOULD be backed up
        (self.vault_root / "important.md").write_text("Important content")
        (self.vault_root / "Inbox").mkdir()
        (self.vault_root / "Inbox" / "note.md").write_text("Inbox note")

        # Content that SHOULD NOT be backed up (heavy/derived directories)
        (self.vault_root / "backups").mkdir()
        (self.vault_root / "backups" / "old-backup.txt").write_text("Old backup content")

        (self.vault_root / ".git").mkdir()
        (self.vault_root / ".git" / "config").write_text("Git config")

        (self.vault_root / "web_ui_env").mkdir()  # Python virtual environment
        (self.vault_root / "web_ui_env" / "lib").mkdir()
        (self.vault_root / "web_ui_env" / "lib" / "python3.13").mkdir()
        (self.vault_root / "web_ui_env" / "lib" / "python3.13" / "site-packages").mkdir()
        (self.vault_root / "web_ui_env" / "lib" / "python3.13" / "site-packages" / "large_package.py").write_text("Large package content")

    def test_backup_excludes_backups_directory(self):
        """RED: Test that backup excludes existing backups/ directory."""
        backup_path = self.organizer.create_backup()

        # Should NOT contain backups directory
        backups_in_backup = Path(backup_path) / "backups"
        self.assertFalse(backups_in_backup.exists(), "backups/ directory should be excluded from backup")

        # Should still contain important content
        important_in_backup = Path(backup_path) / "important.md"
        self.assertTrue(important_in_backup.exists(), "Important content should be included")

    def test_backup_excludes_git_directory(self):
        """RED: Test that backup excludes .git/ directory."""
        backup_path = self.organizer.create_backup()

        # Should NOT contain .git directory
        git_in_backup = Path(backup_path) / ".git"
        self.assertFalse(git_in_backup.exists(), ".git/ directory should be excluded from backup")

        # Should still contain important content
        inbox_in_backup = Path(backup_path) / "Inbox" / "note.md"
        self.assertTrue(inbox_in_backup.exists(), "Inbox content should be included")

    def test_backup_excludes_venv_directory(self):
        """RED: Test that backup excludes Python virtual environment directories."""
        backup_path = self.organizer.create_backup()

        # Should NOT contain venv directory
        venv_in_backup = Path(backup_path) / "web_ui_env"
        self.assertFalse(venv_in_backup.exists(), "Virtual environment should be excluded from backup")

    def test_backup_includes_only_essential_content(self):
        """RED: Test that backup includes essential content but excludes derived/heavy directories."""
        backup_path = self.organizer.create_backup()
        backup_path_obj = Path(backup_path)

        # Should include essential content
        essential_files = ["important.md", "Inbox/note.md"]
        for file_path in essential_files:
            backup_file = backup_path_obj / file_path
            self.assertTrue(backup_file.exists(), f"Essential file {file_path} should be included")

        # Should exclude heavy/derived directories
        excluded_dirs = ["backups", ".git", "web_ui_env"]
        for dir_name in excluded_dirs:
            excluded_dir = backup_path_obj / dir_name
            self.assertFalse(excluded_dir.exists(), f"Directory {dir_name} should be excluded")

    def test_backup_exclude_patterns_configurable(self):
        """RED: Test that exclude patterns can be configured."""
        # Create organizer with custom exclude patterns
        custom_excludes = ["backups", ".git", "custom_exclude"]

        # Create custom exclude directory
        (self.vault_root / "custom_exclude").mkdir()
        (self.vault_root / "custom_exclude" / "file.txt").write_text("Should be excluded")

        # This test will fail until we implement configurable excludes
        organizer_with_custom = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(self.backup_root),
            exclude_patterns=custom_excludes  # This parameter doesn't exist yet
        )

        backup_path = organizer_with_custom.create_backup()

        # Custom exclude should not be in backup
        custom_exclude_in_backup = Path(backup_path) / "custom_exclude"
        self.assertFalse(custom_exclude_in_backup.exists(), "Custom exclude directory should not be in backup")


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


class TestDirectoryOrganizerRetention(unittest.TestCase):
    """Tests for P0: Backup retention and pruning."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.test_dir) / "vault"
        self.backup_root = Path(self.test_dir) / "backups"
        self.vault_root.mkdir()
        self.backup_root.mkdir()

        # Create some dummy backup directories with valid names
        self.backups = [
            self.backup_root / "knowledge-20250918-100000", # Oldest
            self.backup_root / "knowledge-20250918-110000",
            self.backup_root / "knowledge-20250918-120000",
            self.backup_root / "knowledge-20250918-130000",
            self.backup_root / "knowledge-20250918-140000"  # Newest
        ]
        for backup in self.backups:
            backup.mkdir()

        # Add a non-backup file/dir to ensure it's ignored
        (self.backup_root / "not-a-backup.txt").touch()
        (self.backup_root / "random-dir").mkdir()

        self.organizer = DirectoryOrganizer(str(self.vault_root), backup_root=str(self.backup_root))

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_list_backups_sorted_correctly(self):
        """Should list existing backups, sorted from newest to oldest."""
        sorted_backups = self.organizer.list_backups()
        self.assertEqual(len(sorted_backups), 5)
        self.assertEqual(sorted_backups[0].resolve(), self.backups[4].resolve()) # Newest first
        self.assertEqual(sorted_backups[4].resolve(), self.backups[0].resolve()) # Oldest last

    def test_prune_backups_dry_run_identifies_correct_backups_to_delete(self):
        """Dry run should identify older backups for deletion without actually deleting."""
        keep = 3
        prune_plan = self.organizer.prune_backups(keep=keep, dry_run=True)

        self.assertIn("plan", prune_plan)
        self.assertEqual(prune_plan["keep"], keep)
        self.assertEqual(prune_plan["found"], 5)
        self.assertEqual(len(prune_plan["to_prune"]), 2)
        self.assertEqual(len(prune_plan["to_keep"]), 3)
        self.assertIn(str(self.backups[0].resolve()), [str(p.resolve()) for p in prune_plan["to_prune"]])
        self.assertIn(str(self.backups[1].resolve()), [str(p.resolve()) for p in prune_plan["to_prune"]])

        # Verify no directories were actually deleted
        self.assertTrue(self.backups[0].exists())
        self.assertTrue(self.backups[1].exists())

    def test_prune_backups_handles_keeping_more_than_exist(self):
        """If keep > found, no backups should be pruned."""
        prune_plan = self.organizer.prune_backups(keep=10, dry_run=True)
        self.assertEqual(len(prune_plan["to_prune"]), 0)
        self.assertEqual(len(prune_plan["to_keep"]), 5)

    def test_prune_backups_handles_no_backups_gracefully(self):
        """If no backups exist, it should return an empty plan."""
        # Create a new organizer with an empty backup dir
        empty_backup_root = Path(self.test_dir) / "empty_backups"
        empty_backup_root.mkdir()
        organizer = DirectoryOrganizer(str(self.vault_root), backup_root=str(empty_backup_root))

        prune_plan = organizer.prune_backups(keep=3, dry_run=True)
        self.assertEqual(prune_plan["found"], 0)
        self.assertEqual(len(prune_plan["to_prune"]), 0)


if __name__ == "__main__":
    unittest.main()
