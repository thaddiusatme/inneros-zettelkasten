"""
TDD Tests for OneDrive Integration in CaptureMatcherPOC
RED Phase - Failing tests for scan_onedrive_captures() functionality

Tests the OneDrive file discovery system that scans actual Samsung S23
capture files from OneDrive sync directories and validates pairing accuracy.
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from datetime import datetime, timedelta
import sys
import os
import re
import pytest

# Add development directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from capture_matcher import CaptureMatcherPOC


@pytest.mark.integration
@pytest.mark.slow_integration  # External OneDrive API
class TestOneDriveIntegration(unittest.TestCase):
    """Test OneDrive file discovery and Samsung capture scanning"""
    
    def setUp(self):
        """Set up test fixtures with real OneDrive paths"""
        self.onedrive_screenshots = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Galaxy/DCIM/Screenshots"
        self.onedrive_voice = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal/Voice Recorder"
        
        self.matcher = CaptureMatcherPOC(self.onedrive_screenshots, self.onedrive_voice)
    
    def test_scan_onedrive_captures_method_exists(self):
        """RED: scan_onedrive_captures() method should exist"""
        # This test will fail because the method doesn't exist yet
        self.assertTrue(hasattr(self.matcher, 'scan_onedrive_captures'),
                       "CaptureMatcherPOC should have scan_onedrive_captures method")
    
    def test_scan_onedrive_captures_returns_structured_data(self):
        """RED: Method should return structured capture data"""
        # This will fail because method doesn't exist
        result = self.matcher.scan_onedrive_captures()
        
        # Expected structure from OneDrive scanning
        expected_keys = ['screenshots', 'voice_notes', 'scan_stats', 'errors']
        for key in expected_keys:
            self.assertIn(key, result, f"Result should contain {key}")
    
    def test_scan_with_date_range_filtering(self):
        """RED: Should support date range filtering (7-day default)"""
        # Test 7-day lookback default
        result = self.matcher.scan_onedrive_captures(days_back=7)
        self.assertIsInstance(result, dict)
        
        # Test custom date range
        start_date = datetime.now() - timedelta(days=3)
        end_date = datetime.now()
        result = self.matcher.scan_onedrive_captures(start_date=start_date, end_date=end_date)
        self.assertIsInstance(result, dict)
    
    def test_handle_missing_onedrive_directories(self):
        """RED: Should handle missing OneDrive directories gracefully"""
        # Test with non-existent paths
        fake_matcher = CaptureMatcherPOC("/fake/screenshots/path", "/fake/voice/path")
        
        result = fake_matcher.scan_onedrive_captures()
        
        # Should return error information instead of crashing
        self.assertIn('errors', result)
        self.assertTrue(len(result['errors']) > 0)
    
    def test_samsung_filename_pattern_validation_in_real_files(self):
        """RED: Should validate Samsung patterns in real OneDrive files"""
        result = self.matcher.scan_onedrive_captures()
        
        # Should find at least some Samsung files if OneDrive sync is working
        total_files = len(result['screenshots']) + len(result['voice_notes'])
        self.assertGreater(total_files, 0, "Should find some Samsung capture files")
        
        # Validate filename patterns in found files
        for screenshot in result['screenshots']:
            # Accept both .jpg and .png screenshots
            self.assertRegex(screenshot['filename'], 
                           r'^Screenshot_\d{8}_\d{6}.*\.(jpg|png)$',
                           "Screenshots should match Samsung pattern")
        
        for voice in result['voice_notes']:
            # Accept both Samsung and OneDrive voice patterns
            samsung_pattern = r'^Recording_\d{8}_\d{6}\.m4a$'
            onedrive_pattern = r'^Voice \d{6}_\d{6}\.m4a$'
            
            matches_pattern = (
                re.match(samsung_pattern, voice['filename']) or 
                re.match(onedrive_pattern, voice['filename'])
            )
            self.assertTrue(matches_pattern, 
                           f"Voice recording {voice['filename']} should match Samsung or OneDrive pattern")
    
    def test_file_metadata_extraction(self):
        """RED: Should extract file metadata (path, size, modified time)"""
        result = self.matcher.scan_onedrive_captures()
        
        if result['screenshots']:
            screenshot = result['screenshots'][0]
            required_fields = ['filename', 'path', 'size', 'modified_time', 'type']
            for field in required_fields:
                self.assertIn(field, screenshot, f"Screenshot should have {field}")
    
    def test_sync_latency_measurement(self):
        """RED: Should measure OneDrive sync timing"""
        result = self.matcher.scan_onedrive_captures()
        
        # Should include sync timing information
        self.assertIn('scan_stats', result)
        stats = result['scan_stats']
        
        required_stats = ['scan_duration', 'files_processed', 'sync_latency_check']
        for stat in required_stats:
            self.assertIn(stat, stats, f"Scan stats should include {stat}")
    
    def test_performance_under_30_seconds(self):
        """RED: Should process typical daily volume (<30 seconds)"""
        import time
        
        start_time = time.time()
        result = self.matcher.scan_onedrive_captures(days_back=1)  # Typical daily volume
        end_time = time.time()
        
        processing_time = end_time - start_time
        self.assertLess(processing_time, 30, 
                       f"Should process daily captures in <30s, took {processing_time:.2f}s")
    
    def test_configure_onedrive_paths_method(self):
        """RED: Should support OneDrive path configuration"""
        # This will fail because method doesn't exist
        new_screenshot_path = "/custom/screenshots/path"
        new_voice_path = "/custom/voice/path"
        
        self.matcher.configure_onedrive_paths(new_screenshot_path, new_voice_path)
        
        # Verify paths were updated
        self.assertEqual(self.matcher.screenshots_dir, new_screenshot_path)
        self.assertEqual(self.matcher.voice_dir, new_voice_path)
    
    def test_real_world_pairing_accuracy_validation(self):
        """RED: Should achieve >90% pairing accuracy with real files"""
        result = self.matcher.scan_onedrive_captures(days_back=7)
        
        # Get all captures for matching
        all_captures = []
        for screenshot in result['screenshots']:
            all_captures.append({**screenshot, 'type': 'screenshot'})
        for voice in result['voice_notes']:
            all_captures.append({**voice, 'type': 'voice'})
        
        # Test pairing accuracy
        matches = self.matcher.match_by_timestamp(all_captures)
        
        total_screenshots = len(result['screenshots'])
        paired_screenshots = len(matches['paired'])
        
        if total_screenshots > 0:
            pairing_accuracy = paired_screenshots / total_screenshots
            self.assertGreater(pairing_accuracy, 0.90,
                             f"Pairing accuracy {pairing_accuracy:.2%} should be >90%")


if __name__ == '__main__':
    # Run the failing tests to establish RED phase
    unittest.main(verbosity=2)
