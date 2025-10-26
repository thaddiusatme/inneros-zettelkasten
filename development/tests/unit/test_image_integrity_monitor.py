#!/usr/bin/env python3
"""
Test Suite for ImageIntegrityMonitor - Image Disappearing Bug Reproduction
RED Phase: These tests systematically reproduce the image loss bug across AI workflows
"""

import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from typing import List

# Add development directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# This import will fail until we create the class - that's the RED phase!
try:
    from src.ai.image_integrity_monitor import ImageIntegrityMonitor
except ImportError:
    # Expected to fail in RED phase
    ImageIntegrityMonitor = None

# Import existing AI classes that interact with images
try:
    from src.ai.workflow_manager import WorkflowManager
    from src.ai.llama_vision_ocr import LlamaVisionOCR
except ImportError:
    WorkflowManager = None
    LlamaVisionOCR = None


class TestImageIntegrityMonitorBugReproduction:
    """
    Test suite to systematically reproduce image disappearing bugs
    These tests SHOULD FAIL initially to demonstrate the problem
    """

    def setup_method(self):
        """Set up test environment with controlled image files"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.vault_path = self.test_dir / "test_vault"
        self.vault_path.mkdir(exist_ok=True)

        # Create test directories
        (self.vault_path / "Inbox").mkdir(exist_ok=True)
        (self.vault_path / "Permanent Notes").mkdir(exist_ok=True)
        (self.vault_path / "Literature Notes").mkdir(exist_ok=True)
        (self.vault_path / "Media").mkdir(exist_ok=True)
        (self.vault_path / "Templates").mkdir(exist_ok=True)

        # Create test images
        self.test_images = self._create_test_images()

        # Initialize monitor (will fail in RED phase)
        if ImageIntegrityMonitor:
            self.monitor = ImageIntegrityMonitor(str(self.vault_path))
        else:
            self.monitor = None

    def teardown_method(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def _create_test_images(self) -> List[Path]:
        """Create test image files for controlled testing"""
        test_images = []

        # Create sample image files (dummy content)
        image_data = b"FAKE_IMAGE_DATA_FOR_TESTING"

        for i, name in enumerate([
            "screenshot_messenger.jpg",
            "diagram_workflow.png",
            "code_snippet.png",
            "pasted_image.png"
        ]):
            image_path = self.vault_path / "Media" / name
            image_path.write_bytes(image_data + bytes(str(i), 'utf-8'))
            test_images.append(image_path)

        return test_images

    def _create_note_with_images(self, note_path: Path, image_paths: List[Path]) -> Path:
        """Create a test note with embedded image references"""
        content = """---
type: fleeting
created: 2025-09-24 22:10
status: inbox
tags:
  - test
  - image-bug-reproduction
---

# Test Note with Images

This note contains multiple image references for testing image integrity.

## Screenshot Reference
![Screenshot](Media/screenshot_messenger.jpg)

## Diagram
![[diagram_workflow.png]]

## Code Snippet
![Code](Media/code_snippet.png)

## Pasted Image
![[pasted_image.png]]

This note should preserve all images during AI processing.
"""
        note_path.write_text(content)
        return note_path

    # ============================================================================
    # RED PHASE TESTS: These SHOULD FAIL to demonstrate the bug
    # ============================================================================

    def test_image_integrity_monitor_initialization_works(self):
        """GREEN: ImageIntegrityMonitor class initializes correctly"""
        # Should not raise an error
        monitor = ImageIntegrityMonitor(str(self.vault_path))
        assert monitor is not None
        assert monitor.vault_path == Path(self.vault_path)
        assert isinstance(monitor.tracked_images, dict)
        assert isinstance(monitor.workflow_steps, list)

    def test_screenshot_ocr_processing_loses_images(self):
        """RED: Screenshot OCR processing causes image loss (BUG REPRODUCTION)"""
        pytest.skip("RED Phase: This test reproduces the actual bug - will implement in GREEN phase")

        # Create note with screenshot reference
        note_path = self.vault_path / "Inbox" / "test_screenshot_note.md"
        note_with_images = self._create_note_with_images(note_path, self.test_images)

        # Verify images exist before processing
        for image_path in self.test_images:
            assert image_path.exists(), f"Test image {image_path} should exist before processing"

        # Simulate LLaVA OCR processing (this should preserve images but currently doesn't)
        if LlamaVisionOCR:
            llava_processor = LlamaVisionOCR()
            # Process the screenshot - this is where images disappear
            result = llava_processor.analyze_screenshot(self.test_images[0])

        # EXPECTED TO FAIL: Images should still exist after processing
        for image_path in self.test_images:
            assert image_path.exists(), f"BUG: Image {image_path} disappeared during OCR processing!"

    def test_note_promotion_workflow_loses_images(self):
        """RED: Note promotion from Inbox to Permanent Notes loses images"""
        pytest.skip("RED Phase: This test reproduces the actual bug - will implement in GREEN phase")

        # Create fleeting note with images in Inbox
        note_path = self.vault_path / "Inbox" / "fleeting_with_images.md"
        note_with_images = self._create_note_with_images(note_path, self.test_images)

        # Verify images exist before promotion
        for image_path in self.test_images:
            assert image_path.exists(), f"Image {image_path} should exist before promotion"

        # Simulate note promotion workflow
        if WorkflowManager:
            workflow = WorkflowManager(str(self.vault_path))
            # This promotion process may lose images
            promotion_result = workflow.promote_fleeting_note(str(note_path), target_type="permanent")

        # EXPECTED TO FAIL: Images should still exist after promotion
        for image_path in self.test_images:
            assert image_path.exists(), f"BUG: Image {image_path} disappeared during note promotion!"

    def test_template_processing_loses_images(self):
        """RED: Template processing with Templater causes image loss"""
        pytest.skip("RED Phase: This test reproduces the actual bug - will implement in GREEN phase")

        # Create template with image references
        template_path = self.vault_path / "Templates" / "test_template.md"
        template_content = """---
