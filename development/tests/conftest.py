"""
Pytest configuration for test suite
"""

import sys
from pathlib import Path

# Add src directory to Python path
development_dir = Path(__file__).parent.parent
src_dir = development_dir / "src"
sys.path.insert(0, str(development_dir))
sys.path.insert(0, str(src_dir))
