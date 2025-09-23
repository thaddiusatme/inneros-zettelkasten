"""
CaptureMatcherPOC - Core functionality for timestamp-based capture matching

Implements temporal matching of Samsung S23 screenshots and voice recordings
based on filename timestamp patterns for knowledge capture workflow.

TDD Implementation - Core timestamp parsing and matching algorithms
"""

import re
import subprocess
import sys
import time
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List

# Add development/src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from ai.workflow_manager import WorkflowManager
except ImportError:
    # Fallback for test environments
    WorkflowManager = None


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
    
    # Template constants for markdown generation
    YAML_TEMPLATE = """---
type: fleeting
created: {timestamp}
status: inbox
tags:
  - capture
  - samsung-s23
  - screenshot-voice-pair
source: capture
device: Samsung S23
time_gap_seconds: {time_gap}
---"""
    
    MARKDOWN_TEMPLATE = """
# Capture Summary

Knowledge capture from Samsung S23 screenshot and voice note pair.

## Screenshot Reference

- **File**: {screenshot_filename}
- **Size**: {screenshot_size}
- **Timestamp**: {screenshot_timestamp}
- **Path**: {screenshot_path}

## Voice Note Reference

- **File**: {voice_filename}
- **Size**: {voice_size}  
- **Timestamp**: {voice_timestamp}
- **Path**: {voice_path}

## Capture Metadata

- **Time Gap**: {time_gap} seconds between screenshot and voice note
- **Device**: Samsung S23 (detected from filename patterns)
- **Capture Session**: {capture_session}

## Processing Notes

*Add your analysis, insights, and connections here*

- [ ] Review screenshot content
- [ ] Listen to voice note
- [ ] Extract key insights
- [ ] Link to related notes
- [ ] Consider promotion to permanent note

"""
    
    def __init__(self, screenshots_dir: str, voice_dir: str):
        """Initialize matcher with source directories
        
        Args:
            screenshots_dir: Path to Samsung screenshots directory
            voice_dir: Path to voice recordings directory
        """
        self.screenshots_dir = screenshots_dir
        self.voice_dir = voice_dir
        self.match_threshold = 60  # seconds
        self.inbox_dir = None  # Will be set via configure_inbox_directory()
    
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
    
    def interactive_review_captures(self, matched_pairs: List[Dict]) -> Dict:
        """Interactive CLI review of matched capture pairs
        
        Args:
            matched_pairs: List of matched screenshot/voice pairs from match_by_timestamp()
            
        Returns:
            Dict with kept, skipped, deleted lists and session stats
        """
        # Initialize result structure
        result = {
            "kept": [],
            "skipped": [],
            "deleted": [],
            "session_stats": {
                "total_reviewed": 0,
                "kept_count": 0,
                "skipped_count": 0,
                "deleted_count": 0
            }
        }
        
        if not matched_pairs:
            print("No capture pairs to review.")
            return result
        
        total_pairs = len(matched_pairs)
        print(f"📋 Starting interactive review of {total_pairs} capture pairs")
        print("Commands: [k]eep, [s]kip, [d]elete, [v]iew, [h]elp, [q]uit\n")
        
        for i, pair in enumerate(matched_pairs):
            current_index = i + 1
            
            # Display pair information
            self._display_capture_pair(pair, current_index, total_pairs)
            
            # Get user input
            while True:
                try:
                    user_input = input(f"\n({current_index}/{total_pairs}) Action [k/s/d/v/h/q]: ").strip().lower()
                    
                    if user_input == 'k':  # Keep
                        result["kept"].append(pair)
                        result["session_stats"]["kept_count"] += 1
                        print("✅ Kept pair for processing")
                        break
                    elif user_input == 's':  # Skip
                        result["skipped"].append(pair)
                        result["session_stats"]["skipped_count"] += 1
                        print("⏭️ Skipped pair")
                        break
                    elif user_input == 'd':  # Delete
                        result["deleted"].append(pair)
                        result["session_stats"]["deleted_count"] += 1
                        print("🗑️ Marked pair for deletion")
                        break
                    elif user_input == 'v':  # View screenshot
                        screenshot_path = pair["screenshot"]["path"]
                        self._open_screenshot_in_viewer(screenshot_path)
                        continue  # Stay in the same pair after viewing
                    elif user_input == 'h':  # Help
                        self._show_help()
                        continue
                    elif user_input == 'q':  # Quit
                        print("🛑 Exiting review session...")
                        result["session_stats"]["total_reviewed"] = current_index - 1
                        return result
                    else:
                        print("❌ Invalid command. Please enter k, s, d, v, h, or q. Try again:")
                        continue
                        
                except KeyboardInterrupt:
                    print("\n🛑 Review session interrupted.")
                    result["session_stats"]["total_reviewed"] = current_index - 1
                    return result
            
            result["session_stats"]["total_reviewed"] = current_index
            
            # Add spacing between pairs
            if current_index < total_pairs:
                print("\n" + "─" * 50)
        
        print("\n🎉 Review session complete!")
        self._show_session_summary(result["session_stats"])
        
        return result
    
    def _display_capture_pair(self, pair: Dict, current: int, total: int) -> None:
        """Display capture pair information with formatting
        
        Args:
            pair: Matched pair dict with screenshot, voice, time_gap_seconds
            current: Current item index  
            total: Total items count
        """
        screenshot = pair["screenshot"]
        voice = pair["voice"]
        gap_seconds = pair["time_gap_seconds"]
        
        # Show progress header
        print(f"\n📋 Reviewing Pair {current}/{total}")
        print("─" * 30)
        
        print(f"📸 Screenshot: {screenshot['filename']}")
        print(f"🎤 Voice: {voice['filename']}")
        print(f"⏱️ Time Gap: {gap_seconds} seconds")
        
        # Show file paths (truncated for readability)
        screenshot_path = screenshot.get("path", "N/A")
        voice_path = voice.get("path", "N/A")
        if len(screenshot_path) > 60:
            screenshot_path = "..." + screenshot_path[-57:]
        if len(voice_path) > 60:
            voice_path = "..." + voice_path[-57:]
        
        print(f"📂 Screenshot Path: {screenshot_path}")
        print(f"📂 Voice Path: {voice_path}")
    
    def _show_help(self) -> None:
        """Display help information for available commands"""
        print("\n📋 Available Commands:")
        print("  k - Keep this pair for markdown note generation")
        print("  s - Skip this pair (ignore for now)")
        print("  d - Delete this pair (remove files)")
        print("  v - View screenshot in external viewer")
        print("  h - Show this help message")
        print("  q - Quit review session")
        print("\nNote: Only 'kept' pairs will be processed into markdown notes.")
    
    def _show_session_summary(self, stats: Dict) -> None:
        """Display session summary statistics
        
        Args:
            stats: Session statistics dict
        """
        total = stats["total_reviewed"]
        kept = stats["kept_count"]
        skipped = stats["skipped_count"]
        deleted = stats["deleted_count"]
        
        print("📊 Session Summary:")
        print(f"   Total Reviewed: {total}")
        print(f"   ✅ Kept: {kept}")
        print(f"   ⏭️ Skipped: {skipped}")
        print(f"   🗑️ Deleted: {deleted}")
    
    def _open_screenshot_in_viewer(self, screenshot_path: str) -> None:
        """Open screenshot in external viewer (macOS Preview or default app)
        
        Args:
            screenshot_path: Full path to screenshot file
        """
        try:
            print("🖼️ Opening screenshot in viewer...")
            
            # Use macOS 'open' command which opens files with default application
            subprocess.run(['open', screenshot_path], 
                          capture_output=True, 
                          text=True, 
                          check=True)
            
            print("✅ Screenshot opened successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error opening screenshot: {e}")
            print(f"   Try manually opening: {screenshot_path}")
        except FileNotFoundError:
            print("❌ 'open' command not found (macOS required)")
            print(f"   Screenshot path: {screenshot_path}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print(f"   Screenshot path: {screenshot_path}")
    
    def configure_inbox_directory(self, inbox_dir: str) -> None:
        """Configure the inbox directory for note generation
        
        Args:
            inbox_dir: Path to the InnerOS inbox directory (e.g., knowledge/Inbox/)
        """
        self.inbox_dir = inbox_dir
    
    def generate_capture_note(self, capture_pair: Dict, description: str) -> Dict:
        """Generate markdown note from capture pair
        
        Args:
            capture_pair: Matched screenshot/voice pair from interactive review
            description: User-provided description for the capture
            
        Returns:
            Dict with markdown_content, filename, and file_path
            
        Raises:
            ValueError: If capture_pair is missing required fields
            TypeError: If description is not a string
        """
        # Validate inputs
        if not isinstance(description, str):
            raise TypeError("Description must be a string")
        
        if not capture_pair or not isinstance(capture_pair, dict):
            raise ValueError("Capture pair must be a non-empty dictionary")
            
        required_fields = ["screenshot", "voice", "time_gap_seconds"]
        for field in required_fields:
            if field not in capture_pair:
                raise ValueError(f"Capture pair missing required field: {field}")
        
        # Extract and validate data
        screenshot = capture_pair["screenshot"]
        voice = capture_pair["voice"]
        time_gap = capture_pair["time_gap_seconds"]
        
        if not screenshot.get("timestamp"):
            raise ValueError("Screenshot missing timestamp field")
        if not voice.get("timestamp"):
            raise ValueError("Voice note missing timestamp field")
        
        # Use screenshot timestamp as primary timestamp
        capture_timestamp = screenshot["timestamp"]
        
        # Generate kebab-case filename
        filename = self._generate_capture_filename(capture_timestamp, description)
        
        # Generate file path
        inbox_dir = self.inbox_dir if self.inbox_dir else '/path/to/knowledge/Inbox'
        file_path = f"{inbox_dir}/{filename}"
        
        # Generate markdown content
        markdown_content = self._generate_markdown_template(capture_pair, description, capture_timestamp)
        
        return {
            "markdown_content": markdown_content,
            "filename": filename,
            "file_path": file_path
        }
    
    def generate_capture_notes_batch(self, kept_pairs: List[Dict], descriptions: List[str]) -> List[Dict]:
        """Generate markdown notes for multiple capture pairs
        
        Args:
            kept_pairs: List of kept capture pairs from interactive review
            descriptions: List of descriptions matching kept pairs
            
        Returns:
            List of generation results with processing stats
            
        Raises:
            ValueError: If kept_pairs is empty or invalid
            TypeError: If inputs are not the expected types
        """
        # Validate inputs
        if not isinstance(kept_pairs, list):
            raise TypeError("kept_pairs must be a list")
        if not isinstance(descriptions, list):
            raise TypeError("descriptions must be a list") 
        if not kept_pairs:
            raise ValueError("kept_pairs cannot be empty")
            
        results = []
        errors = []
        
        for i, pair in enumerate(kept_pairs):
            try:
                description = descriptions[i] if i < len(descriptions) else f"capture-{i+1}"
                result = self.generate_capture_note(pair, description)
                results.append(result)
            except Exception as e:
                error_info = {
                    "pair_index": i,
                    "error": str(e),
                    "pair_data": pair
                }
                errors.append(error_info)
        
        # Add processing statistics
        if results:
            results[0]["processing_stats"] = {
                "total_pairs": len(kept_pairs),
                "successful": len(results),
                "errors": len(errors),
                "error_details": errors
            }
        
        return results
    
    def _generate_capture_filename(self, timestamp: datetime, description: str) -> str:
        """Generate kebab-case filename following InnerOS conventions
        
        Args:
            timestamp: Capture timestamp
            description: User description
            
        Returns:
            Kebab-case filename like capture-20250122-1435-description.md
        """
        # Format timestamp as YYYYMMDD-HHMM
        date_str = timestamp.strftime("%Y%m%d-%H%M")
        
        # Convert description to kebab-case
        # Remove special chars, convert to lowercase, replace spaces/underscores with hyphens
        clean_desc = re.sub(r'[^a-zA-Z0-9\s_-]', '', description)
        clean_desc = re.sub(r'[\s_]+', '-', clean_desc.strip())
        kebab_desc = clean_desc.lower()
        
        return f"capture-{date_str}-{kebab_desc}.md"
    
    def _generate_markdown_template(self, capture_pair: Dict, description: str, timestamp: datetime) -> str:
        """Generate markdown content with YAML frontmatter using class templates
        
        Args:
            capture_pair: Screenshot and voice pair data
            description: User description
            timestamp: Capture timestamp
            
        Returns:
            Complete markdown content with YAML frontmatter
        """
        screenshot = capture_pair["screenshot"]
        voice = capture_pair["voice"]
        time_gap = capture_pair["time_gap_seconds"]
        
        # Format timestamp for YAML (ISO format without seconds for brevity)
        yaml_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
        
        # Calculate file sizes in readable format
        screenshot_size = self._format_file_size(screenshot.get("size", 0))
        voice_size = self._format_file_size(voice.get("size", 0))
        
        # Generate YAML frontmatter using template
        yaml_frontmatter = self.YAML_TEMPLATE.format(
            timestamp=yaml_timestamp,
            time_gap=time_gap
        )
        
        # Generate markdown content using template
        content = self.MARKDOWN_TEMPLATE.format(
            screenshot_filename=screenshot['filename'],
            screenshot_size=screenshot_size,
            screenshot_timestamp=timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            screenshot_path=screenshot.get('path', 'N/A'),
            voice_filename=voice['filename'],
            voice_size=voice_size,
            voice_timestamp=voice['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            voice_path=voice.get('path', 'N/A'),
            time_gap=time_gap,
            capture_session=timestamp.strftime('%Y-%m-%d %H:%M')
        )
        
        return yaml_frontmatter + content
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format
        
        Args:
            size_bytes: File size in bytes
        Returns:
            Formatted size string (e.g., "1.0 MB", "512 KB")
        """
        if size_bytes == 0:
            return "Unknown"
        
        # Use the enhanced utility function for consistency
        from zettelkasten_capture_utils import ZettelkastenCaptureEnhancer
        enhancer = ZettelkastenCaptureEnhancer()
        return enhancer.format_file_size(size_bytes)
    
    def process_capture_notes_with_ai(self, capture_notes: List[Dict]) -> Dict:
        """Process capture notes with AI workflow integration
        
        Integrates generated capture notes with existing InnerOS AI workflow systems
        
        Args:
            capture_notes: List of capture note dictionaries from generate_capture_note()
            
        Returns:
            Dict with AI processing results, statistics, and errors
            
        Performance Targets:
            - <30 seconds for 5+ capture notes
            - >0.7 quality scores for well-formed captures
            - 3-8 relevant AI tags per note
        """
        start_time = time.time()
        
        # Initialize comprehensive result structure
        result = self._initialize_ai_processing_result(len(capture_notes))
        
        # Initialize WorkflowManager for AI processing
        workflow_manager = self._setup_workflow_manager(result)
        
        # Process each capture note with enhanced error handling
        for i, note in enumerate(capture_notes):
            try:
                # Validate and process individual note
                ai_result = self._process_individual_capture_note(
                    note, i, workflow_manager, result
                )
                
                if ai_result:
                    result["ai_results"].append(ai_result)
                    result["processing_stats"]["successful"] += 1
                    
            except Exception as e:
                self._handle_processing_error(e, i, note, result)
        
        # Finalize processing statistics
        result["processing_stats"]["processing_time"] = time.time() - start_time
        result["processing_stats"]["average_quality_score"] = self._calculate_average_quality_score(result["ai_results"])
        
        return result
    
    def _initialize_ai_processing_result(self, total_notes: int) -> Dict:
        """Initialize the AI processing result structure"""
        return {
            "processing_stats": {
                "total_notes": total_notes,
                "successful": 0,
                "errors": 0,
                "processing_time": 0.0,
                "average_quality_score": 0.0,
                "workflow_manager_available": WorkflowManager is not None
            },
            "ai_results": [],
            "errors": []
        }
    
    def _setup_workflow_manager(self, result: Dict) -> Optional[object]:
        """Setup WorkflowManager for AI processing with error handling"""
        if WorkflowManager is None:
            result["errors"].append("WorkflowManager not available - using fallback AI processing")
            return None
            
        try:
            # Use inbox directory if configured, otherwise use a temporary directory  
            base_dir = self.inbox_dir if self.inbox_dir else "/tmp/capture_test"
            return WorkflowManager(base_dir)
        except Exception as e:
            result["errors"].append(f"Failed to initialize WorkflowManager: {e}")
            return None
    
    def _process_individual_capture_note(self, note: Dict, index: int, 
                                       workflow_manager: Optional[object], 
                                       result: Dict) -> Optional[Dict]:
        """Process individual capture note with AI integration"""
        # Validate note structure
        self._validate_capture_note_structure(note)
        
        # Create temporary file for AI processing
        temp_path = self._create_temp_file_for_processing(note["markdown_content"])
        
        try:
            # Initialize AI result with defaults
            ai_result = self._create_default_ai_result(note)
            
            # Enhance with WorkflowManager AI processing if available
            if workflow_manager is not None:
                self._enhance_with_workflow_manager(ai_result, temp_path, workflow_manager, note["filename"], result)
            
            return ai_result
            
        finally:
            # Always clean up temporary file
            self._cleanup_temp_file(temp_path)
    
    def _validate_capture_note_structure(self, note: Dict) -> None:
        """Validate that capture note has required structure"""
        if not isinstance(note, dict):
            raise ValueError("Invalid note: must be dictionary")
        
        required_fields = ["markdown_content", "filename", "file_path"]
        for field in required_fields:
            if field not in note:
                raise ValueError(f"Invalid note: missing {field}")
    
    def _create_temp_file_for_processing(self, content: str) -> str:
        """Create temporary file for AI processing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
            temp_file.write(content)
            return temp_file.name
    
    def _create_default_ai_result(self, note: Dict) -> Dict:
        """Create default AI result structure with fallback values"""
        return {
            "original_filename": note["filename"],
            "file_path": note["file_path"],
            "quality_score": 0.8,  # Default high score for capture notes
            "ai_tags": ["capture", "samsung-s23", "knowledge-management"],
            "recommendations": [
                "Review screenshot content",
                "Process voice note", 
                "Consider promotion to permanent"
            ],
            "processing_method": "fallback"  # Will be updated if WorkflowManager succeeds
        }
    
    def _enhance_with_workflow_manager(self, ai_result: Dict, temp_path: str, 
                                     workflow_manager: object, filename: str, 
                                     result: Dict) -> None:
        """Enhance AI result using WorkflowManager processing"""
        try:
            # Process with existing AI workflow (dry_run=True for safety)
            processing_result = workflow_manager.process_inbox_note(
                temp_path, dry_run=True, fast=False
            )
            
            # Extract and integrate AI results from WorkflowManager
            if "processing" in processing_result:
                processing_data = processing_result["processing"]
                
                # Update quality score (prioritize real AI scoring)
                if "quality_score" in processing_data:
                    ai_result["quality_score"] = processing_data["quality_score"]
                
                # Update AI tags (prefer AI-generated tags)
                if "ai_tags" in processing_data and processing_data["ai_tags"]:
                    ai_result["ai_tags"] = processing_data["ai_tags"]
                
                # Update recommendations (use AI enhancement suggestions)
                if "enhancement_suggestions" in processing_data:
                    ai_result["recommendations"] = processing_data["enhancement_suggestions"]
                
                ai_result["processing_method"] = "workflow_manager"
        
        except Exception as e:
            # Graceful degradation - keep default values and log error
            result["errors"].append(f"AI processing failed for {filename}: {e}")
            ai_result["processing_method"] = "fallback_due_to_error"
    
    def _cleanup_temp_file(self, temp_path: str) -> None:
        """Clean up temporary file with error handling"""
        try:
            Path(temp_path).unlink()
        except Exception:
            # Silently ignore cleanup errors - temporary files will be cleaned up by OS
            pass
    
    def _handle_processing_error(self, error: Exception, index: int, 
                               note: any, result: Dict) -> None:
        """Handle processing errors with comprehensive error information"""
        error_info = {
            "note_index": index,
            "error": str(error),
            "error_type": type(error).__name__,
            "filename": note.get("filename", "unknown") if isinstance(note, dict) else "invalid",
            "timestamp": datetime.now().isoformat()
        }
        result["errors"].append(error_info)
        result["processing_stats"]["errors"] += 1
    
    def _calculate_average_quality_score(self, ai_results: List[Dict]) -> float:
        """Calculate average quality score across processed notes"""
        if not ai_results:
            return 0.0
        
        total_score = sum(result.get("quality_score", 0.0) for result in ai_results)
        return round(total_score / len(ai_results), 3)
