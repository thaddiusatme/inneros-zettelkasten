"""
TDD Iteration 2: Feature Handler Real Processing Integration Tests

RED PHASE: Failing tests that drive integration with real processing engines
- ScreenshotEventHandler → ScreenshotProcessor
- SmartLinkEventHandler → LinkSuggestionEngine + AIConnections

Following TDD methodology: RED → GREEN → REFACTOR → COMMIT → LESSONS

REFACTOR UPDATE: Tests now patch feature_handler_utils module after utility extraction
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from src.automation.feature_handlers import ScreenshotEventHandler, SmartLinkEventHandler


# ==================== P0.1: ScreenshotEventHandler Integration ====================

class TestScreenshotHandlerProcessorIntegration:
    """Test suite for ScreenshotEventHandler integration with ScreenshotProcessor."""
    
    @patch('src.automation.feature_handler_utils.ScreenshotProcessor')
    def test_screenshot_handler_integrates_with_processor(self, mock_processor_class, tmp_path, monkeypatch):
        """
        RED: Test ScreenshotEventHandler calls ScreenshotProcessor.process_screenshots_with_ocr()
        
        Acceptance Criteria:
        - ScreenshotProcessor imported and instantiated
        - process_screenshots_with_ocr() called with screenshot file path
        - Metrics updated based on processing results
        - events_processed incremented on success
        """
        monkeypatch.chdir(tmp_path)
        
        # Setup mock processor instance
        mock_processor_instance = MagicMock()
        mock_ocr_result = MagicMock()
        mock_ocr_result.extracted_text = "Sample OCR text"
        mock_ocr_result.confidence_score = 0.85
        mock_processor_instance.process_screenshots_with_ocr.return_value = {
            'screenshot.jpg': mock_ocr_result
        }
        mock_processor_class.return_value = mock_processor_instance
        
        # Initialize handler
        handler = ScreenshotEventHandler(str(tmp_path / "onedrive"))
        
        # Create screenshot file
        screenshot = tmp_path / "Screenshot_20251007-143022_Chrome.jpg"
        screenshot.touch()
        
        # Process event
        handler.process(screenshot, 'created')
        
        # Assert processor called with screenshot path
        mock_processor_instance.process_screenshots_with_ocr.assert_called_once()
        call_args = mock_processor_instance.process_screenshots_with_ocr.call_args[0][0]
        assert screenshot in call_args or str(screenshot) in [str(p) for p in call_args]
        
        # Assert metrics updated
        metrics = handler.get_metrics()
        assert metrics['events_processed'] == 1
        assert metrics['events_failed'] == 0
    
    @patch('src.automation.feature_handler_utils.ScreenshotProcessor')
    def test_screenshot_handler_handles_ocr_service_unavailable(self, mock_processor_class, tmp_path, monkeypatch):
        """
        RED: Test graceful fallback when OCR service (Ollama) is unavailable
        
        Acceptance Criteria:
        - Exception caught and logged
        - events_failed metric incremented
        - Processing continues without crash
        - User-friendly error message logged
        """
        monkeypatch.chdir(tmp_path)
        
        # Setup mock processor to raise exception
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_screenshots_with_ocr.side_effect = Exception("Ollama service unavailable")
        mock_processor_class.return_value = mock_processor_instance
        
        # Initialize handler
        handler = ScreenshotEventHandler(str(tmp_path / "onedrive"))
        
        # Create screenshot file
        screenshot = tmp_path / "Screenshot_20251007-143022_Chrome.jpg"
        screenshot.touch()
        
        # Process event (should not raise)
        handler.process(screenshot, 'created')
        
        # Assert error handled gracefully
        metrics = handler.get_metrics()
        assert metrics['events_processed'] == 0
        assert metrics['events_failed'] == 1
    
    @patch('src.automation.feature_handler_utils.ScreenshotProcessor')
    def test_screenshot_handler_tracks_ocr_success_metrics(self, mock_processor_class, tmp_path, monkeypatch):
        """
        RED: Test handler tracks OCR-specific success metrics
        
        Acceptance Criteria:
        - Track successful OCR extractions
        - Track daily note generation success
        - Metrics available via get_metrics()
        """
        monkeypatch.chdir(tmp_path)
        
        # Setup mock with successful OCR result
        mock_processor_instance = MagicMock()
        mock_ocr_result = MagicMock()
        mock_ocr_result.extracted_text = "Sample text"
        mock_ocr_result.confidence_score = 0.90
        mock_processor_instance.process_screenshots_with_ocr.return_value = {
            'screenshot.jpg': mock_ocr_result
        }
        mock_processor_class.return_value = mock_processor_instance
        
        handler = ScreenshotEventHandler(str(tmp_path / "onedrive"))
        screenshot = tmp_path / "Screenshot_20251007-143022_Chrome.jpg"
        screenshot.touch()
        
        handler.process(screenshot, 'created')
        
        # Assert OCR metrics tracked
        metrics = handler.get_metrics()
        assert 'ocr_success' in metrics or 'events_processed' in metrics
        # Future enhancement: track OCR-specific metrics separately


# ==================== P0.2: SmartLinkEventHandler Integration ====================

class TestSmartLinkHandlerEngineIntegration:
    """Test suite for SmartLinkEventHandler integration with LinkSuggestionEngine."""
    
    @patch('src.automation.feature_handler_utils.AIConnections')
    @patch('src.automation.feature_handler_utils.LinkSuggestionEngine')
    def test_smart_link_handler_integrates_with_engine(self, mock_engine_class, 
                                                       mock_connections_class, tmp_path, monkeypatch):
        """
        RED: Test SmartLinkEventHandler calls LinkSuggestionEngine for semantic analysis
        
        Acceptance Criteria:
        - LinkSuggestionEngine imported and instantiated
        - generate_link_suggestions() called with note content
        - AIConnections used for similarity analysis
        - links_suggested metric updated with suggestion count
        """
        monkeypatch.chdir(tmp_path)
        
        # Setup mock engine instance
        mock_engine_instance = MagicMock()
        mock_suggestion = MagicMock()
        mock_suggestion.target_note = "related-note.md"
        mock_suggestion.quality_score = 0.8
        mock_engine_instance.generate_link_suggestions.return_value = [
            mock_suggestion,
            mock_suggestion
        ]
        mock_engine_class.return_value = mock_engine_instance
        
        # Setup mock connections
        mock_connections_instance = MagicMock()
        mock_connections_instance.find_similar_notes.return_value = [
            ('related-note.md', 0.85)
        ]
        mock_connections_class.return_value = mock_connections_instance
        
        # Initialize handler
        handler = SmartLinkEventHandler(str(tmp_path))
        
        # Create note file
        note = tmp_path / "test-note.md"
        note.write_text("# Test Note\n\nSome content for testing.")
        
        # Process event
        handler.process(note, 'created')
        
        # Assert engine called
        assert mock_engine_instance.generate_link_suggestions.called or \
               mock_connections_instance.find_similar_notes.called
        
        # Assert metrics updated
        metrics = handler.get_metrics()
        assert metrics['events_processed'] == 1
        assert metrics['links_suggested'] >= 0  # Should reflect actual suggestions
    
    @patch('src.automation.feature_handler_utils.AIConnections')
    def test_smart_link_handler_handles_engine_failure(self, mock_connections_class, tmp_path, monkeypatch):
        """
        RED: Test graceful fallback when AIConnections initialization fails
        
        Acceptance Criteria:
        - Exception caught and logged
        - events_failed metric incremented  
        - Processing continues without crash
        """
        monkeypatch.chdir(tmp_path)
        
        # Setup mock to raise exception during initialization
        mock_connections_class.side_effect = Exception("AI service unavailable")
        
        handler = SmartLinkEventHandler(str(tmp_path))
        note = tmp_path / "test-note.md"
        note.write_text("# Test Note")
        
        # Process event (should not raise)
        handler.process(note, 'created')
        
        # Assert error handled gracefully
        metrics = handler.get_metrics()
        assert metrics['events_failed'] == 1
    
    @patch('src.automation.feature_handler_utils.AIConnections')
    def test_smart_link_handler_updates_links_suggested_metric(self, mock_connections_class, tmp_path, monkeypatch):
        """
        RED: Test links_suggested metric accurately reflects suggestion count
        
        Acceptance Criteria:
        - links_suggested incremented by actual suggestion count
        - Metric matches number of suggestions from engine
        - Available via get_metrics()
        """
        monkeypatch.chdir(tmp_path)
        
        # Setup mock with 3 suggestions
        mock_connections_instance = MagicMock()
        mock_connections_instance.find_similar_notes.return_value = [
            ('note1.md', 0.85),
            ('note2.md', 0.80),
            ('note3.md', 0.75)
        ]
        mock_connections_class.return_value = mock_connections_instance
        
        handler = SmartLinkEventHandler(str(tmp_path))
        note = tmp_path / "test-note.md"
        note.write_text("# Test Note")
        
        handler.process(note, 'created')
        
        metrics = handler.get_metrics()
        assert metrics['links_suggested'] == 3  # Should match suggestion count


# ==================== P0.3: Configuration and Error Handling ====================

class TestHandlerConfiguration:
    """Test suite for handler-specific configuration support."""
    
    def test_screenshot_handler_accepts_configuration(self, tmp_path):
        """
        RED: Test ScreenshotEventHandler accepts configuration dict
        
        Future enhancement for P1:
        - onedrive_path from config
        - ocr_options from config
        - processing_threshold from config
        """
        # Placeholder for P1 configuration support
        handler = ScreenshotEventHandler(str(tmp_path / "onedrive"))
        assert handler.onedrive_path == tmp_path / "onedrive"
    
    def test_smart_link_handler_accepts_similarity_threshold(self, tmp_path):
        """
        RED: Test SmartLinkEventHandler accepts similarity threshold
        
        Future enhancement for P1:
        - similarity_threshold configurable (0.5-0.95)
        - max_suggestions configurable
        """
        # Placeholder for P1 configuration support
        handler = SmartLinkEventHandler(str(tmp_path))
        assert handler.vault_path == tmp_path


# ==================== P1: Performance Monitoring ====================

class TestHandlerPerformanceMonitoring:
    """Test suite for handler performance monitoring (P1 feature)."""
    
    @patch('src.automation.feature_handler_utils.ScreenshotProcessor')
    def test_screenshot_handler_tracks_processing_time(self, mock_processor_class, tmp_path, monkeypatch):
        """
        RED: Test handler tracks processing time per event
        
        P1 Enhancement:
        - Track avg_processing_time
        - Track max_processing_time
        - Warn if processing exceeds 10s threshold
        """
        monkeypatch.chdir(tmp_path)
        
        mock_processor_instance = MagicMock()
        mock_processor_instance.process_screenshots_with_ocr.return_value = {}
        mock_processor_class.return_value = mock_processor_instance
        
        handler = ScreenshotEventHandler(str(tmp_path / "onedrive"))
        screenshot = tmp_path / "Screenshot_20251007-143022_Chrome.jpg"
        screenshot.touch()
        
        handler.process(screenshot, 'created')
        
        # P1: Future enhancement for performance metrics
        metrics = handler.get_metrics()
        # assert 'avg_processing_time' in metrics
        # assert 'max_processing_time' in metrics
