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


if __name__ == '__main__':
    unittest.main()
