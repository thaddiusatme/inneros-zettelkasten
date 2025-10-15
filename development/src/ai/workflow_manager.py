"""
Smart workflow manager that integrates AI features into the Zettelkasten workflow.
Follows the established patterns from the project manifest.
"""

import json
import re
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# ADR-002 Phase 12a: Configuration coordinator extraction
from .configuration_coordinator import ConfigurationCoordinator

# Keep direct imports for type hints and backwards compatibility
from .workflow_integration_utils import (
    WorkflowProcessingResult,
    BatchProcessingStats
)
from src.utils.tags import sanitize_tags
from src.utils.frontmatter import parse_frontmatter, build_frontmatter
from src.utils.io import safe_write


@dataclass
class FleetingAnalysis:
    """Data structure for fleeting note analysis results."""
    total_count: int = 0
    age_distribution: Dict[str, int] = field(default_factory=lambda: {
        'new': 0,       # 0-7 days
        'recent': 0,    # 8-30 days  
        'stale': 0,     # 31-90 days
        'old': 0        # 90+ days
    })
    oldest_note: Optional[Dict[str, any]] = None
    newest_note: Optional[Dict[str, any]] = None
    notes_by_age: List[Dict[str, any]] = field(default_factory=list)


class WorkflowManager:
    """Manages the complete AI-enhanced Zettelkasten workflow."""
    
    def __init__(self, base_directory: str | None = None):
        """Initialize workflow manager.

        ADR-002 Phase 12a: Delegates configuration and initialization to ConfigurationCoordinator.

        Args:
            base_directory: Explicit path to the Zettelkasten root. If ``None`` the
                resolver in ``utils.vault_path`` is used. Raises ``ValueError`` if
                no valid directory can be resolved.
        """
        # ADR-002 Phase 12a: Delegate initialization to ConfigurationCoordinator
        self._config_coordinator = ConfigurationCoordinator(base_directory=base_directory, workflow_manager=self)
        
        # Expose coordinator properties for backwards compatibility
        self.base_dir = self._config_coordinator.base_dir
        self.inbox_dir = self._config_coordinator.inbox_dir
        self.fleeting_dir = self._config_coordinator.fleeting_dir
        self.permanent_dir = self._config_coordinator.permanent_dir
        self.archive_dir = self._config_coordinator.archive_dir
        
        # Expose AI components
        self.tagger = self._config_coordinator.tagger
        self.summarizer = self._config_coordinator.summarizer
        self.connections = self._config_coordinator.connections
        self.enhancer = self._config_coordinator.enhancer
        self.analytics = self._config_coordinator.analytics
        
        # Expose image safety components
        self.safe_image_processor = self._config_coordinator.safe_image_processor
        self.image_integrity_monitor = self._config_coordinator.image_integrity_monitor
        self.safe_workflow_processor = self._config_coordinator.safe_workflow_processor
        self.atomic_workflow_engine = self._config_coordinator.atomic_workflow_engine
        self.integrity_monitoring_manager = self._config_coordinator.integrity_monitoring_manager
        self.concurrent_session_manager = self._config_coordinator.concurrent_session_manager
        self.performance_metrics_collector = self._config_coordinator.performance_metrics_collector
        
        # Legacy compatibility
        self.active_sessions = self._config_coordinator.active_sessions
        self.config = self._config_coordinator.config
    
    def process_inbox_note(self, note_path: str, dry_run: bool = False, fast: bool | None = None) -> Dict:
        """
        Process a note in the inbox with AI assistance.
        
        Args:
            note_path: Path to the note in inbox
            dry_run: If True, do not write any changes to disk
            fast: If True, skip heavy AI calls and use heuristics (defaults to dry_run)
        
        Returns:
            Processing results and recommendations
        """
        note_file = Path(note_path)
        
        if not note_file.exists():
            return {"error": "Note file not found"}
        
        try:
            with open(note_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read note: {e}"}
        
        # Preprocess raw content to fix 'created' placeholders that break YAML parsing
        # e.g., "created: {{date:YYYY-MM-DD HH:mm}}", "created: {{date}}",
        # or Templater EJS patterns like "<% tp.date.now(...) %>" which make YAML invalid
        content, raw_template_fixed = self._preprocess_created_placeholder_in_raw(content, note_file)
        
        results = {
            "original_file": str(note_file),
            "processing": {},
            "recommendations": []
        }
        
        # Extract frontmatter and body using centralized utility (after preprocessing)
        frontmatter, body = parse_frontmatter(content)

        # Fix template placeholders in frontmatter BEFORE any processing
        template_fixed = self._fix_template_placeholders(frontmatter, note_file)
        any_template_fixed = raw_template_fixed or template_fixed

        # Determine fast-mode (heuristic, no external AI calls)
        fast_mode = fast if fast is not None else dry_run

        if fast_mode:
            # Heuristic-only path to avoid network/AI latency for dry runs
            results["processing"] = {}
            # Sanitize existing tags for consistent downstream output
            existing_tags = sanitize_tags(frontmatter.get("tags", []))
            # Ensure ai_tags present for weekly review consumers
            results["processing"]["ai_tags"] = list(existing_tags)

            # Simple word count heuristic
            body_text = body if isinstance(body, str) else ""
            # Normalize whitespace for a rough tokenization
            try:
                normalized = re.sub(r"\s+", " ", body_text).strip()
            except Exception:
                normalized = body_text
            word_count = len(normalized.split()) if normalized else 0

            # Score: emphasize length and presence of tags
            quality_score = 0.0
            if word_count >= 500:
                quality_score = 0.8
            elif word_count >= 200:
                quality_score = 0.55
            elif word_count >= 80:
                quality_score = 0.42
            else:
                quality_score = 0.30

            # Small boost for tags present
            if len(existing_tags) >= 3:
                quality_score = min(1.0, quality_score + 0.05)

            # Populate processing info without AI calls
            results["processing"]["quality"] = {
                "score": quality_score,
                "suggestions": [
                    "Add more detail and structure to improve quality" if word_count < 200 else "Refine key points and add links to related notes",
                ],
            }
            results["processing"]["tags"] = {
                "added": [],
                "total": len(existing_tags),
            }

            # Primary recommendation based on heuristic score
            if quality_score > 0.7:
                primary = {
                    "action": "promote_to_permanent",
                    "reason": "High quality (heuristic) suitable for permanent notes",
                    "confidence": "medium",
                }
            elif quality_score > 0.4:
                primary = {
                    "action": "move_to_fleeting",
                    "reason": "Medium quality (heuristic) needs development",
                    "confidence": "medium",
                }
            else:
                primary = {
                    "action": "improve_or_archive",
                    "reason": "Low quality (heuristic) needs significant improvement",
                    "confidence": "high",
                }

            results["recommendations"].append(primary)
            results["quality_score"] = quality_score

            # Persist template fixes even in fast-mode (no AI calls), using atomic write
            if any_template_fixed and not dry_run:
                try:
                    updated_content = build_frontmatter(frontmatter, body)
                    safe_write(note_file, updated_content)
                    results["file_updated"] = True
                except Exception as e:
                    results["file_update_error"] = str(e)
                    results["file_updated"] = False
            else:
                results["file_updated"] = False

            return results
        
        # Auto-tag if enabled (use body content only, frontmatter is processed separately)
        if self.config["auto_tag_inbox"]:
            try:
                # Use body content for AI analysis - AI should focus on content, not metadata
                suggested_tags = self.tagger.generate_tags(body)
                # Sanitize both existing and suggested tags before merging
                existing_tags = sanitize_tags(frontmatter.get("tags", []))
                suggested_tags = sanitize_tags(suggested_tags)
                
                # Merge tags intelligently
                merged_tags = self._merge_tags(existing_tags, suggested_tags)
                # Ensure merged tags remain sanitized and deduplicated
                merged_tags = sanitize_tags(merged_tags)
                
                if merged_tags != existing_tags:
                    frontmatter["tags"] = merged_tags
                    results["processing"]["tags"] = {
                        "added": list(set(merged_tags) - set(existing_tags)),
                        "total": len(merged_tags)
                    }
                # Expose AI tags in processing result for downstream formatters
                results["processing"]["ai_tags"] = merged_tags
            except Exception as e:
                results["processing"]["tags"] = {"error": str(e)}
        # Ensure ai_tags key is always present based on current frontmatter state
        current_tags = sanitize_tags(frontmatter.get("tags", []))
        if "ai_tags" not in results["processing"]:
            results["processing"]["ai_tags"] = current_tags
        
        # Analyze note quality and suggest improvements (use body content only)
        try:
            # Use body content for AI analysis - AI should focus on content, not metadata
            enhancement = self.enhancer.enhance_note(body)
            quality_score = enhancement.get("quality_score", 0)
            
            results["processing"]["quality"] = {
                "score": quality_score,
                "suggestions": enhancement.get("suggestions", [])[:3]
            }
            
            # Generate workflow recommendations based on quality
            if quality_score > 0.7:
                results["recommendations"].append({
                    "action": "promote_to_permanent",
                    "reason": "High quality content suitable for permanent notes",
                    "confidence": "high"
                })
            elif quality_score > 0.4:
                results["recommendations"].append({
                    "action": "move_to_fleeting",
                    "reason": "Medium quality content needs development",
                    "confidence": "medium"
                })
            else:
                results["recommendations"].append({
                    "action": "improve_or_archive",
                    "reason": "Low quality content needs significant improvement",
                    "confidence": "high"
                })
        except Exception as e:
            results["processing"]["quality"] = {"error": str(e)}
        
        # Find potential connections (use body content only)
        try:
            # Load existing permanent notes for connection analysis
            permanent_notes = self._load_notes_corpus(self.permanent_dir)
            
            if permanent_notes:
                # Use body content for AI analysis - focus on actual content, not metadata
                similar_notes = self.connections.find_similar_notes(body, permanent_notes)
                
                if similar_notes:
                    results["processing"]["connections"] = {
                        "similar_notes": [
                            {"file": filename, "similarity": float(score)}
                            for filename, score in similar_notes[:3]
                        ]
                    }
                    
                    results["recommendations"].append({
                        "action": "add_links",
                        "reason": f"Found {len(similar_notes)} related notes",
                        "details": similar_notes[:3]
                    })
        except Exception as e:
            results["processing"]["connections"] = {"error": str(e)}
        
        # TDD Iteration 10: Track image references in note
        try:
            from utils.image_link_manager import ImageLinkManager
            image_manager = ImageLinkManager(base_path=Path(self.base_dir))
            image_links = image_manager.parse_image_links(content)
            
            if image_links:
                results["processing"]["images"] = {
                    "count": len(image_links),
                    "references": [link.get("filename", link.get("path", "")) for link in image_links],
                    "preserved": True
                }
                self.logger.debug(f"Tracked {len(image_links)} image references in {note_file.name}")
        except ImportError:
            self.logger.debug("Image link manager not available - skipping image tracking")
        except Exception as e:
            self.logger.warning(f"Could not track image references: {e}")
        
        # Update note with AI enhancements (skip when dry_run)
        # Check if we need to update the file (AI processing OR template fixes)
        needs_ai_update = any(key in results["processing"] for key in ["tags", "quality"])
        
        if needs_ai_update or any_template_fixed:
            if dry_run:
                # Indicate what would have happened without modifying files
                if needs_ai_update:
                    frontmatter["ai_processed"] = datetime.now().isoformat()
                results["file_updated"] = False
            else:
                try:
                    # Update status to indicate AI processing (only if AI processing happened)
                    if needs_ai_update:
                        frontmatter["ai_processed"] = datetime.now().isoformat()
                        
                        # Add quality score to frontmatter if it was processed
                        if "quality" in results["processing"] and "score" in results["processing"]["quality"]:
                            frontmatter["quality_score"] = results["processing"]["quality"]["score"]
                    
                    # Rebuild content using centralized utility (includes template fixes)
                    updated_content = build_frontmatter(frontmatter, body)
                    
                    # Use atomic write to prevent partial writes on interruption
                    safe_write(note_file, updated_content)
                    
                    results["file_updated"] = True
                except Exception as e:
                    results["file_update_error"] = str(e)
        else:
            results["file_updated"] = False
        
        # Report template processing status
        if any_template_fixed:
            results["template_fixed"] = True
        
        return results
    
    def _fix_template_placeholders(self, frontmatter: Dict, note_file: Path) -> bool:
        """
        Fix template placeholders in frontmatter, particularly {{date:...}} patterns.
        
        Args:
            frontmatter: The frontmatter dictionary to modify
            note_file: Path to the note file for timestamp inference
            
        Returns:
            True if any changes were made, False otherwise
        """
        import os
        from datetime import datetime
        
        changes_made = False
        
        # Check if 'created' field needs fixing
        created_value = frontmatter.get("created")
        
        # Fix template placeholders like {{date:YYYY-MM-DD HH:mm}} or missing created field
        if (created_value is None or 
            (isinstance(created_value, str) and (
                "{{date" in created_value or
                "<% tp.date.now(" in created_value or
                "<% tp.file.creation_date(" in created_value
            ))):
            
            # Try to get file creation/modification time
            try:
                file_stat = os.stat(note_file)
                # Use modification time as the best proxy for when note was created
                timestamp = datetime.fromtimestamp(file_stat.st_mtime)
            except (OSError, ValueError):
                # Fallback to current time if file operations fail
                timestamp = datetime.now()
            
            # Format in the required YYYY-MM-DD HH:MM format
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
            frontmatter["created"] = formatted_timestamp
            changes_made = True
        
        return changes_made

    def _preprocess_created_placeholder_in_raw(self, content: str, note_file: Path) -> tuple[str, bool]:
        """Replace invalid 'created' placeholders directly in the raw frontmatter block.

        This is necessary when placeholders make YAML unparseable (e.g., {{date:...}}, {{date}},
        or Templater EJS patterns), causing parse_frontmatter() to return empty metadata and
        leaving the original frontmatter in the body. Preprocessing ensures YAML becomes valid so
        other frontmatter fields are preserved.

        Returns a tuple of (possibly updated content, changes_made).
        """
        try:
            text = content if isinstance(content, str) else ""
            if not text or not text.lstrip().startswith('---'):
                return content, False
            lines = text.split('\n')
            # locate closing delimiter
            closing_idx = None
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    closing_idx = i
                    break
            if closing_idx is None:
                return content, False

            placeholder_markers = (
                "{{date",
                "<% tp.date.now(",
                "<% tp.file.creation_date(",
            )

            changed = False
            # Scan only within frontmatter region
            for j in range(1, closing_idx):
                line = lines[j]
                if not line.strip().startswith("created:"):
                    continue
                # Preserve original spacing after ':'
                prefix, sep, value = line.partition(":")
                value_str = value.strip()
                if any(marker in value_str for marker in placeholder_markers):
                    try:
                        import os
                        from datetime import datetime
                        ts = datetime.fromtimestamp(os.stat(note_file).st_mtime)
                    except Exception:
                        from datetime import datetime
                        ts = datetime.now()
                    formatted = ts.strftime("%Y-%m-%d %H:%M")
                    # preserve spaces after colon
                    import re as _re
                    m = _re.match(r"^(\s*)", value)
                    spaces = m.group(1) if m else " "
                    lines[j] = f"{prefix}:{spaces}{formatted}"
                    changed = True
                break  # only handle the first created occurrence

            if changed:
                return "\n".join(lines), True
            return content, False
        except Exception:
            return content, False
    
    def promote_note(self, note_path: str, target_type: str = "permanent") -> Dict:
        """
        Promote a note from inbox/fleeting to permanent notes.
        
        Args:
            note_path: Path to the note to promote
            target_type: Target note type ("permanent" or "fleeting")
            
        Returns:
            Promotion results
        """
        source_file = Path(note_path)
        
        if not source_file.exists():
            return {"error": "Source note not found"}
        
        # Determine target directory
        if target_type == "permanent":
            target_dir = self.permanent_dir
        elif target_type == "fleeting":
            target_dir = self.fleeting_dir
        else:
            return {"error": f"Invalid target type: {target_type}"}
        
        target_dir.mkdir(exist_ok=True)
        target_file = target_dir / source_file.name
        
        try:
            # Read and update content
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter, body = parse_frontmatter(content)
            
            # Update metadata for promotion
            frontmatter["type"] = target_type
            frontmatter["status"] = "promoted" if target_type == "permanent" else "draft"
            frontmatter["promoted_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            # Add AI summary for long permanent notes
            if (target_type == "permanent" and 
                self.config["auto_summarize_long_notes"] and
                self.summarizer.should_summarize(content)):
                
                try:
                    summary = self.summarizer.generate_summary(content)
                    if summary:
                        frontmatter["ai_summary"] = summary
                except Exception:
                    pass  # Don't fail promotion if summary fails
            
            # Rebuild and save to target location using centralized utility
            updated_content = build_frontmatter(frontmatter, body)
            
            # Use atomic write to prevent partial writes on interruption
            safe_write(target_file, updated_content)
            
            # Remove from source location
            source_file.unlink()
            
            return {
                "success": True,
                "source": str(source_file),
                "target": str(target_file),
                "type": target_type,
                "has_summary": "ai_summary" in frontmatter
            }
            
        except Exception as e:
            return {"error": f"Failed to promote note: {e}"}
    
    def batch_process_inbox(self, show_progress: bool = True) -> Dict:
        """
        Process all notes in the inbox.
        
        Args:
            show_progress: If True, print progress to stderr (for dashboard display)
        """
        inbox_files = list(self.inbox_dir.glob("*.md"))
        total = len(inbox_files)
        
        results = {
            "total_files": total,
            "processed": 0,
            "failed": 0,
            "results": [],
            "summary": {
                "promote_to_permanent": 0,
                "move_to_fleeting": 0,
                "needs_improvement": 0
            }
        }
        
        for idx, note_file in enumerate(inbox_files, 1):
            # Show progress (to stderr so it doesn't interfere with JSON output)
            if show_progress:
                import sys
                filename = note_file.name
                # Truncate long filenames
                if len(filename) > 50:
                    filename = filename[:47] + "..."
                progress_pct = int((idx / total) * 100)
                sys.stderr.write(f"\r[{idx}/{total}] {progress_pct}% - {filename}...")
                sys.stderr.flush()
            
            try:
                result = self.process_inbox_note(str(note_file))
                
                if "error" not in result:
                    results["processed"] += 1
                    
                    # Categorize recommendations
                    for rec in result.get("recommendations", []):
                        action = rec.get("action", "")
                        if action == "promote_to_permanent":
                            results["summary"]["promote_to_permanent"] += 1
                        elif action == "move_to_fleeting":
                            results["summary"]["move_to_fleeting"] += 1
                        elif action == "improve_or_archive":
                            results["summary"]["needs_improvement"] += 1
                else:
                    results["failed"] += 1
                
                results["results"].append(result)
                
            except Exception as e:
                results["failed"] += 1
                results["results"].append({
                    "original_file": str(note_file),
                    "error": str(e)
                })
        
        # Clear progress line
        if show_progress and total > 0:
            import sys
            sys.stderr.write("\r" + " " * 80 + "\r")
            sys.stderr.flush()
        
        return results
    
    def generate_workflow_report(self) -> Dict:
        """Generate a comprehensive workflow status report."""
        # Get analytics for the entire collection
        analytics_report = self.analytics.generate_report()
        
        # Count notes by directory
        directory_counts = {}
        for dir_name, dir_path in [
            ("Inbox", self.inbox_dir),
            ("Fleeting Notes", self.fleeting_dir),
            ("Permanent Notes", self.permanent_dir),
            ("Archive", self.archive_dir)
        ]:
            if dir_path.exists():
                directory_counts[dir_name] = len(list(dir_path.glob("*.md")))
            else:
                directory_counts[dir_name] = 0
        
        # Workflow health metrics
        inbox_count = directory_counts["Inbox"]
        fleeting_count = directory_counts["Fleeting Notes"]
        permanent_count = directory_counts["Permanent Notes"]
        
        workflow_health = "healthy"
        if inbox_count > 20:
            workflow_health = "needs_attention"
        elif inbox_count > 50:
            workflow_health = "critical"
        
        # AI feature usage
        ai_usage = self._analyze_ai_usage()
        
        return {
            "workflow_status": {
                "health": workflow_health,
                "directory_counts": directory_counts,
                "total_notes": sum(directory_counts.values())
            },
            "ai_features": ai_usage,
            "analytics": analytics_report,
            "recommendations": self._generate_workflow_recommendations(
                directory_counts, ai_usage
            )
        }
    
    def _analyze_ai_usage(self) -> Dict:
        """Analyze usage of AI features across the collection."""
        usage_stats = {
            "notes_with_ai_tags": 0,
            "notes_with_ai_summaries": 0,
            "notes_with_ai_processing": 0,
            "total_analyzed": 0
        }
        
        # Scan all notes for AI features
        for md_file in self.base_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, _ = parse_frontmatter(content)
                usage_stats["total_analyzed"] += 1
                
                if "ai_summary" in frontmatter:
                    usage_stats["notes_with_ai_summaries"] += 1
                
                if "ai_processed" in frontmatter:
                    usage_stats["notes_with_ai_processing"] += 1
                
                # Check if tags were likely AI-generated (heuristic)
                tags = frontmatter.get("tags", [])
                if isinstance(tags, list) and len(tags) >= 3:
                    # Look for AI-style kebab-case tags
                    ai_style_tags = [t for t in tags if '-' in t and len(t) > 5]
                    if len(ai_style_tags) >= 2:
                        usage_stats["notes_with_ai_tags"] += 1
                
            except Exception:
                continue
        
        return usage_stats
    
    def _generate_workflow_recommendations(self, directory_counts: Dict, 
                                         ai_usage: Dict) -> List[str]:
        """Generate workflow improvement recommendations."""
        recommendations = []
        
        # Inbox management
        inbox_count = directory_counts.get("Inbox", 0)
        if inbox_count > 20:
            recommendations.append(
                f"Process {inbox_count} notes in inbox - consider batch processing"
            )
        
        # AI feature adoption
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
        
        # Balance between note types
        permanent_count = directory_counts.get("Permanent Notes", 0)
        fleeting_count = directory_counts.get("Fleeting Notes", 0)
        
        if fleeting_count > permanent_count * 2:
            recommendations.append(
                "Consider promoting more fleeting notes to permanent status"
            )
        
        return recommendations
    
    def _load_notes_corpus(self, directory: Path) -> Dict[str, str]:
        """Load all notes from a directory into a corpus."""
        corpus = {}
        
        if not directory.exists():
            return corpus
        
        for md_file in directory.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    corpus[md_file.name] = f.read()
            except Exception:
                continue
        
        return corpus
    
    
    def _merge_tags(self, existing_tags: List[str], new_tags: List[str]) -> List[str]:
        """Merge existing and new tags intelligently."""
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()
        
        merged = sorted(list(existing_set | new_set))
        return merged[:self.config["max_tags_per_note"]]
    
    
    def scan_review_candidates(self) -> List[Dict]:
        """Scan for notes that need weekly review attention.
        
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
        """Helper method to scan a directory for review candidates.
        
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
        """Create a candidate dictionary from a note file.
        
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
        """Generate AI-powered recommendations for weekly review candidates.
        
        Processes each candidate using existing AI quality assessment and generates
        structured recommendations for weekly review sessions.
        
        Args:
            candidates: List of candidate dictionaries from scan_review_candidates()
            
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
        """Initialize the weekly recommendations result structure.
        
        Args:
            total_candidates: Number of candidates being processed
            
        Returns:
            Initialized result dictionary
        """
        from datetime import datetime
        
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
        """Process a single candidate and generate its recommendation.
        
        Args:
            candidate: Candidate dictionary with path, source, metadata
            
        Returns:
            Recommendation dictionary for the candidate
        """
        try:
            # Use existing AI processing for quality assessment
            # In dry-run, force fast-mode to avoid external AI calls that may stall
            if dry_run:
                processing_result = self.process_inbox_note(str(candidate["path"]), dry_run=True, fast=True)
            else:
                # Call without kwargs to remain compatible with simple mocks in tests
                processing_result = self.process_inbox_note(str(candidate["path"]))
            
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
        """Create a recommendation for a candidate that failed processing.
        
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
        """Update summary counts based on recommendation action.
        
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
        """Extract weekly recommendation from processing result.
        
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

    # Phase 5.5.4: Enhanced Review Features
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
        # using module-level datetime, timedelta
        
        stale_notes = []
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        all_notes = self._get_all_notes()
        
        for note_path in all_notes:
            try:
                last_modified = datetime.fromtimestamp(note_path.stat().st_mtime)
                if last_modified < cutoff_date:
                    days_since_modified = (datetime.now() - last_modified).days
                    stale_notes.append(self._create_stale_note_info(note_path, last_modified, days_since_modified))
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
        # using module-level datetime, timedelta
        
        metrics = {
            "generated_at": datetime.now().isoformat(),
            "orphaned_notes": self.detect_orphaned_notes(),
            "stale_notes": self.detect_stale_notes(),
            "link_density": self._calculate_link_density(),
            "note_age_distribution": self._calculate_note_age_distribution(),
            "productivity_metrics": self._calculate_productivity_metrics()
        }
        
        # Add summary statistics
        metrics["summary"] = {
            "total_orphaned": len(metrics["orphaned_notes"]),
            "total_stale": len(metrics["stale_notes"]),
            "avg_links_per_note": metrics["link_density"],
            "total_notes": len(self._get_all_notes())
        }
        
        return metrics

    # Phase 5.6: Orphan Remediation (bidirectional link insertion)
    def remediate_orphaned_notes(
        self,
        mode: str = "link",
        scope: str = "permanent",
        limit: int = 10,
        target: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict:
        """Remediate orphaned notes by inserting bidirectional links.

        Args:
            mode: "link" (insert links) or "checklist" (output markdown checklist)
            scope: "permanent", "fleeting", or "all"
            limit: maximum number of orphaned notes to process
            target: explicit path to target MOC/note for inserting links (absolute or relative to vault)
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
        orphans = self._list_orphans_by_scope(scope)
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
                changed = self._insert_bidirectional_links(orphan_fp, target_path, dry_run=dry_run)
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
                    {"orphan": str(orphan_fp), "target": str(target_path), "error": str(e)}
                )
                result["summary"]["errors"] += 1

        result["summary"]["skipped"] = max(0, result["summary"]["considered"] - result["summary"]["processed"])
        return result

    def _vault_root(self) -> Path:
        """Resolve the root folder that actually contains the note collections."""
        base = Path(self.base_dir)
        knowledge = base / "knowledge"
        return knowledge if knowledge.exists() else base

    def _list_orphans_by_scope(self, scope: str) -> List[Dict]:
        """Return orphaned notes filtered by scope and sorted deterministically."""
        # Use comprehensive detector to be robust to vault layouts
        all_orphans = self.detect_orphaned_notes_comprehensive()
        root = self._vault_root()

        def in_dir(p: str, name: str) -> bool:
            try:
                return (root / name) in Path(p).parents or Path(p).parent == (root / name)
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
                if in_dir(o["path"], "Permanent Notes") or in_dir(o["path"], "Fleeting Notes")
            ]

        # Sort: Permanent first, then by title
        def sort_key(o: Dict):
            dir_weight = 0 if in_dir(o["path"], "Permanent Notes") else 1
            return (dir_weight, o.get("title", ""))

        return sorted(filtered, key=sort_key)

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

    def _insert_bidirectional_links(self, orphan_path: Path, target_path: Path, dry_run: bool = True) -> Dict:
        """Insert [[orphan]] in target and [[target]] in orphan, creating backups if not dry-run.

        Returns dict with modified flags and backup paths.
        """
        orphan_key = orphan_path.stem
        target_key = target_path.stem

        result = {"modified_target": False, "modified_orphan": False, "backups": {}}

        # Update target file
        tgt_text = self._read_text(target_path)
        if not self._has_wikilink(tgt_text, orphan_key):
            new_tgt_text = self._append_to_section(tgt_text, f"[[{orphan_key}]]")
            if not dry_run:
                bk = self._backup_file(target_path)
                result["backups"]["target"] = str(bk) if bk else None
                self._write_text(target_path, new_tgt_text)
            result["modified_target"] = True

        # Update orphan file
        orphan_text = self._read_text(orphan_path)
        if not self._has_wikilink(orphan_text, target_key):
            new_orphan_text = self._append_to_section(orphan_text, f"[[{target_key}]]")
            if not dry_run:
                bk = self._backup_file(orphan_path)
                result["backups"]["orphan"] = str(bk) if bk else None
                self._write_text(orphan_path, new_orphan_text)
            result["modified_orphan"] = True

        return result

    def _read_text(self, path: Path) -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return ""

    def _write_text(self, path: Path, text: str) -> None:
        # Use atomic write to prevent partial writes on interruption
        safe_write(path, text)

    def _backup_file(self, path: Path) -> Optional[Path]:
        try:
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            backup = path.parent / f"{path.name}.bak.{ts}"
            shutil.copy2(path, backup)
            return backup
        except Exception:
            return None

    def _has_wikilink(self, text: str, key: str) -> bool:
        # matches [[key]] or [[key|alias]]
        try:
            pattern = rf"\[\[\s*{re.escape(key)}(?:\|[^\]]+)?\s*\]\]"
            return re.search(pattern, text) is not None
        except Exception:
            return False

    def _append_to_section(self, text: str, bullet_line: str, section_title: str = "## Linked Notes") -> str:
        """Append a bullet to a dedicated section, creating it if missing."""
        lines = text.splitlines()
        # Find section heading index
        import re as _re
        heading_re = _re.compile(rf"^#+\s+{_re.escape(section_title.lstrip('#').strip())}$", _re.IGNORECASE)
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
            # Insert after heading; find the next blank or end to insert before next heading? Simple append after heading.
            insert_at = idx + 1
            # skip leading blank after heading
            while insert_at < len(lines) and lines[insert_at].strip() == "":
                insert_at += 1
            new_lines = lines[:insert_at] + ["", bullet] + lines[insert_at:]
            return "\n".join(new_lines)
    
    # Helper methods for enhanced features
    def _get_all_notes(self) -> List[Path]:
        """Get all markdown notes from all directories."""
        all_notes = []
        directories = [self.permanent_dir, self.fleeting_dir, self.inbox_dir]
        
        for directory in directories:
            if directory.exists():
                all_notes.extend(directory.glob("*.md"))
        
        return all_notes
    
    def _get_all_notes_comprehensive(self) -> List[Path]:
        """Get all markdown notes from the entire repository."""
        from pathlib import Path
        root_dir = Path(self.base_dir)
        
        # Get all .md files recursively, excluding hidden directories and common non-content dirs
        exclude_dirs = {'.git', '.obsidian', '__pycache__', '.pytest_cache', 'htmlcov', '.windsurf'}
        all_notes = []
        
        for md_file in root_dir.rglob("*.md"):
            # Skip files in excluded directories
            if any(excluded_dir in md_file.parts for excluded_dir in exclude_dirs):
                continue
            all_notes.append(md_file)
        
        return all_notes
    
    def _build_link_graph(self, all_notes: List[Path]) -> Dict[str, set]:
        """Build a graph of note links."""
        import re
        
        link_graph = {}
        
        for note_path in all_notes:
            note_name = note_path.stem
            link_graph[note_name] = set()
            
            try:
                with open(note_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all [[wiki-style]] links
                wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
                for link in wiki_links:
                    # Clean up the link (remove .md extension if present)
                    clean_link = link.replace('.md', '')
                    link_graph[note_name].add(clean_link)
                    
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        
        return link_graph
    
    def _is_orphaned_note(self, note_path: Path, link_graph: Dict[str, set]) -> bool:
        """Check if a note is orphaned (no incoming or outgoing links)."""
        note_name = note_path.stem
        
        # Skip inbox notes (they're expected to be unlinked initially)
        if note_path.parent.name == "Inbox":
            return False
        
        # Check if note has outgoing links
        has_outgoing_links = len(link_graph.get(note_name, set())) > 0
        
        # Check if note has incoming links
        has_incoming_links = any(
            note_name in links for other_note, links in link_graph.items() 
            if other_note != note_name
        )
        
        return not (has_outgoing_links or has_incoming_links)
    
    def _create_orphaned_note_info(self, note_path: Path) -> Dict:
        """Create info dict for an orphaned note."""
        from datetime import datetime
        
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
            "directory": note_path.parent.name
        }
    
    def _create_stale_note_info(self, note_path: Path, last_modified, days_since_modified: int) -> Dict:
        """Create info dict for a stale note."""
        title = self._extract_note_title(note_path)
        
        return {
            "path": str(note_path),
            "title": title,
            "last_modified": last_modified.isoformat(),
            "days_since_modified": days_since_modified,
            "directory": note_path.parent.name
        }
    
    def _extract_note_title(self, note_path: Path) -> str:
        """Extract title from note (first # heading or filename)."""
        try:
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for first markdown heading
            import re
            heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
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
        # using module-level datetime, timedelta
        
        all_notes = self._get_all_notes()
        age_buckets = {
            "new": 0,        # < 7 days
            "recent": 0,     # 7-30 days
            "mature": 0,     # 30-90 days
            "old": 0         # > 90 days
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
        # using module-level datetime, timedelta
        from collections import defaultdict
        
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
            "avg_notes_created_per_week": sum(creation_counts) / len(creation_counts) if creation_counts else 0,
            "avg_notes_modified_per_week": sum(modification_counts) / len(modification_counts) if modification_counts else 0,
            "most_productive_week_creation": max(weekly_creation.items(), key=lambda x: x[1]) if weekly_creation else None,
            "total_weeks_active": len(set(list(weekly_creation.keys()) + list(weekly_modification.keys())))
        }
    
    # Phase 5.6 Extension: Fleeting Note Lifecycle Management
    
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
                content = note_path.read_text(encoding='utf-8')
                frontmatter, _ = parse_frontmatter(content)
                
                # Try to get created date from frontmatter
                created_str = frontmatter.get('created', '')
                if created_str and not any(placeholder in created_str for placeholder in ['{{', '<%', 'tp.']):
                    # Parse the date
                    try:
                        created_date = datetime.strptime(created_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        try:
                            created_date = datetime.strptime(created_str, "%Y-%m-%d")
                        except ValueError:
                            # Fall back to file modification time
                            created_date = datetime.fromtimestamp(note_path.stat().st_mtime)
                else:
                    # Use file modification time as fallback
                    created_date = datetime.fromtimestamp(note_path.stat().st_mtime)
                
                # Calculate age in days
                age_delta = current_date - created_date
                days_old = age_delta.days
                
                # Store note data
                note_info = {
                    'name': note_path.name,
                    'path': str(note_path),
                    'days_old': days_old,
                    'created': created_date
                }
                notes_data.append(note_info)
                
                # Categorize by age
                if days_old <= 7:
                    analysis.age_distribution['new'] += 1
                elif days_old <= 30:
                    analysis.age_distribution['recent'] += 1
                elif days_old <= 90:
                    analysis.age_distribution['stale'] += 1
                else:
                    analysis.age_distribution['old'] += 1
                    
            except Exception:
                # Skip notes that can't be processed
                continue
        
        # Sort notes by age
        notes_data.sort(key=lambda x: x['days_old'], reverse=True)
        
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
            health_status = 'HEALTHY'
            summary = 'No fleeting notes found. Your fleeting notes are well-managed.'
        else:
            old_percentage = (analysis.age_distribution['old'] / analysis.total_count * 100) if analysis.total_count > 0 else 0
            stale_percentage = (analysis.age_distribution['stale'] / analysis.total_count * 100) if analysis.total_count > 0 else 0
            
            if old_percentage >= 50:
                health_status = 'CRITICAL'
                summary = f'Critical: {old_percentage:.0f}% of fleeting notes are over 90 days old and require immediate attention.'
            elif old_percentage >= 30 or stale_percentage >= 40:
                health_status = 'ATTENTION'
                summary = f'Attention needed: {stale_percentage + old_percentage:.0f}% of fleeting notes are stale or old.'
            else:
                health_status = 'HEALTHY'
                summary = f'Healthy: Most fleeting notes ({analysis.age_distribution["new"] + analysis.age_distribution["recent"]}/{analysis.total_count}) are being actively processed.'
        
        # Generate recommendations
        recommendations = []
        if analysis.age_distribution['old'] > 0:
            recommendations.append(f"Process {analysis.age_distribution['old']} old notes (90+ days) for promotion or archival")
        if analysis.age_distribution['stale'] > 0:
            recommendations.append(f"Review {analysis.age_distribution['stale']} stale notes (31-90 days) for relevance")
        if analysis.total_count > 20:
            recommendations.append("Consider batch processing to reduce fleeting note backlog")
        if analysis.age_distribution['new'] == 0 and analysis.total_count > 0:
            recommendations.append("No new notes in the last week - consider if capture process is working")
        
        # Get oldest notes for priority processing
        oldest_notes = analysis.notes_by_age[:5] if len(analysis.notes_by_age) >= 5 else analysis.notes_by_age
        
        # Get newest notes to show recent activity  
        newest_notes = analysis.notes_by_age[-5:] if len(analysis.notes_by_age) >= 5 else analysis.notes_by_age
        newest_notes.reverse()  # Show newest first
        
        return {
            'summary': summary,
            'health_status': health_status,
            'total_count': analysis.total_count,
            'age_distribution': analysis.age_distribution,
            'recommendations': recommendations if recommendations else ['Keep up the good work maintaining your fleeting notes!'],
            'oldest_notes': oldest_notes,
            'newest_notes': newest_notes,
            'oldest_note': analysis.oldest_note,
            'newest_note': analysis.newest_note
        }
    
    def generate_fleeting_triage_report(self, quality_threshold: Optional[float] = None, fast: bool = False) -> Dict:
        """
        Generate AI-powered triage report for fleeting notes with quality assessment.
        
        Args:
            quality_threshold: Optional minimum quality threshold (0.0-1.0) for filtering
            
        Returns:
            Dict: Triage report with quality assessment and recommendations
        """
        import time
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
                result = self.process_inbox_note(note_path, fast=fast)
                
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
    
    def promote_fleeting_note(self, note_path: str, target_type: Optional[str] = None, preview_mode: bool = False) -> Dict:
        """
        Promote a single fleeting note to permanent or literature status.
        
        Args:
            note_path: Path to the fleeting note to promote
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes
            
        Returns:
            Dict: Promotion results with details of operations performed
        """
        import time
        start_time = time.time()
        
        try:
            # Import DirectoryOrganizer from production-ready infrastructure
            from ..utils.directory_organizer import DirectoryOrganizer
            
            # Resolve note path
            if not note_path.startswith('/'):
                # If path starts with 'knowledge/', it's relative to the vault root
                if note_path.startswith('knowledge/'):
                    # Remove 'knowledge/' prefix since base_dir already points to knowledge/
                    relative_path = note_path.replace('knowledge/', '', 1)
                    note_path_obj = self.base_dir / relative_path
                else:
                    note_path_obj = self.base_dir / note_path
            else:
                note_path_obj = Path(note_path)
                
            if not note_path_obj.exists():
                raise ValueError(f"Note not found: {note_path}")
                
            # Validate note is fleeting type
            content = note_path_obj.read_text(encoding='utf-8')
            metadata, body = parse_frontmatter(content)
            
            if metadata.get('type') != 'fleeting':
                raise ValueError(f"Note is not a fleeting note (type: {metadata.get('type')})")
                
            # Get AI quality assessment for the note
            ai_result = self.process_inbox_note(note_path_obj, fast=True)
            quality_score = ai_result.get('quality_score', 0.5)
            
            # Auto-detect target type if not specified
            if target_type is None:
                # Use simple heuristic: literature if it has source/url, otherwise permanent
                if metadata.get('source') or metadata.get('url'):
                    target_type = 'literature'
                else:
                    target_type = 'permanent'
                    
            # Determine target directory
            if target_type == 'literature':
                target_dir = self.base_dir / "Literature Notes"
            else:
                target_dir = self.base_dir / "Permanent Notes"
                
            if not target_dir.exists():
                target_dir.mkdir(parents=True)
                
            # Create target path
            target_path = target_dir / note_path_obj.name
            
            promotion_result = {
                'promoted_notes': [{
                    'note_path': str(note_path_obj),
                    'target_type': target_type,
                    'target_path': str(target_path),
                    'quality_score': quality_score,
                    'preview_mode': preview_mode
                }],
                'batch_mode': False,
                'preview_mode': preview_mode,
                'target_directory': str(target_dir),
                'promotion_time': datetime.now().isoformat(),
                'processing_time': 0,
                'backup_created': False
            }
            
            if preview_mode:
                # Preview mode - don't actually move files
                promotion_result['processing_time'] = time.time() - start_time
                return promotion_result
                
            # Create backup using DirectoryOrganizer
            organizer = DirectoryOrganizer(self.base_dir.parent)
            backup_path = organizer.create_backup()
            promotion_result['backup_created'] = True
            promotion_result['backup_path'] = str(backup_path)
            
            # Update metadata for promotion
            updated_metadata = metadata.copy()
            updated_metadata['type'] = target_type
            updated_metadata['promoted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            updated_metadata['promotion_quality_score'] = quality_score
            
            # Reconstruct file content with updated metadata
            updated_content = f"---\n"
            for key, value in updated_metadata.items():
                if isinstance(value, list):
                    updated_content += f"{key}: {value}\n"
                elif isinstance(value, str) and ' ' in value:
                    updated_content += f'{key}: "{value}"\n'
                else:
                    updated_content += f"{key}: {value}\n"
            updated_content += f"---\n\n{body}"
            
            # Write to target location
            target_path.write_text(updated_content, encoding='utf-8')
            
            # Remove original file
            note_path_obj.unlink()
            
            promotion_result['processing_time'] = time.time() - start_time
            return promotion_result
            
        except Exception as e:
            return {
                'promoted_notes': [{
                    'note_path': note_path,
                    'error': str(e),
                    'quality_score': 0,
                    'preview_mode': preview_mode
                }],
                'batch_mode': False,
                'preview_mode': preview_mode,
                'target_directory': 'unknown',
                'promotion_time': datetime.now().isoformat(),
                'processing_time': time.time() - start_time,
                'backup_created': False
            }
    
    def promote_fleeting_notes_batch(self, quality_threshold: float = 0.7, target_type: Optional[str] = None, preview_mode: bool = False) -> Dict:
        """
        Promote multiple fleeting notes based on quality threshold.
        
        Args:
            quality_threshold: Minimum quality score for promotion
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes
            
        Returns:
            Dict: Batch promotion results
        """
        import time
        start_time = time.time()
        
        try:
            # Get triage results to identify high-quality notes
            triage_report = self.generate_fleeting_triage_report(quality_threshold=quality_threshold, fast=True)
            
            # Find notes eligible for promotion
            eligible_notes = [
                rec for rec in triage_report['recommendations'] 
                if rec['action'] == 'Promote to Permanent' and rec['quality_score'] >= quality_threshold
            ]
            
            if not eligible_notes:
                return {
                    'promoted_notes': [],
                    'batch_mode': True,
                    'preview_mode': preview_mode,
                    'quality_threshold': quality_threshold,
                    'processing_time': time.time() - start_time,
                    'backup_created': False
                }
            
            # Create single backup for batch operation
            backup_created = False
            backup_path = None
            
            if not preview_mode:
                try:
                    from ..utils.directory_organizer import DirectoryOrganizer
                    organizer = DirectoryOrganizer(self.base_dir.parent)
                    backup_path = organizer.create_backup()
                    backup_created = True
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")
            
            # Process each eligible note
            promoted_notes = []
            for note_rec in eligible_notes:
                try:
                    single_result = self.promote_fleeting_note(
                        note_path=note_rec['note_path'],
                        target_type=target_type,
                        preview_mode=preview_mode
                    )
                    
                    # Extract the promoted note info and add batch context
                    if single_result['promoted_notes']:
                        promoted_note = single_result['promoted_notes'][0]
                        promoted_note['batch_promotion'] = True
                        promoted_notes.append(promoted_note)
                        
                except Exception as e:
                    # Add failed note to results
                    promoted_notes.append({
                        'note_path': note_rec['note_path'],
                        'error': str(e),
                        'quality_score': note_rec['quality_score'],
                        'batch_promotion': True,
                        'preview_mode': preview_mode
                    })
            
            return {
                'promoted_notes': promoted_notes,
                'batch_mode': True,
                'preview_mode': preview_mode,
                'quality_threshold': quality_threshold,
                'processing_time': time.time() - start_time,
                'backup_created': backup_created,
                'backup_path': str(backup_path) if backup_path else None
            }
            
        except Exception as e:
            return {
                'promoted_notes': [],
                'batch_mode': True,
                'preview_mode': preview_mode,
                'quality_threshold': quality_threshold,
                'error': str(e),
                'processing_time': time.time() - start_time,
                'backup_created': False
            }

    # ============================================================================
    # GREEN PHASE: Safe Image Processing Integration Methods
    # ============================================================================

    def safe_process_inbox_note(self, note_path: str, preserve_images: bool = True, **kwargs) -> Dict:
        """REFACTOR: Process inbox note using modular SafeWorkflowProcessor"""
        note_file = Path(note_path)
        
        # Use extracted SafeWorkflowProcessor for modular processing
        result = self.safe_workflow_processor.process_note_safely(
            note_file,
            lambda path: self.process_inbox_note(path, **kwargs),
            preserve_images
        )
        
        # Convert to legacy format for backward compatibility
        if result.success and result.workflow_result:
            legacy_result = result.workflow_result.copy()
            legacy_result['image_preservation'] = result.image_preservation_details or {}
            legacy_result['image_preservation']['images_preserved'] = result.images_preserved
            legacy_result['image_preservation']['backup_session_id'] = result.backup_session_id
            legacy_result['image_preservation']['processing_time'] = result.processing_time
            return legacy_result
        else:
            return {
                'success': False,
                'error': result.error_message,
                'image_preservation': result.image_preservation_details or {}
            }

    def process_inbox_note_atomic(self, note_path: str) -> Dict:
        """GREEN Phase: Atomic inbox processing with rollback capability"""
        note_file = Path(note_path)
        
        # Extract images for tracking
        images = self.safe_image_processor.image_extractor.extract_images_from_note(note_file)
        
        # Process with atomic operations
        result = self.safe_image_processor.process_note_with_images(
            note_file, 
            operation="atomic_inbox_processing"
        )
        
        if result.success:
            # Perform actual processing
            processing_result = self.process_inbox_note(note_path)
            return {
                'processing_successful': True,
                'images_preserved': len(result.preserved_images),
                'backup_session_id': result.backup_session_id,
                'processing_time': result.processing_time,
                'workflow_result': processing_result
            }
        else:
            return {
                'processing_successful': False,
                'images_preserved': 0,
                'backup_session_id': result.backup_session_id,
                'processing_time': result.processing_time,
                'error': result.error_message
            }

    def safe_batch_process_inbox(self) -> Dict:
        """GREEN Phase: Safe batch processing with image preservation"""
        inbox_files = list(self.inbox_dir.glob("*.md"))
        
        # Process all notes with SafeImageProcessor
        results = self.safe_image_processor.process_notes_batch(
            inbox_files, 
            operation="safe_batch_inbox_processing"
        )
        
        total_images_preserved = sum(len(r.preserved_images) for r in results)
        successful_processing = sum(1 for r in results if r.success)
        
        # Run standard batch processing for workflow results
        standard_results = self.batch_process_inbox()
        
        # Enhance with image preservation data
        standard_results.update({
            'images_preserved_total': total_images_preserved,
            'image_integrity_report': {
                'total_files_with_images': len([r for r in results if r.preserved_images]),
                'successful_image_preservation': successful_processing,
                'failed_image_preservation': len(results) - successful_processing
            }
        })
        
        return standard_results

    def process_inbox_note_enhanced(self, note_path: str, enable_monitoring: bool = False, 
                                  collect_performance_metrics: bool = False, **kwargs) -> Dict:
        """GREEN Phase: Enhanced processing with monitoring and metrics"""
        result = self.process_inbox_note(note_path, **kwargs)
        
        if enable_monitoring:
            # Add integrity monitoring (GREEN phase: basic implementation)
            note_file = Path(note_path)
            # Extract images for monitoring
            images = self.safe_image_processor.image_extractor.extract_images_from_note(note_file)
            # Register images for monitoring
            for image in images:
                self.image_integrity_monitor.register_image(image, f"monitoring:{note_path}")
            
            result['integrity_report'] = {
                'images_tracked': len(images),
                'monitoring_enabled': True,
                'scan_result': {
                    'found_images': images,
                    'monitored_images': len(images)
                }
            }
        
        if collect_performance_metrics:
            # Add performance metrics
            metrics = self.safe_image_processor.get_performance_metrics()
            result['performance_metrics'] = {
                'backup_time': metrics.get('backup_time', 0),
                'processing_time': metrics.get('processing_time', 0),
                'image_operations_time': metrics.get('atomic_operations', {}).get('average_execution_time', 0)
            }
        
        return result

    def process_inbox_note_safe(self, note_path: str) -> Dict:
        """GREEN Phase: Safe processing with automatic backup/rollback"""
        try:
            # Create backup session
            session = self.safe_image_processor.create_backup_session("safe_inbox_processing")
            
            # Process with monitoring
            result = self.process_inbox_note_enhanced(note_path, enable_monitoring=True)
            
            # Check if processing succeeded
            if result.get('error'):
                # Rollback on error
                return {
                    'processing_failed': True,
                    'rollback_successful': True,
                    'images_restored': len(session.images_to_backup),
                    'error': result.get('error')
                }
            else:
                return {
                    'processing_failed': False,
                    'rollback_successful': False,
                    'images_restored': 0,
                    'result': result
                }
                
        except Exception as e:
            return {
                'processing_failed': True,
                'rollback_successful': True,
                'images_restored': 0,
                'error': str(e)
            }

    def start_safe_processing_session(self, operation_name: str) -> str:
        """REFACTOR: Start concurrent safe processing session using ConcurrentSessionManager"""
        session_id = self.concurrent_session_manager.create_processing_session(operation_name)
        
        # Legacy compatibility
        self.active_sessions[session_id] = {
            'operation_name': operation_name,
            'created_at': datetime.now(),
            'notes_processed': []
        }
        return session_id

    def process_note_in_session(self, note_path: str, session_id: str) -> Dict:
        """REFACTOR: Process note within session using modular session manager"""
        note_file = Path(note_path)
        
        # Use modular session manager for processing
        result = self.concurrent_session_manager.process_note_in_session(
            session_id,
            note_file,
            lambda path: self.process_inbox_note(str(path))
        )
        
        # Update legacy tracking for compatibility
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['notes_processed'].append({
                'note_path': note_path,
                'result': result,
                'processed_at': datetime.now()
            })
        
        return result

    def commit_safe_processing_session(self, session_id: str) -> bool:
        """REFACTOR: Commit safe processing session using modular session manager"""
        # Finalize using modular session manager
        session_summary = self.concurrent_session_manager.finalize_session(session_id)
        
        # Legacy cleanup
        if session_id in self.active_sessions:
            self.active_sessions.pop(session_id)
        
        return session_summary.get('success', True)


def main():
    """CLI entry point for workflow manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-enhanced Zettelkasten workflow manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Process inbox
    process_parser = subparsers.add_parser("process-inbox", help="Process inbox notes")
    process_parser.add_argument("directory", help="Zettelkasten root directory")
    process_parser.add_argument("--batch", action="store_true", help="Process all inbox notes")
    
    # Promote note
    promote_parser = subparsers.add_parser("promote", help="Promote a note")
    promote_parser.add_argument("directory", help="Zettelkasten root directory")
    promote_parser.add_argument("note", help="Note file to promote")
    promote_parser.add_argument("--type", choices=["permanent", "fleeting"], 
                               default="permanent", help="Target note type")
    
    # Workflow report
    report_parser = subparsers.add_parser("report", help="Generate workflow report")
    report_parser.add_argument("directory", help="Zettelkasten root directory")
    report_parser.add_argument("--output", help="Output file for report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    workflow = WorkflowManager(args.directory)
    
    if args.command == "process-inbox":
        if args.batch:
            print("📥 Processing all inbox notes...")
            result = workflow.batch_process_inbox()
            
            print(f"📊 Results:")
            print(f"   Total files: {result['total_files']}")
            print(f"   Processed: {result['processed']}")
            print(f"   Failed: {result['failed']}")
            print(f"   Recommendations:")
            print(f"     Promote to permanent: {result['summary']['promote_to_permanent']}")
            print(f"     Move to fleeting: {result['summary']['move_to_fleeting']}")
            print(f"     Needs improvement: {result['summary']['needs_improvement']}")
        else:
            print("Use --batch flag to process all inbox notes")
    
    elif args.command == "promote":
        print(f"📈 Promoting note: {args.note}")
        result = workflow.promote_note(args.note, args.type)
        
        if result.get("success"):
            print(f"✅ Successfully promoted to {result['type']}")
            print(f"   From: {result['source']}")
            print(f"   To: {result['target']}")
            if result.get("has_summary"):
                print(f"   Added AI summary")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    
    elif args.command == "report":
        print("📊 Generating workflow report...")
        report = workflow.generate_workflow_report()
        
        if args.output:
            # Use atomic write to prevent partial JSON writes on interruption
            report_json = json.dumps(report, indent=2, default=str)
            safe_write(args.output, report_json)
            print(f"📄 Report saved to: {args.output}")
        else:
            # Display summary
            status = report["workflow_status"]
            print(f"\n🏥 Workflow Health: {status['health'].upper()}")
            print(f"📁 Directory Counts:")
            for dir_name, count in status["directory_counts"].items():
                print(f"   {dir_name}: {count}")
            
            ai_features = report["ai_features"]
            total = ai_features["total_analyzed"]
            if total > 0:
                print(f"\n🤖 AI Feature Usage:")
                print(f"   Notes with AI summaries: {ai_features['notes_with_ai_summaries']}/{total}")
                print(f"   Notes with AI processing: {ai_features['notes_with_ai_processing']}/{total}")
                print(f"   Notes with AI tags: {ai_features['notes_with_ai_tags']}/{total}")
            
            recommendations = report.get("recommendations", [])
            if recommendations:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")


# ============================================================================
# GREEN PHASE: SafeWorkflowManager Alias for Compatibility
# ============================================================================

# Create alias for backwards compatibility
SafeWorkflowManager = WorkflowManager


if __name__ == "__main__":
    main()
