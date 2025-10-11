"""
TDD Iteration 3 RED Phase: Feature Handler Configuration Support

Tests for configuration-driven handler behavior:
- YAML configuration loading and validation
- Handler initialization with config dicts
- Backward compatibility with positional args
- Default value handling for missing config keys
- Configuration validation and error handling
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add development directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.automation.feature_handlers import ScreenshotEventHandler, SmartLinkEventHandler
from src.automation.config import ConfigurationLoader, DaemonConfig


class TestScreenshotHandlerConfiguration:
    """Test ScreenshotEventHandler configuration loading"""
    
    def test_screenshot_handler_loads_onedrive_path_from_config(self):
        """Handler should load OneDrive path from config dict"""
        config_dict = {
            'onedrive_path': '/test/onedrive/path',
            'knowledge_path': '/test/knowledge',
            'ocr_enabled': True,
            'processing_timeout': 600
        }
        
        handler = ScreenshotEventHandler(config=config_dict)
        
        assert handler.onedrive_path == Path('/test/onedrive/path')
        assert handler.knowledge_path == Path('/test/knowledge')
        assert handler.ocr_enabled is True
        assert handler.processing_timeout == 600
    
    def test_screenshot_handler_backward_compatibility_positional_args(self):
        """Handler should still work with positional argument (backward compatibility)"""
        handler = ScreenshotEventHandler(onedrive_path='/legacy/path')
        
        assert handler.onedrive_path == Path('/legacy/path')
        # Should use defaults for other settings
        assert handler.knowledge_path is not None
        assert handler.ocr_enabled is True  # Default
        assert handler.processing_timeout == 600  # Default
    
    def test_screenshot_handler_config_overrides_positional_arg(self):
        """Config dict should take precedence over positional arg"""
        config_dict = {'onedrive_path': '/config/path'}
        
        handler = ScreenshotEventHandler(
            onedrive_path='/positional/path',
            config=config_dict
        )
        
        assert handler.onedrive_path == Path('/config/path')
    
    def test_screenshot_handler_uses_defaults_for_missing_config_keys(self):
        """Handler should use sensible defaults when config keys missing"""
        config_dict = {'onedrive_path': '/test/path'}  # Minimal config
        
        handler = ScreenshotEventHandler(config=config_dict)
        
        assert handler.onedrive_path == Path('/test/path')
        assert handler.knowledge_path is not None  # Has default
        assert handler.ocr_enabled is True  # Default enabled
        assert handler.processing_timeout == 600  # 10 minutes default
    
    def test_screenshot_handler_validates_required_config_keys(self):
        """Handler should validate required configuration keys"""
        config_dict = {'knowledge_path': '/test/knowledge'}  # Missing onedrive_path
        
        with pytest.raises(ValueError, match="onedrive_path.*required"):
            handler = ScreenshotEventHandler(config=config_dict)
    
    def test_screenshot_handler_passes_config_to_integrator(self):
        """Handler should pass configuration to ScreenshotProcessorIntegrator"""
        config_dict = {
            'onedrive_path': '/test/path',
            'ocr_enabled': False,
            'processing_timeout': 300
        }
        
        with patch('src.automation.feature_handlers.ScreenshotProcessorIntegrator') as MockIntegrator:
            handler = ScreenshotEventHandler(config=config_dict)
            
            # Verify integrator received configuration
            call_args = MockIntegrator.call_args
            assert call_args is not None
            # Should pass config to integrator initialization
            assert 'ocr_enabled' in str(call_args) or call_args[1].get('ocr_enabled') == False


class TestSmartLinkHandlerConfiguration:
    """Test SmartLinkEventHandler configuration loading"""
    
    def test_smart_link_handler_loads_similarity_threshold_from_config(self):
        """Handler should load similarity threshold from config dict"""
        config_dict = {
            'similarity_threshold': 0.80,
            'max_suggestions': 10,
            'auto_insert': True
        }
        
        handler = SmartLinkEventHandler(config=config_dict)
        
        assert handler.similarity_threshold == 0.80
        assert handler.max_suggestions == 10
        assert handler.auto_insert is True
    
    def test_smart_link_handler_backward_compatibility(self):
        """Handler should work without config dict (backward compatibility)"""
        handler = SmartLinkEventHandler()
        
        # Should use defaults
        assert handler.similarity_threshold == 0.75  # Default
        assert handler.max_suggestions == 5  # Default
        assert handler.auto_insert is False  # Default (safe)
    
    def test_smart_link_handler_uses_defaults_for_missing_keys(self):
        """Handler should use defaults for missing configuration keys"""
        config_dict = {'similarity_threshold': 0.85}  # Partial config
        
        handler = SmartLinkEventHandler(config=config_dict)
        
        assert handler.similarity_threshold == 0.85  # From config
        assert handler.max_suggestions == 5  # Default
        assert handler.auto_insert is False  # Default
    
    def test_smart_link_handler_validates_similarity_threshold_range(self):
        """Handler should validate similarity threshold is in valid range (0.0-1.0)"""
        config_dict = {'similarity_threshold': 1.5}  # Invalid
        
        with pytest.raises(ValueError, match="similarity_threshold.*0.0.*1.0"):
            handler = SmartLinkEventHandler(config=config_dict)
    
    def test_smart_link_handler_passes_config_to_integrator(self):
        """Handler should pass configuration to SmartLinkEngineIntegrator"""
        config_dict = {
            'similarity_threshold': 0.85,
            'max_suggestions': 8
        }
        
        with patch('src.automation.feature_handlers.SmartLinkEngineIntegrator') as MockIntegrator:
            handler = SmartLinkEventHandler(config=config_dict)
            
            # Verify integrator received configuration
            call_args = MockIntegrator.call_args
            assert call_args is not None
            # Should pass threshold and max_suggestions to integrator


class TestConfigurationLoaderHandlerIntegration:
    """Test ConfigurationLoader properly parses handler configuration"""
    
    def test_configuration_loader_parses_screenshot_handler_section(self):
        """ConfigurationLoader should parse screenshot_handler section from YAML"""
        raw_config = {
            'daemon': {'check_interval': 60, 'log_level': 'INFO'},
            'screenshot_handler': {
                'enabled': True,
                'onedrive_path': '~/OneDrive/Screenshots',
                'knowledge_path': '~/repos/inneros-zettelkasten/knowledge',
                'ocr_enabled': True,
                'processing_timeout': 600
            }
        }
        
        loader = ConfigurationLoader()
        config = loader._parse_config(raw_config)
        
        assert config.screenshot_handler is not None
        assert config.screenshot_handler.enabled is True
        assert config.screenshot_handler.onedrive_path == '~/OneDrive/Screenshots'
        assert config.screenshot_handler.knowledge_path == '~/repos/inneros-zettelkasten/knowledge'
        assert config.screenshot_handler.ocr_enabled is True
        assert config.screenshot_handler.processing_timeout == 600
    
    def test_configuration_loader_parses_smart_link_handler_section(self):
        """ConfigurationLoader should parse smart_link_handler section from YAML"""
        raw_config = {
            'daemon': {'check_interval': 60},
            'smart_link_handler': {
                'enabled': True,
                'similarity_threshold': 0.80,
                'max_suggestions': 10,
                'auto_insert': False
            }
        }
        
        loader = ConfigurationLoader()
        config = loader._parse_config(raw_config)
        
        assert config.smart_link_handler is not None
        assert config.smart_link_handler.enabled is True
        assert config.smart_link_handler.similarity_threshold == 0.80
        assert config.smart_link_handler.max_suggestions == 10
        assert config.smart_link_handler.auto_insert is False
    
    def test_configuration_loader_handles_missing_handler_sections(self):
        """ConfigurationLoader should handle missing handler sections gracefully"""
        raw_config = {
            'daemon': {'check_interval': 60, 'log_level': 'INFO'}
            # No handler sections
        }
        
        loader = ConfigurationLoader()
        config = loader._parse_config(raw_config)
        
        # Should be None, not raise errors
        assert config.screenshot_handler is None
        assert config.smart_link_handler is None
    
    def test_configuration_loader_uses_defaults_for_optional_handler_keys(self):
        """ConfigurationLoader should use defaults for optional handler keys"""
        raw_config = {
            'daemon': {'check_interval': 60},
            'screenshot_handler': {
                'enabled': True,
                'onedrive_path': '~/OneDrive'
                # Missing optional keys
            }
        }
        
        loader = ConfigurationLoader()
        config = loader._parse_config(raw_config)
        
        assert config.screenshot_handler.enabled is True
        assert config.screenshot_handler.onedrive_path == '~/OneDrive'
        # Should have defaults for optional fields
        assert hasattr(config.screenshot_handler, 'ocr_enabled')
        assert hasattr(config.screenshot_handler, 'processing_timeout')


class TestConfigurationValidation:
    """Test configuration validation and error handling"""
    
    def test_validates_screenshot_handler_onedrive_path_exists(self):
        """Should validate OneDrive path is provided when handler enabled"""
        config_dict = {
            'screenshot_handler': {
                'enabled': True
                # Missing onedrive_path
            }
        }
        
        from src.automation.config_utils import ConfigValidator
        errors = ConfigValidator.validate_handler_config(config_dict)
        
        assert len(errors) > 0
        assert any('onedrive_path' in err.lower() for err in errors)
    
    def test_validates_smart_link_similarity_threshold_range(self):
        """Should validate similarity threshold is in valid range"""
        config_dict = {
            'smart_link_handler': {
                'enabled': True,
                'similarity_threshold': 2.0  # Invalid
            }
        }
        
        from src.automation.config_utils import ConfigValidator
        errors = ConfigValidator.validate_handler_config(config_dict)
        
        assert len(errors) > 0
        assert any('similarity_threshold' in err.lower() for err in errors)
    
    def test_validation_passes_for_valid_handler_config(self):
        """Should pass validation for valid handler configuration"""
        config_dict = {
            'screenshot_handler': {
                'enabled': True,
                'onedrive_path': '~/OneDrive',
                'ocr_enabled': True
            },
            'smart_link_handler': {
                'enabled': True,
                'similarity_threshold': 0.75,
                'max_suggestions': 5
            }
        }
        
        from src.automation.config_utils import ConfigValidator
        errors = ConfigValidator.validate_handler_config(config_dict)
        
        assert len(errors) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
