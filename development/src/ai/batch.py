"""
batch — user-invoked orchestration for multi-note workflows.

Consolidates workflow_manager, batch_processing_coordinator,
batch_inbox_processor, note_processing_coordinator,
workflow_integration_utils, and workflow_reporting_coordinator (issue #120).

Single import point for all batch/orchestration concerns. Does not own the
event loop — daemon/file-watching concerns are handled separately.

Import boundary: imports from enrichment, analytics, connections_discovery,
llm_client, and lifecycle modules. Does NOT import from the old split files
(tagger, summarizer, enhancer, connections, connection_coordinator).
"""

# ===========================================================================
# workflow_integration_utils — result types + safe/atomic/monitoring helpers
# ===========================================================================

import json
import logging
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable, Any
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


# ===========================================================================
# batch_processing_coordinator — batch inbox processing with progress output
# ===========================================================================


class BatchProcessingCoordinator:
    """Coordinates batch processing of inbox notes with progress tracking."""

    def __init__(
        self, inbox_dir: Path, process_callback: Optional[Callable[[str], Dict]] = None
    ):
        """Initialize the batch processing coordinator.

        Args:
            inbox_dir: Path to inbox directory
            process_callback: Optional callback for processing notes (can be set later)
        """
        if not isinstance(inbox_dir, Path):
            inbox_dir = Path(inbox_dir)

        # Ensure inbox directory exists (create if needed for test environments)
        created = not inbox_dir.exists()
        inbox_dir.mkdir(parents=True, exist_ok=True)

        if created:
            logger.info(f"Created inbox directory for test environment: {inbox_dir}")
        else:
            logger.debug(f"Using existing inbox directory: {inbox_dir}")

        # Callback can be None initially and set later by WorkflowManager
        if process_callback is not None and not callable(process_callback):
            logger.error(f"Invalid process_callback type: {type(process_callback)}")
            raise TypeError("process_callback must be a callable function")

        self.inbox_dir = inbox_dir
        self.process_callback = process_callback

        logger.info(
            f"BatchProcessingCoordinator initialized: inbox_dir={inbox_dir}, "
            f"has_callback={process_callback is not None}"
        )

    def batch_process_inbox(self, show_progress: bool = True) -> Dict:
        """Process all notes in the inbox with progress tracking."""
        inbox_files = list(self.inbox_dir.glob("*.md"))
        total = len(inbox_files)

        logger.info(
            f"Starting batch processing: {total} files in {self.inbox_dir}, "
            f"show_progress={show_progress}"
        )

        results = {
            "total_files": total,
            "processed": 0,
            "failed": 0,
            "results": [],
            "summary": {
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0,
            },
        }

        for idx, note_file in enumerate(inbox_files, 1):
            if show_progress:
                filename = note_file.name
                if len(filename) > 50:
                    filename = filename[:47] + "..."
                progress_pct = int((idx / total) * 100)
                sys.stderr.write(f"\r[{idx}/{total}] {progress_pct}% - {filename}...")
                sys.stderr.flush()

            logger.debug(f"Processing note [{idx}/{total}]: {note_file.name}")

            try:
                result = self.process_callback(str(note_file))

                if "error" not in result:
                    results["processed"] += 1
                    logger.debug(f"Successfully processed: {note_file.name}")

                    for rec in result.get("recommendations", []):
                        action = rec.get("action", "")
                        if action == "promote_to_permanent":
                            results["summary"]["promote_to_permanent"] += 1
                        elif action == "move_to_fleeting":
                            results["summary"]["move_to_fleeting"] += 1
                        elif action == "improve_or_archive":
                            results["summary"]["needs_improvement"] += 1
                else:
                    results["failed"] += 1
                    logger.warning(
                        f"Processing failed for {note_file.name}: {result.get('error', 'Unknown error')}"
                    )

                results["results"].append(result)

            except Exception as e:
                results["failed"] += 1
                logger.error(
                    f"Exception processing {note_file.name}: {type(e).__name__}: {e}",
                    exc_info=True,
                )
                results["results"].append(
                    {"original_file": str(note_file), "error": str(e)}
                )

        if show_progress and total > 0:
            sys.stderr.write("\r" + " " * 80 + "\r")
            sys.stderr.flush()

        logger.info(
            f"Batch processing complete: {results['processed']}/{total} successful, "
            f"{results['failed']} failed | "
            f"Summary: {results['summary']['promote_to_permanent']} promote, "
            f"{results['summary']['move_to_fleeting']} fleeting, "
            f"{results['summary']['needs_improvement']} needs improvement"
        )

        return results


# ===========================================================================
# note_processing_coordinator — AI-powered per-note processing
# ===========================================================================

from src.utils.tags import sanitize_tags
from src.utils.frontmatter import parse_frontmatter, build_frontmatter
from src.utils.io import safe_write


