"""
RED Phase Tests for CoreWorkflowManager Refactoring

These tests define the expected behavior of CoreWorkflowManager after refactoring.
All tests should FAIL initially (ImportError) - this is the RED phase.

Tests focus on:
- Exception-based error handling
- Manager orchestration and coordination
- Result validation with sensible defaults
- AI cost gating (quality_score threshold)
- Bug report creation on total failures
- Dry run mode preventing file writes
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call
from datetime import datetime

# These imports will FAIL - classes don't exist yet (RED phase)
from src.ai.core_workflow_manager import CoreWorkflowManager
from src.ai.analytics_manager import AnalyticsManager
from src.ai.ai_enhancement_manager import AIEnhancementManager
from src.ai.connection_manager import ConnectionManager


@pytest.fixture
def mock_base_dir(tmp_path):
    """Create temporary vault structure for testing."""
    vault = tmp_path / "test_vault"
    vault.mkdir()
    (vault / "Inbox").mkdir()
    (vault / "Fleeting Notes").mkdir()
    (vault / "Permanent Notes").mkdir()
    (vault / ".automation" / "review_queue").mkdir(parents=True)
    return vault


@pytest.fixture
def sample_config():
    """Standard config for testing."""
    return {
        'quality_thresholds': {
            'excellent': 0.8,
            'good': 0.6,
            'needs_improvement': 0.4
        },
        'ai_enhancement': {
            'cost_gate_threshold': 0.3,
            'max_tags': 8
        }
    }


@pytest.fixture
def mock_analytics_manager():
    """Mock AnalyticsManager with spec."""
    return Mock(spec=AnalyticsManager)


@pytest.fixture
def mock_ai_enhancement_manager():
    """Mock AIEnhancementManager with spec."""
    return Mock(spec=AIEnhancementManager)


@pytest.fixture
def mock_connection_manager():
    """Mock ConnectionManager with spec."""
    return Mock(spec=ConnectionManager)


class TestCoreWorkflowManagerOrchestration:
    """Test Core's ability to orchestrate all 3 managers."""
    
    def test_core_orchestrates_all_managers_with_exception_handling(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test Core calls all 3 managers and merges results correctly."""
        # Arrange
        mock_analytics_manager.assess_quality.return_value = {
            'success': True,
            'quality_score': 0.8,
            'word_count': 500,
            'tag_count': 3,
            'link_count': 2
        }
        
        mock_ai_enhancement_manager.enhance_note.return_value = {
            'success': True,
            'tags': ['test', 'refactoring'],
            'summary': 'Test note about refactoring',
            'source': 'local_ollama',
            'fallback': False
        }
        
        mock_connection_manager.discover_links.return_value = [
            {'target': 'related-note.md', 'score': 0.9, 'reason': 'semantic similarity'},
            {'target': 'another-note.md', 'score': 0.7, 'reason': 'shared tags'}
        ]
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('test.md', dry_run=True)
        
        # Assert - Verify all managers called
        mock_analytics_manager.assess_quality.assert_called_once_with('test.md', dry_run=True)
        mock_ai_enhancement_manager.enhance_note.assert_called_once_with('test.md', fast=False, dry_run=True)
        mock_connection_manager.discover_links.assert_called_once_with('test.md', dry_run=True)
        
        # Assert - Verify result structure
        assert result['success'] == True
        assert 'analytics' in result
        assert result['analytics']['quality_score'] == 0.8
        assert 'ai_enhancement' in result
        assert result['ai_enhancement']['tags'] == ['test', 'refactoring']
        assert 'connections' in result
        assert len(result['connections']) == 2
        assert 'errors' in result
        assert len(result['errors']) == 0


class TestCoreExceptionHandling:
    """Test Core's exception-based error handling strategy."""
    
    def test_core_stops_on_analytics_validation_error(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test Core stops processing when Analytics raises ValueError."""
        # Arrange
        mock_analytics_manager.assess_quality.side_effect = ValueError("note_path cannot be empty")
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('', dry_run=True)
        
        # Assert - Early return on validation error
        assert result['success'] == False
        assert len(result['errors']) == 1
        assert result['errors'][0]['stage'] == 'analytics'
        assert result['errors'][0]['type'] == 'validation'
        assert 'note_path cannot be empty' in result['errors'][0]['error']
        
        # Assert - AI and Connections NOT called (early return)
        mock_ai_enhancement_manager.enhance_note.assert_not_called()
        mock_connection_manager.discover_links.assert_not_called()
    
    def test_core_stops_on_analytics_file_not_found_error(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test Core stops processing when Analytics raises FileNotFoundError."""
        # Arrange
        mock_analytics_manager.assess_quality.side_effect = FileNotFoundError("Note file not found")
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('nonexistent.md', dry_run=True)
        
        # Assert - Early return on file not found
        assert result['success'] == False
        assert len(result['errors']) == 1
        assert result['errors'][0]['stage'] == 'analytics'
        assert result['errors'][0]['type'] == 'not_found'
        
        # Assert - AI and Connections NOT called
        mock_ai_enhancement_manager.enhance_note.assert_not_called()
        mock_connection_manager.discover_links.assert_not_called()
    
    def test_core_continues_on_ai_failure_with_degraded_result(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test Core continues when AI fails (AI is enhancement, not requirement)."""
        # Arrange
        mock_analytics_manager.assess_quality.return_value = {
            'success': True,
            'quality_score': 0.8
        }
        
        mock_ai_enhancement_manager.enhance_note.side_effect = Exception("AI processing failed")
        
        mock_connection_manager.discover_links.return_value = [
            {'target': 'related.md', 'score': 0.9}
        ]
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('test.md', dry_run=True)
        
        # Assert - Workflow continues despite AI failure
        assert 'analytics' in result
        assert result['analytics']['quality_score'] == 0.8
        
        # Assert - AI error recorded but workflow continues
        ai_errors = [e for e in result['errors'] if e['stage'] == 'ai_enhancement']
        assert len(ai_errors) == 1
        assert 'AI processing failed' in ai_errors[0]['error']
        
        # Assert - Degraded AI result present
        assert 'ai_enhancement' in result
        assert result['ai_enhancement']['success'] == False
        assert result['ai_enhancement']['tags'] == []
        assert result['ai_enhancement']['summary'] == ''
        
        # Assert - Connections still called and processed
        assert 'connections' in result
        assert len(result['connections']) == 1
        mock_connection_manager.discover_links.assert_called_once()


class TestCoreAICostGating:
    """Test AI enhancement cost gating based on quality_score."""
    
    def test_core_skips_ai_when_quality_score_below_threshold(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test Core skips AI enhancement when quality_score < 0.3."""
        # Arrange
        mock_analytics_manager.assess_quality.return_value = {
            'success': True,
            'quality_score': 0.2  # Below 0.3 threshold
        }
        
        mock_connection_manager.discover_links.return_value = []
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('low-quality.md', dry_run=True)
        
        # Assert - AI NOT called (cost gating)
        mock_ai_enhancement_manager.enhance_note.assert_not_called()
        
        # Assert - Warning about AI skipped
        assert any('AI' in str(w) and 'skipped' in str(w) for w in result.get('warnings', []))
        
        # Assert - AI result indicates skipped
        assert result['ai_enhancement']['skipped'] == True
        assert result['ai_enhancement']['reason'] == 'quality_too_low'


class TestCoreBugReporting:
    """Test Core's bug report creation on total failures."""
    
    def test_core_creates_bug_report_on_total_failure(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test Core creates WORKFLOW_FAILURE bug report when all 3 managers fail."""
        # Arrange
        mock_analytics_manager.assess_quality.side_effect = Exception("Analytics critical error")
        mock_ai_enhancement_manager.enhance_note.side_effect = Exception("AI total failure")
        mock_connection_manager.discover_links.side_effect = Exception("Connections failed")
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('test.md', dry_run=False)
        
        # Assert - All 3 errors recorded
        assert len(result['errors']) >= 3
        
        # Assert - Warning about total failure
        assert any('Total workflow failure' in str(w) for w in result.get('warnings', []))
        
        # Assert - Bug report created
        bug_reports = list((mock_base_dir / ".automation" / "review_queue").glob('WORKFLOW_FAILURE_*.md'))
        assert len(bug_reports) > 0
        
        # Assert - Bug report contains critical info
        bug_content = bug_reports[0].read_text()
        assert 'CRITICAL' in bug_content
        assert 'test.md' in bug_content
        assert 'Analytics critical error' in bug_content or 'ANALYTICS' in bug_content


class TestCoreResultValidation:
    """Test Core's result validation with sensible defaults."""
    
    def test_core_validates_manager_results_and_uses_defaults(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test Core validates manager results and applies sensible defaults."""
        # Arrange - Analytics missing quality_score
        mock_analytics_manager.assess_quality.return_value = {
            'success': True
            # Missing: quality_score
        }
        
        # Arrange - AI missing tags and summary
        mock_ai_enhancement_manager.enhance_note.return_value = {
            'success': True
            # Missing: tags, summary
        }
        
        mock_connection_manager.discover_links.return_value = []
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('test.md', dry_run=True)
        
        # Assert - Defaults applied to analytics
        assert 'quality_score' in result['analytics']
        assert result['analytics']['quality_score'] == 0.5  # Neutral default
        
        # Assert - Defaults applied to AI
        assert 'tags' in result['ai_enhancement']
        assert result['ai_enhancement']['tags'] == []
        assert 'summary' in result['ai_enhancement']
        assert result['ai_enhancement']['summary'] == ''


class TestCoreDryRunMode:
    """Test Core's dry run mode prevents file writes."""
    
    def test_dry_run_prevents_save_operations(
        self, mock_base_dir, sample_config, mock_analytics_manager,
        mock_ai_enhancement_manager, mock_connection_manager
    ):
        """Test dry_run=True prevents file writes."""
        # Arrange
        mock_analytics_manager.assess_quality.return_value = {
            'success': True,
            'quality_score': 0.8
        }
        
        mock_ai_enhancement_manager.enhance_note.return_value = {
            'success': True,
            'tags': ['test'],
            'summary': 'Test'
        }
        
        mock_connection_manager.discover_links.return_value = []
        
        core = CoreWorkflowManager(
            mock_base_dir, sample_config,
            mock_analytics_manager,
            mock_ai_enhancement_manager,
            mock_connection_manager
        )
        
        # Act
        result = core.process_inbox_note('test.md', dry_run=True)
        
        # Assert - All managers called with dry_run=True
        mock_analytics_manager.assess_quality.assert_called_with('test.md', dry_run=True)
        mock_ai_enhancement_manager.enhance_note.assert_called_with('test.md', fast=False, dry_run=True)
        mock_connection_manager.discover_links.assert_called_with('test.md', dry_run=True)
        
        # Assert - Result indicates dry_run
        # (Implementation detail: Core should track dry_run in result)
        assert result.get('dry_run') == True or 'dry_run' in str(result.get('warnings', []))
