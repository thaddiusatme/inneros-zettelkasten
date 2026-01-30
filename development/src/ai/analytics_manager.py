"""
Analytics Manager - Pure Metrics Calculation (NO AI Dependencies)

Provides quality assessment, note analysis, and workflow metrics without AI calls.
This enables fast, cost-free analysis and parallel execution with ConnectionManager.

Features:
- Quality score calculation (word count, tags, links, frontmatter)
- Orphaned note detection (no incoming/outgoing links)
- Stale note detection (not modified within threshold)
- Workflow report generation (metrics by type/status)
- Review candidate identification (high-quality fleeting notes)

Design Principles:
- Pure Python metrics - no AI dependencies
- Exception-based error communication
- Configurable thresholds
- Can run in parallel with ConnectionManager
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import re

from .types import AnalyticsResult, ConfigDict, WorkflowReport, ReviewCandidate


class AnalyticsManager:
    """
    Pure metrics calculation for notes without AI dependencies.

    Provides:
    - Quality assessment (word count, tags, links, frontmatter completeness)
    - Orphaned note detection (link graph analysis)
    - Stale note detection (modification time threshold)
    - Workflow reports (aggregated metrics)
    - Review candidate identification

    NO AI Dependencies - can execute in parallel with ConnectionManager.
    """

    def __init__(self, base_dir: Path, config: ConfigDict) -> None:
        """
        Initialize AnalyticsManager.

        Args:
            base_dir: Base directory of the Zettelkasten vault
            config: Configuration dict with thresholds and weights
        """
        self.base_dir = Path(base_dir)
        self.config = config

    def assess_quality(self, note_path: str, dry_run: bool = False) -> AnalyticsResult:
        """
        Assess the quality of a note based on multiple metrics.

        Calculates:
        - Word count (content length) - 500 words = 1.0 score
        - Tag count (categorization) - 5 tags = 1.0 score
        - Link count (connections) - 5 links = 1.0 score
        - Frontmatter completeness - present = 1.0 score
        - Overall quality score (weighted sum with default weights: 0.3/0.2/0.3/0.2)

        Args:
            note_path: Path to the note file (relative to base_dir)
            dry_run: If True, can skip expensive operations (currently unused for analytics)

        Returns:
            Dict with quality metrics:
            {
                'success': True,
                'quality_score': float (0.0-1.0),
                'word_count': int,
                'tag_count': int,
                'link_count': int,
                'has_frontmatter': bool,
                'metrics': {
                    'word_score': float,
                    'tag_score': float,
                    'link_score': float,
                    'frontmatter_score': float
                }
            }

        Raises:
            ValueError: If note_path is empty or invalid
            FileNotFoundError: If note file doesn't exist

        Examples:
            >>> # Example 1: High quality note (well-developed content)
            >>> analytics = AnalyticsManager(Path('knowledge'), config)
            >>> result = analytics.assess_quality('Permanent Notes/machine-learning-basics.md')
            >>> print(f"Quality: {result['quality_score']}")
            Quality: 0.85
            >>> print(f"Words: {result['word_count']}, Tags: {result['tag_count']}, Links: {result['link_count']}")
            Words: 650, Tags: 5, Links: 8
            >>> print(f"Has frontmatter: {result['has_frontmatter']}")
            Has frontmatter: True
            >>> # Breakdown of score components
            >>> print(result['metrics'])
            {'word_score': 1.0, 'tag_score': 1.0, 'link_score': 1.0, 'frontmatter_score': 1.0}

            >>> # Example 2: Low quality note (needs development)
            >>> result = analytics.assess_quality('Inbox/quick-snippet.md')
            >>> print(f"Quality: {result['quality_score']}")
            Quality: 0.28
            >>> print(f"Words: {result['word_count']}, Tags: {result['tag_count']}, Links: {result['link_count']}")
            Words: 45, Tags: 1, Links: 0
            >>> # This note would trigger cost gating (skip AI enhancement)
            >>> if result['quality_score'] < 0.3:
            ...     print("Below cost gate threshold - AI enhancement will be skipped")
            Below cost gate threshold - AI enhancement will be skipped

            >>> # Example 3: Medium quality note (promotion candidate)
            >>> result = analytics.assess_quality('Fleeting Notes/interesting-idea.md')
            >>> print(f"Quality: {result['quality_score']}")
            Quality: 0.72
            >>> # Good enough for promotion to permanent notes
            >>> if result['quality_score'] >= 0.7:
            ...     print("High quality - recommend promotion to permanent notes")
            High quality - recommend promotion to permanent notes

            >>> # Example 4: Error handling - empty path
            >>> try:
            ...     result = analytics.assess_quality('')
            ... except ValueError as e:
            ...     print(f"Validation error: {e}")
            Validation error: note_path cannot be empty

            >>> # Example 5: Error handling - missing file
            >>> try:
            ...     result = analytics.assess_quality('NonExistent/note.md')
            ... except FileNotFoundError as e:
            ...     print(f"File not found: {e}")
            File not found: Note file not found: NonExistent/note.md

            >>> # Example 6: Understanding quality score calculation
            >>> result = analytics.assess_quality('Inbox/example.md')
            >>> # Quality score = weighted sum of normalized metrics
            >>> # Default weights: word_count=0.3, tag_count=0.2, link_count=0.3, frontmatter=0.2
            >>> metrics = result['metrics']
            >>> calculated_score = (
            ...     metrics['word_score'] * 0.3 +
            ...     metrics['tag_score'] * 0.2 +
            ...     metrics['link_score'] * 0.3 +
            ...     metrics['frontmatter_score'] * 0.2
            ... )
            >>> assert abs(calculated_score - result['quality_score']) < 0.01

            >>> # Example 7: Note without frontmatter penalty
            >>> result = analytics.assess_quality('Inbox/no-frontmatter.md')
            >>> if not result['has_frontmatter']:
            ...     print(f"Missing frontmatter reduces score by {0.2}")
            ...     print(f"Max possible score: {1.0 - 0.2}")
            Missing frontmatter reduces score by 0.2
            Max possible score: 0.8
        """
        # Validation
        if not note_path or note_path.strip() == "":
            raise ValueError("note_path cannot be empty")

        # Check file exists
        full_path = (
            self.base_dir / note_path
            if not Path(note_path).is_absolute()
            else Path(note_path)
        )
        if not full_path.exists():
            raise FileNotFoundError(f"Note file not found: {note_path}")

        # Read note content
        content = full_path.read_text(encoding="utf-8")

        # Extract frontmatter
        has_frontmatter = content.startswith("---")
        frontmatter_content = ""
        body_content = content

        if has_frontmatter:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_content = parts[1]
                body_content = parts[2]

        # Calculate metrics
        word_count = len(body_content.split())

        # Extract tags from frontmatter and body
        tags = set()
        # Frontmatter tags
        if frontmatter_content:
            tag_match = re.search(r"tags:\s*\[(.*?)\]", frontmatter_content)
            if tag_match:
                tag_str = tag_match.group(1)
                tags.update(
                    tag.strip().strip("\"'")
                    for tag in tag_str.split(",")
                    if tag.strip()
                )

        # Inline tags (#tag)
        inline_tags = re.findall(r"#([\w-]+)", body_content)
        tags.update(inline_tags)

        tag_count = len(tags)

        # Count links ([[link]])
        links = re.findall(r"\[\[(.*?)\]\]", body_content)
        link_count = len(links)

        # Calculate quality score (weighted)
        weights = self.config.get("analytics", {}).get(
            "quality_weights",
            {
                "word_count": 0.3,
                "tag_count": 0.2,
                "link_count": 0.3,
                "frontmatter": 0.2,
            },
        )

        # Normalize metrics to 0-1 scale
        word_score = min(word_count / 500.0, 1.0)  # 500 words = max score
        tag_score = min(tag_count / 5.0, 1.0)  # 5 tags = max score
        link_score = min(link_count / 5.0, 1.0)  # 5 links = max score
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
        """
        Detect notes with no incoming or outgoing links.

        Builds a bidirectional link graph and identifies isolated notes
        that are disconnected from the knowledge graph.

        Returns:
            List of orphaned notes with metadata:
            [{
                'note': str (filename),
                'title': str (extracted from content),
                'incoming_links': 0,
                'outgoing_links': 0
            }]

        Examples:
            >>> # Example 1: Detect isolated notes in vault
            >>> analytics = AnalyticsManager(Path('knowledge'), config)
            >>> orphaned = analytics.detect_orphaned_notes()
            >>> print(f"Found {len(orphaned)} orphaned notes")
            Found 17 orphaned notes
            >>> for note in orphaned[:3]:
            ...     print(f"- {note['title']} ({note['note']})")
            - Quick Thought (fleeting-20250920-idea.md)
            - Random Snippet (inbox-snippet.md)
            - Unconnected Concept (concept-draft.md)

            >>> # Example 2: Check if specific note is orphaned
            >>> orphaned = analytics.detect_orphaned_notes()
            >>> my_note = 'fleeting-20250920-idea.md'
            >>> is_orphaned = any(n['note'] == my_note for n in orphaned)
            >>> if is_orphaned:
            ...     print(f"{my_note} is disconnected from knowledge graph")
            ...     print("Action: Add [[wiki-links]] to connect this note")
            fleeting-20250920-idea.md is disconnected from knowledge graph
            Action: Add [[wiki-links]] to connect this note

            >>> # Example 3: Empty vault or all notes connected
            >>> orphaned = analytics.detect_orphaned_notes()
            >>> if not orphaned:
            ...     print("No orphaned notes - excellent knowledge graph connectivity!")
            No orphaned notes - excellent knowledge graph connectivity!

            >>> # Example 4: Prioritize orphaned notes by note type
            >>> orphaned = analytics.detect_orphaned_notes()
            >>> # Orphaned permanent notes are more concerning than fleeting
            >>> for note in orphaned:
            ...     if 'permanent' in note['note'].lower():
            ...         print(f"HIGH PRIORITY: {note['title']} should have connections")
            HIGH PRIORITY: Advanced Concepts should have connections

            >>> # Example 5: Use with workflow report
            >>> orphaned = analytics.detect_orphaned_notes()
            >>> report = analytics.generate_workflow_report()
            >>> print(f"Orphaned: {len(orphaned)} / {report['total_notes']}")
            >>> connectivity_pct = ((report['total_notes'] - len(orphaned)) / report['total_notes']) * 100
            >>> print(f"Knowledge graph connectivity: {connectivity_pct:.1f}%")
            Orphaned: 17 / 76
            Knowledge graph connectivity: 77.6%
        """
        # Build link graph
        link_graph = self._build_link_graph()

        orphaned = []
        for note_path, links in link_graph.items():
            incoming = links.get("incoming", [])
            outgoing = links.get("outgoing", [])

            # Orphaned = no incoming AND no outgoing
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
        """
        Detect notes not modified within threshold period.

        Scans vault for notes that haven't been touched recently, which
        may indicate outdated content or abandoned concepts.

        Args:
            days_threshold: Days since modification (default: 90 from config)

        Returns:
            List of stale notes sorted by days_since_modified (descending):
            [{
                'note': str (filename),
                'title': str (extracted from content),
                'last_modified': datetime,
                'days_since_modified': int
            }]

        Examples:
            >>> # Example 1: Find notes not touched in 90+ days
            >>> from datetime import datetime, timedelta
            >>> analytics = AnalyticsManager(Path('knowledge'), config)
            >>> stale = analytics.detect_stale_notes(days_threshold=90)
            >>> print(f"Found {len(stale)} stale notes (90+ days)")
            Found 12 stale notes (90+ days)
            >>> # Most stale notes listed first
            >>> for note in stale[:3]:
            ...     print(f"- {note['title']}: {note['days_since_modified']} days ago")
            - Old Project Ideas: 345 days ago
            - Abandoned Draft: 278 days ago
            - Outdated Concept: 156 days ago

            >>> # Example 2: Custom threshold for weekly review
            >>> stale_recent = analytics.detect_stale_notes(days_threshold=30)
            >>> print(f"{len(stale_recent)} notes not modified in past month")
            >>> # These might need review or archiving
            >>> for note in stale_recent:
            ...     if note['days_since_modified'] > 60:
            ...         print(f"Archive candidate: {note['title']}")
            8 notes not modified in past month
            Archive candidate: Summer Research Notes
            Archive candidate: Temporary Project Thoughts

            >>> # Example 3: Strict threshold for active projects
            >>> stale_very_recent = analytics.detect_stale_notes(days_threshold=7)
            >>> if stale_very_recent:
            ...     print("These active notes need attention:")
            ...     for note in stale_very_recent:
            ...         print(f"  - {note['title']} (inactive {note['days_since_modified']} days)")
            These active notes need attention:
              - Current Research (inactive 10 days)
              - Weekly Goals (inactive 8 days)

            >>> # Example 4: Check modification timestamps
            >>> stale = analytics.detect_stale_notes(days_threshold=90)
            >>> for note in stale[:2]:
            ...     mod_date = note['last_modified']
            ...     print(f"{note['title']}: last modified {mod_date.strftime('%Y-%m-%d')}")
            Old Project Ideas: last modified 2024-01-15
            Abandoned Draft: last modified 2024-03-20

            >>> # Example 5: No stale notes (well-maintained vault)
            >>> stale = analytics.detect_stale_notes(days_threshold=90)
            >>> if not stale:
            ...     print("All notes recently updated - excellent maintenance!")
            All notes recently updated - excellent maintenance!

            >>> # Example 6: Use with workflow report
            >>> stale = analytics.detect_stale_notes()
            >>> report = analytics.generate_workflow_report()
            >>> stale_pct = (len(stale) / report['total_notes']) * 100
            >>> print(f"Stale notes: {len(stale)} / {report['total_notes']} ({stale_pct:.1f}%)")
            >>> if stale_pct > 20:
            ...     print("Consider archiving or updating stale notes")
            Stale notes: 12 / 76 (15.8%)
        """
        if days_threshold is None:
            days_threshold = self.config.get("analytics", {}).get(
                "stale_threshold_days", 90
            )

        threshold_date = datetime.now() - timedelta(days=days_threshold)
        stale_notes = []

        # Scan all markdown files
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
        """
        Generate aggregated workflow metrics across the vault.

        Scans all notes and aggregates statistics by type, status, quality,
        and maintenance metrics (orphaned/stale notes).

        Returns:
            Dict with workflow statistics:
            {
                'total_notes': int,
                'notes_by_type': {'permanent': int, 'fleeting': int, 'literature': int},
                'notes_by_status': {'inbox': int, 'promoted': int, 'published': int},
                'avg_quality_score': float (0.0-1.0),
                'quality_scores': [list of scores],
                'orphaned_count': int,
                'stale_count': int
            }

        Examples:
            >>> # Example 1: Generate vault overview report
            >>> analytics = AnalyticsManager(Path('knowledge'), config)
            >>> report = analytics.generate_workflow_report()
            >>> print(f"Total notes: {report['total_notes']}")
            Total notes: 76
            >>> print(f"Average quality: {report['avg_quality_score']}")
            Average quality: 0.68
            >>> print(f"Notes by type: {report['notes_by_type']}")
            Notes by type: {'permanent': 23, 'fleeting': 35, 'literature': 18}
            >>> print(f"Notes by status: {report['notes_by_status']}")
            Notes by status: {'inbox': 12, 'promoted': 28, 'published': 36}

            >>> # Example 2: Check vault health metrics
            >>> report = analytics.generate_workflow_report()
            >>> orphaned_pct = (report['orphaned_count'] / report['total_notes']) * 100
            >>> stale_pct = (report['stale_count'] / report['total_notes']) * 100
            >>> print(f"Vault health:")
            >>> print(f"  - Orphaned: {report['orphaned_count']} ({orphaned_pct:.1f}%)")
            >>> print(f"  - Stale: {report['stale_count']} ({stale_pct:.1f}%)")
            Vault health:
              - Orphaned: 17 (22.4%)
              - Stale: 12 (15.8%)

            >>> # Example 3: Identify workflow bottlenecks
            >>> report = analytics.generate_workflow_report()
            >>> inbox_count = report['notes_by_status'].get('inbox', 0)
            >>> if inbox_count > 20:
            ...     print(f"ALERT: {inbox_count} notes stuck in inbox")
            ...     print("Action: Run weekly review to process backlog")
            ALERT: 35 notes stuck in inbox
            Action: Run weekly review to process backlog

            >>> # Example 4: Track note type distribution
            >>> report = analytics.generate_workflow_report()
            >>> for note_type, count in report['notes_by_type'].items():
            ...     pct = (count / report['total_notes']) * 100
            ...     print(f"{note_type}: {count} ({pct:.1f}%)")
            permanent: 23 (30.3%)
            fleeting: 35 (46.1%)
            literature: 18 (23.7%)

            >>> # Example 5: Quality distribution analysis
            >>> report = analytics.generate_workflow_report()
            >>> scores = report['quality_scores']
            >>> high_quality = sum(1 for s in scores if s >= 0.7)
            >>> medium_quality = sum(1 for s in scores if 0.3 <= s < 0.7)
            >>> low_quality = sum(1 for s in scores if s < 0.3)
            >>> print(f"Quality distribution:")
            >>> print(f"  High (≥0.7): {high_quality} notes")
            >>> print(f"  Medium: {medium_quality} notes")
            >>> print(f"  Low (<0.3): {low_quality} notes")
            Quality distribution:
              High (≥0.7): 28 notes
              Medium: 42 notes
              Low (<0.3): 6 notes
        """
        report = {
            "total_notes": 0,
            "notes_by_type": {},
            "notes_by_status": {},
            "avg_quality_score": 0.0,
            "quality_scores": [],
        }

        # Scan all markdown files
        for md_file in self.base_dir.rglob("*.md"):
            if ".git" in str(md_file) or "Archive" in str(md_file):
                continue

            report["total_notes"] += 1

            # Extract metadata
            try:
                content = md_file.read_text(encoding="utf-8")

                # Parse type
                type_match = re.search(r"type:\s*(\w+)", content)
                if type_match:
                    note_type = type_match.group(1)
                    report["notes_by_type"][note_type] = (
                        report["notes_by_type"].get(note_type, 0) + 1
                    )

                # Parse status
                status_match = re.search(r"status:\s*(\w+)", content)
                if status_match:
                    status = status_match.group(1)
                    report["notes_by_status"][status] = (
                        report["notes_by_status"].get(status, 0) + 1
                    )

                # Calculate quality score
                try:
                    quality_result = self.assess_quality(
                        str(md_file.relative_to(self.base_dir))
                    )
                    report["quality_scores"].append(quality_result["quality_score"])
                except Exception:
                    pass

            except Exception:
                continue

        # Calculate average quality
        if report["quality_scores"]:
            report["avg_quality_score"] = round(
                sum(report["quality_scores"]) / len(report["quality_scores"]), 2
            )

        # Add orphaned and stale counts
        report["orphaned_count"] = len(self.detect_orphaned_notes())
        report["stale_count"] = len(self.detect_stale_notes())

        return report

    def scan_review_candidates(
        self, min_quality_score: Optional[float] = None
    ) -> ReviewCandidate:
        """
        Identify high-quality fleeting notes ready for promotion.

        Scans Fleeting Notes directory for notes that meet quality threshold
        and provides rationale for promotion recommendations.

        Args:
            min_quality_score: Minimum quality threshold (default: 0.7 from config)

        Returns:
            List of promotion candidates sorted by quality score (descending):
            [{
                'note': str (filename),
                'title': str (extracted from content),
                'quality_score': float,
                'metrics': {...component scores...},
                'rationale': str (human-readable reason)
            }]

        Examples:
            >>> # Example 1: Find notes ready for promotion
            >>> analytics = AnalyticsManager(Path('knowledge'), config)
            >>> candidates = analytics.scan_review_candidates()
            >>> print(f"Found {len(candidates)} promotion candidates")
            Found 5 promotion candidates
            >>> for note in candidates:
            ...     print(f"- {note['title']}: {note['quality_score']} - {note['rationale']}")
            - Machine Learning Concepts: 0.85 - Ready for promotion: substantial content, well-categorized, well-connected, complete metadata
            - Design Patterns: 0.78 - Ready for promotion: substantial content, well-connected, complete metadata
            - Research Ideas: 0.72 - Ready for promotion: well-categorized, complete metadata

            >>> # Example 2: Custom quality threshold
            >>> # Strict threshold for only best notes
            >>> candidates = analytics.scan_review_candidates(min_quality_score=0.8)
            >>> print(f"{len(candidates)} notes meet strict threshold (≥0.8)")
            >>> for note in candidates:
            ...     print(f"- {note['title']}: {note['quality_score']}")
            3 notes meet strict threshold (≥0.8)
            - Machine Learning Concepts: 0.85
            - Advanced Algorithms: 0.82

            >>> # Example 3: Lenient threshold for weekly review
            >>> candidates = analytics.scan_review_candidates(min_quality_score=0.6)
            >>> print(f"{len(candidates)} notes ready for review (≥0.6)")
            >>> # These might need minor improvements before promotion
            >>> for note in candidates:
            ...     if note['quality_score'] < 0.7:
            ...         print(f"Needs work: {note['title']} ({note['quality_score']})")
            ...         print(f"  Suggestion: {note['rationale']}")
            8 notes ready for review (≥0.6)
            Needs work: Quick Thoughts (0.65)
              Suggestion: Meets quality threshold

            >>> # Example 4: No candidates found
            >>> candidates = analytics.scan_review_candidates()
            >>> if not candidates:
            ...     print("No fleeting notes ready for promotion")
            ...     print("Continue developing fleeting notes or lower threshold")
            No fleeting notes ready for promotion
            Continue developing fleeting notes or lower threshold

            >>> # Example 5: Inspect candidate metrics
            >>> candidates = analytics.scan_review_candidates()
            >>> for note in candidates[:1]:  # Top candidate
            ...     print(f"{note['title']} - Quality: {note['quality_score']}")
            ...     metrics = note['metrics']
            ...     print(f"  Word score: {metrics['word_score']}")
            ...     print(f"  Tag score: {metrics['tag_score']}")
            ...     print(f"  Link score: {metrics['link_score']}")
            ...     print(f"  Frontmatter: {metrics['frontmatter_score']}")
            Machine Learning Concepts - Quality: 0.85
              Word score: 1.0
              Tag score: 1.0
              Link score: 1.0
              Frontmatter: 1.0

            >>> # Example 6: Use with weekly review automation
            >>> candidates = analytics.scan_review_candidates()
            >>> if candidates:
            ...     print("Weekly Review Checklist:")
            ...     for i, note in enumerate(candidates, 1):
            ...         print(f"{i}. [ ] Review {note['title']} (quality: {note['quality_score']})")
            Weekly Review Checklist:
            1. [ ] Review Machine Learning Concepts (quality: 0.85)
            2. [ ] Review Design Patterns (quality: 0.78)
            3. [ ] Review Research Ideas (quality: 0.72)
        """
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
                # High quality fleeting notes are promotion candidates
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

        # First pass: collect all outgoing links
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

        # Second pass: populate incoming links
        for source_path, links in link_graph.items():
            for target_link in links["outgoing"]:
                # Find target in graph
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
            # Look for first # heading
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
