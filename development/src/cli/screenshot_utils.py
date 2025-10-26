#!/usr/bin/env python3
"""
Samsung Screenshot Evening Workflow System - Utility Classes

Utility classes for the Evening Screenshot Processor following established 
modular architecture patterns from Smart Link Management TDD iterations.

Utilities:
- OneDriveScreenshotDetector: Scan and detect Samsung screenshots
- ScreenshotOCRProcessor: OCR processing integration with llama_vision_ocr.py
- DailyNoteGenerator: Generate daily notes with YAML frontmatter
- SmartLinkIntegrator: Integration with Smart Link Management system
- SafeScreenshotManager: Safety-first file management with backup patterns
"""

import logging
from pathlib import Path
from datetime import datetime, date
import re
import shutil
import tempfile
from typing import List, Dict, Any, Optional
import sys

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.llama_vision_ocr import VisionAnalysisResult

logger = logging.getLogger(__name__)


class OneDriveScreenshotDetector:
    """
    Utility for detecting and scanning Samsung screenshots from OneDrive
    
    Handles Samsung Galaxy S23 screenshot naming patterns and file detection
    following the pattern: Screenshot_YYYYMMDD_HHMMSS_AppName.jpg
    """

    def __init__(self, onedrive_path: str):
        """
        Initialize OneDrive screenshot detector
        
        Args:
            onedrive_path: Path to OneDrive Samsung Screenshots directory
        """
        self.onedrive_path = Path(onedrive_path)
        self.samsung_pattern = re.compile(r'Screenshot_(\d{8})_(\d{6})_(.+)\.jpg$')

        logger.info(f"Initialized OneDriveScreenshotDetector for {onedrive_path}")

    def scan_todays_screenshots(self, limit: Optional[int] = None) -> List[Path]:
        """
        Scan for recent Samsung screenshots (last 7 days)
        
        Args:
            limit: Optional limit on number of screenshots to return (most recent)
        
        Returns:
            List of screenshot file paths from the last 7 days
        """
        if not self.onedrive_path.exists():
            logger.warning(f"OneDrive path does not exist: {self.onedrive_path}")
            return []

        from datetime import timedelta

        # Get date range for last 7 days
        today = date.today()
        date_range = [(today - timedelta(days=i)).strftime("%Y%m%d") for i in range(7)]

        screenshots = []

        try:
            for file_path in self.onedrive_path.glob("*.jpg"):
                if self.is_samsung_screenshot(file_path.name):
                    # Extract date from filename
                    match = self.samsung_pattern.match(file_path.name)
                    if match and match.group(1) in date_range:
                        screenshots.append(file_path)
                        logger.debug(f"Found recent screenshot: {file_path.name}")

            # Sort by filename (chronological), newest first
            screenshots = sorted(screenshots, reverse=True)

            # Apply limit if specified
            if limit and limit > 0:
                screenshots = screenshots[:limit]
                logger.info(f"Limited to {len(screenshots)} most recent screenshots")

            logger.info(f"Found {len(screenshots)} screenshots from last 7 days")
            return screenshots

        except Exception as e:
            logger.error(f"Error scanning screenshots: {e}")
            return []

    def is_samsung_screenshot(self, filename: str) -> bool:
        """
        Check if filename matches Samsung screenshot pattern
        
        Args:
            filename: Name of file to check
            
        Returns:
            True if matches Samsung pattern
        """
        return bool(self.samsung_pattern.match(filename))

    def extract_screenshot_metadata(self, filename: str) -> Dict[str, Any]:
        """
        Extract metadata from Samsung screenshot filename
        
        Args:
            filename: Samsung screenshot filename
            
        Returns:
            Dictionary with timestamp, app_name, etc.
        """
        match = self.samsung_pattern.match(filename)
        if not match:
            return {}

        date_str, time_str, app_name = match.groups()

        # Parse timestamp
        try:
            timestamp = datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
        except ValueError:
            timestamp = None

        return {
            'timestamp': timestamp,
            'app_name': app_name.replace('_', ' '),
            'date_str': date_str,
            'time_str': time_str,
            'original_filename': filename
        }


