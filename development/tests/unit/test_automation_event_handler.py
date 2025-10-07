"""
Automation Event Handler TDD Iteration 2 P1.2 - RED Phase

Complete test suite for AutomationEventHandler that processes FileWatcher events
through CoreWorkflowManager AI pipelines. Implements event-driven automation
with debouncing, error handling, and health monitoring.

Test Coverage:
- P0.1: Event Handler Initialization (2 tests) - CoreWorkflowManager integration
- P0.2: Event Processing (3 tests) - process_file_event() with AI workflows
- P0.3: Debouncing & Queue Management (3 tests) - prevent duplicate processing
- P0.4: Error Handling (2 tests) - graceful degradation when AI unavailable
- P0.5: Health Monitoring (2 tests) - event handler status tracking

Architecture Requirements (ADR-001):
- AutomationEventHandler <200 LOC
- Single responsibility: FileWatcher events → CoreWorkflowManager processing
- No god class - focused on event processing only
- Integration with existing health monitoring

RED Phase Target: 12/12 tests failing with clear ImportError/AttributeError messages
"""

import pytest
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Will fail: ImportError - AutomationEventHandler not yet defined
# from src.automation.event_handler import AutomationEventHandler


# ============================================================================
# P0.1: Event Handler Initialization (2 tests)
# ============================================================================

class TestEventHandlerInitialization:
    """Test AutomationEventHandler initialization with CoreWorkflowManager."""
    
    def test_event_handler_initializes_with_vault_path(self, tmp_path):
        """
        P0.1.1: Event handler initializes with vault path for CoreWorkflowManager.
        
        Expected behavior:
        - Creates CoreWorkflowManager instance internally
        - Initializes event queue (empty list/deque)
        - Sets up debouncing timer registry
        - No events processed until process_file_event() called
        
        Will fail: ImportError - AutomationEventHandler not yet defined
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault_path = tmp_path / "knowledge"
        vault_path.mkdir()
        (vault_path / "Inbox").mkdir()
        
        handler = AutomationEventHandler(vault_path=str(vault_path))
        
        assert handler.vault_path == Path(vault_path), "Should store vault path"
        assert handler.core_workflow is not None, "Should initialize CoreWorkflowManager"
        assert len(handler.event_queue) == 0, "Event queue should start empty"
        assert len(handler._debounce_timers) == 0, "No debounce timers initially"
    
    def test_event_handler_uses_default_debounce_seconds(self, tmp_path):
        """
        P0.1.2: Event handler accepts configurable debounce_seconds parameter.
        
        Expected behavior:
        - Default debounce_seconds = 2.0 (matches FileWatcher default)
        - Custom debounce_seconds configurable via constructor
        - Debounce setting used for event processing delay
        
        Will fail: ImportError - AutomationEventHandler not yet defined
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault_path = tmp_path / "knowledge"
        vault_path.mkdir()
        
        # Test default
        handler_default = AutomationEventHandler(vault_path=str(vault_path))
        assert handler_default.debounce_seconds == 2.0, "Should default to 2.0 seconds"
        
        # Test custom
        handler_custom = AutomationEventHandler(
            vault_path=str(vault_path),
            debounce_seconds=1.0
        )
        assert handler_custom.debounce_seconds == 1.0, "Should accept custom debounce"


# ============================================================================
# P0.2: Event Processing (3 tests)
# ============================================================================

