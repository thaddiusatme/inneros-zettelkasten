#!/usr/bin/env python3
"""
End-to-End Link Processor - TDD Iteration 3 GREEN Phase
Complete workflow from real notes to link suggestions
"""

from typing import List
from .real_note_connection_processor import RealNoteConnectionProcessor
from .link_suggestion_engine import LinkSuggestion


class EndToEndLinkProcessor:
    """Complete end-to-end processor for link suggestions from real notes"""

    def __init__(self, vault_path: str):
        """
        Initialize end-to-end processor

        Args:
            vault_path: Path to vault directory
        """
        self.vault_path = vault_path
        self.processor = RealNoteConnectionProcessor(vault_path)

    def process_note_for_link_suggestions(
        self, target_note: str, min_quality: float = 0.6, max_results: int = 10
    ) -> List[LinkSuggestion]:
        """
        Process a note for complete link suggestions workflow

        Args:
            target_note: Name of target note file
            min_quality: Minimum quality threshold
            max_results: Maximum number of results

        Returns:
            List of LinkSuggestion objects
        """
        suggestions = self.processor.generate_suggestions_for_note(
            target_note, min_quality=min_quality
        )

        # Limit results
        return suggestions[:max_results]