class ScreenshotOCRProcessor:
    """
    Utility for OCR processing of screenshots using llama_vision_ocr.py
    
    Integrates with existing LlamaVisionOCR system for content analysis
    """

    def __init__(self):
        """Initialize Screenshot OCR Processor"""
        from src.cli.evening_screenshot_utils import LlamaVisionOCR
        self.vision_ocr = LlamaVisionOCR(local_mode=True)
        logger.info("Initialized ScreenshotOCRProcessor with LlamaVisionOCR")

    def process_screenshot(self, image_path: Path) -> Optional[VisionAnalysisResult]:
        """
        Process single screenshot with OCR
        
        Args:
            image_path: Path to screenshot image
            
        Returns:
            VisionAnalysisResult or None if processing fails
        """
        try:
            if not image_path.exists() or image_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
                logger.warning(f"Invalid image file: {image_path}")
                return self.vision_ocr.get_fallback_analysis(image_path)

            result = self.vision_ocr.analyze_screenshot(image_path)
            if result:
                logger.info(f"OCR processed {image_path.name}: {result.confidence_score:.2f} confidence")
                return result
            else:
                logger.warning(f"OCR failed for {image_path.name}, using fallback")
                return self.vision_ocr.get_fallback_analysis(image_path)

        except Exception as e:
            logger.error(f"Error processing screenshot {image_path}: {e}")
            return self.vision_ocr.get_fallback_analysis(image_path)

    def process_batch(self, image_paths: List[Path], progress_callback=None) -> Dict[str, VisionAnalysisResult]:
        """
        Process batch of screenshots with OCR
        
        Args:
            image_paths: List of screenshot paths
            progress_callback: Optional callback for progress updates (current, total, filename)
            
        Returns:
            Dictionary mapping image paths to OCR results
        """
        results = {}
        total = len(image_paths)

        for i, image_path in enumerate(image_paths):
            # Progress callback with detailed info
            if progress_callback:
                progress_callback(i + 1, total, image_path.name)

            logger.info(f"🔍 Processing [{i+1}/{total}]: {image_path.name}")
            result = self.process_screenshot(image_path)
            if result:
                # Use index to handle duplicate paths in batch processing
                key = f"{str(image_path)}_{i}" if str(image_path) in results else str(image_path)
                results[key] = result

        logger.info(f"Batch OCR processing completed: {len(results)}/{len(image_paths)} successful")
        return results


