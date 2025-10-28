---
type: project-manifest
created: 2025-01-08
updated: 2025-01-08
status: active
priority: P1
tags: [metadata-repair, inbox-validation, workflow-automation, tdd, adr-002]
---

# Inbox Metadata Repair System - Project Manifest

**Last Updated**: 2025-01-08  
**Status**: 📋 **PLANNED** - Ready for TDD implementation  
**Priority**: P1 - **ENABLES COMPLETE AUTO-PROMOTION WORKFLOW**  
**Timeline**: 3-4 hours (follows proven TDD patterns)  
**Depends On**: Auto-promotion system (PBI-002 complete ✅)

---

## 🎯 Problem Statement

### Current Pain Point
**8 notes in Inbox cannot be auto-promoted** due to missing `type:` frontmatter field:
- `voice-note-prompts-for-knowledge-capture.md`
- `Study link between price risk and trust in decision-making.md`
- `sprint 2 8020.md`
- `newsletter-generator-prompt.md`
- `zettelkasten-voice-prompts-v1.md`
- `Progress-8-26.md`
- `enhanced-connections-live-data-analysis-report.md`
- `voice-prompts-quick-reference-card.md`

**Impact**:
- Auto-promotion errors on 8 notes (21% of Inbox)
- Manual frontmatter editing required
- Notes with high quality (0.85) cannot progress through workflow
- Recurring issue from bulk imports without validation

### Root Cause Analysis (RCA)

**Primary Cause**: Bulk import on Oct 12, 2024 without validation
```bash
# All 8 error notes created at same timestamp
Oct 12 21:24 - zettelkasten-voice-prompts-v1.md
Oct 12 21:24 - voice-prompts-quick-reference-card.md
Oct 12 21:24 - sprint 2 8020.md
Oct 12 21:24 - newsletter-generator-prompt.md
Oct 12 21:24 - enhanced-connections-live-data-analysis-report.md
Oct 12 21:24 - Study link between...md
Oct 12 21:24 - Progress-8-26.md
```

**Contributing Factors**:
1. No naming convention enforcement (working notes use `prefix-YYYYMMDD-HHMM-title.md`)
2. No import validation pipeline
3. No automated template application on import
4. No quality gates before Inbox placement

**Prevention Strategy**: Automated Template System (Option B)

---

## 🏗️ Solution: Automated Template System

### Architecture Pattern (ADR-002 Compliance)

Following established extraction patterns from:
- `NoteLifecycleManager` (ADR-002, Oct 14, 2025) ✅
- `PromotionEngine` (PBI-002, Jan 8, 2025) ✅
- Single responsibility principle
- Composition over inheritance
- Dependency injection enabled

### Component: MetadataRepairEngine

**Responsibility**: Detect and repair missing frontmatter fields in Inbox notes

**Location**: `development/src/ai/metadata_repair_engine.py`

**Key Methods**:
```python
class MetadataRepairEngine:
    """
    Detects and repairs missing frontmatter in Inbox notes.
    
    ADR-002 Pattern: Single responsibility, dependency injection, testable.
    """
    
    def __init__(self, inbox_dir: str, dry_run: bool = True):
        """Initialize with Inbox directory and mode."""
        
    def scan_inbox_for_missing_metadata(self) -> List[Dict]:
        """Identify notes missing required frontmatter fields."""
        
    def infer_note_type(self, note_path: Path, content: str) -> str:
        """Infer type from filename patterns and content."""
        
    def repair_note_metadata(self, note_path: Path, inferred_type: str) -> Dict:
        """Add missing frontmatter while preserving existing fields."""
        
    def repair_batch(self, notes: List[Path], preview: bool = True) -> Dict:
        """Batch repair with progress tracking and validation."""
```

**Integration Points**:
- `WorkflowManager.metadata_repair_engine` (delegation only)
- `CoreWorkflowCLI` (--repair-metadata command)
- `PromotionEngine` (pre-promotion validation)

---

## 📋 Implementation Plan

### PBI-001: Detection System (RED Phase) - 45 min

**Objective**: Build comprehensive detection for missing frontmatter

