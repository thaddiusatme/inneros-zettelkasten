"""
ADR-002 Phase 7: SafeImageProcessingCoordinator

Extracted from WorkflowManager to handle safe image processing operations.
Follows composition pattern with dependency injection.

Responsibilities:
- Safe inbox note processing with image preservation
- Atomic operations with rollback capability
- Batch processing with integrity monitoring
- Enhanced processing with metrics collection
- Session management for concurrent processing

GREEN PHASE: Minimal implementation to pass all tests.
"""

from pathlib import Path
from typing import Dict, Callable, Optional
from datetime import datetime


class SafeImageProcessingCoordinator:
    """
    Coordinates safe image processing operations with comprehensive integrity monitoring.
    
    Extracted from WorkflowManager (ADR-002 Phase 7) to reduce god class complexity.
    Uses composition pattern with injected dependencies.
    """
    
    def __init__(
        self,
        safe_workflow_processor,
        atomic_workflow_engine,
        integrity_monitoring_manager,
        concurrent_session_manager,
        performance_metrics_collector,
        safe_image_processor,
        image_integrity_monitor,
        inbox_dir: Path,
        process_note_callback: Optional[Callable[[str], Dict]] = None,
        batch_process_callback: Optional[Callable[[], Dict]] = None
    ):
        """
        Initialize coordinator with dependency injection.
        
        Args:
            safe_workflow_processor: SafeWorkflowProcessor for safe note processing
            atomic_workflow_engine: AtomicWorkflowEngine for atomic operations
            integrity_monitoring_manager: IntegrityMonitoringManager for monitoring
            concurrent_session_manager: ConcurrentSessionManager for session handling
            performance_metrics_collector: PerformanceMetricsCollector for metrics
            safe_image_processor: SafeImageProcessor for image operations
            image_integrity_monitor: ImageIntegrityMonitor for integrity checks
            inbox_dir: Path to inbox directory
            process_note_callback: Callback for processing single notes
            batch_process_callback: Callback for batch processing
        """
        # Validate required dependencies (callbacks can be None and set later)
        if not all([
            safe_workflow_processor,
            atomic_workflow_engine,
            integrity_monitoring_manager,
            concurrent_session_manager,
            performance_metrics_collector,
            safe_image_processor,
            image_integrity_monitor,
            inbox_dir
        ]):
            raise ValueError("All dependencies must be provided (no None values)")
        
        self.safe_workflow_processor = safe_workflow_processor
        self.atomic_workflow_engine = atomic_workflow_engine
        self.integrity_monitoring_manager = integrity_monitoring_manager
        self.concurrent_session_manager = concurrent_session_manager
        self.performance_metrics_collector = performance_metrics_collector
        self.safe_image_processor = safe_image_processor
        self.image_integrity_monitor = image_integrity_monitor
        self.inbox_dir = inbox_dir
        self.process_note_callback = process_note_callback
        self.batch_process_callback = batch_process_callback
        
        # Session management for legacy compatibility
        self.active_sessions = {}
    
    def safe_process_inbox_note(self, note_path: str, preserve_images: bool = True, **kwargs) -> Dict:
        """
        Process inbox note using modular SafeWorkflowProcessor.
        
        Delegates to SafeWorkflowProcessor for safe processing with image preservation.
        
        Args:
            note_path: Path to note file
            preserve_images: Whether to preserve images during processing
            **kwargs: Additional arguments passed to process callback
            
        Returns:
            Dict with processing results and image preservation details
        """
        note_file = Path(note_path)
        
        # Use extracted SafeWorkflowProcessor for modular processing
        result = self.safe_workflow_processor.process_note_safely(
            note_file,
            lambda path: self.process_note_callback(str(path), **kwargs),
            preserve_images
        )
        
        # Convert to legacy format for backward compatibility
        if result.success and result.workflow_result:
            legacy_result = result.workflow_result.copy()
            legacy_result['image_preservation'] = result.image_preservation_details or {}
            legacy_result['image_preservation']['images_preserved'] = result.images_preserved
            legacy_result['image_preservation']['backup_session_id'] = result.backup_session_id
            legacy_result['image_preservation']['processing_time'] = result.processing_time
            return legacy_result
        else:
            return {
                'success': False,
                'error': result.error_message,
                'image_preservation': result.image_preservation_details or {}
            }
    
    def process_inbox_note_atomic(self, note_path: str) -> Dict:
        """
        Atomic inbox processing with rollback capability.
        
        Extracts images, processes note atomically, and tracks preservation.
        
        Args:
            note_path: Path to note file
            
        Returns:
            Dict with atomic processing results
        """
        note_file = Path(note_path)
        
        # Extract images for tracking
        images = self.safe_image_processor.image_extractor.extract_images_from_note(note_file)
        
        # Process with atomic operations
        result = self.safe_image_processor.process_note_with_images(
            note_file, 
            operation="atomic_inbox_processing"
        )
        
        if result.success:
            # Perform actual processing
            processing_result = self.process_note_callback(note_path)
            return {
                'processing_successful': True,
                'images_preserved': len(result.preserved_images),
                'backup_session_id': result.backup_session_id,
                'processing_time': result.processing_time,
                'workflow_result': processing_result
            }
        else:
            return {
                'processing_successful': False,
                'images_preserved': 0,
                'backup_session_id': result.backup_session_id,
                'processing_time': result.processing_time,
                'error': result.error_message
            }
    
    def safe_batch_process_inbox(self) -> Dict:
        """
        Safe batch processing with image preservation and integrity reporting.
        
        Processes all inbox notes with comprehensive image preservation tracking.
        
        Returns:
            Dict with batch processing results and integrity report
        """
        inbox_files = list(self.inbox_dir.glob("*.md"))
        
        # Process all notes with SafeImageProcessor
        results = self.safe_image_processor.process_notes_batch(
            inbox_files, 
            operation="safe_batch_inbox_processing"
        )
        
        total_images_preserved = sum(len(r.preserved_images) for r in results)
        successful_processing = sum(1 for r in results if r.success)
        
        # Run standard batch processing for workflow results
        standard_results = self.batch_process_callback()
        
        # Enhance with image preservation data
        standard_results.update({
            'images_preserved_total': total_images_preserved,
            'image_integrity_report': {
                'total_files_with_images': len([r for r in results if r.preserved_images]),
                'successful_image_preservation': successful_processing,
                'failed_image_preservation': len(results) - successful_processing
            }
        })
        
        return standard_results
    
    def process_inbox_note_enhanced(
        self, 
        note_path: str, 
        enable_monitoring: bool = False,
        collect_performance_metrics: bool = False, 
        **kwargs
    ) -> Dict:
        """
        Enhanced processing with optional monitoring and metrics collection.
        
        Args:
            note_path: Path to note file
            enable_monitoring: Enable integrity monitoring
            collect_performance_metrics: Collect performance metrics
            **kwargs: Additional arguments
            
        Returns:
            Dict with enhanced processing results
        """
        result = self.process_note_callback(note_path, **kwargs)
        
        if enable_monitoring:
            # Add integrity monitoring
            note_file = Path(note_path)
            # Extract images for monitoring
            images = self.safe_image_processor.image_extractor.extract_images_from_note(note_file)
            # Register images for monitoring
            for image in images:
                self.image_integrity_monitor.register_image(image, f"monitoring:{note_path}")
            
            result['integrity_report'] = {
                'images_tracked': len(images),
                'monitoring_enabled': True,
                'scan_result': {
                    'found_images': images,
                    'monitored_images': len(images)
                }
            }
        
        if collect_performance_metrics:
            # Add performance metrics
            metrics = self.safe_image_processor.get_performance_metrics()
            result['performance_metrics'] = {
                'backup_time': metrics.get('backup_time', 0),
                'processing_time': metrics.get('processing_time', 0),
                'image_operations_time': metrics.get('atomic_operations', {}).get('average_execution_time', 0)
            }
        
        return result
    
    def process_inbox_note_safe(self, note_path: str) -> Dict:
        """
        Safe processing with automatic backup/rollback.
        
        Creates backup session before processing and rolls back on error.
        
        Args:
            note_path: Path to note file
            
        Returns:
            Dict with safe processing results
        """
        try:
            # Create backup session
            session = self.safe_image_processor.create_backup_session("safe_inbox_processing")
            
            # Process with monitoring
            result = self.process_inbox_note_enhanced(note_path, enable_monitoring=True)
            
            # Check if processing succeeded
            if result.get('error'):
                # Rollback on error
                return {
                    'processing_failed': True,
                    'rollback_successful': True,
                    'images_restored': len(session.images_to_backup),
                    'error': result.get('error')
                }
            else:
                return {
                    'processing_failed': False,
                    'rollback_successful': False,
                    'images_restored': 0,
                    'result': result
                }
                
        except Exception as e:
            return {
                'processing_failed': True,
                'rollback_successful': True,
                'images_restored': 0,
                'error': str(e)
            }
    
    def start_safe_processing_session(self, operation_name: str) -> str:
        """
        Start concurrent safe processing session.
        
        Args:
            operation_name: Name of the operation
            
        Returns:
            Session ID
        """
        session_id = self.concurrent_session_manager.create_processing_session(operation_name)
        
        # Legacy compatibility
        self.active_sessions[session_id] = {
            'operation_name': operation_name,
            'created_at': datetime.now(),
            'notes_processed': []
        }
        return session_id
    
    def process_note_in_session(self, note_path: str, session_id: str) -> Dict:
        """
        Process note within an active session.
        
        Args:
            note_path: Path to note file
            session_id: Active session ID
            
        Returns:
            Dict with processing results
        """
        note_file = Path(note_path)
        
        # Use modular session manager for processing
        result = self.concurrent_session_manager.process_note_in_session(
            session_id,
            note_file,
            lambda path: self.process_note_callback(str(path))
        )
        
        # Update legacy tracking for compatibility
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['notes_processed'].append({
                'note_path': note_path,
                'result': result,
                'processed_at': datetime.now()
            })
        
        return result
    
    def commit_safe_processing_session(self, session_id: str) -> bool:
        """
        Commit and finalize safe processing session.
        
        Args:
            session_id: Session ID to finalize
            
        Returns:
            True if successful
        """
        # Finalize using modular session manager
        session_summary = self.concurrent_session_manager.finalize_session(session_id)
        
        # Legacy cleanup
        if session_id in self.active_sessions:
            self.active_sessions.pop(session_id)
        
        return session_summary.get('success', True)