class NoteProcessingCoordinator:
    """
    Coordinator for AI-powered note processing and template handling.

    Extracted from WorkflowManager (ADR-002 Phase 6) to maintain single
    responsibility principle. Handles all note processing logic including
    AI tagging, quality scoring, connection discovery, and template fixes.
    """

    def __init__(
        self,
        tagger,
        summarizer,
        enhancer,
        connection_coordinator,
        config: Optional[Dict] = None,
    ):
        """
        Initialize note processing coordinator.

        Args:
            tagger: AI tagger component for generating tags
            summarizer: AI summarizer component for creating summaries
            enhancer: AI enhancer component for quality assessment
            connection_coordinator: Connection discovery coordinator
            config: Optional configuration dictionary
        """
        self.tagger = tagger
        self.summarizer = summarizer
        self.enhancer = enhancer
        self.connection_coordinator = connection_coordinator

        # Default configuration
        self.config = {
            "auto_tag_inbox": True,
            "auto_summarize_long_notes": True,
            "min_words_for_summary": 500,
            "max_tags_per_note": 8,
            "similarity_threshold": 0.7,
        }

        # Update with user config if provided
        if config:
            self.config.update(config)

    def process_note(
        self,
        note_path: str,
        dry_run: bool = False,
        fast: Optional[bool] = None,
        corpus_dir: Optional[Path] = None,
    ) -> Dict:
        """
        Process a note with AI assistance.

        Extracted from WorkflowManager.process_inbox_note() for single responsibility.

        Args:
            note_path: Path to the note file
            dry_run: If True, do not write changes to disk
            fast: If True, skip AI calls and use heuristics (defaults to dry_run)
            corpus_dir: Optional directory for connection discovery

        Returns:
            Processing results with processing details, recommendations, and metadata
        """
        note_file = Path(note_path)

        if not note_file.exists():
            return {"error": "Note file not found"}

        try:
            with open(note_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read note: {e}"}

        # Preprocess raw content to fix 'created' placeholders that break YAML parsing
        content, raw_template_fixed = self._preprocess_created_placeholder_in_raw(
            content, note_file
        )

        results = {
            "original_file": str(note_file),
            "processing": {},
            "recommendations": [],
        }

        # Extract frontmatter and body using centralized utility
        frontmatter, body = parse_frontmatter(content)

        # Fix template placeholders in frontmatter BEFORE any processing
        template_fixed = self._fix_template_placeholders(frontmatter, note_file)
        any_template_fixed = raw_template_fixed or template_fixed

        # Determine fast-mode (heuristic, no external AI calls)
        fast_mode = fast if fast is not None else dry_run

        if fast_mode:
            # Heuristic-only path to avoid network/AI latency
            results["processing"] = {}
            existing_tags = sanitize_tags(frontmatter.get("tags", []))
            results["processing"]["ai_tags"] = list(existing_tags)

            # Simple word count heuristic
            body_text = body if isinstance(body, str) else ""
            try:
                normalized = re.sub(r"\s+", " ", body_text).strip()
            except Exception:
                normalized = body_text
            word_count = len(normalized.split()) if normalized else 0

            # Score: emphasize length and presence of tags
            quality_score = 0.0
            if word_count >= 500:
                quality_score = 0.8
            elif word_count >= 200:
                quality_score = 0.55
            elif word_count >= 80:
                quality_score = 0.42
            else:
                quality_score = 0.30

            # Small boost for tags present
            if len(existing_tags) >= 3:
                quality_score = min(1.0, quality_score + 0.05)

            # Populate processing info without AI calls
            results["processing"]["quality"] = {
                "score": quality_score,
                "suggestions": [
                    (
                        "Add more detail and structure to improve quality"
                        if word_count < 200
                        else "Refine key points and add links to related notes"
                    )
                ],
            }
            results["processing"]["tags"] = {"added": [], "total": len(existing_tags)}

            # Primary recommendation based on heuristic score
            if quality_score > 0.7:
                primary = {
                    "action": "promote_to_permanent",
                    "reason": "High quality (heuristic) suitable for permanent notes",
                    "confidence": "medium",
                }
            elif quality_score > 0.4:
                primary = {
                    "action": "move_to_fleeting",
                    "reason": "Medium quality (heuristic) needs development",
                    "confidence": "medium",
                }
            else:
                primary = {
                    "action": "improve_or_archive",
                    "reason": "Low quality (heuristic) needs significant improvement",
                    "confidence": "high",
                }

            results["recommendations"].append(primary)
            results["quality_score"] = quality_score

            # Persist triage_recommendation to frontmatter (Phase 1 feature)
            frontmatter["triage_recommendation"] = primary["action"]

            # Persist changes (template fixes + triage_recommendation) in fast-mode
            if not dry_run:
                try:
                    updated_content = build_frontmatter(frontmatter, body)
                    safe_write(note_file, updated_content)
                    results["file_updated"] = True
                except Exception as e:
                    results["file_update_error"] = str(e)
                    results["file_updated"] = False
            else:
                results["file_updated"] = False

            return results

        # Track if any AI processing errors occurred
        ai_processing_errors = []

        # Auto-tag if enabled (use body content only)
        if self.config["auto_tag_inbox"]:
            try:
                suggested_tags = self.tagger.generate_tags(body)
                existing_tags = sanitize_tags(frontmatter.get("tags", []))
                suggested_tags = sanitize_tags(suggested_tags)

                # Merge tags intelligently
                merged_tags = self._merge_tags(existing_tags, suggested_tags)
                merged_tags = sanitize_tags(merged_tags)

                if merged_tags != existing_tags:
                    frontmatter["tags"] = merged_tags
                    results["processing"]["tags"] = {
                        "added": list(set(merged_tags) - set(existing_tags)),
                        "total": len(merged_tags),
                    }

                results["processing"]["ai_tags"] = merged_tags
            except Exception as e:
                results["processing"]["tags"] = {"error": str(e)}
                ai_processing_errors.append(("tagging", str(e)))

        # Ensure ai_tags key is always present
        current_tags = sanitize_tags(frontmatter.get("tags", []))
        if "ai_tags" not in results["processing"]:
            results["processing"]["ai_tags"] = current_tags

        # Analyze note quality and suggest improvements
        try:
            enhancement = self.enhancer.enhance_note(body)
            quality_score = enhancement.get("quality_score", 0)

            results["processing"]["quality"] = {
                "score": quality_score,
                "suggestions": enhancement.get("suggestions", [])[:3],
            }

            # Generate workflow recommendations based on quality
            if quality_score > 0.7:
                results["recommendations"].append(
                    {
                        "action": "promote_to_permanent",
                        "reason": "High quality content suitable for permanent notes",
                        "confidence": "high",
                    }
                )
            elif quality_score > 0.4:
                results["recommendations"].append(
                    {
                        "action": "move_to_fleeting",
                        "reason": "Medium quality content needs development",
                        "confidence": "medium",
                    }
                )
            else:
                results["recommendations"].append(
                    {
                        "action": "improve_or_archive",
                        "reason": "Low quality content needs significant improvement",
                        "confidence": "high",
                    }
                )
        except Exception as e:
            results["processing"]["quality"] = {"error": str(e)}
            ai_processing_errors.append(("quality", str(e)))

        # Find potential connections
        suggested_links = []
        try:
            if corpus_dir:
                connections = self.connection_coordinator.discover_connections(
                    body, corpus_dir=corpus_dir
                )

                if connections:
                    results["processing"]["connections"] = {
                        "similar_notes": [
                            {
                                "file": conn["filename"],
                                "similarity": float(conn["similarity"]),
                            }
                            for conn in connections[:3]
                        ]
                    }

                    results["recommendations"].append(
                        {
                            "action": "add_links",
                            "reason": f"Found {len(connections)} related notes",
                            "details": connections[:3],
                        }
                    )

                    # Compute suggested_links for persistence (Phase 2)
                    suggested_links = self._compute_suggested_links(connections, body)
        except Exception as e:
            results["processing"]["connections"] = {"error": str(e)}

        # Update note with AI enhancements (skip when dry_run)
        needs_ai_update = any(
            key in results["processing"] for key in ["tags", "quality"]
        )

        # Extract primary triage recommendation for persistence
        primary_recommendation = None
        if results["recommendations"]:
            primary_recommendation = results["recommendations"][0].get("action")

        # Determine if we have suggested links to persist
        has_suggested_links = len(suggested_links) > 0

        if needs_ai_update or any_template_fixed or has_suggested_links:
            if dry_run:
                if needs_ai_update:
                    frontmatter["ai_processed"] = datetime.now().isoformat()
                results["file_updated"] = False
            else:
                try:
                    if needs_ai_update:
                        frontmatter["ai_processed"] = datetime.now().isoformat()

                        if (
                            "quality" in results["processing"]
                            and "score" in results["processing"]["quality"]
                        ):
                            frontmatter["quality_score"] = results["processing"][
                                "quality"
                            ]["score"]

                        # Persist triage_recommendation (Phase 1 feature)
                        if primary_recommendation:
                            frontmatter["triage_recommendation"] = (
                                primary_recommendation
                            )

                    # Persist suggested_links to frontmatter (Phase 2 feature)
                    if has_suggested_links:
                        frontmatter["suggested_links"] = suggested_links

                    # Update body with ## Suggested Connections section (Phase 3 feature)
                    updated_body = body
                    if has_suggested_links:
                        section_content = self._build_suggested_connections_section(
                            suggested_links
                        )
                        updated_body = self._replace_or_append_section(
                            body, "## Suggested Connections", section_content
                        )

                    # Rebuild content using centralized utility
                    updated_content = build_frontmatter(frontmatter, updated_body)
                    safe_write(note_file, updated_content)
                    results["file_updated"] = True
                except Exception as e:
                    results["file_update_error"] = str(e)
                    results["file_updated"] = False
        else:
            results["file_updated"] = False

        # Report template processing status
        if any_template_fixed:
            results["template_fixed"] = True

        return results

    def _fix_template_placeholders(self, frontmatter: Dict, note_file: Path) -> bool:
        """
        Fix template placeholders in frontmatter, particularly {{date:...}} patterns.

        Args:
            frontmatter: The frontmatter dictionary to modify
            note_file: Path to the note file for timestamp inference

        Returns:
            True if any changes were made, False otherwise
        """
        import os

        changes_made = False
        created_value = frontmatter.get("created")

        # Fix template placeholders like {{date:YYYY-MM-DD HH:mm}} or missing created field
        if created_value is None or (
            isinstance(created_value, str)
            and (
                "{{date" in created_value
                or "<% tp.date.now(" in created_value
                or "<% tp.file.creation_date(" in created_value
            )
        ):

            try:
                file_stat = os.stat(note_file)
                timestamp = datetime.fromtimestamp(file_stat.st_mtime)
            except (OSError, ValueError):
                timestamp = datetime.now()

            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
            frontmatter["created"] = formatted_timestamp
            changes_made = True

        return changes_made

    def _preprocess_created_placeholder_in_raw(
        self, content: str, note_file: Path
    ) -> tuple:
        """
        Replace invalid 'created' placeholders directly in the raw frontmatter block.

        This is necessary when placeholders make YAML unparseable, causing parse_frontmatter()
        to return empty metadata. Preprocessing ensures YAML becomes valid.

        Returns:
            Tuple of (possibly updated content, changes_made)
        """
        try:
            text = content if isinstance(content, str) else ""
            if not text or not text.lstrip().startswith("---"):
                return content, False

            lines = text.split("\n")

            # Locate closing delimiter
            closing_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    closing_idx = i
                    break

            if closing_idx is None:
                return content, False

            placeholder_markers = (
                "{{date",
                "<% tp.date.now(",
                "<% tp.file.creation_date(",
            )

            changed = False

            # Scan only within frontmatter region
            for j in range(1, closing_idx):
                line = lines[j]
                if not line.strip().startswith("created:"):
                    continue

                prefix, sep, value = line.partition(":")
                value_str = value.strip()

                if any(marker in value_str for marker in placeholder_markers):
                    try:
                        import os

                        ts = datetime.fromtimestamp(os.stat(note_file).st_mtime)
                    except Exception:
                        ts = datetime.now()

                    formatted = ts.strftime("%Y-%m-%d %H:%M")

                    # Preserve spaces after colon
                    m = re.match(r"^(\s*)", value)
                    spaces = m.group(1) if m else " "
                    lines[j] = f"{prefix}:{spaces}{formatted}"
                    changed = True
                break

            if changed:
                return "\n".join(lines), True
            return content, False
        except Exception:
            return content, False

    def _merge_tags(self, existing_tags: List[str], new_tags: List[str]) -> List[str]:
        """
        Merge existing and new tags intelligently.

        Args:
            existing_tags: Current tags in the note
            new_tags: New tags to add

        Returns:
            Merged and deduplicated tag list (limited by max_tags_per_note)
        """
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()

        merged = sorted(list(existing_set | new_set))
        return merged[: self.config["max_tags_per_note"]]

    def _extract_wikilinks_from_body(self, body: str) -> set:
        """
        Extract all wikilinks from note body.

        Args:
            body: Note body text

        Returns:
            Set of note names (without .md extension) found in [[wikilinks]]
        """
        if not body:
            return set()
        # Match [[note-name]] or [[note-name|alias]] patterns
        pattern = r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]"
        matches = re.findall(pattern, body)
        return set(matches)

    def _compute_suggested_links(
        self, connections: List[Dict], body: str, max_links: int = 5
    ) -> List[str]:
        """
        Compute suggested links from connection discoveries.

        Args:
            connections: List of connection results with 'filename' and 'similarity'
            body: Note body for deduplication against existing links
            max_links: Maximum number of suggested links (default 5)

        Returns:
            List of wikilink strings like ["[[note-name]]", ...]
        """
        if not connections:
            return []

        # Extract existing links from body for deduplication
        existing_links = self._extract_wikilinks_from_body(body)

        suggested = []
        seen = set()

        for conn in connections:
            filename = conn.get("filename", "")
            if not filename:
                continue

            # Remove .md extension for wikilink format
            note_name = filename.replace(".md", "")

            # Deduplicate: skip if already in body or already suggested
            if note_name in existing_links or note_name in seen:
                continue

            seen.add(note_name)
            suggested.append(f"[[{note_name}]]")

            if len(suggested) >= max_links:
                break

        return suggested

    def _replace_or_append_section(self, body: str, header: str, new_block: str) -> str:
        """
        Replace an existing section or append a new one to note body.

        Args:
            body: Current note body
            header: Section header (e.g., "## Suggested Connections")
            new_block: New content for the section (including header)

        Returns:
            Updated body with section replaced or appended
        """
        if not body:
            return new_block

        # Check if section exists - find header and everything after until next ## or end
        pattern = rf"({re.escape(header)}.*?)(?=\n## |\Z)"
        if re.search(pattern, body, re.DOTALL):
            # Replace existing section
            updated = re.sub(pattern, new_block.rstrip(), body, flags=re.DOTALL)
            return updated
        else:
            # Append new section at end
            return body.rstrip() + "\n\n" + new_block

    def _build_suggested_connections_section(self, suggested_links: List[str]) -> str:
        """
        Build the ## Suggested Connections section content.

        Args:
            suggested_links: List of wikilink strings

        Returns:
            Formatted section string with header, timestamp, and links
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        lines = [
            "## Suggested Connections",
            "",
            f"> Auto-generated by InnerOS on {timestamp}",
            "",
        ]
        for link in suggested_links:
            lines.append(f"- {link}")

        return "\n".join(lines)


# ===========================================================================
# workflow_reporting_coordinator — status reports and health assessment
# ===========================================================================


class WorkflowReportingCoordinator:
    """
    Coordinates workflow reporting and health assessment operations.

    ADR-002 Phase 10: Extracted from WorkflowManager (~120 LOC reduction).

    Responsibilities:
    - Generate comprehensive workflow status reports
    - Analyze AI feature usage across the vault
    - Assess workflow health status
    - Generate intelligent recommendations for workflow improvement

    Integration:
    - Uses NoteAnalytics for collection-wide analytics
    - Consumed by CLI layer (workflow_demo.py)
    - Independent of other coordinators
    """

    def __init__(self, base_dir: Path, analytics):
        """
        Initialize WorkflowReportingCoordinator.

        Args:
            base_dir: Base directory of the Zettelkasten vault
            analytics: NoteAnalytics instance for collection analysis
        """
        self.base_dir = Path(base_dir)
        self.analytics = analytics

        # Define standard directories
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.archive_dir = self.base_dir / "Archive"

    def generate_workflow_report(self) -> Dict:
        """
        Generate a comprehensive workflow status report.

        Returns:
            Dict containing:
                - workflow_status: Health, directory counts, total notes
                - ai_features: AI usage statistics
                - analytics: Collection analytics from NoteAnalytics
                - recommendations: List of workflow improvement suggestions
        """
        # Get analytics for the entire collection
        analytics_report = self.analytics.generate_report()

        # Count notes by directory
        directory_counts = self._count_notes_by_directory()

        # Assess workflow health
        workflow_health = self._assess_workflow_health(directory_counts)

        # Analyze AI feature usage
        ai_usage = self._analyze_ai_usage()

        # Generate recommendations
        recommendations = self._generate_workflow_recommendations(
            directory_counts, ai_usage
        )

        return {
            "workflow_status": {
                "health": workflow_health,
                "directory_counts": directory_counts,
                "total_notes": sum(directory_counts.values()),
            },
            "ai_features": ai_usage,
            "analytics": analytics_report,
            "recommendations": recommendations,
        }

    def _count_notes_by_directory(self) -> Dict[str, int]:
        """
        Count markdown notes in each workflow directory.

        Returns:
            Dictionary mapping directory names to note counts
        """
        directory_counts = {}

        for dir_name, dir_path in [
            ("Inbox", self.inbox_dir),
            ("Fleeting Notes", self.fleeting_dir),
            ("Permanent Notes", self.permanent_dir),
            ("Archive", self.archive_dir),
        ]:
            if dir_path.exists():
                directory_counts[dir_name] = len(list(dir_path.glob("*.md")))
            else:
                directory_counts[dir_name] = 0

        return directory_counts

    def _assess_workflow_health(self, directory_counts: Dict[str, int]) -> str:
        """
        Assess workflow health based on inbox backlog.

        Args:
            directory_counts: Directory note counts

        Returns:
            Health status: "healthy", "needs_attention", or "critical"
        """
        inbox_count = directory_counts.get("Inbox", 0)

        if inbox_count > 50:
            return "critical"
        elif inbox_count > 20:
            return "needs_attention"
        else:
            return "healthy"

    def _analyze_ai_usage(self) -> Dict:
        """
        Analyze usage of AI features across the collection.

        Scans all markdown notes in the vault and counts:
        - Notes with AI-generated tags (heuristic: kebab-case tags)
        - Notes with AI summaries
        - Notes with AI processing flags

        Returns:
            Dictionary with AI usage statistics
        """
        usage_stats = {
            "notes_with_ai_tags": 0,
            "notes_with_ai_summaries": 0,
            "notes_with_ai_processing": 0,
            "total_analyzed": 0,
        }

        # Scan all notes for AI features
        for md_file in self.base_dir.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                frontmatter, _ = parse_frontmatter(content)
                usage_stats["total_analyzed"] += 1

                # Check for AI summary
                if "ai_summary" in frontmatter:
                    usage_stats["notes_with_ai_summaries"] += 1

                # Check for AI processing flag
                if "ai_processed" in frontmatter:
                    usage_stats["notes_with_ai_processing"] += 1

                # Check for AI-style tags (heuristic: kebab-case tags)
                tags = frontmatter.get("tags", [])
                if isinstance(tags, list) and len(tags) >= 3:
                    # Look for AI-style kebab-case tags
                    ai_style_tags = [t for t in tags if "-" in t and len(t) > 5]
                    if len(ai_style_tags) >= 2:
                        usage_stats["notes_with_ai_tags"] += 1

            except Exception:
                # Skip files that can't be read or parsed
                continue

        return usage_stats

    def _generate_workflow_recommendations(
        self, directory_counts: Dict[str, int], ai_usage: Dict
    ) -> List[str]:
        """
        Generate workflow improvement recommendations.

        Analyzes workflow state and AI adoption to suggest improvements:
        - Inbox management recommendations
        - AI feature adoption suggestions
        - Note type balance recommendations

        Args:
            directory_counts: Directory note counts
            ai_usage: AI usage statistics

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Inbox management recommendations
        inbox_count = directory_counts.get("Inbox", 0)
        if inbox_count > 20:
            recommendations.append(
                f"Process {inbox_count} notes in inbox - consider batch processing"
            )

        # AI feature adoption recommendations
        total_notes = ai_usage.get("total_analyzed", 0)
        if total_notes > 0:
            ai_summary_rate = ai_usage["notes_with_ai_summaries"] / total_notes
            if ai_summary_rate < 0.3:
                recommendations.append(
                    "Consider enabling auto-summarization for long notes"
                )

            ai_processing_rate = ai_usage["notes_with_ai_processing"] / total_notes
            if ai_processing_rate < 0.5:
                recommendations.append(
                    "Enable AI processing for inbox notes to improve workflow efficiency"
                )

        # Note type balance recommendations
        permanent_count = directory_counts.get("Permanent Notes", 0)
        fleeting_count = directory_counts.get("Fleeting Notes", 0)

        if fleeting_count > permanent_count * 2:
            recommendations.append(
                "Consider promoting more fleeting notes to permanent status"
            )

        return recommendations


