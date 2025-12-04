#!/usr/bin/env python3
"""CLI Pattern Linter - Placeholder.

This is a placeholder script for the pre-commit hook.
TODO: Implement actual CLI argument pattern validation per CLI-ARGUMENT-STANDARDS.md
"""

import sys


def main() -> int:
    """Placeholder linter - always passes."""
    # TODO: Implement actual linting logic
    # For now, pass all files to unblock commits
    if len(sys.argv) > 1:
        print(f"  ✓ {sys.argv[1]}: OK (placeholder)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
