# ADR-002: Extract NoteLifecycleManager from WorkflowManager

**Date**: 2025-10-14  
**Status**: Accepted  
**Trigger**: Architectural constraint violation (WorkflowManager: 2,402 LOC, 59 methods)  
**Related**: PBI-001 Status Update Bug Fix

---

## Context

WorkflowManager has grown to **2,402 LOC with 59 methods**, violating architectural constraints:
- **Hard limit**: 500 LOC, 20 methods
- **Violation severity**: 380% over LOC limit, 295% over method limit
- **Class name trigger**: "Manager" + >300 LOC = critical refactoring required

### Immediate Problem
Need to implement PBI-001 (status update bug fix) but cannot add to WorkflowManager without further architectural debt.

### Current Architecture Issues
1. **God Class Anti-Pattern**: WorkflowManager handles:
   - Note processing (AI enhancement, tagging, quality scoring)
   - Connection discovery
   - Weekly review generation
   - Analytics and metrics
   - Image integrity monitoring
   - Fleeting note lifecycle
   - **Status management** (mixed with other concerns)

2. **High Coupling**: 59 methods create complex interdependencies
3. **Test Complexity**: Tests require extensive mocking of unrelated features
4. **Merge Conflicts**: Frequent conflicts from multiple developers/features

---

## Decision

**Extract `NoteLifecycleManager`** as a focused class responsible for note lifecycle state management.

### Responsibilities (Single Responsibility Principle)
- Note status transitions (`inbox` → `promoted` → `published`)
- Status validation (prevent invalid transitions)
- Lifecycle metadata management (`processed_date`, `promoted_date`, `published_date`)
- Status history tracking (for audit/undo)

### Non-Responsibilities (Keep Decoupled)
- ❌ AI processing (stays in WorkflowManager)
- ❌ File movement (delegated to DirectoryOrganizer)
- ❌ Quality scoring (stays in enhancer)
- ❌ Weekly review (stays in WorkflowManager)

---

## Design

### Class Structure

```python
# development/src/ai/note_lifecycle_manager.py

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

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
    
    ~150 LOC target, <10 methods
    """
    
    VALID_STATUSES = ["inbox", "promoted", "published", "archived"]
    VALID_TRANSITIONS = {
        "inbox": ["promoted", "archived"],
        "promoted": ["published", "inbox", "archived"],
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
        pass
    
    def validate_transition(
        self,
        current_status: str,
        new_status: str
    ) -> tuple[bool, str]:
        """
        Validate if status transition is allowed.
        
        Returns:
            (is_valid, error_message)
        """
        pass
    
    def get_status_history(
        self,
        note_path: Path
    ) -> List[StatusTransition]:
        """Get complete status history for a note."""
        pass
    
    def _add_timestamp_field(
        self,
        frontmatter: Dict,
        status: str
    ) -> str:
        """Add appropriate timestamp field for status."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if status == "promoted":
            frontmatter["processed_date"] = timestamp
        elif status == "published":
            frontmatter["promoted_date"] = timestamp
        elif status == "archived":
            frontmatter["archived_date"] = timestamp
            
        return timestamp
```

### Integration with WorkflowManager

```python
# development/src/ai/workflow_manager.py

class WorkflowManager:
    def __init__(self, base_directory: str | None = None):
        # ... existing init ...
        
        # Add lifecycle manager
        from .note_lifecycle_manager import NoteLifecycleManager
        self.lifecycle_manager = NoteLifecycleManager()
    
    def process_inbox_note(self, note_path: str, dry_run: bool = False, fast: bool | None = None) -> Dict:
        # ... existing processing ...
        
        # After successful AI processing (line ~380):
        if needs_ai_update and not dry_run:
            # Delegate status update to lifecycle manager
            status_result = self.lifecycle_manager.update_status(
                note_file,
                new_status="promoted",
                reason="AI processing completed",
                metadata={
                    "quality_score": quality_score,
                    "ai_processed": True
                }
            )
            
            if status_result["status_updated"]:
                results["status_updated"] = status_result["new_status"]
                # Lifecycle manager handles frontmatter updates
```

---

## Implementation Plan (TDD)

### Phase 1: Extract NoteLifecycleManager (2 hours)
1. **RED**: Create `test_note_lifecycle_manager.py` with 6 core tests
   - `test_update_status_inbox_to_promoted()`
   - `test_update_status_adds_processed_date()`
   - `test_validate_transition_allowed()`
   - `test_validate_transition_forbidden()`
   - `test_update_status_preserves_metadata()`
   - `test_update_status_idempotent()`

