#!/usr/bin/env python3
"""
Atomic I/O operations for safe file writes.
Implements temp file + fsync + atomic rename pattern to prevent partial writes.
"""

import os
from pathlib import Path
from typing import Union


def safe_write(path: Union[str, Path], content: str) -> None:
    """
    Write content to file atomically using temp file + fsync + rename pattern.

    This prevents partial writes on interruption (SIGTERM, power loss, etc.)
    by writing to a temporary file first, syncing to disk, then atomically
    renaming to the target path.

    Args:
        path: Target file path (string or pathlib.Path)
        content: Content to write to file

    Raises:
        IOError: If write operation fails
        OSError: If fsync or rename operation fails
    """
    # Convert to Path object for consistent handling
    target_path = Path(path)
    temp_path_str = str(target_path) + ".tmp"

    try:
        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Write to temporary file
        with open(temp_path_str, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()  # Flush Python buffers
            os.fsync(f.fileno())  # Force OS to write to disk

        # Atomically replace/rename temp file to target (overwrites if exists)
        os.replace(temp_path_str, str(target_path))

    except Exception as e:
        # Clean up temp file if it exists
        if os.path.exists(temp_path_str):
            try:
                os.unlink(temp_path_str)
            except OSError:
                pass  # Ignore cleanup failures

        # Re-raise the original exception
        raise e