**Test Suite** (8-10 failing tests):
```python
# development/tests/unit/test_metadata_repair_engine.py

class TestMetadataDetection:
    def test_detects_missing_type_field()
    def test_detects_missing_created_field()
    def test_ignores_notes_with_complete_frontmatter()
    def test_handles_notes_without_frontmatter_block()
    def test_reports_multiple_missing_fields()

class TestTypeInference:
    def test_infers_literature_from_lit_prefix()
    def test_infers_fleeting_from_fleeting_prefix()
    def test_infers_fleeting_from_capture_prefix()
    def test_defaults_to_fleeting_for_unknown_patterns()
    def test_content_based_inference_for_ambiguous_names()
```

**Expected Results**: All 8-10 tests fail (no implementation exists)

**Deliverables**:
- Complete test suite in `test_metadata_repair_engine.py`
- Test fixtures for 8 actual error notes
- Clear documentation of inference rules

---

### PBI-002: Repair Engine (GREEN Phase) - 60 min

**Objective**: Implement minimal logic to pass all tests

**Core Implementation**:

```python
# Pattern detection rules
FILENAME_PATTERNS = {
    r'^lit-\d{8}-\d{4}': 'literature',
    r'^fleeting-\d{8}-\d{4}': 'fleeting',
    r'^capture-\d{8}-\d{4}': 'fleeting',
    r'^prompt-\d{8}-\d{4}': 'fleeting',
}

# Content-based inference (fallback)
CONTENT_KEYWORDS = {
    'literature': ['source:', 'author:', 'citation:', 'reference:'],
    'permanent': ['concept:', 'principle:', 'framework:', 'synthesis:'],
}

# Default: fleeting (safest assumption)
DEFAULT_TYPE = 'fleeting'
```

**Safety Features**:
1. **Backup before modification**: Use existing backup system
2. **Preserve existing fields**: Only add missing fields, never overwrite
3. **Validation**: Check frontmatter syntax after repair
4. **Dry-run mode**: Preview changes before applying
5. **Atomic operations**: All-or-nothing for batch repairs

**Expected Results**: All 10 tests passing

**Deliverables**:
- `metadata_repair_engine.py` (250-300 lines)
- Pattern matching implementation
- Content analysis utilities
- Backup integration

---

### PBI-003: WorkflowManager Integration (REFACTOR Phase) - 30 min

**Objective**: Add delegation method following ADR-002 patterns

**Implementation**:

```python
# development/src/ai/workflow_manager.py

class WorkflowManager:
    def __init__(self, base_directory: str):
        # ... existing initialization ...
        
        # ADR-002 Phase 12: Metadata Repair Engine
        self.metadata_repair_engine = MetadataRepairEngine(
            inbox_dir=self.inbox_dir,
            dry_run=True  # Safe by default
        )
    
    def repair_inbox_metadata(self, dry_run: bool = True) -> Dict:
        """
        Repair missing frontmatter in Inbox notes.
        
        ADR-002 Phase 12: Delegates to MetadataRepairEngine.
        Follows established delegation pattern.
        
        Args:
            dry_run: If True, preview repairs without making changes
            
        Returns:
            Dict: Repair results with counts and details
        """
        return self.metadata_repair_engine.repair_batch(
            notes=self._scan_inbox_notes(),
            preview=dry_run
        )
```

**Test Coverage** (3 new tests):
- `test_workflow_manager_has_repair_method()`
- `test_repair_delegates_to_metadata_engine()`
- `test_repair_passes_dry_run_parameter()`

**Expected Results**: 13/13 tests passing (10 engine + 3 delegation)

---

### PBI-004: CLI Integration - 30 min

**Objective**: Add user-friendly command for metadata repair

**CLI Command**:

```python
# development/src/cli/core_workflow_cli.py

@click.command()
@click.option('--dry-run', is_flag=True, default=True,
              help='Preview repairs without making changes')
@click.option('--execute', is_flag=True, default=False,
              help='Execute repairs (disables dry-run)')
def repair_metadata(dry_run: bool, execute: bool):
    """
    Repair missing frontmatter in Inbox notes.
    
    Detects notes missing required fields (type, created) and adds them
    based on filename patterns and content analysis.
    
    Examples:
        # Preview repairs
        python core_workflow_cli.py knowledge repair-metadata
        
        # Execute repairs
        python core_workflow_cli.py knowledge repair-metadata --execute
    """
    results = cli.workflow_manager.repair_inbox_metadata(
        dry_run=(not execute)
    )
    
    # Format output...
```

