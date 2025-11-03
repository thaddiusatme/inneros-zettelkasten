"""
FleetingNoteCoordinator - ADR-002 Phase 12b (Vault Config Migration)

GitHub Issue #45 - Phase 2 Priority 3: Migrate to centralized vault configuration.
Uses vault_config.yaml for directory paths instead of hardcoded directories.

Extracts fleeting note management logic from WorkflowManager.
Responsible for:
- Fleeting note discovery and scanning
- Quality assessment and triage reporting
- Single and batch note promotion
- Preview mode operations
- Progress reporting and statistics

Target: Extract ~250-300 LOC from WorkflowManager (fleeting note methods)
"""

import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable

from src.utils.frontmatter import parse_frontmatter
from src.config.vault_config_loader import get_vault_config


class FleetingNoteCoordinator:
    """
    Coordinates fleeting note management workflows.

    ADR-002 Phase 12b: Extracts fleeting note triage and promotion to reduce WorkflowManager complexity.
    """

    def __init__(
        self,
        base_dir: Path,
        workflow_manager,
        process_callback: Optional[Callable] = None,
        default_quality_threshold: float = 0.7,
    ):
        """
        Initialize fleeting note coordinator.

        Args:
            base_dir: Base directory of the vault (vault config loads from here)
            workflow_manager: WorkflowManager instance for AI processing
            process_callback: Optional callback to WorkflowManager.process_inbox_note for quality assessment
            default_quality_threshold: Default quality threshold for promotion
            
        Note:
            Directory paths loaded from vault_config.yaml in knowledge/ subdirectory.
            Part of GitHub Issue #45 - Vault Configuration Centralization.
        """
        self.base_dir = Path(base_dir)
        self.workflow_manager = workflow_manager
        
        # Load vault configuration for directory paths
        vault_config = get_vault_config(str(self.base_dir))
        self.fleeting_dir = vault_config.fleeting_dir
        self.inbox_dir = vault_config.inbox_dir
        self.permanent_dir = vault_config.permanent_dir
        self.literature_dir = vault_config.literature_dir
        
        self.process_callback = process_callback
        self.default_quality_threshold = default_quality_threshold

        # Ensure directories exist
        self.fleeting_dir.mkdir(parents=True, exist_ok=True)
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def find_fleeting_notes(self) -> List[Path]:
        """
        Find all fleeting notes for triage processing.

        Returns:
            List of Path objects for fleeting notes
        """
        fleeting_notes = []

        # Check both Fleeting Notes and Inbox directories
        for directory in [self.fleeting_dir, self.inbox_dir]:
            if directory.exists():
                for note_file in directory.glob("*.md"):
                    try:
                        content = note_file.read_text(encoding="utf-8")
                        metadata, _ = parse_frontmatter(content)

                        # Include notes that are explicitly fleeting type or in fleeting directory
                        if (
                            metadata.get("type") == "fleeting"
                            or directory.name == "Fleeting Notes"
                        ):
                            fleeting_notes.append(note_file)

                    except Exception:
                        # Skip files that can't be read or parsed
                        continue

        return fleeting_notes

    def generate_triage_report(
        self, quality_threshold: Optional[float] = None, fast: bool = True
    ) -> Dict:
        """
        Generate AI-powered triage report for fleeting notes with quality assessment.

        Args:
            quality_threshold: Optional minimum quality threshold (0.0-1.0) for filtering
            fast: If True, use fast mode for quality assessment

        Returns:
            Dict: Triage report with quality assessment and recommendations
        """
        start_time = time.time()

        # Get fleeting notes for processing
        fleeting_notes = self.find_fleeting_notes()

        if not fleeting_notes:
            return {
                "total_notes_processed": 0,
                "quality_distribution": {"high": 0, "medium": 0, "low": 0},
                "recommendations": [],
                "processing_time": time.time() - start_time,
                "quality_threshold": quality_threshold,
            }

        # Process each note for quality assessment
        recommendations = []
        quality_scores = []

        for note_path in fleeting_notes:
            try:
                # Use callback for quality assessment
                result = self.process_callback(note_path, fast=fast)

                quality_score = result.get("quality_score", 0.5)
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
                    recommendations.append(
                        {
                            "note_path": str(note_path),
                            "quality_score": quality_score,
                            "action": action,
                            "rationale": rationale,
                            "ai_tags": result.get("ai_tags", []),
                            "created": result.get("metadata", {}).get(
                                "created", "Unknown"
                            ),
                        }
                    )

            except Exception as e:
                # Handle individual note processing errors gracefully
                recommendations.append(
                    {
                        "note_path": str(note_path),
                        "quality_score": 0.0,
                        "action": "Processing Error",
                        "rationale": f"Error processing note: {str(e)}",
                        "ai_tags": [],
                        "created": "Unknown",
                    }
                )

        # Calculate quality distribution
        quality_distribution = {"high": 0, "medium": 0, "low": 0}
        for score in quality_scores:
            if score >= 0.7:
                quality_distribution["high"] += 1
            elif score >= 0.4:
                quality_distribution["medium"] += 1
            else:
                quality_distribution["low"] += 1

        # Sort recommendations by quality score (highest first)
        recommendations.sort(key=lambda x: x["quality_score"], reverse=True)

        processing_time = time.time() - start_time
        total_processed = len(fleeting_notes)
        filtered_count = (
            total_processed - len(recommendations) if quality_threshold else 0
        )

        return {
            "total_notes_processed": total_processed,
            "quality_distribution": quality_distribution,
            "recommendations": recommendations,
            "processing_time": processing_time,
            "quality_threshold": quality_threshold,
            "filtered_count": filtered_count,
        }

    def promote_fleeting_note(
        self,
        note_path: str,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
        base_dir: Optional[Path] = None,
    ) -> Dict:
        """
        Promote a single fleeting note to permanent or literature status.

        Args:
            note_path: Path to the fleeting note to promote
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes
            base_dir: Base directory for path resolution (optional)

        Returns:
            Dict: Promotion results with details of operations performed
        """
        start_time = time.time()

        try:
            # Import DirectoryOrganizer from production-ready infrastructure
            from src.utils.directory_organizer import DirectoryOrganizer

            # Resolve note path
            if not note_path.startswith("/"):
                # If path starts with 'knowledge/', it's relative to the vault root
                if note_path.startswith("knowledge/") and base_dir:
                    # Remove 'knowledge/' prefix since base_dir already points to knowledge/
                    relative_path = note_path.replace("knowledge/", "", 1)
                    note_path_obj = base_dir / relative_path
                elif base_dir:
                    note_path_obj = base_dir / note_path
                else:
                    note_path_obj = Path(note_path)
            else:
                note_path_obj = Path(note_path)

            if not note_path_obj.exists():
                raise ValueError(f"Note not found: {note_path}")

            # Validate note is fleeting type
            content = note_path_obj.read_text(encoding="utf-8")
            metadata, body = parse_frontmatter(content)

            if metadata.get("type") != "fleeting":
                raise ValueError(
                    f"Note is not a fleeting note (type: {metadata.get('type')})"
                )

            # Get AI quality assessment for the note
            ai_result = self.process_callback(note_path_obj, fast=True)
            quality_score = ai_result.get("quality_score", 0.5)

            # Auto-detect target type if not specified
            if target_type is None:
                # Use simple heuristic: literature if it has source/url, otherwise permanent
                if metadata.get("source") or metadata.get("url"):
                    target_type = "literature"
                else:
                    target_type = "permanent"

            # Determine target directory
            if target_type == "literature":
                target_dir = self.literature_dir
            else:
                target_dir = self.permanent_dir

            if not target_dir.exists():
                target_dir.mkdir(parents=True)

            # Create target path
            target_path = target_dir / note_path_obj.name

            promotion_result = {
                "success": True,
                "promoted_notes": [
                    {
                        "note_path": str(note_path_obj),
                        "target_type": target_type,
                        "target_path": str(target_path),
                        "quality_score": quality_score,
                        "preview_mode": preview_mode,
                    }
                ],
                "batch_mode": False,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "target_directory": str(target_dir),
                "promotion_time": datetime.now().isoformat(),
                "processing_time": 0,
                "backup_created": False,
                "metadata_updated": True,
            }

            if preview_mode:
                # Preview mode - don't actually move files
                promotion_result["processing_time"] = time.time() - start_time
                return promotion_result

            # Create backup using DirectoryOrganizer
            if base_dir:
                organizer = DirectoryOrganizer(
                    base_dir.parent if base_dir.parent else base_dir
                )
                backup_path = organizer.create_backup()
                promotion_result["backup_created"] = True
                promotion_result["backup_path"] = str(backup_path)

            # Update metadata for promotion
            updated_metadata = metadata.copy()
            updated_metadata["type"] = target_type
            updated_metadata["promoted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            updated_metadata["promoted_date"] = datetime.now().strftime(
                "%Y-%m-%d %H:%M"
            )
            updated_metadata["promotion_quality_score"] = quality_score

            # Reconstruct file content with updated metadata
            updated_content = "---\n"
            for key, value in updated_metadata.items():
                if isinstance(value, list):
                    updated_content += f"{key}: {value}\n"
                elif isinstance(value, str) and " " in value:
                    updated_content += f'{key}: "{value}"\n'
                else:
                    updated_content += f"{key}: {value}\n"
            updated_content += f"---\n\n{body}"

            # Write to target location
            target_path.write_text(updated_content, encoding="utf-8")

            # Remove original file
            note_path_obj.unlink()

            promotion_result["processing_time"] = time.time() - start_time
            return promotion_result

        except Exception as e:
            return {
                "success": False,
                "promoted_notes": [
                    {
                        "note_path": note_path,
                        "error": str(e),
                        "quality_score": 0,
                        "preview_mode": preview_mode,
                    }
                ],
                "batch_mode": False,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "target_directory": "unknown",
                "promotion_time": datetime.now().isoformat(),
                "processing_time": time.time() - start_time,
                "backup_created": False,
                "error": str(e),
            }

    def promote_fleeting_notes_batch(
        self,
        quality_threshold: float = 0.7,
        target_type: Optional[str] = None,
        preview_mode: bool = False,
        base_dir: Optional[Path] = None,
    ) -> Dict:
        """
        Promote multiple fleeting notes based on quality threshold.

        Args:
            quality_threshold: Minimum quality score for promotion
            target_type: Target type ('permanent' or 'literature'), auto-detected if None
            preview_mode: If True, show what would be done without making changes
            base_dir: Base directory for path resolution (optional)

        Returns:
            Dict: Batch promotion results
        """
        start_time = time.time()

        try:
            # Get triage results to identify high-quality notes
            triage_report = self.generate_triage_report(
                quality_threshold=quality_threshold, fast=True
            )

            # Find notes eligible for promotion
            eligible_notes = [
                rec
                for rec in triage_report["recommendations"]
                if rec["action"] == "Promote to Permanent"
                and rec["quality_score"] >= quality_threshold
            ]

            if not eligible_notes:
                return {
                    "total_promoted": 0,
                    "total_skipped": triage_report["total_notes_processed"],
                    "promoted_notes": [],
                    "batch_mode": True,
                    "preview": preview_mode,
                    "preview_mode": preview_mode,
                    "quality_threshold": quality_threshold,
                    "processing_time": time.time() - start_time,
                    "backup_created": False,
                }

            # Create single backup for batch operation
            backup_created = False
            backup_path = None

            if not preview_mode and base_dir:
                try:
                    from src.utils.directory_organizer import DirectoryOrganizer

                    organizer = DirectoryOrganizer(
                        base_dir.parent if base_dir.parent else base_dir
                    )
                    backup_path = organizer.create_backup()
                    backup_created = True
                except Exception as e:
                    print(f"Warning: Could not create backup: {e}")

            # Process each eligible note
            promoted_notes = []
            for note_rec in eligible_notes:
                try:
                    single_result = self.promote_fleeting_note(
                        note_path=note_rec["note_path"],
                        target_type=target_type,
                        preview_mode=preview_mode,
                        base_dir=base_dir,
                    )

                    # Extract the promoted note info and add batch context
                    if single_result.get("promoted_notes"):
                        promoted_note = single_result["promoted_notes"][0]
                        promoted_note["batch_promotion"] = True
                        promoted_notes.append(promoted_note)

                except Exception as e:
                    # Add failed note to results
                    promoted_notes.append(
                        {
                            "note_path": note_rec["note_path"],
                            "error": str(e),
                            "quality_score": note_rec["quality_score"],
                            "batch_promotion": True,
                            "preview_mode": preview_mode,
                        }
                    )

            total_processed = triage_report["total_notes_processed"]
            total_promoted = len([n for n in promoted_notes if "error" not in n])
            total_skipped = total_processed - len(eligible_notes)

            return {
                "total_promoted": total_promoted,
                "total_skipped": total_skipped,
                "promoted_notes": promoted_notes,
                "batch_mode": True,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "quality_threshold": quality_threshold,
                "processing_time": time.time() - start_time,
                "backup_created": backup_created,
                "backup_path": str(backup_path) if backup_path else None,
            }

        except Exception as e:
            return {
                "total_promoted": 0,
                "total_skipped": 0,
                "promoted_notes": [],
                "batch_mode": True,
                "preview": preview_mode,
                "preview_mode": preview_mode,
                "quality_threshold": quality_threshold,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "backup_created": False,
            }
