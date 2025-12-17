"""Configuration management for InnerOS Zettelkasten."""

from .vault_config_loader import (
    VaultConfig,
    get_vault_config,
    get_inbox_dir,
    get_vault_root,
)

__all__ = ["VaultConfig", "get_vault_config", "get_inbox_dir", "get_vault_root"]
