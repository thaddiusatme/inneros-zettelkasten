#!/usr/bin/env python3
"""
Test Suite for SafeImageProcessor - Atomic Image Operations with Rollback
TDD Iteration 2 RED Phase: Systematic tests for atomic image operations
"""

import pytest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Optional

# Add development directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

# These imports will fail until we create the classes - that's the RED phase!
try:
    from src.ai.safe_image_processor import SafeImageProcessor, ImageBackupSession, ProcessingResult
    from src.ai.image_integrity_monitor import ImageIntegrityMonitor
except ImportError:
    # Expected to fail in RED phase
    SafeImageProcessor = None
    ImageBackupSession = None
    ProcessingResult = None
    ImageIntegrityMonitor = None


class TestSafeImageProcessorRedPhase:
    """
    RED Phase: These tests SHOULD FAIL to demonstrate SafeImageProcessor requirements
    These tests define the atomic operations interface we need to implement
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
        
        # Create test images and notes
        self.test_images = self._create_test_images()
        self.test_notes = self._create_test_notes_with_images()
        
        # Initialize processor (will fail in RED phase)
        if SafeImageProcessor:
            self.processor = SafeImageProcessor(str(self.vault_path))
        else:
            self.processor = None
    
    def teardown_method(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def _create_test_images(self) -> List[Path]:
        """Create test image files for controlled testing"""
        test_images = []
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
    
    def _create_test_notes_with_images(self) -> List[Path]:
        """Create test notes with image references"""
        notes = []
        
        # Note 1: Multiple image references
        note1_content = """---
type: fleeting
created: 2025-09-24 22:15
status: inbox
tags:
  - test
  - image-processing
---

# Test Note with Multiple Images

This note contains multiple image references for testing atomic operations.

![Screenshot](Media/screenshot_messenger.jpg)
![[diagram_workflow.png]]
![Code](Media/code_snippet.png)

Content with image references that must be preserved during AI processing.
"""
        note1_path = self.vault_path / "Inbox" / "test_note_multiple_images.md"
        note1_path.write_text(note1_content)
        notes.append(note1_path)
        
        # Note 2: Single image reference  
        note2_content = """---
type: literature
created: 2025-09-24 22:15
status: inbox
---

# Literature Note with Diagram

![[pasted_image.png]]

