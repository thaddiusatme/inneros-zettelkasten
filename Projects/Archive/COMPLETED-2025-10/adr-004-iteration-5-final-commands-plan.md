# ADR-004 Iteration 5: Final 3 Commands - Implementation Plan

**Date**: 2025-10-11  
**Status**: 🔄 IN PROGRESS - RED Phase  
**Target**: 100% CLI Extraction Complete

---

## Commands to Extract (3 total)

### 1. `--start-safe-session` → Extend safe_workflow_cli.py
**Utility**: `safe_workflow_cli_utils.py` (line 371 - already implemented!)  
**Estimated**: 15 minutes (just expose existing utility)  
**Approach**: Add new command handler to existing SafeWorkflowCLI class

### 2. `--prune-backups` → Create backup_cli.py
**Utility**: `DirectoryOrganizer.prune_backups()` (already implemented!)  
**Estimated**: 20 minutes (simple wrapping)  
**Approach**: New CLI wrapping DirectoryOrganizer backup management

### 3. `--interactive` → Create interactive_cli.py
**Function**: `interactive_mode()` in workflow_demo.py (lines 549-643)  
**Estimated**: 25 minutes (more complex, needs refactoring)  
**Approach**: Extract and clean up interactive loop logic

---

## TDD Phases

### RED Phase (15-20 minutes)
- [ ] Create test_safe_workflow_cli.py additions (start-safe-session tests)
- [ ] Create test_backup_cli.py (prune-backups tests)
- [ ] Create test_interactive_cli.py (interactive mode tests)
- [ ] All tests fail with expected errors

### GREEN Phase (30-40 minutes)
- [ ] Extend safe_workflow_cli.py with start-safe-session handler
- [ ] Create backup_cli.py wrapping DirectoryOrganizer
- [ ] Create interactive_cli.py extracting interactive_mode()
- [ ] All tests passing (minimal implementation)

### REFACTOR Phase (10-15 minutes)
- [ ] Clean up error handling
- [ ] Add proper logging
- [ ] Validate with real vault
- [ ] All tests still passing

### COMMIT & DOCS (30 minutes)
- [ ] Git commit all 3 CLIs
- [ ] Create lessons learned document
- [ ] Update ADR-004 to 100% COMPLETE status
- [ ] Celebrate! 🎉

---

## File Checklist

### New Files
- [ ] `development/src/cli/backup_cli.py` (~150 LOC)
- [ ] `development/src/cli/interactive_cli.py` (~200 LOC)
- [ ] `development/tests/unit/test_backup_cli.py` (3-4 tests)
- [ ] `development/tests/unit/test_interactive_cli.py` (3-4 tests)

### Modified Files
- [ ] `development/src/cli/safe_workflow_cli.py` (+30 LOC)
- [ ] `development/tests/unit/test_safe_workflow_cli.py` (+2 tests)

### Documentation
- [ ] `Projects/ACTIVE/adr-004-iteration-5-final-lessons-learned.md`
- [ ] `Projects/ACTIVE/adr-004-cli-layer-extraction.md` (update to 100%)

---

## Success Criteria

✅ **All 25 commands extracted** (22/25 → 25/25)  
✅ **All tests passing** (100% success rate)  
✅ **ADR-004 marked COMPLETE**  
✅ **Velocity metrics documented**  
✅ **Celebrate 100% CLI extraction!** 🎉

---

## Next Action

Starting RED phase - writing failing tests for all 3 commands...
