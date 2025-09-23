"""
Tests for CaptureMatcherPOC - Core filename timestamp parsing + Interactive CLI

Test-Driven Development (TDD) - RED Phase for Interactive CLI
Testing Samsung S23 filename patterns:
- Screenshot_YYYYMMDD_HHMMSS.png
- Recording_YYYYMMDD_HHMMSS.m4a

NEW: Interactive CLI Features
- interactive_review_captures() method
- User input handling (k/s/d + Enter)
- Progress tracking and session state
"""

from datetime import datetime
import sys
import os
from unittest.mock import patch
from io import StringIO

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


class TestInteractiveCLI:
    """Test suite for Interactive CLI features - TDD RED PHASE"""
    
    def test_interactive_review_captures_method_exists(self):
        """Test that interactive_review_captures method exists"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # This should fail - method doesn't exist yet
        assert hasattr(matcher, 'interactive_review_captures'), "interactive_review_captures method should exist"
    
    @patch('builtins.input', side_effect=['k', 's', 'd', 'q'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_interactive_review_basic_user_input(self, mock_stdout, mock_input):
        """Test basic user input handling (k/s/d/q commands)"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        # Sample matched pairs data
        matched_pairs = [
            {
                "screenshot": {"filename": "Screenshot_20250122_143512.png", "path": "/fake/1.png"},
                "voice": {"filename": "Recording_20250122_143528.m4a", "path": "/fake/1.m4a"},
                "time_gap_seconds": 16
            },
            {
                "screenshot": {"filename": "Screenshot_20250122_144000.png", "path": "/fake/2.png"},
                "voice": {"filename": "Recording_20250122_144015.m4a", "path": "/fake/2.m4a"},
                "time_gap_seconds": 15
            }
        ]
        
        # This should fail - method doesn't exist yet
        result = matcher.interactive_review_captures(matched_pairs)
        
        # Verify result structure
        assert 'kept' in result, "Result should contain 'kept' key"
        assert 'skipped' in result, "Result should contain 'skipped' key"
        assert 'deleted' in result, "Result should contain 'deleted' key"
        assert 'session_stats' in result, "Result should contain 'session_stats' key"
    
    @patch('builtins.input', side_effect=['k'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_capture_pair_display_formatting(self, mock_stdout, mock_input):
        """Test that capture pairs are displayed with proper formatting"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        matched_pair = {
            "screenshot": {"filename": "Screenshot_20250122_143512.png", "path": "/fake/1.png"},
            "voice": {"filename": "Recording_20250122_143528.m4a", "path": "/fake/1.m4a"},
            "time_gap_seconds": 16
        }
        
        # This should fail - method doesn't exist yet
        matcher.interactive_review_captures([matched_pair])
        
        output = mock_stdout.getvalue()
        
        # Verify display formatting
        assert "📸" in output or "Screenshot" in output, "Should display screenshot info with emoji"
        assert "🎤" in output or "Recording" in output, "Should display voice info with emoji"
        assert "16" in output, "Should display time gap"
        assert "[k]eep" in output or "keep" in output.lower(), "Should show keep option"
        assert "[s]kip" in output or "skip" in output.lower(), "Should show skip option"
        assert "[d]elete" in output or "delete" in output.lower(), "Should show delete option"
    
    @patch('builtins.input', side_effect=['k', 's', 'q'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_progress_tracking_display(self, mock_stdout, mock_input):
        """Test that progress is tracked and displayed during review"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        matched_pairs = [
            {
                "screenshot": {"filename": "Screenshot_20250122_143512.png", "path": "/fake/1.png"},
                "voice": {"filename": "Recording_20250122_143528.m4a", "path": "/fake/1.m4a"},
                "time_gap_seconds": 16
            },
            {
                "screenshot": {"filename": "Screenshot_20250122_144000.png", "path": "/fake/2.png"},
                "voice": {"filename": "Recording_20250122_144015.m4a", "path": "/fake/2.m4a"},
                "time_gap_seconds": 15
            }
        ]
        
        # This should fail - method doesn't exist yet
        result = matcher.interactive_review_captures(matched_pairs)
        
        output = mock_stdout.getvalue()
        
        # Verify progress tracking
        assert "1/2" in output or "(1 of 2)" in output, "Should show current item progress"
        assert "2/2" in output or "(2 of 2)" in output, "Should show final item progress"
        
        # Verify session stats
        assert result['session_stats']['total_reviewed'] == 2, "Should track total reviewed"
        assert result['session_stats']['kept_count'] == 1, "Should track kept count"
        assert result['session_stats']['skipped_count'] == 1, "Should track skipped count"
    
    @patch('builtins.input', side_effect=['invalid', 'k'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_input_handling(self, mock_stdout, mock_input):
        """Test handling of invalid user input with helpful error messages"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        matched_pair = {
            "screenshot": {"filename": "Screenshot_20250122_143512.png", "path": "/fake/1.png"},
            "voice": {"filename": "Recording_20250122_143528.m4a", "path": "/fake/1.m4a"},
            "time_gap_seconds": 16
        }
        
        # This should fail - method doesn't exist yet
        matcher.interactive_review_captures([matched_pair])
        
        output = mock_stdout.getvalue()
        
        # Verify invalid input handling
        assert "invalid" in output.lower() or "error" in output.lower(), "Should show error for invalid input"
        assert "try again" in output.lower() or "please enter" in output.lower(), "Should prompt for valid input"
    
    @patch('builtins.input', side_effect=['h', 'k'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_help_system_display(self, mock_stdout, mock_input):
        """Test help system shows available commands and shortcuts"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        matched_pair = {
            "screenshot": {"filename": "Screenshot_20250122_143512.png", "path": "/fake/1.png"},
            "voice": {"filename": "Recording_20250122_143528.m4a", "path": "/fake/1.m4a"},
            "time_gap_seconds": 16
        }
        
        # This should fail - method doesn't exist yet
        matcher.interactive_review_captures([matched_pair])
        
        output = mock_stdout.getvalue()
        
        # Verify help system
        assert "help" in output.lower(), "Should show help information"
        assert "commands" in output.lower() or "options" in output.lower(), "Should list available commands"
        assert "k" in output and "keep" in output.lower(), "Should explain k command"
        assert "s" in output and "skip" in output.lower(), "Should explain s command"
        assert "d" in output and "delete" in output.lower(), "Should explain d command"
    
    @patch('subprocess.run')
    @patch('builtins.input', side_effect=['v', 'k'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_view_screenshot_external_viewer(self, mock_stdout, mock_input, mock_subprocess):
        """Test 'v' command opens screenshot in external viewer"""
        matcher = CaptureMatcherPOC("/fake/screenshots", "/fake/voice")
        
        matched_pair = {
            "screenshot": {"filename": "Screenshot_20250122_143512.png", "path": "/fake/screenshot.png"},
            "voice": {"filename": "Recording_20250122_143528.m4a", "path": "/fake/voice.m4a"},
            "time_gap_seconds": 16
        }
        
        # Execute interactive review
        result = matcher.interactive_review_captures([matched_pair])
        
        output = mock_stdout.getvalue()
        
        # Verify 'v' command functionality
        assert "opening screenshot" in output.lower() or "viewer" in output.lower(), "Should show view confirmation"
        
        # Verify subprocess called with correct file
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert "/fake/screenshot.png" in str(call_args), "Should open correct screenshot path"
        
        # Verify user can continue after viewing
        assert result['kept'], "Should allow keeping after viewing"
        assert len(result['kept']) == 1, "Should have kept the viewed pair"
