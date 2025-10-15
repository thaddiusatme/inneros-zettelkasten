"""
Tests for ConfigurationCoordinator (ADR-002 Phase 12a)

RED Phase: Comprehensive failing tests for Configuration & Initialization extraction.
Target: Extract ~149 LOC from WorkflowManager (__init__ and _load_config).
"""
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Target class (doesn't exist yet - RED phase)
from src.ai.configuration_coordinator import ConfigurationCoordinator


class TestConfigurationCoordinatorInitialization:
    """Test ConfigurationCoordinator initialization and dependency management."""
    
    def test_initialization_with_explicit_base_directory(self, tmp_path):
        """Test coordinator initialization with explicit vault path."""
        vault_path = tmp_path / "test_vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        
        assert coordinator.base_dir == vault_path
        assert coordinator.inbox_dir == vault_path / "Inbox"
        assert coordinator.fleeting_dir == vault_path / "Fleeting Notes"
        assert coordinator.literature_dir == vault_path / "Literature Notes"
        assert coordinator.permanent_dir == vault_path / "Permanent Notes"
        assert coordinator.archive_dir == vault_path / "Archive"
    
    def test_initialization_with_vault_path_resolution(self, tmp_path, monkeypatch):
        """Test coordinator initialization with automatic vault path resolution."""
        vault_path = tmp_path / "resolved_vault"
        vault_path.mkdir()
        
        # Mock the vault path resolver at the correct import location
        mock_resolver = Mock(return_value=str(vault_path))
        monkeypatch.setattr(
            'src.utils.vault_path.get_default_vault_path',
            mock_resolver
        )
        
        coordinator = ConfigurationCoordinator()
        
        assert coordinator.base_dir == vault_path
        mock_resolver.assert_called_once()
    
    def test_initialization_fails_with_invalid_path(self):
        """Test coordinator raises ValueError for non-existent vault path."""
        with pytest.raises(ValueError, match="No vault path supplied"):
            ConfigurationCoordinator(base_directory=None)
    
    def test_initialization_expands_user_home_directory(self, tmp_path):
        """Test coordinator expands ~ in base_directory path."""
        # Create temp vault in user home equivalent
        vault_path = tmp_path / "home" / "user" / "vault"
        vault_path.mkdir(parents=True)
        
        # Mock Path.expanduser to return our test path
        with patch.object(Path, 'expanduser', return_value=vault_path):
            coordinator = ConfigurationCoordinator(base_directory="~/vault")
            assert coordinator.base_dir == vault_path


class TestConfigurationCoordinatorAIComponents:
    """Test AI component initialization and management."""
    
    @patch('src.ai.configuration_coordinator.AITagger')
    @patch('src.ai.configuration_coordinator.AISummarizer')
    @patch('src.ai.configuration_coordinator.AIConnections')
    @patch('src.ai.configuration_coordinator.AIEnhancer')
    @patch('src.ai.configuration_coordinator.NoteAnalytics')
    def test_ai_components_initialization(
        self, mock_analytics, mock_enhancer, mock_connections,
        mock_summarizer, mock_tagger, tmp_path
    ):
        """Test all AI components are initialized correctly."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        
        # Verify all AI components created
        mock_tagger.assert_called_once()
        mock_summarizer.assert_called_once()
        mock_connections.assert_called_once()
        mock_enhancer.assert_called_once()
        mock_analytics.assert_called_once_with(str(vault_path))
        
        # Verify components stored as instance variables
        assert coordinator.tagger is not None
        assert coordinator.summarizer is not None
        assert coordinator.connections is not None
        assert coordinator.enhancer is not None
        assert coordinator.analytics is not None


class TestConfigurationCoordinatorDependencies:
    """Test coordinator placeholder management."""
    
    def test_coordinator_placeholders_initialized_to_none(self, tmp_path):
        """Test that coordinator placeholders are initialized to None."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        
        # Verify all coordinator placeholders are None (will be set by WorkflowManager)
        assert coordinator.lifecycle_manager is None
        assert coordinator.connection_coordinator is None
        assert coordinator.analytics_coordinator is None
        assert coordinator.promotion_engine is None
        assert coordinator.review_triage_coordinator is None
        assert coordinator.note_processing_coordinator is None
        assert coordinator.safe_image_processing_coordinator is None
        assert coordinator.orphan_remediation_coordinator is None
        assert coordinator.fleeting_analysis_coordinator is None
        assert coordinator.reporting_coordinator is None
        assert coordinator.batch_processing_coordinator is None
    
    def test_set_coordinator_method(self, tmp_path):
        """Test that coordinators can be set dynamically."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        
        # Set a mock coordinator
        mock_coordinator = Mock()
        coordinator.set_coordinator('lifecycle_manager', mock_coordinator)
        
        assert coordinator.lifecycle_manager is mock_coordinator


class TestConfigurationLoading:
    """Test configuration file loading and management."""
    
    def test_load_config_with_default_values(self, tmp_path):
        """Test config loading returns default values when no config file exists."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        config = coordinator.get_config()
        
        # Verify default configuration values
        assert config["auto_tag_inbox"] is True
        assert config["auto_summarize_long_notes"] is True
        assert config["auto_enhance_permanent_notes"] is False
        assert config["min_words_for_summary"] == 500
        assert config["max_tags_per_note"] == 8
        assert config["similarity_threshold"] == 0.7
        assert config["archive_after_days"] == 90
    
    def test_load_config_from_existing_file(self, tmp_path):
        """Test config loading merges user config with defaults."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        # Create custom config file
        config_file = vault_path / ".ai_workflow_config.json"
        custom_config = {
            "auto_tag_inbox": False,
            "max_tags_per_note": 12,
            "custom_setting": "custom_value"
        }
        config_file.write_text(json.dumps(custom_config))
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        config = coordinator.get_config()
        
        # Verify custom values override defaults
        assert config["auto_tag_inbox"] is False
        assert config["max_tags_per_note"] == 12
        assert config["custom_setting"] == "custom_value"
        
        # Verify defaults are preserved for non-overridden values
        assert config["auto_summarize_long_notes"] is True
        assert config["similarity_threshold"] == 0.7
    
    def test_load_config_handles_malformed_json(self, tmp_path):
        """Test config loading gracefully handles malformed JSON files."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        # Create malformed config file
        config_file = vault_path / ".ai_workflow_config.json"
        config_file.write_text("{invalid json content")
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        config = coordinator.get_config()
        
        # Should return default config without raising exception
        assert config["auto_tag_inbox"] is True
        assert config["max_tags_per_note"] == 8
    
    def test_config_file_path_is_correct(self, tmp_path):
        """Test config file path is constructed correctly."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        expected_config_path = vault_path / ".ai_workflow_config.json"
        
        assert coordinator.config_file_path == expected_config_path


class TestLegacyCompatibility:
    """Test legacy compatibility features."""
    
    def test_active_sessions_initialization(self, tmp_path):
        """Test legacy active_sessions dictionary is initialized."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        
        assert hasattr(coordinator, 'active_sessions')
        assert isinstance(coordinator.active_sessions, dict)
        assert len(coordinator.active_sessions) == 0


class TestConfigurationCoordinatorIntegration:
    """Test integration between ConfigurationCoordinator and WorkflowManager."""
    
    def test_coordinator_provides_core_dependencies(self, tmp_path):
        """Test coordinator exposes core dependencies needed by WorkflowManager."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        
        # Verify core dependencies are accessible
        assert coordinator.base_dir is not None
        assert coordinator.inbox_dir is not None
        assert coordinator.config is not None
        assert coordinator.tagger is not None
        assert coordinator.summarizer is not None
        assert coordinator.connections is not None
        assert coordinator.enhancer is not None
        assert coordinator.analytics is not None
        
        # Verify image processing components initialized
        assert coordinator.safe_image_processor is not None
        assert coordinator.image_integrity_monitor is not None
        assert coordinator.safe_workflow_processor is not None
        
        # Verify coordinator placeholders exist (even if None)
        assert hasattr(coordinator, 'lifecycle_manager')
        assert hasattr(coordinator, 'connection_coordinator')
        assert hasattr(coordinator, 'batch_processing_coordinator')
    
    def test_coordinator_initialization_performance(self, tmp_path):
        """Test coordinator initialization completes quickly."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        import time
        start = time.time()
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        duration = time.time() - start
        
        # Should initialize in less than 1 second
        assert duration < 1.0
        assert coordinator is not None


class TestUtilityMethods:
    """Test utility and helper methods."""
    
    def test_get_directory_paths(self, tmp_path):
        """Test utility method to retrieve all directory paths."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        paths = coordinator.get_directory_paths()
        
        assert paths["inbox"] == vault_path / "Inbox"
        assert paths["fleeting"] == vault_path / "Fleeting Notes"
        assert paths["literature"] == vault_path / "Literature Notes"
        assert paths["permanent"] == vault_path / "Permanent Notes"
        assert paths["archive"] == vault_path / "Archive"
    
    def test_reload_config(self, tmp_path):
        """Test config can be reloaded after file changes."""
        vault_path = tmp_path / "vault"
        vault_path.mkdir()
        
        coordinator = ConfigurationCoordinator(base_directory=str(vault_path))
        initial_config = coordinator.get_config()
        
        # Modify config file
        config_file = vault_path / ".ai_workflow_config.json"
        new_config = {"max_tags_per_note": 15}
        config_file.write_text(json.dumps(new_config))
        
        # Reload config
        coordinator.reload_config()
        updated_config = coordinator.get_config()
        
        assert updated_config["max_tags_per_note"] == 15
        assert initial_config["max_tags_per_note"] != updated_config["max_tags_per_note"]
