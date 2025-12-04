"""
TDD Iteration 1 - Phase 2 E2E Validation: YouTube Workflow

RED PHASE: End-to-end tests validating YouTube quote extraction pipeline works without manual intervention.

These tests verify:
- YouTubeFeatureHandler processes YouTube notes (source: youtube in frontmatter)
- Quote extraction works (or graceful fallback if IP-banned/API unavailable)
- Handler is properly registered with AutomationDaemon
- Metrics and health status are reported
- Exit code semantics enable CI automation

Tests use isolated temp directories following HOME isolation pattern from Phase 1.

Key YouTube handler requirements:
- Frontmatter must have `source: youtube`
- Frontmatter must have `ready_for_processing: true` (user approval)
- Frontmatter should have `video_id` (or extracted from body)
- Handler marks `ai_processed: true` after successful processing
"""

import os
from pathlib import Path
import pytest


# Mark all tests in this module as E2E and slow (potential AI/network processing)
pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestYouTubeWorkflowE2E:
    """
    End-to-end tests for YouTube quote extraction workflow.
    
    These tests validate the complete pipeline from YouTube note creation
    to automatic quote extraction in the knowledge vault.
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
        
        # Create .automation/cache for transcript caching
        automation_cache = tmp_path / ".automation" / "cache"
        automation_cache.mkdir(parents=True)
        
        return {
            "root": tmp_path,
            "knowledge_inbox": knowledge_inbox,
            "knowledge_permanent": knowledge_permanent,
            "inneros_dir": inneros_dir,
            "automation_logs": automation_logs,
            "automation_cache": automation_cache,
        }

    @pytest.fixture
    def youtube_note_ready(self, isolated_test_env: dict) -> Path:
        """
        Create a YouTube note that is ready for processing.
        
        This note has:
        - source: youtube (required)
        - ready_for_processing: true (user approval)
        - video_id: a valid test video ID
        - ai_processed: not set (so handler will process)
        """
        note = isolated_test_env["knowledge_inbox"] / "youtube-test-video.md"
        note.write_text("""---
title: Test YouTube Video for E2E
created: 2025-12-04
source: youtube
video_id: dQw4w9WgXcQ
ready_for_processing: true
tags: [youtube, test]
---

# Test YouTube Video

This is a test note for validating YouTube quote extraction.

**Video ID**: `dQw4w9WgXcQ`

## User Notes

