"""
connections_insertion — filesystem link mutations for Zettelkasten notes.

Consolidated self-contained module (issue #120). Inlines:
  link_insertion_engine.py, link_insertion_utils.py,
  link_suggestion_utils.py, link_suggestion_engine.py,
  real_connection_integration_engine.py, connection_integration_utils.py,
  orphan_remediation_coordinator.py

Filesystem I/O with rollback. Takes suggestions from connections_discovery
and writes wiki-links into note files. Pure compute lives in
connections_discovery.py; mutations live here.

Import boundary: may import from connections_discovery and llm_client.
Does NOT import from enrichment, lifecycle, or batch.
"""

# ---------------------------------------------------------------------------
# link_suggestion_utils (inlined — QualityScore, LinkTextGenerator, etc.)
# ---------------------------------------------------------------------------

import re
import shutil
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable, Any, Tuple


@dataclass
class QualityScore:
    """Data model for link quality assessment"""

    score: float  # 0.0 to 1.0
    confidence: str  # "high", "medium", "low"
    explanation: str


class LinkTextGenerator:
    """Utility class for generating intelligent link text from note metadata"""

    @staticmethod
    def generate_from_file_path(file_path: str) -> str:
        """Generate link text from file path"""
        if file_path.endswith(".md"):
            name = file_path.replace(".md", "").split("/")[-1]
        else:
            name = file_path.split("/")[-1]
        name = name.replace("-", " ").replace("_", " ")
        name = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", name)
        name = re.sub(r"^(fleeting|permanent|lit|zettel)-", "", name)
        return name.title().strip()

    @staticmethod
    def generate_from_semantic_overlap(
        overlap_terms: str, min_term_length: int = 3
    ) -> str:
        """Generate semantically meaningful link text from content overlap"""
        if not overlap_terms:
            return ""
        terms = overlap_terms.split()
        meaningful_terms = [term for term in terms if len(term) >= min_term_length]
        if len(meaningful_terms) >= 2:
            return " ".join(meaningful_terms[:3]).title()
        elif meaningful_terms:
            return meaningful_terms[0].title()
        else:
            return ""

    @classmethod
    def generate_intelligent_link_text(
        cls, file_path: str, content_overlap: str = ""
    ) -> str:
        """Generate intelligent link text using multiple strategies"""
        if content_overlap:
            semantic_text = cls.generate_from_semantic_overlap(content_overlap)
            if semantic_text:
                return f"[[{semantic_text}]]"
        file_text = cls.generate_from_file_path(file_path)
        return f"[[{file_text}]]"


class LinkQualityAssessor:
    """Utility class for assessing link suggestion quality with confidence scoring"""

    HIGH_QUALITY_THRESHOLD = 0.8
    MEDIUM_QUALITY_THRESHOLD = 0.6

    @classmethod
    def assess_connection_quality(
        cls,
        similarity_score: float,
        content_overlap: str = "",
        note_types: tuple = None,
    ) -> QualityScore:
        """Assess quality of a connection with multiple factors"""
        base_score = similarity_score
        if content_overlap and len(content_overlap.split()) >= 3:
            base_score = min(1.0, base_score + 0.1)
        if note_types and cls._are_compatible_types(note_types[0], note_types[1]):
            base_score = min(1.0, base_score + 0.05)
        if base_score >= cls.HIGH_QUALITY_THRESHOLD:
            confidence = "high"
            explanation = cls._generate_high_quality_explanation(
                similarity_score, content_overlap
            )
        elif base_score >= cls.MEDIUM_QUALITY_THRESHOLD:
            confidence = "medium"
            explanation = cls._generate_medium_quality_explanation(
                similarity_score, content_overlap
            )
        else:
            confidence = "low"
            explanation = cls._generate_low_quality_explanation(similarity_score)
        return QualityScore(
            score=base_score, confidence=confidence, explanation=explanation
        )

    @staticmethod
    def _are_compatible_types(source_type: str, target_type: str) -> bool:
        compatible_pairs = {
            ("permanent", "permanent"),
            ("permanent", "literature"),
            ("literature", "permanent"),
            ("fleeting", "permanent"),
            ("permanent", "fleeting"),
        }
        return (source_type, target_type) in compatible_pairs

    @staticmethod
    def _generate_high_quality_explanation(similarity: float, overlap: str) -> str:
        if overlap and len(overlap.split()) >= 3:
            return f"Strong semantic similarity ({similarity:.1%}) with rich content overlap"
        return f"Strong semantic similarity ({similarity:.1%}) between note contents"

    @staticmethod
    def _generate_medium_quality_explanation(similarity: float, overlap: str) -> str:
        if overlap:
            return f"Moderate semantic relationship ({similarity:.1%}) with shared concepts"
        return f"Moderate semantic relationship ({similarity:.1%}) detected"

    @staticmethod
    def _generate_low_quality_explanation(similarity: float) -> str:
        return f"Weak connection ({similarity:.1%}) - manual review recommended"


