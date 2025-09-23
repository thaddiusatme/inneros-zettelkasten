"""
CaptureMatcherPOC - Core functionality for timestamp-based capture matching

Implements temporal matching of Samsung S23 screenshots and voice recordings
based on filename timestamp patterns for knowledge capture workflow.

TDD Implementation - Core timestamp parsing and matching algorithms
"""

import re
from datetime import datetime
from typing import Optional, Dict, List


class TimestampParser:
    """Utility class for parsing Samsung S23 filename timestamps"""
    
    # Regex patterns for Samsung filename formats
    SCREENSHOT_PATTERN = re.compile(r'^Screenshot_(\d{8})_(\d{6})\.png$')
    RECORDING_PATTERN = re.compile(r'^Recording_(\d{8})_(\d{6})\.m4a$')
    
    @classmethod
    def parse_samsung_filename(cls, filename: str) -> Optional[datetime]:
        """Parse timestamp from Samsung S23 filename patterns
        
        Args:
            filename: Screenshot_YYYYMMDD_HHMMSS.png or Recording_YYYYMMDD_HHMMSS.m4a
            
        Returns:
            datetime object or None if parsing fails
        """
        # Try screenshot pattern first
        match = cls.SCREENSHOT_PATTERN.match(filename)
        if not match:
            # Try recording pattern
            match = cls.RECORDING_PATTERN.match(filename)
        
        if not match:
            return None
            
        date_str, time_str = match.groups()
        
        try:
            # Parse date components (YYYYMMDD)
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            
            # Parse time components (HHMMSS)
            hour = int(time_str[0:2])
            minute = int(time_str[2:4])
            second = int(time_str[4:6])
            
            # Validate ranges
            if not cls._validate_datetime_components(year, month, day, hour, minute, second):
                return None
            
            return datetime(year, month, day, hour, minute, second)
            
        except (ValueError, IndexError):
            return None
    
    @staticmethod
    def _validate_datetime_components(year: int, month: int, day: int, 
                                     hour: int, minute: int, second: int) -> bool:
        """Validate datetime component ranges"""
        return (
            1900 <= year <= 2100 and
            1 <= month <= 12 and
            1 <= day <= 31 and
            0 <= hour <= 23 and
            0 <= minute <= 59 and
            0 <= second <= 59
        )


class CaptureMatcherPOC:
    """POC for matching screenshots and voice notes by filename timestamps"""
    
    def __init__(self, screenshots_dir: str, voice_dir: str):
        """Initialize matcher with source directories
        
        Args:
            screenshots_dir: Path to Samsung screenshots directory
            voice_dir: Path to voice recordings directory
        """
        self.screenshots_dir = screenshots_dir
        self.voice_dir = voice_dir
        self.match_threshold = 60  # seconds
    
    def parse_filename_timestamp(self, filename: str) -> Optional[datetime]:
        """Extract timestamp from Samsung filename patterns using TimestampParser
        
        Args:
            filename: Samsung filename (Screenshot_YYYYMMDD_HHMMSS.png or Recording_YYYYMMDD_HHMMSS.m4a)
            
        Returns:
            datetime object or None if parsing fails
        """
        return TimestampParser.parse_samsung_filename(filename)
    
    def match_by_timestamp(self, captures: List[Dict]) -> Dict:
        """Match screenshots and voice notes by timestamp proximity
        
        Args:
            captures: List of file info dicts with filename, type, path keys
            
        Returns:
            Dict with paired, unpaired_screenshots, unpaired_voice lists
        """
        # Parse timestamps for all captures
        screenshots = []
        voices = []
        
        for capture in captures:
            timestamp = self.parse_filename_timestamp(capture["filename"])
            if timestamp is None:
                continue
                
            capture_with_timestamp = {**capture, "timestamp": timestamp}
            
            if capture["type"] == "screenshot":
                screenshots.append(capture_with_timestamp)
            elif capture["type"] == "voice":
                voices.append(capture_with_timestamp)
        
        # Sort by timestamp for efficient matching
        screenshots.sort(key=lambda x: x["timestamp"])
        voices.sort(key=lambda x: x["timestamp"])
        
        paired = []
        used_voices = set()
        unpaired_screenshots = []
        
        # For each screenshot, find the closest voice note within threshold
        for screenshot in screenshots:
            best_match = None
            best_gap = float('inf')
            
            for i, voice in enumerate(voices):
                if i in used_voices:
                    continue
                    
                gap = abs((voice["timestamp"] - screenshot["timestamp"]).total_seconds())
                
                if gap <= self.match_threshold and gap < best_gap:
                    best_match = i
                    best_gap = gap
            
            if best_match is not None:
                voice = voices[best_match]
                paired.append({
                    "screenshot": screenshot,
                    "voice": voice,
                    "time_gap_seconds": int(best_gap)
                })
                used_voices.add(best_match)
            else:
                unpaired_screenshots.append(screenshot)
        
        # Collect unpaired voice notes
        unpaired_voice = [voice for i, voice in enumerate(voices) if i not in used_voices]
        
        return {
            "paired": paired,
            "unpaired_screenshots": unpaired_screenshots,
            "unpaired_voice": unpaired_voice
        }
