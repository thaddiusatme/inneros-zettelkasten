"""
Centralized Bug Report Creation for AI Workflow Failures.

This utility provides standardized bug report creation for various workflow
failures, enabling systematic tracking and debugging of AI system issues.

Features:
- AI enhancement failure reports (tier-specific)
- Total workflow failure reports (multi-system)
- Standardized markdown format for human review
- Automatic timestamping and report organization

Reports are written to: .automation/review_queue/
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class BugReporter:
    """
    Creates standardized bug reports for AI workflow failures.
    
    All reports are written to .automation/review_queue/ directory
    with timestamps for easy tracking and review.
    
    Examples:
        >>> reporter = BugReporter(Path("/path/to/zettelkasten"))
        >>> reporter.create_ai_failure_report(
        ...     "Inbox/test.md",
        ...     {"tier": "local_llm", "error": "Connection refused"}
        ... )
        PosixPath('.../review_queue/AI_FAILURE_20251005_2000.md')
    """

    def __init__(self, base_dir: Path):
        """
        Initialize BugReporter with base directory.
        
        Args:
            base_dir: Root directory of the Zettelkasten vault
        """
        self.base_dir = Path(base_dir)
        self.review_queue = self.base_dir / ".automation" / "review_queue"
        self.review_queue.mkdir(parents=True, exist_ok=True)

    def create_ai_failure_report(
        self,
        note_path: str,
        error_details: Dict[str, Any]
    ) -> Path:
        """
        Create AI enhancement failure report.
        
        Creates a detailed report when AI enhancement fails at any tier
        (local LLM, external API, or total failure). Includes error details,
        tier information, and actionable troubleshooting steps.
        
        Args:
            note_path: Path to the note that failed enhancement
            error_details: Dict with error information:
                - tier: Which AI tier failed (local_llm, external_api, degraded)
                - error_type: Exception type (ConnectionError, TimeoutError, etc.)
                - error: Error message string
                - fallback: Whether fallback was used (optional)
        
        Returns:
            Path to the created bug report file
        
        Examples:
            >>> reporter = BugReporter(Path("."))
            >>> report_path = reporter.create_ai_failure_report(
            ...     "Inbox/note.md",
            ...     {
            ...         "tier": "local_llm",
            ...         "error_type": "ConnectionError",
            ...         "error": "Ollama service unreachable"
            ...     }
            ... )
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        bug_report_path = self.review_queue / f"AI_FAILURE_{timestamp}.md"

        report_content = f"""# AI Enhancement Failure Report

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Note**: {note_path}
**Tier**: {error_details.get('tier', 'Unknown')}
**Error Type**: {error_details.get('error_type', 'Unknown')}
**Error**: {error_details.get('error', 'Unknown error')}

## Failure Details
- Fallback Used: {error_details.get('fallback', False)}
- Tier: {error_details.get('tier', 'Unknown')}

## Action Required
- [ ] Check Ollama service status (if local_llm failure)
- [ ] Verify model availability
- [ ] Review error logs
- [ ] Test with different note content
- [ ] Check API keys if using external API
- [ ] Verify network connectivity

## Error Details
```
{error_details}
```
"""

        bug_report_path.write_text(report_content)
        return bug_report_path

    def create_workflow_failure_report(
        self,
        note_path: str,
        result: Dict[str, Any]
    ) -> Path:
        """
        Create total workflow failure report for multi-system failures.
        
        Creates a CRITICAL priority report when multiple systems fail
        simultaneously (3+ errors). Includes complete error summary and
        full result context for comprehensive debugging.
        
        Args:
            note_path: Path to the note that failed processing
            result: Complete workflow result dict with:
                - errors: List of error dicts (stage, type, error)
                - analytics: Analytics result (may be degraded)
                - ai_enhancement: AI enhancement result (may be degraded)
                - connections: Connection discovery result (may be empty)
        
        Returns:
            Path to the created bug report file
        
        Examples:
            >>> reporter = BugReporter(Path("."))
            >>> result = {
            ...     "errors": [
            ...         {"stage": "analytics", "error": "File not found"},
            ...         {"stage": "ai_enhancement", "error": "LLM timeout"},
            ...         {"stage": "connections", "error": "DB unavailable"}
            ...     ]
            ... }
            >>> report_path = reporter.create_workflow_failure_report(
            ...     "Inbox/note.md", result
            ... )
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        bug_report_path = self.review_queue / f"WORKFLOW_FAILURE_{timestamp}.md"

        errors_summary = "\n".join([
            f"- **{err['stage']}**: {err['error']}"
            for err in result.get('errors', [])
        ])

        report_content = f"""# Total Workflow Failure Report - CRITICAL

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Note**: {note_path}
**Errors**: {len(result.get('errors', []))} CRITICAL failures

## Failed Systems
{errors_summary}

## Action Required
- [ ] Check system health for all managers
- [ ] Review configuration settings
- [ ] Verify file accessibility
- [ ] Check service availability (Ollama, APIs)
- [ ] Review error logs

## Complete Result
```json
{result}
```
"""

        bug_report_path.write_text(report_content)
        return bug_report_path
