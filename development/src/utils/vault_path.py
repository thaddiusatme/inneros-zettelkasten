"""Utility for resolving the default InnerOS vault path.

The resolver checks, in order:
1. Environment variable ``INNEROS_VAULT_PATH``.
2. Configuration files named ``.inneros.yaml``, ``.inneros.yml`` or ``.inneros.json``
   located either in the **current working directory** or the user's home
   directory.

If a candidate path exists and is a directory, it is returned as a ``Path``
object. Otherwise the resolver returns ``None``.

This utility is kept intentionally small and dependency-light. YAML parsing is
only attempted if ``pyyaml`` is importable; otherwise the file is ignored.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

_CONFIG_FILENAMES = (".inneros.yaml", ".inneros.yml", ".inneros.json")


def _load_yaml(path: Path) -> Optional[dict]:
    """Attempt to load YAML safely; returns ``None`` on failure or missing lib."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return None  # YAML support not available

    try:
        return yaml.safe_load(path.read_text()) or {}
    except Exception:
        return None


def _load_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _read_config_file(config_path: Path) -> Optional[str]:
    """Return the ``vault_path`` value if present in *config_path*."""
    if not config_path.exists() or not config_path.is_file():
        return None

    if config_path.suffix in {".yaml", ".yml"}:
        data = _load_yaml(config_path)
        if data is None:
            # Lightweight fallback: naive key: value parser (no nesting)
            try:
                import re

                matches = re.findall(
                    r'^\s*vault_path\s*:\s*["\']?(.*?)["\']?\s*$',
                    config_path.read_text(),
                    re.MULTILINE,
                )
                if matches:
                    return matches[0]
            except Exception:
                pass
    else:
        data = _load_json(config_path)

    if not isinstance(data, dict):
        return None
    vault_path = data.get("vault_path")
    if isinstance(vault_path, str):
        return vault_path
    return None


def get_default_vault_path() -> Optional[Path]:
    """Resolve and return the default vault directory or ``None``.

    Precedence order:
    1. ``INNEROS_VAULT_PATH`` environment variable.
    2. Config file in current working directory.
    3. Config file in the user's home directory.
    """
    # 1. Environment variable
    env_path = os.environ.get("INNEROS_VAULT_PATH")
    if env_path and Path(env_path).expanduser().resolve().is_dir():
        return Path(env_path).expanduser().resolve()

    # 2 & 3. Config files
    search_dirs = [Path.cwd(), Path.home()]
    for directory in search_dirs:
        for filename in _CONFIG_FILENAMES:
            candidate = directory / filename
            vault_path = _read_config_file(candidate)
            if vault_path and Path(vault_path).expanduser().resolve().is_dir():
                return Path(vault_path).expanduser().resolve()

    return None
