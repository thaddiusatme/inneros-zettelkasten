"""
Smart workflow manager that integrates AI features into the Zettelkasten workflow.
Follows the established patterns from the project manifest.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .tagger import AITagger
from .summarizer import AISummarizer
from .connections import AIConnections
from .enhancer import AIEnhancer
from .analytics import NoteAnalytics
from .safe_image_processor import SafeImageProcessor
from .image_integrity_monitor import ImageIntegrityMonitor
from .note_lifecycle_manager import NoteLifecycleManager
from .connection_coordinator import ConnectionCoordinator
from .analytics_coordinator import AnalyticsCoordinator
from .promotion_engine import PromotionEngine
from .review_triage_coordinator import ReviewTriageCoordinator
from .note_processing_coordinator import NoteProcessingCoordinator
from .safe_image_processing_coordinator import SafeImageProcessingCoordinator
from .orphan_remediation_coordinator import OrphanRemediationCoordinator
from .fleeting_analysis_coordinator import FleetingAnalysisCoordinator, FleetingAnalysis
from .workflow_reporting_coordinator import WorkflowReportingCoordinator
from .batch_processing_coordinator import BatchProcessingCoordinator
from .fleeting_note_coordinator import FleetingNoteCoordinator
from .metadata_repair_engine import MetadataRepairEngine
from .workflow_integration_utils import (
    SafeWorkflowProcessor,
    AtomicWorkflowEngine,
    IntegrityMonitoringManager,
    ConcurrentSessionManager,
    PerformanceMetricsCollector,
)
from src.utils.frontmatter import parse_frontmatter
from src.utils.io import safe_write
from .workflow_metrics_coordinator import WorkflowMetricsCoordinator
from src.config.vault_config_loader import get_vault_config


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

        # Load vault configuration and define workflow directories
        vault_config = get_vault_config(str(self.base_dir))
        self.inbox_dir = vault_config.inbox_dir
        self.fleeting_dir = vault_config.fleeting_dir
        self.literature_dir = vault_config.literature_dir
        self.permanent_dir = vault_config.permanent_dir
        self.archive_dir = vault_config.archive_dir

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
            base_dir=self.base_dir,
            workflow_manager=self,
            min_similarity=0.7,
            max_suggestions=5,
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

        # ADR-002 Phase 13: Metrics coordination extraction
        # Phase 3.1: Real-time metrics collection via coordinator
        self.metrics_coordinator = WorkflowMetricsCoordinator()

        # ADR-002 Phase 7: Safe image processing coordinator extraction
        self.safe_image_processing_coordinator = SafeImageProcessingCoordinator(
            base_dir=self.base_dir,
            workflow_manager=self,
            safe_workflow_processor=self.safe_workflow_processor,
            atomic_workflow_engine=self.atomic_workflow_engine,
            integrity_monitoring_manager=self.integrity_monitoring_manager,
            concurrent_session_manager=self.concurrent_session_manager,
            performance_metrics_collector=self.performance_metrics_collector,
            safe_image_processor=self.safe_image_processor,
            image_integrity_monitor=self.image_integrity_monitor,
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
            base_dir=self.base_dir,
            workflow_manager=self,
            process_callback=self.process_inbox_note,
        )

        # ADR-002 Phase 12b: Fleeting note coordinator extraction
        self.fleeting_note_coordinator = FleetingNoteCoordinator(
            base_dir=self.base_dir,
            workflow_manager=self,
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

        # ADR-002 Phase 13: Record metrics via coordinator
        # Phase 3.1: Real-time metrics collection
        elapsed_ms = (time.time() - start_time) * 1000
        self.metrics_coordinator.record_note_processing(elapsed_ms, success=True)

        # P0-1.3: Update status to 'promoted' after successful AI processing
        # Only update status when:
        # - Not in dry-run mode (no file modifications)
        # - Not in fast mode (fast mode skips AI processing, just provides preview)
        # - File was actually updated (processing succeeded)
        # - No AI processing errors occurred
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

    # ADR-002 Phase 6: Template processing methods removed - delegated to NoteProcessingCoordinator
    # These methods are now internal to NoteProcessingCoordinator:
    # - _fix_template_placeholders()
    # - _preprocess_created_placeholder_in_raw()
    # - _merge_tags()

    def promote_note(self, note_path: str, target_type: str = "permanent") -> Dict:
        """
        Promote a note from inbox/fleeting to appropriate directory.

        ADR-002 Phase 4: Delegates to PromotionEngine.

        Args:
            note_path: Path to the note to promote
            target_type: Target note type ("permanent", "literature", or "fleeting")

        Returns:
            Promotion results
        """
        return self.promotion_engine.promote_note(note_path, target_type)

    def _validate_note_for_promotion(
        self, note_path: Path, frontmatter: Dict, quality_threshold: float
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate if a note is eligible for auto-promotion.

        Args:
            note_path: Path to the note
            frontmatter: Parsed frontmatter metadata
            quality_threshold: Minimum quality score required

        Returns:
            Tuple of (is_valid, note_type, error_message)
        """
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

        Args:
            show_progress: If True, print progress to stderr (for dashboard display)

        Returns:
            Dict with total_files, processed, failed, results, and summary
        """
        return self.batch_processing_coordinator.batch_process_inbox(
            show_progress=show_progress
        )

    def generate_workflow_report(self) -> Dict:
        """
        Generate a comprehensive workflow status report.

        ADR-002 Phase 10: Delegates to WorkflowReportingCoordinator.

        Returns:
            Dict with workflow_status, ai_features, analytics, and recommendations
        """
        return self.reporting_coordinator.generate_workflow_report()

    # NOTE: _load_notes_corpus() extracted to ConnectionCoordinator (ADR-002 Phase 2)

    def _merge_tags(self, existing_tags: List[str], new_tags: List[str]) -> List[str]:
        """Merge existing and new tags intelligently."""
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()

        merged = sorted(list(existing_set | new_set))
        return merged[: self.config["max_tags_per_note"]]

    def scan_review_candidates(self) -> List[Dict]:
        """
        Scan for notes that need weekly review attention.

        ADR-002 Phase 5: Delegates to ReviewTriageCoordinator.

        Returns:
            List of candidate dictionaries with path, source, and metadata
        """
        return self.review_triage_coordinator.scan_review_candidates()

    def generate_weekly_recommendations(
        self, candidates: List[Dict], dry_run: bool = False
    ) -> Dict:
        """
        Generate AI-powered recommendations for weekly review candidates.

        ADR-002 Phase 5: Delegates to ReviewTriageCoordinator.

        Args:
            candidates: List of candidate dictionaries
            dry_run: If True, use fast mode to skip external AI calls

        Returns:
            Dictionary with summary, recommendations, and timestamp
        """
        return self.review_triage_coordinator.generate_weekly_recommendations(
            candidates, dry_run
        )

    # Phase 5.5.4: Enhanced Review Features (delegated to AnalyticsCoordinator)
    def detect_orphaned_notes(self) -> List[Dict]:
        """
        Detect notes that have no bidirectional links to other notes.

        Orphaned notes are permanent notes that:
        - Are not linked to by any other notes
        - Do not link to any other notes

        Returns:
            List of orphaned note dictionaries with path, title, last_modified
        """
        return self.analytics_coordinator.detect_orphaned_notes()

    def detect_orphaned_notes_comprehensive(self) -> List[Dict]:
        """
        Detect orphaned notes across the entire repository (not just workflow directories).

        This scans ALL markdown files in the repository, not just Inbox/Fleeting/Permanent.
        Use this for a complete view of isolated notes in your knowledge graph.

        Returns:
            List of orphaned note dictionaries with path, title, last_modified
        """
        return self.analytics_coordinator.detect_orphaned_notes_comprehensive()

    def detect_stale_notes(self, days_threshold: int = 90) -> List[Dict]:
        """
        Detect notes that haven't been modified in a specified time period.

        Args:
            days_threshold: Number of days to consider a note stale (default: 90)

        Returns:
            List of stale note dictionaries with path, title, last_modified, days_since_modified
        """
        return self.analytics_coordinator.detect_stale_notes(days_threshold)

    def generate_enhanced_metrics(self) -> Dict:
        """
        Generate comprehensive metrics for weekly review including orphaned notes,
        stale notes, and advanced analytics.

        Returns:
            Dictionary with enhanced metrics:
            - orphaned_notes: List of orphaned notes
            - stale_notes: List of stale notes
            - link_density: Average links per note
            - note_age_distribution: Distribution of note ages
            - productivity_metrics: Creation and modification patterns
        """
        return self.analytics_coordinator.generate_enhanced_metrics()

    # Phase 5.6: Orphan Remediation (ADR-002 Phase 8: Delegated to OrphanRemediationCoordinator)
    def remediate_orphaned_notes(
        self,
        mode: str = "link",
        scope: str = "permanent",
        limit: int = 10,
        target: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict:
        """
        Remediate orphaned notes by inserting bidirectional links.

        ADR-002 Phase 8: Delegates to OrphanRemediationCoordinator.

        Args:
            mode: "link" (insert links) or "checklist" (output markdown checklist)
            scope: "permanent", "fleeting", or "all"
            limit: maximum number of orphaned notes to process
            target: explicit path to target MOC/note for inserting links
            dry_run: when True, do not modify files; preview only

        Returns:
            Dictionary with summary and actions performed or planned.
        """
        return self.orphan_remediation_coordinator.remediate_orphaned_notes(
            mode=mode, scope=scope, limit=limit, target=target, dry_run=dry_run
        )

    # Helper methods for enhanced features
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
        from pathlib import Path

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

    # Analytics helper methods removed - now handled by AnalyticsCoordinator (ADR-002 Phase 3)
    # Removed: _build_link_graph, _is_orphaned_note, _create_orphaned_note_info,
    # _create_stale_note_info, _extract_note_title, _calculate_link_density,
    # _calculate_note_age_distribution, _calculate_productivity_metrics

    # Phase 5.6 Extension: Fleeting Note Lifecycle Management

    def analyze_fleeting_notes(self) -> FleetingAnalysis:
        """
        Analyze fleeting notes collection for age distribution and health metrics.

        ADR-002 Phase 9: Delegates to FleetingAnalysisCoordinator.

        Returns:
            FleetingAnalysis: Data structure with age analysis results
        """
        return self.fleeting_analysis_coordinator.analyze_fleeting_notes()

    def generate_fleeting_health_report(self) -> Dict:
        """
        Generate a health report for fleeting notes with recommendations.

        ADR-002 Phase 9: Delegates to FleetingAnalysisCoordinator.

        Returns:
            Dict: Health report with status, distribution, and recommendations
        """
        return self.fleeting_analysis_coordinator.generate_fleeting_health_report()

    def generate_fleeting_triage_report(
        self, quality_threshold: Optional[float] = None, fast: bool = False
    ) -> Dict:
        """
        Generate AI-powered triage report for fleeting notes with quality assessment.

        ADR-002 Phase 5: Delegates to ReviewTriageCoordinator.

        Args:
            quality_threshold: Optional minimum quality threshold (0.0-1.0) for filtering
            fast: If True, use fast mode to skip external AI calls for speed

        Returns:
            Dict: Triage report with quality assessment and recommendations
        """
        return self.review_triage_coordinator.generate_fleeting_triage_report(
            quality_threshold, fast
        )

    def promote_fleeting_note(
        self,
        note_path: str,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
    ) -> Dict:
        """
        Promote a single fleeting note to permanent or literature status.

        ADR-002 Phase 4: Delegates to PromotionEngine.

        Args:
            note_path: Path to the fleeting note to promote
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes

        Returns:
            Dict: Promotion results with details of operations performed
        """
        return self.promotion_engine.promote_fleeting_note(
            note_path, target_type, preview_mode
        )

    def promote_fleeting_notes_batch(
        self,
        quality_threshold: float = 0.7,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
    ) -> Dict:
        """
        Promote multiple fleeting notes based on quality threshold.

        ADR-002 Phase 4: Delegates to PromotionEngine.

        Args:
            quality_threshold: Minimum quality score for promotion
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes

        Returns:
            Dict: Batch promotion results
        """
        return self.promotion_engine.promote_fleeting_notes_batch(
            quality_threshold, target_type, preview_mode
        )

    def auto_promote_ready_notes(
        self, dry_run: bool = False, quality_threshold: float = 0.7
    ) -> Dict:
        """
        Automatically promote notes that meet quality threshold.

        ADR-002 Phase 11: Delegates to PromotionEngine.auto_promote_ready_notes().
        Follows established delegation pattern from promote_note() and promote_fleeting_notes_batch().

        Args:
            dry_run: If True, preview promotions without making changes
            quality_threshold: Minimum quality score required (default: 0.7)

        Returns:
            Dict: Auto-promotion results with counts and details
        """
        return self.promotion_engine.auto_promote_ready_notes(
            dry_run=dry_run, quality_threshold=quality_threshold
        )

    def repair_inbox_metadata(self, execute: bool = False) -> Dict:
        """
        Repair missing frontmatter metadata in Inbox notes.

        ADR-002 Phase 13: Delegates to MetadataRepairEngine for metadata repair operations.
        Fixes critical blocker where 8 notes (21%) are missing 'type:' field.

        Args:
            execute: If True, actually modify files. If False (default), preview only.

        Returns:
            Dict: Repair results with counts and details
        """
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
            print("📥 Processing all inbox notes...")
            result = workflow.batch_process_inbox()

            print("📊 Results:")
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
        print(f"📈 Promoting note: {args.note}")
        result = workflow.promote_note(args.note, args.type)

        if result.get("success"):
            print(f"✅ Successfully promoted to {result['type']}")
            print(f"   From: {result['source']}")
            print(f"   To: {result['target']}")
            if result.get("has_summary"):
                print("   Added AI summary")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    elif args.command == "report":
        print("📊 Generating workflow report...")
        report = workflow.generate_workflow_report()

        if args.output:
            # Use atomic write to prevent partial JSON writes on interruption
            report_json = json.dumps(report, indent=2, default=str)
            safe_write(args.output, report_json)
            print(f"📄 Report saved to: {args.output}")
        else:
            # Display summary
            status = report["workflow_status"]
            print(f"\n🏥 Workflow Health: {status['health'].upper()}")
            print("📁 Directory Counts:")
            for dir_name, count in status["directory_counts"].items():
                print(f"   {dir_name}: {count}")

            ai_features = report["ai_features"]
            total = ai_features["total_analyzed"]
            if total > 0:
                print("\n🤖 AI Feature Usage:")
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
                print("\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")


# ============================================================================
# GREEN PHASE: SafeWorkflowManager Alias for Compatibility
# ============================================================================

# Create alias for backwards compatibility
SafeWorkflowManager = WorkflowManager


if __name__ == "__main__":
    main()
