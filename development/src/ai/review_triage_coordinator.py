"""
Review and Triage Coordinator - ADR-002 Phase 5 Extraction

Coordinates weekly review candidate scanning and fleeting note triage operations.
Extracted from WorkflowManager to maintain single responsibility and reduce class size.

This coordinator handles:
- Weekly review candidate scanning (inbox + fleeting notes)
- AI-powered recommendation generation for weekly review
- Fleeting note triage with quality assessment
- Quality-based categorization and filtering
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

from src.utils.frontmatter import parse_frontmatter
from src.utils.tags import sanitize_tags


class ReviewTriageCoordinator:
    """
    Coordinates review and triage operations for weekly review and fleeting notes.
    
    ADR-002 Phase 5: Extracted from WorkflowManager (~371 LOC reduction).
    
    Responsibilities:
    - Scan directories for review candidates
    - Generate AI-powered weekly recommendations
    - Assess fleeting note quality and generate triage reports
    - Categorize notes by quality thresholds
    
    Integration:
    - Uses WorkflowManager.process_inbox_note() for AI quality assessment
    - Consumed by CLI layer (workflow_demo.py)
    - Independent of other coordinators (Lifecycle, Connection, Analytics, Promotion)
    """

    def __init__(self, base_dir: Path, workflow_manager):
        """
        Initialize ReviewTriageCoordinator.
        
        Args:
            base_dir: Base directory of the Zettelkasten vault
            workflow_manager: WorkflowManager instance for AI processing delegation
        """
        self.base_dir = Path(base_dir)
        self.workflow_manager = workflow_manager
        self.inbox_dir = self.base_dir / "Inbox"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"

    def scan_review_candidates(self) -> List[Dict]:
        """
        Scan for notes that need weekly review attention.
        
        Finds all notes that require review:
        - All .md files in Inbox/ directory (regardless of status)
        - Files in Fleeting Notes/ directory with status: inbox
        
        Returns:
            List of candidate dictionaries with:
                - path: Path object to the note file
                - source: "inbox" or "fleeting" indicating origin
                - metadata: Parsed YAML frontmatter (empty dict if invalid)
        """
        candidates = []

        # Scan inbox directory - all .md files are candidates
        candidates.extend(self._scan_directory_for_candidates(
            self.inbox_dir,
            source_type="inbox",
            filter_func=None  # All inbox files are candidates
        ))

        # Scan fleeting notes directory - only notes with status: inbox
        candidates.extend(self._scan_directory_for_candidates(
            self.fleeting_dir,
            source_type="fleeting",
            filter_func=lambda metadata: metadata.get("status") == "inbox"
        ))

        return candidates

    def _scan_directory_for_candidates(self, directory: Path, source_type: str,
                                     filter_func: Optional[callable] = None) -> List[Dict]:
        """
        Helper method to scan a directory for review candidates.
        
        Args:
            directory: Path to scan
            source_type: Type identifier ("inbox" or "fleeting")
            filter_func: Optional function to filter candidates based on metadata
            
        Returns:
            List of candidate dictionaries
        """
        candidates = []

        if not directory.exists():
            return candidates

        try:
            for note_path in directory.glob("*.md"):
                try:
                    candidate = self._create_candidate_dict(note_path, source_type)

                    # Apply filter if provided
                    if filter_func is None or filter_func(candidate["metadata"]):
                        candidates.append(candidate)

                except Exception as e:
                    # Log error but continue processing other files
                    # For now, include problematic files with empty metadata
                    candidates.append({
                        "path": note_path,
                        "source": source_type,
                        "metadata": {},
                        "error": str(e)
                    })
        except Exception:
            # Handle directory access errors gracefully
            pass

        return candidates

    def _create_candidate_dict(self, note_path: Path, source_type: str) -> Dict:
        """
        Create a candidate dictionary from a note file.
        
        Args:
            note_path: Path to the note file
            source_type: Source type ("inbox" or "fleeting")
            
        Returns:
            Dictionary with path, source, and metadata
            
        Raises:
            Exception: If file cannot be read or processed
        """
        with open(note_path, 'r', encoding='utf-8') as f:
            content = f.read()

        metadata, _ = parse_frontmatter(content)

        return {
            "path": note_path,
            "source": source_type,
            "metadata": metadata
        }

    def generate_weekly_recommendations(self, candidates: List[Dict], dry_run: bool = False) -> Dict:
        """
        Generate AI-powered recommendations for weekly review candidates.
        
        Processes each candidate using existing AI quality assessment and generates
        structured recommendations for weekly review sessions.
        
        Args:
            candidates: List of candidate dictionaries from scan_review_candidates()
            dry_run: If True, use fast mode to skip external AI calls
            
        Returns:
            Dictionary with:
                - summary: Counts by recommendation type
                - recommendations: List of detailed recommendation objects
                - generated_at: ISO timestamp of generation
        """
        result = self._initialize_recommendations_result(len(candidates))

        # Process each candidate with error handling
        for candidate in candidates:
            recommendation = self._process_candidate_for_recommendation(candidate, dry_run=dry_run)
            result["recommendations"].append(recommendation)

            # Update summary counts based on action
            self._update_summary_counts(result["summary"], recommendation["action"])

        return result

    def _initialize_recommendations_result(self, total_candidates: int) -> Dict:
        """
        Initialize the weekly recommendations result structure.
        
        Args:
            total_candidates: Number of candidates being processed
            
        Returns:
            Initialized result dictionary
        """
        return {
            "summary": {
                "total_notes": total_candidates,
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0,
                "processing_errors": 0
            },
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }

    def _process_candidate_for_recommendation(self, candidate: Dict, dry_run: bool = False) -> Dict:
        """
        Process a single candidate and generate its recommendation.
        
        Args:
            candidate: Candidate dictionary with path, source, metadata
            dry_run: If True, use fast mode to avoid external AI calls
            
        Returns:
            Recommendation dictionary for the candidate
        """
        try:
            # Use existing AI processing for quality assessment
            # In dry-run, force fast-mode to avoid external AI calls that may stall
            if dry_run:
                processing_result = self.workflow_manager.process_inbox_note(
                    str(candidate["path"]), dry_run=True, fast=True
                )
            else:
                # Call without kwargs to remain compatible with simple mocks in tests
                processing_result = self.workflow_manager.process_inbox_note(str(candidate["path"]))

            if "error" in processing_result:
                return self._create_error_recommendation(
                    candidate,
                    "Processing failed - manual review required",
                    processing_result["error"]
                )

            # Extract and format the recommendation
            return self._extract_weekly_recommendation(candidate, processing_result)

        except Exception as e:
            return self._create_error_recommendation(
                candidate,
                "Unexpected error during processing",
                str(e)
            )

    def _create_error_recommendation(self, candidate: Dict, reason: str, error: str) -> Dict:
        """
        Create a recommendation for a candidate that failed processing.
        
        Args:
            candidate: Original candidate dictionary
            reason: Human-readable reason for the error
            error: Technical error message
            
        Returns:
            Error recommendation dictionary
        """
        return {
            "file_name": candidate["path"].name,
            "source": candidate["source"],
            "action": "manual_review",
            "reason": reason,
            "error": error,
            "quality_score": None,
            "confidence": None,
            "ai_tags": [],
            "metadata": candidate.get("metadata", {})
        }

    def _update_summary_counts(self, summary: Dict, action: str) -> None:
        """
        Update summary counts based on recommendation action.
        
        Args:
            summary: Summary dictionary to update
            action: Recommendation action type
        """
        if action == "promote_to_permanent":
            summary["promote_to_permanent"] += 1
        elif action == "move_to_fleeting":
            summary["move_to_fleeting"] += 1
        elif action == "improve_or_archive":
            summary["needs_improvement"] += 1
        elif action == "manual_review":
            summary["processing_errors"] += 1

    def _extract_weekly_recommendation(self, candidate: Dict, processing_result: Dict) -> Dict:
        """
        Extract weekly recommendation from processing result.
        
        Args:
            candidate: Original candidate dictionary
            processing_result: Result from process_inbox_note()
            
        Returns:
            Formatted recommendation dictionary
        """
        # Get first recommendation (most important)
        recommendations = processing_result.get("recommendations", [])
        primary_rec = recommendations[0] if recommendations else {
            "action": "manual_review",
            "reason": "No specific recommendation generated",
            "confidence": 0.5
        }

        # Sanitize metadata tags for clean display in weekly outputs (non-destructive)
        metadata = candidate["metadata"] if isinstance(candidate.get("metadata"), dict) else {}
        if metadata:
            try:
                if "tags" in metadata:
                    metadata = {**metadata, "tags": sanitize_tags(metadata.get("tags", []))}
            except Exception:
                # If anything goes wrong, fall back to original metadata
                metadata = candidate.get("metadata", {})

        return {
            "file_name": candidate["path"].name,
            "source": candidate["source"],
            "action": primary_rec["action"],
            "reason": primary_rec["reason"],
            "quality_score": processing_result.get("quality_score"),
            "confidence": primary_rec.get("confidence", 0.5),
            "ai_tags": processing_result.get("processing", {}).get("ai_tags", []),
            "metadata": metadata
        }

    def generate_fleeting_triage_report(self, quality_threshold: Optional[float] = None, fast: bool = False) -> Dict:
        """
        Generate AI-powered triage report for fleeting notes with quality assessment.
        
        Args:
            quality_threshold: Optional minimum quality threshold (0.0-1.0) for filtering
            fast: If True, use fast mode to skip external AI calls for speed
            
        Returns:
            Dict: Triage report with quality assessment and recommendations
        """
        start_time = time.time()

        # Get fleeting notes for processing
        fleeting_notes = self._find_fleeting_notes()

        if not fleeting_notes:
            return {
                'total_notes_processed': 0,
                'quality_distribution': {'high': 0, 'medium': 0, 'low': 0},
                'recommendations': [],
                'processing_time': time.time() - start_time,
                'quality_threshold': quality_threshold
            }

        # Process each note for quality assessment
        recommendations = []
        quality_scores = []

        for note_path in fleeting_notes:
            try:
                # Use existing AI infrastructure for processing
                result = self.workflow_manager.process_inbox_note(note_path, fast=fast)

                quality_score = result.get('quality_score', 0.5)
                quality_scores.append(quality_score)

                # Generate recommendation based on quality
                if quality_score >= 0.7:
                    action = "Promote to Permanent"
                    rationale = "High quality content with clear insights and good structure. Ready for promotion."
                elif quality_score >= 0.4:
                    action = "Needs Enhancement"
                    rationale = "Medium quality with potential. Consider adding more detail or connections."
                else:
                    action = "Consider Archiving"
                    rationale = "Low quality content. May need significant work or could be archived."

                # Apply quality threshold filter if specified
                if quality_threshold is None or quality_score >= quality_threshold:
                    recommendations.append({
                        'note_path': str(note_path),
                        'quality_score': quality_score,
                        'action': action,
                        'rationale': rationale,
                        'ai_tags': result.get('ai_tags', []),
                        'created': result.get('metadata', {}).get('created', 'Unknown')
                    })

            except Exception as e:
                # Handle individual note processing errors gracefully
                recommendations.append({
                    'note_path': str(note_path),
                    'quality_score': 0.0,
                    'action': "Processing Error",
                    'rationale': f"Error processing note: {str(e)}",
                    'ai_tags': [],
                    'created': 'Unknown'
                })

        # Calculate quality distribution
        quality_distribution = {'high': 0, 'medium': 0, 'low': 0}
        for score in quality_scores:
            if score >= 0.7:
                quality_distribution['high'] += 1
            elif score >= 0.4:
                quality_distribution['medium'] += 1
            else:
                quality_distribution['low'] += 1

        # Sort recommendations by quality score (highest first)
        recommendations.sort(key=lambda x: x['quality_score'], reverse=True)

        processing_time = time.time() - start_time
        total_processed = len(fleeting_notes)
        filtered_count = total_processed - len(recommendations) if quality_threshold else 0

        return {
            'total_notes_processed': total_processed,
            'quality_distribution': quality_distribution,
            'recommendations': recommendations,
            'processing_time': processing_time,
            'quality_threshold': quality_threshold,
            'filtered_count': filtered_count
        }

    def _find_fleeting_notes(self) -> List[Path]:
        """Find all fleeting notes for triage processing."""
        fleeting_notes = []

        # Check both Fleeting Notes and Inbox directories
        fleeting_dir = self.base_dir / "Fleeting Notes"
        inbox_dir = self.base_dir / "Inbox"

        for directory in [fleeting_dir, inbox_dir]:
            if directory.exists():
                for note_file in directory.glob("*.md"):
                    try:
                        content = note_file.read_text(encoding='utf-8')
                        metadata, _ = parse_frontmatter(content)

                        # Include notes that are explicitly fleeting type or in fleeting directory
                        if (metadata.get('type') == 'fleeting' or
                            directory.name == "Fleeting Notes"):
                            fleeting_notes.append(note_file)

                    except Exception:
                        # Skip files that can't be read or parsed
                        continue

        return fleeting_notes