class TestEventProcessing:
    """Test process_file_event() integration with CoreWorkflowManager."""
    
    @pytest.fixture
    def test_vault(self, tmp_path):
        """Create test vault with Inbox directory."""
        vault = tmp_path / "knowledge"
        inbox = vault / "Inbox"
        inbox.mkdir(parents=True)
        return vault, inbox
    
    def test_process_file_event_calls_core_workflow_manager(self, test_vault):
        """
        P0.2.1: process_file_event() invokes CoreWorkflowManager.process_inbox_note().
        
        Expected behavior:
        - Accepts file_path (Path) and event_type (str: 'created'|'modified')
        - Converts Path to string for CoreWorkflowManager
        - Calls core_workflow.process_inbox_note(note_path)
        - Returns processing result or queues for async processing
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'process_file_event'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        test_note = inbox / "test-note.md"
        test_note.write_text("---\ntitle: Test\n---\nContent")
        
        handler = AutomationEventHandler(vault_path=str(vault))
        
        # Mock CoreWorkflowManager to verify it's called
        with patch.object(handler.core_workflow, 'process_inbox_note') as mock_process:
            mock_process.return_value = {
                'success': True,
                'analytics': {'quality_score': 0.75}
            }
            
            # Process created event
            result = handler.process_file_event(test_note, "created")
            
            # Verify CoreWorkflowManager was called with correct path
            mock_process.assert_called_once()
            call_args = mock_process.call_args
            assert "test-note.md" in str(call_args[0][0]), "Should pass note path"
    
    def test_process_file_event_ignores_non_markdown_files(self, test_vault):
        """
        P0.2.2: Only .md files are processed - other extensions ignored.
        
        Expected behavior:
        - Check file extension before processing
        - Process: .md files only
        - Ignore: .txt, .tmp, .swp, images, etc.
        - Return early with {'skipped': True, 'reason': 'not_markdown'}
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'process_file_event'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        
        # Create non-markdown file
        txt_file = inbox / "test.txt"
        txt_file.write_text("Not markdown")
        
        handler = AutomationEventHandler(vault_path=str(vault))
        
        # Mock CoreWorkflowManager to verify it's NOT called
        with patch.object(handler.core_workflow, 'process_inbox_note') as mock_process:
            result = handler.process_file_event(txt_file, "created")
            
            # Should skip processing
            assert result.get('skipped') is True, "Should skip non-markdown files"
            assert 'not_markdown' in result.get('reason', ''), "Should explain why skipped"
            mock_process.assert_not_called()
    
    def test_process_file_event_handles_modified_events(self, test_vault):
        """
        P0.2.3: Handles both 'created' and 'modified' event types.
        
        Expected behavior:
        - 'created' events: Process immediately (new capture)
        - 'modified' events: Process after debounce (avoid processing while editing)
        - 'deleted' events: Ignored (no processing needed)
        - Event type logged for metrics tracking
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'process_file_event'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        test_note = inbox / "modified-note.md"
        test_note.write_text("---\ntitle: Modified\n---\nContent")
        
        handler = AutomationEventHandler(vault_path=str(vault))
        
        # Mock CoreWorkflowManager
        with patch.object(handler.core_workflow, 'process_inbox_note') as mock_process:
            mock_process.return_value = {'success': True}
            
            # Process modified event
            result = handler.process_file_event(test_note, "modified")
            
            # Should process (after debounce in async implementation)
            # For synchronous test, verify it's queued or processed
            assert result is not None, "Should return result or queue status"


# ============================================================================
# P0.3: Debouncing & Queue Management (3 tests)
# ============================================================================

class TestDebouncingAndQueue:
    """Test event queue management and debouncing to prevent duplicate processing."""
    
    @pytest.fixture
    def test_vault(self, tmp_path):
        """Create test vault with Inbox directory."""
        vault = tmp_path / "knowledge"
        inbox = vault / "Inbox"
        inbox.mkdir(parents=True)
        return vault, inbox
    
    def test_debouncing_prevents_duplicate_processing(self, test_vault):
        """
        P0.3.1: Rapid events on same file debounced - only processed once.
        
        Expected behavior:
        - Multiple events within debounce_seconds treated as single event
        - Timer resets on each new event (last event wins)
        - Only final event processed after debounce period
        - Prevents processing while user actively editing
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'process_file_event'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        test_note = inbox / "rapid-edits.md"
        test_note.write_text("---\ntitle: Rapid\n---\nV1")
        
        # Use short debounce for testing
        handler = AutomationEventHandler(vault_path=str(vault), debounce_seconds=0.2)
        
        # Mock CoreWorkflowManager to count invocations
        with patch.object(handler.core_workflow, 'process_inbox_note') as mock_process:
            mock_process.return_value = {'success': True}
            
            # Simulate rapid-fire modifications
            handler.process_file_event(test_note, "modified")
            time.sleep(0.05)  # 50ms between events (< debounce)
            handler.process_file_event(test_note, "modified")
            time.sleep(0.05)
            handler.process_file_event(test_note, "modified")
            
            # Wait for debounce to complete
            time.sleep(0.3)
            
            # Should only process once (after final event)
            assert mock_process.call_count == 1, "Should debounce rapid events to single processing"
    
    def test_event_queue_tracks_pending_events(self, test_vault):
        """
        P0.3.2: Event queue tracks events waiting for processing.
        
        Expected behavior:
        - Events added to queue when debounce active
        - Queue depth accessible for monitoring
        - Queue cleared as events processed
        - FIFO ordering for events on different files
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'event_queue'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        
        handler = AutomationEventHandler(vault_path=str(vault), debounce_seconds=0.5)
        
        # Create multiple test notes
        note1 = inbox / "note1.md"
        note1.write_text("---\ntitle: Note1\n---\nContent")
        note2 = inbox / "note2.md"
        note2.write_text("---\ntitle: Note2\n---\nContent")
        
        # Process events (should queue with debounce)
        handler.process_file_event(note1, "created")
        handler.process_file_event(note2, "created")
        
        # Queue should track pending events
        # (Exact queue structure depends on implementation - list, deque, dict)
        assert hasattr(handler, 'event_queue'), "Should have event_queue attribute"
    
    def test_deleted_events_ignored(self, test_vault):
        """
        P0.3.3: 'deleted' events do not trigger AI processing.
        
        Expected behavior:
        - 'deleted' event type detected and skipped
        - No CoreWorkflowManager invocation
        - Event logged for metrics but not queued
        - Return {'skipped': True, 'reason': 'deleted_event'}
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'process_file_event'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        
        handler = AutomationEventHandler(vault_path=str(vault))
        
        # Mock CoreWorkflowManager to verify it's NOT called
        with patch.object(handler.core_workflow, 'process_inbox_note') as mock_process:
            # Simulate deleted event (file doesn't exist)
            deleted_path = inbox / "deleted-note.md"
            result = handler.process_file_event(deleted_path, "deleted")
            
            # Should skip processing
            assert result.get('skipped') is True, "Should skip deleted events"
            mock_process.assert_not_called()


