"""
TDD Iteration 11 RED Phase: Samsung Capture Integration with Centralized Storage

Tests for integrating ImageAttachmentManager with Samsung screenshot capture workflow
to save new screenshots directly to attachments/YYYY-MM/ instead of scattered locations.

P0 Features:
- New screenshots go directly to attachments/YYYY-MM/
- Generated capture notes use centralized image paths
- Original scattered file cleaned up after centralization
- Existing scattered images remain untouched (no bulk migration)
- All existing tests continue passing (zero regressions)

Test Structure:
1. Core Integration Tests - ScreenshotProcessor with ImageAttachmentManager
2. Note Generation Tests - Centralized paths in generated notes
3. Cleanup Tests - Original files removed after successful centralization
4. Backward Compatibility Tests - Existing workflows preserved
5. Error Recovery Tests - Rollback on failure
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.cli.screenshot_processor import ScreenshotProcessor
from src.utils.image_attachment_manager import ImageAttachmentManager
from src.ai.llama_vision_ocr import VisionAnalysisResult


class TestSamsungCaptureCentralizedStorage(unittest.TestCase):
    """
    RED Phase Tests for Samsung Capture Integration with Centralized Storage
    
    Expected to FAIL initially - drives implementation of P0 centralized storage.
    """

    def setUp(self):
        """Set up test environment with temporary directories"""
        self.test_dir = tempfile.mkdtemp()
        self.knowledge_path = Path(self.test_dir) / "knowledge"
        self.onedrive_path = Path(self.test_dir) / "onedrive"

        # Create directory structure
        self.knowledge_path.mkdir(parents=True)
        (self.knowledge_path / "Inbox").mkdir()
        (self.knowledge_path / "attachments").mkdir()
        self.onedrive_path.mkdir()

        # Create test screenshot in OneDrive
        self.test_screenshot = self.onedrive_path / "Screenshot_20251002_120000_Chrome.jpg"
        self.test_screenshot.write_bytes(b"fake image data")

        # Initialize processor with ImageAttachmentManager integration
        self.processor = ScreenshotProcessor(
            onedrive_path=str(self.onedrive_path),
            knowledge_path=str(self.knowledge_path)
        )

    def tearDown(self):
        """Clean up test directories"""
        shutil.rmtree(self.test_dir)

    # ============================================================
    # P0-1: Core Integration Tests
    # ============================================================

    def test_screenshot_processor_initializes_image_attachment_manager(self):
        """
        Test: ScreenshotProcessor initializes ImageAttachmentManager in __init__
        
        Expected Behavior:
        - ImageAttachmentManager instance created with knowledge_path
        - Manager accessible via self.image_manager attribute
        - Zero regressions - all existing initialization preserved
        """
        # Verify ImageAttachmentManager initialized
        self.assertIsNotNone(
            getattr(self.processor, 'image_manager', None),
            "ScreenshotProcessor should have image_manager attribute"
        )

        self.assertIsInstance(
            self.processor.image_manager,
            ImageAttachmentManager,
            "image_manager should be ImageAttachmentManager instance"
        )

        # Verify correct base_path
        self.assertEqual(
            self.processor.image_manager.base_path,
            self.knowledge_path,
            "ImageAttachmentManager should use knowledge_path as base"
        )

    def test_new_screenshot_saved_to_centralized_attachments(self):
        """
        Test: New screenshot goes directly to attachments/2025-10/samsung-*.jpg
        
        Expected Behavior:
        - Screenshot copied to attachments/YYYY-MM/ (based on capture date)
        - Filename format: samsung-YYYYMMDD-HHMMSS.jpg
        - Original OneDrive file deleted after successful save
        - Returns centralized path for note generation
        """
        # Mock OCR result
        mock_ocr = VisionAnalysisResult(
            extracted_text="Sample OCR text",
            content_summary="Chrome browser screenshot",
            main_topics=['web', 'browser'],
            key_insights=['Important content'],
            suggested_connections=[],
            content_type='screenshot',
            confidence_score=0.85,
            processing_time=1.0
        )

        # Process screenshot with centralization
        with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
            mock_ocr_process.return_value = {str(self.test_screenshot): mock_ocr}

            result = self.processor.process_batch(limit=1)

        # Verify centralized file created
        expected_month_folder = self.knowledge_path / "attachments" / "2025-10"
        self.assertTrue(
            expected_month_folder.exists(),
            f"Month folder should be created: {expected_month_folder}"
        )

        # Find centralized screenshot (samsung-20251002-120000.jpg)
        centralized_files = list(expected_month_folder.glob("samsung-*.jpg"))
        self.assertEqual(
            len(centralized_files), 1,
            f"Should have exactly 1 centralized screenshot, found {len(centralized_files)}"
        )

        centralized_path = centralized_files[0]
        self.assertTrue(
            centralized_path.name.startswith("samsung-"),
            f"Filename should start with samsung-, got: {centralized_path.name}"
        )

        # Verify original OneDrive file removed (cleanup after centralization)
        self.assertFalse(
            self.test_screenshot.exists(),
            "Original OneDrive screenshot should be deleted after centralization"
        )

    def test_generated_note_uses_centralized_image_path(self):
        """
        Test: Generated capture note references centralized image path
        
        Expected Behavior:
        - Note contains: ![Screenshot](../attachments/2025-10/samsung-20251002-120000.jpg)
        - Path is relative from Inbox/ directory
        - Original OneDrive path NOT in note content
        - YAML frontmatter includes centralized screenshot reference
        """
        # Mock OCR result
        mock_ocr = VisionAnalysisResult(
            extracted_text="Sample OCR text",
            content_summary="Chrome browser screenshot",
            main_topics=['web', 'browser'],
            key_insights=['Important content'],
            suggested_connections=[],
            content_type='screenshot',
            confidence_score=0.85,
            processing_time=1.0
        )

        # Process screenshot with centralization
        with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
            mock_ocr_process.return_value = {str(self.test_screenshot): mock_ocr}

            result = self.processor.process_batch(limit=1)

        # Verify note was created
        self.assertGreater(
            len(result['individual_note_paths']), 0,
            "Should create at least one individual note"
        )

        note_path = Path(result['individual_note_paths'][0])
        self.assertTrue(note_path.exists(), f"Note should exist: {note_path}")

        # Read note content
        note_content = note_path.read_text()

        # Verify centralized path in note (relative from Inbox/)
        self.assertIn(
            "../attachments/2025-10/samsung-",
            note_content,
            "Note should reference centralized image path with ../attachments/"
        )

        # Verify original OneDrive path NOT in note
        self.assertNotIn(
            str(self.onedrive_path),
            note_content,
            "Note should NOT reference original OneDrive path"
        )

        self.assertNotIn(
            "Screenshot_20251002_120000_Chrome.jpg",
            note_content,
            "Note should NOT reference original Samsung filename"
        )

    # ============================================================
    # P0-2: Cleanup Tests
    # ============================================================

    def test_original_screenshot_deleted_after_centralization(self):
        """
        Test: Original OneDrive screenshot deleted after successful centralization
        
        Expected Behavior:
        - After processing, original file at onedrive_path no longer exists
        - Centralized copy exists in attachments/
        - No data loss - file content preserved in centralized location
        """
        # Create test screenshot with known content
        test_content = b"unique test image data 12345"
        self.test_screenshot.write_bytes(test_content)

        # Mock OCR result
        mock_ocr = VisionAnalysisResult(
            extracted_text="Test OCR",
            content_summary="Test screenshot",
            main_topics=['test'],
            key_insights=['test insight'],
            suggested_connections=[],
            content_type='screenshot',
            confidence_score=0.85,
            processing_time=1.0
        )

        # Process screenshot
        with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
            mock_ocr_process.return_value = {str(self.test_screenshot): mock_ocr}

            result = self.processor.process_batch(limit=1)

        # Verify original deleted
        self.assertFalse(
            self.test_screenshot.exists(),
            "Original OneDrive screenshot should be deleted"
        )

        # Verify centralized copy exists with same content
        centralized_files = list((self.knowledge_path / "attachments" / "2025-10").glob("samsung-*.jpg"))
        self.assertEqual(len(centralized_files), 1, "Should have centralized copy")

        centralized_content = centralized_files[0].read_bytes()
        self.assertEqual(
            centralized_content, test_content,
            "Centralized copy should have same content as original"
        )

    def test_centralization_preserves_image_quality(self):
        """
        Test: Image data integrity preserved during centralization
        
        Expected Behavior:
        - Byte-for-byte copy of original image
        - File size matches original
        - No compression or modification
        """
        # Create test image with specific content
        original_content = b"PNG\x89fake image data with binary content\x00\xFF"
        self.test_screenshot.write_bytes(original_content)
        original_size = self.test_screenshot.stat().st_size

        # Mock OCR and process
        mock_ocr = VisionAnalysisResult(
            extracted_text="Test", content_summary="Test",
            main_topics=[], key_insights=[], suggested_connections=[],
            content_type='screenshot', confidence_score=0.85, processing_time=1.0
        )

        with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
            mock_ocr_process.return_value = {str(self.test_screenshot): mock_ocr}
            self.processor.process_batch(limit=1)

        # Verify centralized image has identical content
        centralized_files = list((self.knowledge_path / "attachments" / "2025-10").glob("samsung-*.jpg"))
        self.assertEqual(len(centralized_files), 1)

        centralized_path = centralized_files[0]
        centralized_content = centralized_path.read_bytes()
        centralized_size = centralized_path.stat().st_size

        self.assertEqual(
            centralized_content, original_content,
            "Centralized image should have identical byte content"
        )
        self.assertEqual(
            centralized_size, original_size,
            "Centralized image should have identical file size"
        )

    # ============================================================
    # P0-3: Backward Compatibility Tests
    # ============================================================

    def test_existing_workflows_continue_working(self):
        """
        Test: Existing screenshot processing workflows work unchanged
        
        Expected Behavior:
        - All existing test methods continue passing
        - OCR processing unchanged
        - Note generation structure preserved
        - Only difference: image path and cleanup behavior
        """
        # Mock OCR result
        mock_ocr = VisionAnalysisResult(
            extracted_text="Backward compatibility test",
            content_summary="Testing existing workflows",
            main_topics=['compatibility', 'testing'],
            key_insights=['Everything works'],
            suggested_connections=[],
            content_type='screenshot',
            confidence_score=0.85,
            processing_time=1.0
        )

        # Process using existing API
        with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
            mock_ocr_process.return_value = {str(self.test_screenshot): mock_ocr}

            result = self.processor.process_batch(limit=1)

        # Verify all expected result keys present (backward compatibility)
        expected_keys = [
            'processed_count', 'individual_note_paths', 'processing_time',
            'tracking_stats', 'ocr_results'
        ]
        for key in expected_keys:
            self.assertIn(
                key, result,
                f"Result should contain {key} for backward compatibility"
            )

        # Verify processing succeeded
        self.assertEqual(result['processed_count'], 1)
        self.assertEqual(len(result['individual_note_paths']), 1)

    def test_no_bulk_migration_of_existing_images(self):
        """
        Test: Existing scattered images remain untouched (no automatic migration)
        
        Expected Behavior:
        - Only NEW screenshots processed with centralization
        - Existing scattered images in vault not affected
        - Notes referencing old scattered images still work
        - Migration is opt-in, not automatic
        """
        # Create "existing" scattered image (simulating old screenshot)
        existing_scattered = self.knowledge_path / "old_screenshot.jpg"
        existing_scattered.write_bytes(b"old scattered image")

        # Create "existing" note referencing scattered image
        existing_note = self.knowledge_path / "Inbox" / "old-note.md"
        existing_note.write_text(f"""---
