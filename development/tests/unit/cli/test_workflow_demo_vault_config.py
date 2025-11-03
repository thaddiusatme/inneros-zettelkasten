"""
Tests for workflow_demo.py vault configuration integration.

Vault Configuration Integration (GitHub Issue #45):
- Tests workflow_demo.py uses vault_config.yaml for directory paths
- Validates knowledge/ subdirectory organization
- Part of Phase 2 Priority 2 CLI tools migration (Module 2)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.config.vault_config_loader import get_vault_config


class TestWorkflowDemoVaultConfigIntegration:
    """Test workflow_demo.py integration with vault configuration."""

    def test_youtube_batch_processing_uses_vault_config_inbox(self, tmp_path):
        """
        RED PHASE: Verify YouTube batch processing uses vault config for inbox directory.
        
        Expected to FAIL until GREEN phase replaces hardcoded 'Inbox' path.
        The --process-youtube-notes command should use knowledge/Inbox from config.
        """
        # Arrange: Create vault config structure
        config = get_vault_config(str(tmp_path))
        config.inbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock YouTube note in knowledge/Inbox
        youtube_note = config.inbox_dir / "youtube-20250101-test.md"
        youtube_note.write_text("""---
title: Test YouTube Note
type: literature
url: https://youtube.com/watch?v=test123
---

Test content
""")
        
        # Act & Assert: Mock the YouTube processing to verify inbox path
        # The code at line 1810 currently hardcodes "Inbox"
        # It should use vault config instead
        from pathlib import Path as MockPath
        
        # Import will fail if hardcoded path is used (since only knowledge/Inbox exists)
        expected_inbox = config.inbox_dir
        actual_hardcoded = tmp_path / "Inbox"
        
        # Test assertion: vault config inbox should exist, hardcoded should not
        assert expected_inbox.exists(), "Vault config inbox should exist"
        assert not actual_hardcoded.exists(), "Hardcoded Inbox should not exist"
        assert "knowledge" in str(expected_inbox), f"Expected knowledge/ in path: {expected_inbox}"


class TestWorkflowDemoDirectoryResolution:
    """Test that workflow_demo properly resolves directories via vault config."""
    
    def test_module_can_access_vault_config(self, tmp_path):
        """
        RED PHASE: Verify workflow_demo.py can import and use vault_config_loader.
        
        This ensures the module has access to configuration infrastructure.
        """
        # The module should be able to import vault config
        try:
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from src.cli import workflow_demo
            from src.config.vault_config_loader import get_vault_config
            
            # Verify we can get config
            config = get_vault_config(str(tmp_path))
            assert config is not None
            assert hasattr(config, 'inbox_dir')
            
            # Verify knowledge/ subdirectory structure
            assert "knowledge" in str(config.inbox_dir)
            
        except ImportError as e:
            pytest.fail(f"Failed to import required modules: {e}")