# ===========================================================================
# batch_inbox_processor — idempotent batch processing with skip logic
# ===========================================================================


def is_note_eligible_for_processing(note_path: Path) -> bool:
    """
    Determine if a note needs processing.

    A note is eligible if:
    - ai_processed is missing OR false, OR
    - triage_recommendation is missing

    A note is NOT eligible (should be skipped) if:
    - ai_processed is true AND triage_recommendation is present

    Args:
        note_path: Path to the note file

    Returns:
        True if note should be processed, False if it should be skipped
    """
    try:
        content = note_path.read_text(encoding="utf-8")
        frontmatter, _ = parse_frontmatter(content)

        if frontmatter is None:
            return True

        ai_processed = frontmatter.get("ai_processed")
        triage_recommendation = frontmatter.get("triage_recommendation")

        processed = False
        if isinstance(ai_processed, bool):
            processed = ai_processed
        elif ai_processed is None:
            processed = False
        elif isinstance(ai_processed, str):
            normalized = ai_processed.strip().lower()
            processed = normalized not in {"", "false", "no", "0", "none", "null"}
        else:
            processed = True

        if processed is True and triage_recommendation is not None:
            logger.debug(f"Skipping already processed note: {note_path.name}")
            return False

        return True

    except Exception as e:
        logger.warning(f"Error reading note {note_path}: {e}")
        return True