# ============================================================================
# P0.4: Error Handling (2 tests)
# ============================================================================

class TestErrorHandling:
    """Test graceful error handling when CoreWorkflowManager unavailable or fails."""
    
    @pytest.fixture
    def test_vault(self, tmp_path):
        """Create test vault with Inbox directory."""
        vault = tmp_path / "knowledge"
        inbox = vault / "Inbox"
        inbox.mkdir(parents=True)
        return vault, inbox
    
    def test_handles_core_workflow_manager_exception(self, test_vault):
        """
        P0.4.1: Graceful handling when CoreWorkflowManager.process_inbox_note() fails.
        
        Expected behavior:
        - Catch exceptions from CoreWorkflowManager
        - Log error with file path and exception details
        - Return error result: {'success': False, 'error': str(e)}
        - Daemon continues running (error doesn't crash event handler)
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'process_file_event'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        test_note = inbox / "problematic-note.md"
        test_note.write_text("---\ntitle: Problem\n---\nContent")
        
        handler = AutomationEventHandler(vault_path=str(vault))
        
        # Mock CoreWorkflowManager to raise exception
        with patch.object(handler.core_workflow, 'process_inbox_note') as mock_process:
            mock_process.side_effect = Exception("AI service unavailable")
            
            # Should handle exception gracefully
            result = handler.process_file_event(test_note, "created")
            
            assert result is not None, "Should return result even on error"
            assert result.get('success') is False, "Should indicate failure"
            assert 'error' in result, "Should include error message"
    
    def test_handles_missing_vault_path(self, tmp_path):
        """
        P0.4.2: Clear error when vault_path doesn't exist or is invalid.
        
        Expected behavior:
        - Validate vault_path exists during initialization
        - Raise ValueError with descriptive message if invalid
        - Error message includes provided path for debugging
        
        Will fail: ImportError - AutomationEventHandler not yet defined
        """
        from src.automation.event_handler import AutomationEventHandler
        
        invalid_path = tmp_path / "nonexistent" / "vault"
        
        with pytest.raises(ValueError, match="vault_path"):
            AutomationEventHandler(vault_path=str(invalid_path))


# ============================================================================
# P0.5: Health Monitoring (2 tests)
# ============================================================================

class TestHealthMonitoring:
    """Test event handler health check integration."""
    
    @pytest.fixture
    def test_vault(self, tmp_path):
        """Create test vault with Inbox directory."""
        vault = tmp_path / "knowledge"
        inbox = vault / "Inbox"
        inbox.mkdir(parents=True)
        return vault, inbox
    
    def test_get_health_status_returns_handler_health(self, test_vault):
        """
        P0.5.1: get_health_status() returns event handler operational status.
        
        Expected behavior:
        - Returns dict with 'is_healthy', 'queue_depth', 'processing_count'
        - is_healthy=True when handler operational
        - queue_depth shows pending events count
        - processing_count tracks total events processed
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'get_health_status'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        handler = AutomationEventHandler(vault_path=str(vault))
        
        health = handler.get_health_status()
        
        assert 'is_healthy' in health, "Should include is_healthy status"
        assert 'queue_depth' in health, "Should report queue depth"
        assert health['is_healthy'] is True, "Should be healthy when initialized"
        assert health['queue_depth'] == 0, "Queue should be empty initially"
    
    def test_get_metrics_tracks_event_processing_stats(self, test_vault):
        """
        P0.5.2: get_metrics() provides event processing statistics.
        
        Expected behavior:
        - Returns dict with processing metrics
        - Tracks: total_events_processed, successful_events, failed_events
        - Tracks: avg_processing_time, queue_depth_max
        - Metrics updated after each event processed
        
        Will fail: AttributeError - AutomationEventHandler has no attribute 'get_metrics'
        """
        from src.automation.event_handler import AutomationEventHandler
        
        vault, inbox = test_vault
        handler = AutomationEventHandler(vault_path=str(vault))
        
        metrics = handler.get_metrics()
        
        assert 'total_events_processed' in metrics, "Should track total events"
        assert 'successful_events' in metrics, "Should track successes"
        assert 'failed_events' in metrics, "Should track failures"
        assert metrics['total_events_processed'] == 0, "Should start at 0"


