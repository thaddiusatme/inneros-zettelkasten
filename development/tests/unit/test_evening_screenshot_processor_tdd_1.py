#!/usr/bin/env python3
"""
TDD Iteration 1: Samsung Screenshot Evening Workflow System - RED Phase Tests

Comprehensive failing tests for EveningScreenshotProcessor following established TDD patterns.
Building on existing OCR (llama_vision_ocr.py) and Smart Link Management (TDD Iterations 1-6).

Test Coverage:
- P0: OneDrive screenshot detection and import
- P0: OCR processing integration
- P0: Daily note generation with YAML frontmatter
- P0: Smart Link Integration for auto-MOC connections
- P1: Safety-First File Management with backup patterns
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add development directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ai.llama_vision_ocr import VisionAnalysisResult
from src.cli.evening_screenshot_processor import EveningScreenshotProcessor
from src.cli.evening_screenshot_utils import (
    OneDriveScreenshotDetector,
    ScreenshotOCRProcessor, 
    DailyNoteGenerator,
    SmartLinkIntegrator,
    SafeScreenshotManager
)


class TestEveningScreenshotProcessor(unittest.TestCase):
    """Test suite for Evening Screenshot Processor main orchestrator"""
    
    def setUp(self):
        """Set up test environment with temporary directories"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_dir = Path(self.temp_dir) / "knowledge"
        self.knowledge_dir.mkdir(parents=True)
        (self.knowledge_dir / "Inbox").mkdir()
        
        # Mock OneDrive screenshot directory
        self.onedrive_dir = Path(self.temp_dir) / "OneDrive" / "Screenshots"
        self.onedrive_dir.mkdir(parents=True)
        
        # Create test screenshot files with realistic Samsung naming pattern
        self.test_screenshots = [
            "Screenshot_20250925_180000_Instagram.jpg",
            "Screenshot_20250925_181500_Samsung Internet.jpg",
            "Screenshot_20250925_183000_Gmail.jpg"
        ]
        
        for screenshot in self.test_screenshots:
            screenshot_path = self.onedrive_dir / screenshot
            # Create minimal JPG file (empty file for testing)
            screenshot_path.write_bytes(b'\xff\xd8\xff\xe0\x00\x10JFIF')  # Minimal JPEG header
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_evening_processor_initialization_fails(self):
        """RED: Test EveningScreenshotProcessor initialization (should fail - class doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = EveningScreenshotProcessor(
                onedrive_path=str(self.onedrive_dir),
                knowledge_path=str(self.knowledge_dir)
            )
    
    def test_evening_processor_scan_screenshots_fails(self):
        """RED: Test screenshot scanning functionality (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = EveningScreenshotProcessor(
                onedrive_path=str(self.onedrive_dir),
                knowledge_path=str(self.knowledge_dir)
            )
            screenshots = processor.scan_todays_screenshots()
            self.assertGreaterEqual(len(screenshots), 3)
    
    def test_evening_processor_batch_process_fails(self):
        """RED: Test batch processing of screenshots (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = EveningScreenshotProcessor(
                onedrive_path=str(self.onedrive_dir),
                knowledge_path=str(self.knowledge_dir)
            )
            result = processor.process_evening_batch()
            self.assertIn('processed_count', result)
            self.assertIn('daily_note_path', result)
            self.assertIn('processing_time', result)


class TestOneDriveScreenshotDetector(unittest.TestCase):
    """Test suite for OneDrive screenshot detection utility"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp() 
        self.onedrive_dir = Path(self.temp_dir) / "OneDrive" / "Screenshots"
        self.onedrive_dir.mkdir(parents=True)
        
        # Create test screenshots with various dates
        self.today_screenshots = [
            f"Screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_Instagram.jpg",
            f"Screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}_Gmail.jpg"
        ]
        
        self.old_screenshots = [
            "Screenshot_20250920_120000_Facebook.jpg",
            "Screenshot_20250921_140000_Twitter.jpg"
        ]
        
        for screenshot in self.today_screenshots + self.old_screenshots:
            (self.onedrive_dir / screenshot).write_bytes(b'\xff\xd8\xff\xe0\x00\x10JFIF')
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_onedrive_detector_initialization_fails(self):
        """RED: Test OneDriveScreenshotDetector initialization (should fail - class doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            detector = OneDriveScreenshotDetector(str(self.onedrive_dir))
    
    def test_scan_todays_screenshots_fails(self):
        """RED: Test scanning today's screenshots (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            detector = OneDriveScreenshotDetector(str(self.onedrive_dir))
            screenshots = detector.scan_todays_screenshots()
            self.assertEqual(len(screenshots), 2)  # Only today's screenshots
    
    def test_samsung_naming_pattern_detection_fails(self):
        """RED: Test Samsung screenshot naming pattern detection (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            detector = OneDriveScreenshotDetector(str(self.onedrive_dir))
            is_samsung = detector.is_samsung_screenshot("Screenshot_20250925_180000_Instagram.jpg")
            self.assertTrue(is_samsung)
    
    def test_screenshot_metadata_extraction_fails(self):
        """RED: Test screenshot metadata extraction (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            detector = OneDriveScreenshotDetector(str(self.onedrive_dir))
            metadata = detector.extract_screenshot_metadata("Screenshot_20250925_180000_Instagram.jpg")
            self.assertIn('timestamp', metadata)
            self.assertIn('app_name', metadata)
            self.assertEqual(metadata['app_name'], 'Instagram')


class TestScreenshotOCRProcessor(unittest.TestCase):
    """Test suite for Screenshot OCR processing utility"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image = Path(self.temp_dir) / "test_screenshot.jpg"
        self.test_image.write_bytes(b'\xff\xd8\xff\xe0\x00\x10JFIF')  # Minimal JPEG
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_ocr_processor_initialization_fails(self):
        """RED: Test ScreenshotOCRProcessor initialization (should fail - class doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = ScreenshotOCRProcessor()
    
    def test_process_screenshot_ocr_fails(self):
        """RED: Test OCR processing of screenshot (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = ScreenshotOCRProcessor()
            result = processor.process_screenshot(self.test_image)
            self.assertIsInstance(result, VisionAnalysisResult)
    
    def test_batch_ocr_processing_fails(self):
        """RED: Test batch OCR processing (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = ScreenshotOCRProcessor()
            screenshots = [self.test_image, self.test_image]
            results = processor.process_batch(screenshots)
            self.assertEqual(len(results), 2)
    
    def test_ocr_error_handling_fails(self):
        """RED: Test OCR error handling for invalid files (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = ScreenshotOCRProcessor()
            invalid_file = Path(self.temp_dir) / "invalid.txt"
            invalid_file.write_text("not an image")
            result = processor.process_screenshot(invalid_file)
            # Should return fallback result, not crash


class TestDailyNoteGenerator(unittest.TestCase):
    """Test suite for Daily Note generation utility"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_dir = Path(self.temp_dir) / "knowledge"
        self.inbox_dir = self.knowledge_dir / "Inbox"
        self.inbox_dir.mkdir(parents=True)
        
        # Mock OCR results
        self.mock_ocr_results = [
            VisionAnalysisResult(
                extracted_text="Check out this amazing AI breakthrough!",
                content_summary="Article about AI advancements",
                main_topics=["artificial-intelligence", "technology"],
                key_insights=["AI capabilities expanding rapidly"],
                suggested_connections=["machine-learning", "automation"],
                content_type="social_media",
                confidence_score=0.85,
                processing_time=2.5
            ),
            VisionAnalysisResult(
                extracted_text="Meeting notes: Project deadline moved to next Friday",
                content_summary="Work meeting screenshot",
                main_topics=["project-management", "deadlines"],
                key_insights=["Timeline changes require adjustment"],
                suggested_connections=["workflow", "planning"],
                content_type="messaging_app",
                confidence_score=0.90,
                processing_time=1.8
            )
        ]
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_daily_note_generator_initialization_fails(self):
        """RED: Test DailyNoteGenerator initialization (should fail - class doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            generator = DailyNoteGenerator(str(self.knowledge_dir))
    
    def test_generate_daily_note_fails(self):
        """RED: Test daily note generation (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            generator = DailyNoteGenerator(str(self.knowledge_dir))
            note_path = generator.generate_daily_note(
                ocr_results=self.mock_ocr_results,
                screenshot_paths=["test1.jpg", "test2.jpg"],
                date_str="2025-09-25"
            )
            self.assertTrue(Path(note_path).exists())
    
    def test_yaml_frontmatter_generation_fails(self):
        """RED: Test YAML frontmatter generation (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            generator = DailyNoteGenerator(str(self.knowledge_dir))
            yaml_content = generator.generate_yaml_frontmatter(
                ocr_results=self.mock_ocr_results,
                screenshot_count=2
            )
            self.assertIn('type: fleeting', yaml_content)
            self.assertIn('status: inbox', yaml_content)
            self.assertIn('created:', yaml_content)
    
    def test_embedded_images_generation_fails(self):
        """RED: Test embedded image generation (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            generator = DailyNoteGenerator(str(self.knowledge_dir))
            screenshot_paths = ["screenshot1.jpg", "screenshot2.jpg"]
            embedded_content = generator.generate_embedded_images(screenshot_paths)
            self.assertIn('![](', embedded_content)


class TestSmartLinkIntegrator(unittest.TestCase):
    """Test suite for Smart Link Integration utility"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_dir = Path(self.temp_dir) / "knowledge"
        self.knowledge_dir.mkdir()
        
        # Create mock MOC files
        self.ahs_moc = self.knowledge_dir / "AHS MOC.md"
        self.ahs_moc.write_text("# AHS Business Strategy\n\n[[business-model]] [[content-creation]]")
        
        self.tech_moc = self.knowledge_dir / "Technical MOC.md" 
        self.tech_moc.write_text("# Technical Notes\n\n[[programming]] [[ai-development]]")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_smart_link_integrator_initialization_fails(self):
        """RED: Test SmartLinkIntegrator initialization (should fail - class doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            integrator = SmartLinkIntegrator(str(self.knowledge_dir))
    
    def test_suggest_moc_connections_fails(self):
        """RED: Test MOC connection suggestions (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            integrator = SmartLinkIntegrator(str(self.knowledge_dir))
            ocr_result = VisionAnalysisResult(
                extracted_text="Business strategy discussion",
                content_summary="AHS business planning",
                main_topics=["business", "strategy"], 
                key_insights=["Need better content workflow"],
                suggested_connections=["automation", "ai-tools"],
                content_type="social_media",
                confidence_score=0.80,
                processing_time=2.0
            )
            suggestions = integrator.suggest_moc_connections(ocr_result)
            self.assertGreater(len(suggestions), 0)
    
    def test_auto_link_insertion_fails(self):
        """RED: Test automatic link insertion (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            integrator = SmartLinkIntegrator(str(self.knowledge_dir))
            daily_note_path = Path(self.temp_dir) / "daily-note.md"
            daily_note_path.write_text("# Daily Screenshots\n\nContent about AI and business.")
            
            updated_content = integrator.auto_insert_links(
                daily_note_path,
                suggested_links=["[[AHS MOC]]", "[[ai-development]]"]
            )
            self.assertIn("[[AHS MOC]]", updated_content)


class TestSafeScreenshotManager(unittest.TestCase):
    """Test suite for Safe Screenshot Management utility"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_dir = Path(self.temp_dir) / "knowledge"
        self.knowledge_dir.mkdir()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_safe_manager_initialization_fails(self):
        """RED: Test SafeScreenshotManager initialization (should fail - class doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            manager = SafeScreenshotManager(str(self.knowledge_dir))
    
    def test_backup_creation_fails(self):
        """RED: Test backup creation before processing (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            manager = SafeScreenshotManager(str(self.knowledge_dir))
            backup_path = manager.create_evening_backup()
            self.assertTrue(Path(backup_path).exists())
    
    def test_rollback_capability_fails(self):
        """RED: Test rollback capability (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            manager = SafeScreenshotManager(str(self.knowledge_dir))
            backup_path = manager.create_evening_backup()
            success = manager.rollback_from_backup(backup_path)
            self.assertTrue(success)
    
    def test_deduplication_fails(self):
        """RED: Test screenshot deduplication (should fail - method doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            manager = SafeScreenshotManager(str(self.knowledge_dir))
            screenshots = ["screenshot1.jpg", "screenshot2.jpg", "screenshot1.jpg"]  # Duplicate
            deduplicated = manager.deduplicate_screenshots(screenshots)
            self.assertEqual(len(deduplicated), 2)


class TestEveningWorkflowIntegration(unittest.TestCase):
    """Test suite for integration with existing workflow systems"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.knowledge_dir = Path(self.temp_dir) / "knowledge"
        self.knowledge_dir.mkdir()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_workflow_manager_integration_fails(self):
        """RED: Test integration with WorkflowManager (should fail - integration doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = EveningScreenshotProcessor(
                onedrive_path="/fake/path",
                knowledge_path=str(self.knowledge_dir)
            )
            # Should integrate with existing WorkflowManager for AI processing
            result = processor.process_with_workflow_manager()
            self.assertIn('quality_scores', result)
            self.assertIn('ai_tags', result)
    
    def test_weekly_review_integration_fails(self):
        """RED: Test weekly review integration (should fail - integration doesn't exist)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = EveningScreenshotProcessor(
                onedrive_path="/fake/path", 
                knowledge_path=str(self.knowledge_dir)
            )
            # Should make daily notes compatible with weekly review
            daily_note = processor.generate_review_compatible_note()
            self.assertIn('status: inbox', daily_note)
    
    def test_performance_targets_fails(self):
        """RED: Test performance targets (<10 minutes for 5-20 screenshots) (should fail - no implementation)"""
        with self.assertRaises((ImportError, NameError, AttributeError)):
            processor = EveningScreenshotProcessor(
                onedrive_path="/fake/path",
                knowledge_path=str(self.knowledge_dir)
            )
            # Mock 15 screenshots
            screenshots = [f"screenshot_{i}.jpg" for i in range(15)]
            start_time = datetime.now()
            processor.process_batch_with_timing(screenshots)
            processing_time = (datetime.now() - start_time).total_seconds()
            self.assertLess(processing_time, 600)  # 10 minutes = 600 seconds


if __name__ == '__main__':
    unittest.main()