class DailyNoteGenerator:
    """
    Utility for generating daily notes with OCR results and embedded images
    
    Creates notes in knowledge/Inbox/ with proper YAML frontmatter following
    established InnerOS Zettelkasten patterns
    """

    def __init__(self, knowledge_path: str):
        """
        Initialize Daily Note Generator
        
        Args:
            knowledge_path: Path to knowledge base root
        """
        self.knowledge_path = Path(knowledge_path)
        self.inbox_path = self.knowledge_path / "Inbox"
        self.inbox_path.mkdir(exist_ok=True)

        logger.info(f"Initialized DailyNoteGenerator for {knowledge_path}")

    def generate_daily_note(self, ocr_results: List[VisionAnalysisResult],
                          screenshot_paths: List[str], date_str: str) -> Optional[str]:
        """
        Generate daily note with OCR results and embedded screenshots
        
        Args:
            ocr_results: List of OCR analysis results
            screenshot_paths: List of screenshot file paths
            date_str: Date string (YYYY-MM-DD format)
            
        Returns:
            Path to generated daily note file
        """
        try:
            note_filename = f"daily-screenshots-{date_str}.md"
            note_path = self.inbox_path / note_filename

            # Generate YAML frontmatter
            yaml_content = self.generate_yaml_frontmatter(ocr_results, len(screenshot_paths))

            # Generate note content
            content_sections = []

            # Add summary section
            content_sections.append("## Daily Screenshot Summary\n")
            content_sections.append(f"Processed {len(screenshot_paths)} screenshots from Samsung S23 via OneDrive.\n")

            # Add OCR analysis section
            if ocr_results:
                content_sections.append("## Content Analysis\n")
                for i, ocr_result in enumerate(ocr_results, 1):
                    content_sections.append(f"### Screenshot {i}\n")
                    content_sections.append(f"**Content Type**: {ocr_result.content_type}\n")
                    content_sections.append(f"**Summary**: {ocr_result.content_summary}\n")

                    if ocr_result.extracted_text.strip():
                        content_sections.append(f"**Extracted Text**: {ocr_result.extracted_text[:200]}...\n")

                    if ocr_result.main_topics:
                        topics_str = ", ".join(ocr_result.main_topics)
                        content_sections.append(f"**Topics**: {topics_str}\n")

                    content_sections.append("")

            # Add embedded images section
            embedded_images = self.generate_embedded_images(screenshot_paths)
            content_sections.append("## Screenshots\n")
            content_sections.append(embedded_images)

            # Combine all content
            full_content = yaml_content + "\n" + "\n".join(content_sections)

            # Write to file
            note_path.write_text(full_content, encoding='utf-8')
            logger.info(f"Generated daily note: {note_path}")

            return str(note_path)

        except Exception as e:
            logger.error(f"Error generating daily note: {e}")
            return None

    def generate_yaml_frontmatter(self, ocr_results: List[VisionAnalysisResult],
                                screenshot_count: int) -> str:
        """
        Generate YAML frontmatter for daily note
        
        Args:
            ocr_results: OCR analysis results for tag generation
            screenshot_count: Number of screenshots processed
            
        Returns:
            YAML frontmatter content
        """
        # Extract tags from OCR results
        all_tags = set(['daily-screenshots', 'visual-knowledge', 'samsung-s23'])

        for ocr_result in ocr_results:
            # Add main topics as tags
            for topic in ocr_result.main_topics:
                all_tags.add(topic.lower().replace(' ', '-'))

            # Add content type as tag
            if ocr_result.content_type:
                all_tags.add(ocr_result.content_type.replace('_', '-'))

        # Limit to reasonable number of tags
        tags_list = sorted(list(all_tags))[:8]
        tags_str = '[' + ', '.join(f'"{tag}"' for tag in tags_list) + ']'

        yaml_content = f"""---
type: fleeting
created: {datetime.now().strftime('%Y-%m-%d %H:%M')}
status: inbox
visibility: private
tags: {tags_str}
screenshot_count: {screenshot_count}
processing_date: {date.today().strftime('%Y-%m-%d')}
source: samsung_s23_onedrive
---"""

        return yaml_content

    def generate_embedded_images(self, screenshot_paths: List[str]) -> str:
        """
        Generate embedded image markdown for screenshots
        
        Args:
            screenshot_paths: List of screenshot file paths
            
        Returns:
            Markdown content with embedded images
        """
        if not screenshot_paths:
            return "No screenshots processed.\n"

        embedded_content = []

        for i, screenshot_path in enumerate(screenshot_paths, 1):
            # Use relative path from knowledge base
            path_obj = Path(screenshot_path)
            filename = path_obj.name

            # Create markdown image embed
            embedded_content.append(f"### Screenshot {i}: {filename}\n")
            embedded_content.append(f"![{filename}]({screenshot_path})\n")

        return "\n".join(embedded_content)


class SmartLinkIntegrator:
    """
    Utility for integrating with Smart Link Management system
    
    Provides MOC connection suggestions and automatic link insertion
    building on existing connections_demo.py functionality
    """

    def __init__(self, knowledge_path: str):
        """
        Initialize Smart Link Integrator
        
        Args:
            knowledge_path: Path to knowledge base root
        """
        self.knowledge_path = Path(knowledge_path)
        logger.info(f"Initialized SmartLinkIntegrator for {knowledge_path}")

    def suggest_moc_connections(self, ocr_result: VisionAnalysisResult) -> List[str]:
        """
        Suggest MOC connections based on OCR analysis
        
        Args:
            ocr_result: OCR analysis result
            
        Returns:
            List of suggested wikilink connections
        """
        suggestions = []

        # Business/AHS content detection
        business_keywords = ['business', 'strategy', 'revenue', 'marketing', 'content', 'ahs']
        if any(keyword in ocr_result.content_summary.lower() or
               keyword in ' '.join(ocr_result.main_topics).lower()
               for keyword in business_keywords):
            suggestions.append("[[AHS MOC]]")

        # Technical content detection
        tech_keywords = ['programming', 'code', 'development', 'ai', 'technology', 'software']
        if any(keyword in ocr_result.content_summary.lower() or
               keyword in ' '.join(ocr_result.main_topics).lower()
               for keyword in tech_keywords):
            suggestions.append("[[Technical MOC]]")

        # Add suggested connections from OCR
        for connection in ocr_result.suggested_connections[:2]:  # Limit to top 2
            wiki_link = f"[[{connection.replace('_', '-')}]]"
            if wiki_link not in suggestions:
                suggestions.append(wiki_link)

        logger.info(f"Generated {len(suggestions)} MOC connection suggestions")
        return suggestions[:4]  # Limit to top 4 suggestions

    def auto_insert_links(self, note_path: Path, suggested_links: List[str]) -> str:
        """
        Automatically insert suggested links into daily note
        
        Args:
            note_path: Path to daily note file
            suggested_links: List of wikilink suggestions
            
        Returns:
            Updated note content with inserted links
        """
        try:
            if not note_path.exists():
                logger.warning(f"Note file does not exist: {note_path}")
                return ""

            content = note_path.read_text(encoding='utf-8')

            # Find insertion point (after summary section)
            insertion_point = content.find("## Content Analysis")
            if insertion_point == -1:
                insertion_point = content.find("## Screenshots")

            if insertion_point == -1:
                # Append to end
                links_section = "\n## Related Notes\n\n" + "\n".join(f"- {link}" for link in suggested_links) + "\n"
                updated_content = content + links_section
            else:
                # Insert before the found section
                links_section = "\n## Related Notes\n\n" + "\n".join(f"- {link}" for link in suggested_links) + "\n\n"
                updated_content = content[:insertion_point] + links_section + content[insertion_point:]

            # Write updated content back to file
            note_path.write_text(updated_content, encoding='utf-8')
            logger.info(f"Inserted {len(suggested_links)} links into {note_path.name}")

            return updated_content

        except Exception as e:
            logger.error(f"Error inserting links: {e}")
            return content if 'content' in locals() else ""


