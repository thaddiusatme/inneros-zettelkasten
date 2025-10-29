#!/usr/bin/env python3
"""
Fleeting Notes Formatter - Display and export formatting for fleeting notes reports

Extracted from fleeting_cli.py to maintain single responsibility and keep CLI under 400 LOC.
Handles all display formatting and markdown export functionality.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict


class FleetingFormatter:
    """
    Formatter for fleeting notes health and triage reports

    Responsibilities:
    - Format health reports for console display
    - Format triage reports for console display
    - Export reports to markdown format
    - Consistent section formatting
    """

    def display_health_report(self, health_report: Dict) -> str:
        """
        Display fleeting notes health report to console.

        Args:
            health_report: Health report dictionary from WorkflowManager

        Returns:
            Formatted string for console output
        """
        lines = []

        # Health status with emoji
        status_emoji = {"HEALTHY": "✅", "ATTENTION": "⚠️", "CRITICAL": "🚨"}

        status = health_report["health_status"]
        lines.append(f"   Health Status: {status_emoji.get(status, '❓')} {status}")
        lines.append(f"   Total Notes: {health_report['total_count']}")

        # Age distribution
        lines.append("\nAGE DISTRIBUTION")
        lines.append("-" * 16)
        distribution = health_report["age_distribution"]
        lines.append(f"   New (0-7 days):     {distribution['new']:>3}")
        lines.append(f"   Recent (8-30 days): {distribution['recent']:>3}")
        lines.append(f"   Stale (31-90 days): {distribution['stale']:>3}")
        lines.append(f"   Old (90+ days):     {distribution['old']:>3}")

        # Summary
        lines.append("\nSUMMARY")
        lines.append("-" * 7)
        lines.append(f"   {health_report['summary']}")

        # Recommendations
        lines.append("\nRECOMMENDATIONS")
        lines.append("-" * 15)
        for i, rec in enumerate(health_report["recommendations"], 1):
            lines.append(f"   {i}. {rec}")

        # Show oldest notes if any
        if health_report.get("oldest_notes"):
            lines.append("\nOLDEST NOTES (Priority Processing)")
            lines.append("-" * 35)
            for note in health_report["oldest_notes"][:3]:  # Show top 3
                created = note["created"]
                if isinstance(created, str):
                    created = datetime.fromisoformat(created)
                age_days = (datetime.now() - created).days
                lines.append(f"   📄 {note['name']} ({age_days} days old)")

        return "\n".join(lines)

    def format_health_markdown(self, health_report: Dict) -> str:
        """
        Format fleeting health report as markdown for export.

        Args:
            health_report: Health report dictionary from WorkflowManager

        Returns:
            Markdown formatted string
        """
        lines = []

        # Status
        status = health_report["health_status"]
        lines.append(f"**Health Status:** {status}")
        lines.append(f"**Total Notes:** {health_report['total_count']}")
        lines.append("")

        # Age distribution
        lines.append("## Age Distribution")
        distribution = health_report["age_distribution"]
        lines.append(f"- New (0-7 days): {distribution['new']}")
        lines.append(f"- Recent (8-30 days): {distribution['recent']}")
        lines.append(f"- Stale (31-90 days): {distribution['stale']}")
        lines.append(f"- Old (90+ days): {distribution['old']}")
        lines.append("")

        # Summary
        lines.append("## Summary")
        lines.append(health_report["summary"])
        lines.append("")

        # Recommendations
        lines.append("## Recommendations")
        for i, rec in enumerate(health_report["recommendations"], 1):
            lines.append(f"{i}. {rec}")

        return "\n".join(lines)

    def display_triage_report(self, triage_report: Dict) -> str:
        """
        Display fleeting triage report to console.

        Args:
            triage_report: Triage report dictionary from WorkflowManager

        Returns:
            Formatted string for console output
        """
        lines = []

        # Quality assessment
        lines.append("QUALITY ASSESSMENT")
        lines.append("-" * 18)
        lines.append(
            f"   Total notes processed: {triage_report['total_notes_processed']}"
        )

        # Quality distribution
        quality_dist = triage_report["quality_distribution"]
        lines.append(f"   High Quality (>0.7): {quality_dist.get('high', 0)}")
        lines.append(f"   Medium Quality (0.4-0.7): {quality_dist.get('medium', 0)}")
        lines.append(f"   Low Quality (<0.4): {quality_dist.get('low', 0)}")

        if triage_report.get("quality_threshold"):
            lines.append(f"   Quality threshold: {triage_report['quality_threshold']}")
            filtered_count = triage_report.get("filtered_count", 0)
            lines.append(f"   Notes filtered by quality threshold: {filtered_count}")

        # Triage recommendations
        lines.append("\nTRIAGE RECOMMENDATIONS")
        lines.append("-" * 22)
        recommendations = triage_report["recommendations"]

        # Group recommendations by action
        action_groups = {}
        for rec in recommendations:
            action = rec["action"]
            if action not in action_groups:
                action_groups[action] = []
            action_groups[action].append(rec)

        for action, recs in action_groups.items():
            action_emoji = (
                "✅"
                if "Promote" in action
                else "⚠️" if "Enhancement" in action else "🚨"
            )
            lines.append(f"   {action_emoji} {action}: {len(recs)} notes")
            for rec in recs[:3]:  # Show top 3 per category
                note_name = Path(rec["note_path"]).stem
                quality = rec["quality_score"]
                lines.append(f"      📄 {note_name} (quality: {quality:.2f})")
            if len(recs) > 3:
                lines.append(f"      ... and {len(recs) - 3} more")

        # Batch processing results
        lines.append("\nBATCH PROCESSING RESULTS")
        lines.append("-" * 24)
        processing_time = triage_report.get("processing_time", 0)
        lines.append(f"   Processing time: {processing_time:.2f} seconds")
        lines.append(
            f"   Notes per second: {triage_report['total_notes_processed'] / max(processing_time, 0.1):.1f}"
        )

        return "\n".join(lines)

    def format_triage_markdown(self, triage_report: Dict) -> str:
        """
        Format fleeting triage report as markdown for export.

        Args:
            triage_report: Triage report dictionary from WorkflowManager

        Returns:
            Markdown formatted string
        """
        lines = []
        lines.append("# Fleeting Notes Triage Report")
        lines.append("")

        # Quality assessment
        lines.append("## Quality Assessment")
        lines.append(f"Total notes processed: {triage_report['total_notes_processed']}")
        lines.append("")

        quality_dist = triage_report["quality_distribution"]
        lines.append("### Quality Distribution")
        lines.append(f"- High Quality (>0.7): {quality_dist.get('high', 0)}")
        lines.append(f"- Medium Quality (0.4-0.7): {quality_dist.get('medium', 0)}")
        lines.append(f"- Low Quality (<0.4): {quality_dist.get('low', 0)}")
        lines.append("")

        # Recommendations
        lines.append("## Triage Recommendations")
        recommendations = triage_report["recommendations"]

        # Group by action
        action_groups = {}
        for rec in recommendations:
            action = rec["action"]
            if action not in action_groups:
                action_groups[action] = []
            action_groups[action].append(rec)

        for action, recs in action_groups.items():
            lines.append(f"### {action} ({len(recs)} notes)")
            for rec in recs:
                note_name = Path(rec["note_path"]).stem
                quality = rec["quality_score"]
                lines.append(f"- **{note_name}** (quality: {quality:.2f})")
                lines.append(f"  - Reason: {rec['reason']}")
            lines.append("")

        return "\n".join(lines)
