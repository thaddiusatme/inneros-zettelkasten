"""
Workflow Reporting Coordinator - ADR-002 Phase 10 Extraction

Coordinates workflow status reporting, AI feature usage analysis, and health assessment.
Extracted from WorkflowManager to maintain single responsibility and reduce class size.

This coordinator handles:
- Comprehensive workflow status reporting
- AI feature usage analysis across the vault
- Workflow health assessment (healthy/needs_attention/critical)
- Intelligent recommendation generation
"""

from pathlib import Path
from typing import Dict, List

from src.utils.frontmatter import parse_frontmatter


class WorkflowReportingCoordinator:
    """
    Coordinates workflow reporting and health assessment operations.

    ADR-002 Phase 10: Extracted from WorkflowManager (~120 LOC reduction).

    Responsibilities:
    - Generate comprehensive workflow status reports
    - Analyze AI feature usage across the vault
    - Assess workflow health status
    - Generate intelligent recommendations for workflow improvement

    Integration:
    - Uses NoteAnalytics for collection-wide analytics
    - Consumed by CLI layer (workflow_demo.py)
    - Independent of other coordinators
    """

    def __init__(self, base_dir: Path, analytics):
        """
        Initialize WorkflowReportingCoordinator.

        Args:
            base_dir: Base directory of the Zettelkasten vault
            analytics: NoteAnalytics instance for collection analysis
        """
        self.base_dir = Path(base_dir)
        self.analytics = analytics

        # Define standard directories
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.archive_dir = self.base_dir / "Archive"

    def generate_workflow_report(self) -> Dict:
        """
        Generate a comprehensive workflow status report.

        Returns:
            Dict containing:
                - workflow_status: Health, directory counts, total notes
                - ai_features: AI usage statistics
                - analytics: Collection analytics from NoteAnalytics
                - recommendations: List of workflow improvement suggestions
        """
        # Get analytics for the entire collection
        analytics_report = self.analytics.generate_report()

        # Count notes by directory
        directory_counts = self._count_notes_by_directory()

        # Assess workflow health
        workflow_health = self._assess_workflow_health(directory_counts)

        # Analyze AI feature usage
        ai_usage = self._analyze_ai_usage()

        # Generate recommendations
        recommendations = self._generate_workflow_recommendations(
            directory_counts, ai_usage
        )

        return {
            "workflow_status": {
                "health": workflow_health,
                "directory_counts": directory_counts,
                "total_notes": sum(directory_counts.values()),
            },
            "ai_features": ai_usage,
            "analytics": analytics_report,
            "recommendations": recommendations,
        }

    def _count_notes_by_directory(self) -> Dict[str, int]:
        """
        Count markdown notes in each workflow directory.

        Returns:
            Dictionary mapping directory names to note counts
        """
        directory_counts = {}

        for dir_name, dir_path in [
            ("Inbox", self.inbox_dir),
            ("Fleeting Notes", self.fleeting_dir),
            ("Permanent Notes", self.permanent_dir),
            ("Archive", self.archive_dir),
        ]:
            if dir_path.exists():
                directory_counts[dir_name] = len(list(dir_path.glob("*.md")))
            else:
                directory_counts[dir_name] = 0

        return directory_counts

    def _assess_workflow_health(self, directory_counts: Dict[str, int]) -> str:
        """
        Assess workflow health based on inbox backlog.

        Args:
            directory_counts: Directory note counts

        Returns:
            Health status: "healthy", "needs_attention", or "critical"
        """
        inbox_count = directory_counts.get("Inbox", 0)

        if inbox_count > 50:
            return "critical"
        elif inbox_count > 20:
            return "needs_attention"
        else:
            return "healthy"

    def _analyze_ai_usage(self) -> Dict:
        """
        Analyze usage of AI features across the collection.

        Scans all markdown notes in the vault and counts:
        - Notes with AI-generated tags (heuristic: kebab-case tags)
        - Notes with AI summaries
        - Notes with AI processing flags

        Returns:
            Dictionary with AI usage statistics
        """
        usage_stats = {
            "notes_with_ai_tags": 0,
            "notes_with_ai_summaries": 0,
            "notes_with_ai_processing": 0,
            "total_analyzed": 0,
        }

        # Scan all notes for AI features
        for md_file in self.base_dir.rglob("*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()

                frontmatter, _ = parse_frontmatter(content)
                usage_stats["total_analyzed"] += 1

                # Check for AI summary
                if "ai_summary" in frontmatter:
                    usage_stats["notes_with_ai_summaries"] += 1

                # Check for AI processing flag
                if "ai_processed" in frontmatter:
                    usage_stats["notes_with_ai_processing"] += 1

                # Check for AI-style tags (heuristic: kebab-case tags)
                tags = frontmatter.get("tags", [])
                if isinstance(tags, list) and len(tags) >= 3:
                    # Look for AI-style kebab-case tags
                    ai_style_tags = [t for t in tags if "-" in t and len(t) > 5]
                    if len(ai_style_tags) >= 2:
                        usage_stats["notes_with_ai_tags"] += 1

            except Exception:
                # Skip files that can't be read or parsed
                continue

        return usage_stats

    def _generate_workflow_recommendations(
        self, directory_counts: Dict[str, int], ai_usage: Dict
    ) -> List[str]:
        """
        Generate workflow improvement recommendations.

        Analyzes workflow state and AI adoption to suggest improvements:
        - Inbox management recommendations
        - AI feature adoption suggestions
        - Note type balance recommendations

        Args:
            directory_counts: Directory note counts
            ai_usage: AI usage statistics

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Inbox management recommendations
        inbox_count = directory_counts.get("Inbox", 0)
        if inbox_count > 20:
            recommendations.append(
                f"Process {inbox_count} notes in inbox - consider batch processing"
            )

        # AI feature adoption recommendations
        total_notes = ai_usage.get("total_analyzed", 0)
        if total_notes > 0:
            ai_summary_rate = ai_usage["notes_with_ai_summaries"] / total_notes
            if ai_summary_rate < 0.3:
                recommendations.append(
                    "Consider enabling auto-summarization for long notes"
                )

            ai_processing_rate = ai_usage["notes_with_ai_processing"] / total_notes
            if ai_processing_rate < 0.5:
                recommendations.append(
                    "Enable AI processing for inbox notes to improve workflow efficiency"
                )

        # Note type balance recommendations
        permanent_count = directory_counts.get("Permanent Notes", 0)
        fleeting_count = directory_counts.get("Fleeting Notes", 0)

        if fleeting_count > permanent_count * 2:
            recommendations.append(
                "Consider promoting more fleeting notes to permanent status"
            )

        return recommendations
