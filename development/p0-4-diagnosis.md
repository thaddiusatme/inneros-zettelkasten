# P0-4 RED Phase: PromotionEngine Return Format Diagnosis

**Date**: 2025-11-02  
**Branch**: `fix/p0-4-promotion-engine-return-format`  
**Status**: RED Phase Complete - Root causes identified

---

## Test Failures Summary

### 5 Failing Tests Documented:

1. ✗ `test_promote_note_to_permanent` - **KeyError: 'success'**
2. ✗ `test_promote_note_to_literature` - **KeyError: 'success'**  
3. ✗ `test_auto_promote_ready_notes_scans_inbox` - **assert 0 == 3** (no candidates found)
4. ✗ `test_auto_promote_tracks_by_type` - **TypeError: 'int' object not subscriptable**
5. ✗ `test_auto_promote_moves_notes_end_to_end` - **AttributeError: 'int' has no 'get'**

---

## Root Cause Analysis

### Problem 1: `by_type` Return Format Mismatch (CRITICAL)

**Location**: `promotion_engine.py` lines 288-292

**Current Implementation**:
```python
"by_type": {
    "fleeting": 0,      # INTEGER (promoted count)
    "literature": 0,    # INTEGER
    "permanent": 0,     # INTEGER
}
```

**Expected by Tests** (line 376 in test_promotion_engine.py):
```python
assert result["by_type"]["permanent"]["promoted"] == 1
#                                      ^^^^^^^^^^^ Expects nested dict!
```

**Expected by CLI** (line 103 in core_workflow_cli.py):
```python
promoted_count = counts.get("promoted", 0)
# where counts = results["by_type"][note_type]
# Expects: {"promoted": int, "skipped": int}
```

**Impact**: 
- Tests 4 & 5 fail with `TypeError: 'int' object is not subscriptable`
- CLI crashes with `AttributeError: 'int' object has no attribute 'get'`

---

### Problem 2: Status Field Requirement Change (REGRESSION)

**Location**: `promotion_engine.py` line 335

**Current Code**:
```python
status = frontmatter.get("status", "inbox")
if status != self.AUTO_PROMOTION_STATUS:  # AUTO_PROMOTION_STATUS = "promoted"
    logger.debug(f"Skipping {note_path.name}: Status '{status}' != required 'promoted'")
    continue
```

**Test Setup** (line 290 in tests):
```python
status: inbox  # Tests expect auto-promotion to work on inbox notes!
```

**Impact**:
- Test 3 fails with `assert 0 == 3` - NO candidates found because all test notes have `status: inbox`
- `total_candidates` stays at 0 because all notes are skipped

**Likely Cause**: P0-1 changes introduced two-stage promotion workflow:
1. Manual promotion: `inbox` → `promoted` status
2. Auto-promotion: `promoted` → `published` status (with directory move)

But tests still expect single-stage auto-promotion directly from `inbox`.

---

### Problem 3: `promote_note()` Return Format (MINOR - Tests May Be Wrong)

**Location**: `promotion_engine.py` lines 139-145

**Current Implementation**:
```python
return {
    "success": True,
    "source": str(source_file),
    "target": result["destination_path"],
    "type": result["note_type"],
    "has_summary": has_summary,
}
```

**But Wait!** Looking at line 127:
```python
if result.get("promoted"):  # This checks NoteLifecycleManager response
    # Build return dict...
```

The issue is that `promote_note()` delegates to `NoteLifecycleManager.promote_note()`, which returns:
```python
{
    "promoted": True,         # NOT "success"!
    "destination_path": str,
    "note_type": str
}
```

So the `if result.get("promoted")` works, but then we transform it. Tests expect `result["success"]` but if the note doesn't get promoted (line 146-147), we return `{"error": ...}` instead of `{"success": False, "error": ...}`.

**Impact**: Tests 1 & 2 fail with `KeyError: 'success'` when promotion fails.

---

## Solution Strategy (GREEN Phase)

### Fix 1: Update `by_type` to nested dict structure

