#!/usr/bin/env python3
"""
SafeImageProcessor - Atomic Image Operations with Guaranteed Rollback
TDD Iteration 2 REFACTOR Phase: Production-ready implementation with modular architecture
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import uuid

# Import extracted utility classes
from .safe_image_processor_utils import (
    ImageBackupManager,
    AtomicOperationEngine,
    ImageExtractor,
    SessionManager,
    ProcessingResultBuilder,
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Result of safe image processing operation"""

    success: bool
    operation: str
    note_path: Path
    preserved_images: List[Path]
    processing_time: float
    backup_session_id: str
    error_message: Optional[str] = None


@dataclass
class BackupIntegrityCheck:
    """Result of backup integrity validation"""

    all_backups_valid: bool
    invalid_backups: List[str]
    validation_time: float


class ImageBackupSession:
    """
    RED Phase: Stub implementation for backup session management
    Atomic backup and rollback operations for image preservation
    """

    def __init__(
        self, vault_path: Path, operation_name: str, images_to_backup: List[Path]
    ):
        """Initialize backup session"""
        self.vault_path = vault_path
        self.operation_name = operation_name
        self.images_to_backup = images_to_backup
        self.session_id = str(uuid.uuid4())

        # RED Phase: Log that we're in stub mode
        logger.warning(
            "ImageBackupSession initialized in RED phase - limited functionality"
        )

    def create_backups(self):
        """GREEN Phase: Minimal implementation - create backups of images"""
        import shutil

        self.backup_dir = self.vault_path / ".image_backups" / self.session_id
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.backups = {}
        for image_path in self.images_to_backup:
            if image_path.exists():
                backup_path = self.backup_dir / image_path.name
                shutil.copy2(image_path, backup_path)
                self.backups[str(image_path)] = backup_path
                logger.debug(f"Backed up {image_path} to {backup_path}")

    def start_monitoring(self):
        """GREEN Phase: Minimal implementation - start monitoring session"""
        self.monitoring_started = datetime.now()
        logger.debug(f"Started monitoring session: {self.session_id}")

    def commit(self):
        """GREEN Phase: Minimal implementation - commit successful operation"""
        # Clean up backup directory since operation succeeded
        import shutil

        if hasattr(self, "backup_dir") and self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
            logger.debug(f"Committed session: {self.session_id}, cleaned up backups")

    def rollback(self):
        """GREEN Phase: Minimal implementation - rollback failed operation"""
        import shutil

        if hasattr(self, "backups"):
            for original_path, backup_path in self.backups.items():
                if backup_path.exists():
                    original = Path(original_path)
                    if original.parent.exists():
                        shutil.copy2(backup_path, original)
                        logger.debug(f"Restored {original} from backup")
            logger.debug(f"Rolled back session: {self.session_id}")

    def validate_backup_integrity(self) -> BackupIntegrityCheck:
        """GREEN Phase: Minimal implementation - validate backup integrity"""
        start_time = datetime.now()
        invalid_backups = []

        if hasattr(self, "backups"):
            for original_path, backup_path in self.backups.items():
                if not backup_path.exists():
                    invalid_backups.append(str(backup_path))

        validation_time = (datetime.now() - start_time).total_seconds()

        return BackupIntegrityCheck(
            all_backups_valid=len(invalid_backups) == 0,
            invalid_backups=invalid_backups,
            validation_time=validation_time,
        )