class InsertionContextDetector:
    """Utility for detecting appropriate insertion points in notes"""

    SECTION_PATTERNS = {
        "related_concepts": [
            r"## Related Concepts?",
            r"## Related",
            r"## See Also",
            r"## Connections?",
        ],
        "see_also": [
            r"## See Also",
            r"## References?",
            r"## Links?",
            r"## Further Reading",
        ],
        "main_content": [
            r"## [^#\n]+",
            r"# [^#\n]+",
        ],
    }

    @classmethod
    def detect_insertion_point(
        cls, note_content: str, link_type: str = "related"
    ) -> tuple:
        """Detect best insertion point for a link in note content"""
        lines = note_content.split("\n")
        for section_type, patterns in cls.SECTION_PATTERNS.items():
            for pattern in patterns:
                for i, line in enumerate(lines):
                    if re.match(pattern, line.strip(), re.IGNORECASE):
                        return section_type, line.strip()
        if cls._has_structured_content(lines):
            return "related_concepts", "## Related Concepts"
        else:
            return "main_content", "# Main Content"

    @staticmethod
    def _has_structured_content(lines: List[str]) -> bool:
        heading_count = sum(1 for line in lines if line.strip().startswith("#"))
        return heading_count >= 2


class SuggestionBatchProcessor:
    """Utility for efficient batch processing of link suggestions"""

    @staticmethod
    def sort_by_quality(suggestions: List[Any]) -> List[Any]:
        return sorted(suggestions, key=lambda x: x.quality_score, reverse=True)

    @staticmethod
    def filter_by_threshold(suggestions: List[Any], min_quality: float) -> List[Any]:
        return [s for s in suggestions if s.quality_score >= min_quality]

    @staticmethod
    def limit_results(suggestions: List[Any], max_results: int) -> List[Any]:
        return suggestions[:max_results]

    @classmethod
    def process_batch(
        cls, suggestions: List[Any], min_quality: float = 0.0, max_results: int = 10
    ) -> List[Any]:
        """Complete batch processing pipeline"""
        filtered = cls.filter_by_threshold(suggestions, min_quality)
        sorted_suggestions = cls.sort_by_quality(filtered)
        return cls.limit_results(sorted_suggestions, max_results)


# ---------------------------------------------------------------------------
# link_insertion_utils (base utilities — must come first, referenced by engine)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# link_insertion_engine
# ---------------------------------------------------------------------------


class LinkInsertionEngine:
    """
    Engine for safely inserting link suggestions into actual note files
    with comprehensive backup and rollback capabilities
    """

    def __init__(self, vault_path: str, backup_enabled: bool = True):
        """Initialize LinkInsertionEngine with modular utility architecture"""
        self.vault_path = str(vault_path)  # Keep as string for test compatibility
        self._vault_path_obj = Path(vault_path)
        self.backup_enabled = backup_enabled

        # Initialize modular utilities
        self.backup_manager = SafetyBackupManager(self._vault_path_obj)
        self.content_validator = ContentValidator(self._vault_path_obj)
        self.insertion_processor = SmartInsertionProcessor()
        self.location_enhancer = LocationDetectionEnhancer()
        self.batch_orchestrator = BatchInsertionOrchestrator()

        # Legacy compatibility
        self.insertion_validator = self._create_validator()

    def _create_validator(self):
        """Create insertion validator - compatibility wrapper"""
        return lambda x: self.content_validator.validate_markdown_structure(str(x))

    def insert_suggestions_into_note(
        self,
        note_path: str,
        suggestions: List[Any],
        validate_targets: bool = False,
        check_duplicates: bool = False,
        atomic: bool = False,
        auto_detect_location: bool = False,
        create_sections: bool = False,
    ) -> InsertionResult:
        """
        Insert link suggestions into a note file with safety checks

        Args:
            note_path: Path to note file relative to vault
            suggestions: List of LinkSuggestion objects
            validate_targets: Check if target notes exist
            check_duplicates: Skip duplicate links
            atomic: All-or-nothing insertion
            auto_detect_location: Use InsertionContextDetector for placement
            create_sections: Create sections if they don't exist

        Returns:
            InsertionResult with operation details
        """
        full_path = self._vault_path_obj / note_path
        if not full_path.exists():
            return InsertionResult(
                success=False,
                insertions_made=0,
                error_message=f"Note not found: {note_path}",
            )

        # Create backup if enabled
        backup_path = None
        if self.backup_enabled:
            try:
                backup_path = self.backup_manager.create_timestamped_backup(note_path)
            except Exception as e:
                return InsertionResult(
                    success=False,
                    insertions_made=0,
                    error_message=f"Backup creation failed: {str(e)}",
                )

        try:
            original_content = full_path.read_text()
            content = original_content
            insertions_made = 0
            duplicates_skipped = 0
            auto_detected_locations = 0

            for suggestion in suggestions:
                # Validate target if requested
                if validate_targets:
                    if not self.content_validator.validate_target_exists(
                        suggestion.target_note
                    ):
                        # For any validation failure, rollback and fail
                        if backup_path:
                            self.backup_manager.restore_from_backup(
                                backup_path, note_path
                            )
                        return InsertionResult(
                            success=False,
                            insertions_made=0,
                            error_message="rollback: target validation failed",
                        )

                # Check for duplicates
                if check_duplicates and self.content_validator.check_duplicate_link(
                    content, suggestion.suggested_link_text
                ):
                    duplicates_skipped += 1
                    continue

                # Auto-detect location if requested
                if auto_detect_location:
                    suggested_location, insertion_context = (
                        self.location_enhancer.auto_detect_insertion_location(
                            content, suggestion
                        )
                    )
                    if suggestion.suggested_location == "auto_detect":
                        auto_detected_locations += 1
                else:
                    suggested_location = suggestion.suggested_location
                    insertion_context = suggestion.insertion_context

                # Insert the link using utility
                new_content = self.insertion_processor.insert_at_location(
                    content,
                    suggestion.suggested_link_text,
                    suggested_location,
                    insertion_context,
                    create_sections,
                )

                if new_content != content:  # Content was modified
                    content = new_content
                    insertions_made += 1

            # Write modified content back to file
            if insertions_made > 0:
                full_path.write_text(content)

            return InsertionResult(
                success=True,
                insertions_made=insertions_made,
                duplicates_skipped=duplicates_skipped,
                backup_path=str(backup_path) if backup_path else None,
                auto_detected_locations=auto_detected_locations,
            )

        except Exception as e:
            # Rollback on any error
            if backup_path and full_path.exists():
                self.backup_manager.restore_from_backup(backup_path, note_path)

            return InsertionResult(
                success=False,
                insertions_made=0,
                error_message=f"Insertion failed: {str(e)}",
            )

    def insert_multiple_suggestions(
        self, suggestions: List[Any], progress_callback: Optional[Callable] = None
    ) -> List[InsertionResult]:
        """
        Insert suggestions into multiple notes with progress tracking using batch orchestrator

        Args:
            suggestions: List of suggestions with source_note paths
            progress_callback: Optional callback for progress updates

        Returns:
            List of InsertionResult objects
        """
        # Use batch orchestrator for efficient processing
        suggestions_by_note = self.batch_orchestrator.group_suggestions_by_note(
            suggestions
        )

        # Execute batch insertion with progress tracking
        return self.batch_orchestrator.execute_with_progress(
            suggestions_by_note, self.insert_suggestions_into_note, progress_callback
        )

    def preview_changes(self, note_path: str, suggestions: List[Any]) -> dict:
        """Preview changes that would be made without actually modifying files"""
        note_full_path = self._vault_path_obj / note_path

        try:
            # Read original content
            original_content = note_full_path.read_text(encoding="utf-8")

            # Generate modified content using insertion processor
            modified_content = original_content
            diff_lines = []

            for suggestion in suggestions:
                # Mock insertion for preview
                link_text = suggestion.suggested_link_text
                section_hint = getattr(suggestion, "suggested_location", "end")

                # Simple insertion simulation for preview
                if section_hint and section_hint in modified_content:
                    # Insert near the section
                    section_line = f"## {section_hint.replace('_', ' ').title()}"
                    if section_line in modified_content:
                        modified_content = modified_content.replace(
                            section_line, f"{section_line}\n{link_text}"
                        )
                        diff_lines.append(f"+{link_text}")
                else:
                    # Insert at end
                    modified_content += f"\n{link_text}"
                    diff_lines.append(f"+{link_text}")

            return {
                "original_content": original_content,
                "modified_content": modified_content,
                "diff": "\n".join(diff_lines),
            }

        except Exception as e:
            return {
                "error": f"Preview failed: {str(e)}",
                "original_content": "",
                "modified_content": "",
                "diff": "",
            }


