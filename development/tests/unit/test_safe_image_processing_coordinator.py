"""
ADR-002 Phase 7: SafeImageProcessingCoordinator extraction tests

RED PHASE: Comprehensive failing tests for safe image processing coordination.
Following Phase 6 success pattern with dependency injection and composition.

Test Coverage:
- Safe inbox note processing with image preservation
- Atomic operations with rollback capability
- Batch processing with integrity monitoring
- Enhanced processing with metrics collection
- Session management for concurrent processing
- Error handling and recovery scenarios
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

# This will fail until we create the coordinator
from development.src.ai.safe_image_processing_coordinator import (
    SafeImageProcessingCoordinator,
)


class TestSafeImageProcessingCoordinatorInitialization:
    """Test coordinator initialization with dependency injection."""

    def test_coordinator_initialization_with_dependencies(self):
        """Test SafeImageProcessingCoordinator accepts all required dependencies."""
        # Arrange
        safe_workflow_processor = Mock()
        atomic_workflow_engine = Mock()
        integrity_monitoring_manager = Mock()
        concurrent_session_manager = Mock()
        performance_metrics_collector = Mock()
        safe_image_processor = Mock()
        image_integrity_monitor = Mock()
        inbox_dir = Path("/test/Inbox")
        process_note_callback = Mock()
        batch_process_callback = Mock()

        # Act
        coordinator = SafeImageProcessingCoordinator(
            safe_workflow_processor=safe_workflow_processor,
            atomic_workflow_engine=atomic_workflow_engine,
            integrity_monitoring_manager=integrity_monitoring_manager,
            concurrent_session_manager=concurrent_session_manager,
            performance_metrics_collector=performance_metrics_collector,
            safe_image_processor=safe_image_processor,
            image_integrity_monitor=image_integrity_monitor,
            inbox_dir=inbox_dir,
            process_note_callback=process_note_callback,
            batch_process_callback=batch_process_callback,
        )

        # Assert
        assert coordinator.safe_workflow_processor == safe_workflow_processor
        assert coordinator.atomic_workflow_engine == atomic_workflow_engine
        assert coordinator.integrity_monitoring_manager == integrity_monitoring_manager
        assert coordinator.concurrent_session_manager == concurrent_session_manager
        assert (
            coordinator.performance_metrics_collector == performance_metrics_collector
        )
        assert coordinator.safe_image_processor == safe_image_processor
        assert coordinator.image_integrity_monitor == image_integrity_monitor
        assert coordinator.inbox_dir == inbox_dir
        assert coordinator.process_note_callback == process_note_callback
        assert coordinator.batch_process_callback == batch_process_callback


class TestSafeProcessInboxNote:
    """Test safe_process_inbox_note() delegation to SafeWorkflowProcessor."""

    def test_safe_process_delegates_to_workflow_processor(self):
        """Test safe_process_inbox_note delegates to SafeWorkflowProcessor."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        mock_result = Mock()
        mock_result.success = True
        mock_result.workflow_result = {"processed": True}
        mock_result.images_preserved = 3
        mock_result.backup_session_id = "backup-123"
        mock_result.processing_time = 0.5
        mock_result.image_preservation_details = {"status": "ok"}

        coordinator.safe_workflow_processor.process_note_safely.return_value = (
            mock_result
        )

        # Act
        result = coordinator.safe_process_inbox_note(note_path, preserve_images=True)

        # Assert
        coordinator.safe_workflow_processor.process_note_safely.assert_called_once()
        assert result["image_preservation"]["images_preserved"] == 3
        assert result["image_preservation"]["backup_session_id"] == "backup-123"

    def test_safe_process_handles_failure_gracefully(self):
        """Test safe_process_inbox_note handles processing failure."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        mock_result = Mock()
        mock_result.success = False
        mock_result.workflow_result = None
        mock_result.error_message = "Processing failed"
        mock_result.image_preservation_details = {"status": "failed"}

        coordinator.safe_workflow_processor.process_note_safely.return_value = (
            mock_result
        )

        # Act
        result = coordinator.safe_process_inbox_note(note_path)

        # Assert
        assert result["success"] is False
        assert result["error"] == "Processing failed"

    def _create_coordinator(self):
        """Helper to create coordinator with mocked dependencies."""
        return SafeImageProcessingCoordinator(
            safe_workflow_processor=Mock(),
            atomic_workflow_engine=Mock(),
            integrity_monitoring_manager=Mock(),
            concurrent_session_manager=Mock(),
            performance_metrics_collector=Mock(),
            safe_image_processor=Mock(),
            image_integrity_monitor=Mock(),
            inbox_dir=Path("/test/Inbox"),
            process_note_callback=Mock(return_value={"success": True}),
            batch_process_callback=Mock(return_value={"processed": 5}),
        )


class TestProcessInboxNoteAtomic:
    """Test process_inbox_note_atomic() with rollback capability."""

    def test_atomic_processing_with_success(self):
        """Test atomic processing completes successfully."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        mock_result = Mock()
        mock_result.success = True
        mock_result.preserved_images = ["img1.png", "img2.png"]
        mock_result.backup_session_id = "backup-456"
        mock_result.processing_time = 0.3

        coordinator.safe_image_processor.image_extractor.extract_images_from_note.return_value = [
            "img1.png",
            "img2.png",
        ]
        coordinator.safe_image_processor.process_note_with_images.return_value = (
            mock_result
        )
        coordinator.process_note_callback.return_value = {"processed": True}

        # Act
        result = coordinator.process_inbox_note_atomic(note_path)

        # Assert
        assert result["processing_successful"] is True
        assert result["images_preserved"] == 2
        assert result["backup_session_id"] == "backup-456"

    def test_atomic_processing_rollback_on_failure(self):
        """Test atomic processing performs rollback on failure."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        mock_result = Mock()
        mock_result.success = False
        mock_result.preserved_images = []
        mock_result.backup_session_id = "backup-789"
        mock_result.processing_time = 0.2
        mock_result.error_message = "Image processing failed"

        coordinator.safe_image_processor.process_note_with_images.return_value = (
            mock_result
        )

        # Act
        result = coordinator.process_inbox_note_atomic(note_path)

        # Assert
        assert result["processing_successful"] is False
        assert result["images_preserved"] == 0
        assert result["error"] == "Image processing failed"

    def _create_coordinator(self):
        """Helper to create coordinator with mocked dependencies."""
        mock_processor = Mock()
        mock_processor.image_extractor.extract_images_from_note.return_value = []

        return SafeImageProcessingCoordinator(
            safe_workflow_processor=Mock(),
            atomic_workflow_engine=Mock(),
            integrity_monitoring_manager=Mock(),
            concurrent_session_manager=Mock(),
            performance_metrics_collector=Mock(),
            safe_image_processor=mock_processor,
            image_integrity_monitor=Mock(),
            inbox_dir=Path("/test/Inbox"),
            process_note_callback=Mock(return_value={"success": True}),
            batch_process_callback=Mock(return_value={"processed": 5}),
        )


class TestSafeBatchProcessInbox:
    """Test safe_batch_process_inbox() with comprehensive integrity reporting."""

    def test_batch_processing_aggregates_results(self):
        """Test batch processing aggregates image preservation results."""
        # Arrange
        coordinator = self._create_coordinator()

        mock_results = [
            Mock(success=True, preserved_images=["img1.png", "img2.png"]),
            Mock(success=True, preserved_images=["img3.png"]),
            Mock(success=False, preserved_images=[]),
        ]

        coordinator.inbox_dir.glob.return_value = [
            Path("/test/Inbox/note1.md"),
            Path("/test/Inbox/note2.md"),
            Path("/test/Inbox/note3.md"),
        ]
        coordinator.safe_image_processor.process_notes_batch.return_value = mock_results
        coordinator.batch_process_callback.return_value = {"processed": 3}

        # Act
        result = coordinator.safe_batch_process_inbox()

        # Assert
        assert result["images_preserved_total"] == 3
        assert result["image_integrity_report"]["total_files_with_images"] == 2
        assert result["image_integrity_report"]["successful_image_preservation"] == 2
        assert result["image_integrity_report"]["failed_image_preservation"] == 1

    def test_batch_processing_with_empty_inbox(self):
        """Test batch processing handles empty inbox gracefully."""
        # Arrange
        coordinator = self._create_coordinator()
        coordinator.inbox_dir.glob.return_value = []
        coordinator.safe_image_processor.process_notes_batch.return_value = (
            []
        )  # Empty list for empty inbox
        coordinator.batch_process_callback.return_value = {"processed": 0}

        # Act
        result = coordinator.safe_batch_process_inbox()

        # Assert
        assert result["images_preserved_total"] == 0
        assert result["processed"] == 0

    def _create_coordinator(self):
        """Helper to create coordinator with mocked dependencies."""
        return SafeImageProcessingCoordinator(
            safe_workflow_processor=Mock(),
            atomic_workflow_engine=Mock(),
            integrity_monitoring_manager=Mock(),
            concurrent_session_manager=Mock(),
            performance_metrics_collector=Mock(),
            safe_image_processor=Mock(),
            image_integrity_monitor=Mock(),
            inbox_dir=Mock(),
            process_note_callback=Mock(return_value={"success": True}),
            batch_process_callback=Mock(return_value={"processed": 5}),
        )


class TestProcessInboxNoteEnhanced:
    """Test process_inbox_note_enhanced() with monitoring and metrics."""

    def test_enhanced_processing_with_monitoring_enabled(self):
        """Test enhanced processing enables integrity monitoring."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        images = ["img1.png", "img2.png", "img3.png"]
        coordinator.safe_image_processor.image_extractor.extract_images_from_note.return_value = (
            images
        )
        coordinator.process_note_callback.return_value = {"processed": True}

        # Act
        result = coordinator.process_inbox_note_enhanced(
            note_path, enable_monitoring=True
        )

        # Assert
        assert result["integrity_report"]["images_tracked"] == 3
        assert result["integrity_report"]["monitoring_enabled"] is True
        assert len(result["integrity_report"]["scan_result"]["found_images"]) == 3

    def test_enhanced_processing_with_performance_metrics(self):
        """Test enhanced processing collects performance metrics."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        metrics = {
            "backup_time": 0.1,
            "processing_time": 0.5,
            "atomic_operations": {"average_execution_time": 0.2},
        }
        coordinator.safe_image_processor.get_performance_metrics.return_value = metrics
        coordinator.process_note_callback.return_value = {"processed": True}

        # Act
        result = coordinator.process_inbox_note_enhanced(
            note_path, collect_performance_metrics=True
        )

        # Assert
        assert result["performance_metrics"]["backup_time"] == 0.1
        assert result["performance_metrics"]["processing_time"] == 0.5
        assert result["performance_metrics"]["image_operations_time"] == 0.2

    def test_enhanced_processing_with_both_features(self):
        """Test enhanced processing with monitoring and metrics enabled."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        coordinator.safe_image_processor.image_extractor.extract_images_from_note.return_value = [
            "img.png"
        ]
        coordinator.safe_image_processor.get_performance_metrics.return_value = {
            "backup_time": 0.1
        }
        coordinator.process_note_callback.return_value = {"processed": True}

        # Act
        result = coordinator.process_inbox_note_enhanced(
            note_path, enable_monitoring=True, collect_performance_metrics=True
        )

        # Assert
        assert "integrity_report" in result
        assert "performance_metrics" in result

    def _create_coordinator(self):
        """Helper to create coordinator with mocked dependencies."""
        mock_processor = Mock()
        mock_processor.image_extractor.extract_images_from_note.return_value = []
        mock_processor.get_performance_metrics.return_value = {}

        return SafeImageProcessingCoordinator(
            safe_workflow_processor=Mock(),
            atomic_workflow_engine=Mock(),
            integrity_monitoring_manager=Mock(),
            concurrent_session_manager=Mock(),
            performance_metrics_collector=Mock(),
            safe_image_processor=mock_processor,
            image_integrity_monitor=Mock(),
            inbox_dir=Path("/test/Inbox"),
            process_note_callback=Mock(return_value={"success": True}),
            batch_process_callback=Mock(return_value={"processed": 5}),
        )


