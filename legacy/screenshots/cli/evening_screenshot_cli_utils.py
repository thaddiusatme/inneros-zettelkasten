#!/usr/bin/env python3
"""
TDD ITERATION 2 GREEN PHASE: Evening Screenshot CLI Utilities Compatibility Shim

This module provides compatibility by re-exporting classes from screenshot_cli_utils
under expected names for evening screenshot workflow tests.

Following established patterns from Smart Link Management and Advanced Tag Enhancement
TDD iterations for seamless CLI integration.
"""

# Re-export classes with evening-specific naming for compatibility
from .screenshot_cli_utils import (
    ScreenshotCLIOrchestrator as EveningScreenshotCLIOrchestrator,
    CLIProgressReporter,
    ConfigurationManager,
    CLIOutputFormatter,
    CLIExportManager,
)

# Make classes available at module level for test imports
__all__ = [
    "EveningScreenshotCLIOrchestrator",
    "CLIProgressReporter",
    "ConfigurationManager",
    "CLIOutputFormatter",
    "CLIExportManager",
]
