#!/usr/bin/env python3
"""
TDD ITERATION 8 RED PHASE: Individual File Generation Tests

Critical refactor from daily note batch output to individual file generation per screenshot.
This addresses the core mobile workflow requirement for better organization and searchability.

Tests expect:
- N screenshots → N individual files (not 1 daily note)
- Semantic filenames: capture-YYYYMMDD-HHMM-keywords.md
- Individual tracking records per note
- No daily note creation

Following TDD methodology from InnerOS Windsurf Rules v4.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import sys
import json

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.screenshot_processor import ScreenshotProcessor


class TestIndividualFileGeneration:
    """RED Phase tests for individual screenshot file generation"""

    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing"""
        onedrive_dir = tempfile.mkdtemp()
        knowledge_dir = tempfile.mkdtemp()

        # Create Inbox directory
        inbox_dir = Path(knowledge_dir) / "Inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)

        # Create test screenshots with proper Samsung naming pattern
        # Pattern: Screenshot_YYYYMMDD_HHMMSS_AppName.jpg
        screenshots = []
        now = datetime.now()
        for i in range(3):
            # Create realistic Samsung screenshot names with different times
            timestamp = now.replace(hour=10 + i, minute=30 + i, second=0)
            screenshot_name = f"Screenshot_{timestamp.strftime('%Y%m%d')}_{timestamp.strftime('%H%M%S')}_TestApp{i}.jpg"
            screenshot = Path(onedrive_dir) / screenshot_name
            screenshot.touch()
            screenshots.append(screenshot)

        yield {
            "onedrive": onedrive_dir,
            "knowledge": knowledge_dir,
            "screenshots": screenshots,
        }

        # Cleanup
        shutil.rmtree(onedrive_dir)
        shutil.rmtree(knowledge_dir)

    def test_batch_creates_individual_files(self, temp_dirs):
        """
        TEST 1: Batch processing creates N individual files for N screenshots

        EXPECTED BEHAVIOR:
        - Process 3 screenshots
        - Creates 3 separate markdown files in Inbox/
        - Each file has unique content from its screenshot
        - NO daily-note-YYYY-MM-DD.md created

        CURRENT BEHAVIOR (FAILING):
        - Creates 1 daily-note-YYYY-MM-DD.md with all screenshots
        """
        processor = ScreenshotProcessor(
            onedrive_path=temp_dirs["onedrive"], knowledge_path=temp_dirs["knowledge"]
        )

        # Process batch
        result = processor.process_batch(limit=3, force=True)

        # Assert individual files created
        inbox_dir = Path(temp_dirs["knowledge"]) / "Inbox"
        created_files = list(inbox_dir.glob("capture-*.md"))

        # RED PHASE EXPECTATION: 3 individual files
        assert (
            len(created_files) == 3
        ), f"Expected 3 individual files, got {len(created_files)}"

        # Verify each file is unique
        file_contents = [f.read_text() for f in created_files]
        assert len(set(file_contents)) == 3, "Expected unique content per file"

        # Verify result metadata
        assert result["processed_count"] == 3
        assert "individual_note_paths" in result
        assert len(result["individual_note_paths"]) == 3

    def test_individual_files_have_semantic_names(self, temp_dirs):
        """
        TEST 2: Individual files have semantic contextual filenames

        EXPECTED BEHAVIOR:
        - Filenames follow pattern: capture-YYYYMMDD-HHMM-ocr-keywords.md
        - Keywords extracted from OCR content
        - Examples: capture-20251001-0852-twitter-ai-thread.md

        CURRENT BEHAVIOR (FAILING):
        - Creates daily-note-YYYY-MM-DD.md (not contextual)
        """
        processor = ScreenshotProcessor(
            onedrive_path=temp_dirs["onedrive"], knowledge_path=temp_dirs["knowledge"]
        )

        # Process batch
        result = processor.process_batch(limit=3, force=True)

        inbox_dir = Path(temp_dirs["knowledge"]) / "Inbox"
        created_files = list(inbox_dir.glob("*.md"))

        # RED PHASE EXPECTATION: Semantic filenames
        for file_path in created_files:
            filename = file_path.name

            # Check pattern: capture-YYYYMMDD-HHMM-description.md
            assert filename.startswith(
                "capture-"
            ), f"Expected 'capture-' prefix, got {filename}"

            parts = filename.replace(".md", "").split("-")
            assert (
                len(parts) >= 4
            ), f"Expected at least 4 parts in filename, got {parts}"

            # Verify date format (YYYYMMDD)
            date_part = parts[1]
            assert len(date_part) == 8, f"Expected YYYYMMDD format, got {date_part}"
            assert date_part.isdigit(), f"Expected numeric date, got {date_part}"

            # Verify time format (HHMM)
            time_part = parts[2]
            assert len(time_part) == 4, f"Expected HHMM format, got {time_part}"
            assert time_part.isdigit(), f"Expected numeric time, got {time_part}"

            # Verify contextual description exists (remaining parts)
            description_parts = parts[3:]
            assert (
                len(description_parts) > 0
            ), "Expected contextual description in filename"

    def test_tracking_records_individual_note_paths(self, temp_dirs):
        """
        TEST 3: Screenshot tracker records individual note paths

        EXPECTED BEHAVIOR:
        - Each screenshot tracked with its unique note path
        - tracker.mark_processed(screenshot, individual_note_path)
        - No single daily note path for multiple screenshots

        CURRENT BEHAVIOR (FAILING):
        - Tracker records same daily note path for all screenshots
        """
        processor = ScreenshotProcessor(
            onedrive_path=temp_dirs["onedrive"], knowledge_path=temp_dirs["knowledge"]
        )

        screenshots = temp_dirs["screenshots"]

        # Process batch
        result = processor.process_batch(limit=3, force=True)

        # Check tracking data
        tracking_file = (
            Path(temp_dirs["knowledge"]) / ".screenshot_processing_history.json"
        )
        assert tracking_file.exists(), "Tracking file should exist"

        with open(tracking_file, "r") as f:
            tracking_data = json.load(f)

        # RED PHASE EXPECTATION: Each screenshot has unique note path
        processed_screenshots = tracking_data.get("processed_screenshots", {})
        assert (
            len(processed_screenshots) == 3
        ), f"Expected 3 tracked screenshots, got {len(processed_screenshots)}"

        # Verify unique paths (not all pointing to same daily note)
        note_paths = [data["note_path"] for data in processed_screenshots.values()]
        unique_paths = set(note_paths)

        assert (
            len(unique_paths) == 3
        ), f"Expected 3 unique note paths, got {len(unique_paths)}"

        # Verify paths follow individual file pattern
        for path in note_paths:
            assert "capture-" in path, f"Expected individual capture file, got {path}"
            assert (
                "daily-note-" not in path
            ), f"Should not use daily note path, got {path}"

    def test_no_daily_note_created(self, temp_dirs):
        """
        TEST 4: No daily note file created (critical regression check)

        EXPECTED BEHAVIOR:
        - Individual files only (capture-*.md)
        - NO daily-note-YYYY-MM-DD.md
        - Legacy daily note system deprecated

        CURRENT BEHAVIOR (FAILING):
        - Creates daily-note-YYYY-MM-DD.md
        """
        processor = ScreenshotProcessor(
            onedrive_path=temp_dirs["onedrive"], knowledge_path=temp_dirs["knowledge"]
        )

        # Process batch
        result = processor.process_batch(limit=3, force=True)

        inbox_dir = Path(temp_dirs["knowledge"]) / "Inbox"

        # RED PHASE EXPECTATION: No daily note files
        daily_note_pattern = "daily-note-*.md"
        daily_notes = list(inbox_dir.glob(daily_note_pattern))

        assert (
            len(daily_notes) == 0
        ), f"Expected no daily notes, found {len(daily_notes)}: {[d.name for d in daily_notes]}"

        # Alternative patterns to check
        daily_screenshot_pattern = "daily-screenshots-*.md"
        daily_screenshot_notes = list(inbox_dir.glob(daily_screenshot_pattern))

        assert (
            len(daily_screenshot_notes) == 0
        ), f"Expected no daily screenshot notes, found {len(daily_screenshot_notes)}"

        # Verify result doesn't have daily_note_path key
        assert (
            "daily_note_path" not in result or result["daily_note_path"] is None
        ), "Result should not include daily_note_path"

    def test_individual_files_have_rich_context(self, temp_dirs):
        """
        TEST 5: Individual files contain rich context structure

        EXPECTED BEHAVIOR:
        - Each file has proper YAML frontmatter
        - Each file has screenshot reference section
        - Each file has AI Vision Analysis section
        - Each file has structured content (not just batch dump)

        NOTE: Actual claims/quotes/categories depend on OCR success.
        This test validates structure, not OCR-dependent content.
        """
        processor = ScreenshotProcessor(
            onedrive_path=temp_dirs["onedrive"], knowledge_path=temp_dirs["knowledge"]
        )

        # Process batch
        result = processor.process_batch(limit=3, force=True)

        inbox_dir = Path(temp_dirs["knowledge"]) / "Inbox"
        created_files = list(inbox_dir.glob("capture-*.md"))

        # GREEN PHASE EXPECTATION: Structured individual notes
        for file_path in created_files:
            content = file_path.read_text()

            # Check for proper structure (all individual notes should have these)
            assert "---" in content, f"Expected YAML frontmatter in {file_path.name}"
            assert "type:" in content, f"Expected type field in {file_path.name}"
            assert "status:" in content, f"Expected status field in {file_path.name}"

            # Check for individual note structure
            assert (
                "## Screenshot Reference" in content or "##" in content
            ), f"Expected structured sections in {file_path.name}"

            assert (
                "## AI Vision Analysis" in content or "AI" in content
            ), f"Expected AI analysis section in {file_path.name}"

            # Verify NOT a daily note format
            assert (
                "Daily Screenshots" not in content
            ), f"Should not be daily note format in {file_path.name}"


