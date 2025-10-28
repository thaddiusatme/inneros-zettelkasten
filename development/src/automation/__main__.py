"""
Module entry point for automation daemon.
Allows running with: python3 -m src.automation
"""

from .daemon import main

if __name__ == "__main__":
    main()
