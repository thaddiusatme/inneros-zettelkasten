"""
Vault Configuration Loader

Centralizes vault directory structure configuration to make it easy to:
- Point all automations to knowledge/Inbox instead of root-level Inbox
- Support different vault structures for testing vs production
- Make directory paths configurable without code changes

Created: 2025-11-02 (Sprint 1 Retrospective complete)
Related: Starter pack improvements, production vault usage
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
from functools import lru_cache


class VaultConfig:
    """Load and provide access to vault structure configuration."""

    def __init__(
        self, config_path: Optional[Path] = None, base_dir: Optional[Path] = None
    ):
        """
        Initialize vault configuration.

        Args:
            config_path: Path to vault_config.yaml (defaults to development/vault_config.yaml)
            base_dir: Base directory for the vault (defaults to project root)
        """
        self.base_dir = base_dir or Path.cwd()

        # Default config path
        if config_path is None:
            # Try multiple locations
            candidates = [
                Path(__file__).parent.parent.parent
                / "vault_config.yaml",  # development/
                self.base_dir / "vault_config.yaml",  # project root
                self.base_dir
                / "development"
                / "vault_config.yaml",  # project_root/development/
            ]
            config_path = next((p for p in candidates if p.exists()), candidates[0])

        self.config_path = Path(config_path)
        self._config_data = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            # Return default configuration if file doesn't exist
            return self._get_default_config()

        with open(self.config_path, "r") as f:
            return yaml.safe_load(f) or {}

    def _get_default_config(self) -> Dict:
        """Return default configuration for backwards compatibility."""
        return {
            "vault": {
                "root": "knowledge",
                "directories": {
                    "inbox": "Inbox",
                    "fleeting": "Fleeting Notes",
                    "permanent": "Permanent Notes",
                    "literature": "Literature Notes",
                    "archive": "Archive",
                    "projects": "Projects",
                    "people": "People",
                    "templates": "Templates",
                    "reports": "Reports",
                    "media": "Media",
                },
            },
            "quality": {
                "auto_promote_threshold": 0.7,
                "high_quality_threshold": 0.8,
            },
            "workflow": {
                "enable_auto_promotion": True,
                "enable_quality_scoring": True,
                "enable_ai_tagging": True,
            },
        }

    @property
    def vault_root(self) -> Path:
        """Get the vault root directory (e.g., 'knowledge')."""
        root = self._config_data.get("vault", {}).get("root", "knowledge")
        return self.base_dir / root

    @property
    def inbox_dir(self) -> Path:
        """Get the Inbox directory path."""
        inbox_name = (
            self._config_data.get("vault", {})
            .get("directories", {})
            .get("inbox", "Inbox")
        )
        return self.vault_root / inbox_name

    @property
    def fleeting_dir(self) -> Path:
        """Get the Fleeting Notes directory path."""
        fleeting_name = (
            self._config_data.get("vault", {})
            .get("directories", {})
            .get("fleeting", "Fleeting Notes")
        )
        return self.vault_root / fleeting_name

    @property
    def permanent_dir(self) -> Path:
        """Get the Permanent Notes directory path."""
        permanent_name = (
            self._config_data.get("vault", {})
            .get("directories", {})
            .get("permanent", "Permanent Notes")
        )
        return self.vault_root / permanent_name

    @property
    def literature_dir(self) -> Path:
        """Get the Literature Notes directory path."""
        literature_name = (
            self._config_data.get("vault", {})
            .get("directories", {})
            .get("literature", "Literature Notes")
        )
        return self.vault_root / literature_name

    @property
    def archive_dir(self) -> Path:
        """Get the Archive directory path."""
        archive_name = (
            self._config_data.get("vault", {})
            .get("directories", {})
            .get("archive", "Archive")
        )
        return self.vault_root / archive_name

    @property
    def reports_dir(self) -> Path:
        """Get the Reports directory path."""
        reports_name = (
            self._config_data.get("vault", {})
            .get("directories", {})
            .get("reports", "Reports")
        )
        return self.vault_root / reports_name

    @property
    def media_dir(self) -> Path:
        """Get the Media directory path."""
        media_name = (
            self._config_data.get("vault", {})
            .get("directories", {})
            .get("media", "Media")
        )
        return self.vault_root / media_name

    def get_directory(self, dir_name: str) -> Path:
        """
        Get any configured directory by name.

        Args:
            dir_name: Directory name from config (e.g., 'inbox', 'projects', 'templates')

        Returns:
            Full path to the directory
        """
        dir_relative = (
            self._config_data.get("vault", {}).get("directories", {}).get(dir_name)
        )
        if dir_relative is None:
            raise ValueError(f"Directory '{dir_name}' not found in vault configuration")
        return self.vault_root / dir_relative

    @property
    def quality_threshold(self) -> float:
        """Get the auto-promotion quality threshold."""
        return self._config_data.get("quality", {}).get("auto_promote_threshold", 0.7)

    @property
    def high_quality_threshold(self) -> float:
        """Get the high quality threshold."""
        return self._config_data.get("quality", {}).get("high_quality_threshold", 0.8)

    def ensure_directories_exist(self):
        """Create all configured directories if they don't exist."""
        directories = self._config_data.get("vault", {}).get("directories", {})
        for dir_name in directories.values():
            dir_path = self.vault_root / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_vault_config(base_dir: Optional[str] = None) -> VaultConfig:
    """
    Get a singleton instance of VaultConfig.

    Args:
        base_dir: Base directory for the vault (defaults to current working directory)

    Returns:
        VaultConfig instance

    Usage:
        >>> config = get_vault_config()
        >>> inbox_path = config.inbox_dir
        >>> print(inbox_path)  # knowledge/Inbox
    """
    return VaultConfig(base_dir=Path(base_dir) if base_dir else None)


# Backwards compatibility helpers
def get_inbox_dir(base_dir: Optional[str] = None) -> Path:
    """Get inbox directory path (defaults to knowledge/Inbox)."""
    return get_vault_config(base_dir).inbox_dir


def get_vault_root(base_dir: Optional[str] = None) -> Path:
    """Get vault root directory (defaults to knowledge/)."""
    return get_vault_config(base_dir).vault_root