def scan_eligible_notes(inbox_dir: Path) -> List[Path]:
    """
    Scan inbox directory and return only notes that need processing.

    Args:
        inbox_dir: Path to the Inbox directory

    Returns:
        List of Path objects for eligible notes
    """
    if not inbox_dir.exists():
        logger.warning(f"Inbox directory does not exist: {inbox_dir}")
        return []

    eligible = []
    for note_path in inbox_dir.glob("*.md"):
        if is_note_eligible_for_processing(note_path):
            eligible.append(note_path)

    logger.info(f"Found {len(eligible)} eligible notes in {inbox_dir}")
    return eligible


def process_single_note(
    note_path: Path,
    workflow_manager: Optional[Any] = None,
) -> Dict:
    """
    Process a single note using the workflow manager.

    Args:
        note_path: Path to the note to process
        workflow_manager: Optional WorkflowManager instance

    Returns:
        Processing result dict with success, triage_recommendation, etc.
    """
    if workflow_manager is None:
        vault_path = note_path.parent.parent
        workflow_manager = WorkflowManager(str(vault_path))

    result = workflow_manager.process_inbox_note(str(note_path), dry_run=False)

    triage_rec = None
    recommendations = result.get("recommendations", [])
    if recommendations:
        triage_rec = recommendations[0].get("action")

    return {
        "success": "error" not in result,
        "note": note_path.name,
        "path": str(note_path),
        "triage_recommendation": triage_rec,
        "details": result,
    }


