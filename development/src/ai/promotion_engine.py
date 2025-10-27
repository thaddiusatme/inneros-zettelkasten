"""
PromotionEngine - Handles note promotion workflows.

Extracted from WorkflowManager as part of ADR-002 Phase 4.
Responsible for promoting notes between directories based on quality and type.

Composition Pattern:
- Used by WorkflowManager via delegation
- Depends on NoteLifecycleManager for lifecycle operations
- Integrates with DirectoryOrganizer for safe file operations
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging

from src.utils.frontmatter import parse_frontmatter, build_frontmatter
from src.utils.io import safe_write
from .note_lifecycle_manager import NoteLifecycleManager


logger = logging.getLogger(__name__)


class PromotionEngine:
    """
    Handles note promotion between directories based on quality thresholds.
    
    Key Responsibilities:
    - Single note promotion
    - Batch promotion workflows
    - Auto-promotion based on quality scores
    - Validation of promotion eligibility
    - Integration with DirectoryOrganizer for safe operations
    """

    def __init__(
        self,
        base_dir: Path,
        lifecycle_manager: NoteLifecycleManager,
        config: Optional[Dict] = None
    ):
        """
        Initialize PromotionEngine.
        
        Args:
            base_dir: Base directory for the knowledge vault
            lifecycle_manager: NoteLifecycleManager instance for lifecycle operations
            config: Optional configuration dictionary
        """
        self.base_dir = Path(base_dir)
        self.lifecycle_manager = lifecycle_manager
        self.config = config or {}

        # Set up directory paths
        self.inbox_dir = self.base_dir / "Inbox"
        self.permanent_dir = self.base_dir / "Permanent Notes"
        self.literature_dir = self.base_dir / "Literature Notes"
        self.fleeting_dir = self.base_dir / "Fleeting Notes"

        # Ensure target directories exist
        self.permanent_dir.mkdir(exist_ok=True)
        self.literature_dir.mkdir(exist_ok=True)
        self.fleeting_dir.mkdir(exist_ok=True)

        logger.info(f"PromotionEngine initialized with base_dir: {base_dir}")

    def promote_note(self, note_path: str, target_type: str = "permanent") -> Dict:
        """
        Promote a note from inbox/fleeting to appropriate directory.
        
        This method now delegates to NoteLifecycleManager for unified promotion logic.
        If target_type is specified, it updates the note's type field before promotion.
        
        Args:
            note_path: Path to the note to promote
            target_type: Target note type ("permanent", "literature", or "fleeting")
                        If provided, overrides the note's existing type field.
            
        Returns:
            Promotion results dictionary with keys:
            - success: bool
            - source: str (original path)
            - target: str (new path)
            - type: str (note type)
            - error: str (if failed)
        """
        source_file = Path(note_path)

        if not source_file.exists():
            return {"error": "Source note not found"}

        # Validate target type
        if target_type not in ["permanent", "literature", "fleeting"]:
            return {"error": f"Invalid target type: {target_type}"}

        try:
            # If target_type specified, update note's type field before promotion
            # This allows caller to override note's classification if needed
            if target_type:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                frontmatter, body = parse_frontmatter(content)
                
                # Update type field to match target
                frontmatter["type"] = target_type
                
                # Write updated type back to note
                updated_content = build_frontmatter(frontmatter, body)
                safe_write(source_file, updated_content)

            # Delegate to NoteLifecycleManager for unified promotion logic
            # This handles: status update, validation, file move, timestamps
            result = self.lifecycle_manager.promote_note(source_file)

            if result.get("promoted"):
                # Transform result to match expected format
                return {
                    "success": True,
                    "source": str(source_file),
                    "target": result["destination_path"],
                    "type": result["note_type"],
                    "has_summary": False  # Legacy field for compatibility
                }
            else:
                return {"error": result.get("error", "Promotion failed")}

        except Exception as e:
            return {"error": f"Failed to promote note: {e}"}

    def _validate_note_for_promotion(
        self,
        note_path: Path,
        frontmatter: Dict,
        quality_threshold: float
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate if a note is eligible for auto-promotion.
        
        Args:
            note_path: Path to the note
            frontmatter: Parsed frontmatter metadata
            quality_threshold: Minimum quality score required
            
        Returns:
            Tuple of (is_valid, note_type, error_message)
        """
        # Check quality score
        quality_score = frontmatter.get("quality_score", 0.0)
        if quality_score < quality_threshold:
            return False, None, f"Quality score {quality_score:.2f} below threshold {quality_threshold}"

        # Check for required type field
        note_type = frontmatter.get("type")
        if not note_type:
            return False, None, "Missing 'type' field in frontmatter"

        # Validate type is one of the expected values
        valid_types = ["permanent", "literature", "fleeting"]
        if note_type not in valid_types:
            return False, None, f"Invalid type '{note_type}', must be one of: {valid_types}"

        return True, note_type, None

    def _execute_note_promotion(
        self,
        note_path: Path,
        note_type: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Execute the actual file promotion operation.
        
        Args:
            note_path: Path to the note to promote
            note_type: Target note type
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            result = self.promote_note(str(note_path), target_type=note_type)

            if "error" in result:
                return False, result["error"]

            # Status update and file move are now handled by promote_note() delegation
            # No need for separate status update - NoteLifecycleManager handles it atomically
            
            return True, None

        except Exception as e:
            error_msg = f"Promotion execution failed: {e}"
            logger.exception(error_msg)
            return False, error_msg

    def auto_promote_ready_notes(
        self,
        dry_run: bool = False,
        quality_threshold: float = 0.7
    ) -> Dict:
        """
        Automatically promote notes that meet quality threshold.
        
        Scans Inbox/ for notes with quality_score >= threshold,
        then promotes them to appropriate directories based on type field.
        
        Args:
            dry_run: If True, preview promotions without making changes
            quality_threshold: Minimum quality score required (default: 0.7)
            
        Returns:
            Dict with promotion results including counts and details
        """
        results = {
            "total_candidates": 0,
            "promoted_count": 0,
            "skipped_count": 0,
            "error_count": 0,
            "promoted": [],
            "skipped_notes": [],
            "errors": [],
            "by_type": {
                "fleeting": {"promoted": 0, "skipped": 0},
                "literature": {"promoted": 0, "skipped": 0},
                "permanent": {"promoted": 0, "skipped": 0}
            },
            "dry_run": dry_run,
        }

        if dry_run:
            results["would_promote_count"] = 0
            results["preview"] = []
            logger.info("Auto-promotion running in DRY-RUN mode (no changes will be made)")

        # Scan inbox for candidate notes (including subdirectories)
        if not self.inbox_dir.exists():
            logger.warning(f"Inbox directory does not exist: {self.inbox_dir}")
            return results

        inbox_files = list(self.inbox_dir.rglob("*.md"))
        logger.info(f"Scanning {len(inbox_files)} notes in Inbox/ (including subdirectories) for auto-promotion candidates")

        for note_path in inbox_files:
            try:
                # Read note metadata
                content = note_path.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(content)

                # Skip notes without quality scores
                quality_score = frontmatter.get("quality_score")
                if quality_score is None:
                    continue

                # Skip notes that don't have inbox status
                status = frontmatter.get("status", "inbox")
                if status not in ["inbox", "promoted"]:
                    continue

                results["total_candidates"] += 1
                logger.debug(f"Evaluating candidate: {note_path.name} (quality: {quality_score})")

                # Validate note eligibility
                is_valid, note_type, error_msg = self._validate_note_for_promotion(
                    note_path, frontmatter, quality_threshold
                )

                if not is_valid:
                    results["skipped_count"] += 1
                    results["skipped_notes"].append({
                        "path": note_path.name,
                        "quality": frontmatter.get("quality_score", 0.0),
                        "type": frontmatter.get("type", "unknown"),
                        "reason": error_msg or "Validation failed"
                    })
                    # Track by type for skipped notes
                    note_type_for_skip = frontmatter.get("type", "permanent")
                    if note_type_for_skip in results["by_type"]:
                        results["by_type"][note_type_for_skip]["skipped"] += 1
                    if error_msg and "type" in error_msg.lower():
                        results["error_count"] += 1
                        results["errors"].append({"note": note_path.name, "error": error_msg})
                    logger.debug(f"Skipped {note_path.name}: {error_msg}")
                    continue

                # At this point, note_type is guaranteed to be a string
                assert note_type is not None, "note_type should not be None after successful validation"

                # Dry-run mode: preview only
                if dry_run:
                    quality_score = frontmatter.get("quality_score", 0.0)
                    results["would_promote_count"] += 1
                    results["preview"].append({
                        "note": note_path.name,
                        "type": note_type,
                        "quality": quality_score,
                        "target": f"{note_type.title()} Notes/"
                    })
                    logger.info(f"Would promote: {note_path.name} → {note_type.title()} Notes/")
                    continue

                # Execute promotion
                success, error_msg = self._execute_note_promotion(note_path, note_type)

                if success:
                    results["promoted_count"] += 1
                    results["by_type"][note_type]["promoted"] += 1
                    results["promoted"].append({
                        "title": note_path.name,
                        "type": note_type,
                        "quality": frontmatter.get("quality_score", 0.0),
                        "target": f"{note_type.title()} Notes/"
                    })
                    logger.info(f"Promoted: {note_path.name} → {note_type.title()} Notes/")
                else:
                    results["error_count"] += 1
                    results["errors"].append({"note": note_path.name, "error": error_msg})
                    logger.error(f"Promotion failed for {note_path.name}: {error_msg}")

            except Exception as e:
                results["error_count"] += 1
                results["errors"].append({
                    "note": note_path.name,
                    "error": str(e)
                })
                logger.exception(f"Error processing {note_path.name}: {e}")

        # Add summary section
        results["summary"] = {
            "total_candidates": results["total_candidates"],
            "promoted_count": results["promoted_count"],
            "skipped_count": results["skipped_count"],
            "error_count": results["error_count"]
        }

        # Summary logging
        logger.info(
            f"Auto-promotion complete: {results['promoted_count']} promoted, "
            f"{results['skipped_count']} skipped, {results['error_count']} errors"
        )

        return results

    def promote_fleeting_note(
        self,
        note_path: str,
        target_type: Optional[str] = None,
        preview_mode: bool = False
    ) -> Dict:
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
            # Import DirectoryOrganizer
            from ..utils.directory_organizer import DirectoryOrganizer

            # Resolve note path
            if not note_path.startswith('/'):
                if note_path.startswith('knowledge/'):
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

            # Get quality score
            quality_score = metadata.get('quality_score', 0.5)

            # Auto-detect target type if not specified
            if target_type is None:
                if metadata.get('source') or metadata.get('url'):
                    target_type = 'literature'
                else:
                    target_type = 'permanent'

            # Determine target directory
            if target_type == 'literature':
                target_dir = self.literature_dir
            else:
                target_dir = self.permanent_dir

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
                promotion_result['processing_time'] = time.time() - start_time
                return promotion_result

            # Create backup
            organizer = DirectoryOrganizer(self.base_dir.parent)
            backup_path = organizer.create_backup()
            promotion_result['backup_created'] = True
            promotion_result['backup_path'] = str(backup_path)

            # Update metadata for promotion
            updated_metadata = metadata.copy()
            updated_metadata['type'] = target_type
            updated_metadata['promoted_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            updated_metadata['promotion_quality_score'] = quality_score

            # Reconstruct file content
            updated_content = "---\n"
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

    def promote_fleeting_notes_batch(
        self,
        quality_threshold: float = 0.7,
        target_type: Optional[str] = None,
        preview_mode: bool = False
    ) -> Dict:
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
            # Scan fleeting notes directory for high-quality notes
            fleeting_notes = []
            if self.fleeting_dir.exists():
                for note_path in self.fleeting_dir.glob("*.md"):
                    try:
                        content = note_path.read_text(encoding='utf-8')
                        metadata, _ = parse_frontmatter(content)
                        quality = metadata.get('quality_score', 0.0)

                        if quality >= quality_threshold:
                            fleeting_notes.append({
                                'note_path': str(note_path),
                                'quality_score': quality,
                                'action': 'Promote to Permanent'
                            })
                    except Exception:
                        continue

            if not fleeting_notes:
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
                    logger.warning(f"Could not create backup: {e}")

            # Process each eligible note
            promoted_notes = []
            for note_rec in fleeting_notes:
                try:
                    # Determine target type for this note
                    note_target = target_type
                    if note_target is None:
                        # Auto-detect based on source/url
                        try:
                            note_path_obj = Path(note_rec['note_path'])
                            content = note_path_obj.read_text(encoding='utf-8')
                            metadata, _ = parse_frontmatter(content)
                            if metadata.get('source') or metadata.get('url'):
                                note_target = 'literature'
                            else:
                                note_target = 'permanent'
                        except Exception:
                            note_target = 'permanent'

                    # Use basic promote_note (backup already created for batch)
                    if not preview_mode:
                        result = self.promote_note(note_rec['note_path'], target_type=note_target)
                        if "success" in result and result["success"]:
                            promoted_notes.append({
                                'note_path': note_rec['note_path'],
                                'target_type': note_target,
                                'target_path': result.get('target', ''),
                                'quality_score': note_rec['quality_score'],
                                'batch_promotion': True,
                                'preview_mode': False
                            })
                        else:
                            promoted_notes.append({
                                'note_path': note_rec['note_path'],
                                'error': result.get('error', 'Unknown error'),
                                'quality_score': note_rec['quality_score'],
                                'batch_promotion': True,
                                'preview_mode': False
                            })
                    else:
                        # Preview mode
                        promoted_notes.append({
                            'note_path': note_rec['note_path'],
                            'target_type': note_target,
                            'quality_score': note_rec['quality_score'],
                            'batch_promotion': True,
                            'preview_mode': True
                        })

                except Exception as e:
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