type: fleeting
---

# Old Note

![Old Screenshot]({existing_scattered})
""")

        # Process NEW screenshot
        mock_ocr = VisionAnalysisResult(
            extracted_text="New screenshot",
            content_summary="New capture",
            main_topics=['new'],
            key_insights=['New content'],
            suggested_connections=[],
            content_type='screenshot',
            confidence_score=0.85,
            processing_time=1.0
        )

        with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
            mock_ocr_process.return_value = {str(self.test_screenshot): mock_ocr}

            self.processor.process_batch(limit=1)

        # Verify old scattered image UNTOUCHED
        self.assertTrue(
            existing_scattered.exists(),
            "Existing scattered image should remain untouched"
        )

        # Verify old note content UNCHANGED
        old_note_content = existing_note.read_text()
        self.assertIn(
            str(existing_scattered),
            old_note_content,
            "Old note should still reference original scattered path"
        )

    # ============================================================
    # P0-4: Error Recovery Tests
    # ============================================================

    def test_rollback_on_centralization_failure(self):
        """
        Test: If centralization fails, original screenshot preserved
        
        Expected Behavior:
        - If ImageAttachmentManager.save_to_attachments() fails
        - Original OneDrive file NOT deleted
        - Error logged and raised
        - No partial state (all-or-nothing)
        """
        # Mock ImageAttachmentManager to simulate failure
        with patch.object(
            ImageAttachmentManager, 'save_to_attachments',
            side_effect=IOError("Disk full - simulated error")
        ):
            mock_ocr = VisionAnalysisResult(
                extracted_text="Test",
                content_summary="Test",
                main_topics=[], key_insights=[], suggested_connections=[],
                content_type='screenshot', confidence_score=0.85, processing_time=1.0
            )

            with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
                mock_ocr_process.return_value = {str(self.test_screenshot): mock_ocr}

                # Processing should handle error gracefully
                try:
                    result = self.processor.process_batch(limit=1)
                except Exception:
                    pass  # Expected to fail during centralization

            # Verify original file PRESERVED (not deleted despite error)
            self.assertTrue(
                self.test_screenshot.exists(),
                "Original screenshot should be preserved if centralization fails"
            )

    def test_device_prefix_applied_correctly(self):
        """
        Test: Device-specific prefixes applied to centralized filenames
        
        Expected Behavior:
        - Samsung screenshots: samsung-YYYYMMDD-HHMMSS.jpg
        - iPad screenshots: ipad-YYYYMMDD-HHMMSS.png
        - Prefix detected automatically from filename patterns
        """
        # Test Samsung screenshot
        samsung_screenshot = self.onedrive_path / "Screenshot_20251002_143000_Messenger.jpg"
        samsung_screenshot.write_bytes(b"samsung screenshot")

        mock_ocr = VisionAnalysisResult(
            extracted_text="Samsung",
            content_summary="Samsung screenshot",
            main_topics=[], key_insights=[], suggested_connections=[],
            content_type='screenshot', confidence_score=0.85, processing_time=1.0
        )

        with patch.object(self.processor.ocr_processor, 'process_batch') as mock_ocr_process:
            mock_ocr_process.return_value = {str(samsung_screenshot): mock_ocr}

            # Mock screenshot detector to return our test screenshot
            with patch.object(
                self.processor.screenshot_detector, 'scan_todays_screenshots',
                return_value=[samsung_screenshot]
            ):
                result = self.processor.process_batch(limit=1)

        # Verify samsung- prefix
        centralized_files = list((self.knowledge_path / "attachments" / "2025-10").glob("samsung-*.jpg"))
        self.assertGreater(
            len(centralized_files), 0,
            "Should have centralized Samsung screenshot with samsung- prefix"
        )

        samsung_centralized = centralized_files[0]
        self.assertTrue(
            samsung_centralized.name.startswith("samsung-20251002-"),
            f"Samsung screenshot should have samsung- prefix, got: {samsung_centralized.name}"
        )


if __name__ == '__main__':
    unittest.main()