def batch_process_unprocessed_inbox(
    inbox_dir: Path,
    dry_run: bool = False,
    workflow_manager: Optional[Any] = None,
    show_progress: bool = True,
) -> Dict:
    """
    Process all unprocessed notes in the inbox.

    Args:
        inbox_dir: Path to the Inbox directory
        dry_run: If True, don't modify files - just report what would be done
        workflow_manager: Optional WorkflowManager instance
        show_progress: If True, print progress to stderr

    Returns:
        Dict with processed, skipped, errors, error_details, summary, dry_run
    """
    all_notes = list(inbox_dir.glob("*.md")) if inbox_dir.exists() else []
    eligible_notes = scan_eligible_notes(inbox_dir)
    skipped_count = len(all_notes) - len(eligible_notes)

    result = {
        "processed": 0,
        "skipped": skipped_count,
        "errors": 0,
        "error_details": [],
        "summary": {"by_recommendation": {}},
        "dry_run": dry_run,
    }

    if dry_run:
        result["would_process"] = len(eligible_notes)
        result["eligible_notes"] = [str(p) for p in eligible_notes]
        return result

    total = len(eligible_notes)
    for idx, note_path in enumerate(eligible_notes, 1):
        if show_progress:
            pct = int((idx / total) * 100) if total > 0 else 100
            sys.stderr.write(f"\r[{idx}/{total}] {pct}% - {note_path.name[:40]}...")
            sys.stderr.flush()

        try:
            proc_result = process_single_note(note_path, workflow_manager)

            if proc_result.get("success"):
                result["processed"] += 1
                rec = proc_result.get("triage_recommendation")
                if rec:
                    by_rec = result["summary"]["by_recommendation"]
                    by_rec[rec] = by_rec.get(rec, 0) + 1
            else:
                result["errors"] += 1
                result["error_details"].append(
                    {
                        "note": note_path.name,
                        "path": str(note_path),
                        "error": "Processing returned failure",
                    }
                )

        except Exception as e:
            result["errors"] += 1
            result["error_details"].append(
                {
                    "note": note_path.name,
                    "path": str(note_path),
                    "error": str(e),
                }
            )
            logger.exception(f"Error processing {note_path.name}")

    if show_progress and total > 0:
        sys.stderr.write("\r" + " " * 60 + "\r")
        sys.stderr.flush()

    return result


# ===========================================================================
# workflow_manager — main orchestration class + SafeWorkflowManager alias
# ===========================================================================

from .enrichment import AITagger, AISummarizer, AIEnhancer
from .connections_discovery import AIConnections, ConnectionCoordinator
from .analytics import NoteAnalytics, AnalyticsCoordinator
from .media import SafeImageProcessor, ImageIntegrityMonitor
from .lifecycle import (
    NoteLifecycleManager,
    PromotionEngine,
    ReviewTriageCoordinator,
    FleetingAnalysisCoordinator,
    FleetingAnalysis,
    FleetingNoteCoordinator,
)
from .connections_insertion import OrphanRemediationCoordinator
from .metadata_repair_engine import MetadataRepairEngine


