"""
Analytics Coordinator for Zettelkasten workflow management.

This module handles analytics and metrics calculations including:
- Orphaned note detection (bidirectional link analysis)
- Stale note detection (age-based analysis)
- Enhanced metrics generation (link density, age distribution, productivity)
- Link graph construction and analysis

Extracted from WorkflowManager as part of ADR-002 Phase 3 decomposition.
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict
import re

from src.config.vault_config_loader import get_vault_config


class AnalyticsCoordinator:
    """
    Coordinates analytics and metrics operations for note collections.

    Responsibilities:
    - Detect orphaned notes (no incoming/outgoing links)
    - Detect stale notes (not modified within threshold)
    - Generate comprehensive enhanced metrics
    - Build and analyze link graphs
    - Calculate productivity metrics

    This class follows the Single Responsibility Principle by focusing
    exclusively on analytics and metrics calculation.
    """

    def __init__(self, base_dir: Path, workflow_manager=None):
        """
        Initialize AnalyticsCoordinator.

        Args:
            base_dir: Base directory of the vault (vault config loads from here)
            workflow_manager: WorkflowManager instance (optional, for future use)
            
        Note:
            Directory paths loaded from vault_config.yaml in knowledge/ subdirectory.
            Part of GitHub Issue #45 - Vault Configuration Centralization.
        """
        self.base_dir = Path(base_dir)
        self.workflow_manager = workflow_manager
        
        # Load vault configuration for directory paths
        vault_config = get_vault_config(str(self.base_dir))
        self.inbox_dir = vault_config.inbox_dir
        self.fleeting_dir = vault_config.fleeting_dir
        self.permanent_dir = vault_config.permanent_dir

    def detect_orphaned_notes(self) -> List[Dict]:
        """
        Detect notes that have no bidirectional links to other notes.

        Orphaned notes are permanent notes that:
        - Are not linked to by any other notes
        - Do not link to any other notes

        Returns:
            List of orphaned note dictionaries with path, title, last_modified
        """
        orphaned_notes = []
        all_notes = self._get_all_notes()
        link_graph = self._build_link_graph(all_notes)

        for note_path in all_notes:
            if self._is_orphaned_note(note_path, link_graph):
                orphaned_notes.append(self._create_orphaned_note_info(note_path))

        return orphaned_notes

    def detect_orphaned_notes_comprehensive(self) -> List[Dict]:
        """
        Detect orphaned notes across the entire repository (not just workflow directories).

        This scans ALL markdown files in the repository, not just Inbox/Fleeting/Permanent.
        Use this for a complete view of isolated notes in your knowledge graph.

        Returns:
            List of orphaned note dictionaries with path, title, last_modified
        """
        orphaned_notes = []
        all_notes = self._get_all_notes_comprehensive()
        link_graph = self._build_link_graph(all_notes)

        for note_path in all_notes:
            if self._is_orphaned_note(note_path, link_graph):
                orphaned_notes.append(self._create_orphaned_note_info(note_path))

        return orphaned_notes

    def detect_stale_notes(self, days_threshold: int = 90) -> List[Dict]:
        """
        Detect notes that haven't been modified in a specified time period.

        Args:
            days_threshold: Number of days to consider a note stale (default: 90)

        Returns:
            List of stale note dictionaries with path, title, last_modified, days_since_modified
        """
        stale_notes = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        all_notes = self._get_all_notes()

        for note_path in all_notes:
            try:
                last_modified = datetime.fromtimestamp(note_path.stat().st_mtime)
                if last_modified < cutoff_date:
                    days_since_modified = (datetime.now() - last_modified).days
                    stale_notes.append(
                        self._create_stale_note_info(
                            note_path, last_modified, days_since_modified
                        )
                    )
            except (OSError, AttributeError):
                # Skip if we can't get file stats
                continue

        # Sort by days since modified (most stale first)
        stale_notes.sort(key=lambda x: x["days_since_modified"], reverse=True)
        return stale_notes

    def generate_enhanced_metrics(self) -> Dict:
        """
        Generate comprehensive metrics for weekly review including orphaned notes,
        stale notes, and advanced analytics.

        Returns:
            Dictionary with enhanced metrics:
            - orphaned_notes: List of orphaned notes
            - stale_notes: List of stale notes
            - link_density: Average links per note
            - note_age_distribution: Distribution of note ages
            - productivity_metrics: Creation and modification patterns
        """
        metrics = {
            "generated_at": datetime.now().isoformat(),
            "orphaned_notes": self.detect_orphaned_notes(),
            "stale_notes": self.detect_stale_notes(),
            "link_density": self._calculate_link_density(),
            "note_age_distribution": self._calculate_note_age_distribution(),
            "productivity_metrics": self._calculate_productivity_metrics(),
        }

        # Add summary statistics
        metrics["summary"] = {
            "total_orphaned": len(metrics["orphaned_notes"]),
            "total_stale": len(metrics["stale_notes"]),
            "avg_links_per_note": metrics["link_density"],
            "total_notes": len(self._get_all_notes()),
        }

        return metrics

    # Helper methods for internal operations

    def _get_all_notes(self) -> List[Path]:
        """Get all markdown notes from workflow directories."""
        all_notes = []
        directories = [self.permanent_dir, self.fleeting_dir, self.inbox_dir]

        for directory in directories:
            if directory.exists():
                all_notes.extend(directory.glob("*.md"))

        return all_notes

    def _get_all_notes_comprehensive(self) -> List[Path]:
        """Get all markdown notes from the entire repository."""
        root_dir = Path(self.base_dir)
        return list(root_dir.rglob("*.md"))

    def _build_link_graph(self, all_notes: List[Path]) -> Dict[str, set]:
        """
        Build a graph of note links.

        Args:
            all_notes: List of note paths to analyze

        Returns:
            Dictionary mapping note names to sets of linked note names
        """
        link_graph = {}

        for note_path in all_notes:
            note_name = note_path.stem
            link_graph[note_name] = set()

            try:
                with open(note_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find all [[wiki-style]] links
                wiki_links = re.findall(r"\[\[([^\]]+)\]\]", content)
                for link in wiki_links:
                    # Clean up the link (remove .md extension if present)
                    clean_link = link.replace(".md", "")
                    link_graph[note_name].add(clean_link)

            except (UnicodeDecodeError, FileNotFoundError):
                continue

        return link_graph

    def _is_orphaned_note(self, note_path: Path, link_graph: Dict[str, set]) -> bool:
        """
        Check if a note is orphaned (no incoming or outgoing links).

        Args:
            note_path: Path to the note to check
            link_graph: Complete link graph for all notes

        Returns:
            True if note is orphaned, False otherwise
        """
        note_name = note_path.stem

        # Skip inbox notes (they're expected to be unlinked initially)
        if note_path.parent.name == "Inbox":
            return False

        # Check if note has outgoing links
        has_outgoing_links = len(link_graph.get(note_name, set())) > 0

        # Check if note has incoming links
        has_incoming_links = any(
            note_name in links
            for other_note, links in link_graph.items()
            if other_note != note_name
        )

        return not (has_outgoing_links or has_incoming_links)

    def _create_orphaned_note_info(self, note_path: Path) -> Dict:
        """Create info dict for an orphaned note."""
        try:
            last_modified = datetime.fromtimestamp(note_path.stat().st_mtime)
            title = self._extract_note_title(note_path)
        except (OSError, AttributeError):
            last_modified = None
            title = note_path.stem

        return {
            "path": str(note_path),
            "title": title,
            "last_modified": last_modified.isoformat() if last_modified else None,
            "directory": note_path.parent.name,
        }

    def _create_stale_note_info(
        self, note_path: Path, last_modified: datetime, days_since_modified: int
    ) -> Dict:
        """Create info dict for a stale note."""
        title = self._extract_note_title(note_path)

        return {
            "path": str(note_path),
            "title": title,
            "last_modified": last_modified.isoformat(),
            "days_since_modified": days_since_modified,
            "directory": note_path.parent.name,
        }

    def _extract_note_title(self, note_path: Path) -> str:
        """Extract title from note (first # heading or filename)."""
        try:
            with open(note_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Look for first markdown heading
            heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if heading_match:
                return heading_match.group(1).strip()

            # Fall back to filename
            return note_path.stem

        except (UnicodeDecodeError, FileNotFoundError):
            return note_path.stem

    def _calculate_link_density(self) -> float:
        """Calculate average number of links per note."""
        all_notes = self._get_all_notes()
        if not all_notes:
            return 0.0

        link_graph = self._build_link_graph(all_notes)
        total_links = sum(len(links) for links in link_graph.values())

        return total_links / len(all_notes) if all_notes else 0.0

    def _calculate_note_age_distribution(self) -> Dict:
        """Calculate distribution of note ages."""
        all_notes = self._get_all_notes()
        age_buckets = {
            "new": 0,  # < 7 days
            "recent": 0,  # 7-30 days
            "mature": 0,  # 30-90 days
            "old": 0,  # > 90 days
        }

        now = datetime.now()

        for note_path in all_notes:
            try:
                created_time = datetime.fromtimestamp(note_path.stat().st_ctime)
                age_days = (now - created_time).days

                if age_days < 7:
                    age_buckets["new"] += 1
                elif age_days < 30:
                    age_buckets["recent"] += 1
                elif age_days < 90:
                    age_buckets["mature"] += 1
                else:
                    age_buckets["old"] += 1

            except (OSError, AttributeError):
                age_buckets["old"] += 1  # Default to old if we can't get creation time

        return age_buckets

    def _calculate_productivity_metrics(self) -> Dict:
        """Calculate productivity metrics like notes per week."""
        all_notes = self._get_all_notes()
        weekly_creation = defaultdict(int)
        weekly_modification = defaultdict(int)

        for note_path in all_notes:
            try:
                created_time = datetime.fromtimestamp(note_path.stat().st_ctime)
                modified_time = datetime.fromtimestamp(note_path.stat().st_mtime)

                # Get week start (Monday) for creation and modification
                created_week = created_time.strftime("%Y-W%U")
                modified_week = modified_time.strftime("%Y-W%U")

                weekly_creation[created_week] += 1
                weekly_modification[modified_week] += 1

            except (OSError, AttributeError):
                continue

        # Calculate averages
        creation_counts = list(weekly_creation.values())
        modification_counts = list(weekly_modification.values())

        return {
            "avg_notes_created_per_week": (
                sum(creation_counts) / len(creation_counts) if creation_counts else 0
            ),
            "avg_notes_modified_per_week": (
                sum(modification_counts) / len(modification_counts)
                if modification_counts
                else 0
            ),
            "most_productive_week_creation": (
                max(weekly_creation.items(), key=lambda x: x[1])
                if weekly_creation
                else None
            ),
            "total_weeks_active": len(
                set(list(weekly_creation.keys()) + list(weekly_modification.keys()))
            ),
        }