**Output Format**:

```
🔧 Repairing Inbox metadata...
   Mode: DRY-RUN (preview only)

NOTES NEEDING REPAIR
--------------------
   📄 voice-note-prompts-for-knowledge-capture.md
      Missing: type
      Inferred: fleeting (from filename pattern)
      
   📄 Study link between price risk and trust in decision-making.md
      Missing: type, created
      Inferred: fleeting (default), created: 2024-10-12 21:24

SUMMARY
-------
   ✅ Would repair: 8 notes
   ⚠️  Manual review: 0 notes
   🚨 Errors: 0 notes

Run with --execute to apply repairs.
```

---

### PBI-005: Real Data Validation - 20 min

**Objective**: Test on actual 8 error notes and validate auto-promotion

**Validation Steps**:

1. **Dry-run preview**:
   ```bash
   python3 development/src/cli/core_workflow_cli.py knowledge repair-metadata
   ```

2. **Execute repairs**:
   ```bash
   python3 development/src/cli/core_workflow_cli.py knowledge repair-metadata --execute
   ```

3. **Verify repairs**:
   - Check all 8 notes have `type:` field
   - Validate frontmatter syntax correct
   - Confirm existing fields preserved

4. **Run auto-promotion**:
   ```bash
   python3 development/src/cli/core_workflow_cli.py knowledge auto-promote --quality-threshold 0.7
   ```

5. **Expected results**:
   - **0 errors** (down from 8)
   - **5+ additional notes promoted** (high-quality notes that were blocked)
   - **Clean Inbox workflow**

---

## 🎯 Success Criteria

### Functional Requirements
- ✅ Detects 8/8 notes missing `type:` field
- ✅ Infers correct type from filename patterns
- ✅ Preserves all existing frontmatter fields
- ✅ Creates backup before modifications
- ✅ Supports dry-run preview mode
- ✅ Integrates with auto-promotion workflow

### Quality Requirements
- ✅ 13+ tests passing (10 engine + 3 delegation)
- ✅ Zero regressions on existing tests
- ✅ ADR-002 compliance verified
- ✅ <300 LOC for MetadataRepairEngine
- ✅ <5 methods per class

### User Impact
- ✅ 8 blocked notes can now be promoted
- ✅ Auto-promotion runs with 0 errors
- ✅ No manual frontmatter editing required
- ✅ Future bulk imports will be validated

---

## 📊 Time Estimates

| Phase | Duration | Cumulative |
|-------|----------|------------|
| PBI-001: Detection Tests (RED) | 45 min | 45 min |
| PBI-002: Repair Engine (GREEN) | 60 min | 1h 45m |
| PBI-003: Integration (REFACTOR) | 30 min | 2h 15m |
| PBI-004: CLI Integration | 30 min | 2h 45m |
| PBI-005: Real Data Validation | 20 min | 3h 05m |
| **Buffer** | 25 min | **3h 30m** |

**Total**: 3-4 hours (follows proven TDD patterns)

---

## 🏗️ Architecture Integration

### Follows ADR-002 Patterns ✅

**Pattern**: Single Responsibility Extraction
- `NoteLifecycleManager`: Status management (Oct 14, 2025) ✅
- `PromotionEngine`: Quality-gated promotion (Jan 8, 2025) ✅
- `MetadataRepairEngine`: Frontmatter repair (This project) 📋

**Delegation Chain**:
```
CoreWorkflowCLI
  ↓
WorkflowManager.repair_inbox_metadata()
  ↓
MetadataRepairEngine.repair_batch()
  ↓
BackupSystem (existing)
```

**No Business Logic in WorkflowManager**: Simple passthrough delegation

---

## 🚀 Future Enhancements (Optional)

### Phase 2: Import Validation Pipeline (3 hours)
**Prevent recurrence** of bulk import issues:

```python
class InboxIntakeValidator:
    """Validates notes before accepting into Inbox."""
    
    def validate_import(self, file_path: Path) -> ValidationResult:
        """Check required frontmatter, naming convention, syntax."""
        
    def auto_repair_on_import(self, file_path: Path):
        """Apply templates automatically during import."""
        
    def quarantine_invalid_notes(self, notes: List[Path]):
        """Move invalid notes to quarantine directory."""
```

**Integration Points**:
- Desktop automation scripts
- Manual import workflows
- Git pre-commit hooks

**Timeline**: Post-repair system, if recurring issues detected

---

## 📁 Deliverables

### Code Files
- [ ] `development/src/ai/metadata_repair_engine.py` (250-300 lines)
- [ ] `development/tests/unit/test_metadata_repair_engine.py` (300-350 lines)
- [ ] Updated `development/src/ai/workflow_manager.py` (+15 lines)
- [ ] Updated `development/src/cli/core_workflow_cli.py` (+40 lines)

### Documentation
- [ ] This manifest
- [ ] Lessons learned document (after completion)
- [ ] Updated CLI reference with `repair-metadata` command
- [ ] ADR-002 Phase 12 documentation

### Test Results
- [ ] 13/13 tests passing (10 engine + 3 delegation)
- [ ] Zero regressions on 89 existing promotion tests
- [ ] 8/8 real notes successfully repaired
- [ ] Auto-promotion runs with 0 errors

---

## 🎓 Key Learnings (To Document)

### What Worked
- RCA identified bulk import as root cause
- TDD approach prevents over-engineering
- ADR-002 patterns accelerate development
- Pattern matching + content analysis provides robust inference

### What to Watch
- Edge cases: Notes with unusual naming conventions
- Performance: Batch processing 100+ notes
- Validation: Ensuring frontmatter syntax remains valid
- User feedback: Are inferred types accurate?

### Future Improvements
- Import validation pipeline (Phase 2)
- Pre-commit hooks for frontmatter validation
- Automated template system for all note creation
- Note dataclass to prevent KeyError bugs (separate project)

---

## 📋 Dependencies & Prerequisites

### Required (Already Complete) ✅
- Auto-promotion system (PBI-002, Jan 8, 2025)
- WorkflowManager delegation patterns (ADR-002)
- Backup system (existing)
- TDD infrastructure (Oct 2025)

### Optional (Nice to Have)
- CI/CD pipeline (for automated testing)
- Pre-commit hooks (for validation)

---

## 🚦 Go/No-Go Decision Criteria

**Proceed if**:
- ✅ Auto-promotion working (PBI-002 complete)
- ✅ 8 notes confirmed as blocking workflow
- ✅ TDD infrastructure ready
- ✅ 3-4 hours available for focused work

**Defer if**:
- ❌ Higher priority bugs discovered
- ❌ Auto-promotion system unstable
- ❌ Major architecture changes in progress

**Current Status**: ✅ **GO** - All prerequisites met

---

## 📊 Metrics & Monitoring

### Before Repair
- Inbox notes with errors: **8 (21%)**
- Auto-promotion error rate: **21%**
- Notes blocked from promotion: **8**
- Manual intervention required: **Yes**

### After Repair (Target)
- Inbox notes with errors: **0 (0%)**
- Auto-promotion error rate: **0%**
- Notes blocked from promotion: **0**
- Manual intervention required: **No**

### Long-term Monitoring
- Track import sources causing missing metadata
- Monitor false positive/negative rates for type inference
- Measure time saved vs manual frontmatter editing

---

## ✅ Definition of Done

- [ ] All 13 tests passing (100% success rate)
- [ ] Zero regressions on existing tests
- [ ] 8/8 real notes successfully repaired
- [ ] Auto-promotion runs with 0 errors
- [ ] CLI command documented
- [ ] Lessons learned documented
- [ ] Code reviewed for ADR-002 compliance
- [ ] Branch merged to main
- [ ] User can run workflow end-to-end without manual intervention

---

**Ready to Start**: Yes ✅  
**Estimated Completion**: 3-4 hours  
**Next Step**: Begin PBI-001 (RED Phase) - Create failing tests