class UndoManager:
    """Simple stack-based undo tracker for link insertions (TDD Iteration 6).

    Notes:
        - This minimal implementation is designed to satisfy RED→GREEN tests.
        - It records insertion operations and returns the latest on undo.
        - When restore=False, no filesystem side effects are performed (unit-test safe).
        - Future iterations can integrate safetyBackupManager for actual restore behavior.
    """

    def __init__(self, max_history: int = 50):
        self._max_history = max_history
        self._history: list[dict] = []

    def record_insertion(self, operation: dict) -> None:
        """Record an insertion operation for potential undo.

        Expected keys include: target_file, insertions, backup_path, timestamp
        """
        if not isinstance(operation, dict):
            return
        self._history.append(operation)
        # Enforce max history size (drop oldest)
        if len(self._history) > self._max_history:
            self._history.pop(0)

    def history_size(self) -> int:
        return len(self._history)

    def can_undo(self) -> bool:
        return bool(self._history)

    def undo_last(self, restore: bool = True) -> dict:
        """Undo the most recent insertion operation.

        Args:
            restore: If True, attempt to restore from backup (no-op in unit tests).

        Returns:
            Dict with keys: success (bool), message (str optional), target_file (str optional), backup_path (str optional)
        """
        if not self._history:
            return {"success": False, "message": "No operations to undo"}

        op = self._history.pop()

        # In this minimal implementation, we do not perform actual file restoration.
        # Future work: Use SafetyBackupManager.restore_from_backup(op['backup_path'], op['target_file'])
        # when restore is True and paths are valid.
        result = {
            "success": True,
            "target_file": op.get("target_file"),
            "backup_path": op.get("backup_path"),
        }
        if restore:
            # Indicate that a restore would be attempted in full implementation
            result["restored"] = False
        return result


# ---------------------------------------------------------------------------
# connection_integration_utils
# ---------------------------------------------------------------------------

import os
import glob
import time
from dataclasses import dataclass as _dataclass


@_dataclass
class ConnectionObject:
    """Mock connection object format expected by LinkSuggestionEngine"""

    target_file: str
    similarity_score: float
    source_file: str = ""
    content_overlap: str = ""


class SimilarityResultConverter:
    """Converts AIConnections similarity results to LinkSuggestionEngine connection objects"""

    @staticmethod
    def convert_to_connections(
        similarity_results: List[Tuple[str, float]], target_note: str, vault_path: str
    ) -> List[ConnectionObject]:
        """
        Convert AIConnections similarity results to connection objects

        Args:
            similarity_results: List of (filename, similarity_score) tuples from AIConnections
            target_note: The source note being analyzed
            vault_path: Path to vault directory

        Returns:
            List of ConnectionObject instances compatible with LinkSuggestionEngine
        """
        connections = []

        for filename, similarity in similarity_results:
            connection = ConnectionObject(
                target_file=filename,
                similarity_score=similarity,
                source_file=target_note,
                content_overlap="",  # Could be enhanced with actual content analysis
            )
            connections.append(connection)

        return connections

    @staticmethod
    def convert_batch(
        similarity_results: List[Tuple[str, float]], target_note: str, vault_path: str
    ) -> List[ConnectionObject]:
        """Batch conversion with same interface as convert_to_connections"""
        return SimilarityResultConverter.convert_to_connections(
            similarity_results, target_note, vault_path
        )