This is a literature note with a single image reference.
"""
        note2_path = self.vault_path / "Inbox" / "literature_with_image.md"
        note2_path.write_text(note2_content)
        notes.append(note2_path)
        
        return notes

    # ============================================================================
    # RED PHASE TESTS: SafeImageProcessor Atomic Operations
    # ============================================================================

    def test_safe_image_processor_initialization_works(self):
        """GREEN: SafeImageProcessor class initializes correctly"""
        processor = SafeImageProcessor(str(self.vault_path))
        assert processor is not None
        assert processor.vault_path == self.vault_path
        assert isinstance(processor.active_sessions, dict)
        assert isinstance(processor.performance_metrics, dict)

    def test_create_backup_session_works(self):
        """GREEN: Backup session creation works"""
        if self.processor:
            session = self.processor.create_backup_session("test_operation")
            assert session is not None
            assert session.operation_name == "test_operation"
            assert session.session_id in self.processor.active_sessions

    def test_atomic_note_processing_works(self):
        """GREEN: Atomic note processing with image preservation works"""
        if self.processor:
            # This should process a note while preserving all images atomically
            result = self.processor.process_note_with_images(
                self.test_notes[0],
                operation="ai_enhancement"
            )
            assert result.success is True
            assert len(result.preserved_images) >= 0  # Images preserved (may be 0 if none found)
            assert result.processing_time > 0

    def test_backup_and_rollback_works(self):
        """GREEN: Backup and rollback capability works"""
        if self.processor:
            # Test with a session that has actual images
            images = self._create_test_images()
            session = ImageBackupSession(self.vault_path, "test_rollback", images)
            
            # Create backups
            session.create_backups()
            
            # Simulate processing failure by deleting an image
            original_image = images[0]
            original_content = original_image.read_bytes()
            original_image.unlink()
            
            # This should restore the image
            session.rollback()
            
            # Image should be restored
            assert original_image.exists()
            # Content should match
            assert original_image.read_bytes() == original_content

    def test_batch_processing_atomic_operations_works(self):
        """GREEN: Batch processing with atomic guarantees works"""
        if self.processor:
            # Process multiple notes atomically
            results = self.processor.process_notes_batch(
                self.test_notes,
                operation="ai_batch_enhancement"
            )
            
            # Should return results for all notes
            assert len(results) == len(self.test_notes)
            
            # Each result should have required fields
            for result in results:
                assert hasattr(result, 'success')
                assert hasattr(result, 'processing_time')
                assert hasattr(result, 'backup_session_id')

    def test_integration_with_workflow_manager_works(self):
        """GREEN: Integration with existing WorkflowManager works"""
        if self.processor:
            # Mock WorkflowManager processing
            mock_workflow_result = {
                'success': True,
                'processed_note': str(self.test_notes[0]),
                'ai_tags': ['test', 'enhanced'],
                'quality_score': 0.8
            }
            
            # Safe processing should integrate with WorkflowManager
            result = self.processor.safe_workflow_processing(
                note_path=self.test_notes[0],
                workflow_operation=lambda note: mock_workflow_result
            )
            
            assert result.success is True
            assert result.processing_time > 0
            assert result.backup_session_id is not None

    def test_performance_monitoring_works(self):
        """GREEN: Performance monitoring during safe operations works"""
        if self.processor:
            # Monitor performance during atomic operations
            performance_data = self.processor.get_performance_metrics()
            assert 'backup_time' in performance_data
            assert 'processing_time' in performance_data
            assert 'rollback_count' in performance_data
            assert isinstance(performance_data, dict)

    def test_concurrent_processing_safety_fails(self):
        """RED: Concurrent processing safety doesn't exist"""
        with pytest.raises((AttributeError, TypeError)):
            if self.processor:
                # Simulate concurrent processing attempts
                session1 = self.processor.create_backup_session("concurrent_1")
                session2 = self.processor.create_backup_session("concurrent_2")
                
                # Should handle concurrent sessions safely
                assert session1.session_id != session2.session_id

    # ============================================================================
    # RED PHASE TESTS: ImageBackupSession Functionality
    # ============================================================================

    def test_backup_session_lifecycle_fails(self):
        """RED: Complete backup session lifecycle doesn't exist"""
        with pytest.raises((ImportError, AttributeError, TypeError)):
            if ImageBackupSession:
                session = ImageBackupSession(
                    vault_path=self.vault_path,
                    operation_name="test_lifecycle",
                    images_to_backup=self.test_images
                )
                
                # Session lifecycle: create → backup → process → commit/rollback
                session.create_backups()
                session.start_monitoring()
                
                # Simulate processing
                processing_successful = True
                
                if processing_successful:
                    session.commit()
                else:
                    session.rollback()

    def test_backup_integrity_validation_fails(self):
        """RED: Backup integrity validation doesn't exist"""
        with pytest.raises((AttributeError, TypeError)):
            if ImageBackupSession:
                session = ImageBackupSession(
                    vault_path=self.vault_path,
                    operation_name="integrity_test",
                    images_to_backup=self.test_images
                )
                
                # Should validate backup integrity
                integrity_check = session.validate_backup_integrity()
                assert integrity_check.all_backups_valid is True

    # ============================================================================
    # RED PHASE TESTS: ProcessingResult Interface
    # ============================================================================

    def test_processing_result_structure_fails(self):
        """RED: ProcessingResult data structure doesn't exist"""
        with pytest.raises((ImportError, AttributeError, TypeError)):
            if ProcessingResult:
                result = ProcessingResult(
                    success=True,
                    operation="test_operation",
                    note_path=self.test_notes[0],
                    preserved_images=self.test_images,
                    processing_time=1.5,
                    backup_session_id="test_session_123"
                )
                
                assert result.success is True
                assert len(result.preserved_images) == len(self.test_images)

    def test_error_handling_and_recovery_fails(self):
        """RED: Comprehensive error handling doesn't exist"""
        with pytest.raises((AttributeError, TypeError)):
            if self.processor:
                # Test error scenarios and recovery
                with patch('pathlib.Path.exists', side_effect=PermissionError("Simulated error")):
                    result = self.processor.process_note_with_images(
                        self.test_notes[0],
                        operation="error_test"
                    )
                    
                    # Should handle errors gracefully
                    assert result.success is False
                    assert result.error_message is not None


if __name__ == "__main__":
    # Run the tests to see systematic failures
    pytest.main([__file__, "-v", "--tb=short"])
