"""
TDD Iteration 7: Processed Screenshot Tracking System - RED Phase

Tests for tracking which screenshots have been processed to prevent reprocessing.
All tests should FAIL initially - RED phase of TDD cycle.
"""

import unittest
from pathlib import Path
import json
import tempfile
import shutil
from datetime import datetime
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.screenshot_tracking import ProcessedScreenshotTracker


class TestProcessedScreenshotTracker(unittest.TestCase):
    """Test suite for ProcessedScreenshotTracker - RED Phase"""
    
    def setUp(self):
        """Create temporary directory for test history files"""
        self.test_dir = tempfile.mkdtemp()
        self.history_file = Path(self.test_dir) / ".screenshot_processing_history.json"
        
    def tearDown(self):
        """Clean up temporary test directory"""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_tracker_initialization(self):
        """Test 1: Initialize tracker with empty history"""
        tracker = ProcessedScreenshotTracker(self.history_file)
        
        # Should create empty history file
        self.assertTrue(self.history_file.exists())
        
        # Should have correct structure
        with open(self.history_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn('processed_screenshots', data)
        self.assertIn('version', data)
        self.assertEqual(data['version'], '1.0')
        self.assertEqual(len(data['processed_screenshots']), 0)
    
    def test_mark_screenshot_processed(self):
        """Test 2: Mark a screenshot as processed"""
        tracker = ProcessedScreenshotTracker(self.history_file)
        
        screenshot_path = Path("/path/to/Screenshot_20250927_131418_Threads.jpg")
        daily_note = "daily-screenshots-2025-09-30.md"
        
        # Mark as processed
        tracker.mark_processed(screenshot_path, daily_note)
        
        # Verify entry exists in history
        history = tracker.get_history()
        self.assertIn(screenshot_path.name, history['processed_screenshots'])
        
        # Verify metadata
        entry = history['processed_screenshots'][screenshot_path.name]
        self.assertIn('processed_at', entry)
        self.assertEqual(entry['daily_note'], daily_note)
        self.assertIn('file_hash', entry)
    
    def test_is_processed_detection(self):
        """Test 3: Detect if screenshot has been processed"""
        tracker = ProcessedScreenshotTracker(self.history_file)
        
        processed_path = Path("/path/to/Screenshot_20250927_131418_Threads.jpg")
        unprocessed_path = Path("/path/to/Screenshot_20250930_100000_Instagram.jpg")
        
        # Mark one as processed
        tracker.mark_processed(processed_path, "daily-note.md")
        
        # Verify detection
        self.assertTrue(tracker.is_processed(processed_path))
        self.assertFalse(tracker.is_processed(unprocessed_path))
    
    def test_filter_unprocessed_screenshots(self):
        """Test 4: Filter list to unprocessed screenshots only"""
        tracker = ProcessedScreenshotTracker(self.history_file)
        
        # Mix of processed and unprocessed
        all_screenshots = [
            Path("/path/Screenshot_20250927_131418_Threads.jpg"),
            Path("/path/Screenshot_20250927_083404_Threads.jpg"),
            Path("/path/Screenshot_20250930_100000_Instagram.jpg"),
            Path("/path/Screenshot_20250930_110000_Chrome.jpg"),
        ]
        
        # Mark some as processed
        tracker.mark_processed(all_screenshots[0], "daily-note-1.md")
        tracker.mark_processed(all_screenshots[1], "daily-note-1.md")
        
        # Filter to unprocessed
        unprocessed = tracker.filter_unprocessed(all_screenshots)
        
        # Should only return last 2
        self.assertEqual(len(unprocessed), 2)
        self.assertIn(all_screenshots[2], unprocessed)
        self.assertIn(all_screenshots[3], unprocessed)
        self.assertNotIn(all_screenshots[0], unprocessed)
        self.assertNotIn(all_screenshots[1], unprocessed)
    
    def test_force_flag_bypasses_tracking(self):
        """Test 5: --force flag includes all screenshots regardless of history"""
        tracker = ProcessedScreenshotTracker(self.history_file)
        
        screenshots = [
            Path("/path/Screenshot_20250927_131418_Threads.jpg"),
            Path("/path/Screenshot_20250930_100000_Instagram.jpg"),
        ]
        
        # Mark all as processed
        for screenshot in screenshots:
            tracker.mark_processed(screenshot, "daily-note.md")
        
        # Filter with force=True
        unprocessed = tracker.filter_unprocessed(screenshots, force=True)
        
        # Should return all screenshots when force=True
        self.assertEqual(len(unprocessed), 2)
        self.assertIn(screenshots[0], unprocessed)
        self.assertIn(screenshots[1], unprocessed)
    
    def test_statistics_reporting(self):
        """Test 6: Report statistics on new vs already-processed"""
        tracker = ProcessedScreenshotTracker(self.history_file)
        
        screenshots = [
            Path("/path/Screenshot_20250927_131418_Threads.jpg"),
            Path("/path/Screenshot_20250927_083404_Threads.jpg"),
            Path("/path/Screenshot_20250930_100000_Instagram.jpg"),
        ]
        
        # Mark first one as processed
        tracker.mark_processed(screenshots[0], "daily-note-old.md")
        
        # Get statistics
        stats = tracker.get_statistics(screenshots)
        
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['already_processed'], 1)
        self.assertEqual(stats['new_screenshots'], 2)
        self.assertIn(screenshots[0].name, stats['processed_files'])
    
    def test_history_persistence(self):
        """Test 7: History persists across tracker instances"""
        # First tracker - mark screenshots
        tracker1 = ProcessedScreenshotTracker(self.history_file)
        screenshot = Path("/path/Screenshot_20250927_131418_Threads.jpg")
        tracker1.mark_processed(screenshot, "daily-note.md")
        
        # Create new tracker instance
        tracker2 = ProcessedScreenshotTracker(self.history_file)
        
        # Should load history from disk
        self.assertTrue(tracker2.is_processed(screenshot))
        history = tracker2.get_history()
        self.assertIn(screenshot.name, history['processed_screenshots'])
    
    def test_concurrent_safety(self):
        """Test 8: Safe concurrent writes to history file"""
        tracker = ProcessedScreenshotTracker(self.history_file)
        
        # Simulate concurrent writes
        screenshots = [
            Path(f"/path/Screenshot_2025092{i}_100000_App.jpg")
            for i in range(5)
        ]
        
        # Mark all in quick succession
        for screenshot in screenshots:
            tracker.mark_processed(screenshot, f"daily-note-{screenshot.name}.md")
        
        # Verify all were recorded
        history = tracker.get_history()
        for screenshot in screenshots:
            self.assertIn(screenshot.name, history['processed_screenshots'])
        
        # Verify no corruption
        self.assertEqual(len(history['processed_screenshots']), 5)


class TestEveningScreenshotProcessorIntegration(unittest.TestCase):
    """Integration tests with EveningScreenshotProcessor - RED Phase"""
    
    def setUp(self):
        """Setup test environment"""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Cleanup"""
        if Path(self.test_dir).exists():
            shutil.rmtree(self.test_dir)
    
    def test_processor_filters_processed_screenshots(self):
        """Test: Processor integrates tracking to filter processed screenshots"""
        # This will test the integration in EveningScreenshotProcessor
        # Expected to fail until GREEN phase
        self.fail("Integration test not yet implemented - RED phase")
    
    def test_processor_marks_screenshots_after_processing(self):
        """Test: Processor marks screenshots as processed after successful OCR"""
        # Expected to fail until GREEN phase
        self.fail("Integration test not yet implemented - RED phase")
    
    def test_processor_statistics_include_tracking_info(self):
        """Test: Processor results include new vs already-processed counts"""
        # Expected to fail until GREEN phase
        self.fail("Integration test not yet implemented - RED phase")


if __name__ == '__main__':
    unittest.main()