class WorkflowManager:
    """Manages the complete AI-enhanced Zettelkasten workflow."""

    def __init__(self, base_directory: str | None = None):
        """Initialize workflow manager.

        Args:
            base_directory: Explicit path to the Zettelkasten root. If ``None`` the
                resolver in ``utils.vault_path`` is used. Raises ``ValueError`` if
                no valid directory can be resolved.
        """
        if base_directory is None:
            from src.utils.vault_path import get_default_vault_path

            resolved = get_default_vault_path()
            if resolved is None:
                raise ValueError(
                    "No vault path supplied and none could be resolved via "
                    "INNEROS_VAULT_PATH or .inneros.* config files."
                )
            self.base_dir = resolved
        else:
            self.base_dir = Path(base_directory).expanduser()

        # Define workflow directories
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"
        self.literature_dir = self.base_dir / "Literature Notes"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.archive_dir = self.base_dir / "Archive"

        # Initialize AI components
        self.tagger = AITagger()
        self.summarizer = AISummarizer()
        self.connections = AIConnections()  # Legacy support
        self.enhancer = AIEnhancer()
        self.analytics = NoteAnalytics(str(self.base_dir))

        # ADR-002 Phase 1: Lifecycle manager extraction
        self.lifecycle_manager = NoteLifecycleManager(base_dir=self.base_dir)

        # ADR-002 Phase 2: Connection coordinator extraction
        self.connection_coordinator = ConnectionCoordinator(
            str(self.base_dir), min_similarity=0.7, max_suggestions=5
        )

        # ADR-002 Phase 3: Analytics coordinator extraction
        self.analytics_coordinator = AnalyticsCoordinator(self.base_dir)

        # ADR-002 Phase 4: Promotion engine extraction
        self.promotion_engine = PromotionEngine(
            self.base_dir,
            self.lifecycle_manager,
            config=None,  # Use default config for now
        )

        # ADR-002 Phase 5: Review/Triage coordinator extraction
        self.review_triage_coordinator = ReviewTriageCoordinator(
            self.base_dir, self  # Pass self for delegation to process_inbox_note
        )

        # ADR-002 Phase 6: Note processing coordinator extraction
        self.note_processing_coordinator = NoteProcessingCoordinator(
            tagger=self.tagger,
            summarizer=self.summarizer,
            enhancer=self.enhancer,
            connection_coordinator=self.connection_coordinator,
            config=None,  # Will use default config
        )

        # Initialize image safety components (GREEN phase)
        self.safe_image_processor = SafeImageProcessor(str(self.base_dir))
        self.image_integrity_monitor = ImageIntegrityMonitor(str(self.base_dir))

        # REFACTOR: Initialize extracted utility classes for modular architecture
        self.safe_workflow_processor = SafeWorkflowProcessor(
            self.safe_image_processor, self.image_integrity_monitor
        )
        self.atomic_workflow_engine = AtomicWorkflowEngine(self.safe_image_processor)
        self.integrity_monitoring_manager = IntegrityMonitoringManager(
            self.image_integrity_monitor, self.safe_image_processor
        )
        self.concurrent_session_manager = ConcurrentSessionManager(
            self.safe_workflow_processor
        )
        self.performance_metrics_collector = PerformanceMetricsCollector(
            self.safe_image_processor
        )

        # ADR-002 Phase 7: Safe image processing coordinator extraction
        from .media import SafeImageProcessingCoordinator

        self.safe_image_processing_coordinator = SafeImageProcessingCoordinator(
            safe_workflow_processor=self.safe_workflow_processor,
            atomic_workflow_engine=self.atomic_workflow_engine,
            integrity_monitoring_manager=self.integrity_monitoring_manager,
            concurrent_session_manager=self.concurrent_session_manager,
            performance_metrics_collector=self.performance_metrics_collector,
            safe_image_processor=self.safe_image_processor,
            image_integrity_monitor=self.image_integrity_monitor,
            inbox_dir=self.inbox_dir,
            process_note_callback=self.process_inbox_note,
            batch_process_callback=self.batch_process_inbox,
        )

        # ADR-002 Phase 8: Orphan remediation coordinator extraction
        self.orphan_remediation_coordinator = OrphanRemediationCoordinator(
            base_dir=str(self.base_dir),
            analytics_coordinator=self.analytics_coordinator,
        )

        # ADR-002 Phase 9: Fleeting analysis coordinator extraction
        self.fleeting_analysis_coordinator = FleetingAnalysisCoordinator(
            fleeting_dir=self.fleeting_dir
        )

        # ADR-002 Phase 10: Workflow reporting coordinator extraction
        self.reporting_coordinator = WorkflowReportingCoordinator(
            base_dir=self.base_dir, analytics=self.analytics
        )

        # ADR-002 Phase 11: Batch processing coordinator extraction
        self.batch_processing_coordinator = BatchProcessingCoordinator(
            inbox_dir=self.inbox_dir, process_callback=self.process_inbox_note
        )

        # ADR-002 Phase 12b: Fleeting note coordinator extraction
        self.fleeting_note_coordinator = FleetingNoteCoordinator(
            fleeting_dir=self.fleeting_dir,
            inbox_dir=self.inbox_dir,
            permanent_dir=self.permanent_dir,
            literature_dir=self.literature_dir,
            process_callback=self.process_inbox_note,
            default_quality_threshold=0.7,
        )

        # ADR-002 Phase 13: Metadata repair engine extraction
        self.metadata_repair_engine = MetadataRepairEngine(
            str(self.inbox_dir), dry_run=True  # Default to safe mode
        )

        # Session management for concurrent processing (legacy compatibility)
        self.active_sessions = {}

        # Workflow configuration
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load workflow configuration."""
        config_file = self.base_dir / ".ai_workflow_config.json"

        default_config = {
            "auto_tag_inbox": True,
            "auto_summarize_long_notes": True,
            "auto_enhance_permanent_notes": False,
            "min_words_for_summary": 500,
            "max_tags_per_note": 8,
            "similarity_threshold": 0.7,
            "archive_after_days": 90,
        }

        if config_file.exists():
            try:
                with open(config_file, "r") as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception:
                pass

        return default_config

    def process_inbox_note(
        self, note_path: str, dry_run: bool = False, fast: bool | None = None
    ) -> Dict:
        """
        Process a note in the inbox with AI assistance.

        ADR-002 Phase 6: Delegates to NoteProcessingCoordinator for single responsibility.

        Args:
            note_path: Path to the note in inbox
            dry_run: If True, do not write any changes to disk
            fast: If True, skip heavy AI calls and use heuristics (defaults to dry_run)

        Returns:
            Processing results and recommendations
        """
        import time

        # Phase 3.1: Metrics instrumentation
        start_time = time.time()

        # Delegate to NoteProcessingCoordinator
        results = self.note_processing_coordinator.process_note(
            note_path=note_path,
            dry_run=dry_run,
            fast=fast,
            corpus_dir=self.permanent_dir,
        )

        # Metrics recording removed (moved to legacy/daemons/ in Phase 3 simplification refactor)
        _ = (time.time() - start_time) * 1000  # elapsed_ms, intentionally unused

        # P0-1.3: Update status to 'promoted' after successful AI processing
        has_processing_errors = self._has_ai_processing_errors(results)
        should_update_status = (
            not dry_run
            and not fast
            and results.get("file_updated")
            and not has_processing_errors
        )

        if should_update_status:
            try:
                note_path_obj = Path(note_path)
                status_result = self.lifecycle_manager.update_status(
                    note_path_obj,
                    new_status="promoted",
                    reason="AI processing completed successfully",
                )

                # Add status_updated field to results if successful
                if status_result.get("validation_passed"):
                    results["status_updated"] = status_result.get(
                        "status_updated", "promoted"
                    )
                else:
                    # Log validation failure but don't fail the whole operation
                    if "warnings" not in results:
                        results["warnings"] = []
                    error_msg = status_result.get("error", "Unknown validation error")
                    results["warnings"].append(
                        f"Status update validation failed: {error_msg}"
                    )

            except Exception as e:
                # Graceful degradation - don't fail processing if status update fails
                if "warnings" not in results:
                    results["warnings"] = []
                results["warnings"].append(f"Status update failed: {str(e)}")

        return results

    def _has_ai_processing_errors(self, results: Dict) -> bool:
        """
        Check if AI processing encountered any errors.

        Args:
            results: Processing results dict from NoteProcessingCoordinator

        Returns:
            True if any AI processing errors were detected
        """
        processing = results.get("processing", {})

        # Check each AI processing component for errors
        for component in ["tags", "quality", "connections"]:
            if component in processing:
                component_result = processing[component]
                # Error is indicated by presence of "error" key
                if isinstance(component_result, dict) and "error" in component_result:
                    return True

        return False

    def promote_note(self, note_path: str, target_type: str = "permanent") -> Dict:
        """
        Promote a note from inbox/fleeting to appropriate directory.

        ADR-002 Phase 4: Delegates to PromotionEngine.
        """
        return self.promotion_engine.promote_note(note_path, target_type)

    def _validate_note_for_promotion(
        self, note_path: Path, frontmatter: Dict, quality_threshold: float
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate if a note is eligible for auto-promotion."""
        # Check quality score
        quality_score = frontmatter.get("quality_score", 0.0)
        if quality_score < quality_threshold:
            return (
                False,
                None,
                f"Quality score {quality_score:.2f} below threshold {quality_threshold}",
            )

        # Check for required type field
        note_type = frontmatter.get("type")
        if not note_type:
            return False, None, "Missing 'type' field in frontmatter"

        # Validate type is one of the expected values
        valid_types = ["permanent", "literature", "fleeting"]
        if note_type not in valid_types:
            return (
                False,
                None,
                f"Invalid type '{note_type}', must be one of: {valid_types}",
            )

        return True, note_type, None

    def batch_process_inbox(self, show_progress: bool = True) -> Dict:
        """
        Process all notes in the inbox.

        ADR-002 Phase 11: Delegates to BatchProcessingCoordinator.
        """
        return self.batch_processing_coordinator.batch_process_inbox(
            show_progress=show_progress
        )

    def generate_workflow_report(self) -> Dict:
        """
        Generate a comprehensive workflow status report.

        ADR-002 Phase 10: Delegates to WorkflowReportingCoordinator.
        """
        return self.reporting_coordinator.generate_workflow_report()

    def _merge_tags(self, existing_tags: List[str], new_tags: List[str]) -> List[str]:
        """Merge existing and new tags intelligently."""
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()

        merged = sorted(list(existing_set | new_set))
        return merged[: self.config["max_tags_per_note"]]

    def scan_review_candidates(self) -> List[Dict]:
        """Scan for notes that need weekly review attention."""
        return self.review_triage_coordinator.scan_review_candidates()

    def generate_weekly_recommendations(
        self, candidates: List[Dict], dry_run: bool = False
    ) -> Dict:
        """Generate AI-powered recommendations for weekly review candidates."""
        return self.review_triage_coordinator.generate_weekly_recommendations(
            candidates, dry_run
        )

    def detect_orphaned_notes(self) -> List[Dict]:
        """Detect notes that have no bidirectional links to other notes."""
        return self.analytics_coordinator.detect_orphaned_notes()

    def detect_orphaned_notes_comprehensive(self) -> List[Dict]:
        """Detect orphaned notes across the entire repository."""
        return self.analytics_coordinator.detect_orphaned_notes_comprehensive()

    def detect_stale_notes(self, days_threshold: int = 90) -> List[Dict]:
        """Detect notes that haven't been modified in a specified time period."""
        return self.analytics_coordinator.detect_stale_notes(days_threshold)

    def generate_enhanced_metrics(self) -> Dict:
        """Generate comprehensive metrics for weekly review."""
        return self.analytics_coordinator.generate_enhanced_metrics()

    def remediate_orphaned_notes(
        self,
        mode: str = "link",
        scope: str = "permanent",
        limit: int = 10,
        target: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict:
        """Remediate orphaned notes by inserting bidirectional links."""
        return self.orphan_remediation_coordinator.remediate_orphaned_notes(
            mode=mode, scope=scope, limit=limit, target=target, dry_run=dry_run
        )

    def _get_all_notes(self) -> List[Path]:
        """Get all markdown notes from all directories."""
        all_notes = []
        directories = [self.permanent_dir, self.fleeting_dir, self.inbox_dir]

        for directory in directories:
            if directory.exists():
                all_notes.extend(directory.glob("*.md"))

        return all_notes

    def _get_all_notes_comprehensive(self) -> List[Path]:
        """Get all markdown notes from the entire repository."""
        root_dir = Path(self.base_dir)

        # Get all .md files recursively, excluding hidden directories and common non-content dirs
        exclude_dirs = {
            ".git",
            ".obsidian",
            "__pycache__",
            ".pytest_cache",
            "htmlcov",
            ".windsurf",
        }
        all_notes = []

        for md_file in root_dir.rglob("*.md"):
            # Skip files in excluded directories
            if any(excluded_dir in md_file.parts for excluded_dir in exclude_dirs):
                continue
            all_notes.append(md_file)

        return all_notes

    def analyze_fleeting_notes(self) -> FleetingAnalysis:
        """Analyze fleeting notes collection for age distribution and health metrics."""
        return self.fleeting_analysis_coordinator.analyze_fleeting_notes()

    def generate_fleeting_health_report(self) -> Dict:
        """Generate a health report for fleeting notes with recommendations."""
        return self.fleeting_analysis_coordinator.generate_fleeting_health_report()

    def generate_fleeting_triage_report(
        self,
        quality_threshold: Optional[float] = None,
        mutate: bool = False,
    ) -> Dict:
        """Generate LLM-powered triage report for fleeting notes."""
        return self.review_triage_coordinator.generate_fleeting_triage_report(
            quality_threshold=quality_threshold, mutate=mutate
        )

    def promote_fleeting_note(
        self,
        note_path: str,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
    ) -> Dict:
        """Promote a single fleeting note to permanent or literature status."""
        return self.promotion_engine.promote_fleeting_note(
            note_path, target_type, preview_mode
        )

    def promote_fleeting_notes_batch(
        self,
        quality_threshold: float = 0.7,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
    ) -> Dict:
        """Promote multiple fleeting notes based on quality threshold."""
        return self.promotion_engine.promote_fleeting_notes_batch(
            quality_threshold, target_type, preview_mode
        )

    def auto_promote_ready_notes(
        self, dry_run: bool = False, quality_threshold: float = 0.7
    ) -> Dict:
        """Automatically promote notes that meet quality threshold."""
        return self.promotion_engine.auto_promote_ready_notes(
            dry_run=dry_run, quality_threshold=quality_threshold
        )

    def repair_inbox_metadata(self, execute: bool = False) -> Dict:
        """Repair missing frontmatter metadata in Inbox notes."""
        # Create engine with appropriate dry_run setting
        engine = MetadataRepairEngine(str(self.inbox_dir), dry_run=not execute)

        # Scan for notes needing repair
        results = {
            "notes_scanned": 0,
            "repairs_needed": 0,
            "repairs_made": 0,
            "errors": [],
        }

        for note_path in self.inbox_dir.glob("*.md"):
            results["notes_scanned"] += 1
            missing_fields = engine.detect_missing_metadata(str(note_path))

            if missing_fields:
                results["repairs_needed"] += 1
                try:
                    repair_result = engine.repair_note_metadata(str(note_path))
                    if execute and "added" in repair_result:
                        results["repairs_made"] += 1
                except Exception as e:
                    results["errors"].append({"note": note_path.name, "error": str(e)})

        return results

    # ============================================================================
    # GREEN PHASE: Safe Image Processing Integration Methods
    # ============================================================================
    # ADR-002 Phase 7: Delegated to SafeImageProcessingCoordinator

    def safe_process_inbox_note(
        self, note_path: str, preserve_images: bool = True, **kwargs
    ) -> Dict:
        """Delegate to SafeImageProcessingCoordinator for safe inbox note processing."""
        return self.safe_image_processing_coordinator.safe_process_inbox_note(
            note_path, preserve_images, **kwargs
        )

    def process_inbox_note_atomic(self, note_path: str) -> Dict:
        """Delegate to SafeImageProcessingCoordinator for atomic processing."""
        return self.safe_image_processing_coordinator.process_inbox_note_atomic(
            note_path
        )

    def safe_batch_process_inbox(self) -> Dict:
        """Delegate to SafeImageProcessingCoordinator for safe batch processing."""
        return self.safe_image_processing_coordinator.safe_batch_process_inbox()

    def process_inbox_note_enhanced(
        self,
        note_path: str,
        enable_monitoring: bool = False,
        collect_performance_metrics: bool = False,
        **kwargs,
    ) -> Dict:
        """Delegate to SafeImageProcessingCoordinator for enhanced processing."""
        return self.safe_image_processing_coordinator.process_inbox_note_enhanced(
            note_path, enable_monitoring, collect_performance_metrics, **kwargs
        )

    def process_inbox_note_safe(self, note_path: str) -> Dict:
        """Delegate to SafeImageProcessingCoordinator for safe processing with backup/rollback."""
        return self.safe_image_processing_coordinator.process_inbox_note_safe(note_path)

    def start_safe_processing_session(self, operation_name: str) -> str:
        """Delegate to SafeImageProcessingCoordinator for session management."""
        return self.safe_image_processing_coordinator.start_safe_processing_session(
            operation_name
        )

    def process_note_in_session(self, note_path: str, session_id: str) -> Dict:
        """Delegate to SafeImageProcessingCoordinator for session-based processing."""
        return self.safe_image_processing_coordinator.process_note_in_session(
            note_path, session_id
        )

    def commit_safe_processing_session(self, session_id: str) -> bool:
        """Delegate to SafeImageProcessingCoordinator for session commit."""
        return self.safe_image_processing_coordinator.commit_safe_processing_session(
            session_id
        )


def main():
    """CLI entry point for workflow manager."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI-enhanced Zettelkasten workflow manager"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Process inbox
    process_parser = subparsers.add_parser("process-inbox", help="Process inbox notes")
    process_parser.add_argument("directory", help="Zettelkasten root directory")
    process_parser.add_argument(
        "--batch", action="store_true", help="Process all inbox notes"
    )

    # Promote note
    promote_parser = subparsers.add_parser("promote", help="Promote a note")
    promote_parser.add_argument("directory", help="Zettelkasten root directory")
    promote_parser.add_argument("note", help="Note file to promote")
    promote_parser.add_argument(
        "--type",
        choices=["permanent", "fleeting"],
        default="permanent",
        help="Target note type",
    )

    # Workflow report
    report_parser = subparsers.add_parser("report", help="Generate workflow report")
    report_parser.add_argument("directory", help="Zettelkasten root directory")
    report_parser.add_argument("--output", help="Output file for report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    workflow = WorkflowManager(args.directory)

    if args.command == "process-inbox":
        if args.batch:
            print("Processing all inbox notes...")
            result = workflow.batch_process_inbox()

            print("Results:")
            print(f"   Total files: {result['total_files']}")
            print(f"   Processed: {result['processed']}")
            print(f"   Failed: {result['failed']}")
            print("   Recommendations:")
            print(
                f"     Promote to permanent: {result['summary']['promote_to_permanent']}"
            )
            print(f"     Move to fleeting: {result['summary']['move_to_fleeting']}")
            print(f"     Needs improvement: {result['summary']['needs_improvement']}")
        else:
            print("Use --batch flag to process all inbox notes")

    elif args.command == "promote":
        print(f"Promoting note: {args.note}")
        result = workflow.promote_note(args.note, args.type)

        if result.get("success"):
            print(f"Successfully promoted to {result['type']}")
            print(f"   From: {result['source']}")
            print(f"   To: {result['target']}")
            if result.get("has_summary"):
                print("   Added AI summary")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")

    elif args.command == "report":
        print("Generating workflow report...")
        report = workflow.generate_workflow_report()

        if args.output:
            # Use atomic write to prevent partial JSON writes on interruption
            report_json = json.dumps(report, indent=2, default=str)
            safe_write(args.output, report_json)
            print(f"Report saved to: {args.output}")
        else:
            # Display summary
            status = report["workflow_status"]
            print(f"\nWorkflow Health: {status['health'].upper()}")
            print("Directory Counts:")
            for dir_name, count in status["directory_counts"].items():
                print(f"   {dir_name}: {count}")

            ai_features = report["ai_features"]
            total = ai_features["total_analyzed"]
            if total > 0:
                print("\nAI Feature Usage:")
                print(
                    f"   Notes with AI summaries: {ai_features['notes_with_ai_summaries']}/{total}"
                )
                print(
                    f"   Notes with AI processing: {ai_features['notes_with_ai_processing']}/{total}"
                )
                print(
                    f"   Notes with AI tags: {ai_features['notes_with_ai_tags']}/{total}"
                )

            recommendations = report.get("recommendations", [])
            if recommendations:
                print("\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")


# ============================================================================
# GREEN PHASE: SafeWorkflowManager Alias for Compatibility
# ============================================================================

# Create alias for backwards compatibility
SafeWorkflowManager = WorkflowManager


if __name__ == "__main__":
    main()


__all__ = [
    # Core
    "WorkflowManager",
    "SafeWorkflowManager",
    # Coordinators
    "BatchProcessingCoordinator",
    "NoteProcessingCoordinator",
    "WorkflowReportingCoordinator",
    # Utilities
    "WorkflowProcessingResult",
    "BatchProcessingStats",
    "SafeWorkflowProcessor",
    "AtomicWorkflowEngine",
    "IntegrityMonitoringManager",
    "ConcurrentSessionManager",
    "PerformanceMetricsCollector",
    # Functions
    "batch_process_unprocessed_inbox",
    "is_note_eligible_for_processing",
    "scan_eligible_notes",
    "process_single_note",
]
