#!/usr/bin/env python3
"""
TDD Iteration 9 - RED Phase: Multi-Device Screenshot Detection Tests
Testing device pattern detection for Samsung S23 and iPad screenshots
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from src.cli.multi_device_detector import MultiDeviceDetector, DeviceType


class TestSamsungS23Detection:
    """Test Samsung S23 screenshot detection and metadata extraction"""
    
    def test_detect_samsung_s23_from_filename(self):
        """Should identify Samsung S23 from Screenshot_YYYYMMDD_HHMMSS_AppName.jpg pattern"""
        # Arrange
        detector = MultiDeviceDetector()
        samsung_screenshots = [
            Path("Screenshot_20250926_095442_Innerview.jpg"),
            Path("Screenshot_20250810_143028_Chrome.jpg"),
            Path("Screenshot_20251001_183045_Threads.jpg"),
        ]
        
        # Act & Assert
        for screenshot in samsung_screenshots:
            device_type = detector.detect_device(screenshot)
            assert device_type == DeviceType.SAMSUNG_S23, \
                f"Failed to detect Samsung S23 from {screenshot.name}"
    
    def test_extract_samsung_timestamp_from_filename(self):
        """Should extract YYYYMMDD_HHMMSS timestamp from Samsung screenshot filename"""
        # Arrange
        detector = MultiDeviceDetector()
        test_cases = [
            {
                'filename': Path("Screenshot_20250926_095442_Innerview.jpg"),
                'expected': datetime(2025, 9, 26, 9, 54, 42)
            },
            {
                'filename': Path("Screenshot_20250810_143028_Chrome.jpg"),
                'expected': datetime(2025, 8, 10, 14, 30, 28)
            },
            {
                'filename': Path("Screenshot_20251001_183045_Threads.jpg"),
                'expected': datetime(2025, 10, 1, 18, 30, 45)
            },
        ]
        
        # Act & Assert
        for test_case in test_cases:
            timestamp = detector.extract_timestamp(test_case['filename'])
            assert timestamp == test_case['expected'], \
                f"Failed to extract timestamp from {test_case['filename'].name}. " \
                f"Expected {test_case['expected']}, got {timestamp}"
    
    def test_extract_samsung_app_name_from_filename(self):
        """Should extract app name from Samsung screenshot filename"""
        # Arrange
        detector = MultiDeviceDetector()
        test_cases = [
            {
                'filename': Path("Screenshot_20250926_095442_Innerview.jpg"),
                'expected_app': 'Innerview'
            },
            {
                'filename': Path("Screenshot_20250810_143028_Chrome.jpg"),
                'expected_app': 'Chrome'
            },
            {
                'filename': Path("Screenshot_20251001_183045_Threads.jpg"),
                'expected_app': 'Threads'
            },
        ]
        
        # Act & Assert
        for test_case in test_cases:
            metadata = detector.extract_metadata(test_case['filename'])
            assert 'app_name' in metadata, \
                f"Missing app_name in metadata for {test_case['filename'].name}"
            assert metadata['app_name'] == test_case['expected_app'], \
                f"Failed to extract app name from {test_case['filename'].name}. " \
                f"Expected {test_case['expected_app']}, got {metadata.get('app_name')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