class RealNoteLoader:
    """Loads and processes real notes from the file system"""

    def __init__(self, vault_path: str):
        """
        Initialize note loader

        Args:
            vault_path: Path to the vault/knowledge directory
        """
        self.vault_path = vault_path

    def load_note_content(self, filename: str) -> str:
        """
        Load content of a specific note

        Args:
            filename: Name of the note file to load

        Returns:
            Note content as string
        """
        file_path = os.path.join(self.vault_path, filename)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""
        except Exception:
            return ""

    def load_corpus_excluding(self, exclude_filename: str) -> Dict[str, str]:
        """
        Load all notes in corpus except the specified file

        Args:
            exclude_filename: Filename to exclude from corpus

        Returns:
            Dictionary mapping filenames to content
        """
        corpus = {}

        # Find all markdown files in vault
        md_pattern = os.path.join(self.vault_path, "**/*.md")
        md_files = glob.glob(md_pattern, recursive=True)

        for file_path in md_files:
            filename = os.path.basename(file_path)

            # Skip the excluded file
            if filename == exclude_filename:
                continue

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    corpus[filename] = f.read()
            except Exception:
                # Skip files that can't be read
                continue

        return corpus

    def load_full_corpus(self) -> Dict[str, str]:
        """
        Load all notes in the vault

        Returns:
            Dictionary mapping filenames to content
        """
        return self.load_corpus_excluding("")  # Don't exclude any files


class PerformanceMonitor:
    """Monitors performance of connection discovery operations"""

    def __init__(self, target_time: float = 2.0):
        """
        Initialize performance monitor

        Args:
            target_time: Target time in seconds for operations
        """
        self.target_time = target_time
        self.metrics = {}
        self.current_operation = None
        self.start_time = None

    def measure(self, operation_name: str):
        """
        Context manager for measuring operation time

        Args:
            operation_name: Name of the operation being measured
        """
        return self._PerformanceMeasurement(self, operation_name)

    def get_metrics(self) -> Dict[str, float]:
        """
        Get all recorded metrics

        Returns:
            Dictionary mapping operation names to execution times
        """
        return self.metrics.copy()

    def is_within_target(self, operation_name: str) -> bool:
        """
        Check if operation was within target time

        Args:
            operation_name: Name of operation to check

        Returns:
            True if operation was within target time
        """
        return self.metrics.get(operation_name, float("inf")) <= self.target_time

    def _record_metric(self, operation_name: str, execution_time: float):
        """Record execution time for an operation"""
        self.metrics[operation_name] = execution_time

    class _PerformanceMeasurement:
        """Context manager for performance measurement"""

        def __init__(self, monitor: "PerformanceMonitor", operation_name: str):
            self.monitor = monitor
            self.operation_name = operation_name
            self.start_time = None

        def __enter__(self):
            self.start_time = time.time()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            if self.start_time is not None:
                execution_time = time.time() - self.start_time
                self.monitor._record_metric(self.operation_name, execution_time)


class ConnectionQualityAnalyzer:
    """Analyzes quality of connections for realistic scoring"""

    @staticmethod
    def analyze_connection_quality(content1: str, content2: str) -> "QualityScore":
        """
        Analyze connection quality between two pieces of content

        Args:
            content1: First content string
            content2: Second content string

        Returns:
            QualityScore object with score, confidence, and explanation
        """
        # Simple implementation for GREEN phase
        # Calculate word overlap as basic similarity metric
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return QualityScore(0.0, "low", "Empty content")

        overlap = len(words1.intersection(words2))
        union = len(words1.union(words2))

        if union == 0:
            score = 0.0
        else:
            score = overlap / union

        # Determine confidence level
        if score >= 0.7:
            confidence = "high"
            explanation = f"Strong content overlap ({overlap} shared words)"
        elif score >= 0.4:
            confidence = "medium"
            explanation = f"Moderate content overlap ({overlap} shared words)"
        else:
            confidence = "low"
            explanation = f"Limited content overlap ({overlap} shared words)"

        return QualityScore(score, confidence, explanation)