# ============================================================================
# Test Execution Summary
# ============================================================================

"""
RED Phase Test Summary:

TDD Iteration 2 P1.2 (RED PHASE): 12/12 tests WILL FAIL

P0.1 Event Handler Initialization (2 tests):
1. test_event_handler_initializes_with_vault_path - ImportError: AutomationEventHandler not defined
2. test_event_handler_uses_default_debounce_seconds - ImportError: AutomationEventHandler not defined

P0.2 Event Processing (3 tests):
3. test_process_file_event_calls_core_workflow_manager - AttributeError: no process_file_event
4. test_process_file_event_ignores_non_markdown_files - AttributeError: no process_file_event
5. test_process_file_event_handles_modified_events - AttributeError: no process_file_event

P0.3 Debouncing & Queue Management (3 tests):
6. test_debouncing_prevents_duplicate_processing - AttributeError: no process_file_event
7. test_event_queue_tracks_pending_events - AttributeError: no event_queue attribute
8. test_deleted_events_ignored - AttributeError: no process_file_event

P0.4 Error Handling (2 tests):
9. test_handles_core_workflow_manager_exception - AttributeError: no process_file_event
10. test_handles_missing_vault_path - ImportError: AutomationEventHandler not defined

P0.5 Health Monitoring (2 tests):
11. test_get_health_status_returns_handler_health - AttributeError: no get_health_status
12. test_get_metrics_tracks_event_processing_stats - AttributeError: no get_metrics

Next Phase: GREEN - Implement AutomationEventHandler class (~80 LOC)
Required implementation:
- src/automation/event_handler.py: AutomationEventHandler class
  - __init__(vault_path, debounce_seconds=2.0)
  - process_file_event(file_path, event_type) → dict
  - get_health_status() → dict
  - get_metrics() → dict
  - _debounce_event() - internal debouncing logic
  - event_queue (list/deque)
  - _debounce_timers (dict)
  - core_workflow (CoreWorkflowManager instance)

Integration points:
- src/automation/daemon.py: Wire event_handler into _on_file_event() callback
- src/automation/health.py: Add event_handler health check
"""
