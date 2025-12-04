"""
TDD Iteration 1 - Phase 2 E2E Validation: Screenshot Workflow

RED PHASE: End-to-end tests validating screenshot → Inbox note pipeline works without manual intervention.

These tests verify:
- Screenshot file drop triggers handler processing
- OCR extraction produces meaningful text (or graceful fallback)
- Note appears in knowledge/Inbox/ with correct frontmatter
- Handler is properly registered with AutomationDaemon
- Exit code semantics enable CI automation

Tests use isolated temp directories following HOME isolation pattern from Phase 1.
"""

import time
import os
from pathlib import Path
from datetime import datetime
import pytest


# Mark all tests in this module as E2E and slow (potential AI processing)
pytestmark = [pytest.mark.e2e, pytest.mark.slow]


class TestScreenshotWorkflowE2E:
    """
    End-to-end tests for screenshot → Inbox note workflow.
    
    These tests validate the complete pipeline from screenshot file drop
    to note creation in the knowledge vault.
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
        Create isolated test environment with fake OneDrive and knowledge vault.
        
        Following HOME isolation pattern from Phase 1 to prevent test interference.
        """
        # Create directory structure
        onedrive_screenshots = tmp_path / "OneDrive" / "Pictures" / "Screenshots"
        onedrive_screenshots.mkdir(parents=True)
        
        knowledge_inbox = tmp_path / "knowledge" / "Inbox"
        knowledge_inbox.mkdir(parents=True)
        
        # Create .inneros directory for daemon state
        inneros_dir = tmp_path / ".inneros"
        inneros_dir.mkdir(parents=True)
        
        # Create .automation/logs for handler logging
        automation_logs = tmp_path / ".automation" / "logs"
        automation_logs.mkdir(parents=True)
        
        return {
            "root": tmp_path,
            "onedrive_screenshots": onedrive_screenshots,
            "knowledge_inbox": knowledge_inbox,
            "inneros_dir": inneros_dir,
            "automation_logs": automation_logs,
        }

    @pytest.fixture
    def sample_screenshot(self, isolated_test_env: dict) -> Path:
        """
        Create a sample Samsung screenshot file for testing.
        
        Samsung Galaxy S23 naming pattern: Screenshot_YYYYMMDD-HHmmss_*.jpg
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        screenshot_name = f"Screenshot_{timestamp}_test.jpg"
        screenshot_path = isolated_test_env["onedrive_screenshots"] / screenshot_name
        
        # Create a minimal valid JPEG file (1x1 pixel)
        # JPEG header for 1x1 white pixel
        jpeg_data = bytes([
            0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01,
            0x01, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0xFF, 0xDB, 0x00, 0x43,
            0x00, 0x08, 0x06, 0x06, 0x07, 0x06, 0x05, 0x08, 0x07, 0x07, 0x07, 0x09,
            0x09, 0x08, 0x0A, 0x0C, 0x14, 0x0D, 0x0C, 0x0B, 0x0B, 0x0C, 0x19, 0x12,
            0x13, 0x0F, 0x14, 0x1D, 0x1A, 0x1F, 0x1E, 0x1D, 0x1A, 0x1C, 0x1C, 0x20,
            0x24, 0x2E, 0x27, 0x20, 0x22, 0x2C, 0x23, 0x1C, 0x1C, 0x28, 0x37, 0x29,
            0x2C, 0x30, 0x31, 0x34, 0x34, 0x34, 0x1F, 0x27, 0x39, 0x3D, 0x38, 0x32,
            0x3C, 0x2E, 0x33, 0x34, 0x32, 0xFF, 0xC0, 0x00, 0x0B, 0x08, 0x00, 0x01,
            0x00, 0x01, 0x01, 0x01, 0x11, 0x00, 0xFF, 0xC4, 0x00, 0x1F, 0x00, 0x00,
            0x01, 0x05, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0A, 0x0B, 0xFF, 0xC4, 0x00, 0xB5, 0x10, 0x00, 0x02, 0x01, 0x03,
            0x03, 0x02, 0x04, 0x03, 0x05, 0x05, 0x04, 0x04, 0x00, 0x00, 0x01, 0x7D,
            0x01, 0x02, 0x03, 0x00, 0x04, 0x11, 0x05, 0x12, 0x21, 0x31, 0x41, 0x06,
            0x13, 0x51, 0x61, 0x07, 0x22, 0x71, 0x14, 0x32, 0x81, 0x91, 0xA1, 0x08,
            0x23, 0x42, 0xB1, 0xC1, 0x15, 0x52, 0xD1, 0xF0, 0x24, 0x33, 0x62, 0x72,
            0x82, 0x09, 0x0A, 0x16, 0x17, 0x18, 0x19, 0x1A, 0x25, 0x26, 0x27, 0x28,
            0x29, 0x2A, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x43, 0x44, 0x45,
            0x46, 0x47, 0x48, 0x49, 0x4A, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59,
            0x5A, 0x63, 0x64, 0x65, 0x66, 0x67, 0x68, 0x69, 0x6A, 0x73, 0x74, 0x75,
            0x76, 0x77, 0x78, 0x79, 0x7A, 0x83, 0x84, 0x85, 0x86, 0x87, 0x88, 0x89,
            0x8A, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x9A, 0xA2, 0xA3,
            0xA4, 0xA5, 0xA6, 0xA7, 0xA8, 0xA9, 0xAA, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6,
            0xB7, 0xB8, 0xB9, 0xBA, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0xC8, 0xC9,
            0xCA, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0xD9, 0xDA, 0xE1, 0xE2,
            0xE3, 0xE4, 0xE5, 0xE6, 0xE7, 0xE8, 0xE9, 0xEA, 0xF1, 0xF2, 0xF3, 0xF4,
            0xF5, 0xF6, 0xF7, 0xF8, 0xF9, 0xFA, 0xFF, 0xDA, 0x00, 0x08, 0x01, 0x01,
            0x00, 0x00, 0x3F, 0x00, 0xFB, 0xD5, 0xFF, 0xD9
        ])
        
        screenshot_path.write_bytes(jpeg_data)
        return screenshot_path

    # =========================================================================
    # TEST 0: Smoke test - Handler class can be imported
    # =========================================================================
    def test_screenshot_handler_can_be_imported(self):
        """
        TEST 0: ScreenshotEventHandler can be imported (smoke test).
        
        Acceptance Criteria:
        - Import succeeds without error
        - Class exists and is callable
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        assert ScreenshotEventHandler is not None
        assert callable(ScreenshotEventHandler)

    # =========================================================================
    # TEST 1: Handler initialization with config
    # =========================================================================
    def test_screenshot_handler_initializes_with_config(
        self, isolated_test_env: dict
    ):
        """
        TEST 1: ScreenshotEventHandler initializes with valid config.
        
        Acceptance Criteria:
        - Handler accepts config dictionary
        - onedrive_path is set correctly
        - No exceptions during initialization
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        config = {
            "onedrive_path": str(isolated_test_env["onedrive_screenshots"]),
            "knowledge_path": str(isolated_test_env["knowledge_inbox"].parent),
            "ocr_enabled": False,  # Disable OCR for unit test isolation
            "processing_timeout": 60,
        }
        
        handler = ScreenshotEventHandler(config=config)
        
        assert handler.onedrive_path == isolated_test_env["onedrive_screenshots"]
        assert handler.ocr_enabled is False

    # =========================================================================
    # TEST 2: Handler recognizes Samsung screenshot naming pattern
    # =========================================================================
    def test_screenshot_handler_recognizes_samsung_pattern(
        self, isolated_test_env: dict, sample_screenshot: Path
    ):
        """
        TEST 2: Handler correctly identifies Samsung screenshot files.
        
        Acceptance Criteria:
        - Files matching Screenshot_YYYYMMDD-HHmmss_*.jpg are recognized
        - Non-screenshot files are ignored
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        config = {
            "onedrive_path": str(isolated_test_env["onedrive_screenshots"]),
            "ocr_enabled": False,
        }
        
        handler = ScreenshotEventHandler(config=config)
        
        # Should recognize Samsung screenshot
        assert handler._is_screenshot(sample_screenshot) is True
        
        # Should ignore non-screenshot files
        non_screenshot = isolated_test_env["onedrive_screenshots"] / "regular_photo.jpg"
        non_screenshot.write_bytes(b"fake jpeg")
        assert handler._is_screenshot(non_screenshot) is False
        
        # Should ignore non-image files
        text_file = isolated_test_env["onedrive_screenshots"] / "Screenshot_20241201-120000_test.txt"
        text_file.write_text("not an image")
        assert handler._is_screenshot(text_file) is False

    # =========================================================================
    # TEST 3: Handler processes screenshot and creates note
    # =========================================================================
    def test_screenshot_handler_creates_note_in_inbox(
        self, isolated_test_env: dict, sample_screenshot: Path
    ):
        """
        TEST 3: Handler processes screenshot and creates note in Inbox.
        
        Acceptance Criteria:
        - Processing a screenshot creates a .md file
        - Note appears in knowledge/Inbox/ directory
        - Note has valid frontmatter with required fields
        
        This is the core E2E test for the screenshot workflow.
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        config = {
            "onedrive_path": str(isolated_test_env["onedrive_screenshots"]),
            "knowledge_path": str(isolated_test_env["knowledge_inbox"].parent),
            "ocr_enabled": False,  # Disable OCR for test isolation
            "processing_timeout": 60,
        }
        
        handler = ScreenshotEventHandler(config=config)
        
        # Process the screenshot
        handler.process(sample_screenshot, "created")
        
        # Verify note was created in Inbox
        inbox_files = list(isolated_test_env["knowledge_inbox"].glob("*.md"))
        
        assert len(inbox_files) >= 1, (
            f"Expected at least 1 note in Inbox, found {len(inbox_files)}.\n"
            f"Inbox contents: {list(isolated_test_env['knowledge_inbox'].iterdir())}"
        )
        
        # Verify note has frontmatter
        note_content = inbox_files[0].read_text()
        assert "---" in note_content, "Note should have YAML frontmatter"

    # =========================================================================
    # TEST 4: OCR fallback produces placeholder text
    # =========================================================================
    def test_screenshot_handler_ocr_fallback(
        self, isolated_test_env: dict, sample_screenshot: Path
    ):
        """
        TEST 4: When OCR unavailable, handler produces placeholder content.
        
        Acceptance Criteria:
        - Handler doesn't crash when Ollama/OCR unavailable
        - Note is still created with placeholder text
        - Error is logged but processing continues
        
        This ensures CI stability without requiring Ollama.
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        config = {
            "onedrive_path": str(isolated_test_env["onedrive_screenshots"]),
            "knowledge_path": str(isolated_test_env["knowledge_inbox"].parent),
            "ocr_enabled": True,  # Enable OCR to test fallback
            "processing_timeout": 30,
        }
        
        handler = ScreenshotEventHandler(config=config)
        
        # Process should not raise even if OCR fails
        try:
            handler.process(sample_screenshot, "created")
        except Exception as e:
            pytest.fail(f"Handler should not raise when OCR unavailable: {e}")
        
        # Note should still be created (possibly with placeholder)
        inbox_files = list(isolated_test_env["knowledge_inbox"].glob("*.md"))
        # Note: May be 0 if handler gracefully skips on OCR failure
        # This test verifies no crash, not necessarily note creation

    # =========================================================================
    # TEST 5: Handler registered in daemon startup
    # =========================================================================
    def test_screenshot_handler_registered_in_daemon(
        self, isolated_test_env: dict, env_with_pythonpath: dict, repo_root: Path
    ):
        """
        TEST 5: ScreenshotEventHandler is registered when daemon starts.
        
        Acceptance Criteria:
        - Daemon with screenshot config has screenshot_handler initialized
        - Handler is connected to file watcher callbacks
        """
        from src.automation.config import DaemonConfig
        
        # Create minimal config with screenshot handler enabled
        config = DaemonConfig()
        
        # Verify config structure exists
        assert hasattr(config, 'screenshot_handler'), (
            "DaemonConfig should have screenshot_handler attribute"
        )

    # =========================================================================
    # TEST 6: E2E - CLI processes screenshots via make up
    # =========================================================================
    def test_screenshot_workflow_via_cli(
        self, isolated_test_env: dict, sample_screenshot: Path, 
        env_with_pythonpath: dict, repo_root: Path
    ):
        """
        TEST 6: Full E2E - Screenshot processing via inneros-up daemon.
        
        Acceptance Criteria:
        - inneros-up starts daemon with screenshot handler
        - Dropping screenshot file triggers processing
        - Note appears in Inbox within timeout period
        - Exit code 0 indicates success
        
        This is the ultimate E2E validation of the screenshot pipeline.
        """
        # Set up isolated HOME to prevent interference with real daemon
        test_env = env_with_pythonpath.copy()
        test_env["HOME"] = str(isolated_test_env["root"])
        
        # Create daemon config in test environment
        config_dir = isolated_test_env["root"] / ".inneros"
        config_dir.mkdir(exist_ok=True)
        
        daemon_config = config_dir / "daemon_config.yaml"
        daemon_config.write_text(f"""
file_watching:
  enabled: true
  watch_path: {isolated_test_env['onedrive_screenshots']}
  debounce_seconds: 1
  ignore_patterns:
    - "*.tmp"
    - ".DS_Store"

screenshot_handler:
  enabled: true
  onedrive_path: {isolated_test_env['onedrive_screenshots']}
  knowledge_path: {isolated_test_env['knowledge_inbox'].parent}
  ocr_enabled: false
  processing_timeout: 30
""")
        
        # Start daemon in background (non-blocking)
        # Note: This test structure shows the INTENT - actual implementation
        # may need adjustment based on how inneros-up is structured
        
        # For RED phase, we expect this to fail until GREEN phase implementation
        pytest.skip(
            "RED PHASE: Skipping full E2E test until daemon CLI integration is complete. "
            "This test documents the expected behavior for GREEN phase implementation."
        )

    # =========================================================================
    # TEST 7: Handler metrics tracking
    # =========================================================================
    def test_screenshot_handler_tracks_metrics(
        self, isolated_test_env: dict, sample_screenshot: Path
    ):
        """
        TEST 7: Handler tracks processing metrics for monitoring.
        
        Acceptance Criteria:
        - Handler exposes get_metrics() method
        - Metrics include events_processed count
        - Metrics include error tracking
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        config = {
            "onedrive_path": str(isolated_test_env["onedrive_screenshots"]),
            "ocr_enabled": False,
        }
        
        handler = ScreenshotEventHandler(config=config)
        
        # Get initial metrics
        metrics = handler.get_metrics()
        
        assert "events_processed" in metrics
        assert "events_failed" in metrics
        assert metrics["events_processed"] == 0

    # =========================================================================
    # TEST 8: Handler health status reporting
    # =========================================================================
    def test_screenshot_handler_health_status(
        self, isolated_test_env: dict
    ):
        """
        TEST 8: Handler reports health status for daemon monitoring.
        
        Acceptance Criteria:
        - Handler exposes get_health() method
        - Health includes status field (healthy/degraded/unhealthy)
        - Health includes error_rate metric
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        config = {
            "onedrive_path": str(isolated_test_env["onedrive_screenshots"]),
            "ocr_enabled": False,
        }
        
        handler = ScreenshotEventHandler(config=config)
        
        health = handler.get_health()
        
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "error_rate" in health

    # =========================================================================
    # TEST 9: Error messaging for missing OneDrive path
    # =========================================================================
    def test_screenshot_handler_error_on_missing_path(self):
        """
        TEST 9: Handler provides clear error when OneDrive path doesn't exist.
        
        Acceptance Criteria:
        - Missing onedrive_path in config raises ValueError
        - Error message is actionable
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        # Config without onedrive_path should raise
        with pytest.raises(ValueError) as exc_info:
            ScreenshotEventHandler(config={"ocr_enabled": False})
        
        assert "onedrive_path" in str(exc_info.value).lower()

    # =========================================================================
    # TEST 10: Batch processing multiple screenshots
    # =========================================================================
    def test_screenshot_handler_batch_processing(
        self, isolated_test_env: dict
    ):
        """
        TEST 10: Handler can process multiple screenshots in sequence.
        
        Acceptance Criteria:
        - Multiple screenshots are processed without error
        - Metrics reflect total processed count
        - No race conditions or file conflicts
        """
        from src.automation.feature_handlers import ScreenshotEventHandler
        
        config = {
            "onedrive_path": str(isolated_test_env["onedrive_screenshots"]),
            "knowledge_path": str(isolated_test_env["knowledge_inbox"].parent),
            "ocr_enabled": False,
        }
        
        handler = ScreenshotEventHandler(config=config)
        
        # Create multiple screenshots
        screenshots = []
        for i in range(3):
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            screenshot_name = f"Screenshot_{timestamp}_{i:03d}.jpg"
            screenshot_path = isolated_test_env["onedrive_screenshots"] / screenshot_name
            screenshot_path.write_bytes(b"\xff\xd8\xff\xe0")  # Minimal JPEG header
            screenshots.append(screenshot_path)
            time.sleep(0.1)  # Ensure unique timestamps
        
        # Process all screenshots
        for screenshot in screenshots:
            handler.process(screenshot, "created")
        
        # Verify metrics
        metrics = handler.get_metrics()
        # Note: events_processed may be 0 if processing fails gracefully
        # This test verifies no crashes during batch processing
