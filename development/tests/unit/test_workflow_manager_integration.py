#!/usr/bin/env python3
"""
TDD Iteration 3 - RED Phase: AI Workflow Integration Tests
Integration tests for SafeImageProcessor with WorkflowManager
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import List

from src.ai.workflow_manager import WorkflowManager


class TestWorkflowManagerImageIntegration:
    """RED Phase: Tests for integrating SafeImageProcessor with WorkflowManager"""

    def setup_method(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.vault_path = Path(self.test_dir)

        # Create test directory structure
        (self.vault_path / "Inbox").mkdir(parents=True)
        (self.vault_path / "Fleeting Notes").mkdir(parents=True)
        (self.vault_path / "Permanent Notes").mkdir(parents=True)
        (self.vault_path / "Media").mkdir(parents=True)

        # Create test notes with images
        self.test_notes = self._create_test_notes_with_images()

        # Initialize components (they don't exist yet - RED phase)
        self.workflow_manager = None
        self.safe_processor = None
        self.integrity_monitor = None

    def teardown_method(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)

    def _create_test_notes_with_images(self) -> List[Path]:
        """Create test notes containing image references"""
        notes = []

        # Test note 1: Markdown images
        note1_path = self.vault_path / "Inbox" / "test-note-with-markdown-images.md"
        note1_content = """---
type: fleeting
created: 2025-09-24 22:30
status: inbox
tags: [test, images]
---

# Test Note with Images

This note contains various image formats:

![Test Image 1](../Media/test-image-1.png)

Some text content here.

![Test Image 2](../Media/test-image-2.jpg)
"""
        note1_path.write_text(note1_content)
        notes.append(note1_path)

        # Test note 2: Wiki-style images
        note2_path = self.vault_path / "Inbox" / "test-note-with-wiki-images.md"
        note2_content = """---
type: literature
created: 2025-09-24 22:31
status: inbox
tags: [research, visual]
---

# Research Note

Important findings with supporting images:

![[research-diagram.png]]

Key insights:
- Finding 1
- Finding 2

![[data-visualization.svg]]
"""
        note2_path.write_text(note2_content)
        notes.append(note2_path)

        # Test note 3: No images (control)
        note3_path = self.vault_path / "Inbox" / "test-note-without-images.md"
        note3_content = """---
type: permanent
created: 2025-09-24 22:32
status: inbox
tags: [concept, theory]
---

# Pure Text Note

This note contains only text content with no images.

