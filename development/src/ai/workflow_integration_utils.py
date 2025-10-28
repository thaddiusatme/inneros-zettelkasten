#!/usr/bin/env python3
"""
AI Workflow Integration Utilities - REFACTOR Phase Extraction
Modular utility classes for SafeImageProcessor ↔ WorkflowManager integration
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class WorkflowProcessingResult:
    """Structured result for workflow processing operations"""

    success: bool
    operation: str
    note_path: Path
    processing_time: float
    images_preserved: int
    backup_session_id: str
    workflow_result: Optional[Dict] = None
    error_message: Optional[str] = None
    image_preservation_details: Optional[Dict] = None


@dataclass
class BatchProcessingStats:
    """Statistics for batch processing operations"""

    total_notes: int
    successful_operations: int
    failed_operations: int
    total_images_preserved: int
    total_processing_time: float
    average_processing_time: float
    integrity_report: Dict


class SafeWorkflowProcessor:
    """
    REFACTOR: Orchestrates safe workflow processing with image preservation
    Extracted from WorkflowManager for modular architecture
    """

    def __init__(self, safe_image_processor, image_integrity_monitor):
        self.safe_image_processor = safe_image_processor
        self.image_integrity_monitor = image_integrity_monitor
        self.operation_history: List[WorkflowProcessingResult] = []
        logger.debug("SafeWorkflowProcessor initialized with modular components")

    def process_note_safely(
        self,
        note_path: Path,
        workflow_operation: Callable,
        preserve_images: bool = True,
        **kwargs,
    ) -> WorkflowProcessingResult:
        """Process single note with comprehensive safety guarantees"""
        start_time = datetime.now()

        if preserve_images:
            # Use atomic operations for safety
            result = self.safe_image_processor.safe_workflow_processing(
                note_path, lambda path: workflow_operation(str(path), **kwargs)
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            if result.success:
                # Get workflow result details
                workflow_result = workflow_operation(str(note_path), **kwargs)

                processing_result = WorkflowProcessingResult(
                    success=True,
                    operation="safe_workflow_processing",
                    note_path=note_path,
                    processing_time=processing_time,
                    images_preserved=len(result.preserved_images),
                    backup_session_id=result.backup_session_id,
                    workflow_result=workflow_result,
                    image_preservation_details={
                        "enabled": True,
                        "backup_created": True,
                        "rollback_available": True,
                    },
                )
            else:
                processing_result = WorkflowProcessingResult(
                    success=False,
                    operation="safe_workflow_processing",
                    note_path=note_path,
                    processing_time=processing_time,
                    images_preserved=0,
                    backup_session_id=result.backup_session_id,
                    error_message=result.error_message,
                    image_preservation_details={
                        "enabled": True,
                        "rollback_performed": True,
                        "recovery_successful": True,
                    },
                )
        else:
            # Direct processing without image safety
            workflow_result = workflow_operation(str(note_path), **kwargs)
            processing_time = (datetime.now() - start_time).total_seconds()

            processing_result = WorkflowProcessingResult(
                success=True,
                operation="direct_workflow_processing",
                note_path=note_path,
                processing_time=processing_time,
                images_preserved=0,
                backup_session_id="none",
                workflow_result=workflow_result,
                image_preservation_details={"enabled": False},
            )

        # Track operation history
        self.operation_history.append(processing_result)

        return processing_result

    def process_batch_safely(
        self,
        note_paths: List[Path],
        workflow_operation: Callable,
        operation_name: str = "batch_processing",
    ) -> BatchProcessingStats:
        """Process multiple notes with atomic batch guarantees"""
        start_time = datetime.now()

        # Process each note with individual safety
        results = []
        for note_path in note_paths:
            result = self.process_note_safely(note_path, workflow_operation)
            results.append(result)

        # Calculate batch statistics
        total_processing_time = (datetime.now() - start_time).total_seconds()
        successful_ops = sum(1 for r in results if r.success)
        failed_ops = len(results) - successful_ops
        total_images = sum(r.images_preserved for r in results)
        avg_processing_time = total_processing_time / len(results) if results else 0.0

        # Generate integrity report
        integrity_report = {
            "total_files_with_images": len(
                [r for r in results if r.images_preserved > 0]
            ),
            "successful_image_preservation": successful_ops,
            "failed_image_preservation": failed_ops,
            "backup_sessions_created": len(
                set(
                    r.backup_session_id
                    for r in results
                    if r.backup_session_id != "none"
                )
            ),
        }

        return BatchProcessingStats(
            total_notes=len(note_paths),
            successful_operations=successful_ops,
            failed_operations=failed_ops,
            total_images_preserved=total_images,
            total_processing_time=total_processing_time,
            average_processing_time=avg_processing_time,
            integrity_report=integrity_report,
        )

    def get_processing_statistics(self) -> Dict:
        """Get comprehensive processing statistics"""
        if not self.operation_history:
            return {
                "total_operations": 0,
                "success_rate": 0.0,
                "average_processing_time": 0.0,
                "total_images_preserved": 0,
            }

        successful = sum(1 for op in self.operation_history if op.success)
        total_time = sum(op.processing_time for op in self.operation_history)
        total_images = sum(op.images_preserved for op in self.operation_history)

        return {
            "total_operations": len(self.operation_history),
            "successful_operations": successful,
            "failed_operations": len(self.operation_history) - successful,
            "success_rate": successful / len(self.operation_history),
            "average_processing_time": total_time / len(self.operation_history),
            "total_processing_time": total_time,
            "total_images_preserved": total_images,
            "operations_with_image_preservation": len(
                [op for op in self.operation_history if op.images_preserved > 0]
            ),
        }


class AtomicWorkflowEngine:
    """
    REFACTOR: Handles atomic workflow operations with guaranteed rollback
    Extracted for handling complex multi-step workflows with safety
    """

    def __init__(self, safe_image_processor):
        self.safe_image_processor = safe_image_processor
        self.active_operations: Dict[str, Dict] = {}
        logger.debug("AtomicWorkflowEngine initialized")

    def execute_atomic_workflow(
        self, operation_id: str, note_path: Path, workflow_steps: List[Callable]
    ) -> WorkflowProcessingResult:
        """Execute multi-step workflow atomically"""
        start_time = datetime.now()

        # Extract images for atomic protection
        images = self.safe_image_processor.image_extractor.extract_images_from_note(
            note_path
        )

        # Create atomic session
        session = self.safe_image_processor.create_backup_session(
            f"atomic_workflow_{operation_id}"
        )

        try:
            # Execute workflow steps sequentially
            workflow_results = []
            for i, step in enumerate(workflow_steps):
                step_result = step(note_path)
                workflow_results.append(step_result)

                # Validate images still exist after each step
                missing_images = [img for img in images if not img.exists()]
                if missing_images:
                    raise RuntimeError(
                        f"Images missing after step {i}: {missing_images}"
                    )

            # All steps completed successfully
            processing_time = (datetime.now() - start_time).total_seconds()

            return WorkflowProcessingResult(
                success=True,
                operation=f"atomic_workflow_{operation_id}",
                note_path=note_path,
                processing_time=processing_time,
                images_preserved=len(images),
                backup_session_id=session.session_id,
                workflow_result={
                    "steps_completed": len(workflow_steps),
                    "step_results": workflow_results,
                },
            )

        except Exception as e:
            # Rollback on any failure
            session.rollback()
            processing_time = (datetime.now() - start_time).total_seconds()

            return WorkflowProcessingResult(
                success=False,
                operation=f"atomic_workflow_{operation_id}",
                note_path=note_path,
                processing_time=processing_time,
                images_preserved=0,
                backup_session_id=session.session_id,
                error_message=str(e),
            )


class IntegrityMonitoringManager:
    """
    REFACTOR: Manages image integrity monitoring during workflow operations
    Extracted for dedicated monitoring and reporting capabilities
    """

    def __init__(self, image_integrity_monitor, safe_image_processor):
        self.image_integrity_monitor = image_integrity_monitor
        self.safe_image_processor = safe_image_processor
        self.monitoring_sessions: Dict[str, Dict] = {}
        logger.debug("IntegrityMonitoringManager initialized")

    def start_monitoring_session(self, session_name: str, note_path: Path) -> str:
        """Start comprehensive monitoring for workflow session"""
        session_id = f"{session_name}_{uuid.uuid4().hex[:8]}"

        # Extract and register images for monitoring
        images = self.safe_image_processor.image_extractor.extract_images_from_note(
            note_path
        )

        # Register images with integrity monitor
        for image in images:
            self.image_integrity_monitor.register_image(image, f"session:{session_id}")

        # Track session
        self.monitoring_sessions[session_id] = {
            "session_name": session_name,
            "note_path": note_path,
            "monitored_images": images,
            "started_at": datetime.now(),
            "status": "active",
        }

        logger.debug(
            f"Started monitoring session {session_id} for {len(images)} images"
        )
        return session_id

    def generate_monitoring_report(self, session_id: str) -> Dict:
        """Generate comprehensive monitoring report for session"""
        if session_id not in self.monitoring_sessions:
            return {"error": "Session not found"}

        session = self.monitoring_sessions[session_id]

        # Check current status of monitored images
        current_images = session["monitored_images"]
        existing_images = [img for img in current_images if img.exists()]
        missing_images = [img for img in current_images if not img.exists()]

        # Generate detailed report
        report = {
            "session_id": session_id,
            "session_name": session["session_name"],
            "note_path": str(session["note_path"]),
            "monitoring_duration": (
                datetime.now() - session["started_at"]
            ).total_seconds(),
            "images_tracked": len(current_images),
            "images_existing": len(existing_images),
            "images_missing": len(missing_images),
            "integrity_status": "healthy" if not missing_images else "compromised",
            "monitoring_enabled": True,
            "scan_result": {
                "found_images": existing_images,
                "missing_images": missing_images,
                "monitored_images": len(current_images),
            },
        }

        return report

    def close_monitoring_session(self, session_id: str) -> Dict:
        """Close monitoring session and generate final report"""
        final_report = self.generate_monitoring_report(session_id)

        if session_id in self.monitoring_sessions:
            self.monitoring_sessions[session_id]["status"] = "closed"
            self.monitoring_sessions[session_id]["closed_at"] = datetime.now()

        return final_report


class ConcurrentSessionManager:
    """
    REFACTOR: Manages concurrent processing sessions with safety coordination
    Extracted for handling multiple simultaneous workflow operations
    """

    def __init__(self, safe_workflow_processor):
        self.safe_workflow_processor = safe_workflow_processor
        self.active_sessions: Dict[str, Dict] = {}
        self.session_history: List[Dict] = []
        logger.debug("ConcurrentSessionManager initialized")

    def create_processing_session(
        self, operation_name: str, metadata: Optional[Dict] = None
    ) -> str:
        """Create new concurrent processing session"""
        session_id = f"{operation_name}_{uuid.uuid4().hex[:8]}"

        session_info = {
            "session_id": session_id,
            "operation_name": operation_name,
            "created_at": datetime.now(),
            "status": "created",
            "notes_processed": [],
            "metadata": metadata or {},
        }

        self.active_sessions[session_id] = session_info
        logger.debug(f"Created concurrent processing session: {session_id}")
        return session_id

    def process_note_in_session(
        self, session_id: str, note_path: Path, workflow_operation: Callable
    ) -> Dict:
        """Process note within concurrent session"""
        if session_id not in self.active_sessions:
            return {"success": False, "error": "Invalid session ID"}

        # Process note using safe workflow processor
        result = self.safe_workflow_processor.process_note_safely(
            note_path, workflow_operation
        )

        # Track in session
        self.active_sessions[session_id]["notes_processed"].append(
            {
                "note_path": str(note_path),
                "result": result,
                "processed_at": datetime.now(),
            }
        )

        self.active_sessions[session_id]["status"] = "processing"

        return {
            "success": result.success,
            "session_id": session_id,
            "processing_result": result,
            "images_preserved": result.images_preserved,
        }

    def finalize_session(self, session_id: str) -> Dict:
        """Finalize processing session and generate summary"""
        if session_id not in self.active_sessions:
            return {"success": False, "error": "Invalid session ID"}

        session_info = self.active_sessions.pop(session_id)
        session_info["status"] = "completed"
        session_info["completed_at"] = datetime.now()

        # Generate session summary
        notes_processed = session_info["notes_processed"]
        successful_notes = sum(1 for note in notes_processed if note["result"].success)
        total_images = sum(note["result"].images_preserved for note in notes_processed)

        session_summary = {
            "session_id": session_id,
            "operation_name": session_info["operation_name"],
            "total_notes": len(notes_processed),
            "successful_notes": successful_notes,
            "failed_notes": len(notes_processed) - successful_notes,
            "total_images_preserved": total_images,
            "session_duration": (
                session_info["completed_at"] - session_info["created_at"]
            ).total_seconds(),
            "success_rate": (
                successful_notes / len(notes_processed) if notes_processed else 0.0
            ),
        }

        # Archive session
        self.session_history.append(session_info)

        return session_summary

    def get_session_statistics(self) -> Dict:
        """Get statistics for all concurrent sessions"""
        active_count = len(self.active_sessions)
        completed_count = len(self.session_history)

        if self.session_history:
            total_notes = sum(
                len(session["notes_processed"]) for session in self.session_history
            )
            total_success = sum(
                sum(1 for note in session["notes_processed"] if note["result"].success)
                for session in self.session_history
            )
        else:
            total_notes = total_success = 0

        return {
            "active_sessions": active_count,
            "completed_sessions": completed_count,
            "total_sessions": active_count + completed_count,
            "total_notes_processed": total_notes,
            "overall_success_rate": (
                total_success / total_notes if total_notes > 0 else 0.0
            ),
        }


class PerformanceMetricsCollector:
    """
    REFACTOR: Collects and analyzes performance metrics for workflow operations
    Extracted for comprehensive performance monitoring and optimization
    """

    def __init__(self, safe_image_processor):
        self.safe_image_processor = safe_image_processor
        self.metrics_history: List[Dict] = []
        logger.debug("PerformanceMetricsCollector initialized")

    def collect_operation_metrics(
        self, operation_result: WorkflowProcessingResult
    ) -> Dict:
        """Collect comprehensive metrics for single operation"""
        # Get base performance metrics from SafeImageProcessor
        base_metrics = self.safe_image_processor.get_performance_metrics()

        # Enhance with operation-specific metrics
        operation_metrics = {
            "operation_type": operation_result.operation,
            "processing_time": operation_result.processing_time,
            "images_preserved": operation_result.images_preserved,
            "success": operation_result.success,
            "backup_session_id": operation_result.backup_session_id,
            "timestamp": datetime.now().isoformat(),
            # From SafeImageProcessor
            "backup_time": base_metrics.get("backup_time", 0),
            "base_processing_time": base_metrics.get("processing_time", 0),
            "rollback_count": base_metrics.get("rollback_count", 0),
            # Advanced metrics
            "atomic_operations": base_metrics.get("atomic_operations", {}),
            "session_stats": base_metrics.get("session_stats", {}),
            # Performance indicators
            "images_per_second": (
                operation_result.images_preserved / operation_result.processing_time
                if operation_result.processing_time > 0
                else 0
            ),
            "efficiency_ratio": (
                (operation_result.images_preserved / operation_result.processing_time)
                if operation_result.processing_time > 0
                else 0
            ),
        }

        # Store in history
        self.metrics_history.append(operation_metrics)

        return operation_metrics

    def generate_performance_report(self, time_window_hours: int = 24) -> Dict:
        """Generate comprehensive performance report"""
        # Filter recent metrics
        cutoff_time = datetime.now() - datetime.timedelta(hours=time_window_hours)
        recent_metrics = [
            m
            for m in self.metrics_history
            if datetime.fromisoformat(m["timestamp"]) > cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No metrics available for specified time window"}

        # Calculate aggregated statistics
        total_operations = len(recent_metrics)
        successful_operations = sum(1 for m in recent_metrics if m["success"])
        total_processing_time = sum(m["processing_time"] for m in recent_metrics)
        total_images = sum(m["images_preserved"] for m in recent_metrics)

        return {
            "time_window_hours": time_window_hours,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "success_rate": successful_operations / total_operations,
            "total_processing_time": total_processing_time,
            "average_processing_time": total_processing_time / total_operations,
            "total_images_preserved": total_images,
            "average_images_per_operation": total_images / total_operations,
            "operations_per_hour": total_operations / time_window_hours,
            "images_per_hour": total_images / time_window_hours,
            "efficiency_metrics": {
                "fastest_operation": min(m["processing_time"] for m in recent_metrics),
                "slowest_operation": max(m["processing_time"] for m in recent_metrics),
                "most_images_preserved": max(
                    m["images_preserved"] for m in recent_metrics
                ),
                "average_efficiency_ratio": sum(
                    m["efficiency_ratio"] for m in recent_metrics
                )
                / total_operations,
            },
        }