type: {{type}}
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
---

# {{title}}

## Reference Images
![Screenshot](Media/screenshot_messenger.jpg)
![[diagram_workflow.png]]

Template processing should preserve image references.
"""
        template_path.write_text(template_content)

        # Verify images exist before template processing
        for image_path in self.test_images:
            assert image_path.exists(), f"Image {image_path} should exist before template processing"

        # Simulate template processing (this may cause image loss)
        # Note: This would typically involve Templater plugin processing
        processed_note_path = self.vault_path / "Inbox" / "processed_from_template.md"

        # EXPECTED TO FAIL: Images should still exist after template processing
        for image_path in self.test_images:
            assert image_path.exists(), f"BUG: Image {image_path} disappeared during template processing!"

    def test_batch_ai_processing_loses_images(self):
        """RED: Batch AI processing of multiple notes causes image loss"""
        pytest.skip("RED Phase: This test reproduces the actual bug - will implement in GREEN phase")

        # Create multiple notes with images
        notes_with_images = []
        for i in range(3):
            note_path = self.vault_path / "Inbox" / f"batch_note_{i}.md"
            notes_with_images.append(self._create_note_with_images(note_path, self.test_images))

        # Verify all images exist before batch processing
        for image_path in self.test_images:
            assert image_path.exists(), f"Image {image_path} should exist before batch processing"

        # Simulate batch AI processing
        if WorkflowManager:
            workflow = WorkflowManager(str(self.vault_path))
            # Process all notes in batch - this may cause image loss
            for note_path in notes_with_images:
                workflow.process_inbox_note(str(note_path))

        # EXPECTED TO FAIL: Images should still exist after batch processing
        for image_path in self.test_images:
            assert image_path.exists(), f"BUG: Image {image_path} disappeared during batch AI processing!"

    def test_weekly_review_automation_loses_images(self):
        """RED: Weekly review automation process causes image loss"""
        pytest.skip("RED Phase: This test reproduces the actual bug - will implement in GREEN phase")

        # Create notes that would be processed during weekly review
        note_path = self.vault_path / "Inbox" / "weekly_review_candidate.md"
        note_with_images = self._create_note_with_images(note_path, self.test_images)

        # Verify images exist before weekly review
        for image_path in self.test_images:
            assert image_path.exists(), f"Image {image_path} should exist before weekly review"

        # Simulate weekly review automation
        if WorkflowManager:
            workflow = WorkflowManager(str(self.vault_path))
            # Weekly review may include promotion, summarization, etc.
            review_result = workflow.generate_weekly_review()

        # EXPECTED TO FAIL: Images should still exist after weekly review
        for image_path in self.test_images:
            assert image_path.exists(), f"BUG: Image {image_path} disappeared during weekly review!"

    # ============================================================================
    # GREEN PHASE TESTS: Basic functionality should work
    # ============================================================================

    def test_register_image_for_monitoring_works(self):
        """GREEN: Image registration functionality works"""
        if self.monitor:
            # Should not raise an error
            self.monitor.register_image(self.test_images[0], "test_context")

            # Verify image was registered
            assert len(self.monitor.tracked_images) == 1
            image_key = str(self.test_images[0])
            assert image_key in self.monitor.tracked_images
            assert self.monitor.tracked_images[image_key]['context'] == "test_context"

    def test_verify_image_exists_works(self):
        """GREEN: Image existence verification works"""
        if self.monitor:
            # Should return True for existing images
            result = self.monitor.verify_image_exists(self.test_images[0])
            assert result is True

            # Should return False for non-existent images
            fake_image = self.vault_path / "nonexistent.jpg"
            result = self.monitor.verify_image_exists(fake_image)
            assert result is False

    def test_track_workflow_step_works(self):
        """GREEN: Workflow step tracking works"""
        if self.monitor:
            # Should not raise an error
            self.monitor.track_workflow_step("test_step", self.test_images)

            # Verify workflow step was tracked
            assert len(self.monitor.workflow_steps) == 1
            step = self.monitor.workflow_steps[0]
            assert step['step_name'] == "test_step"
            assert len(step['images']) == len(self.test_images)

    def test_generate_audit_report_works(self):
        """GREEN: Audit report generation works"""
        if self.monitor:
            # Register some images first
            for i, image in enumerate(self.test_images):
                self.monitor.register_image(image, f"context_{i}")

            # Generate report
            report = self.monitor.generate_audit_report()

            # Verify report structure (detailed report format)
            assert report['summary']['total_tracked_images'] == len(self.test_images)
            assert 'vault_path' in report
            assert 'generated_at' in report
            assert 'tracked_images' in report
            assert 'analysis' in report  # New detailed analysis section

    def test_image_integrity_validation_works(self):
        """GREEN: Comprehensive image integrity validation works"""
        if self.monitor:
            # This should track images through a complete workflow
            self.monitor.start_workflow_monitoring("test_workflow")

            # Simulate workflow steps
            self.monitor.register_images_for_workflow(self.test_images)
            self.monitor.checkpoint("pre_ai_processing")

            # Simulate AI processing (where images might disappear)
            self.monitor.checkpoint("post_ai_processing")

            # Validate all images still exist
            validation_result = self.monitor.validate_workflow_integrity()
            assert validation_result.all_images_preserved is True
            assert len(validation_result.missing_images) == 0
            assert len(validation_result.workflow_steps) > 0


if __name__ == "__main__":
    # Run the tests to see systematic failures
    pytest.main([__file__, "-v", "--tb=short"])
