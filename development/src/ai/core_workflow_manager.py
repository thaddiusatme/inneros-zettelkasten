"""
Core Workflow Manager - Orchestrates Analytics, AI Enhancement, and Connection Discovery

This manager coordinates the workflow of processing notes through three specialized managers:
1. AnalyticsManager - Pure metrics calculation (quality scoring, orphaned/stale detection)
2. AIEnhancementManager - AI-powered enhancement with 3-tier fallback
3. ConnectionManager - Semantic link discovery and suggestions

Design Principles:
- Exception-based error handling for clean orchestration
- Cost gating to prevent expensive AI operations on low-quality notes
- Bug report creation for failures requiring human review
- Graceful degradation on partial failures
- Dry run mode for testing/preview without side effects
"""

from pathlib import Path
from typing import TYPE_CHECKING

from src.ai.types import WorkflowResult, ConfigDict
from src.utils.bug_reporter import BugReporter
from src.utils.result_validator import ResultValidator

if TYPE_CHECKING:
    from src.ai.analytics_manager import AnalyticsManager
    from src.ai.ai_enhancement_manager import AIEnhancementManager
    from src.ai.connection_manager import ConnectionManager


class CoreWorkflowManager:
    """
    Orchestrates the complete workflow for processing notes.

    Coordinates three specialized managers:
    - AnalyticsManager: Quality assessment and metrics
    - AIEnhancementManager: AI-powered tagging and summarization
    - ConnectionManager: Semantic link discovery

    Implements:
    - Exception-based error handling
    - Cost gating (skip AI for low-quality notes)
    - Bug report creation on failures
    - Result validation with sensible defaults
    """

    def __init__(
        self,
        base_dir: Path,
        config: ConfigDict,
        analytics_manager: "AnalyticsManager",
        ai_enhancement_manager: "AIEnhancementManager",
        connection_manager: "ConnectionManager",
    ) -> None:
        """
        Initialize CoreWorkflowManager with dependency injection.

        Args:
            base_dir: Base directory of the Zettelkasten vault
            config: Configuration dict with thresholds and settings
            analytics_manager: AnalyticsManager instance
            ai_enhancement_manager: AIEnhancementManager instance
            connection_manager: ConnectionManager instance
        """
        self.base_dir = Path(base_dir)
        self.config = config
        self.analytics = analytics_manager
        self.ai_enhancement = ai_enhancement_manager
        self.connections = connection_manager
        self.bug_reporter = BugReporter(base_dir)

    def process_inbox_note(
        self, note_path: str, dry_run: bool = False
    ) -> WorkflowResult:
        """
        Process a note through the complete workflow.

        Workflow stages:
        1. Analytics assessment (quality, metadata)
        2. Cost gating check (skip AI if quality too low)
        3. AI enhancement (tagging, summarization) if quality gate passes
        4. Connection discovery (link suggestions)

        Args:
            note_path: Path to the note file (relative to base_dir)
            dry_run: If True, prevent file writes and API costs

        Returns:
            Dict containing results from all managers with structure:
            {
                'success': bool,
                'analytics': {...quality metrics...},
                'ai_enhancement': {...tags, summary...},
                'connections': [...link suggestions...],
                'errors': [...error dicts...],
                'warnings': [...warning strings...],
                'dry_run': bool (if applicable)
            }

        Exception Handling:
        - ValueError from Analytics: Returns validation error (stops processing)
        - FileNotFoundError from Analytics: Returns not_found error (stops processing)
        - AI/Connection failures: Graceful degradation with error recording

        Examples:
            >>> # Example 1: Basic usage with successful processing
            >>> from pathlib import Path
            >>> core = CoreWorkflowManager(
            ...     base_dir=Path('knowledge'),
            ...     config={'ai_enhancement': {'cost_gate_threshold': 0.3}},
            ...     analytics_manager=analytics,
            ...     ai_enhancement_manager=ai_enhancement,
            ...     connection_manager=connections
            ... )
            >>> result = core.process_inbox_note('Inbox/fleeting-20250924-idea.md')
            >>> print(f"Success: {result['success']}")
            Success: True
            >>> print(f"Quality: {result['analytics']['quality_score']}")
            Quality: 0.75
            >>> print(f"Tags: {result['ai_enhancement']['tags']}")
            Tags: ['machine-learning', 'zettelkasten', 'productivity']
            >>> print(f"Connections: {len(result['connections'])} links suggested")
            Connections: 3 links suggested

            >>> # Example 2: Dry run mode - preview without AI costs
            >>> result = core.process_inbox_note('Inbox/test-note.md', dry_run=True)
            >>> assert result['dry_run'] == True
            >>> # AI calls are skipped or use cached/mock results
            >>> if result['ai_enhancement'].get('skipped'):
            ...     print("AI enhancement skipped in dry run")

            >>> # Example 3: Low quality note - cost gating in action
            >>> result = core.process_inbox_note('Inbox/low-quality-snippet.md')
            >>> if result['ai_enhancement'].get('skipped'):
            ...     print(f"AI skipped: {result['ai_enhancement']['reason']}")
            ...     print(f"Quality: {result['ai_enhancement']['quality_score']}")
            ...     print(f"Threshold: {result['ai_enhancement']['threshold']}")
            AI skipped: quality_too_low
            Quality: 0.25
            Threshold: 0.3
            >>> # Analytics and connections still run, only AI is skipped
            >>> assert result['analytics']['quality_score'] < 0.3
            >>> assert result['success'] == True  # Workflow succeeds with degraded result

            >>> # Example 4: Error handling - graceful degradation
            >>> result = core.process_inbox_note('Inbox/problematic-note.md')
            >>> if not result['success']:
            ...     for error in result['errors']:
            ...         print(f"{error['stage']}: {error['type']} - {error['error']}")
            analytics: validation - Invalid YAML frontmatter
            >>> # Partial results may still be available
            >>> if result['connections']:
            ...     print(f"Found {len(result['connections'])} connections despite errors")

            >>> # Example 5: Accessing specific manager results
            >>> result = core.process_inbox_note('Inbox/literature-note.md')
            >>> # Analytics results
            >>> quality = result['analytics']['quality_score']
            >>> word_count = result['analytics'].get('word_count', 0)
            >>> link_count = result['analytics'].get('link_count', 0)
            >>>
            >>> # AI Enhancement results
            >>> if result['ai_enhancement'].get('success'):
            ...     tags = result['ai_enhancement']['tags']
            ...     summary = result['ai_enhancement']['summary']
            ...     print(f"Generated {len(tags)} tags and summary")
            >>>
            >>> # Connection Discovery results
            >>> for conn in result['connections']:
            ...     print(f"Suggest link to: {conn['target_note']}")
            ...     print(f"  Relevance: {conn['relevance_score']}")
            ...     print(f"  Reason: {conn['explanation']}")

            >>> # Example 6: Handling warnings
            >>> result = core.process_inbox_note('Inbox/edge-case-note.md')
            >>> for warning in result.get('warnings', []):
            ...     print(f"Warning: {warning}")
            Warning: AI enhancement skipped: quality score 0.28 below threshold 0.3
        """
        # Analytics stage - raises exceptions on validation/file errors
        try:
            analytics_result = self.analytics.assess_quality(note_path, dry_run=dry_run)
        except ValueError as e:
            # Validation error - stop early
            return {
                "success": False,
                "analytics": {},
                "ai_enhancement": {},
                "connections": {},
                "errors": [
                    {"stage": "analytics", "type": "validation", "error": str(e)}
                ],
                "warnings": [],
            }
        except FileNotFoundError as e:
            # File not found - stop early
            return {
                "success": False,
                "analytics": {},
                "ai_enhancement": {},
                "connections": {},
                "errors": [
                    {"stage": "analytics", "type": "not_found", "error": str(e)}
                ],
                "warnings": [],
            }
        except Exception as e:
            # Generic Analytics error - continue with degraded result
            analytics_result = {"success": False, "quality_score": 0.0, "error": str(e)}
            analytics_error = {
                "stage": "analytics",
                "type": "exception",
                "error": str(e),
            }
        else:
            # Analytics succeeded
            analytics_error = None

        # Initialize result structure
        result = {
            "success": False if analytics_error else True,
            "analytics": analytics_result,
            "ai_enhancement": {},
            "connections": {},
            "errors": [analytics_error] if analytics_error else [],
            "warnings": [],
        }

        # Add dry_run flag if applicable
        if dry_run:
            result["dry_run"] = True

        # Cost gating - skip AI if quality too low (but only if Analytics succeeded)
        quality_score = analytics_result.get("quality_score", 0.0)
        cost_gate_threshold = self.config.get("ai_enhancement", {}).get(
            "cost_gate_threshold", 0.3
        )

        # Only apply cost gating if Analytics succeeded
        analytics_succeeded = analytics_result.get("success", True)
        if analytics_succeeded and quality_score < cost_gate_threshold:
            # Skip AI enhancement due to low quality
            result["ai_enhancement"] = {
                "success": False,
                "skipped": True,
                "reason": "quality_too_low",
                "quality_score": quality_score,
                "threshold": cost_gate_threshold,
                "tags": [],
                "summary": "",
            }
            result["warnings"].append(
                f"AI enhancement skipped: quality score {quality_score} below threshold {cost_gate_threshold}"
            )
        else:
            # Run AI enhancement
            try:
                ai_result = self.ai_enhancement.enhance_note(
                    note_path, fast=False, dry_run=dry_run
                )
                result["ai_enhancement"] = ai_result

                # Check for AI failures
                if not ai_result.get("success", False):
                    result["success"] = False
                    result["errors"].append(
                        {
                            "stage": "ai_enhancement",
                            "type": "enhancement_failed",
                            "error": "AI enhancement failed with fallback",
                        }
                    )
                    # Note: Bug reporting handled by AIEnhancementManager

            except Exception as e:
                # Graceful degradation on AI failure
                result["ai_enhancement"] = {
                    "success": False,
                    "error": str(e),
                    "tags": [],
                    "summary": "",
                }
                result["errors"].append(
                    {"stage": "ai_enhancement", "type": "exception", "error": str(e)}
                )

        # Connection discovery - runs independently
        try:
            connections_result = self.connections.discover_links(
                note_path, dry_run=dry_run
            )
            # discover_links returns list directly
            result["connections"] = connections_result if connections_result else []
        except Exception as e:
            # Graceful degradation on connection failure
            result["connections"] = []
            result["errors"].append(
                {"stage": "connections", "type": "exception", "error": str(e)}
            )

        # Validate and apply sensible defaults
        result = ResultValidator.validate_workflow_result(result)

        # Update note status to 'promoted' if processing succeeded and not in dry_run mode
        if result["success"] and not dry_run:
            try:
                from pathlib import Path
                from src.ai.note_lifecycle_manager import NoteLifecycleManager

                lifecycle = NoteLifecycleManager(base_dir=self.base_dir)
                note_path_obj = (
                    Path(note_path)
                    if not Path(note_path).is_absolute()
                    else Path(note_path)
                )
                if not note_path_obj.is_absolute():
                    note_path_obj = self.base_dir / note_path_obj

                status_result = lifecycle.update_status(
                    note_path_obj,
                    new_status="promoted",
                    reason="AI processing completed successfully",
                )

                if status_result.get("validation_passed"):
                    result["status_updated"] = status_result.get(
                        "status_updated", "promoted"
                    )
                else:
                    result["warnings"].append(
                        f"Status update failed: {status_result.get('error', 'Unknown error')}"
                    )
            except Exception as e:
                result["warnings"].append(f"Status update failed: {str(e)}")

        # Check for total workflow failure (multiple errors)
        if len(result["errors"]) >= 3:
            result["warnings"].append(
                "Total workflow failure - multiple systems failed"
            )
            self.bug_reporter.create_workflow_failure_report(note_path, result)

        return result
