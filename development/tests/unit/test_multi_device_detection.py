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


class TestIPadDetection:
    """Test iPad screenshot detection and metadata extraction"""

    def test_detect_ipad_from_filename(self):
        """Should identify iPad from YYYYMMDD_HHMMSS000_iOS.png pattern"""
        # Arrange
        detector = MultiDeviceDetector()
        ipad_screenshots = [
            Path("20250926_221840000_iOS.png"),
            Path("20250901_042410000_iOS.png"),
            Path("20250305_190004000_iOS.png"),
        ]

        # Act & Assert
        for screenshot in ipad_screenshots:
            device_type = detector.detect_device(screenshot)
            assert device_type == DeviceType.IPAD, \
                f"Failed to detect iPad from {screenshot.name}"

    def test_extract_ipad_timestamp_from_filename(self):
        """Should extract YYYYMMDD_HHMMSS from iPad filename (ignore 000 milliseconds)"""
        # Arrange
        detector = MultiDeviceDetector()
        test_cases = [
            {
                'filename': Path("20250926_221840000_iOS.png"),
                'expected': datetime(2025, 9, 26, 22, 18, 40)
            },
            {
                'filename': Path("20250901_042410000_iOS.png"),
                'expected': datetime(2025, 9, 1, 4, 24, 10)
            },
            {
                'filename': Path("20250305_190004000_iOS.png"),
                'expected': datetime(2025, 3, 5, 19, 0, 4)
            },
        ]

        # Act & Assert
        for test_case in test_cases:
            timestamp = detector.extract_timestamp(test_case['filename'])
            assert timestamp == test_case['expected'], \
                f"Failed to extract timestamp from {test_case['filename'].name}. " \
                f"Expected {test_case['expected']}, got {timestamp}"

    def test_ipad_metadata_does_not_include_app_name(self):
        """iPad screenshots should not have app_name field (not available in filename)"""
        # Arrange
        detector = MultiDeviceDetector()
        ipad_screenshot = Path("20250926_221840000_iOS.png")

        # Act
        metadata = detector.extract_metadata(ipad_screenshot)

        # Assert
        assert 'app_name' not in metadata or metadata['app_name'] is None, \
            f"iPad screenshots should not have app_name, but got: {metadata.get('app_name')}"


class TestUnifiedMetadata:
    """Test unified metadata structure across devices"""

    def test_normalize_device_metadata_samsung(self):
        """Should create unified metadata dict for Samsung screenshots"""
        # Arrange
        detector = MultiDeviceDetector()
        samsung_screenshot = Path("Screenshot_20250926_095442_Innerview.jpg")

        # Act
        metadata = detector.extract_metadata(samsung_screenshot)

        # Assert - Check required fields
        assert 'device_type' in metadata, "Missing device_type field"
        assert metadata['device_type'] == DeviceType.SAMSUNG_S23.value
        assert 'device_name' in metadata, "Missing device_name field"
        assert metadata['device_name'] == "Samsung Galaxy S23"
        assert 'source_file' in metadata, "Missing source_file field"
        assert 'timestamp' in metadata, "Missing timestamp field"
        assert isinstance(metadata['timestamp'], datetime), "timestamp should be datetime object"

    def test_normalize_device_metadata_ipad(self):
        """Should create unified metadata dict for iPad screenshots"""
        # Arrange
        detector = MultiDeviceDetector()
        ipad_screenshot = Path("20250926_221840000_iOS.png")

        # Act
        metadata = detector.extract_metadata(ipad_screenshot)

        # Assert - Check required fields
        assert 'device_type' in metadata, "Missing device_type field"
        assert metadata['device_type'] == DeviceType.IPAD.value
        assert 'device_name' in metadata, "Missing device_name field"
        assert metadata['device_name'] == "iPad"
        assert 'source_file' in metadata, "Missing source_file field"
        assert 'timestamp' in metadata, "Missing timestamp field"
        assert isinstance(metadata['timestamp'], datetime), "timestamp should be datetime object"


class TestUnknownDeviceHandling:
    """Test graceful handling of unknown/unrecognized file patterns"""

    def test_handle_unknown_device_gracefully(self):
        """Should return UNKNOWN device type for unrecognized patterns without crashing"""
        # Arrange
        detector = MultiDeviceDetector()
        unknown_files = [
            Path("random_file.jpg"),
            Path("IMG_1234.png"),  # iOS Camera Roll, not screenshot pattern
            Path("DJI_20240831_113357_59.jpg"),  # Drone photo
            Path("document.pdf"),
        ]

        # Act & Assert
        for unknown_file in unknown_files:
            device_type = detector.detect_device(unknown_file)
            assert device_type == DeviceType.UNKNOWN, \
                f"Should detect {unknown_file.name} as UNKNOWN device"

    def test_unknown_device_returns_none_timestamp(self):
        """Unknown devices should return None for timestamp (cannot extract)"""
        # Arrange
        detector = MultiDeviceDetector()
        unknown_file = Path("random_file.jpg")

        # Act
        timestamp = detector.extract_timestamp(unknown_file)

        # Assert
        assert timestamp is None, \
            f"Unknown devices should return None timestamp, got {timestamp}"

    def test_unknown_device_metadata_includes_type(self):
        """Unknown devices should still return metadata dict with device_type"""
        # Arrange
        detector = MultiDeviceDetector()
        unknown_file = Path("random_file.jpg")

        # Act
        metadata = detector.extract_metadata(unknown_file)

        # Assert
        assert 'device_type' in metadata, "Unknown devices should have device_type"
        assert metadata['device_type'] == DeviceType.UNKNOWN.value
        assert 'source_file' in metadata, "Unknown devices should have source_file"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
