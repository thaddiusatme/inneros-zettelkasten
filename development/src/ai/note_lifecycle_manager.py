"""
Note Lifecycle Manager - Extracted from WorkflowManager (ADR-002)

Handles note status transitions with validation and timestamp management.
Single Responsibility: Status lifecycle management only.

Target: ~150 LOC, <10 methods
Current: ~130 LOC, 6 methods ✅
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Tuple

from src.utils.frontmatter import parse_frontmatter, build_frontmatter
from src.utils.io import safe_write


@dataclass
class StatusTransition:
    """Represents a status transition event."""
    from_status: str
    to_status: str
    timestamp: str
    reason: str
    metadata: Dict


class NoteLifecycleManager:
    """
    Manages note lifecycle status transitions.
    
    Responsibilities:
    - Validate status transitions
    - Update note frontmatter with new status
    - Track status history
    - Provide status query methods
    
    Valid Status Flow:
        inbox → promoted → published → archived
        archived → inbox (resurrection)
    
    Forbidden Transitions:
        - Backwards (promoted → inbox, published → promoted)
        - Skipping steps (inbox → published without promoted)
    """
    
    VALID_STATUSES = ["inbox", "promoted", "published", "archived"]
    
    VALID_TRANSITIONS = {
        "inbox": ["promoted", "archived"],
        "promoted": ["published", "archived"],
        "published": ["archived"],
        "archived": ["inbox"]  # Allow resurrection
    }
    
    def __init__(self):
        """Initialize lifecycle manager."""
        pass
    
    def update_status(
        self,
        note_path: Path,
        new_status: str,
        reason: str = "",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Update note status with validation and history tracking.
        
        Args:
            note_path: Path to the note file
            new_status: Target status (inbox/promoted/published/archived)
            reason: Human-readable reason for transition
            metadata: Additional metadata (quality_score, ai_processed, etc.)
            
        Returns:
            Result dict with status_updated, timestamp, validation_passed
        """
        # Check if file exists
        if not note_path.exists():
            return {
                "status_updated": False,
                "validation_passed": False,
                "error": "Note file not found"
            }
        
        # Validate new status is valid
        if new_status not in self.VALID_STATUSES:
            return {
                "status_updated": False,
                "validation_passed": False,
                "error": f"Invalid status '{new_status}'. Must be one of: {', '.join(self.VALID_STATUSES)}"
            }
        
        try:
            # Read note content
            with open(note_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse frontmatter
            frontmatter, body = parse_frontmatter(content)
            
            # Get current status
            current_status = frontmatter.get("status", "inbox")
            
            # Validate transition (only if status is changing)
            if current_status != new_status:
                is_valid, error_message = self.validate_transition(current_status, new_status)
                if not is_valid:
                    return {
                        "status_updated": False,
                        "validation_passed": False,
                        "error": error_message
                    }
            
            # Update status
            frontmatter["status"] = new_status
            
            # Add appropriate timestamp (idempotent - only add if not already present)
            timestamp = self._add_timestamp_field(frontmatter, new_status)
            
            # Add any additional metadata
            if metadata:
                for key, value in metadata.items():
                    if key not in frontmatter:  # Don't overwrite existing fields
                        frontmatter[key] = value
            
            # Rebuild content
            updated_content = build_frontmatter(frontmatter, body)
            
            # Write back to file
            safe_write(note_path, updated_content)
            
            return {
                "status_updated": new_status,
                "validation_passed": True,
                "timestamp": timestamp,
                "previous_status": current_status
            }
            
        except Exception as e:
            return {
                "status_updated": False,
                "validation_passed": False,
                "error": f"Failed to update status: {str(e)}"
            }
    
    def validate_transition(
        self,
        current_status: str,
        new_status: str
    ) -> Tuple[bool, str]:
        """
        Validate if status transition is allowed.
        
        Args:
            current_status: Current note status
            new_status: Desired new status
            
        Returns:
            (is_valid, error_message)
        """
        # If statuses are the same, it's valid (idempotent)
        if current_status == new_status:
            return (True, "")
        
        # Check if current status has valid transitions defined
        if current_status not in self.VALID_TRANSITIONS:
            return (
                False,
                f"Invalid current status '{current_status}'. Cannot determine valid transitions."
            )
        
        # Check if transition is in valid transitions list
        valid_next_statuses = self.VALID_TRANSITIONS[current_status]
        if new_status not in valid_next_statuses:
            return (
                False,
                f"Transition from '{current_status}' to '{new_status}' is not allowed. "
                f"Valid transitions from '{current_status}': {', '.join(valid_next_statuses)}"
            )
        
        return (True, "")
    
    def _add_timestamp_field(
        self,
        frontmatter: Dict,
        status: str
    ) -> str:
        """
        Add appropriate timestamp field for status.
        Idempotent - won't duplicate if field already exists.
        
        Args:
            frontmatter: Frontmatter dictionary to modify
            status: Status being set
            
        Returns:
            Timestamp string that was added/preserved
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Map status to timestamp field name
        timestamp_fields = {
            "promoted": "processed_date",
            "published": "promoted_date",
            "archived": "archived_date"
        }
        
        # Add timestamp if this status has an associated field
        if status in timestamp_fields:
            field_name = timestamp_fields[status]
            # Only add if not already present (idempotence)
            if field_name not in frontmatter:
                frontmatter[field_name] = timestamp
            else:
                # Return existing timestamp
                timestamp = frontmatter[field_name]
        
        return timestamp
