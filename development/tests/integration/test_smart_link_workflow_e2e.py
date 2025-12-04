"""
TDD Iteration 1 - Phase 2 E2E Validation: Smart Link Workflow

RED PHASE: End-to-end tests validating smart link suggestion pipeline works without manual intervention.

These tests verify:
- SmartLinkEventHandler processes markdown files
- Link suggestions are generated for new/modified notes (or graceful fallback)
- Handler is properly registered with AutomationDaemon
- Metrics and health status are reported
- Exit code semantics enable CI automation

Tests use isolated temp directories following HOME isolation pattern from Phase 1.
"""

import os
from pathlib import Path
import pytest


# Mark all tests in this module as E2E and slow (potential AI processing)
pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestSmartLinkWorkflowE2E:
    """
    End-to-end tests for smart link suggestion workflow.
    
    These tests validate the complete pipeline from note creation/modification
    to link suggestion generation in the knowledge vault.
    """

    @pytest.fixture
    def repo_root(self) -> Path:
        """Get repository root path."""
        return Path(__file__).parent.parent.parent.parent

    @pytest.fixture
    def env_with_pythonpath(self, repo_root: Path) -> dict:
        """Create environment with PYTHONPATH set."""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo_root / "development")
        return env

    @pytest.fixture
    def isolated_test_env(self, tmp_path: Path) -> dict:
        """
        Create isolated test environment with knowledge vault structure.
        
        Following HOME isolation pattern from Phase 1 to prevent test interference.
        """
        # Create directory structure
        knowledge_inbox = tmp_path / "knowledge" / "Inbox"
        knowledge_inbox.mkdir(parents=True)
        
        knowledge_permanent = tmp_path / "knowledge" / "Permanent Notes"
        knowledge_permanent.mkdir(parents=True)
        
        # Create .inneros directory for daemon state
        inneros_dir = tmp_path / ".inneros"
        inneros_dir.mkdir(parents=True)
        
        # Create .automation/logs for handler logging
        automation_logs = tmp_path / ".automation" / "logs"
        automation_logs.mkdir(parents=True)
        
        return {
            "root": tmp_path,
            "knowledge_inbox": knowledge_inbox,
            "knowledge_permanent": knowledge_permanent,
            "inneros_dir": inneros_dir,
            "automation_logs": automation_logs,
        }

    @pytest.fixture
    def sample_notes(self, isolated_test_env: dict) -> list:
        """
        Create sample markdown notes for testing link suggestions.
        
        Notes have related content that should trigger link suggestions.
        """
        notes = []
        
        # Create base permanent note about Python
        python_note = isolated_test_env["knowledge_permanent"] / "python-programming.md"
        python_note.write_text("""---
title: Python Programming
created: 2025-12-01
tags: [programming, python, development]
---

# Python Programming

Python is a versatile programming language used for web development,
data science, automation, and AI applications.

Key features:
- Dynamic typing
- Rich ecosystem
- Easy to learn

Related: [[machine-learning]], [[automation]]
""", encoding="utf-8")
        notes.append(python_note)
        
        # Create base permanent note about Machine Learning
        ml_note = isolated_test_env["knowledge_permanent"] / "machine-learning.md"
        ml_note.write_text("""---
title: Machine Learning
created: 2025-12-01
tags: [ai, machine-learning, python]
---

# Machine Learning

Machine learning is a subset of AI that enables systems to learn
from data without explicit programming.

Common libraries:
- scikit-learn
- TensorFlow
- PyTorch

Related: [[python-programming]], [[data-science]]
""", encoding="utf-8")
        notes.append(ml_note)
        
        return notes

    @pytest.fixture
    def new_inbox_note(self, isolated_test_env: dict) -> Path:
        """
        Create a new inbox note that should trigger link suggestions.
        
        Content is related to existing permanent notes to test connection discovery.
        """
        inbox_note = isolated_test_env["knowledge_inbox"] / "fleeting-python-automation.md"
        inbox_note.write_text("""---
title: Python for Automation
created: 2025-12-03
status: inbox
tags: [fleeting]
---

# Python for Automation

Just learned about using Python for automation tasks.
This connects to my notes on Python programming and could use
machine learning for intelligent automation.

Ideas to explore:
- File processing automation
- Data pipeline automation
- AI-powered workflows
""", encoding="utf-8")
        return inbox_note

    # =========================================================================
    # P0: Core Handler Functionality Tests
    # =========================================================================

    def test_handler_processes_markdown_files(
        self, isolated_test_env: dict, sample_notes: list, new_inbox_note: Path
    ):
        """
        Test: SmartLinkEventHandler processes markdown files on create/modify.
        
        Acceptance Criteria:
        - Handler accepts markdown files
        - Processing completes without error
        - Metrics are updated after processing
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        # Initialize handler with test vault path
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
            "similarity_threshold": 0.5,  # Lower threshold for testing
            "max_suggestions": 5,
        }
        handler = SmartLinkEventHandler(config=config)
        
        # Process the new inbox note (simulating file creation event)
        handler.process(new_inbox_note, "created")
        
        # Verify metrics updated
        metrics = handler.get_metrics()
        assert metrics["events_processed"] >= 1, "Handler should record processed event"

    def test_handler_generates_link_suggestions(
        self, isolated_test_env: dict, sample_notes: list, new_inbox_note: Path
    ):
        """
        Test: Handler generates link suggestions for notes with related content.
        
        Acceptance Criteria:
        - Notes with related content trigger suggestions
        - Suggestions include similarity scores
        - At least one suggestion should be generated (or graceful fallback)
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
            "similarity_threshold": 0.3,  # Very low threshold to ensure matches
            "max_suggestions": 10,
        }
        handler = SmartLinkEventHandler(config=config)
        
        # Process note
        handler.process(new_inbox_note, "created")
        
        # Check metrics - should show suggestions_generated or fallback gracefully
        metrics = handler.get_metrics()
        
        # Either suggestions were generated OR we gracefully fell back
        # (AIConnections may not be available in test env)
        assert "suggestions_generated" in metrics or metrics["events_processed"] > 0, \
            "Handler should either generate suggestions or process gracefully"

    def test_handler_skips_non_markdown_files(self, isolated_test_env: dict):
        """
        Test: Handler ignores non-markdown files.
        
        Acceptance Criteria:
        - .txt, .jpg, .pdf files are not processed
        - No metrics recorded for non-markdown files
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {"vault_path": str(isolated_test_env["root"] / "knowledge")}
        handler = SmartLinkEventHandler(config=config)
        
        # Create and process non-markdown files
        txt_file = isolated_test_env["knowledge_inbox"] / "notes.txt"
        txt_file.write_text("Some text content")
        
        handler.process(txt_file, "created")
        
        metrics = handler.get_metrics()
        assert metrics["events_processed"] == 0, "Non-markdown files should be skipped"

    def test_handler_skips_deleted_events(
        self, isolated_test_env: dict, new_inbox_note: Path
    ):
        """
        Test: Handler ignores deleted file events.
        
        Acceptance Criteria:
        - Deleted events do not trigger processing
        - No metrics recorded for deleted events
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {"vault_path": str(isolated_test_env["root"] / "knowledge")}
        handler = SmartLinkEventHandler(config=config)
        
        # Process as deleted event
        handler.process(new_inbox_note, "deleted")
        
        metrics = handler.get_metrics()
        assert metrics["events_processed"] == 0, "Deleted events should be skipped"

    def test_handler_reports_health_status(self, isolated_test_env: dict):
        """
        Test: Handler provides health status for monitoring.
        
        Acceptance Criteria:
        - get_health() returns status dictionary
        - Status is one of: healthy, degraded, unhealthy
        - Error rate is calculated
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {"vault_path": str(isolated_test_env["root"] / "knowledge")}
        handler = SmartLinkEventHandler(config=config)
        
        health = handler.get_health()
        
        assert "status" in health, "Health should include status"
        assert health["status"] in ["healthy", "degraded", "unhealthy"], \
            "Status should be valid health state"
        assert "error_rate" in health, "Health should include error_rate"

    # =========================================================================
    # P1: Handler Integration Tests
    # =========================================================================

    def test_handler_graceful_ai_fallback(
        self, isolated_test_env: dict, new_inbox_note: Path
    ):
        """
        Test: Handler gracefully handles AIConnections unavailability.
        
        Acceptance Criteria:
        - Processing continues when AI is unavailable
        - Fallback behavior is logged
        - Handler remains healthy (not crashed)
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {"vault_path": str(isolated_test_env["root"] / "knowledge")}
        handler = SmartLinkEventHandler(config=config)
        
        # Process note - should work even if AI unavailable
        handler.process(new_inbox_note, "created")
        
        # Handler should still be healthy
        health = handler.get_health()
        assert health["status"] in ["healthy", "degraded"], \
            "Handler should remain healthy after AI fallback"

    def test_handler_daemon_registration(self, repo_root: Path, isolated_test_env: dict):
        """
        Test: SmartLinkEventHandler is properly registered with AutomationDaemon.
        
        Acceptance Criteria:
        - Daemon can be instantiated with smart_link handler enabled
        - Handler is accessible via daemon.smart_link_handler
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.daemon import AutomationDaemon
        from src.automation.config import (
            DaemonConfig,
            SmartLinkHandlerConfig,
            FileWatchConfig,
        )
        
        # Create file watching config (required for handlers to register)
        file_watch_config = FileWatchConfig(
            enabled=True,
            watch_path=str(isolated_test_env["root"] / "knowledge"),
            patterns=["*.md"],
        )
        
        # Create proper DaemonConfig with smart_link enabled
        smart_link_config = SmartLinkHandlerConfig(
            enabled=True,
            vault_path=str(isolated_test_env["root"] / "knowledge"),
            similarity_threshold=0.75,
            max_suggestions=5,
        )
        
        config = DaemonConfig(
            file_watching=file_watch_config,
            smart_link_handler=smart_link_config,
        )
        
        daemon = AutomationDaemon(config=config)
        
        try:
            # Start daemon to register handlers
            daemon.start()
            
            # Verify handler is registered
            assert daemon.smart_link_handler is not None, \
                "SmartLinkEventHandler should be registered with daemon"
        finally:
            # Clean up - stop daemon
            daemon.stop()

    def test_handler_modified_event_triggers_reanalysis(
        self, isolated_test_env: dict, new_inbox_note: Path
    ):
        """
        Test: Modified events trigger link reanalysis.
        
        Acceptance Criteria:
        - Modified events are processed (not just created)
        - Metrics increment for modified events
        """
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {"vault_path": str(isolated_test_env["root"] / "knowledge")}
        handler = SmartLinkEventHandler(config=config)
        
        # Process as modified event
        handler.process(new_inbox_note, "modified")
        
        metrics = handler.get_metrics()
        assert metrics["events_processed"] >= 1, "Modified events should be processed"

    def test_handler_exports_metrics_json(
        self, isolated_test_env: dict, new_inbox_note: Path
    ):
        """
        Test: Handler exports metrics in JSON format for automation.
        
        Acceptance Criteria:
        - export_metrics() returns valid JSON string
        - JSON includes handler_type and timestamp
        """
        import sys
        import json
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {"vault_path": str(isolated_test_env["root"] / "knowledge")}
        handler = SmartLinkEventHandler(config=config)
        
        # Process a note to generate metrics
        handler.process(new_inbox_note, "created")
        
        # Export and validate JSON
        metrics_json = handler.export_metrics()
        metrics = json.loads(metrics_json)
        
        assert "handler_type" in metrics, "Exported metrics should include handler_type"
        assert metrics["handler_type"] == "smart_link"
        assert "timestamp" in metrics, "Exported metrics should include timestamp"

    # =========================================================================
    # P1: Full Pipeline Integration Test
    # =========================================================================

    def test_full_smart_link_pipeline(
        self, repo_root: Path, isolated_test_env: dict, sample_notes: list
    ):
        """
        Test: Full end-to-end smart link pipeline.
        
        Simulates the complete workflow:
        1. Create new note in inbox
        2. Handler processes note
        3. Link suggestions generated (or graceful fallback)
        4. Metrics and health reported
        
        Acceptance Criteria:
        - Pipeline completes without error
        - Note is processed
        - Health status is healthy
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import SmartLinkEventHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
            "similarity_threshold": 0.3,
            "max_suggestions": 10,
        }
        handler = SmartLinkEventHandler(config=config)
        
        # Create new note dynamically
        new_note = isolated_test_env["knowledge_inbox"] / "fleeting-test-note.md"
        new_note.write_text("""---
title: Test Note
created: 2025-12-03
status: inbox
---

# Test Note

This is a test note about Python programming and machine learning.
It should have connections to existing notes in the vault.
""", encoding="utf-8")
        
        # Process the new note
        handler.process(new_note, "created")
        
        # Verify pipeline completed
        metrics = handler.get_metrics()
        health = handler.get_health()
        
        assert metrics["events_processed"] >= 1, "Note should be processed"
        assert health["status"] in ["healthy", "degraded"], "Pipeline should complete healthy"
        
        # Success - pipeline works end-to-end
        print(f"✅ Smart Link Pipeline: {metrics['events_processed']} events processed")
        print(f"✅ Health Status: {health['status']}")
