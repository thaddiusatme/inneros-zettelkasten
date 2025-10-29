#!/usr/bin/env python3
"""
Multi-Device Screenshot Detection System
Detects device type and extracts metadata from screenshot filenames

REFACTORED: Now uses modular utility classes for cleaner architecture
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from .multi_device_detector_utils import (
    DeviceType,
    DevicePatternMatcher,
    TimestampExtractor,
    DeviceMetadataBuilder,
)


class MultiDeviceDetector:
    """
    Detect device type and extract metadata from screenshot filenames

    Supports:
    - Samsung S23: Screenshot_YYYYMMDD_HHMMSS_AppName.jpg
    - iPad: YYYYMMDD_HHMMSS000_iOS.png
    - Unknown: Any other pattern

    Architecture:
    - DevicePatternMatcher: Regex pattern matching
    - TimestampExtractor: Device-specific timestamp parsing
    - DeviceMetadataBuilder: Unified metadata construction

    Example:
        >>> detector = MultiDeviceDetector()
        >>> path = Path("Screenshot_20250926_095442_Innerview.jpg")
        >>> device_type = detector.detect_device(path)
        >>> print(device_type)
        DeviceType.SAMSUNG_S23
        >>> metadata = detector.extract_metadata(path)
        >>> print(metadata['device_name'])
        Samsung Galaxy S23
    """

    def __init__(self):
        """
        Initialize multi-device detector with utility classes

        Sets up pattern matcher, timestamp extractor, and metadata builder
        for modular device detection and metadata extraction
        """
        self.pattern_matcher = DevicePatternMatcher()
        self.timestamp_extractor = TimestampExtractor(self.pattern_matcher)
        self.metadata_builder = DeviceMetadataBuilder(
            self.pattern_matcher, self.timestamp_extractor
        )

    def detect_device(self, file_path: Path) -> DeviceType:
        """
        Detect device type from filename pattern

        Args:
            file_path: Path to screenshot file

        Returns:
            DeviceType enum (SAMSUNG_S23, IPAD, or UNKNOWN)

        Example:
            >>> detector = MultiDeviceDetector()
            >>> detector.detect_device(Path("Screenshot_20250926_095442_Chrome.jpg"))
            DeviceType.SAMSUNG_S23
            >>> detector.detect_device(Path("20250926_221840000_iOS.png"))
            DeviceType.IPAD
        """
        return self.pattern_matcher.detect_device_type(file_path.name)

    def extract_timestamp(self, file_path: Path) -> Optional[datetime]:
        """
        Extract timestamp from filename using device-specific parsing

        Args:
            file_path: Path to screenshot file

        Returns:
            datetime object or None if cannot extract

        Example:
            >>> detector = MultiDeviceDetector()
            >>> ts = detector.extract_timestamp(Path("Screenshot_20250926_095442_Chrome.jpg"))
            >>> print(ts)
            2025-09-26 09:54:42
        """
        device_type = self.detect_device(file_path)
        return self.timestamp_extractor.extract(file_path.name, device_type)

    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract all device-specific metadata

        Args:
            file_path: Path to screenshot file

        Returns:
            Dictionary with unified metadata structure:
            - device_type: Device identifier (samsung_s23, ipad, unknown)
            - device_name: Human-readable device name
            - source_file: Original filename
            - timestamp: Extracted datetime or None
            - app_name: (Samsung only) Application name

        Example:
            >>> detector = MultiDeviceDetector()
            >>> metadata = detector.extract_metadata(Path("Screenshot_20250926_095442_Chrome.jpg"))
            >>> print(metadata['device_name'])
            Samsung Galaxy S23
            >>> print(metadata['app_name'])
            Chrome
        """
        device_type = self.detect_device(file_path)
        timestamp = self.extract_timestamp(file_path)
        return self.metadata_builder.build(file_path, device_type, timestamp)
