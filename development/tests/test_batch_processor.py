#!/usr/bin/env python3
"""
Test suite for InnerOS Batch Processor
TDD implementation following red-green-refactor methodology
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

# Add development src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from inneros_batch_processor import BatchProcessor


class TestBatchProcessor(unittest.TestCase):
    """Test cases for BatchProcessor directory scanning functionality"""
    
    def setUp(self):
        """Set up test environment with temporary directories and files"""
        self.test_dir = tempfile.mkdtemp()
        self.inbox_dir = Path(self.test_dir) / "knowledge" / "Inbox"
        self.fleeting_dir = Path(self.test_dir) / "knowledge" / "Fleeting Notes"
        
        # Create test directories
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.fleeting_dir.mkdir(parents=True, exist_ok=True)
        
        # Create test markdown files (make them old enough to not be filtered)
        old_time = datetime.now() - timedelta(hours=3)
        self.create_test_file(self.inbox_dir / "test-note-1.md", "Test content 1", old_time)
        self.create_test_file(self.inbox_dir / "test-note-2.md", "Test content 2", old_time)
        self.create_test_file(self.fleeting_dir / "fleeting-note-1.md", "Fleeting content", old_time)
        
        # Create recently modified file (should be filtered out)
        recent_file = self.inbox_dir / "recent-note.md"
        self.create_test_file(recent_file, "Recent content")  # This one stays recent
        
        # Create non-markdown file (should be ignored)
        self.create_test_file(self.inbox_dir / "not-markdown.txt", "Not markdown")
        
        self.processor = BatchProcessor(base_dir=self.test_dir)
    
    def create_test_file(self, path: Path, content: str, file_time: Optional[datetime] = None):
        """Helper to create test files with frontmatter and optional timestamp"""
        if file_time is None:
            file_time = datetime.now()
            
        frontmatter = f"""---
type: fleeting
created: {file_time.strftime('%Y-%m-%d %H:%M')}
status: inbox
---

{content}
"""
        path.write_text(frontmatter)
        
        # Set file modification time if specified
        if file_time != datetime.now():
            timestamp = file_time.timestamp()
            os.utime(path, (timestamp, timestamp))
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_scan_notes_returns_correct_count(self):
        """Test that scan_notes returns correct count of processable files"""
        # This test will FAIL initially (Red phase)
        result = self.processor.scan_notes()
        
        # Should find 3 markdown files (2 inbox + 1 fleeting, excluding recent)
        self.assertEqual(result['total_count'], 3)
        self.assertEqual(len(result['files']), 3)
    
    def test_scan_notes_filters_recent_files(self):
        """Test that recently modified files are filtered out"""
        result = self.processor.scan_notes()
        
        # Should not include recent-note.md
        file_names = [f['name'] for f in result['files']]
        self.assertNotIn('recent-note.md', file_names)
    
    def test_scan_notes_only_includes_markdown(self):
        """Test that only .md files are included"""
        result = self.processor.scan_notes()
        
        # Should not include .txt files
        file_names = [f['name'] for f in result['files']]
        self.assertNotIn('not-markdown.txt', file_names)
    
    def test_scan_notes_includes_both_directories(self):
        """Test that both Inbox and Fleeting Notes directories are scanned"""
        result = self.processor.scan_notes()
        
        # Should include files from both directories
        file_paths = [f['path'] for f in result['files']]
        inbox_files = [p for p in file_paths if 'Inbox' in p]
        fleeting_files = [p for p in file_paths if 'Fleeting Notes' in p]
        
        self.assertGreater(len(inbox_files), 0, "Should find files in Inbox")
        self.assertGreater(len(fleeting_files), 0, "Should find files in Fleeting Notes")
    
    def test_scan_notes_returns_file_details(self):
        """Test that scan_notes returns proper file details"""
        result = self.processor.scan_notes()
        
        # Each file should have required fields
        for file_info in result['files']:
            self.assertIn('name', file_info)
            self.assertIn('path', file_info)
            self.assertIn('size', file_info)
            self.assertIn('modified', file_info)
    
    # === P0-2: DRY-RUN MODE TESTS ===
    
    def test_dry_run_analyzes_yaml_frontmatter(self):
        """Test that dry_run parses YAML frontmatter from files"""
        # This test will FAIL initially (Red phase)
        result = self.processor.dry_run()
        
        # Should find files and analyze their YAML
        self.assertGreater(result['total_analyzed'], 0)
        self.assertIn('files', result)
        
        # Each analyzed file should have frontmatter analysis
        for file_analysis in result['files']:
            self.assertIn('name', file_analysis)
            self.assertIn('current_tags', file_analysis)
            self.assertIn('missing_metadata', file_analysis)
            self.assertIn('ai_opportunities', file_analysis)
    
    def test_dry_run_detects_missing_tags(self):
        """Test that dry_run identifies files with no or few tags"""
        # Create file with minimal tags
        minimal_tags_file = self.inbox_dir / "minimal-tags.md"
        old_time = datetime.now() - timedelta(hours=3)
        self.create_test_file(minimal_tags_file, "Minimal content", old_time)
        
        result = self.processor.dry_run()
        
        # Should identify opportunity for more tags
        minimal_file = next((f for f in result['files'] if f['name'] == 'minimal-tags.md'), None)
        self.assertIsNotNone(minimal_file)
        self.assertIn('needs_more_tags', minimal_file['ai_opportunities'])
    
    def test_dry_run_detects_missing_quality_score(self):
        """Test that dry_run identifies files without quality scores"""
        result = self.processor.dry_run()
        
        # Should identify files missing quality_score metadata
        files_needing_quality = [f for f in result['files'] 
                               if 'needs_quality_score' in f['ai_opportunities']]
        self.assertGreater(len(files_needing_quality), 0)
    
    def test_dry_run_provides_processing_preview(self):
        """Test that dry_run shows what would be processed"""
        result = self.processor.dry_run()
        
        # Should provide summary statistics
        self.assertIn('summary', result)
        self.assertIn('total_files_needing_tags', result['summary'])
        self.assertIn('total_files_needing_quality', result['summary'])
        self.assertIn('estimated_processing_time', result['summary'])
    
    def test_dry_run_respects_same_filters_as_scan(self):
        """Test that dry_run applies same safety filters as scan_notes"""
        scan_result = self.processor.scan_notes()
        dry_run_result = self.processor.dry_run()
        
        # Should find same number of files
        self.assertEqual(len(scan_result['files']), len(dry_run_result['files']))
        
        # Should have same file names
        scan_names = {f['name'] for f in scan_result['files']}
        dry_run_names = {f['name'] for f in dry_run_result['files']}
        self.assertEqual(scan_names, dry_run_names)
    
    def test_dry_run_safe_yaml_parsing(self):
        """Test that dry_run handles malformed YAML gracefully"""
        # Create file with malformed YAML
        bad_yaml_file = self.inbox_dir / "bad-yaml.md"
        old_time = datetime.now() - timedelta(hours=3)
        bad_yaml_content = """---
