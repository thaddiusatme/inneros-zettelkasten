"""
analytics.py — consolidated vault metrics module (#120).

Public classes:
  NoteStats           — dataclass for per-note statistics
  NoteAnalytics       — vault-wide analytics with optional matplotlib/networkx visualization
  AnalyticsManager    — pure-Python quality scoring, orphan/stale detection, workflow reports
  AnalyticsCoordinator — coordinates analytics workflow steps (link graph, age, productivity)

Import boundary: no AI calls in the core managers. Safe to run without Ollama.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from collections import Counter, defaultdict
from datetime import datetime, date, timedelta
from dataclasses import dataclass

try:
    import matplotlib.pyplot as plt  # noqa: F401
    import networkx as nx  # noqa: F401

    HAS_VISUALIZATION = True
except ImportError:
    HAS_VISUALIZATION = False

from src.utils.frontmatter import parse_frontmatter as fm_parse_frontmatter
from .types import AnalyticsResult, ConfigDict, WorkflowReport, ReviewCandidate


# ---------------------------------------------------------------------------
# NoteStats
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# NoteAnalytics
# ---------------------------------------------------------------------------


class NoteAnalytics:
    """Comprehensive analytics for note collections."""

    def __init__(self, notes_directory: str):
        self.notes_dir = Path(notes_directory)
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
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            return None

        frontmatter, body = self._extract_frontmatter(content)

        word_count = len(body.split())

        tags = frontmatter.get("tags", [])
        tag_count = len(tags) if isinstance(tags, list) else 0

        link_count = len(re.findall(r"\[\[([^\]]+)\]\]", body))

        creation_date = self._parse_date(frontmatter.get("created"))
        last_modified = datetime.fromtimestamp(file_path.stat().st_mtime)

        note_type = frontmatter.get("type", "unknown")
        status = frontmatter.get("status", "unknown")
        has_summary = "ai_summary" in frontmatter

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
            quality_score=quality_score,
        )

    def _extract_frontmatter(self, content: str) -> Tuple[Dict, str]:
        """Extract YAML frontmatter and body using centralized parser."""
        metadata, body = fm_parse_frontmatter(content)
        return metadata, body

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_str:
            return None
        if isinstance(date_str, datetime):
            return date_str
        if isinstance(date_str, date):
            return datetime.combine(date_str, datetime.min.time())
        if not isinstance(date_str, str):
            return None

        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def _calculate_quality_score(
        self, word_count: int, tag_count: int, link_count: int, frontmatter: Dict
    ) -> float:
        """Calculate a quality score for the note."""
        score = 0.0
        if word_count > 0:
            score += min(0.3, word_count / 1000 * 0.3)
        if tag_count > 0:
            score += min(0.2, tag_count / 5 * 0.2)
        if link_count > 0:
            score += min(0.2, link_count / 3 * 0.2)
        required_fields = ["type", "created", "status"]
        present_fields = sum(1 for field in required_fields if field in frontmatter)
        score += (present_fields / len(required_fields)) * 0.3
        return min(1.0, score)

    def generate_report(self) -> Dict:
        """Generate comprehensive analytics report."""
        notes = self.scan_notes()
        if not notes:
            return {"error": "No notes found"}

        total_notes = len(notes)
        total_words = sum(note.word_count for note in notes)
        avg_words = total_words / total_notes if total_notes > 0 else 0

        type_counts = Counter(note.note_type for note in notes)
        status_counts = Counter(note.status for note in notes)

        quality_scores = [note.quality_score for note in notes]
        avg_quality = sum(quality_scores) / len(quality_scores)

        creation_dates = [note.creation_date for note in notes if note.creation_date]
        notes_with_summaries = sum(1 for note in notes if note.has_summary)

        total_links = sum(note.link_count for note in notes)
        avg_links = total_links / total_notes if total_notes > 0 else 0

        return {
            "overview": {
                "total_notes": total_notes,
                "total_words": total_words,
                "average_words_per_note": round(avg_words, 1),
                "average_quality_score": round(avg_quality, 2),
                "notes_with_ai_summaries": notes_with_summaries,
                "total_internal_links": total_links,
                "average_links_per_note": round(avg_links, 1),
            },
            "distributions": {
                "note_types": dict(type_counts),
                "note_status": dict(status_counts),
            },
            "quality_metrics": {
                "high_quality_notes": len([n for n in notes if n.quality_score > 0.7]),
                "medium_quality_notes": len(
                    [n for n in notes if 0.4 <= n.quality_score <= 0.7]
                ),
                "low_quality_notes": len([n for n in notes if n.quality_score < 0.4]),
                "quality_distribution": {
                    "min": min(quality_scores),
                    "max": max(quality_scores),
                    "avg": avg_quality,
                },
            },
            "temporal_analysis": {
                "notes_with_dates": len(creation_dates),
                "date_range": {
                    "earliest": (
                        min(creation_dates).isoformat() if creation_dates else None
                    ),
                    "latest": (
                        max(creation_dates).isoformat() if creation_dates else None
                    ),
                },
            },
            "recommendations": self._generate_recommendations(notes),
        }

    def _generate_recommendations(self, notes: List[NoteStats]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []

        low_quality_count = len([n for n in notes if n.quality_score < 0.4])
        if low_quality_count > 0:
            recommendations.append(
                f"Consider improving {low_quality_count} low-quality notes by adding tags, links, or more content"
            )

        untagged_count = len([n for n in notes if n.tag_count == 0])
        if untagged_count > 0:
            recommendations.append(
                f"Add tags to {untagged_count} untagged notes for better organization"
            )

        unlinked_count = len([n for n in notes if n.link_count == 0])
        if unlinked_count > len(notes) * 0.5:
            recommendations.append(
                "Consider adding more internal links to create connections between notes"
            )

        long_notes = [n for n in notes if n.word_count > 500 and not n.has_summary]
        if long_notes:
            recommendations.append(
                f"Generate AI summaries for {len(long_notes)} long notes to improve accessibility"
            )

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
                "output_file": output_file,
            }
        return {
            "message": "Connection graph generation requires full note parsing",
            "output_file": output_file,
        }

    def export_report(self, output_file: str):
        """Export analytics report to JSON file."""
        report = self.generate_report()
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        return f"Report exported to {output_file}"


# ---------------------------------------------------------------------------
# AnalyticsManager
# ---------------------------------------------------------------------------


class AnalyticsManager:
    """
    Pure metrics calculation for notes without AI dependencies.

    Provides quality assessment, orphan/stale detection, workflow reports,
    and promotion candidate scanning. Safe to run without Ollama.
    """

    def __init__(self, base_dir: Path, config: ConfigDict) -> None:
        self.base_dir = Path(base_dir)
        self.config = config

    def assess_quality(self, note_path: str, dry_run: bool = False) -> AnalyticsResult:
        """Assess the quality of a note based on multiple metrics."""
        if not note_path or note_path.strip() == "":
            raise ValueError("note_path cannot be empty")

        full_path = (
            self.base_dir / note_path
            if not Path(note_path).is_absolute()
            else Path(note_path)
        )
        if not full_path.exists():
            raise FileNotFoundError(f"Note file not found: {note_path}")

        content = full_path.read_text(encoding="utf-8")

        has_frontmatter = content.startswith("---")
        frontmatter_content = ""
        body_content = content

        if has_frontmatter:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_content = parts[1]
                body_content = parts[2]

        word_count = len(body_content.split())

        tags = set()
        if frontmatter_content:
            tag_match = re.search(r"tags:\s*\[(.*?)\]", frontmatter_content)
            if tag_match:
                tag_str = tag_match.group(1)
                tags.update(
                    tag.strip().strip("\"'")
                    for tag in tag_str.split(",")
                    if tag.strip()
                )
        inline_tags = re.findall(r"#([\w-]+)", body_content)
        tags.update(inline_tags)
        tag_count = len(tags)

        links = re.findall(r"\[\[(.*?)\]\]", body_content)
        link_count = len(links)

        weights = self.config.get("analytics", {}).get(
            "quality_weights",
            {
                "word_count": 0.3,
                "tag_count": 0.2,
                "link_count": 0.3,
                "frontmatter": 0.2,
            },
        )

        word_score = min(word_count / 500.0, 1.0)
        tag_score = min(tag_count / 5.0, 1.0)
        link_score = min(link_count / 5.0, 1.0)
        frontmatter_score = 1.0 if has_frontmatter else 0.0

        quality_score = (
            word_score * weights["word_count"]
            + tag_score * weights["tag_count"]
            + link_score * weights["link_count"]
            + frontmatter_score * weights["frontmatter"]
        )

        return {
            "success": True,
            "quality_score": round(quality_score, 2),
            "word_count": word_count,
            "tag_count": tag_count,
            "link_count": link_count,
            "has_frontmatter": has_frontmatter,
            "metrics": {
                "word_score": round(word_score, 2),
                "tag_score": round(tag_score, 2),
                "link_score": round(link_score, 2),
                "frontmatter_score": frontmatter_score,
            },
        }

    def detect_orphaned_notes(self) -> ReviewCandidate:
        """Detect notes with no incoming or outgoing links."""
        link_graph = self._build_link_graph()
        orphaned = []
        for note_path, links in link_graph.items():
            incoming = links.get("incoming", [])
            outgoing = links.get("outgoing", [])
            if len(incoming) == 0 and len(outgoing) == 0:
                orphaned.append(
                    {
                        "note": Path(note_path).name,
                        "title": self._extract_title(note_path),
                        "incoming_links": 0,
                        "outgoing_links": 0,
                    }
                )
        return orphaned

    def detect_stale_notes(
        self, days_threshold: Optional[int] = None
    ) -> ReviewCandidate:
        """Detect notes not modified within threshold period."""
        if days_threshold is None:
            days_threshold = self.config.get("analytics", {}).get(
                "stale_threshold_days", 90
            )

        threshold_date = datetime.now() - timedelta(days=days_threshold)
        stale_notes = []

        for md_file in self.base_dir.rglob("*.md"):
            if ".git" in str(md_file) or "Archive" in str(md_file):
                continue
            modified_time = datetime.fromtimestamp(md_file.stat().st_mtime)
            if modified_time < threshold_date:
                days_since = (datetime.now() - modified_time).days
                stale_notes.append(
                    {
                        "note": md_file.name,
                        "title": self._extract_title(md_file),
                        "last_modified": modified_time,
                        "days_since_modified": days_since,
                    }
                )

        return sorted(stale_notes, key=lambda x: x["days_since_modified"], reverse=True)

    def generate_workflow_report(self) -> WorkflowReport:
        """Generate aggregated workflow metrics across the vault."""
        report: Dict = {
            "total_notes": 0,
            "notes_by_type": {},
            "notes_by_status": {},
            "avg_quality_score": 0.0,
            "quality_scores": [],
        }

        for md_file in self.base_dir.rglob("*.md"):
            if ".git" in str(md_file) or "Archive" in str(md_file):
                continue
            report["total_notes"] += 1
            try:
                content = md_file.read_text(encoding="utf-8")
                type_match = re.search(r"type:\s*(\w+)", content)
                if type_match:
                    note_type = type_match.group(1)
                    report["notes_by_type"][note_type] = (
                        report["notes_by_type"].get(note_type, 0) + 1
                    )
                status_match = re.search(r"status:\s*(\w+)", content)
                if status_match:
                    status = status_match.group(1)
                    report["notes_by_status"][status] = (
                        report["notes_by_status"].get(status, 0) + 1
                    )
                try:
                    quality_result = self.assess_quality(
                        str(md_file.relative_to(self.base_dir))
                    )
                    report["quality_scores"].append(quality_result["quality_score"])
                except Exception:
                    pass
            except Exception:
                continue

        if report["quality_scores"]:
            report["avg_quality_score"] = round(
                sum(report["quality_scores"]) / len(report["quality_scores"]), 2
            )

        report["orphaned_count"] = len(self.detect_orphaned_notes())
        report["stale_count"] = len(self.detect_stale_notes())

        return report

    def scan_review_candidates(
        self, min_quality_score: Optional[float] = None
    ) -> ReviewCandidate:
        """Identify high-quality fleeting notes ready for promotion."""
        if min_quality_score is None:
            min_quality_score = self.config.get("analytics", {}).get(
                "promotion_threshold", 0.7
            )

        candidates = []
        fleeting_dir = self.base_dir / "Fleeting Notes"
        if not fleeting_dir.exists():
            return candidates

        for note_file in fleeting_dir.glob("*.md"):
            try:
                quality_result = self.assess_quality(
                    str(note_file.relative_to(self.base_dir))
                )
                if quality_result["quality_score"] >= min_quality_score:
                    candidates.append(
                        {
                            "note": note_file.name,
                            "title": self._extract_title(note_file),
                            "quality_score": quality_result["quality_score"],
                            "metrics": quality_result.get("metrics", {}),
                            "rationale": self._generate_promotion_rationale(
                                quality_result
                            ),
                        }
                    )
            except Exception:
                continue

        return sorted(candidates, key=lambda x: x["quality_score"], reverse=True)

    def _build_link_graph(self) -> Dict[str, Dict[str, List[str]]]:
        """Build bidirectional link graph for all notes."""
        link_graph = {}
        for md_file in self.base_dir.rglob("*.md"):
            if ".git" in str(md_file):
                continue
            note_path = str(md_file.relative_to(self.base_dir))
            link_graph[note_path] = {"incoming": [], "outgoing": []}
            try:
                content = md_file.read_text(encoding="utf-8")
                links = re.findall(r"\[\[(.*?)\]\]", content)
                link_graph[note_path]["outgoing"] = links
            except Exception:
                continue

        for source_path, links in link_graph.items():
            for target_link in links["outgoing"]:
                for target_path in link_graph.keys():
                    if target_link in target_path:
                        link_graph[target_path]["incoming"].append(source_path)
                        break

        return link_graph

    def _extract_title(self, file_path: Union[str, Path]) -> str:
        """Extract title from note file."""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        try:
            content = file_path.read_text(encoding="utf-8")
            title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()
        except Exception:
            pass
        return file_path.stem

    def _generate_promotion_rationale(self, quality_result: AnalyticsResult) -> str:
        """Generate human-readable rationale for promotion recommendation."""
        reasons = []
        if quality_result["word_count"] > 300:
            reasons.append("substantial content")
        if quality_result["tag_count"] >= 3:
            reasons.append("well-categorized")
        if quality_result["link_count"] >= 3:
            reasons.append("well-connected")
        if quality_result["has_frontmatter"]:
            reasons.append("complete metadata")
        if reasons:
            return f"Ready for promotion: {', '.join(reasons)}"
        return "Meets quality threshold"


# ---------------------------------------------------------------------------
# AnalyticsCoordinator
# ---------------------------------------------------------------------------


class AnalyticsCoordinator:
    """
    Coordinates analytics and metrics operations for note collections.

    Handles orphan/stale detection, enhanced metrics, link graph construction,
    age distribution, and productivity metrics.
    """

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"
        self.permanent_dir = self.base_dir / "Permanent Notes"

    def detect_orphaned_notes(self) -> List[Dict]:
        """Detect notes that have no bidirectional links to other notes."""
        all_notes = self._get_all_notes()
        link_graph = self._build_link_graph(all_notes)
        return [
            self._create_orphaned_note_info(p)
            for p in all_notes
            if self._is_orphaned_note(p, link_graph)
        ]

    def detect_orphaned_notes_comprehensive(self) -> List[Dict]:
        """Detect orphaned notes across the entire repository."""
        all_notes = self._get_all_notes_comprehensive()
        link_graph = self._build_link_graph(all_notes)
        return [
            self._create_orphaned_note_info(p)
            for p in all_notes
            if self._is_orphaned_note(p, link_graph)
        ]

    def detect_stale_notes(self, days_threshold: int = 90) -> List[Dict]:
        """Detect notes not modified within threshold period."""
        stale_notes = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        for note_path in self._get_all_notes():
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
                continue
        stale_notes.sort(key=lambda x: x["days_since_modified"], reverse=True)
        return stale_notes

    def generate_enhanced_metrics(self) -> Dict:
        """Generate comprehensive metrics for weekly review."""
        metrics = {
            "generated_at": datetime.now().isoformat(),
            "orphaned_notes": self.detect_orphaned_notes(),
            "stale_notes": self.detect_stale_notes(),
            "link_density": self._calculate_link_density(),
            "note_age_distribution": self._calculate_note_age_distribution(),
            "productivity_metrics": self._calculate_productivity_metrics(),
        }
        metrics["summary"] = {
            "total_orphaned": len(metrics["orphaned_notes"]),
            "total_stale": len(metrics["stale_notes"]),
            "avg_links_per_note": metrics["link_density"],
            "total_notes": len(self._get_all_notes()),
        }
        return metrics

    def _get_all_notes(self) -> List[Path]:
        """Get all markdown notes from workflow directories."""
        all_notes = []
        for directory in [self.permanent_dir, self.fleeting_dir, self.inbox_dir]:
            if directory.exists():
                all_notes.extend(directory.glob("*.md"))
        return all_notes

    def _get_all_notes_comprehensive(self) -> List[Path]:
        """Get all markdown notes from the entire repository."""
        return list(self.base_dir.rglob("*.md"))

    def _build_link_graph(self, all_notes: List[Path]) -> Dict[str, set]:
        """Build a graph of note links."""
        link_graph = {}
        for note_path in all_notes:
            note_name = note_path.stem
            link_graph[note_name] = set()
            try:
                with open(note_path, "r", encoding="utf-8") as f:
                    content = f.read()
                wiki_links = re.findall(r"\[\[([^\]]+)\]\]", content)
                for link in wiki_links:
                    link_graph[note_name].add(link.replace(".md", ""))
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        return link_graph

    def _is_orphaned_note(self, note_path: Path, link_graph: Dict[str, set]) -> bool:
        """Check if a note is orphaned (no incoming or outgoing links)."""
        if note_path.parent.name == "Inbox":
            return False
        note_name = note_path.stem
        has_outgoing = len(link_graph.get(note_name, set())) > 0
        has_incoming = any(
            note_name in links
            for other, links in link_graph.items()
            if other != note_name
        )
        return not (has_outgoing or has_incoming)

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
        return {
            "path": str(note_path),
            "title": self._extract_note_title(note_path),
            "last_modified": last_modified.isoformat(),
            "days_since_modified": days_since_modified,
            "directory": note_path.parent.name,
        }

    def _extract_note_title(self, note_path: Path) -> str:
        """Extract title from note (first # heading or filename)."""
        try:
            with open(note_path, "r", encoding="utf-8") as f:
                content = f.read()
            heading_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
            if heading_match:
                return heading_match.group(1).strip()
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
        return total_links / len(all_notes)

    def _calculate_note_age_distribution(self) -> Dict:
        """Calculate distribution of note ages."""
        all_notes = self._get_all_notes()
        age_buckets = {"new": 0, "recent": 0, "mature": 0, "old": 0}
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
                age_buckets["old"] += 1
        return age_buckets

    def _calculate_productivity_metrics(self) -> Dict:
        """Calculate productivity metrics like notes per week."""
        all_notes = self._get_all_notes()
        weekly_creation: Dict[str, int] = defaultdict(int)
        weekly_modification: Dict[str, int] = defaultdict(int)
        for note_path in all_notes:
            try:
                created_time = datetime.fromtimestamp(note_path.stat().st_ctime)
                modified_time = datetime.fromtimestamp(note_path.stat().st_mtime)
                weekly_creation[created_time.strftime("%Y-W%U")] += 1
                weekly_modification[modified_time.strftime("%Y-W%U")] += 1
            except (OSError, AttributeError):
                continue
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


# ---------------------------------------------------------------------------
# CLI entry point (preserved from original analytics.py)
# ---------------------------------------------------------------------------


def main():
    """CLI entry point for analytics."""
    import argparse

    parser = argparse.ArgumentParser(description="Note collection analytics")
    parser.add_argument("directory", help="Notes directory to analyze")
    parser.add_argument("--output", help="Output file for report (JSON)")
    parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )
    args = parser.parse_args()

    analytics = NoteAnalytics(args.directory)
    print(f"Analyzing notes in: {args.directory}")

    report = analytics.generate_report()
    if "error" in report:
        print(f"Error: {report['error']}")
        return

    if args.format == "json":
        if args.output:
            analytics.export_report(args.output)
            print(f"Report saved to: {args.output}")
        else:
            print(json.dumps(report, indent=2, default=str))
    else:
        overview = report["overview"]
        print("\nOVERVIEW")
        print(f"   Total Notes: {overview['total_notes']}")
        print(f"   Total Words: {overview['total_words']:,}")
        print(f"   Avg Words/Note: {overview['average_words_per_note']}")
        print(f"   Avg Quality Score: {overview['average_quality_score']}/1.0")
        print(f"   Notes with AI Summaries: {overview['notes_with_ai_summaries']}")
        print(f"   Total Internal Links: {overview['total_internal_links']}")
        print("\nDISTRIBUTIONS")
        print(f"   Note Types: {report['distributions']['note_types']}")
        print(f"   Note Status: {report['distributions']['note_status']}")
        quality = report["quality_metrics"]
        print("\nQUALITY METRICS")
        print(f"   High (>0.7): {quality['high_quality_notes']}")
        print(f"   Medium (0.4-0.7): {quality['medium_quality_notes']}")
        print(f"   Low (<0.4): {quality['low_quality_notes']}")
        print("\nRECOMMENDATIONS")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"   {i}. {rec}")


if __name__ == "__main__":
    main()
