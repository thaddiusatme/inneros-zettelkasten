#!/usr/bin/env python3
"""
Multi-Device Screenshot Detection System
Detects device type and extracts metadata from screenshot filenames
"""

import re
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional


class DeviceType(Enum):
    """Supported device types for screenshot detection"""
    SAMSUNG_S23 = "samsung_s23"
    IPAD = "ipad"
    UNKNOWN = "unknown"


class MultiDeviceDetector:
    """
    Detect device type and extract metadata from screenshot filenames
    
    Supports:
    - Samsung S23: Screenshot_YYYYMMDD_HHMMSS_AppName.jpg
    - iPad: YYYYMMDD_HHMMSS000_iOS.png
    - Unknown: Any other pattern
    """
    
    def __init__(self):
        """Initialize device patterns"""
        self.device_patterns = {
            DeviceType.SAMSUNG_S23: {
                'regex': re.compile(r'^Screenshot_(\d{8})_(\d{6})_(.+)\.jpg$'),
                'timestamp_format': '%Y%m%d_%H%M%S',
            },
            DeviceType.IPAD: {
                'regex': re.compile(r'^(\d{8})_(\d{6})\d{3}_iOS\.png$'),
                'timestamp_format': '%Y%m%d_%H%M%S',
            }
        }
    
    def detect_device(self, file_path: Path) -> DeviceType:
        """
        Detect device type from filename pattern
        
        Args:
            file_path: Path to screenshot file
            
        Returns:
            DeviceType enum (SAMSUNG_S23, IPAD, or UNKNOWN)
        """
        filename = file_path.name
        
        # Check Samsung S23 pattern
        if self.device_patterns[DeviceType.SAMSUNG_S23]['regex'].match(filename):
            return DeviceType.SAMSUNG_S23
        
        # Check iPad pattern
        if self.device_patterns[DeviceType.IPAD]['regex'].match(filename):
            return DeviceType.IPAD
        
        # Unknown device
        return DeviceType.UNKNOWN
    
    def extract_timestamp(self, file_path: Path) -> Optional[datetime]:
        """
        Extract timestamp from filename using device-specific regex
        
        Args:
            file_path: Path to screenshot file
            
        Returns:
            datetime object or None if cannot extract
        """
        device_type = self.detect_device(file_path)
        
        if device_type == DeviceType.UNKNOWN:
            return None
        
        filename = file_path.name
        pattern_info = self.device_patterns[device_type]
        match = pattern_info['regex'].match(filename)
        
        if not match:
            return None
        
        # Extract date and time groups
        date_str = match.group(1)  # YYYYMMDD
        time_str = match.group(2)  # HHMMSS
        
        # Parse to datetime
        timestamp_str = f"{date_str}_{time_str}"
        return datetime.strptime(timestamp_str, pattern_info['timestamp_format'])
    
    def extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract all device-specific metadata
        
        Args:
            file_path: Path to screenshot file
            
        Returns:
            Dictionary with device metadata
        """
        device_type = self.detect_device(file_path)
        timestamp = self.extract_timestamp(file_path)
        
        metadata = {
            'device_type': device_type.value,
            'device_name': self._get_device_name(device_type),
            'source_file': file_path.name,
            'timestamp': timestamp,
        }
        
        # Samsung-specific: Extract app name
        if device_type == DeviceType.SAMSUNG_S23:
            metadata['app_name'] = self._extract_samsung_app_name(file_path)
        
        return metadata
    
    def _get_device_name(self, device_type: DeviceType) -> str:
        """Get human-readable device name"""
        names = {
            DeviceType.SAMSUNG_S23: "Samsung Galaxy S23",
            DeviceType.IPAD: "iPad",
            DeviceType.UNKNOWN: "Unknown Device"
        }
        return names.get(device_type, "Unknown")
    
    def _extract_samsung_app_name(self, file_path: Path) -> Optional[str]:
        """Extract app name from Samsung screenshot filename"""
        match = self.device_patterns[DeviceType.SAMSUNG_S23]['regex'].match(file_path.name)
        if match:
            return match.group(3)  # Third capture group is app name
        return None
