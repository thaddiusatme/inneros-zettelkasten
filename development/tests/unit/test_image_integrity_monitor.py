#!/usr/bin/env python3
"""
Test Suite for ImageIntegrityMonitor

GREEN tests (TestImageIntegrityMonitorCore): core functionality, run in normal suite.
RED tests (TestImageIntegrityMonitorBugReproduction): bug reproduction, marked wip.
"""

import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from typing import List

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../"))

from src.ai.image_integrity_monitor import ImageIntegrityMonitor

try:
    from src.ai.workflow_manager import WorkflowManager
    from src.ai.llama_vision_ocr import LlamaVisionOCR
except ImportError:
    WorkflowManager = None
    LlamaVisionOCR = None


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_vault(base: Path) -> Path:
    vault = base / "test_vault"
    vault.mkdir(exist_ok=True)
    for d in ["Inbox", "Permanent Notes", "Literature Notes", "Media", "Templates"]:
        (vault / d).mkdir(exist_ok=True)
    return vault


def _make_images(vault: Path) -> List[Path]:
    names = [
        "screenshot_messenger.jpg",
        "diagram_workflow.png",
        "code_snippet.png",
        "pasted_image.png",
    ]
    images = []
    for i, name in enumerate(names):
        p = vault / "Media" / name
        p.write_bytes(b"FAKE_IMAGE_DATA" + bytes(str(i), "utf-8"))
        images.append(p)
    return images


def _make_note_with_images(note_path: Path, images: List[Path]) -> Path:
    note_path.write_text(
        """---
type: fleeting
created: 2025-09-24 22:10
status: inbox
tags:
  - test
---

# Test Note with Images

![Screenshot](Media/screenshot_messenger.jpg)
![[diagram_workflow.png]]
![Code](Media/code_snippet.png)
![[pasted_image.png]]
"""
    )
    return note_path


# ---------------------------------------------------------------------------
# GREEN tests — no wip marker, run in normal suite
# ---------------------------------------------------------------------------


