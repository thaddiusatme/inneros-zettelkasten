"""
Tests for CaptureMatcherPOC - Core filename timestamp parsing

Test-Driven Development (TDD) - RED Phase
Testing Samsung S23 filename patterns:
- Screenshot_YYYYMMDD_HHMMSS.png
- Recording_YYYYMMDD_HHMMSS.m4a
"""

from datetime import datetime
import sys
import os

# Add development directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from development.capture_matcher import CaptureMatcherPOC


class TestCaptureMatcherPOC:
    """Test suite for core timestamp parsing functionality"""
    
    def test_parse_samsung_screenshot_timestamp(self):
        """Test parsing Samsung S23 screenshot filename timestamps"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Test valid Samsung screenshot pattern
        timestamp = matcher.parse_filename_timestamp("Screenshot_20250122_143512.png")
        expected = datetime(2025, 1, 22, 14, 35, 12)
        assert timestamp == expected, f"Expected {expected}, got {timestamp}"
        
        # Test another valid screenshot
        timestamp = matcher.parse_filename_timestamp("Screenshot_20250915_092034.png")
        expected = datetime(2025, 9, 15, 9, 20, 34)
        assert timestamp == expected, f"Expected {expected}, got {timestamp}"
    
    def test_parse_samsung_voice_timestamp(self):
        """Test parsing Samsung voice recording filename timestamps"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Test valid Samsung voice recording pattern
        timestamp = matcher.parse_filename_timestamp("Recording_20250122_143528.m4a")
        expected = datetime(2025, 1, 22, 14, 35, 28)
        assert timestamp == expected, f"Expected {expected}, got {timestamp}"
        
        # Test another valid recording
        timestamp = matcher.parse_filename_timestamp("Recording_20250915_092156.m4a")
        expected = datetime(2025, 9, 15, 9, 21, 56)
        assert timestamp == expected, f"Expected {expected}, got {timestamp}"
    
    def test_parse_invalid_filename_patterns(self):
        """Test handling of invalid or unrecognized filename patterns"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Test various invalid patterns
        invalid_files = [
            "random_file.png",
            "Screenshot_invalid_format.png", 
            "Recording_20250122.m4a",  # Missing time
            "Screenshot_2025_01_22.png",  # Wrong date format
            "IMG_1234.jpg",  # iPhone pattern (not supported yet)
            "",  # Empty string
            "Screenshot_20251301_143512.png",  # Invalid date (month 13)
            "Recording_20250122_256078.m4a"  # Invalid time (hour 25)
        ]
        
        for invalid_file in invalid_files:
            timestamp = matcher.parse_filename_timestamp(invalid_file)
            assert timestamp is None, f"Expected None for {invalid_file}, got {timestamp}"
    
    def test_match_screenshot_voice_pairs_within_threshold(self):
        """Test matching screenshot and voice pairs within time threshold"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Create sample file data with timestamps
        captures = [
            {"filename": "Screenshot_20250122_143512.png", "type": "screenshot", "path": "/fake/screenshots/Screenshot_20250122_143512.png"},
            {"filename": "Recording_20250122_143528.m4a", "type": "voice", "path": "/fake/voice/Recording_20250122_143528.m4a"},
            {"filename": "Screenshot_20250122_144000.png", "type": "screenshot", "path": "/fake/screenshots/Screenshot_20250122_144000.png"}
        ]
        
        matches = matcher.match_by_timestamp(captures)
        
        # Should find one matched pair (16 second gap, within 60 second threshold)
        assert len(matches["paired"]) == 1, f"Expected 1 pair, got {len(matches['paired'])}"
        assert len(matches["unpaired_screenshots"]) == 1, f"Expected 1 unpaired screenshot, got {len(matches['unpaired_screenshots'])}"
        assert len(matches["unpaired_voice"]) == 0, f"Expected 0 unpaired voice notes, got {len(matches['unpaired_voice'])}"
        
        # Verify the matched pair details
        pair = matches["paired"][0]
        assert "Screenshot_20250122_143512.png" in pair["screenshot"]["filename"]
        assert "Recording_20250122_143528.m4a" in pair["voice"]["filename"]
        assert pair["time_gap_seconds"] == 16
    
    def test_match_screenshot_voice_pairs_outside_threshold(self):
        """Test handling of screenshot and voice pairs outside time threshold"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Create sample file data with timestamps > 60 seconds apart
        captures = [
            {"filename": "Screenshot_20250122_143512.png", "type": "screenshot", "path": "/fake/screenshots/Screenshot_20250122_143512.png"},
            {"filename": "Recording_20250122_144612.m4a", "type": "voice", "path": "/fake/voice/Recording_20250122_144612.m4a"}  # 11 minutes later
        ]
        
        matches = matcher.match_by_timestamp(captures)
        
        # Should find no matches (gap too large)
        assert len(matches["paired"]) == 0, f"Expected 0 pairs, got {len(matches['paired'])}"
        assert len(matches["unpaired_screenshots"]) == 1, f"Expected 1 unpaired screenshot, got {len(matches['unpaired_screenshots'])}"
        assert len(matches["unpaired_voice"]) == 1, f"Expected 1 unpaired voice note, got {len(matches['unpaired_voice'])}"
    
    def test_match_multiple_rapid_captures(self):
        """Test matching logic with multiple rapid captures (edge case handling)"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Simulate multiple screenshots close together with fewer voice notes
        captures = [
            {"filename": "Screenshot_20250122_143512.png", "type": "screenshot", "path": "/fake/screenshots/Screenshot_20250122_143512.png"},
            {"filename": "Screenshot_20250122_143542.png", "type": "screenshot", "path": "/fake/screenshots/Screenshot_20250122_143542.png"},
            {"filename": "Screenshot_20250122_143601.png", "type": "screenshot", "path": "/fake/screenshots/Screenshot_20250122_143601.png"},
            {"filename": "Recording_20250122_143528.m4a", "type": "voice", "path": "/fake/voice/Recording_20250122_143528.m4a"},
            {"filename": "Recording_20250122_143615.m4a", "type": "voice", "path": "/fake/voice/Recording_20250122_143615.m4a"}
        ]
        
        matches = matcher.match_by_timestamp(captures)
        
        # Should find 2 pairs (closest timestamp matching)
        assert len(matches["paired"]) == 2, f"Expected 2 pairs, got {len(matches['paired'])}"
        assert len(matches["unpaired_screenshots"]) == 1, f"Expected 1 unpaired screenshot, got {len(matches['unpaired_screenshots'])}"
        assert len(matches["unpaired_voice"]) == 0, f"Expected 0 unpaired voice notes, got {len(matches['unpaired_voice'])}"
        
        # Verify closest timestamp pairing logic
        pair_gaps = [pair["time_gap_seconds"] for pair in matches["paired"]]
        assert all(gap <= 60 for gap in pair_gaps), f"All gaps should be within threshold, got {pair_gaps}"
    
    def test_capture_matcher_initialization(self):
        """Test CaptureMatcherPOC initialization with paths"""
        screenshot_path = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Gallery/DCIM/Screenshots"
        voice_path = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal/Voice Recorder"
        
        matcher = CaptureMatcherPOC(screenshot_path, voice_path)
        
        assert matcher.screenshots_dir == screenshot_path
        assert matcher.voice_dir == voice_path
        assert matcher.match_threshold == 60  # Default threshold in seconds
    
    def test_timestamp_edge_cases(self):
        """Test edge cases in timestamp parsing"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Test end of year/month boundaries
        timestamp = matcher.parse_filename_timestamp("Screenshot_20241231_235959.png")
        expected = datetime(2024, 12, 31, 23, 59, 59)
        assert timestamp == expected, f"Expected {expected}, got {timestamp}"
        
        # Test beginning of year
        timestamp = matcher.parse_filename_timestamp("Recording_20250101_000001.m4a")
        expected = datetime(2025, 1, 1, 0, 0, 1)
        assert timestamp == expected, f"Expected {expected}, got {timestamp}"
