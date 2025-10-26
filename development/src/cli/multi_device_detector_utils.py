#!/usr/bin/env python3
"""
Multi-Device Detection Utility Classes
Extracted from MultiDeviceDetector for modular architecture
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class DeviceType(Enum):
    """Supported device types for screenshot detection"""
    SAMSUNG_S23 = "samsung_s23"
    IPAD = "ipad"
    UNKNOWN = "unknown"


class DevicePatternMatcher:
    """
    Pattern matching logic for device detection
    
    Encapsulates regex patterns and matching logic for different device types
    """

    def __init__(self):
        """Initialize device patterns"""
        self.patterns = {
            DeviceType.SAMSUNG_S23: re.compile(r'^Screenshot_(\d{8})_(\d{6})_(.+)\.jpg$'),
            DeviceType.IPAD: re.compile(r'^(\d{8})_(\d{6})\d{3}_iOS\.png$'),
        }

    def match(self, filename: str, device_type: DeviceType) -> Optional[re.Match]:
        """
        Match filename against device pattern
        
        Args:
            filename: Screenshot filename to match
            device_type: Device type to match against
            
        Returns:
            Match object or None
        """
        if device_type not in self.patterns:
            return None
        return self.patterns[device_type].match(filename)

    def detect_device_type(self, filename: str) -> DeviceType:
        """
        Detect device type from filename
        
        Args:
            filename: Screenshot filename
            
        Returns:
            DeviceType enum
        """
        for device_type in [DeviceType.SAMSUNG_S23, DeviceType.IPAD]:
            if self.match(filename, device_type):
                return device_type
        return DeviceType.UNKNOWN


class TimestampExtractor:
    """
    Device-specific timestamp extraction logic
    
    Parses timestamps from filenames using device-specific formats
    """

    TIMESTAMP_FORMATS = {
        DeviceType.SAMSUNG_S23: '%Y%m%d_%H%M%S',
        DeviceType.IPAD: '%Y%m%d_%H%M%S',
    }

    def __init__(self, pattern_matcher: DevicePatternMatcher):
        """
        Initialize with pattern matcher
        
        Args:
            pattern_matcher: DevicePatternMatcher instance for regex matching
        """
        self.pattern_matcher = pattern_matcher

    def extract(self, filename: str, device_type: DeviceType) -> Optional[datetime]:
        """
        Extract timestamp from filename
        
        Args:
            filename: Screenshot filename
            device_type: Device type (determines parsing logic)
            
        Returns:
            datetime object or None if cannot extract
        """
        if device_type == DeviceType.UNKNOWN:
            return None

        match = self.pattern_matcher.match(filename, device_type)
        if not match:
            return None

        # Extract date and time groups
        date_str = match.group(1)  # YYYYMMDD
        time_str = match.group(2)  # HHMMSS

        # Parse to datetime
        timestamp_str = f"{date_str}_{time_str}"
        timestamp_format = self.TIMESTAMP_FORMATS.get(device_type)

        if not timestamp_format:
            return None

        try:
            return datetime.strptime(timestamp_str, timestamp_format)
        except ValueError:
            return None


class DeviceMetadataBuilder:
    """
    Unified metadata dictionary construction
    
    Builds consistent metadata structure across all device types
    """

    DEVICE_NAMES = {
        DeviceType.SAMSUNG_S23: "Samsung Galaxy S23",
        DeviceType.IPAD: "iPad",
        DeviceType.UNKNOWN: "Unknown Device"
    }

    def __init__(self, pattern_matcher: DevicePatternMatcher,
                 timestamp_extractor: TimestampExtractor):
        """
        Initialize with utilities
        
        Args:
            pattern_matcher: DevicePatternMatcher instance
            timestamp_extractor: TimestampExtractor instance
        """
        self.pattern_matcher = pattern_matcher
        self.timestamp_extractor = timestamp_extractor

    def build(self, file_path: Path, device_type: DeviceType,
              timestamp: Optional[datetime]) -> Dict[str, Any]:
        """
        Build unified metadata dictionary
        
        Args:
            file_path: Path to screenshot file
            device_type: Detected device type
            timestamp: Extracted timestamp (or None)
            
        Returns:
            Dictionary with unified metadata structure
        """
        metadata = {
            'device_type': device_type.value,
            'device_name': self.DEVICE_NAMES.get(device_type, "Unknown"),
            'source_file': file_path.name,
            'timestamp': timestamp,
        }

        # Device-specific fields
        if device_type == DeviceType.SAMSUNG_S23:
            metadata['app_name'] = self._extract_samsung_app_name(file_path.name)

        return metadata

    def _extract_samsung_app_name(self, filename: str) -> Optional[str]:
        """
        Extract app name from Samsung screenshot filename
        
        Args:
            filename: Samsung screenshot filename
            
        Returns:
            App name or None
        """
        match = self.pattern_matcher.match(filename, DeviceType.SAMSUNG_S23)
        if match and len(match.groups()) >= 3:
            return match.group(3)  # Third capture group is app name
        return None
