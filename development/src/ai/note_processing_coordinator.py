"""
ADR-002 Phase 6: NoteProcessingCoordinator

Extracts note processing logic from WorkflowManager for single responsibility.

This coordinator handles:
- AI-powered note processing (tagging, quality scoring, connections)
- Template placeholder fixing and preprocessing
- Fast mode processing with heuristics
- Dry-run and safe file operations

GREEN Phase: Complete implementation extracted from WorkflowManager.
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from src.utils.tags import sanitize_tags
from src.utils.frontmatter import parse_frontmatter, build_frontmatter
from src.utils.io import safe_write


class NoteProcessingCoordinator:
    """
    Coordinator for AI-powered note processing and template handling.
    
    Extracted from WorkflowManager (ADR-002 Phase 6) to maintain single 
    responsibility principle. Handles all note processing logic including
    AI tagging, quality scoring, connection discovery, and template fixes.
    """

    def __init__(
        self,
        tagger,
        summarizer,
        enhancer,
        connection_coordinator,
        config: Optional[Dict] = None
    ):
        """
        Initialize note processing coordinator.
        
        Args:
            tagger: AI tagger component for generating tags
            summarizer: AI summarizer component for creating summaries
            enhancer: AI enhancer component for quality assessment
            connection_coordinator: Connection discovery coordinator
            config: Optional configuration dictionary
        """
        self.tagger = tagger
        self.summarizer = summarizer
        self.enhancer = enhancer
        self.connection_coordinator = connection_coordinator

        # Default configuration
        self.config = {
            "auto_tag_inbox": True,
            "auto_summarize_long_notes": True,
            "min_words_for_summary": 500,
            "max_tags_per_note": 8,
            "similarity_threshold": 0.7
        }

        # Update with user config if provided
        if config:
            self.config.update(config)

    def process_note(
        self,
        note_path: str,
        dry_run: bool = False,
        fast: Optional[bool] = None,
        corpus_dir: Optional[Path] = None
    ) -> Dict:
        """
        Process a note with AI assistance.
        
        Extracted from WorkflowManager.process_inbox_note() for single responsibility.
        
        Args:
            note_path: Path to the note file
            dry_run: If True, do not write changes to disk
            fast: If True, skip AI calls and use heuristics (defaults to dry_run)
            corpus_dir: Optional directory for connection discovery
            
        Returns:
            Processing results with processing details, recommendations, and metadata
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
        content, raw_template_fixed = self._preprocess_created_placeholder_in_raw(content, note_file)

        results = {
            "original_file": str(note_file),
            "processing": {},
            "recommendations": []
        }

        # Extract frontmatter and body using centralized utility
        frontmatter, body = parse_frontmatter(content)

        # Fix template placeholders in frontmatter BEFORE any processing
        template_fixed = self._fix_template_placeholders(frontmatter, note_file)
        any_template_fixed = raw_template_fixed or template_fixed

        # Determine fast-mode (heuristic, no external AI calls)
        fast_mode = fast if fast is not None else dry_run

        if fast_mode:
            # Heuristic-only path to avoid network/AI latency
            results["processing"] = {}
            existing_tags = sanitize_tags(frontmatter.get("tags", []))
            results["processing"]["ai_tags"] = list(existing_tags)

            # Simple word count heuristic
            body_text = body if isinstance(body, str) else ""
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
                    "Add more detail and structure to improve quality" if word_count < 200
                    else "Refine key points and add links to related notes"
                ]
            }
            results["processing"]["tags"] = {
                "added": [],
                "total": len(existing_tags)
            }

            # Primary recommendation based on heuristic score
            if quality_score > 0.7:
                primary = {
                    "action": "promote_to_permanent",
                    "reason": "High quality (heuristic) suitable for permanent notes",
                    "confidence": "medium"
                }
            elif quality_score > 0.4:
                primary = {
                    "action": "move_to_fleeting",
                    "reason": "Medium quality (heuristic) needs development",
                    "confidence": "medium"
                }
            else:
                primary = {
                    "action": "improve_or_archive",
                    "reason": "Low quality (heuristic) needs significant improvement",
                    "confidence": "high"
                }

            results["recommendations"].append(primary)
            results["quality_score"] = quality_score

            # Persist template fixes even in fast-mode, using atomic write
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

        # Track if any AI processing errors occurred
        ai_processing_errors = []

        # Auto-tag if enabled (use body content only)
        if self.config["auto_tag_inbox"]:
            try:
                suggested_tags = self.tagger.generate_tags(body)
                existing_tags = sanitize_tags(frontmatter.get("tags", []))
                suggested_tags = sanitize_tags(suggested_tags)

                # Merge tags intelligently
                merged_tags = self._merge_tags(existing_tags, suggested_tags)
                merged_tags = sanitize_tags(merged_tags)

                if merged_tags != existing_tags:
                    frontmatter["tags"] = merged_tags
                    results["processing"]["tags"] = {
                        "added": list(set(merged_tags) - set(existing_tags)),
                        "total": len(merged_tags)
                    }

                results["processing"]["ai_tags"] = merged_tags
            except Exception as e:
                results["processing"]["tags"] = {"error": str(e)}
                ai_processing_errors.append(("tagging", str(e)))

        # Ensure ai_tags key is always present
        current_tags = sanitize_tags(frontmatter.get("tags", []))
        if "ai_tags" not in results["processing"]:
            results["processing"]["ai_tags"] = current_tags

        # Analyze note quality and suggest improvements
        try:
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
            ai_processing_errors.append(("quality", str(e)))

        # Find potential connections
        try:
            if corpus_dir:
                connections = self.connection_coordinator.discover_connections(
                    body,
                    corpus_dir=corpus_dir
                )

                if connections:
                    results["processing"]["connections"] = {
                        "similar_notes": [
                            {"file": conn["filename"], "similarity": float(conn["similarity"])}
                            for conn in connections[:3]
                        ]
                    }

                    results["recommendations"].append({
                        "action": "add_links",
                        "reason": f"Found {len(connections)} related notes",
                        "details": connections[:3]
                    })
        except Exception as e:
            results["processing"]["connections"] = {"error": str(e)}

        # Update note with AI enhancements (skip when dry_run)
        needs_ai_update = any(key in results["processing"] for key in ["tags", "quality"])

        if needs_ai_update or any_template_fixed:
            if dry_run:
                if needs_ai_update:
                    frontmatter["ai_processed"] = datetime.now().isoformat()
                results["file_updated"] = False
            else:
                try:
                    if needs_ai_update:
                        frontmatter["ai_processed"] = datetime.now().isoformat()

                        if "quality" in results["processing"] and "score" in results["processing"]["quality"]:
                            frontmatter["quality_score"] = results["processing"]["quality"]["score"]

                    # Rebuild content using centralized utility
                    updated_content = build_frontmatter(frontmatter, body)
                    safe_write(note_file, updated_content)
                    results["file_updated"] = True
                except Exception as e:
                    results["file_update_error"] = str(e)
                    results["file_updated"] = False
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

        changes_made = False
        created_value = frontmatter.get("created")

        # Fix template placeholders like {{date:YYYY-MM-DD HH:mm}} or missing created field
        if (created_value is None or
            (isinstance(created_value, str) and (
                "{{date" in created_value or
                "<% tp.date.now(" in created_value or
                "<% tp.file.creation_date(" in created_value
            ))):

            try:
                file_stat = os.stat(note_file)
                timestamp = datetime.fromtimestamp(file_stat.st_mtime)
            except (OSError, ValueError):
                timestamp = datetime.now()

            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M")
            frontmatter["created"] = formatted_timestamp
            changes_made = True

        return changes_made

    def _preprocess_created_placeholder_in_raw(self, content: str, note_file: Path) -> tuple[str, bool]:
        """
        Replace invalid 'created' placeholders directly in the raw frontmatter block.
        
        This is necessary when placeholders make YAML unparseable, causing parse_frontmatter()
        to return empty metadata. Preprocessing ensures YAML becomes valid.
        
        Returns:
            Tuple of (possibly updated content, changes_made)
        """
        try:
            text = content if isinstance(content, str) else ""
            if not text or not text.lstrip().startswith('---'):
                return content, False

            lines = text.split('\n')

            # Locate closing delimiter
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
                "<% tp.file.creation_date("
            )

            changed = False

            # Scan only within frontmatter region
            for j in range(1, closing_idx):
                line = lines[j]
                if not line.strip().startswith("created:"):
                    continue

                prefix, sep, value = line.partition(":")
                value_str = value.strip()

                if any(marker in value_str for marker in placeholder_markers):
                    try:
                        import os
                        ts = datetime.fromtimestamp(os.stat(note_file).st_mtime)
                    except Exception:
                        ts = datetime.now()

                    formatted = ts.strftime("%Y-%m-%d %H:%M")

                    # Preserve spaces after colon
                    m = re.match(r"^(\s*)", value)
                    spaces = m.group(1) if m else " "
                    lines[j] = f"{prefix}:{spaces}{formatted}"
                    changed = True
                break

            if changed:
                return "\n".join(lines), True
            return content, False
        except Exception:
            return content, False

    def _merge_tags(self, existing_tags: List[str], new_tags: List[str]) -> List[str]:
        """
        Merge existing and new tags intelligently.
        
        Args:
            existing_tags: Current tags in the note
            new_tags: New tags to add
            
        Returns:
            Merged and deduplicated tag list (limited by max_tags_per_note)
        """
        existing_set = set(existing_tags) if existing_tags else set()
        new_set = set(new_tags) if new_tags else set()

        merged = sorted(list(existing_set | new_set))
        return merged[:self.config["max_tags_per_note"]]