class TestProcessInboxNoteSafe:
    """Test process_inbox_note_safe() with automatic backup/rollback."""

    def test_safe_processing_creates_backup_session(self):
        """Test safe processing creates backup session before processing."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        mock_session = Mock()
        mock_session.images_to_backup = ["img1.png", "img2.png"]
        coordinator.safe_image_processor.create_backup_session.return_value = (
            mock_session
        )
        coordinator.process_note_callback.return_value = {"processed": True}

        # Act
        result = coordinator.process_inbox_note_safe(note_path)

        # Assert
        coordinator.safe_image_processor.create_backup_session.assert_called_once_with(
            "safe_inbox_processing"
        )
        assert result["processing_failed"] is False

    def test_safe_processing_rollback_on_error(self):
        """Test safe processing performs rollback when processing fails."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        mock_session = Mock()
        mock_session.images_to_backup = ["img1.png"]
        coordinator.safe_image_processor.create_backup_session.return_value = (
            mock_session
        )

        # Simulate process failure
        coordinator.process_note_callback = Mock()
        coordinator.process_note_callback.return_value = {"error": "Processing failed"}

        # Act
        result = coordinator.process_inbox_note_safe(note_path)

        # Assert
        assert result["processing_failed"] is True
        assert result["rollback_successful"] is True
        assert result["images_restored"] == 1
        assert result["error"] == "Processing failed"

    def test_safe_processing_handles_exceptions(self):
        """Test safe processing handles exceptions gracefully."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"

        coordinator.safe_image_processor.create_backup_session.side_effect = Exception(
            "Backup failed"
        )

        # Act
        result = coordinator.process_inbox_note_safe(note_path)

        # Assert
        assert result["processing_failed"] is True
        assert result["rollback_successful"] is True
        assert "Backup failed" in result["error"]

    def _create_coordinator(self):
        """Helper to create coordinator with mocked dependencies."""
        mock_processor = Mock()
        mock_processor.image_extractor.extract_images_from_note.return_value = []

        return SafeImageProcessingCoordinator(
            safe_workflow_processor=Mock(),
            atomic_workflow_engine=Mock(),
            integrity_monitoring_manager=Mock(),
            concurrent_session_manager=Mock(),
            performance_metrics_collector=Mock(),
            safe_image_processor=mock_processor,
            image_integrity_monitor=Mock(),
            inbox_dir=Path("/test/Inbox"),
            process_note_callback=Mock(return_value={"success": True}),
            batch_process_callback=Mock(return_value={"processed": 5}),
        )


class TestSessionManagement:
    """Test concurrent session management for safe processing."""

    def test_start_safe_processing_session(self):
        """Test starting a new safe processing session."""
        # Arrange
        coordinator = self._create_coordinator()
        operation_name = "batch_processing"
        session_id = "session-123"

        coordinator.concurrent_session_manager.create_processing_session.return_value = (
            session_id
        )

        # Act
        result_session_id = coordinator.start_safe_processing_session(operation_name)

        # Assert
        assert result_session_id == session_id
        coordinator.concurrent_session_manager.create_processing_session.assert_called_once_with(
            operation_name
        )

    def test_process_note_in_session(self):
        """Test processing note within an active session."""
        # Arrange
        coordinator = self._create_coordinator()
        note_path = "/test/Inbox/test-note.md"
        session_id = "session-456"

        mock_result = {"processed": True, "session": session_id}
        coordinator.concurrent_session_manager.process_note_in_session.return_value = (
            mock_result
        )

        # Act
        result = coordinator.process_note_in_session(note_path, session_id)

        # Assert
        assert result["processed"] is True
        coordinator.concurrent_session_manager.process_note_in_session.assert_called_once()

    def test_commit_safe_processing_session(self):
        """Test committing and finalizing a processing session."""
        # Arrange
        coordinator = self._create_coordinator()
        session_id = "session-789"

        mock_summary = {"success": True, "notes_processed": 5}
        coordinator.concurrent_session_manager.finalize_session.return_value = (
            mock_summary
        )

        # Act
        success = coordinator.commit_safe_processing_session(session_id)

        # Assert
        assert success is True
        coordinator.concurrent_session_manager.finalize_session.assert_called_once_with(
            session_id
        )

    def test_session_workflow_end_to_end(self):
        """Test complete session workflow from start to commit."""
        # Arrange
        coordinator = self._create_coordinator()

        coordinator.concurrent_session_manager.create_processing_session.return_value = (
            "session-001"
        )
        coordinator.concurrent_session_manager.process_note_in_session.return_value = {
            "success": True
        }
        coordinator.concurrent_session_manager.finalize_session.return_value = {
            "success": True
        }

        # Act
        session_id = coordinator.start_safe_processing_session("test_operation")
        note_result = coordinator.process_note_in_session("/test/note.md", session_id)
        commit_success = coordinator.commit_safe_processing_session(session_id)

        # Assert
        assert session_id == "session-001"
        assert note_result["success"] is True
        assert commit_success is True

    def _create_coordinator(self):
        """Helper to create coordinator with mocked dependencies."""
        return SafeImageProcessingCoordinator(
            safe_workflow_processor=Mock(),
            atomic_workflow_engine=Mock(),
            integrity_monitoring_manager=Mock(),
            concurrent_session_manager=Mock(),
            performance_metrics_collector=Mock(),
            safe_image_processor=Mock(),
            image_integrity_monitor=Mock(),
            inbox_dir=Path("/test/Inbox"),
            process_note_callback=Mock(return_value={"success": True}),
            batch_process_callback=Mock(return_value={"processed": 5}),
        )


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge case scenarios."""

    def test_coordinator_handles_none_dependencies_gracefully(self):
        """Test coordinator initialization validates dependencies."""
        # This should either raise ValueError or handle None gracefully
        with pytest.raises((ValueError, AttributeError)):
            SafeImageProcessingCoordinator(
                safe_workflow_processor=None,
                atomic_workflow_engine=None,
                integrity_monitoring_manager=None,
                concurrent_session_manager=None,
                performance_metrics_collector=None,
                safe_image_processor=None,
                image_integrity_monitor=None,
                inbox_dir=None,
                process_note_callback=None,
                batch_process_callback=None,
            )

    def test_safe_process_with_invalid_path(self):
        """Test safe processing handles invalid file paths."""
        # Arrange
        coordinator = self._create_coordinator()
        invalid_path = "/nonexistent/path/note.md"

        # Mock the workflow processor to return a failure result
        mock_result = Mock()
        mock_result.success = False
        mock_result.workflow_result = None
        mock_result.error_message = "File not found"
        mock_result.image_preservation_details = {}
        coordinator.safe_workflow_processor.process_note_safely.return_value = (
            mock_result
        )

        # Act
        result = coordinator.safe_process_inbox_note(invalid_path)

        # Assert - should return error result, not crash
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "error" in result

    def _create_coordinator(self):
        """Helper to create coordinator with mocked dependencies."""
        return SafeImageProcessingCoordinator(
            safe_workflow_processor=Mock(),
            atomic_workflow_engine=Mock(),
            integrity_monitoring_manager=Mock(),
            concurrent_session_manager=Mock(),
            performance_metrics_collector=Mock(),
            safe_image_processor=Mock(),
            image_integrity_monitor=Mock(),
            inbox_dir=Path("/test/Inbox"),
            process_note_callback=Mock(return_value={"success": True}),
            batch_process_callback=Mock(return_value={"processed": 5}),
        )
