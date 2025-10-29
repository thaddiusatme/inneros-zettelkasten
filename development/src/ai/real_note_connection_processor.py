#!/usr/bin/env python3
"""
Real Note Connection Processor - TDD Iteration 3 GREEN Phase
Processes real notes for connection discovery and link suggestions
"""

from typing import List
from .connection_integration_utils import RealConnectionProcessor
from .link_suggestion_engine import LinkSuggestionEngine, LinkSuggestion


class RealNoteConnectionProcessor:
    """Processes real notes for connection discovery and generates link suggestions"""

    def __init__(self, vault_path: str, quality_threshold: float = 0.5):
        """
        Initialize processor

        Args:
            vault_path: Path to vault directory
            quality_threshold: Minimum quality threshold for suggestions
        """
        self.vault_path = vault_path
        self.quality_threshold = quality_threshold
        self.connection_processor = RealConnectionProcessor(vault_path)
        self.suggestion_engine = LinkSuggestionEngine(vault_path, quality_threshold)

    def generate_suggestions_for_note(
        self, target_file: str, min_quality: float = None
    ) -> List[LinkSuggestion]:
        """
        Generate link suggestions for a target note using real connection discovery

        Args:
            target_file: Name of target note file
            min_quality: Optional minimum quality threshold

        Returns:
            List of LinkSuggestion objects
        """
        min_qual = min_quality or self.quality_threshold

        # Get real connections for the note
        connections = self.connection_processor.process_note_for_connections(
            target_file
        )

        if not connections:
            return []

        # Generate suggestions using LinkSuggestionEngine
        suggestions = self.suggestion_engine.generate_link_suggestions(
            target_note=target_file, connections=connections, min_quality=min_qual
        )

        return suggestions