class SafeScreenshotManager:
    """
    Utility for safe screenshot processing with backup and rollback capabilities
    
    Follows established backup patterns from directory_organizer.py P0 Backup System
    """

    def __init__(self, knowledge_path: str):
        """
        Initialize Safe Screenshot Manager
        
        Args:
            knowledge_path: Path to knowledge base root
        """
        self.knowledge_path = Path(knowledge_path)
        self.backup_root = Path.home() / "backups" / "screenshot_processing"
        self.backup_root.mkdir(parents=True, exist_ok=True)

        logger.info(f"Initialized SafeScreenshotManager with backup root: {self.backup_root}")

    def create_evening_backup(self) -> str:
        """
        Create timestamped backup before evening processing
        
        Returns:
            Path to backup directory
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"evening_screenshots_{timestamp}"
            backup_path = self.backup_root / backup_name

            # Create backup of Inbox directory (where daily notes are created)
            inbox_path = self.knowledge_path / "Inbox"
            if inbox_path.exists():
                shutil.copytree(inbox_path, backup_path / "Inbox")
                logger.info(f"Created evening backup: {backup_path}")
            else:
                # Create empty backup directory structure
                backup_path.mkdir(parents=True)
                logger.info(f"Created empty backup structure: {backup_path}")

            return str(backup_path)

        except Exception as e:
            logger.error(f"Error creating evening backup: {e}")
            # Return temporary backup path as fallback
            return str(tempfile.mkdtemp(prefix="screenshot_backup_"))

    def rollback_from_backup(self, backup_path: str) -> bool:
        """
        Rollback from backup in case of processing failure
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            True if rollback successful
        """
        try:
            backup_dir = Path(backup_path)
            if not backup_dir.exists():
                logger.warning(f"Backup directory does not exist: {backup_path}")
                return False

            inbox_backup = backup_dir / "Inbox"
            inbox_current = self.knowledge_path / "Inbox"

            if inbox_backup.exists() and inbox_current.exists():
                # Remove current Inbox and restore from backup
                shutil.rmtree(inbox_current)
                shutil.copytree(inbox_backup, inbox_current)
                logger.info(f"Successfully rolled back from backup: {backup_path}")
                return True
            else:
                logger.warning("Backup or current Inbox directory missing, skipping rollback")
                return False

        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return False

    def deduplicate_screenshots(self, screenshot_paths: List[str]) -> List[str]:
        """
        Remove duplicate screenshots from processing list
        
        Args:
            screenshot_paths: List of screenshot file paths
            
        Returns:
            Deduplicated list of screenshot paths
        """
        # Simple deduplication by filename
        seen_filenames = set()
        deduplicated = []

        for path in screenshot_paths:
            filename = Path(path).name
            if filename not in seen_filenames:
                seen_filenames.add(filename)
                deduplicated.append(path)
            else:
                logger.debug(f"Skipping duplicate screenshot: {filename}")

        logger.info(f"Deduplicated screenshots: {len(screenshot_paths)} → {len(deduplicated)}")
        return deduplicated