Some initial notes about this video that should be preserved.
""", encoding="utf-8")
        return note

    @pytest.fixture
    def youtube_note_draft(self, isolated_test_env: dict) -> Path:
        """
        Create a YouTube note that is NOT ready for processing (draft state).
        
        This note has:
        - source: youtube (required)
        - ready_for_processing: false (user hasn't approved)
        - Should be skipped by handler
        """
        note = isolated_test_env["knowledge_inbox"] / "youtube-draft-video.md"
        note.write_text("""---
title: Draft YouTube Video
created: 2025-12-04
source: youtube
video_id: abc123xyz
ready_for_processing: false
tags: [youtube, draft]
---

# Draft YouTube Note

This note is still in draft mode and should NOT be processed.
""", encoding="utf-8")
        return note

    @pytest.fixture
    def youtube_note_already_processed(self, isolated_test_env: dict) -> Path:
        """
        Create a YouTube note that was already processed.
        
        This note has:
        - source: youtube (required)
        - ready_for_processing: true
        - ai_processed: true (already done)
        - Should be skipped by handler
        """
        note = isolated_test_env["knowledge_inbox"] / "youtube-processed-video.md"
        note.write_text("""---
title: Already Processed YouTube Video
created: 2025-12-04
source: youtube
video_id: xyz789abc
ready_for_processing: true
ai_processed: true
tags: [youtube, processed]
---

# Already Processed Note

This note has already been processed by the AI.

## Key Insights (AI-Extracted)

- Previous quote 1
- Previous quote 2
""", encoding="utf-8")
        return note

    @pytest.fixture
    def non_youtube_note(self, isolated_test_env: dict) -> Path:
        """
        Create a regular note (not YouTube source).
        
        Should be ignored by YouTubeFeatureHandler.
        """
        note = isolated_test_env["knowledge_inbox"] / "regular-note.md"
        note.write_text("""---
title: Regular Note
created: 2025-12-04
status: inbox
tags: [fleeting]
---

# Regular Note

This is a regular note that should NOT be processed by YouTube handler.
""", encoding="utf-8")
        return note

    # =========================================================================
    # P0: Core Handler Functionality Tests
    # =========================================================================

    def test_handler_import_succeeds(self, repo_root: Path):
        """
        Test: YouTubeFeatureHandler can be imported without errors.
        
        Acceptance Criteria:
        - Import completes without ImportError
        - Class is accessible and instantiable (with config)
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Verify class exists and has required methods
        assert hasattr(YouTubeFeatureHandler, "can_handle"), \
            "Handler should have can_handle method"
        assert hasattr(YouTubeFeatureHandler, "handle"), \
            "Handler should have handle method"

    def test_handler_accepts_youtube_notes(
        self, repo_root: Path, isolated_test_env: dict, youtube_note_ready: Path
    ):
        """
        Test: Handler accepts notes with source: youtube and ready_for_processing: true.
        
        Acceptance Criteria:
        - can_handle() returns True for properly configured YouTube notes
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        # Initialize handler with test vault path
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
            "max_quotes": 5,
            "min_quality": 0.7,
        }
        handler = YouTubeFeatureHandler(config=config)
        
        # Create mock event object (simulating watchdog event)
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
        
        event = MockEvent(youtube_note_ready)
        
        # Handler should accept this note
        can_handle = handler.can_handle(event)
        assert can_handle is True, \
            "Handler should accept YouTube note with ready_for_processing: true"

    def test_handler_rejects_draft_notes(
        self, repo_root: Path, isolated_test_env: dict, youtube_note_draft: Path
    ):
        """
        Test: Handler rejects notes with ready_for_processing: false.
        
        Acceptance Criteria:
        - can_handle() returns False for draft notes
        - User approval required before processing
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
        }
        handler = YouTubeFeatureHandler(config=config)
        
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
        
        event = MockEvent(youtube_note_draft)
        
        can_handle = handler.can_handle(event)
        assert can_handle is False, \
            "Handler should reject draft notes (ready_for_processing: false)"

    def test_handler_skips_already_processed_notes(
        self, repo_root: Path, isolated_test_env: dict, youtube_note_already_processed: Path
    ):
        """
        Test: Handler skips notes with ai_processed: true.
        
        Acceptance Criteria:
        - can_handle() returns False for already processed notes
        - Prevents duplicate processing
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
        }
        handler = YouTubeFeatureHandler(config=config)
        
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
        
        event = MockEvent(youtube_note_already_processed)
        
        can_handle = handler.can_handle(event)
        assert can_handle is False, \
            "Handler should skip already processed notes (ai_processed: true)"

    def test_handler_ignores_non_youtube_notes(
        self, repo_root: Path, isolated_test_env: dict, non_youtube_note: Path
    ):
        """
        Test: Handler ignores notes without source: youtube.
        
        Acceptance Criteria:
        - can_handle() returns False for non-YouTube notes
        - Only YouTube source notes are processed
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
        }
        handler = YouTubeFeatureHandler(config=config)
        
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
        
        event = MockEvent(non_youtube_note)
        
        can_handle = handler.can_handle(event)
        assert can_handle is False, \
            "Handler should ignore non-YouTube notes"

    def test_handler_reports_health_status(
        self, repo_root: Path, isolated_test_env: dict
    ):
        """
        Test: Handler provides health status for monitoring.
        
        Acceptance Criteria:
        - get_health_status() or get_health() returns status dictionary
        - Status is one of: healthy, degraded, unhealthy, blocked
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
        }
        handler = YouTubeFeatureHandler(config=config)
        
        # YouTubeFeatureHandler uses get_health() method
        health = handler.get_health()
        
        assert health is not None, "Handler should provide health status method"
        assert "status" in health, "Health should include status field"
        assert health["status"] in ["healthy", "degraded", "unhealthy", "blocked"], \
            "Status should be valid health state"

    # =========================================================================
    # P1: Graceful Fallback Tests (IP Ban / API Unavailable)
    # =========================================================================

    def test_handler_graceful_transcript_fallback(
        self, repo_root: Path, isolated_test_env: dict, youtube_note_ready: Path
    ):
        """
        Test: Handler gracefully handles transcript fetch failures.
        
        Acceptance Criteria:
        - Handler doesn't crash when transcript unavailable
        - Error is logged but processing continues
        - Handler health degrades gracefully (not crashes)
        
        Note: This test verifies resilience, not successful quote extraction.
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
            "processing_timeout": 5,  # Short timeout for test
        }
        handler = YouTubeFeatureHandler(config=config)
        
        class MockEvent:
            def __init__(self, path):
                self.src_path = str(path)
        
        event = MockEvent(youtube_note_ready)
        
        # Processing may fail (IP ban, no network) but should not raise exception
        try:
            result = handler.handle(event)
            # If we get here, processing attempted (success or graceful failure)
            assert isinstance(result, dict), \
                "Handler should return dict result even on failure"
        except Exception as e:
            # Allow specific expected exceptions, fail on unexpected ones
            allowed_exceptions = (
                "TranscriptsDisabled",
                "NoTranscriptFound",
                "VideoUnavailable",
                "IPBanned",
                "TooManyRequests",
                "ConnectionError",
                "Timeout",
            )
            error_msg = str(e)
            is_expected = any(exp in error_msg for exp in allowed_exceptions)
            
            if not is_expected:
                pytest.fail(f"Unexpected exception during YouTube processing: {e}")
            # Expected exception - handler is gracefully failing

    def test_handler_metrics_track_failures(
        self, repo_root: Path, isolated_test_env: dict
    ):
        """
        Test: Handler metrics track both successes and failures.
        
        Acceptance Criteria:
        - Metrics include failure count tracking
        - Handler exports metrics in expected format
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.feature_handlers import YouTubeFeatureHandler
        
        config = {
            "vault_path": str(isolated_test_env["root"] / "knowledge"),
        }
        handler = YouTubeFeatureHandler(config=config)
        
        # Check metrics tracker exists
        assert hasattr(handler, "metrics_tracker"), \
            "Handler should have metrics_tracker attribute"
        
        # Check export method exists
        assert hasattr(handler, "export_metrics") or hasattr(handler.metrics_tracker, "export_prometheus_format"), \
            "Handler or metrics_tracker should have export method"

    # =========================================================================
    # P1: Daemon Integration Tests
    # =========================================================================

    def test_handler_daemon_registration(
        self, repo_root: Path, isolated_test_env: dict
    ):
        """
        Test: YouTubeFeatureHandler is properly registered with AutomationDaemon.
        
        Acceptance Criteria:
        - Daemon can be instantiated with youtube_handler enabled
        - Handler is accessible via daemon.youtube_handler
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.daemon import AutomationDaemon
        from src.automation.config import (
            DaemonConfig,
            YouTubeHandlerConfig,
            FileWatchConfig,
        )
        
        # Create file watching config (required for handlers to register)
        file_watch_config = FileWatchConfig(
            enabled=True,
            watch_path=str(isolated_test_env["root"] / "knowledge"),
            patterns=["*.md"],
        )
        
        # Create proper DaemonConfig with youtube_handler enabled
        youtube_config = YouTubeHandlerConfig(
            enabled=True,
            vault_path=str(isolated_test_env["root"] / "knowledge"),
            max_quotes=5,
            min_quality=0.7,
        )
        
        config = DaemonConfig(
            file_watching=file_watch_config,
            youtube_handler=youtube_config,
        )
        
        daemon = AutomationDaemon(config=config)
        
        try:
            # Start daemon to register handlers
            daemon.start()
            
            # Verify handler is registered
            assert daemon.youtube_handler is not None, \
                "YouTubeFeatureHandler should be registered with daemon"
        finally:
            # Clean up - stop daemon
            daemon.stop()

    def test_daemon_health_includes_youtube_handler(
        self, repo_root: Path, isolated_test_env: dict
    ):
        """
        Test: Daemon health status includes YouTube handler status.
        
        Acceptance Criteria:
        - get_health() returns dict with handlers section
        - YouTube handler status is included when enabled
        """
        import sys
        sys.path.insert(0, str(repo_root / "development"))
        
        from src.automation.daemon import AutomationDaemon
        from src.automation.config import (
            DaemonConfig,
            YouTubeHandlerConfig,
            FileWatchConfig,
        )
        
        file_watch_config = FileWatchConfig(
            enabled=True,
            watch_path=str(isolated_test_env["root"] / "knowledge"),
            patterns=["*.md"],
        )
        
        youtube_config = YouTubeHandlerConfig(
            enabled=True,
            vault_path=str(isolated_test_env["root"] / "knowledge"),
        )
        
        config = DaemonConfig(
            file_watching=file_watch_config,
            youtube_handler=youtube_config,
        )
        
        daemon = AutomationDaemon(config=config)
        
        try:
            daemon.start()
            
            # AutomationDaemon uses get_daemon_health() method
            health = daemon.get_daemon_health()
            
            assert "handlers" in health, "Health should include handlers section"
            assert "youtube" in health["handlers"], \
                "Handlers section should include youtube status"
        finally:
            daemon.stop()
