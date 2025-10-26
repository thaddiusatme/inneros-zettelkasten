"""
Advanced analytics for note collections with AI-powered insights.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter
from datetime import datetime, date
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False
from dataclasses import dataclass

from .tagger import AITagger
from .summarizer import AISummarizer
from .connections import AIConnections
from src.utils.frontmatter import parse_frontmatter as fm_parse_frontmatter


@dataclass
class NoteStats:
    """Statistics for a single note."""
    filename: str
    word_count: int
    tag_count: int
    link_count: int
    creation_date: Optional[datetime]
    last_modified: Optional[datetime]
    note_type: str
    status: str
    has_summary: bool
    quality_score: float


class NoteAnalytics:
    """Comprehensive analytics for note collections."""

    def __init__(self, notes_directory: str):
        """
        Initialize analytics for a notes directory.
        
        Args:
            notes_directory: Path to the notes directory
        """
        self.notes_dir = Path(notes_directory)
        self.ai_tagger = AITagger()
        self.ai_summarizer = AISummarizer()
        self.ai_connections = AIConnections()

        # Cache for processed notes
        self._note_cache = {}
        self._connection_cache = {}

    def scan_notes(self) -> List[NoteStats]:
        """Scan all notes and collect statistics."""
        notes = []

        for md_file in self.notes_dir.rglob("*.md"):
            try:
                stats = self._analyze_note(md_file)
                if stats:
                    notes.append(stats)
            except Exception as e:
                print(f"Warning: Failed to analyze {md_file}: {e}")

        return notes

    def _analyze_note(self, file_path: Path) -> Optional[NoteStats]:
        """Analyze a single note file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        # Extract frontmatter
        frontmatter, body = self._extract_frontmatter(content)

        # Count words (excluding frontmatter)
        word_count = len(body.split())

        # Count tags
        tags = frontmatter.get("tags", [])
        tag_count = len(tags) if isinstance(tags, list) else 0

        # Count internal links
        link_count = len(re.findall(r'\[\[([^\]]+)\]\]', body))

        # Parse dates
        creation_date = self._parse_date(frontmatter.get("created"))

        # Get file modification time
        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

        # Get note type and status
        note_type = frontmatter.get("type", "unknown")
        status = frontmatter.get("status", "unknown")

        # Check for AI-generated summary
        has_summary = "ai_summary" in frontmatter

        # Calculate quality score (simple heuristic)
        quality_score = self._calculate_quality_score(
            word_count, tag_count, link_count, frontmatter
        )

        return NoteStats(
            filename=file_path.name,
            word_count=word_count,
            tag_count=tag_count,
            link_count=link_count,
            creation_date=creation_date,
            last_modified=last_modified,
            note_type=note_type,
            status=status,
            has_summary=has_summary,
            quality_score=quality_score
        )

    def _extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter and body using centralized parser."""
        metadata, body = fm_parse_frontmatter(content)
        # Ensure tags is a list if present, otherwise default to [] downstream
        return metadata, body

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None

        # Handle if already a datetime object (from YAML parser)
        if isinstance(date_str, datetime):
            return date_str

        # Handle if it's a date object (convert to datetime)
        if isinstance(date_str, date):
            return datetime.combine(date_str, datetime.min.time())

        # Handle string parsing
        if not isinstance(date_str, str):
            return None

        # Try common date formats
        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        return None

    def _calculate_quality_score(self, word_count: int, tag_count: int,
                                link_count: int, frontmatter: Dict) -> float:
        """Calculate a quality score for the note."""
        score = 0.0

        # Word count contribution (0-0.3)
        if word_count > 0:
            score += min(0.3, word_count / 1000 * 0.3)

        # Tag contribution (0-0.2)
        if tag_count > 0:
            score += min(0.2, tag_count / 5 * 0.2)

        # Link contribution (0-0.2)
        if link_count > 0:
            score += min(0.2, link_count / 3 * 0.2)

        # Metadata completeness (0-0.3)
        required_fields = ["type", "created", "status"]
        present_fields = sum(1 for field in required_fields if field in frontmatter)
        score += (present_fields / len(required_fields)) * 0.3

        return min(1.0, score)

    def generate_report(self) -> Dict:
        """Generate comprehensive analytics report."""
        notes = self.scan_notes()

        if not notes:
            return {"error": "No notes found"}

        # Basic statistics
        total_notes = len(notes)
        total_words = sum(note.word_count for note in notes)
        avg_words = total_words / total_notes if total_notes > 0 else 0

        # Note type distribution
        type_counts = Counter(note.note_type for note in notes)

        # Status distribution
        status_counts = Counter(note.status for note in notes)

        # Tag analysis
        all_tags = []
        for note in notes:
            if note.tag_count > 0:
                # We'd need to extract actual tags from files for this
                pass

        # Quality analysis
        quality_scores = [note.quality_score for note in notes]
        avg_quality = sum(quality_scores) / len(quality_scores)

        # Temporal analysis
        creation_dates = [note.creation_date for note in notes if note.creation_date]

        # Notes with AI features
        notes_with_summaries = sum(1 for note in notes if note.has_summary)

        # Link density
        total_links = sum(note.link_count for note in notes)
        avg_links = total_links / total_notes if total_notes > 0 else 0

        report = {
            "overview": {
                "total_notes": total_notes,
                "total_words": total_words,
                "average_words_per_note": round(avg_words, 1),
                "average_quality_score": round(avg_quality, 2),
                "notes_with_ai_summaries": notes_with_summaries,
                "total_internal_links": total_links,
                "average_links_per_note": round(avg_links, 1)
            },
            "distributions": {
                "note_types": dict(type_counts),
                "note_status": dict(status_counts)
            },
            "quality_metrics": {
                "high_quality_notes": len([n for n in notes if n.quality_score > 0.7]),
                "medium_quality_notes": len([n for n in notes if 0.4 <= n.quality_score <= 0.7]),
                "low_quality_notes": len([n for n in notes if n.quality_score < 0.4]),
                "quality_distribution": {
                    "min": min(quality_scores),
                    "max": max(quality_scores),
                    "avg": avg_quality
                }
            },
            "temporal_analysis": {
                "notes_with_dates": len(creation_dates),
                "date_range": {
                    "earliest": min(creation_dates).isoformat() if creation_dates else None,
                    "latest": max(creation_dates).isoformat() if creation_dates else None
                }
            },
            "recommendations": self._generate_recommendations(notes)
        }

        return report

    def _generate_recommendations(self, notes: List[NoteStats]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        # Quality recommendations
        low_quality_count = len([n for n in notes if n.quality_score < 0.4])
        if low_quality_count > 0:
            recommendations.append(
                f"Consider improving {low_quality_count} low-quality notes by adding tags, links, or more content"
            )

        # Tagging recommendations
        untagged_count = len([n for n in notes if n.tag_count == 0])
        if untagged_count > 0:
            recommendations.append(
                f"Add tags to {untagged_count} untagged notes for better organization"
            )

        # Linking recommendations
        unlinked_count = len([n for n in notes if n.link_count == 0])
        if unlinked_count > len(notes) * 0.5:
            recommendations.append(
                "Consider adding more internal links to create connections between notes"
            )

        # Summarization recommendations
        long_notes = [n for n in notes if n.word_count > 500 and not n.has_summary]
        if long_notes:
            recommendations.append(
                f"Generate AI summaries for {len(long_notes)} long notes to improve accessibility"
            )

        # Status recommendations
        inbox_count = len([n for n in notes if n.status == "inbox"])
        if inbox_count > 10:
            recommendations.append(
                f"Process {inbox_count} notes in inbox status - consider promoting to permanent notes"
            )

        return recommendations

    def create_connection_graph(self, output_file: str = "note_connections.png"):
        """Create a visual graph of note connections."""
        if not HAS_VISUALIZATION:
            return {
                "error": "Visualization libraries (matplotlib, networkx) not available",
                "message": "Install with: pip install matplotlib networkx",
                "output_file": output_file
            }

        # This would require parsing all notes to extract links
        # For now, return a placeholder
        return {
            "message": "Connection graph generation requires full note parsing",
            "output_file": output_file
        }

    def export_report(self, output_file: str):
        """Export analytics report to JSON file."""
        report = self.generate_report()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return f"Report exported to {output_file}"


def main():
    """CLI entry point for analytics."""
    import argparse

    parser = argparse.ArgumentParser(description="Note collection analytics")
    parser.add_argument("directory", help="Notes directory to analyze")
    parser.add_argument("--output", help="Output file for report (JSON)")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                       help="Output format")

    args = parser.parse_args()

    # Initialize analytics
    analytics = NoteAnalytics(args.directory)

    print(f"📊 Analyzing notes in: {args.directory}")

    # Generate report
    report = analytics.generate_report()

    if "error" in report:
        print(f"❌ Error: {report['error']}")
        return

    if args.format == "json":
        if args.output:
            analytics.export_report(args.output)
            print(f"📄 Report saved to: {args.output}")
        else:
            print(json.dumps(report, indent=2, default=str))
    else:
        # Text format output
        overview = report["overview"]
        print("\n📈 OVERVIEW")
        print(f"   Total Notes: {overview['total_notes']}")
        print(f"   Total Words: {overview['total_words']:,}")
        print(f"   Average Words/Note: {overview['average_words_per_note']}")
        print(f"   Average Quality Score: {overview['average_quality_score']}/1.0")
        print(f"   Notes with AI Summaries: {overview['notes_with_ai_summaries']}")
        print(f"   Total Internal Links: {overview['total_internal_links']}")

        print("\n📊 DISTRIBUTIONS")
        print(f"   Note Types: {report['distributions']['note_types']}")
        print(f"   Note Status: {report['distributions']['note_status']}")

        quality = report["quality_metrics"]
        print("\n✨ QUALITY METRICS")
        print(f"   High Quality (>0.7): {quality['high_quality_notes']}")
        print(f"   Medium Quality (0.4-0.7): {quality['medium_quality_notes']}")
        print(f"   Low Quality (<0.4): {quality['low_quality_notes']}")

        print("\n💡 RECOMMENDATIONS")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")


if __name__ == "__main__":
    main()
