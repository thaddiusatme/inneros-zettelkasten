"""
TDD Tests for Feature-Specific Event Handlers

Test Coverage:
- Handler initialization and validation
- Event filtering logic (file patterns, event types)
- Callback signature compliance
- Health checks and metrics reporting
- Error handling and edge cases

Following TDD methodology: RED → GREEN → REFACTOR → COMMIT → LESSONS
"""

import logging
from pathlib import Path
from unittest.mock import patch

from src.automation.feature_handlers import ScreenshotEventHandler, SmartLinkEventHandler


# ==================== ScreenshotEventHandler Tests ====================

class TestScreenshotEventHandlerInitialization:
    """Test suite for ScreenshotEventHandler initialization."""
    
    def test_handler_initializes_with_valid_path(self, tmp_path):
        """Test handler initializes successfully with valid OneDrive path."""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        assert handler.onedrive_path == tmp_path
        assert handler.logger is not None
        assert handler.logger.level == logging.INFO
    
    def test_handler_creates_log_directory(self, tmp_path, monkeypatch):
        """Test handler creates .automation/logs directory on init."""
        # Change to temp directory for testing
        monkeypatch.chdir(tmp_path)
        
        handler = ScreenshotEventHandler(str(tmp_path / "onedrive"))
        
        log_dir = Path('.automation/logs')
        assert log_dir.exists()
        assert log_dir.is_dir()
    
    def test_handler_initializes_with_nonexistent_path(self):
        """Test handler initializes even with nonexistent OneDrive path (no validation)."""
        # Current implementation doesn't validate path existence
        handler = ScreenshotEventHandler("/nonexistent/path")
        assert handler.onedrive_path == Path("/nonexistent/path")


class TestScreenshotEventHandlerFiltering:
    """Test suite for screenshot filename pattern recognition."""
    
    def test_samsung_screenshot_jpg_format_recognized(self, tmp_path):
        """Test Samsung S23 screenshot format: Screenshot_YYYYMMDD-HHmmss_*.jpg"""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022_Chrome.jpg"
        assert handler._is_screenshot(screenshot_path) is True
    
    def test_samsung_screenshot_png_format_recognized(self, tmp_path):
        """Test Samsung S23 screenshot format: Screenshot_YYYYMMDD_HHmmss.png"""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007_143022.png"
        assert handler._is_screenshot(screenshot_path) is True
    
    def test_samsung_screenshot_jpeg_extension_recognized(self, tmp_path):
        """Test .jpeg extension is recognized (case insensitive)."""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.JPEG"
        assert handler._is_screenshot(screenshot_path) is True
    
    def test_non_screenshot_files_rejected(self, tmp_path):
        """Test non-screenshot files are rejected."""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        # Regular image files
        assert handler._is_screenshot(tmp_path / "photo.jpg") is False
        assert handler._is_screenshot(tmp_path / "image_123.png") is False
        
        # Other file types
        assert handler._is_screenshot(tmp_path / "document.pdf") is False
        assert handler._is_screenshot(tmp_path / "note.md") is False
    
    def test_screenshot_prefix_required(self, tmp_path):
        """Test Screenshot_ prefix is required."""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        # Missing prefix
        assert handler._is_screenshot(tmp_path / "20251007-143022_Chrome.jpg") is False
        assert handler._is_screenshot(tmp_path / "Capture_20251007-143022.jpg") is False


class TestScreenshotEventHandlerEventProcessing:
    """Test suite for screenshot event processing logic."""
    
    def test_created_events_processed(self, tmp_path, monkeypatch):
        """Test 'created' events trigger screenshot processing."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        screenshot_path.touch()
        
        # Mock logger to capture log calls
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(screenshot_path, 'created')
            
            # Should log processing messages
            assert mock_info.call_count >= 2
            assert any('Processing screenshot' in str(call) for call in mock_info.call_args_list)
    
    def test_modified_events_ignored(self, tmp_path, monkeypatch):
        """Test 'modified' events are filtered out (only process creation)."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(screenshot_path, 'modified')
            
            # Should not log processing (early return)
            assert not any('Processing screenshot' in str(call) for call in mock_info.call_args_list)
    
    def test_deleted_events_ignored(self, tmp_path, monkeypatch):
        """Test 'deleted' events are filtered out."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(screenshot_path, 'deleted')
            
            # Should not log processing
            assert not any('Processing screenshot' in str(call) for call in mock_info.call_args_list)
    
    def test_non_screenshot_files_ignored(self, tmp_path, monkeypatch):
        """Test non-screenshot files are filtered out early."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        regular_file = tmp_path / "photo.jpg"
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(regular_file, 'created')
            
            # Should not log processing
            assert not any('Processing screenshot' in str(call) for call in mock_info.call_args_list)
    
    def test_callback_signature_matches_filewatcher(self, tmp_path, monkeypatch):
        """Test callback signature is compatible with FileWatcher: (Path, str) -> None."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        
        # Should not raise TypeError
        result = handler.process(screenshot_path, 'created')
        assert result is None  # No return value expected


class TestScreenshotEventHandlerErrorHandling:
    """Test suite for screenshot handler error handling."""
    
    def test_processing_errors_logged(self, tmp_path, monkeypatch):
        """Test processing errors are caught and logged without crashing."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        screenshot_path.touch()
        
        # Simulate processing error - patch after filtering but inside try block
        original_info = handler.logger.info
        call_count = [0]
        
        def side_effect_info(msg):
            call_count[0] += 1
            # First call is "Processing screenshot", second would be "Screenshot processed"
            if call_count[0] == 2:
                raise Exception("Processing failed")
            return original_info(msg)
        
        with patch.object(handler.logger, 'info', side_effect=side_effect_info), \
             patch.object(handler.logger, 'error') as mock_error:
            
            # Should not raise exception
            handler.process(screenshot_path, 'created')
            
            # Should log error
            assert mock_error.called
            assert 'Processing failed' in str(mock_error.call_args)