class SafeImageProcessor:
    """
    REFACTOR Phase: Production-ready atomic image processing with modular architecture
    Provides zero-data-loss guarantees through atomic operations and automatic rollback
    """

    def __init__(self, vault_path: str):
        """Initialize SafeImageProcessor with modular utility architecture"""
        self.vault_path = Path(vault_path)

        # Initialize extracted utility classes
        self.backup_manager = ImageBackupManager(self.vault_path)
        self.atomic_engine = AtomicOperationEngine(self.backup_manager)
        self.image_extractor = ImageExtractor(self.vault_path)
        self.session_manager = SessionManager()
        self.result_builder = ProcessingResultBuilder()

        # Legacy compatibility
        self.active_sessions = {}
        self.performance_metrics = {
            "backup_time": 0.0,
            "processing_time": 0.0,
            "rollback_count": 0,
        }

        logger.info(
            f"SafeImageProcessor initialized with modular architecture for vault: {vault_path}"
        )

    def create_backup_session(self, operation_name: str) -> ImageBackupSession:
        """REFACTOR: Create backup session using modular SessionManager"""
        session_id = self.session_manager.create_session(operation_name)

        # For compatibility, create legacy session object
        session = ImageBackupSession(self.vault_path, operation_name, [])
        session.session_id = session_id
        self.active_sessions[session_id] = session

        logger.debug(f"Created backup session: {session_id}")
        return session

    def process_note_with_images(
        self, note_path: Path, operation: str
    ) -> ProcessingResult:
        """REFACTOR: Process note using modular AtomicOperationEngine"""
        start_time = datetime.now()

        # Extract images using modular ImageExtractor
        images = self.image_extractor.extract_images_from_note(note_path)

        # Define processing operation
        def processing_operation():
            # Simulate processing (verify images exist)
            return {"success": all(img.exists() for img in images)}

        # Execute atomically using modular engine
        result = self.atomic_engine.execute_atomic_operation(
            operation_name=operation, images=images, operation_func=processing_operation
        )

        # Build result using modular ProcessingResultBuilder
        processing_time = (datetime.now() - start_time).total_seconds()

        if result.success:
            return self.result_builder.build_success_result(
                operation=operation,
                note_path=note_path,
                preserved_images=images,
                processing_time=processing_time,
                backup_session_id=result.backup_session_id,
            )
        else:
            return self.result_builder.build_failure_result(
                operation=operation,
                note_path=note_path,
                processing_time=processing_time,
                backup_session_id=result.backup_session_id,
                error_message=result.error_details or "Processing failed",
            )

    def process_notes_batch(
        self, note_paths: List[Path], operation: str
    ) -> List[ProcessingResult]:
        """REFACTOR: Batch process notes using modular architecture"""
        results = []

        # Process each note individually using modular implementation
        for note_path in note_paths:
            result = self.process_note_with_images(note_path, operation)
            results.append(result)

        # Build batch summary using modular ProcessingResultBuilder
        batch_summary = self.result_builder.build_batch_results_summary(results)

        # Update performance metrics
        self.performance_metrics["processing_time"] += batch_summary[
            "total_processing_time"
        ]
        self.performance_metrics["rollback_count"] += batch_summary[
            "operations_requiring_rollback"
        ]

        logger.debug(f"Batch processing complete: {batch_summary}")
        return results

    def safe_workflow_processing(
        self, note_path: Path, workflow_operation: Callable
    ) -> ProcessingResult:
        """REFACTOR: Safe workflow processing using modular AtomicOperationEngine"""
        start_time = datetime.now()

        # Extract images using modular extractor
        images = self.image_extractor.extract_images_from_note(note_path)

        # Define workflow operation wrapper
        def workflow_wrapper():
            workflow_result = workflow_operation(note_path)
            workflow_success = bool(
                workflow_result.get("success", True)
                and not workflow_result.get("error")
            )
            # Validate both workflow success and image preservation
            return {
                "success": workflow_success and all(img.exists() for img in images),
                "workflow_result": workflow_result,
                "error": workflow_result.get("error"),
            }

        # Execute atomically using modular engine
        result = self.atomic_engine.execute_atomic_operation(
            operation_name="workflow_processing",
            images=images,
            operation_func=workflow_wrapper,
        )

        # Build result using modular builder
        processing_time = (datetime.now() - start_time).total_seconds()

        if result.success:
            return self.result_builder.build_success_result(
                operation="workflow_processing",
                note_path=note_path,
                preserved_images=images,
                processing_time=processing_time,
                backup_session_id=result.backup_session_id,
            )
        else:
            return self.result_builder.build_failure_result(
                operation="workflow_processing",
                note_path=note_path,
                processing_time=processing_time,
                backup_session_id=result.backup_session_id,
                error_message=result.error_details or "Workflow processing failed",
            )

    def get_performance_metrics(self) -> Dict:
        """REFACTOR: Enhanced performance metrics using modular components"""
        # Get base metrics
        base_metrics = self.performance_metrics.copy()

        # Add atomic engine statistics
        atomic_stats = self.atomic_engine.get_operation_stats()
        base_metrics.update(
            {
                "atomic_operations": atomic_stats,
                "session_stats": self.session_manager.get_session_stats(),
            }
        )

        return base_metrics


