"""
CaptureMatcherPOC - Core functionality for timestamp-based capture matching

Implements temporal matching of Samsung S23 screenshots and voice recordings
based on filename timestamp patterns for knowledge capture workflow.

TDD Implementation - Core timestamp parsing and matching algorithms
"""

import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List


class TimestampParser:
    """Utility class for parsing Samsung S23 filename timestamps"""
    
    # Regex patterns for Samsung filename formats
    SCREENSHOT_PATTERN = re.compile(r'^Screenshot_(\d{8})_(\d{6}).*\.(jpg|png)$')
    RECORDING_PATTERN = re.compile(r'^Recording_(\d{8})_(\d{6})\.m4a$')
    # Alternative OneDrive voice pattern: Voice YYMMDD_HHMMSS.m4a  
    VOICE_PATTERN_ONEDRIVE = re.compile(r'^Voice (\d{6})_(\d{6})\.m4a$')
    
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
        if match:
            date_str, time_str = match.groups()[0], match.groups()[1]  # Skip file extension group
        else:
            # Try recording pattern
            match = cls.RECORDING_PATTERN.match(filename)
            if match:
                date_str, time_str = match.groups()
            else:
                # Try OneDrive voice pattern (Voice YYMMDD_HHMMSS.m4a)
                match = cls.VOICE_PATTERN_ONEDRIVE.match(filename)
                if match:
                    date_str, time_str = match.groups()
                    # Convert YYMMDD to YYYYMMDD (assume 20XX for YY >= 00)
                    yy = date_str[:2]
                    year_prefix = "20" if int(yy) <= 50 else "19"  # Assume 20XX for 00-50, 19XX for 51-99
                    date_str = year_prefix + date_str
                else:
                    return None
        
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
    
    @classmethod
    def create_with_onedrive_defaults(cls, base_onedrive_path: Optional[str] = None) -> 'CaptureMatcherPOC':
        """Create CaptureMatcherPOC with default OneDrive paths
        
        Args:
            base_onedrive_path: Base OneDrive directory path. If None, uses default.
            
        Returns:
            CaptureMatcherPOC instance configured with OneDrive paths
        """
        if base_onedrive_path is None:
            base_onedrive_path = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal"
        
        screenshots_dir = f"{base_onedrive_path}/backlog/Pictures/Samsung Gallery/DCIM/Screenshots"
        voice_dir = f"{base_onedrive_path}/Voice Recorder/Voice Recorder"
        
        return cls(screenshots_dir, voice_dir)
    
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
    
    def configure_onedrive_paths(self, screenshots_dir: str, voice_dir: str) -> None:
        """Configure OneDrive directory paths for file scanning
        
        Args:
            screenshots_dir: Path to Samsung screenshots directory
            voice_dir: Path to voice recordings directory
        """
        self.screenshots_dir = screenshots_dir
        self.voice_dir = voice_dir
    
    def scan_onedrive_captures(self, days_back: int = 7, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> Dict:
        """Scan OneDrive directories for Samsung S23 captures with date filtering
        
        Args:
            days_back: Number of days to look back (default 7)
            start_date: Custom start date for filtering
            end_date: Custom end date for filtering
            
        Returns:
            Dict with screenshots, voice_notes, scan_stats, and errors
        """
        scan_start_time = time.time()
        
        # Set up date filtering
        if start_date is None and end_date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
        elif start_date is None:
            start_date = end_date - timedelta(days=days_back) if end_date else datetime.now() - timedelta(days=days_back)
        elif end_date is None:
            end_date = datetime.now()
        
        # Ensure we have valid datetime objects
        if start_date is None:
            start_date = datetime.now() - timedelta(days=days_back)
        if end_date is None:
            end_date = datetime.now()
        
        result = {
            "screenshots": [],
            "voice_notes": [],
            "scan_stats": {},
            "errors": []
        }
        
        # Scan screenshots directory
        try:
            screenshots_path = Path(self.screenshots_dir)
            if screenshots_path.exists():
                screenshot_files = self._scan_directory_for_samsung_files(
                    screenshots_path, "screenshot", start_date, end_date
                )
                result["screenshots"] = screenshot_files
            else:
                result["errors"].append(f"Screenshots directory not found: {self.screenshots_dir}")
        except Exception as e:
            result["errors"].append(f"Error scanning screenshots: {str(e)}")
        
        # Scan voice recordings directory
        try:
            voice_path = Path(self.voice_dir)
            if voice_path.exists():
                voice_files = self._scan_directory_for_samsung_files(
                    voice_path, "voice", start_date, end_date
                )
                result["voice_notes"] = voice_files
            else:
                result["errors"].append(f"Voice directory not found: {self.voice_dir}")
        except Exception as e:
            result["errors"].append(f"Error scanning voice recordings: {str(e)}")
        
        # Calculate scan statistics
        scan_duration = time.time() - scan_start_time
        total_files = len(result["screenshots"]) + len(result["voice_notes"])
        
        result["scan_stats"] = {
            "scan_duration": scan_duration,
            "files_processed": total_files,
            "sync_latency_check": self._check_sync_latency(result["screenshots"] + result["voice_notes"])
        }
        
        return result
    
    def _scan_directory_for_samsung_files(self, directory: Path, file_type: str, 
                                        start_date: datetime, end_date: datetime) -> List[Dict]:
        """Scan directory for Samsung files matching date range and patterns
        
        Args:
            directory: Path object for directory to scan
            file_type: 'screenshot' or 'voice' to determine pattern matching
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            List of file metadata dictionaries
        """
        files = []
        
        # Define file patterns based on type
        if file_type == "screenshot":
            # Samsung screenshots can be .jpg or .png
            patterns = ["Screenshot_*.jpg", "Screenshot_*.png"]
        else:
            # Voice recordings: Samsung format or OneDrive format
            patterns = ["Recording_*.m4a", "Voice *.m4a"]
        
        try:
            # Scan for matching files using all patterns
            for pattern in patterns:
                for file_path in directory.glob(pattern):
                    # Parse timestamp from filename
                    timestamp = self.parse_filename_timestamp(file_path.name)
                    if timestamp is None:
                        continue
                    
                    # Filter by date range
                    if not (start_date <= timestamp <= end_date):
                        continue
                    
                    # Get file metadata
                    stat = file_path.stat()
                    file_info = {
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified_time": datetime.fromtimestamp(stat.st_mtime),
                        "type": file_type,
                        "timestamp": timestamp
                    }
                    files.append(file_info)
                
        except Exception:
            # Handle directory access errors gracefully - could be permissions, 
            # file system issues, etc. Return empty list to continue processing
            pass
        
        return files
    
    def _check_sync_latency(self, files: List[Dict]) -> Dict:
        """Check OneDrive sync latency by comparing timestamps
        
        Args:
            files: List of file metadata dictionaries
            
        Returns:
            Dict with sync latency information
        """
        if not files:
            return {"status": "no_files_to_check"}
        
        recent_files = 0
        sync_issues = 0
        
        for file_info in files:
            file_age = datetime.now() - file_info["timestamp"]
            if file_age.total_seconds() < 300:  # Files created in last 5 minutes
                recent_files += 1
                
                # Check if modification time differs significantly from filename timestamp
                mod_diff = abs((file_info["modified_time"] - file_info["timestamp"]).total_seconds())
                if mod_diff > 60:  # More than 1 minute difference suggests sync delay
                    sync_issues += 1
        
        return {
            "status": "checked",
            "recent_files_count": recent_files,
            "potential_sync_issues": sync_issues
        }
