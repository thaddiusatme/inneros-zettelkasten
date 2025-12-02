# P0-1 RED Phase: Test Failure Analysis

**Date**: 2025-11-02 08:14  
**Branch**: `fix/p0-workflow-manager-promotion`  
**GitHub Issue**: #41

## Summary

**Total Failures**: 16 tests  
**Categories**: 3 distinct failure patterns

---

## Category 1: Core Promotion Return Values (2 failures)

### Files Affected
- `tests/unit/test_workflow_manager.py::TestWorkflowManager::test_promote_note_to_permanent`
- `tests/unit/test_workflow_manager.py::TestWorkflowManager::test_promote_note_to_fleeting`

### Error Pattern
```python
KeyError: 'success'
```

### Root Cause
`WorkflowManager.promote_note()` and `promote_fleeting_note()` methods are not returning the expected dictionary structure with a 'success' key.

### Expected Return Structure
```python
{
    'success': bool,
    'note_path': str,
    'target_type': str,
    'message': str
}
```

### Implementation Location
- **File**: `development/src/ai/workflow_manager_adapter.py`
- **Methods**: `promote_note()`, `promote_fleeting_note()`

---

## Category 2: Auto-Promotion Logic (10 failures)

### Files Affected
- `test_auto_promote_filters_by_quality_threshold`
- `test_auto_promote_routes_by_type_fleeting`
- `test_auto_promote_routes_by_type_literature`
- `test_auto_promote_routes_by_type_permanent`
- `test_auto_promote_updates_status_to_published`
- `test_auto_promote_adds_promoted_date_timestamp`
- `test_auto_promote_custom_quality_threshold`
- `test_auto_promote_batch_processing_multiple_notes`
- `test_auto_promote_handles_missing_type_field`
- `test_auto_promote_skips_non_promoted_status`

### Error Pattern
```
ERROR src.ai.promotion_engine:promotion_engine.py:342 
Promotion failed for {filename}: NoteLifecycleManager requires base_dir for promote_note()

AssertionError: Should promote {N} note(s)
assert 0 == {expected_count}
```

### Root Cause
The auto-promotion functionality was removed or broken during the WorkflowManager decomposition. The PromotionEngine is failing to properly initialize NoteLifecycleManager with required `base_dir` parameter.

### Expected Behavior
- Filter notes by quality threshold (default 0.75)
- Route notes to correct target type based on 'type' field
- Update status to 'published' after promotion
- Add 'promoted_date' timestamp
- Support custom quality thresholds
- Batch process multiple notes
- Handle missing 'type' fields gracefully
- Only process notes with status='promoted'

### Implementation Location
- **Primary**: `development/src/ai/core_workflow_manager.py`
- **Method**: `auto_promote_notes(quality_threshold, note_type_filter)`
- **Helper**: Quality filtering, type routing, status updates
- **Delegation**: `development/src/ai/workflow_manager_adapter.py::auto_promote()`

---

## Category 3: Status Update Logic (4 failures)

### Files Affected
- `test_process_inbox_note_updates_status_to_promoted`
- `test_process_inbox_note_adds_processed_date`
- `test_process_inbox_note_idempotent_status_update`
- `test_process_inbox_note_status_update_preserves_other_metadata`

### Error Patterns
1. **Missing return key**: `assert 'status_updated' in result`
2. **Missing timestamp**: `assert re.search('processed_date:\\s*\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}', content)`
3. **Status not updated**: `assert 'status: promoted' in content` (status remains 'inbox')
4. **Metadata not preserved**: Status field not being updated while preserving other fields

### Root Cause
The `process_inbox_note()` method does not update the status field or add timestamps to the note's frontmatter. It only processes the note but doesn't persist the lifecycle state changes.

### Expected Behavior
- Update 'status' field from 'inbox' to 'promoted' in frontmatter
- Add 'processed_date' timestamp (format: YYYY-MM-DD HH:MM)
- Return dict includes 'status_updated': True
- Preserve all other metadata fields (tags, custom fields, etc.)
- Idempotent updates (don't duplicate timestamps on re-processing)

### Implementation Location
- **File**: `development/src/ai/core_workflow_manager.py`
- **Method**: `_update_note_status(note_path, new_status)`
- **Integration**: Called from `process_inbox_note()` after successful processing

---

## Test Execution Commands

```bash
# Run all 16 failing tests
pytest tests/unit/test_workflow_manager_auto_promotion.py -v
pytest tests/unit/test_workflow_manager_status_update.py -v
pytest tests/unit/test_workflow_manager.py -k "promote_note" -v

# Run specific category
pytest tests/unit/test_workflow_manager.py::TestWorkflowManager::test_promote_note_to_permanent -v
pytest tests/unit/test_workflow_manager_auto_promotion.py::TestAutoPromotionSystem -v
pytest tests/unit/test_workflow_manager_status_update.py::TestWorkflowManagerStatusUpdate -v
```

---

## Next Steps (GREEN Phase)

### P0-1.1: Fix Core Promotion Return Values (30 min)
- Update `workflow_manager_adapter.py::promote_note()` 
- Update `workflow_manager_adapter.py::promote_fleeting_note()`
- Return proper dict with 'success' key

### P0-1.2: Implement Auto-Promotion Logic (1.5-2 hours)
- Create `core_workflow_manager.py::auto_promote_notes()`
- Implement quality filtering using AnalyticsManager
- Add type-based routing (fleeting/literature/permanent)
- Wire delegation in adapter

### P0-1.3: Fix Status Update Logic (45 min)
- Create `core_workflow_manager.py::_update_note_status()`
- Parse/update frontmatter with status and timestamp
- Ensure idempotent updates
- Preserve all existing metadata

---

**RED Phase Duration**: 10 minutes  
**Next**: GREEN Phase Implementation