It should still be processed safely but with minimal image operations.
"""
        note3_path.write_text(note3_content)
        notes.append(note3_path)

        # Create corresponding image files
        self._create_test_images()

        return notes

    def _create_test_images(self):
        """Create test image files"""
        media_dir = self.vault_path / "Media"

        # Create simple test image files
        test_images = [
            "test-image-1.png",
            "test-image-2.jpg",
            "research-diagram.png",
            "data-visualization.svg"
        ]

        for image_name in test_images:
            image_path = media_dir / image_name
            # Create dummy image content
            image_path.write_bytes(b"dummy image content for " + image_name.encode())

    # ============================================================================
    # RED PHASE TESTS - These should all FAIL initially
    # ============================================================================

    def test_safe_workflow_manager_initialization_works(self):
        """GREEN: SafeWorkflowManager class works"""
        from src.ai.workflow_manager import SafeWorkflowManager
        manager = SafeWorkflowManager(str(self.vault_path))
        assert manager is not None
        assert hasattr(manager, 'safe_image_processor')
        assert hasattr(manager, 'image_integrity_monitor')

    def test_safe_process_inbox_note_works(self):
        """GREEN: Safe process_inbox_note method works"""
        workflow_manager = WorkflowManager(str(self.vault_path))
        # This method integrates SafeImageProcessor
        result = workflow_manager.safe_process_inbox_note(
            str(self.test_notes[0]),
            preserve_images=True
        )
        assert 'image_preservation' in result
        assert result['image_preservation']['enabled'] is True

    def test_atomic_inbox_processing_works(self):
        """GREEN: Atomic inbox processing with rollback works"""
        workflow_manager = WorkflowManager(str(self.vault_path))
        # Processes note with atomic image operations
        result = workflow_manager.process_inbox_note_atomic(
            str(self.test_notes[0])
        )
        assert 'processing_successful' in result
        assert 'images_preserved' in result
        assert 'backup_session_id' in result

    def test_safe_batch_processing_works(self):
        """GREEN: Safe batch processing with image preservation works"""
        workflow_manager = WorkflowManager(str(self.vault_path))
        # Processes all notes while preserving images atomically
        result = workflow_manager.safe_batch_process_inbox()
        assert 'total_files' in result
        assert 'images_preserved_total' in result
        assert 'image_integrity_report' in result

    def test_workflow_with_image_monitoring_works(self):
        """GREEN: Integration with ImageIntegrityMonitor works"""
        workflow_manager = WorkflowManager(str(self.vault_path))
        # Includes integrity monitoring in processing
        result = workflow_manager.process_inbox_note_enhanced(
            str(self.test_notes[0]),
            enable_monitoring=True
        )
        assert 'integrity_report' in result
        assert result['integrity_report']['monitoring_enabled'] is True

    def test_ai_processing_with_backup_rollback_works(self):
        """GREEN: AI processing with automatic backup/rollback works"""
        workflow_manager = WorkflowManager(str(self.vault_path))

        # Simulate AI processing with potential failure handling
        result = workflow_manager.process_inbox_note_safe(
            str(self.test_notes[0])
        )

        # Should handle failures gracefully
        assert 'processing_failed' in result
        assert 'rollback_successful' in result

    def test_performance_monitoring_integration_works(self):
        """GREEN: Performance monitoring for safe operations works"""
        workflow_manager = WorkflowManager(str(self.vault_path))

        # Should provide performance metrics for safe operations
        result = workflow_manager.process_inbox_note_enhanced(
            str(self.test_notes[0]),
            collect_performance_metrics=True
        )

        assert 'performance_metrics' in result
        assert 'backup_time' in result['performance_metrics']
        assert 'processing_time' in result['performance_metrics']
        assert 'image_operations_time' in result['performance_metrics']

    def test_concurrent_safe_processing_works(self):
        """GREEN: Concurrent safe processing with session management works"""
        workflow_manager = WorkflowManager(str(self.vault_path))

        # Should handle concurrent processing safely
        session_id = workflow_manager.start_safe_processing_session("batch_inbox")

        results = []
        for note in self.test_notes[:2]:  # Process subset for faster testing
            result = workflow_manager.process_note_in_session(
                str(note),
                session_id=session_id
            )
            results.append(result)

        commit_result = workflow_manager.commit_safe_processing_session(session_id)

        assert len(results) == 2
        assert commit_result is True

    def test_workflow_safety_manager_integration_fails(self):
        """RED: WorkflowSafetyManager integration doesn't exist"""
        with pytest.raises((AttributeError, TypeError)):
            workflow_manager = WorkflowManager(str(self.vault_path))

            # Should integrate with WorkflowSafetyManager for checkpoint management
            checkpoint_id = workflow_manager.create_workflow_checkpoint("ai_enhancement")

            try:
                # Process note with potential failure point
                result = workflow_manager.process_inbox_note(str(self.test_notes[0]))

                if result.get('success'):
                    workflow_manager.commit_workflow_checkpoint(checkpoint_id)
                else:
                    workflow_manager.restore_workflow_checkpoint(checkpoint_id)

            except Exception:
                restored = workflow_manager.restore_workflow_checkpoint(checkpoint_id)
                assert restored is True

    def test_enhanced_ai_processing_with_safety_fails(self):
        """RED: Enhanced AI processing with safety guarantees doesn't exist"""
        with pytest.raises((AttributeError, TypeError)):
            workflow_manager = WorkflowManager(str(self.vault_path))

            # Should provide enhanced AI processing with complete safety
            result = workflow_manager.enhanced_ai_process_note(
                str(self.test_notes[0]),
                enable_tagging=True,
                enable_enhancement=True,
                enable_summarization=True,
                safety_mode=True
            )

            assert result['ai_processing_complete'] is True
            assert result['images_preserved'] >= 2
            assert 'ai_tags' in result
            assert 'quality_score' in result
            assert 'backup_session_id' in result

    def test_workflow_integration_cli_safety_fails(self):
        """RED: CLI integration with safety flags doesn't exist"""
        with pytest.raises((AttributeError, TypeError)):
            workflow_manager = WorkflowManager(str(self.vault_path))

            # Should support CLI safety flags for all operations
            result = workflow_manager.process_inbox_note(
                str(self.test_notes[0]),
                cli_safe_mode=True,
                cli_backup_enabled=True,
                cli_monitoring_enabled=True
            )

            assert 'cli_safety_report' in result
            assert result['cli_safety_report']['backup_created'] is True
            assert result['cli_safety_report']['monitoring_active'] is True

    def test_comprehensive_error_recovery_fails(self):
        """RED: Comprehensive error recovery system doesn't exist"""
        with pytest.raises((AttributeError, TypeError)):
            workflow_manager = WorkflowManager(str(self.vault_path))

            # Should provide detailed error recovery information
            result = workflow_manager.process_inbox_note_with_recovery(
                str(self.test_notes[0])
            )

            assert 'error_recovery_plan' in result
            assert 'recovery_options' in result['error_recovery_plan']
            assert 'safety_guarantees' in result['error_recovery_plan']