# REFACTOR Phase: Production-ready safety classes using modular architecture


class AtomicFileOperations:
    """REFACTOR: Production-ready atomic file operations using modular utilities"""

    def __init__(self, backup_manager: ImageBackupManager):
        self.backup_manager = backup_manager
        self.atomic_engine = AtomicOperationEngine(backup_manager)
        logger.debug("AtomicFileOperations initialized with modular architecture")

    def execute_file_operation(
        self, operation_name: str, files: List[Path], operation_func: Callable
    ):
        """Execute file operation atomically with automatic rollback"""
        return self.atomic_engine.execute_atomic_operation(
            operation_name=operation_name, images=files, operation_func=operation_func
        )


class WorkflowSafetyManager:
    """REFACTOR: Production-ready workflow safety using modular components"""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.backup_manager = ImageBackupManager(vault_path)
        self.session_manager = SessionManager()
        logger.debug("WorkflowSafetyManager initialized with modular architecture")

    def create_workflow_checkpoint(self, workflow_name: str, files: List[Path]) -> str:
        """Create safety checkpoint for workflow execution"""
        session_id = self.session_manager.create_session(f"workflow_{workflow_name}")
        backup_metadata = self.backup_manager.create_session_backup(session_id, files)

        self.session_manager.update_session_status(
            session_id,
            "checkpoint_created",
            {
                "files_backed_up": backup_metadata.images_backed_up,
                "backup_valid": backup_metadata.is_valid,
            },
        )

        return session_id

    def restore_workflow_checkpoint(self, session_id: str) -> bool:
        """Restore workflow state from checkpoint"""
        success = self.backup_manager.restore_from_backup(session_id)
        self.session_manager.update_session_status(
            session_id, "restored" if success else "restore_failed"
        )
        return success


class ConcurrentProcessingGuard:
    """REFACTOR: Production-ready concurrent processing protection"""

    def __init__(self):
        self.active_operations: Dict[str, Dict] = {}
        self.operation_locks: Dict[str, bool] = {}
        logger.debug("ConcurrentProcessingGuard initialized")

    def acquire_operation_lock(self, resource_id: str, operation_name: str) -> bool:
        """Acquire lock for resource to prevent concurrent modification"""
        if resource_id in self.operation_locks:
            logger.warning(f"Resource {resource_id} already locked by operation")
            return False

        self.operation_locks[resource_id] = True
        self.active_operations[resource_id] = {
            "operation_name": operation_name,
            "started_at": datetime.now(),
            "status": "active",
        }

        logger.debug(f"Acquired lock for resource: {resource_id}")
        return True

    def release_operation_lock(self, resource_id: str) -> bool:
        """Release lock for resource"""
        if resource_id in self.operation_locks:
            del self.operation_locks[resource_id]
            if resource_id in self.active_operations:
                self.active_operations[resource_id]["status"] = "completed"
            logger.debug(f"Released lock for resource: {resource_id}")
            return True

        return False

    def check_concurrent_access(self, resource_id: str) -> bool:
        """Check if resource has concurrent access conflicts"""
        return resource_id in self.operation_locks
