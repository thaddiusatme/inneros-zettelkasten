"""
Automation Event Handler - Processes FileWatcher events through CoreWorkflowManager

Implements event-driven automation with debouncing, error handling, and health monitoring.
Integrates FileWatcher events with AI processing pipeline for automated knowledge capture.

Architecture:
- <200 LOC (ADR-001 compliant)
- Single responsibility: FileWatcher events → CoreWorkflowManager processing
- Debouncing prevents duplicate processing during active editing
- Health monitoring for daemon integration
"""

import threading
import time
from pathlib import Path
from typing import Dict, Any
from collections import deque

from src.ai.workflow_manager_adapter import LegacyWorkflowManagerAdapter


class AutomationEventHandler:
    """
    Processes file system events through CoreWorkflowManager AI pipeline.
    
    Provides debounced event processing to prevent duplicate work during
    active file editing. Tracks metrics for health monitoring and daemon integration.
    
    Size: ~120 LOC (ADR-001 compliant)
    """
    
    def __init__(self, vault_path: str, debounce_seconds: float = 2.0):
        """
        Initialize event handler with CoreWorkflowManager.
        
        Args:
            vault_path: Path to Zettelkasten vault root
            debounce_seconds: Delay before processing events (default 2.0s)
            
        Raises:
            ValueError: If vault_path doesn't exist
        """
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"vault_path does not exist: {vault_path}")
        
        self.debounce_seconds = debounce_seconds
        
        # Initialize CoreWorkflowManager via adapter
        self.core_workflow = LegacyWorkflowManagerAdapter(base_directory=str(vault_path))
        
        # Event queue and debouncing
        self.event_queue: deque = deque()
        self._debounce_timers: Dict[str, threading.Timer] = {}
        
        # Metrics tracking
        self._processing_stats = {
            'total_events_processed': 0,
            'successful_events': 0,
            'failed_events': 0,
            'processing_times': []
        }
    
    def process_file_event(self, file_path: Path, event_type: str) -> Dict[str, Any]:
        """
        Process file event with filtering and debouncing.
        
        Args:
            file_path: Path to the file that triggered event
            event_type: Event type ('created', 'modified', 'deleted')
            
        Returns:
            Processing result or skip reason:
            {
                'success': bool,
                'skipped': bool (if filtered),
                'reason': str (skip reason),
                'result': dict (CoreWorkflowManager result if processed)
            }
        """
        # Filter 1: Ignore deleted events
        if event_type == 'deleted':
            return {'skipped': True, 'reason': 'deleted_event'}
        
        # Filter 2: Only process markdown files
        if not str(file_path).endswith('.md'):
            return {'skipped': True, 'reason': 'not_markdown'}
        
        # Cancel existing timer for this file (last event wins)
        file_key = str(file_path)
        if file_key in self._debounce_timers:
            self._debounce_timers[file_key].cancel()
        
        # Create new debounce timer
        timer = threading.Timer(
            self.debounce_seconds,
            self._execute_processing,
            args=(file_path,)
        )
        self._debounce_timers[file_key] = timer
        timer.start()
        
        return {'queued': True, 'file_path': str(file_path), 'event_type': event_type}
    
    def _execute_processing(self, file_path: Path) -> Dict[str, Any]:
        """
        Execute CoreWorkflowManager processing after debounce.
        
        Args:
            file_path: Path to note file to process
            
        Returns:
            Processing result with metrics
        """
        file_key = str(file_path)
        start_time = time.time()
        
        try:
            # Call CoreWorkflowManager.process_inbox_note()
            result = self.core_workflow.process_inbox_note(str(file_path))
            
            # Track metrics
            duration = time.time() - start_time
            self._processing_stats['total_events_processed'] += 1
            self._processing_stats['successful_events'] += 1
            self._processing_stats['processing_times'].append(duration)
            
            # Clean up timer
            if file_key in self._debounce_timers:
                del self._debounce_timers[file_key]
            
            return {
                'success': True,
                'result': result,
                'processing_time': duration
            }
            
        except Exception as e:
            # Graceful error handling for daemon stability
            duration = time.time() - start_time
            self._processing_stats['total_events_processed'] += 1
            self._processing_stats['failed_events'] += 1
            
            # Clean up timer
            if file_key in self._debounce_timers:
                del self._debounce_timers[file_key]
            
            return {
                'success': False,
                'error': str(e),
                'processing_time': duration
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Return event handler health status.
        
        Returns:
            Health status dict:
            {
                'is_healthy': bool,
                'queue_depth': int,
                'processing_count': int
            }
        """
        return {
            'is_healthy': True,
            'queue_depth': len(self.event_queue),
            'processing_count': self._processing_stats['total_events_processed']
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Return event processing metrics.
        
        Returns:
            Metrics dict:
            {
                'total_events_processed': int,
                'successful_events': int,
                'failed_events': int,
                'avg_processing_time': float
            }
        """
        processing_times = self._processing_stats['processing_times']
        avg_time = sum(processing_times) / len(processing_times) if processing_times else 0.0
        
        return {
            'total_events_processed': self._processing_stats['total_events_processed'],
            'successful_events': self._processing_stats['successful_events'],
            'failed_events': self._processing_stats['failed_events'],
            'avg_processing_time': avg_time
        }
