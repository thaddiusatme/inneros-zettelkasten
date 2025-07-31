"""
Weekly Review Formatter - Transforms AI recommendations into user-friendly checklists.
"""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class WeeklyReviewFormatter:
    """Formats weekly review recommendations into various output formats."""
    
    def __init__(self):
        """Initialize the formatter."""
        self.action_config = {
            "promote_to_permanent": {
                "section": "🎯 Ready to Promote",
                "action_text": "Promote to Permanent",
                "priority": 1
            },
            "move_to_fleeting": {
                "section": "🔄 Further Development",
                "action_text": "Further Develop",
                "priority": 2
            },
            "improve_or_archive": {
                "section": "⚠️ Needs Significant Work",
                "action_text": "Needs Improvement",
                "priority": 3
            },
            "manual_review": {
                "section": "🚨 Manual Review Required",
                "action_text": "Manual Review",
                "priority": 4
            }
        }
    
    def format_checklist(self, recommendations: Dict) -> str:
        """Format recommendations into a markdown checklist.
        
        Args:
            recommendations: Dictionary with summary and recommendations
            
        Returns:
            Formatted markdown checklist string
        """
        lines = []
        
        # Header with date and summary
        lines.extend(self._format_header(recommendations))
        
        # Main sections organized by action type
        lines.extend(self._format_sections(recommendations))
        
        # Footer with metadata
        lines.extend(self._format_footer(recommendations))
        
        return "\\n".join(lines)
    
    def _format_header(self, recommendations: Dict) -> List[str]:
        """Format the checklist header with summary stats."""
        summary = recommendations["summary"]
        generated_at = recommendations["generated_at"]
        
        # Parse date for header
        try:
            date_obj = datetime.fromisoformat(generated_at.replace('Z', '+00:00'))
            date_str = date_obj.strftime("%Y-%m-%d")
        except:
            date_str = "Unknown Date"
        
        lines = [
            f"# Weekly Review - {date_str}",
            ""
        ]
        
        # Summary statistics
        total = summary["total_notes"]
        promote = summary["promote_to_permanent"]
        develop = summary["move_to_fleeting"]
        improve = summary["needs_improvement"]
        errors = summary["processing_errors"]
        
        if total == 0:
            lines.extend([
                "**Summary**: 0 notes to process",
                "",
                "✅ No notes requiring review - your inbox is clear!",
                ""
            ])
        else:
            summary_parts = []
            if promote > 0:
                summary_parts.append(f"{promote} promote")
            if develop > 0:
                summary_parts.append(f"{develop} refine")
            if improve > 0:
                summary_parts.append(f"{improve} improve")
            if errors > 0:
                summary_parts.append(f"{errors} errors")
            
            summary_text = ", ".join(summary_parts) if summary_parts else "0 actions"
            lines.extend([
                f"**Summary**: {total} notes to process ({summary_text})",
                ""
            ])
        
        return lines
    
    def _format_sections(self, recommendations: Dict) -> List[str]:
        """Format the main sections organized by action type."""
        if not recommendations["recommendations"]:
            return ["*No specific actions required.*", ""]
        
        lines = []
        
        # Group recommendations by action
        grouped = self._group_by_action(recommendations["recommendations"])
        
        # Sort sections by priority
        sorted_actions = sorted(grouped.keys(), 
                              key=lambda x: self.action_config[x]["priority"])
        
        for action in sorted_actions:
            if not grouped[action]:
                continue
                
            config = self.action_config[action]
            lines.extend([
                f"## {config['section']} ({len(grouped[action])})",
                ""
            ])
            
            # Format individual items
            for rec in grouped[action]:
                lines.append(self._format_checklist_item(rec, config))
            
            lines.append("")  # Add spacing between sections
        
        return lines
    
    def _group_by_action(self, recommendations: List[Dict]) -> Dict[str, List[Dict]]:
        """Group recommendations by action type."""
        grouped = {
            "promote_to_permanent": [],
            "move_to_fleeting": [],
            "improve_or_archive": [],
            "manual_review": []
        }
        
        for rec in recommendations:
            action = rec["action"]
            if action in grouped:
                grouped[action].append(rec)
        
        return grouped
    
    def _format_checklist_item(self, rec: Dict, config: Dict) -> str:
        """Format a single checklist item."""
        file_name = rec["file_name"]
        action_text = config["action_text"]
        reason = rec["reason"]
        quality_score = rec.get("quality_score")
        confidence = rec.get("confidence")
        
        # Build the checklist line
        line = f"- [ ] **{file_name}** — **{action_text}** ✅"
        
        # Add quality score if available
        if quality_score is not None:
            try:
                qual_val = float(quality_score)
                line += f" | Quality: {qual_val:.2f}"
            except (ValueError, TypeError):
                line += f" | Quality: {quality_score}"
        
        # Add confidence if available
        if confidence is not None:
            try:
                conf_val = float(confidence)
                line += f" | Confidence: {conf_val:.1f}"
            except (ValueError, TypeError):
                line += f" | Confidence: {confidence}"
        
        # Add reason on next line as indented text
        if reason:
            line += f"\\n  - {reason}"
        
        # Add AI tags if available
        ai_tags = rec.get("ai_tags", [])
        if ai_tags:
            tags_text = ", ".join(ai_tags[:5])  # Limit to 5 tags
            line += f"\\n  - Tags: {tags_text}"
        
        return line
    
    def _format_footer(self, recommendations: Dict) -> List[str]:
        """Format the checklist footer with metadata."""
        generated_at = recommendations["generated_at"]
        
        return [
            "---",
            "",
            f"*Generated: {generated_at}*",
            f"*AI-powered recommendations based on content quality and metadata analysis*",
            ""
        ]
    
    def export_checklist(self, recommendations: Dict, export_path: Path) -> Path:
        """Export checklist to a markdown file.
        
        Args:
            recommendations: Dictionary with summary and recommendations
            export_path: Path to export file or directory
            
        Returns:
            Path to the created file
        """
        # If export_path is a directory, generate filename
        if export_path.is_dir():
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"weekly-review-{timestamp}.md"
            export_path = export_path / filename
        
        # Ensure parent directory exists
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Format and write checklist
        checklist_content = self.format_checklist(recommendations)
        export_path.write_text(checklist_content, encoding='utf-8')
        
        return export_path
    
    def format_for_interactive(self, recommendations: Dict) -> List[Dict]:
        """Format recommendations for interactive step-by-step mode.
        
        Args:
            recommendations: Dictionary with summary and recommendations
            
        Returns:
            List of interactive items sorted by priority
        """
        interactive_items = []
        
        for rec in recommendations["recommendations"]:
            action = rec["action"]
            config = self.action_config.get(action, self.action_config["manual_review"])
            
            # Create formatted display text
            display_text = f"**{rec['file_name']}** — {config['action_text']}"
            if rec.get("quality_score"):
                display_text += f" (Quality: {rec['quality_score']:.2f})"
            
            interactive_items.append({
                "file_name": rec["file_name"],
                "action": action,
                "reason": rec["reason"],
                "quality_score": rec.get("quality_score"),
                "confidence": rec.get("confidence"),
                "priority": config["priority"],
                "formatted_display": display_text,
                "source": rec.get("source", "unknown"),
                "ai_tags": rec.get("ai_tags", [])
            })
        
        # Sort by priority (promote first, then develop, then improve)
        interactive_items.sort(key=lambda x: x["priority"])
        
        return interactive_items
    
    def format_enhanced_metrics(self, metrics: Dict) -> str:
        """
        Format enhanced metrics into a readable markdown report.
        
        Args:
            metrics: Dictionary from generate_enhanced_metrics()
            
        Returns:
            Formatted markdown metrics report
        """
        lines = []
        
        # Header
        lines.extend([
            "# 📊 Enhanced Weekly Review Metrics",
            "",
            f"**Generated**: {metrics.get('generated_at', 'Unknown')}",
            ""
        ])
        
        # Summary overview
        summary = metrics.get("summary", {})
        lines.extend([
            "## 📈 Summary Overview",
            "",
            f"- **Total Notes**: {summary.get('total_notes', 0)}",
            f"- **Orphaned Notes**: {summary.get('total_orphaned', 0)}",
            f"- **Stale Notes (>90 days)**: {summary.get('total_stale', 0)}",
            f"- **Average Links per Note**: {summary.get('avg_links_per_note', 0):.2f}",
            ""
        ])
        
        # Orphaned notes section
        orphaned_notes = metrics.get("orphaned_notes", [])
        if orphaned_notes:
            lines.extend([
                "## 🏝️ Orphaned Notes (Need Connections)",
                "",
                "These notes have no links to or from other notes:",
                ""
            ])
            for note in orphaned_notes:
                lines.append(f"- **{note['title']}** ({note['directory']}) - Last modified: {note.get('last_modified', 'Unknown')[:10]}")
            lines.append("")
        
        # Stale notes section
        stale_notes = metrics.get("stale_notes", [])
        if stale_notes:
            lines.extend([
                "## ⏰ Stale Notes (Haven't Been Updated)",
                "",
                "These notes haven't been modified in over 90 days:",
                ""
            ])
            # Show top 10 most stale
            for note in stale_notes[:10]:
                lines.append(f"- **{note['title']}** ({note['directory']}) - {note['days_since_modified']} days old")
            if len(stale_notes) > 10:
                lines.append(f"- ... and {len(stale_notes) - 10} more")
            lines.append("")
        
        # Note age distribution
        age_dist = metrics.get("note_age_distribution", {})
        lines.extend([
            "## 📅 Note Age Distribution",
            "",
            f"- **New** (< 7 days): {age_dist.get('new', 0)} notes",
            f"- **Recent** (7-30 days): {age_dist.get('recent', 0)} notes",
            f"- **Mature** (30-90 days): {age_dist.get('mature', 0)} notes",
            f"- **Old** (> 90 days): {age_dist.get('old', 0)} notes",
            ""
        ])
        
        # Productivity metrics
        productivity = metrics.get("productivity_metrics", {})
        lines.extend([
            "## 💪 Productivity Insights",
            "",
            f"- **Average Notes Created per Week**: {productivity.get('avg_notes_created_per_week', 0):.1f}",
            f"- **Average Notes Modified per Week**: {productivity.get('avg_notes_modified_per_week', 0):.1f}",
            f"- **Total Weeks Active**: {productivity.get('total_weeks_active', 0)}"
        ])
        
        most_productive = productivity.get('most_productive_week_creation')
        if most_productive:
            lines.append(f"- **Most Productive Week**: {most_productive[0]} ({most_productive[1]} notes created)")
        
        lines.append("")
        
        # Link density insights
        link_density = metrics.get("link_density", 0)
        if link_density < 1.0:
            insight = "🔗 Consider adding more connections between your notes"
        elif link_density < 2.0:
            insight = "🔗 Good link density - your notes are moderately connected"
        else:
            insight = "🔗 Excellent link density - your notes form a well-connected knowledge graph"
        
        lines.extend([
            "## 💡 Insights & Recommendations",
            "",
            insight
        ])
        
        if orphaned_notes:
            lines.append("🏝️ Focus on connecting orphaned notes to improve knowledge discoverability")
        
        if stale_notes:
            lines.append("⏰ Consider reviewing or archiving stale notes to keep your collection fresh")
        
        return "\n".join(lines)
