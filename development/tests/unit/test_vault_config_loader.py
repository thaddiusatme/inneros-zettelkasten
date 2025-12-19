"""
Tests for Vault Configuration Loader

Ensures centralized vault configuration works correctly for pointing
all automations to knowledge/Inbox instead of root-level Inbox.

Created: 2025-11-02 (Post Sprint 1)
"""

import pytest
from pathlib import Path
from src.config.vault_config_loader import VaultConfig, get_vault_config, get_inbox_dir

pytestmark = pytest.mark.ci


class TestVaultConfig:
    """Test vault configuration loading and path resolution."""

    def test_default_config_structure(self):
        """Test that default config has expected structure."""
        config = VaultConfig()

        # Should have vault root
        assert config.vault_root.name == "knowledge"

        # Should have all standard directories
        assert config.inbox_dir.name == "Inbox"
        assert config.fleeting_dir.name == "Fleeting Notes"
        assert config.permanent_dir.name == "Permanent Notes"
        assert config.literature_dir.name == "Literature Notes"

    def test_inbox_dir_points_to_knowledge_inbox(self):
        """Test that inbox_dir resolves to knowledge/Inbox."""
        config = VaultConfig()

        # Inbox should be inside knowledge/
        assert "knowledge" in str(config.inbox_dir)
        assert config.inbox_dir.name == "Inbox"

        # Full path should be {base_dir}/knowledge/Inbox
        assert config.inbox_dir == config.vault_root / "Inbox"

    def test_all_directories_under_knowledge(self):
        """Test that all directories resolve under knowledge/ root."""
        config = VaultConfig()

        directories = [
            config.inbox_dir,
            config.fleeting_dir,
            config.permanent_dir,
            config.literature_dir,
            config.archive_dir,
            config.reports_dir,
            config.media_dir,
        ]

        for directory in directories:
            # All should be under knowledge/
            assert (
                config.vault_root in directory.parents or directory == config.vault_root
            )

    def test_quality_thresholds(self):
        """Test quality threshold configuration."""
        config = VaultConfig()

        assert config.quality_threshold == 0.7
        assert config.high_quality_threshold == 0.8

    def test_get_directory_by_name(self):
        """Test dynamic directory lookup."""
        config = VaultConfig()

        # Should be able to get any configured directory
        projects_dir = config.get_directory("projects")
        assert projects_dir.name == "Projects"
        assert config.vault_root in projects_dir.parents

        templates_dir = config.get_directory("templates")
        assert templates_dir.name == "Templates"

    def test_get_directory_unknown_raises_error(self):
        """Test that unknown directory names raise ValueError."""
        config = VaultConfig()

        with pytest.raises(ValueError, match="not found in vault configuration"):
            config.get_directory("nonexistent_directory")

    def test_singleton_get_vault_config(self):
        """Test that get_vault_config returns same instance (cached)."""
        config1 = get_vault_config()
        config2 = get_vault_config()

        # Should be same instance due to @lru_cache
        assert config1 is config2

    def test_get_inbox_dir_convenience_function(self):
        """Test convenience function for getting inbox directory."""
        inbox = get_inbox_dir()

        assert "knowledge" in str(inbox)
        assert inbox.name == "Inbox"

    def test_ensure_directories_exist(self, tmp_path):
        """Test that ensure_directories_exist creates all dirs."""
        # Create config with temp base directory
        config = VaultConfig(base_dir=tmp_path)

        # Directories should not exist yet
        assert not config.inbox_dir.exists()
        assert not config.permanent_dir.exists()

        # Create them
        config.ensure_directories_exist()

        # Now they should exist
        assert config.inbox_dir.exists()
        assert config.permanent_dir.exists()
        assert config.literature_dir.exists()
        assert config.fleeting_dir.exists()


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing code."""

    def test_path_objects_work_with_string_concatenation(self):
        """Test that Path objects work in existing code patterns."""
        config = VaultConfig()

        # Should be able to use with string operations
        inbox_str = str(config.inbox_dir)
        assert "knowledge" in inbox_str
        assert "Inbox" in inbox_str

    def test_config_works_with_relative_base_dir(self):
        """Test config works when base_dir is relative path."""
        config = VaultConfig(base_dir=Path("."))

        # Should still resolve correctly
        assert config.vault_root.name == "knowledge"
        assert config.inbox_dir.name == "Inbox"

    def test_migration_pattern_old_to_new(self, tmp_path):
        """Test migrating from old pattern to new pattern."""
        # OLD PATTERN (hardcoded):
        base_dir_old = tmp_path
        inbox_dir_old = base_dir_old / "Inbox"  # Root-level Inbox

        # NEW PATTERN (using config):
        config = VaultConfig(base_dir=tmp_path)
        inbox_dir_new = config.inbox_dir  # knowledge/Inbox

        # New pattern should point to knowledge/Inbox
        assert "knowledge" in str(inbox_dir_new)
        assert "knowledge" not in str(inbox_dir_old)

        # Names should match
        assert inbox_dir_old.name == inbox_dir_new.name == "Inbox"


class TestProductionUsage:
    """Test real-world usage patterns."""

    def test_promotion_engine_pattern(self):
        """Test pattern used by PromotionEngine."""
        # Simulate PromotionEngine initialization
        base_dir = Path(".")
        config = get_vault_config(str(base_dir))

        # Engine should use these paths
        inbox_dir = config.inbox_dir
        permanent_dir = config.permanent_dir
        literature_dir = config.literature_dir
        fleeting_dir = config.fleeting_dir

        # All should be under knowledge/
        assert "knowledge" in str(inbox_dir)
        assert "knowledge" in str(permanent_dir)
        assert "knowledge" in str(literature_dir)
        assert "knowledge" in str(fleeting_dir)

    def test_automation_script_pattern(self):
        """Test pattern for automation scripts."""
        # Script should use config
        config = get_vault_config()

        # Get inbox for processing
        inbox_path = config.inbox_dir

        # Should point to production inbox
        assert inbox_path == config.vault_root / "Inbox"
        assert "knowledge" in str(inbox_path)

    def test_cli_tool_pattern(self):
        """Test pattern for CLI tools."""
        # CLI receives vault_path argument
        vault_path = "."
        config = get_vault_config(vault_path)

        # CLI should use config for directory resolution
        status_dirs = {
            "Inbox": config.inbox_dir,
            "Fleeting Notes": config.fleeting_dir,
            "Permanent Notes": config.permanent_dir,
        }

        # All should resolve to knowledge/ subdirectories
        for dir_name, dir_path in status_dirs.items():
            assert "knowledge" in str(dir_path)