2. **GREEN**: Implement minimal `NoteLifecycleManager`
   - ~150 LOC target
   - Single responsibility: status management only
   - Uses existing `parse_frontmatter`, `build_frontmatter`, `safe_write`

3. **REFACTOR**: Polish error handling, add docstrings

### Phase 2: Integrate with WorkflowManager (1 hour)
1. **RED**: Update `test_workflow_manager_status_update.py` to verify integration
2. **GREEN**: WorkflowManager delegates to NoteLifecycleManager
3. **REFACTOR**: Remove duplicate status logic from WorkflowManager

### Phase 3: Validate & Document (30 minutes)
1. Run full test suite (expect all existing tests to pass)
2. Update lessons learned
3. Git commit with clean history

**Total Estimate**: 3.5 hours

---

## Consequences

### Positive
- ✅ WorkflowManager reduced by ~100 LOC (still needs further refactoring)
- ✅ Single Responsibility: Status management isolated
- ✅ Testability: NoteLifecycleManager tests don't require AI mocking
- ✅ Reusability: Other systems can use lifecycle manager independently
- ✅ Architectural compliance: Moving toward <500 LOC per class

### Negative
- ⚠️ New class adds one more file to maintain
- ⚠️ WorkflowManager still 2,300+ LOC (requires Phase 2 refactoring)
- ⚠️ Import dependency added (WorkflowManager → NoteLifecycleManager)

### Neutral
- 📝 Sets pattern for future extractions (connection manager, analytics manager)
- 📝 Demonstrates TDD refactoring methodology

---

## Alternatives Considered

### Alternative 1: Add to WorkflowManager anyway
**Rejected**: Violates architectural constraints, increases technical debt

### Alternative 2: Create NoteStatusService (minimal)
**Rejected**: Too narrow, doesn't address broader lifecycle concerns (will need another extraction later)

### Alternative 3: Create InboxProcessor (all inbox logic)
**Rejected**: Too broad, would be another god class (inbox processing includes AI, quality, connections)

### Alternative 4: Inline status update (no abstraction)
**Rejected**: Misses opportunity to enforce valid state transitions

---

## Implementation Status

### ✅ Phase 1: NoteLifecycleManager (COMPLETED 2025-10-14)
- **Status**: Production Ready
- **LOC Extracted**: 222 LOC
- **Tests**: 16/16 passing (100%)
- **Reduction**: ~100 LOC from WorkflowManager
- **Deliverable**: `development/src/ai/note_lifecycle_manager.py`
- **Lessons Learned**: `Projects/COMPLETED-2025-10/pbi-001-note-lifecycle-status-management-lessons-learned.md`

### ✅ Phase 2: ConnectionCoordinator (COMPLETED 2025-10-14)
- **Status**: Production Ready
- **LOC Extracted**: 196 LOC  
- **Tests**: 12/12 passing (100%)
- **Reduction**: 6 LOC from WorkflowManager (+ 196 isolated)
- **Deliverable**: `development/src/ai/connection_coordinator.py`
- **Lessons Learned**: `Projects/ACTIVE/adr-002-phase2-connection-coordinator-extraction-lessons-learned.md`
- **Key Achievement**: Clean separation of connection discovery from god class

### Current State
- **WorkflowManager**: 2642 LOC, 58 methods (down from 2648 LOC, 59 methods)
- **Remaining**: ~2142 LOC to extract to reach <500 LOC target
- **Progress**: 0.2% LOC reduction, significant responsibility isolation

## Follow-up Work

### Immediate (Next Session)
- [ ] Extract AnalyticsCoordinator (analytics/metrics logic, ~400 LOC estimated)
- [ ] OR Extract PromotionEngine (auto-promotion logic, ~200 LOC estimated)

### Short Term (Phases 3-4)
- [ ] Continue systematic extraction following proven TDD pattern
- [ ] Target: 3-4 more extractions needed
- [ ] Each extraction: ~200-400 LOC with comprehensive tests

### Long Term (Phase 6)
- [ ] Complete WorkflowManager decomposition
- [ ] Target: <500 LOC, <20 methods
- [ ] Full architectural compliance
- [ ] Consider ConnectionCoordinator + ConnectionManager unification

---

## References

- **Constraint**: `.windsurf/rules/architectural-constraints.md`
- **Violation Metrics**: 2,402 LOC, 59 methods (380% over, 295% over)
- **Planning**: `Projects/ACTIVE/PBI-PLANNING-SESSION-2025-10-14.md`
- **Related Work**: DirectoryOrganizer (P0+P1 complete), demonstrates proper architecture

---

## Approval

**Decision Maker**: Developer (architectural constraint enforcement)  
**Date**: 2025-10-14  
**Rationale**: Hard architectural limit violated, refactoring mandatory before feature work