type: fleeting
tags: [unclosed array
status: inbox
---

# Content with bad YAML
"""
        bad_yaml_file.write_text(bad_yaml_content)
        os.utime(bad_yaml_file, (old_time.timestamp(), old_time.timestamp()))
        
        # Should not crash on bad YAML
        result = self.processor.dry_run()
        self.assertIsInstance(result, dict)
        
        # Should identify the file as having YAML issues
        bad_file = next((f for f in result['files'] if f['name'] == 'bad-yaml.md'), None)
        self.assertIsNotNone(bad_file)
        self.assertIn('yaml_parsing_error', bad_file)
    
    # === P1-2: BACKUP SYSTEM INTEGRATION TESTS ===
    
    def test_processor_has_backup_integration(self):
        """Test that BatchProcessor can create backups before processing"""
        # This test will FAIL initially (Red phase)
        result = self.processor.create_backup()
        
        # Should return backup path
        self.assertIsInstance(result, str)
        self.assertIn('knowledge-', result)  # Contains timestamp format
        
        # Backup directory should exist
        backup_path = Path(result)
        self.assertTrue(backup_path.exists())
        self.assertTrue(backup_path.is_dir())
    
    def test_process_with_backup_creates_backup_first(self):
        """Test that process_notes creates backup before making changes"""
        # Create a test file to process
        test_file = self.inbox_dir / "process-test.md"
        old_time = datetime.now() - timedelta(hours=3)
        self.create_test_file(test_file, "Test content for processing", old_time)
        
        # This will fail initially - process_notes doesn't exist yet
        result = self.processor.process_notes(create_backup=True, limit=1)
        
        # Should include backup information
        self.assertIn('backup_created', result)
        self.assertIn('backup_path', result)
        self.assertTrue(Path(result['backup_path']).exists())
    
    def test_rollback_capability(self):
        """Test that processor can rollback to previous backup"""
        # Create initial backup
        backup_path = self.processor.create_backup()
        
        # Modify something (simulate processing)
        test_file = self.inbox_dir / "rollback-test.md"
        test_file.write_text("Original content")
        
        # Create another backup
        backup_path_2 = self.processor.create_backup()
        
        # Modify file again
        test_file.write_text("Modified content")
        
        # Rollback to first backup
        self.processor.rollback(backup_path)
        
        # File should not exist (wasn't in original backup)
        self.assertFalse(test_file.exists())
    
    def test_backup_safety_prevents_processing_without_backup(self):
        """Test that processing fails safely if backup creation fails"""
        # Mock backup failure scenario would go here
        # For now, test that we have the safety mechanisms
        self.assertTrue(hasattr(self.processor, 'create_backup'))
        self.assertTrue(hasattr(self.processor, 'rollback'))


if __name__ == '__main__':
    unittest.main()
