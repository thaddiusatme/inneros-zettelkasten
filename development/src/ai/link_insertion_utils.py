#!/usr/bin/env python3
"""
Link Insertion Utilities - TDD Iteration 4 (REFACTOR Phase)
Extracted utilities for modular link insertion architecture with safety-first operations
"""

import shutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Callable, Any

from .link_suggestion_utils import InsertionContextDetector


@dataclass
class InsertionResult:
    """Result of link insertion operation"""

    success: bool
    insertions_made: int
    duplicates_skipped: int = 0
    backup_path: Optional[str] = None
    error_message: Optional[str] = None
    auto_detected_locations: int = 0


class SafetyBackupManager:
    """Manages backup creation and restoration for safe file operations"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)
        self.backup_dir = self.vault_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def create_timestamped_backup(self, file_path: str) -> Path:
        """Create timestamped backup of file with collision prevention"""
        source_path = self.vault_path / file_path
        if not source_path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")

        # Generate unique backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = source_path.stem
        backup_name = f"{filename}_backup_{timestamp}.md"
        backup_path = self.backup_dir / backup_name

        # Handle filename collisions
        counter = 1
        while backup_path.exists():
            backup_name = f"{filename}_backup_{timestamp}_{counter}.md"
            backup_path = self.backup_dir / backup_name
            counter += 1

        # Copy file to backup location with metadata preservation
        shutil.copy2(source_path, backup_path)
        return backup_path

    def restore_from_backup(self, backup_path: Path, target_path: str):
        """Restore file from backup with integrity verification"""
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup not found: {backup_path}")

        target = self.vault_path / target_path
        shutil.copy2(backup_path, target)


class SmartInsertionProcessor:
    """Handles intelligent insertion of links into markdown content"""

    @staticmethod
    def insert_at_location(
        content: str,
        link_text: str,
        location: str,
        context: str,
        create_sections: bool = False,
    ) -> str:
        """
        Insert link at specified location with intelligent placement

        Args:
            content: Original note content
            link_text: Link text to insert (e.g., "[[Note Name]]")
            location: Where to insert ("related_concepts", "see_also", "main_content")
            context: Section heading or context for insertion
            create_sections: Create sections if they don't exist

        Returns:
            Modified content with link inserted
        """
        lines = content.split("\n")

        # Handle different insertion locations
        if location == "related_concepts":
            return SmartInsertionProcessor._insert_in_section(
                lines, link_text, "## Related Concepts", create_sections
            )
        elif location == "see_also":
            return SmartInsertionProcessor._insert_in_section(
                lines, link_text, "## See Also", create_sections
            )
        elif location == "main_content":
            return SmartInsertionProcessor._handle_main_content_insertion(
                lines, link_text, create_sections
            )

        return content  # Return original content if location not recognized

    @staticmethod
    def _insert_in_section(
        lines: List[str],
        link_text: str,
        section_header: str,
        create_sections: bool = False,
    ) -> str:
        """Insert link in specified section, creating it if necessary"""
        # Find existing section
        for i, line in enumerate(lines):
            if line.strip() == section_header:
                # Insert immediately after section header
                lines.insert(i + 1, f"- {link_text}")
                return "\n".join(lines)

        # Section doesn't exist - create it if requested
        if create_sections:
            lines.append("")
            lines.append(section_header)
            lines.append(f"- {link_text}")

        return "\n".join(lines)

    @staticmethod
    def _handle_main_content_insertion(
        lines: List[str], link_text: str, create_sections: bool = False
    ) -> str:
        """Handle insertion in main content area with section creation"""
        if create_sections:
            # Add a Related section at the end for better organization
            lines.append("")
            lines.append("## Related")
            lines.append(f"- {link_text}")
            return "\n".join(lines)
        else:
            # Insert after main heading or at end
            for i, line in enumerate(lines):
                if line.startswith("# ") and i < len(lines) - 1:
                    lines.insert(i + 2, f"- {link_text}")
                    return "\n".join(lines)
            # Fallback: insert at end
            lines.append(f"- {link_text}")
            return "\n".join(lines)


class ContentValidator:
    """Validates markdown content and link targets"""

    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)

    def validate_target_exists(self, target_note: str) -> bool:
        """Check if target note exists in vault"""
        target_path = self.vault_path / target_note
        return target_path.exists()

    def check_duplicate_link(self, content: str, link_text: str) -> bool:
        """Check if link already exists in content"""
        return link_text in content

    def validate_markdown_structure(self, content: str) -> bool:
        """Validate basic markdown structure integrity"""
        lines = content.split("\n")

        # Check for YAML frontmatter
        if not content.startswith("---"):
            return False

        # Check for main heading
        has_main_heading = any(line.startswith("# ") for line in lines)
        return has_main_heading


class BatchInsertionOrchestrator:
    """Orchestrates batch insertion operations with progress tracking"""

    @staticmethod
    def group_suggestions_by_note(suggestions: List[Any]) -> dict:
        """Group suggestions by source note for efficient batch processing"""
        suggestions_by_note = {}
        for suggestion in suggestions:
            note_path = suggestion.source_note
            if note_path not in suggestions_by_note:
                suggestions_by_note[note_path] = []
            suggestions_by_note[note_path].append(suggestion)
        return suggestions_by_note

    @staticmethod
    def execute_with_progress(
        suggestions_by_note: dict,
        insertion_func: Callable,
        progress_callback: Optional[Callable] = None,
    ) -> List[Any]:
        """Execute insertions with progress tracking and error handling"""
        results = []
        total_notes = len(suggestions_by_note)

        for i, (note_path, note_suggestions) in enumerate(suggestions_by_note.items()):
            if progress_callback:
                progress_callback(i / total_notes)

            try:
                result = insertion_func(note_path, note_suggestions)
                results.append(result)
            except Exception as e:
                # Create error result for failed insertion
                error_result = InsertionResult(
                    success=False,
                    insertions_made=0,
                    error_message=f"Batch insertion failed for {note_path}: {str(e)}",
                )
                results.append(error_result)

        return results


class LocationDetectionEnhancer:
    """Enhances location detection with auto-detection capabilities"""

    @staticmethod
    def auto_detect_insertion_location(content: str, suggestion: Any) -> tuple:
        """
        Auto-detect best insertion location using InsertionContextDetector

        Args:
            content: Note content to analyze
            suggestion: Suggestion object with location hints

        Returns:
            Tuple of (location, context) for insertion
        """
        if suggestion.suggested_location == "auto_detect":
            detected_location, detected_context = (
                InsertionContextDetector.detect_insertion_point(content, "related")
            )
            return detected_location, detected_context

        return suggestion.suggested_location, suggestion.insertion_context

    @staticmethod
    def optimize_insertion_strategy(content: str, suggestions: List[Any]) -> List[Any]:
        """Optimize insertion strategy based on content structure and suggestion types"""
        # Analyze content structure
        lines = content.split("\n")
        has_related_section = any("## Related" in line for line in lines)
        has_see_also_section = any("## See Also" in line for line in lines)

        optimized_suggestions = []

        for suggestion in suggestions:
            # Optimize location based on content structure
            if (
                suggestion.suggested_location == "related_concepts"
                and not has_related_section
            ):
                if has_see_also_section:
                    # Use existing See Also section instead
                    suggestion.suggested_location = "see_also"
                    suggestion.insertion_context = "## See Also"

            optimized_suggestions.append(suggestion)

        return optimized_suggestions
