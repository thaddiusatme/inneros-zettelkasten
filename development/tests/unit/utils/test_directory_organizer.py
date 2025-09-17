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


class TestDirectoryOrganizerDryRun(unittest.TestCase):
    """Test dry run move planning functionality."""
    
    def assertHasAttr(self, obj, attr):
        """Helper method to assert object has attribute."""
        self.assertTrue(hasattr(obj, attr), f"Object should have attribute '{attr}'")
    
    def setUp(self):
        """Set up test fixtures for dry run tests."""
        self.test_dir = tempfile.mkdtemp()
        self.vault_root = Path(self.test_dir) / "test_vault"
        self.backup_root = Path(self.test_dir) / "backups"
        
        self.vault_root.mkdir(parents=True)
        self.backup_root.mkdir(parents=True)
        
        # Create realistic directory structure with misplaced files
        self._create_misplaced_files_structure()
        
        self.organizer = DirectoryOrganizer(
            vault_root=str(self.vault_root),
            backup_root=str(self.backup_root)
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir)
    
    def _create_misplaced_files_structure(self):
        """Create realistic test structure with misplaced files."""
        # Create proper directories
        dirs = ["Inbox", "Permanent Notes", "Fleeting Notes", "Literature Notes", "Media"]
        for dir_name in dirs:
            (self.vault_root / dir_name).mkdir()
        
        # Create files that need moving (misplaced based on type field)
        misplaced_files = {
            # Files in Inbox that should be moved based on type
            "Inbox/permanent-note-in-inbox.md": "---\ntype: permanent\ntitle: Test Permanent Note\n---\n\nContent here.",
            "Inbox/literature-note-in-inbox.md": "---\ntype: literature\ntitle: Test Literature Note\n---\n\nContent here.",
            "Inbox/fleeting-note-in-inbox.md": "---\ntype: fleeting\ntitle: Test Fleeting Note\n---\n\nContent here.",
            
            # Files with no type field (should remain in Inbox)
            "Inbox/no-type-field.md": "---\ntitle: No Type Field\n---\n\nContent without type.",
            
            # Files with unknown type
            "Inbox/unknown-type.md": "---\ntype: unknown\ntitle: Unknown Type\n---\n\nContent here.",
            
            # Files already in correct location (should not move)
            "Permanent Notes/already-permanent.md": "---\ntype: permanent\ntitle: Already Permanent\n---\n\nContent.",
            "Literature Notes/already-literature.md": "---\ntype: literature\ntitle: Already Literature\n---\n\nContent.",
            
            # Files with malformed YAML
            "Inbox/malformed-yaml.md": "---\ntype permanent\ntitle: Malformed YAML\n---\n\nContent.",
            
            # Non-markdown files (should not be processed)
            "Inbox/image.png": "fake image content",
            "Media/document.pdf": "fake pdf content"
        }
        
        for file_path, content in misplaced_files.items():
            full_path = self.vault_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    def test_plan_moves_returns_move_plan_object(self):
        """RED: Test that plan_moves returns structured move plan."""
        move_plan = self.organizer.plan_moves()
        
        # Should return MovePlan object with required attributes
        self.assertHasAttr(move_plan, 'moves')
        self.assertHasAttr(move_plan, 'conflicts')
        self.assertHasAttr(move_plan, 'unknown_types')
        self.assertHasAttr(move_plan, 'malformed_files')
        self.assertHasAttr(move_plan, 'summary')
    
    def test_plan_moves_identifies_type_based_moves(self):
        """RED: Test that planning identifies files needing moves based on type."""
        move_plan = self.organizer.plan_moves()
        
        # Should identify permanent note move
        permanent_move = next((m for m in move_plan.moves if 'permanent-note-in-inbox.md' in str(m.source)), None)
        self.assertIsNotNone(permanent_move, "Should identify permanent note needing move")
        self.assertEqual(str(permanent_move.source), str(self.vault_root / "Inbox/permanent-note-in-inbox.md"))
        self.assertEqual(str(permanent_move.target), str(self.vault_root / "Permanent Notes/permanent-note-in-inbox.md"))
        
        # Should identify literature note move
        literature_move = next((m for m in move_plan.moves if 'literature-note-in-inbox.md' in str(m.source)), None)
        self.assertIsNotNone(literature_move, "Should identify literature note needing move")
        self.assertEqual(str(literature_move.target), str(self.vault_root / "Literature Notes/literature-note-in-inbox.md"))
        
        # Should identify fleeting note move
        fleeting_move = next((m for m in move_plan.moves if 'fleeting-note-in-inbox.md' in str(m.source)), None)
        self.assertIsNotNone(fleeting_move, "Should identify fleeting note needing move")
        self.assertEqual(str(fleeting_move.target), str(self.vault_root / "Fleeting Notes/fleeting-note-in-inbox.md"))
    
    def test_plan_moves_ignores_correctly_placed_files(self):
        """RED: Test that planning ignores files already in correct directories."""
        move_plan = self.organizer.plan_moves()
        
        # Should not include files already in correct locations
        source_paths = [str(m.source) for m in move_plan.moves]
        self.assertNotIn(str(self.vault_root / "Permanent Notes/already-permanent.md"), source_paths)
        self.assertNotIn(str(self.vault_root / "Literature Notes/already-literature.md"), source_paths)
    
    def test_plan_moves_flags_unknown_types(self):
        """RED: Test that planning flags unknown file types."""
        move_plan = self.organizer.plan_moves()
        
        # Should flag unknown type
        unknown_files = [str(f) for f in move_plan.unknown_types]
        self.assertIn(str(self.vault_root / "Inbox/unknown-type.md"), unknown_files)
    
    def test_plan_moves_flags_malformed_yaml(self):
        """RED: Test that planning flags malformed YAML files."""
        move_plan = self.organizer.plan_moves()
        
        # Should flag malformed YAML
        malformed_files = [str(f) for f in move_plan.malformed_files]
        self.assertIn(str(self.vault_root / "Inbox/malformed-yaml.md"), malformed_files)
    
    def test_plan_moves_ignores_non_markdown_files(self):
        """RED: Test that planning ignores non-markdown files."""
        move_plan = self.organizer.plan_moves()
        
        # Should not include non-markdown files in any category
        all_files = ([str(m.source) for m in move_plan.moves] + 
                    [str(f) for f in move_plan.unknown_types] + 
                    [str(f) for f in move_plan.malformed_files])
        
        self.assertNotIn(str(self.vault_root / "Inbox/image.png"), all_files)
        self.assertNotIn(str(self.vault_root / "Media/document.pdf"), all_files)
    
    def test_plan_moves_no_file_mutations(self):
        """RED: Test that planning makes zero file system changes."""
        # Record original state
        original_files = {}
        for file_path in self.vault_root.rglob("*.md"):
            original_files[str(file_path)] = file_path.read_text()
        
        # Run planning - should not mutate files
        self.organizer.plan_moves()
        
        # Verify no files were changed
        for file_path in self.vault_root.rglob("*.md"):
            original_content = original_files.get(str(file_path))
            if original_content is not None:
                current_content = file_path.read_text()
                self.assertEqual(original_content, current_content, f"File was modified: {file_path}")
        
        # Verify no files were created or deleted
        current_files = set(str(p) for p in self.vault_root.rglob("*.md"))
        original_file_set = set(original_files.keys())
        self.assertEqual(current_files, original_file_set, "File system was modified during planning")
    
    def test_generate_move_report_json_format(self):
        """RED: Test JSON report generation."""
        move_plan = self.organizer.plan_moves()
        json_report = self.organizer.generate_move_report(move_plan, format='json')
        
        # Should be valid JSON
        import json
        parsed = json.loads(json_report)
        
        # Should contain required sections
        self.assertIn('summary', parsed)
        self.assertIn('moves', parsed)
        self.assertIn('issues', parsed)
        
        # Summary should have counts
        self.assertIn('total_moves', parsed['summary'])
        self.assertIn('unknown_types', parsed['summary'])
        self.assertIn('malformed_files', parsed['summary'])
    
    def test_generate_move_report_markdown_format(self):
        """RED: Test Markdown report generation."""
        move_plan = self.organizer.plan_moves()
        markdown_report = self.organizer.generate_move_report(move_plan, format='markdown')
        
        # Should contain markdown formatting
        self.assertIn('# Directory Organization Plan', markdown_report)
        self.assertIn('## Summary', markdown_report)
        self.assertIn('## Planned Moves', markdown_report)
        
        # Should contain table formatting
        self.assertIn('| Current Path | Target Path | Reason |', markdown_report)
        
        # Should contain move information
        self.assertIn('permanent-note-in-inbox.md', markdown_report)
    
    def test_move_plan_summary_statistics(self):
        """RED: Test that move plan includes accurate summary statistics."""
        move_plan = self.organizer.plan_moves()
        
        # Summary should reflect actual counts
        self.assertEqual(move_plan.summary['total_moves'], len(move_plan.moves))
        self.assertEqual(move_plan.summary['unknown_types'], len(move_plan.unknown_types))
        self.assertEqual(move_plan.summary['malformed_files'], len(move_plan.malformed_files))
        
        # Should have expected counts based on test data
        self.assertGreaterEqual(move_plan.summary['total_moves'], 3)  # At least permanent, literature, fleeting
        self.assertGreaterEqual(move_plan.summary['unknown_types'], 1)  # At least unknown-type.md
        self.assertGreaterEqual(move_plan.summary['malformed_files'], 1)  # At least malformed-yaml.md


if __name__ == "__main__":
    unittest.main()