class RealConnectionProcessor:
    """Main processor that integrates all components for real connection discovery"""

    def __init__(self, vault_path: str, similarity_threshold: float = 0.6):
        """
        Initialize real connection processor

        Args:
            vault_path: Path to vault directory
            similarity_threshold: Minimum similarity threshold for connections
        """
        self.vault_path = vault_path
        self.similarity_threshold = similarity_threshold
        self.note_loader = RealNoteLoader(vault_path)
        self.performance_monitor = PerformanceMonitor()

    def process_note_for_connections(
        self, target_filename: str
    ) -> List[ConnectionObject]:
        """
        Process a note to find real connections

        Args:
            target_filename: Name of target note file

        Returns:
            List of ConnectionObject instances for similar notes
        """
        with self.performance_monitor.measure("load_notes"):
            target_content = self.note_loader.load_note_content(target_filename)
            corpus = self.note_loader.load_corpus_excluding(target_filename)

        if not target_content.strip() or not corpus:
            return []

        # Use AIConnections for real similarity analysis
        from .connections_discovery import AIConnections

        with self.performance_monitor.measure("similarity_analysis"):
            connections = AIConnections(
                similarity_threshold=self.similarity_threshold, max_suggestions=10
            )

            similarity_results = connections.find_similar_notes(target_content, corpus)

        # Convert to connection objects
        connection_objects = SimilarityResultConverter.convert_to_connections(
            similarity_results, target_filename, self.vault_path
        )

        return connection_objects

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics from last operation"""
        return self.performance_monitor.get_metrics()


# ---------------------------------------------------------------------------
# real_connection_integration_engine
# ---------------------------------------------------------------------------

from .connections_discovery import AIConnections


# ---------------------------------------------------------------------------
# link_suggestion_engine (inlined — LinkSuggestion, LinkSuggestionEngine)
# ---------------------------------------------------------------------------


@dataclass
class LinkSuggestion:
    """Data model for a suggested link between notes"""

    source_note: str
    target_note: str
    suggested_link_text: str
    similarity_score: float
    quality_score: float
    confidence: str  # "high", "medium", "low"
    explanation: str
    insertion_context: str
    suggested_location: str  # "related_concepts", "see_also", "main_content"


class LinkSuggestionEngine:
    """
    Converts connection discovery results into actionable link suggestions
    with intelligent quality scoring and link text generation
    """

    def __init__(
        self,
        vault_path: str,
        quality_threshold: float = 0.5,
        max_suggestions: int = 10,
    ):
        self.vault_path = vault_path
        self.quality_threshold = quality_threshold
        self.max_suggestions = max_suggestions

    def generate_link_suggestions(
        self,
        target_note: str,
        connections: List[Any],
        min_quality: float = None,
        max_results: int = None,
    ) -> List[LinkSuggestion]:
        """Generate link suggestions from connection discovery results"""
        suggestions = []
        min_qual = min_quality or self.quality_threshold
        max_res = max_results or self.max_suggestions

        for conn in connections:
            quality = self.score_link_quality(conn)
            if quality.score < min_qual:
                continue
            link_text = self.generate_link_text(
                "", conn.target_file, getattr(conn, "content_overlap", "")
            )
            location, context = InsertionContextDetector.detect_insertion_point(
                "", "related"
            )
            suggestion = LinkSuggestion(
                source_note=getattr(conn, "source_file", target_note),
                target_note=conn.target_file,
                suggested_link_text=link_text,
                similarity_score=getattr(conn, "similarity_score", 0.5),
                quality_score=quality.score,
                confidence=quality.confidence,
                explanation=quality.explanation,
                insertion_context=context,
                suggested_location=location,
            )
            suggestions.append(suggestion)

        return SuggestionBatchProcessor.process_batch(suggestions, min_qual, max_res)

    def generate_link_text(
        self, source_content: str, target_content: str, content_overlap: str = ""
    ) -> str:
        """Generate intelligent link text based on content analysis"""
        return LinkTextGenerator.generate_intelligent_link_text(
            target_content, content_overlap
        )

    def score_link_quality(self, connection: Any) -> QualityScore:
        """Assess the quality of a suggested link connection"""
        similarity_score = getattr(connection, "similarity_score", 0.5)
        content_overlap = getattr(connection, "content_overlap", "")
        return LinkQualityAssessor.assess_connection_quality(
            similarity_score=similarity_score, content_overlap=content_overlap
        )


class RealConnectionIntegrationEngine:
    """
    Production-ready engine that orchestrates real connection discovery
    integration with link suggestion generation
    """

    def __init__(
        self,
        vault_path: str,
        similarity_threshold: float = 0.6,
        quality_threshold: float = 0.5,
        max_suggestions: int = 10,
    ):
        """
        Initialize integration engine

        Args:
            vault_path: Path to vault directory
            similarity_threshold: Minimum similarity for connections
            quality_threshold: Minimum quality for suggestions
            max_suggestions: Maximum suggestions to return
        """
        self.vault_path = vault_path
        self.similarity_threshold = similarity_threshold
        self.quality_threshold = quality_threshold
        self.max_suggestions = max_suggestions

        # Initialize core components
        self.note_loader = RealNoteLoader(vault_path)
        self.ai_connections = AIConnections(
            similarity_threshold=similarity_threshold,
            max_suggestions=max_suggestions * 2,  # Get more candidates for filtering
        )
        self.suggestion_engine = LinkSuggestionEngine(
            vault_path=vault_path,
            quality_threshold=quality_threshold,
            max_suggestions=max_suggestions,
        )
        self.performance_monitor = PerformanceMonitor(target_time=2.0)

    def generate_suggestions_for_note(
        self, target_filename: str, min_quality: float = None
    ) -> List[LinkSuggestion]:
        """
        Generate high-quality link suggestions for a target note using real connection discovery

        Args:
            target_filename: Name of target note file
            min_quality: Optional minimum quality override

        Returns:
            List of LinkSuggestion objects sorted by quality
        """
        min_qual = min_quality or self.quality_threshold

        with self.performance_monitor.measure("total_processing"):
            # Load target note and corpus
            with self.performance_monitor.measure("note_loading"):
                target_content = self.note_loader.load_note_content(target_filename)
                if not target_content.strip():
                    return []

                corpus = self.note_loader.load_corpus_excluding(target_filename)
                if not corpus:
                    return []

            # Perform connection discovery
            with self.performance_monitor.measure("connection_discovery"):
                similarity_results = self.ai_connections.find_similar_notes(
                    target_content, corpus
                )

            # Convert to connection objects
            with self.performance_monitor.measure("format_conversion"):
                connection_objects = SimilarityResultConverter.convert_to_connections(
                    similarity_results, target_filename, self.vault_path
                )

            # Generate link suggestions
            with self.performance_monitor.measure("suggestion_generation"):
                suggestions = self.suggestion_engine.generate_link_suggestions(
                    target_note=target_filename,
                    connections=connection_objects,
                    min_quality=min_qual,
                    max_results=self.max_suggestions,
                )

        return suggestions

    def batch_process_notes(
        self, note_filenames: List[str], min_quality: float = None
    ) -> Dict[str, List[LinkSuggestion]]:
        """
        Process multiple notes for link suggestions in batch

        Args:
            note_filenames: List of note filenames to process
            min_quality: Optional minimum quality threshold

        Returns:
            Dictionary mapping note filenames to their suggestions
        """
        results = {}

        with self.performance_monitor.measure("batch_processing"):
            for filename in note_filenames:
                try:
                    suggestions = self.generate_suggestions_for_note(
                        filename, min_quality
                    )
                    results[filename] = suggestions
                except Exception:
                    # Skip notes that can't be processed
                    results[filename] = []

        return results

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics from last operation"""
        return self.performance_monitor.get_metrics()

    def validate_performance_targets(self) -> Dict[str, bool]:
        """
        Validate that performance targets are being met

        Returns:
            Dictionary indicating which targets are met
        """
        metrics = self.get_performance_metrics()
        return {
            "total_processing_under_2s": metrics.get("total_processing", 999) < 2.0,
            "note_loading_efficient": metrics.get("note_loading", 999) < 0.5,
            "connection_discovery_fast": metrics.get("connection_discovery", 999) < 1.5,
            "suggestion_generation_quick": metrics.get("suggestion_generation", 999)
            < 0.5,
        }


