#!/usr/bin/env python3
"""
Daemon Launcher Script

Handles Python path setup and runs the daemon with proper imports.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now import and run
from automation.daemon_cli import main

if __name__ == "__main__":
    sys.exit(main())