**In `auto_promote_ready_notes()` method**:

```python
# Initialize by_type with nested dicts
"by_type": {
    "fleeting": {"promoted": 0, "skipped": 0},
    "literature": {"promoted": 0, "skipped": 0},
    "permanent": {"promoted": 0, "skipped": 0},
}

# When promoting (line 397):
results["by_type"][note_type]["promoted"] += 1

# When skipping by quality (need to track):
results["by_type"][note_type]["skipped"] += 1
```

### Fix 2: Support both `inbox` and `promoted` status

**Option A** (Minimal - Recommended): Allow both statuses
```python
# Line 335 - change from strict equality to allow list
valid_statuses = ["inbox", self.AUTO_PROMOTION_STATUS]
if status not in valid_statuses:
    logger.debug(f"Skipping {note_path.name}: Status '{status}' not in {valid_statuses}")
    continue
```

**Option B** (Preserve two-stage): Update tests to use `status: promoted`

Recommendation: **Option A** - this maintains backwards compatibility and makes auto-promotion work as tests expect.

### Fix 3: Always return `success` key in `promote_note()`

**In `promote_note()` method** (line 146-147):
```python
else:
    return {
        "success": False,  # ADD THIS KEY!
        "error": result.get("error", "Promotion failed")
    }
```

---

## Expected GREEN Phase Changes

### Files to Modify:

1. **`promotion_engine.py`**:
   - Lines 288-292: Change `by_type` initialization to nested dicts
   - Line 335: Support both `inbox` and `promoted` status  
   - Line 397: Update `by_type[note_type]["promoted"]` increment
   - Line 353-368: Track skipped notes by type in `by_type[note_type]["skipped"]`
   - Line 146: Add `"success": False` to error return

### Estimated Changes:
- **~10 lines modified** in `promotion_engine.py`
- **No changes needed** in `core_workflow_cli.py` (already expects correct format!)
- **No changes needed** in tests (they have correct expectations!)

---

## Success Criteria (GREEN Phase Complete)

✅ All 5 tests passing:
- `test_promote_note_to_permanent` - Returns dict with `success` key
- `test_promote_note_to_literature` - Returns dict with `success` key
- `test_auto_promote_ready_notes_scans_inbox` - Finds 3 candidates (not 0)
- `test_auto_promote_tracks_by_type` - `by_type` is nested dict with `promoted`/`skipped` keys
- `test_auto_promote_moves_notes_end_to_end` - CLI formatting works with nested `by_type`

✅ Zero regressions in full test suite

✅ Return format contract enforced:
```python
# auto_promote_ready_notes() returns:
{
    "total_candidates": int,
    "promoted_count": int,
    "skipped_count": int,
    "error_count": int,
    "by_type": {
        "permanent": {"promoted": int, "skipped": int},
        "literature": {"promoted": int, "skipped": int},
        "fleeting": {"promoted": int, "skipped": int}
    },
    "promoted": List[Dict],
    "skipped_notes": Dict,
    "errors": Dict,
    "dry_run": bool
}

# promote_note() returns:
{
    "success": bool,        # ALWAYS present
    "source": str,          # If success=True
    "target": str,          # If success=True  
    "type": str,            # If success=True
    "error": str            # If success=False
}
```

---

## Time Estimate

- **GREEN Phase**: 30-45 min (minimal fixes to return formats)
- **Verification**: 15 min (run all tests, check for regressions)
- **Total RED + GREEN**: ~1 hour

**Diagnosis took**: 30 minutes  
**Remaining for GREEN**: 30-45 minutes

---

## Key Insight from P0-3

> "Invest time in root cause analysis. One well-understood problem yields many quick fixes."

This diagnosis identified THREE distinct but related issues:
1. Return format structure (nested vs flat dict)
2. Status field requirement change (regression from P0-1)
3. Missing `success` key in error case

All three can be fixed with ~10 lines of code because root causes are clear.

---

**Next Step**: Implement GREEN phase fixes in `promotion_engine.py`