class TestScreenshotEventHandlerMetrics:
    """Test suite for screenshot handler metrics and health checks."""
    
    def test_handler_has_metrics_method(self, tmp_path):
        """Test handler provides get_metrics() method for monitoring."""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        # Should have metrics method
        assert hasattr(handler, 'get_metrics')
        
        metrics = handler.get_metrics()
        assert isinstance(metrics, dict)
        assert 'events_processed' in metrics
        assert 'events_failed' in metrics
    
    def test_metrics_track_processed_events(self, tmp_path, monkeypatch):
        """Test metrics track number of successfully processed events."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        screenshot_path.touch()
        
        # Process multiple events
        handler.process(screenshot_path, 'created')
        handler.process(screenshot_path, 'created')
        
        metrics = handler.get_metrics()
        assert metrics['events_processed'] >= 2
    
    def test_metrics_track_failed_events(self, tmp_path, monkeypatch):
        """Test metrics track number of failed processing attempts."""
        monkeypatch.chdir(tmp_path)
        handler = ScreenshotEventHandler(str(tmp_path))
        
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        screenshot_path.touch()
        
        # Simulate processing failure - raise exception in second info call
        original_info = handler.logger.info
        call_count = [0]
        
        def side_effect_info(msg):
            call_count[0] += 1
            if call_count[0] == 2:  # Second call
                raise Exception("Fail")
            return original_info(msg)
        
        with patch.object(handler.logger, 'info', side_effect=side_effect_info), \
             patch.object(handler.logger, 'error'):
            handler.process(screenshot_path, 'created')
        
        metrics = handler.get_metrics()
        assert 'events_failed' in metrics
        assert metrics['events_failed'] >= 1
    
    def test_handler_has_health_check(self, tmp_path):
        """Test handler provides get_health() method for daemon monitoring."""
        handler = ScreenshotEventHandler(str(tmp_path))
        
        assert hasattr(handler, 'get_health')
        
        health = handler.get_health()
        assert isinstance(health, dict)
        assert 'status' in health  # 'healthy', 'degraded', 'unhealthy'
        assert 'last_processed' in health


# ==================== SmartLinkEventHandler Tests ====================

class TestSmartLinkEventHandlerInitialization:
    """Test suite for SmartLinkEventHandler initialization."""
    
    def test_handler_initializes_with_valid_vault_path(self, tmp_path):
        """Test handler initializes successfully with valid vault path."""
        handler = SmartLinkEventHandler(str(tmp_path))
        
        assert handler.vault_path == tmp_path
        assert handler.logger is not None
        assert handler.logger.level == logging.INFO
    
    def test_handler_creates_log_directory(self, tmp_path, monkeypatch):
        """Test handler creates .automation/logs directory on init."""
        monkeypatch.chdir(tmp_path)
        
        handler = SmartLinkEventHandler(str(tmp_path / "vault"))
        
        log_dir = Path('.automation/logs')
        assert log_dir.exists()
        assert log_dir.is_dir()


class TestSmartLinkEventHandlerFiltering:
    """Test suite for markdown file filtering."""
    
    def test_markdown_files_accepted(self, tmp_path):
        """Test .md files are accepted for processing."""
        handler = SmartLinkEventHandler(str(tmp_path))
        
        note_path = tmp_path / "test-note.md"
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(note_path, 'created')
            
            # Should process markdown files
            assert any('Processing smart links' in str(call) for call in mock_info.call_args_list)
    
    def test_non_markdown_files_rejected(self, tmp_path):
        """Test non-.md files are rejected."""
        handler = SmartLinkEventHandler(str(tmp_path))
        
        # Various non-markdown files
        files_to_reject = [
            tmp_path / "document.txt",
            tmp_path / "image.png",
            tmp_path / "data.json",
            tmp_path / "script.py"
        ]
        
        for file_path in files_to_reject:
            with patch.object(handler.logger, 'info') as mock_info:
                handler.process(file_path, 'created')
                
                # Should not process non-markdown
                assert not any('Processing smart links' in str(call) for call in mock_info.call_args_list)


class TestSmartLinkEventHandlerEventProcessing:
    """Test suite for smart link event processing logic."""
    
    def test_created_events_processed(self, tmp_path, monkeypatch):
        """Test 'created' events trigger smart link analysis."""
        monkeypatch.chdir(tmp_path)
        handler = SmartLinkEventHandler(str(tmp_path))
        
        note_path = tmp_path / "new-note.md"
        note_path.touch()
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(note_path, 'created')
            
            # Should log processing
            assert any('Processing smart links' in str(call) for call in mock_info.call_args_list)
    
    def test_modified_events_processed(self, tmp_path, monkeypatch):
        """Test 'modified' events trigger smart link analysis (note changes)."""
        monkeypatch.chdir(tmp_path)
        handler = SmartLinkEventHandler(str(tmp_path))
        
        note_path = tmp_path / "existing-note.md"
        note_path.write_text("# Updated content")
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(note_path, 'modified')
            
            # Should process modifications
            assert any('Processing smart links' in str(call) for call in mock_info.call_args_list)
    
    def test_deleted_events_ignored(self, tmp_path, monkeypatch):
        """Test 'deleted' events are filtered out (no links to suggest)."""
        monkeypatch.chdir(tmp_path)
        handler = SmartLinkEventHandler(str(tmp_path))
        
        note_path = tmp_path / "deleted-note.md"
        
        with patch.object(handler.logger, 'info') as mock_info:
            handler.process(note_path, 'deleted')
            
            # Should not process deletions
            assert not any('Processing smart links' in str(call) for call in mock_info.call_args_list)
    
    def test_callback_signature_matches_filewatcher(self, tmp_path, monkeypatch):
        """Test callback signature is compatible with FileWatcher: (Path, str) -> None."""
        monkeypatch.chdir(tmp_path)
        handler = SmartLinkEventHandler(str(tmp_path))
        
        note_path = tmp_path / "test-note.md"
        
        # Should not raise TypeError
        result = handler.process(note_path, 'created')
        assert result is None  # No return value expected


class TestSmartLinkEventHandlerMetrics:
    """Test suite for smart link handler metrics and health checks."""
    
    def test_handler_has_metrics_method(self, tmp_path):
        """Test handler provides get_metrics() method for monitoring."""
        handler = SmartLinkEventHandler(str(tmp_path))
        
        assert hasattr(handler, 'get_metrics')
        
        metrics = handler.get_metrics()
        assert isinstance(metrics, dict)
        assert 'events_processed' in metrics
        assert 'links_suggested' in metrics
        assert 'links_inserted' in metrics
    
    def test_metrics_track_link_operations(self, tmp_path, monkeypatch):
        """Test metrics track link suggestions and insertions."""
        monkeypatch.chdir(tmp_path)
        handler = SmartLinkEventHandler(str(tmp_path))
        
        note_path = tmp_path / "test-note.md"
        note_path.touch()
        
        # Process event
        handler.process(note_path, 'created')
        
        metrics = handler.get_metrics()
        assert 'events_processed' in metrics
        assert 'links_suggested' in metrics
        assert 'links_inserted' in metrics
    
    def test_handler_has_health_check(self, tmp_path):
        """Test handler provides get_health() method for daemon monitoring."""
        handler = SmartLinkEventHandler(str(tmp_path))
        
        assert hasattr(handler, 'get_health')
        
        health = handler.get_health()
        assert isinstance(health, dict)
        assert 'status' in health
        assert 'last_processed' in health


# ==================== Integration Tests ====================

class TestFeatureHandlerIntegration:
    """Test suite for handler integration scenarios."""
    
    def test_both_handlers_can_coexist(self, tmp_path):
        """Test both handlers can be instantiated and used together."""
        screenshot_handler = ScreenshotEventHandler(str(tmp_path / "onedrive"))
        link_handler = SmartLinkEventHandler(str(tmp_path / "vault"))
        
        assert screenshot_handler is not None
        assert link_handler is not None
        
        # Each should have independent loggers
        assert screenshot_handler.logger != link_handler.logger
    
    def test_handlers_maintain_independent_metrics(self, tmp_path, monkeypatch):
        """Test handlers maintain separate metrics counters."""
        monkeypatch.chdir(tmp_path)
        
        screenshot_handler = ScreenshotEventHandler(str(tmp_path))
        link_handler = SmartLinkEventHandler(str(tmp_path))
        
        # Process events on each handler
        screenshot_path = tmp_path / "Screenshot_20251007-143022.jpg"
        screenshot_path.touch()
        screenshot_handler.process(screenshot_path, 'created')
        
        note_path = tmp_path / "note.md"
        note_path.touch()
        link_handler.process(note_path, 'created')
        
        # Metrics should be independent
        screenshot_metrics = screenshot_handler.get_metrics()
        link_metrics = link_handler.get_metrics()
        
        assert screenshot_metrics != link_metrics
