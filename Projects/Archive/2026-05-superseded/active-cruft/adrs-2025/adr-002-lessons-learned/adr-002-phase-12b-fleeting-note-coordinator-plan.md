# ADR-002 Phase 12b: Fleeting Note Coordinator - Extraction Plan

**Date**: 2025-10-15 09:16 PDT  
**Branch**: `feat/adr-002-phase-12b-validation-coordinator` → renamed to `feat/adr-002-phase-12b-fleeting-note-coordinator`  
**Status**: 🔴 **PLANNING** - Extraction analysis complete

## 🎯 Extraction Target

### WorkflowManager Current State
- **Current LOC**: 2349 (after Phase 12a)
- **Target**: <500 LOC
- **Remaining**: ~1849 LOC to extract

### Identified Extraction Candidates

**Fleeting Note Management Methods** (~250-300 LOC):

1. **`generate_fleeting_triage_report()`** (~92 lines, 1695-1787)
   - Quality assessment and triage recommendations
   - Processing time tracking
   - Quality distribution analysis
   - Recommendation generation with rationale

2. **`_find_fleeting_notes()`** (~24 lines, 1789-1813)
   - Scans Fleeting Notes and Inbox directories
   - Filters by metadata type
   - Error handling for unparseable files

3. **`promote_fleeting_note()`** (~130+ lines, 1815-onwards)
   - Single note promotion to permanent/literature
   - Preview mode support
   - DirectoryOrganizer integration
   - Backup creation
   - Metadata updates

4. **`promote_fleeting_notes_batch()`** (~100+ lines, estimated)
   - Batch promotion based on quality threshold
   - Progress reporting
   - Aggregate statistics

**Total Extraction**: ~250-300 LOC (conservative estimate)

## 📋 Extraction Strategy

### New Coordinator: `FleetingNoteCoordinator`

**Responsibilities**:
- Fleeting note discovery and scanning
- Quality assessment and triage
- Single and batch promotion workflows
- Preview mode operations
- Progress reporting and statistics

**Dependencies**:
- `DirectoryOrganizer` (for safe file operations)
- `process_inbox_note()` callback (for quality assessment)
- Directory paths (inbox_dir, fleeting_dir, permanent_dir, literature_dir)
- Configuration (quality thresholds)

### Delegation Pattern
WorkflowManager will:
1. Create FleetingNoteCoordinator during initialization
2. Delegate fleeting note methods to coordinator
3. Expose methods for backwards compatibility
4. Pass callback for `process_inbox_note()`

## 🧪 Test Plan (RED Phase)

### Test Categories (~18-20 tests)

**1. FleetingNoteCoordinator Initialization** (3 tests):
- Initialize with required dependencies
- Validate directory paths
- Verify callback registration

**2. Fleeting Note Discovery** (4 tests):
- Find notes in Fleeting Notes directory
- Find notes in Inbox with fleeting type
- Handle missing directories
- Handle unparseable files

**3. Triage Report Generation** (5 tests):
- Generate triage with quality distribution
- Filter by quality threshold
- Handle empty directory
- Calculate processing time
- Sort recommendations by quality score

**4. Single Note Promotion** (4 tests):
- Promote to permanent with backup
- Promote to literature with metadata updates
- Preview mode (no actual changes)
- Handle invalid note paths

**5. Batch Promotion** (3 tests):
- Promote batch based on quality threshold
- Track promotion statistics
- Preview mode for batch operations

**6. Integration with WorkflowManager** (2 tests):
- Coordinator provides all fleeting note methods
- Backwards compatibility maintained

## 📊 Expected Results

### LOC Impact
- **Extracted**: ~250-300 LOC
- **Delegation Overhead**: ~35-40 LOC (15% of extraction)
- **Net Reduction**: ~210-260 LOC
- **Final WorkflowManager**: ~2090-2140 LOC
- **Progress**: 79-80% toward realistic completion

### Test Coverage
- **New Tests**: 18-20 comprehensive tests
- **Expected Pass Rate**: 100%
- **Regressions**: 0 (maintain all existing functionality)

### Development Timeline
- **RED Phase**: ~15 minutes (18-20 tests)
- **GREEN Phase**: ~35 minutes (coordinator implementation)
- **Verification**: ~5 minutes (71 existing + 18-20 new = ~90 tests)
- **REFACTOR**: SKIP (following 12-phase pattern)
- **Commit**: ~10 minutes
- **Documentation**: ~10 minutes
- **Total**: ~75 minutes

## 🎯 Success Criteria

1. ✅ **18-20 comprehensive tests created** (RED phase)
2. ✅ **All tests passing** (GREEN phase)
3. ✅ **Zero regressions** (all existing tests still pass)
4. ✅ **~210-260 LOC net reduction**
5. ✅ **Backwards compatibility maintained**
6. ✅ **Git commit with comprehensive documentation**
7. ✅ **Lessons learned document created**

## 🚀 Next Steps

1. Create comprehensive RED phase tests for FleetingNoteCoordinator
2. Implement minimal GREEN phase coordinator
3. Integrate with WorkflowManager via delegation
4. Verify zero regressions (run all tests)
5. Skip REFACTOR (13th consecutive skip expected)
6. Create git commit with detailed documentation
7. Document lessons learned

---

**Ready to proceed with RED Phase test creation!**