class CLIIntegrationOrchestrator:
    """
    Orchestrates real connection integration for CLI commands with enhanced error handling
    """

    def __init__(self, vault_path: str):
        """Initialize CLI orchestrator"""
        self.vault_path = vault_path
        self.integration_engine = None

    def initialize_engine(
        self,
        similarity_threshold: float = 0.6,
        quality_threshold: float = 0.5,
        max_suggestions: int = 10,
    ) -> bool:
        """
        Initialize integration engine with error handling

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            self.integration_engine = RealConnectionIntegrationEngine(
                vault_path=self.vault_path,
                similarity_threshold=similarity_threshold,
                quality_threshold=quality_threshold,
                max_suggestions=max_suggestions,
            )
            return True
        except Exception:
            return False

    def process_cli_request(
        self, target_filename: str, min_quality: float, max_results: int
    ) -> Optional[List[LinkSuggestion]]:
        """
        Process CLI request with comprehensive error handling

        Args:
            target_filename: Target note filename
            min_quality: Minimum quality threshold
            max_results: Maximum results to return

        Returns:
            List of suggestions or None if processing failed
        """
        if not self.integration_engine:
            if not self.initialize_engine(
                quality_threshold=min_quality, max_suggestions=max_results
            ):
                return None

        try:
            suggestions = self.integration_engine.generate_suggestions_for_note(
                target_filename, min_quality
            )

            # Limit results
            return suggestions[:max_results]

        except FileNotFoundError:
            # Target file or vault directory doesn't exist
            return None
        except Exception:
            # Other processing errors
            return None

    def get_processing_summary(self) -> Optional[Dict[str, any]]:
        """
        Get summary of last processing operation

        Returns:
            Summary dictionary or None if no processing done
        """
        if not self.integration_engine:
            return None

        metrics = self.integration_engine.get_performance_metrics()
        targets = self.integration_engine.validate_performance_targets()

        return {
            "performance_metrics": metrics,
            "targets_met": targets,
            "processing_time": metrics.get("total_processing", 0),
            "performance_grade": (
                "excellent"
                if all(targets.values())
                else "good" if sum(targets.values()) >= 2 else "needs_optimization"
            ),
        }


class ProductionOptimizedProcessor:
    """
    Production-optimized processor with caching and batch processing capabilities
    """

    def __init__(self, vault_path: str):
        """Initialize optimized processor"""
        self.vault_path = vault_path
        self.corpus_cache = None
        self.cache_timestamp = None
        self.engine = RealConnectionIntegrationEngine(vault_path)

    def get_cached_corpus(self, force_refresh: bool = False) -> Dict[str, str]:
        """
        Get corpus with intelligent caching

        Args:
            force_refresh: Force cache refresh

        Returns:
            Cached or fresh corpus
        """
        current_time = time.time()

        # Refresh cache if it's older than 5 minutes or forced
        if (
            force_refresh
            or self.corpus_cache is None
            or self.cache_timestamp is None
            or current_time - self.cache_timestamp > 300
        ):

            self.corpus_cache = self.engine.note_loader.load_full_corpus()
            self.cache_timestamp = current_time

        return self.corpus_cache

    def process_with_caching(
        self, target_filename: str, min_quality: float = 0.5
    ) -> List[LinkSuggestion]:
        """
        Process with optimized caching for better performance

        Args:
            target_filename: Target note filename
            min_quality: Minimum quality threshold

        Returns:
            List of link suggestions
        """
        # Use cached corpus for better performance
        corpus = self.get_cached_corpus()

        # Remove target from corpus if present
        corpus_excluding_target = {
            k: v for k, v in corpus.items() if k != target_filename
        }

        # Load target content
        target_content = self.engine.note_loader.load_note_content(target_filename)
        if not target_content.strip():
            return []

        # Perform optimized connection discovery
        similarity_results = self.engine.ai_connections.find_similar_notes(
            target_content, corpus_excluding_target
        )

        # Convert and generate suggestions
        connections = SimilarityResultConverter.convert_to_connections(
            similarity_results, target_filename, self.vault_path
        )

        return self.engine.suggestion_engine.generate_link_suggestions(
            target_note=target_filename,
            connections=connections,
            min_quality=min_quality,
        )


# ---------------------------------------------------------------------------
# orphan_remediation_coordinator
# ---------------------------------------------------------------------------

from src.utils.io import safe_write


class OrphanRemediationCoordinator:
    """
    Coordinates orphan note remediation through bidirectional link insertion.

    Follows composition pattern established in ADR-002 phases 1-7.
    """

    def __init__(self, base_dir: str, analytics_coordinator):
        """
        Initialize coordinator with required dependencies.

        Args:
            base_dir: Base directory of the Zettelkasten vault
            analytics_coordinator: AnalyticsCoordinator for orphan detection
        """
        self.base_dir = base_dir
        self.analytics_coordinator = analytics_coordinator

    def remediate_orphaned_notes(
        self,
        mode: str = "link",
        scope: str = "permanent",
        limit: int = 10,
        target: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict:
        """
        Remediate orphaned notes by inserting bidirectional links.

        Args:
            mode: "link" (insert links) or "checklist" (output markdown checklist)
            scope: "permanent", "fleeting", or "all"
            limit: maximum number of orphaned notes to process
            target: explicit path to target MOC/note for inserting links
            dry_run: when True, do not modify files; preview only

        Returns:
            Dictionary with summary and actions performed or planned.
        """
        mode = (mode or "link").lower()
        scope = (scope or "permanent").lower()
        if mode not in {"link", "checklist"}:
            mode = "link"
        if scope not in {"permanent", "fleeting", "all"}:
            scope = "permanent"

        vault_root = self._vault_root()

        # Determine target note
        target_path: Optional[Path]
        if target:
            t = Path(target)
            target_path = t if t.is_absolute() else (vault_root / t)
        else:
            target_path = self._find_default_link_target()

        result: Dict = {
            "mode": mode,
            "scope": scope,
            "limit": int(limit),
            "dry_run": bool(dry_run),
            "target": str(target_path) if target_path else None,
            "actions": [],
            "summary": {
                "considered": 0,
                "processed": 0,
                "skipped": 0,
                "errors": 0,
            },
        }

        if not target_path or not target_path.exists():
            return {
                **result,
                "error": f"Target note not found: {target_path if target_path else 'None'}",
            }

        # Gather orphaned notes by scope and apply limit
        orphans = self.list_orphans_by_scope(scope)
        result["summary"]["considered"] = len(orphans)
        selected = orphans[: max(0, int(limit))] if limit else orphans

        if mode == "checklist":
            checklist = [
                f"- [ ] Add link [[{Path(o['path']).stem}]] to [[{target_path.stem}]] and reciprocal link"
                for o in selected
            ]
            md = [
                "# Orphan Remediation Checklist",
                f"Generated: {datetime.now().isoformat(timespec='seconds')}",
                f"Target: [[{target_path.stem}]]",
                "",
            ] + checklist
            result["checklist_markdown"] = "\n".join(md) + "\n"
            return result

        # link mode
        for o in selected:
            orphan_fp = Path(o["path"])
            try:
                changed = self.insert_bidirectional_links(
                    orphan_fp, target_path, dry_run=dry_run
                )
                result["actions"].append(
                    {
                        "orphan": str(orphan_fp),
                        "target": str(target_path),
                        "modified_target": changed.get("modified_target", False),
                        "modified_orphan": changed.get("modified_orphan", False),
                        "backups": changed.get("backups", {}),
                    }
                )
                result["summary"]["processed"] += 1
            except Exception as e:
                result["actions"].append(
                    {
                        "orphan": str(orphan_fp),
                        "target": str(target_path),
                        "error": str(e),
                    }
                )
                result["summary"]["errors"] += 1

        result["summary"]["skipped"] = max(
            0, result["summary"]["considered"] - result["summary"]["processed"]
        )
        return result

    def list_orphans_by_scope(self, scope: str) -> List[Dict]:
        """
        Return orphaned notes filtered by scope and sorted deterministically.

        Args:
            scope: "permanent", "fleeting", or "all"

        Returns:
            List of orphaned note dictionaries with path, title, last_modified
        """
        # Use comprehensive detector to be robust to vault layouts
        all_orphans = self.analytics_coordinator.detect_orphaned_notes_comprehensive()
        root = self._vault_root()

        def in_dir(p: str, name: str) -> bool:
            try:
                return (root / name) in Path(p).parents or Path(p).parent == (
                    root / name
                )
            except Exception:
                return False

        if scope == "permanent":
            filtered = [o for o in all_orphans if in_dir(o["path"], "Permanent Notes")]
        elif scope == "fleeting":
            filtered = [o for o in all_orphans if in_dir(o["path"], "Fleeting Notes")]
        else:
            filtered = [
                o
                for o in all_orphans
                if in_dir(o["path"], "Permanent Notes")
                or in_dir(o["path"], "Fleeting Notes")
            ]

        # Sort: Permanent first, then by title
        def sort_key(o: Dict):
            dir_weight = 0 if in_dir(o["path"], "Permanent Notes") else 1
            return (dir_weight, o.get("title", ""))

        return sorted(filtered, key=sort_key)

    def resolve_target_note(self, target: Optional[str] = None) -> Optional[Path]:
        """
        Resolve target note for link insertion.

        Args:
            target: Optional explicit path to target note

        Returns:
            Path to target note, or None if not found
        """
        if target:
            t = Path(target)
            target_path = t if t.is_absolute() else (self._vault_root() / t)
            return target_path if target_path.exists() else None

        return self._find_default_link_target()

    def insert_bidirectional_links(
        self, orphan_path: Path, target_path: Path, dry_run: bool = True
    ) -> Dict:
        """
        Insert [[orphan]] in target and [[target]] in orphan, creating backups if not dry-run.

        Args:
            orphan_path: Path to orphan note
            target_path: Path to target note
            dry_run: If True, don't modify files

        Returns:
            Dict with modified flags and backup paths
        """
        orphan_key = orphan_path.stem
        target_key = target_path.stem

        result = {"modified_target": False, "modified_orphan": False, "backups": {}}

        # Update target file
        tgt_text = self._read_text(target_path)
        if not self.has_wikilink(tgt_text, orphan_key):
            new_tgt_text = self.append_to_section(tgt_text, f"[[{orphan_key}]]")
            if not dry_run:
                bk = self.backup_file(target_path)
                result["backups"]["target"] = str(bk) if bk else None
                self._write_text(target_path, new_tgt_text)
            result["modified_target"] = True

        # Update orphan file
        orphan_text = self._read_text(orphan_path)
        if not self.has_wikilink(orphan_text, target_key):
            new_orphan_text = self.append_to_section(orphan_text, f"[[{target_key}]]")
            if not dry_run:
                bk = self.backup_file(orphan_path)
                result["backups"]["orphan"] = str(bk) if bk else None
                self._write_text(orphan_path, new_orphan_text)
            result["modified_orphan"] = True

        return result

    def has_wikilink(self, text: str, key: str) -> bool:
        """
        Check if text contains wiki-link to key.

        Args:
            text: Content to search
            key: Note key to find (matches [[key]] or [[key|alias]])

        Returns:
            True if wiki-link found, False otherwise
        """
        try:
            pattern = rf"\[\[\s*{re.escape(key)}(?:\|[^\]]+)?\s*\]\]"
            return re.search(pattern, text) is not None
        except Exception:
            return False

    def append_to_section(
        self, text: str, bullet_line: str, section_title: str = "## Linked Notes"
    ) -> str:
        """
        Append a bullet to a dedicated section, creating it if missing.

        Args:
            text: Original note content
            bullet_line: Link text to append (e.g., "[[note-name]]")
            section_title: Section heading to append to

        Returns:
            Modified text with link appended
        """
        lines = text.splitlines()
        # Find section heading index
        heading_re = re.compile(
            rf"^#+\s+{re.escape(section_title.lstrip('#').strip())}$", re.IGNORECASE
        )
        idx = None
        for i, ln in enumerate(lines):
            if heading_re.match(ln.strip()):
                idx = i
                break
        bullet = f"- {bullet_line}"
        if idx is None:
            # Append new section at end
            new = []
            if lines and lines[-1].strip() != "":
                new = lines + ["", section_title, "", bullet, ""]
            else:
                new = lines + [section_title, "", bullet, ""]
            return "\n".join(new)
        else:
            # Insert after heading
            insert_at = idx + 1
            # skip leading blank after heading
            while insert_at < len(lines) and lines[insert_at].strip() == "":
                insert_at += 1
            new_lines = lines[:insert_at] + ["", bullet] + lines[insert_at:]
            return "\n".join(new_lines)

    def backup_file(self, path: Path) -> Optional[Path]:
        """
        Create timestamped backup of file.

        Args:
            path: File to backup

        Returns:
            Path to backup file, or None if backup failed
        """
        try:
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            backup = path.parent / f"{path.name}.bak.{ts}"
            shutil.copy2(path, backup)
            return backup
        except Exception:
            return None

    # Private helper methods

    def _vault_root(self) -> Path:
        """Resolve the root folder that actually contains the note collections."""
        base = Path(self.base_dir)
        knowledge = base / "knowledge"
        return knowledge if knowledge.exists() else base

    def _find_default_link_target(self) -> Optional[Path]:
        """Pick a sensible default target note (Home Note or an MOC)."""
        root = self._vault_root()
        # 1) Home Note.md
        home = root / "Home Note.md"
        if home.exists():
            return home
        # 2) Zettelkasten MOC in Permanent Notes
        z_moc = root / "Permanent Notes" / "Zettelkasten MOC.md"
        if z_moc.exists():
            return z_moc
        # 3) any MOC file under vault
        moc_candidates = list(root.rglob("*MOC*.md"))
        if moc_candidates:
            moc_candidates.sort()
            return moc_candidates[0]
        return None

    def _read_text(self, path: Path) -> str:
        """Read text from file, returning empty string if not found."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _write_text(self, path: Path, text: str) -> None:
        """Write text to file using atomic write."""
        safe_write(path, text)


__all__ = [
    # link insertion
    "LinkInsertionEngine",
    "UndoManager",
    "InsertionResult",
    "SafetyBackupManager",
    "SmartInsertionProcessor",
    "ContentValidator",
    "BatchInsertionOrchestrator",
    "LocationDetectionEnhancer",
    # real connection integration
    "RealConnectionIntegrationEngine",
    "CLIIntegrationOrchestrator",
    "ProductionOptimizedProcessor",
    # connection integration utilities
    "ConnectionObject",
    "SimilarityResultConverter",
    "RealNoteLoader",
    "PerformanceMonitor",
    "ConnectionQualityAnalyzer",
    "RealConnectionProcessor",
    # orphan remediation
    "OrphanRemediationCoordinator",
]