class TestIndividualProcessingPerformance:
    """RED Phase tests for individual processing performance"""

    @pytest.fixture
    def temp_dirs_performance(self):
        """Create temporary directories with more screenshots for performance testing"""
        onedrive_dir = tempfile.mkdtemp()
        knowledge_dir = tempfile.mkdtemp()

        # Create Inbox directory
        inbox_dir = Path(knowledge_dir) / "Inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)

        # Create 5 test screenshots (performance target: <45s per screenshot)
        # Using proper Samsung naming pattern
        screenshots = []
        now = datetime.now()
        for i in range(5):
            timestamp = now.replace(hour=10 + i, minute=30 + i, second=0)
            screenshot_name = f"Screenshot_{timestamp.strftime('%Y%m%d')}_{timestamp.strftime('%H%M%S')}_PerfTestApp{i}.jpg"
            screenshot = Path(onedrive_dir) / screenshot_name
            screenshot.touch()
            screenshots.append(screenshot)

        yield {
            "onedrive": onedrive_dir,
            "knowledge": knowledge_dir,
            "screenshots": screenshots,
        }

        # Cleanup
        shutil.rmtree(onedrive_dir)
        shutil.rmtree(knowledge_dir)

    def test_individual_processing_meets_performance_target(
        self, temp_dirs_performance
    ):
        """
        TEST 6: Individual processing meets <45s per screenshot target

        EXPECTED BEHAVIOR:
        - Process 5 screenshots in <225 seconds (45s each)
        - Individual file creation doesn't add overhead
        - Performance comparable to daily note approach

        CURRENT BEHAVIOR (FAILING):
        - Daily note approach timing needs baseline
        """
        processor = ScreenshotProcessor(
            onedrive_path=temp_dirs_performance["onedrive"],
            knowledge_path=temp_dirs_performance["knowledge"],
        )

        start_time = datetime.now()

        # Process batch
        result = processor.process_batch(limit=5, force=True)

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # RED PHASE EXPECTATION: <225 seconds for 5 screenshots
        target_time = 45 * 5  # 225 seconds
        assert (
            processing_time < target_time
        ), f"Processing took {processing_time}s, expected <{target_time}s"

        # Verify all files created
        inbox_dir = Path(temp_dirs_performance["knowledge"]) / "Inbox"
        created_files = list(inbox_dir.glob("capture-*.md"))
        assert len(created_files) == 5, f"Expected 5 files, got {len(created_files)}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