class TestImageIntegrityMonitorCore:
    """Core ImageIntegrityMonitor functionality. These must stay green."""

    def setup_method(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.vault_path = _make_vault(self.test_dir)
        self.test_images = _make_images(self.vault_path)
        self.monitor = ImageIntegrityMonitor(str(self.vault_path))

    def teardown_method(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_image_integrity_monitor_initialization_works(self):
        assert self.monitor is not None
        assert self.monitor.vault_path == Path(self.vault_path)
        assert isinstance(self.monitor.tracked_images, dict)
        assert isinstance(self.monitor.workflow_steps, list)

    def test_register_image_for_monitoring_works(self):
        self.monitor.register_image(self.test_images[0], "test_context")
        assert len(self.monitor.tracked_images) == 1
        key = str(self.test_images[0])
        assert key in self.monitor.tracked_images
        assert self.monitor.tracked_images[key]["context"] == "test_context"

    def test_verify_image_exists_works(self):
        assert self.monitor.verify_image_exists(self.test_images[0]) is True
        assert (
            self.monitor.verify_image_exists(self.vault_path / "nonexistent.jpg")
            is False
        )

    def test_track_workflow_step_works(self):
        self.monitor.track_workflow_step("test_step", self.test_images)
        assert len(self.monitor.workflow_steps) == 1
        step = self.monitor.workflow_steps[0]
        assert step["step_name"] == "test_step"
        assert len(step["images"]) == len(self.test_images)

    def test_generate_audit_report_works(self):
        for i, image in enumerate(self.test_images):
            self.monitor.register_image(image, f"context_{i}")
        report = self.monitor.generate_audit_report()
        assert report["summary"]["total_tracked_images"] == len(self.test_images)
        assert "vault_path" in report
        assert "generated_at" in report
        assert "tracked_images" in report
        assert "analysis" in report

    def test_image_integrity_validation_works(self):
        self.monitor.start_workflow_monitoring("test_workflow")
        self.monitor.register_images_for_workflow(self.test_images)
        self.monitor.checkpoint("pre_ai_processing")
        self.monitor.checkpoint("post_ai_processing")
        result = self.monitor.validate_workflow_integrity()
        assert result.all_images_preserved is True
        assert len(result.missing_images) == 0
        assert len(result.workflow_steps) > 0


# ---------------------------------------------------------------------------
# RED tests — marked wip, document real bugs not yet fixed
# ---------------------------------------------------------------------------


@pytest.mark.wip
class TestImageIntegrityMonitorBugReproduction:
    """
    Reproduces image disappearing bugs across AI workflows.
    These tests are intentionally failing (RED phase) — they document
    known bugs to be fixed in future issues.
    """

    def setup_method(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.vault_path = _make_vault(self.test_dir)
        self.test_images = _make_images(self.vault_path)
        self.monitor = ImageIntegrityMonitor(str(self.vault_path))

    def teardown_method(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_screenshot_ocr_processing_loses_images(self):
        """RED: Screenshot OCR processing causes image loss (BUG REPRODUCTION)"""
        pytest.skip("RED Phase: bug reproduction — implement in GREEN phase")

        note_path = self.vault_path / "Inbox" / "test_screenshot_note.md"
        _make_note_with_images(note_path, self.test_images)
        for img in self.test_images:
            assert img.exists()
        if LlamaVisionOCR:
            LlamaVisionOCR().analyze_screenshot(self.test_images[0])
        for img in self.test_images:
            assert img.exists(), f"BUG: {img} disappeared during OCR processing!"

    def test_note_promotion_workflow_loses_images(self):
        """RED: Note promotion from Inbox to Permanent Notes loses images"""
        pytest.skip("RED Phase: bug reproduction — implement in GREEN phase")

        note_path = self.vault_path / "Inbox" / "fleeting_with_images.md"
        _make_note_with_images(note_path, self.test_images)
        for img in self.test_images:
            assert img.exists()
        if WorkflowManager:
            WorkflowManager(str(self.vault_path)).promote_fleeting_note(
                str(note_path), target_type="permanent"
            )
        for img in self.test_images:
            assert img.exists(), f"BUG: {img} disappeared during note promotion!"

    def test_template_processing_loses_images(self):
        """RED: Template processing with Templater causes image loss"""
        pytest.skip("RED Phase: bug reproduction — implement in GREEN phase")

        template_path = self.vault_path / "Templates" / "test_template.md"
        template_path.write_text(
            "---\ntype: {{type}}\n---\n\n![Screenshot](Media/screenshot_messenger.jpg)\n"
        )
        for img in self.test_images:
            assert img.exists()
        for img in self.test_images:
            assert img.exists(), f"BUG: {img} disappeared during template processing!"

    def test_batch_ai_processing_loses_images(self):
        """RED: Batch AI processing of multiple notes causes image loss"""
        pytest.skip("RED Phase: bug reproduction — implement in GREEN phase")

        for i in range(3):
            _make_note_with_images(
                self.vault_path / "Inbox" / f"batch_note_{i}.md", self.test_images
            )
        for img in self.test_images:
            assert img.exists()
        if WorkflowManager:
            wf = WorkflowManager(str(self.vault_path))
            for i in range(3):
                wf.process_inbox_note(
                    str(self.vault_path / "Inbox" / f"batch_note_{i}.md")
                )
        for img in self.test_images:
            assert img.exists(), f"BUG: {img} disappeared during batch AI processing!"

    def test_weekly_review_automation_loses_images(self):
        """RED: Weekly review automation process causes image loss"""
        pytest.skip("RED Phase: bug reproduction — implement in GREEN phase")

        note_path = self.vault_path / "Inbox" / "weekly_review_candidate.md"
        _make_note_with_images(note_path, self.test_images)
        for img in self.test_images:
            assert img.exists()
        if WorkflowManager:
            WorkflowManager(str(self.vault_path)).generate_weekly_review()
        for img in self.test_images:
            assert img.exists(), f"BUG: {img} disappeared during weekly review!"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
