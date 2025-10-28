"""
GREEN PHASE: FleetingAnalysisCoordinator - Extracted from WorkflowManager.

ADR-002 Phase 9: Extract fleeting note analysis functionality from WorkflowManager
into dedicated coordinator following proven composition pattern from Phases 1-8.

Responsibilities:
- Analyze fleeting notes collection for age distribution
- Generate health reports with actionable recommendations
- Coordinate fleeting note lifecycle management

Pattern: Composition over inheritance, dependency injection for testability.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, field

from src.utils.frontmatter import parse_frontmatter


@dataclass
class FleetingAnalysis:
    """Data structure for fleeting note analysis results."""

    total_count: int = 0
    age_distribution: Dict[str, int] = field(
        default_factory=lambda: {
            "new": 0,  # 0-7 days
            "recent": 0,  # 8-30 days
            "stale": 0,  # 31-90 days
            "old": 0,  # 90+ days
        }
    )
    oldest_note: Optional[Dict[str, any]] = None
    newest_note: Optional[Dict[str, any]] = None
    notes_by_age: List[Dict[str, any]] = field(default_factory=list)


class FleetingAnalysisCoordinator:
    """
    Coordinates fleeting note analysis and health reporting.

    Extracted from WorkflowManager (ADR-002 Phase 9) to reduce god class complexity.
    Handles age categorization, statistics aggregation, and health report generation.
    """

    def __init__(self, fleeting_dir: Path):
        """
        Initialize FleetingAnalysisCoordinator.

        Args:
            fleeting_dir: Path to fleeting notes directory

        Raises:
            TypeError: If fleeting_dir is None
            ValueError: If fleeting_dir is invalid
        """
        if fleeting_dir is None:
            raise TypeError("fleeting_dir cannot be None")

        if not isinstance(fleeting_dir, Path):
            fleeting_dir = Path(fleeting_dir)

        self.fleeting_dir = fleeting_dir

    def analyze_fleeting_notes(self) -> FleetingAnalysis:
        """
        Analyze fleeting notes collection for age distribution and health metrics.

        Returns:
            FleetingAnalysis: Data structure with age analysis results
        """
        analysis = FleetingAnalysis()
        notes_data = []

        # Scan fleeting notes directory
        if not self.fleeting_dir.exists():
            return analysis

        current_date = datetime.now()

        for note_path in self.fleeting_dir.glob("*.md"):
            try:
                # Get note age from metadata or file stats
                content = note_path.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(content)

                # Try to get created date from frontmatter
                created_str = frontmatter.get("created", "")
                if created_str and not any(
                    placeholder in created_str for placeholder in ["{{", "<%", "tp."]
                ):
                    # Parse the date
                    try:
                        created_date = datetime.strptime(created_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        try:
                            created_date = datetime.strptime(created_str, "%Y-%m-%d")
                        except ValueError:
                            # Fall back to file modification time
                            created_date = datetime.fromtimestamp(
                                note_path.stat().st_mtime
                            )
                else:
                    # Use file modification time as fallback
                    created_date = datetime.fromtimestamp(note_path.stat().st_mtime)

                # Calculate age in days
                age_delta = current_date - created_date
                days_old = age_delta.days

                # Store note data
                note_info = {
                    "name": note_path.name,
                    "path": str(note_path),
                    "days_old": days_old,
                    "created": created_date,
                }
                notes_data.append(note_info)

                # Categorize by age
                if days_old <= 7:
                    analysis.age_distribution["new"] += 1
                elif days_old <= 30:
                    analysis.age_distribution["recent"] += 1
                elif days_old <= 90:
                    analysis.age_distribution["stale"] += 1
                else:
                    analysis.age_distribution["old"] += 1

            except Exception:
                # Skip notes that can't be processed
                continue

        # Sort notes by age
        notes_data.sort(key=lambda x: x["days_old"], reverse=True)

        # Set analysis results
        analysis.total_count = len(notes_data)
        analysis.notes_by_age = notes_data

        if notes_data:
            analysis.oldest_note = notes_data[0]
            analysis.newest_note = notes_data[-1]

        return analysis

    def generate_fleeting_health_report(self) -> Dict:
        """
        Generate a health report for fleeting notes with recommendations.

        Returns:
            Dict: Health report with status, distribution, and recommendations
        """
        # Get analysis
        analysis = self.analyze_fleeting_notes()

        # Calculate health status
        if analysis.total_count == 0:
            health_status = "HEALTHY"
            summary = "No fleeting notes found. Your fleeting notes are well-managed."
        else:
            old_percentage = (
                (analysis.age_distribution["old"] / analysis.total_count * 100)
                if analysis.total_count > 0
                else 0
            )
            stale_percentage = (
                (analysis.age_distribution["stale"] / analysis.total_count * 100)
                if analysis.total_count > 0
                else 0
            )

            if old_percentage >= 50:
                health_status = "CRITICAL"
                summary = f"Critical: {old_percentage:.0f}% of fleeting notes are over 90 days old and require immediate attention."
            elif old_percentage >= 30 or stale_percentage >= 40:
                health_status = "ATTENTION"
                summary = f"Attention needed: {stale_percentage + old_percentage:.0f}% of fleeting notes are stale or old."
            else:
                health_status = "HEALTHY"
                summary = f'Healthy: Most fleeting notes ({analysis.age_distribution["new"] + analysis.age_distribution["recent"]}/{analysis.total_count}) are being actively processed.'

        # Generate recommendations
        recommendations = []
        if analysis.age_distribution["old"] > 0:
            recommendations.append(
                f"Process {analysis.age_distribution['old']} old notes (90+ days) for promotion or archival"
            )
        if analysis.age_distribution["stale"] > 0:
            recommendations.append(
                f"Review {analysis.age_distribution['stale']} stale notes (31-90 days) for relevance"
            )
        if analysis.total_count > 20:
            recommendations.append(
                "Consider batch processing to reduce fleeting note backlog"
            )
        if analysis.age_distribution["new"] == 0 and analysis.total_count > 0:
            recommendations.append(
                "No new notes in the last week - consider if capture process is working"
            )

        # Get oldest notes for priority processing
        oldest_notes = (
            analysis.notes_by_age[:5]
            if len(analysis.notes_by_age) >= 5
            else analysis.notes_by_age
        )

        # Get newest notes to show recent activity
        newest_notes = (
            analysis.notes_by_age[-5:]
            if len(analysis.notes_by_age) >= 5
            else analysis.notes_by_age
        )
        newest_notes.reverse()  # Show newest first

        return {
            "summary": summary,
            "health_status": health_status,
            "total_count": analysis.total_count,
            "age_distribution": analysis.age_distribution,
            "recommendations": (
                recommendations
                if recommendations
                else ["Keep up the good work maintaining your fleeting notes!"]
            ),
            "oldest_notes": oldest_notes,
            "newest_notes": newest_notes,
            "oldest_note": analysis.oldest_note,
            "newest_note": analysis.newest_note,
        }
