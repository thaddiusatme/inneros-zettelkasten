---
type: session-prompt
created: 2025-10-29
task: P1-2.1
branch: ci-test-fixes-phase-1-blockers
priority: P1-High
---

# Next Session Prompt: CI Test Fixes - Template Fixtures Creation (P1-2.1)

Continue work on branch `ci-test-fixes-phase-1-blockers`. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

## Updated Execution Plan (CI Test Fixes Phase 1)

**CI Run**: https://github.com/thaddiusatme/inneros-zettelkasten/actions/runs/18915166798  
**Current Error Count**: ~291 errors, ~226 failures (down from 361/296 after P0-1.2)

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` (critical path: Template fixture infrastructure for 65+ FileNotFoundError failures).

## Current Status

### Completed
- ✅ **P0-1.1**: monitoring.metrics_collector investigation (CI config issue, downgraded to P1)
- ✅ **P0-1.2**: LlamaVisionOCR import fix (commit `38f623b`)
  - Added `llama_vision_ocr` to `src/ai/__init__.py` exports
  - Fixed import path in `src/cli/screenshot_utils.py:151`
  - Created 4 diagnostic import tests (100% passing)
  - **Impact**: 70+ tests unblocked, 19% error reduction (361 → 291 errors)

### In Progress
**P1-2.1**: Template Fixtures Creation in `development/tests/fixtures/templates/`

### Lessons from Last Iteration (P0-1.2)
- **Module existence ≠ availability**: Without `__all__` export, CI can't find modules
- **TDD diagnostic power**: 5-minute investigation → 20-minute complete solution
- **Minimal fixes maximize impact**: 2-line changes unblocked 70+ tests
- **Root cause first**: Understanding the WHY prevented band-aid fixes

---

## Template Fixtures Analysis

### Current State Discovery

**Existing Infrastructure**:
- ✅ Fixtures directory exists: `development/tests/fixtures/`
- ✅ Contains `test_data/`, `vault_factory.py`, `__init__.py`
- ❌ No `templates/` subdirectory (needs creation)

**Available Templates** (in `knowledge/Templates/`):
1. `youtube-video.md` (4,329 bytes) ← **Primary blocker (65+ failures)**
2. `daily.md` (1,008 bytes)
3. `weekly-review.md` (1,279 bytes)
4. `fleeting.md` (1,545 bytes)
5. `literature.md` (2,331 bytes)
6. `permanent.md` (1,495 bytes)
7. `content-idea.md` (2,250 bytes)
8. `content-idea-raw.md` (2,612 bytes)
9. `chatgpt-prompt.md` (2,576 bytes)
10. `simple-youtube-trigger.md` (196 bytes)
11. `sprint-retro.md` (743 bytes)
12. `sprint-review.md` (918 bytes)
13. `permanent Note Morning Check In Template.md` (1,375 bytes)

**Test Files Affected** (grep analysis):
- `test_templates_auto_inbox.py` - Expects templates in `TEMPLATES_DIR`
- `test_image_integrity_monitor.py` - References `Templates/test_template.md`
- `test_workflow_manager.py` - Tests template placeholder processing
- `test_youtube_note_enhancer.py` - Uses templater patterns
- `test_note_processing_coordinator.py` - Template frontmatter fixes
- Manual test: `test_templater_youtube_hook.md` - Documents `knowledge/Templates/youtube-video.md` expectation

---

## P0 — Critical Blockers (All Complete ✅)

**Status**: P0 phase complete (both tasks). Moving to P1 systematic fixes.

---

## P1 — Systematic Test Infrastructure (High Priority)

### P1-2.1: Create Template Fixtures Directory (CURRENT TASK)

**Impact**: Blocks 65+ FileNotFoundError failures  
**Root Cause**: Tests reference `knowledge/Templates/youtube-video.md` which was removed from public repo

**Implementation Details**:

1. **Create Directory Structure**:
   ```bash
   mkdir -p development/tests/fixtures/templates/
   ```

2. **Copy Template Files**:
   ```bash
   # Copy all templates from knowledge/Templates/ to fixtures
   cp knowledge/Templates/*.md development/tests/fixtures/templates/
   ```

3. **Create Template Discovery Module**:
   - File: `development/tests/fixtures/template_loader.py`
   - Function: `get_template_path(template_name: str) -> Path`
   - Purpose: Centralized template location logic for tests

4. **Update Test Imports**:
   - Replace: `knowledge/Templates/youtube-video.md`
   - With: `fixtures.template_loader.get_template_path("youtube-video.md")`
   - Files to update:
     - `test_templates_auto_inbox.py` (line 16: `TEMPLATES_DIR.glob("*.md")`)
     - `test_image_integrity_monitor.py` (line 200: template path construction)
     - Any other files discovered during grep search

5. **Add Fixture Validation**:
   - Verify templates have valid YAML frontmatter
   - Check for required template variables
   - Ensure auto-move directives present (if applicable)

### P1-2.2: Fix metrics_collector CI PYTHONPATH

**Impact**: 17+ ImportErrors  
**Root Cause**: CI environment can't find `monitoring.metrics_collector` (module exists locally)

**Implementation**:
- Update `.github/workflows/*.yml` to set `PYTHONPATH=development`
- Or: Adjust test imports to use relative paths
- Reference: `test_ci_import_compatibility.py` (all 12 tests pass locally)

### P1-2.3: Module Import Standardization

**Impact**: 50+ ModuleNotFoundErrors  
**Strategy**: Apply lessons from P0-1.2 to other missing module exports

**Acceptance Criteria**:
- ✅ `development/tests/fixtures/templates/` directory created with all 13 templates
- ✅ Template loader utility created and tested
- ✅ 65+ FileNotFoundError failures reduced to 0
- ✅ Tests can locate templates via centralized fixture path
- ✅ Template validation tests passing (RED → GREEN)
- ✅ Error count reduced by 20%+ (~291 → ~230 errors)
- ✅ Zero breaking changes to template content or behavior

---

## P2 — Test Logic Fixes (Future Sessions)

### P2-3.1: Fix AttributeError Failures
**Count**: ~50 failures  
**Examples**: Missing methods in implementation classes

### P2-3.2: Fix AssertionError Failures
**Count**: ~80 failures  
**Examples**: Sorting issues, data structure mismatches, validation failures

### P2-3.3: API Compatibility Fixes
**Count**: 5+ failures  
**Example**: YouTube transcript API version mismatch

---

## Task Tracker

- [x] P0-1.1 - monitoring.metrics_collector investigation
- [x] P0-1.2 - LlamaVisionOCR import fix (commit `38f623b`)
- [ ] **P1-2.1 - Template fixtures creation** ← **CURRENT SESSION**
- [ ] P1-2.2 - metrics_collector PYTHONPATH fix
- [ ] P1-2.3 - Module import standardization
- [ ] P2-3.1 - AttributeError fixes
- [ ] P2-3.2 - AssertionError fixes
- [ ] P2-3.3 - YouTube API compatibility

---

## TDD Cycle Plan

### Red Phase

**Create Failing Test**: `development/tests/unit/test_template_fixtures_infrastructure.py`

```python
"""
RED PHASE: Template Fixtures Infrastructure Tests

Validates that all required templates are available in fixtures directory
and can be discovered by tests. Should fail initially because fixtures/templates/
directory doesn't exist yet.
"""

def test_fixtures_templates_directory_exists():
    """RED: fixtures/templates/ directory should exist"""
    # Should fail - directory doesn't exist yet
    
def test_all_required_templates_present():
    """RED: All 13 templates should be copied to fixtures"""
    required_templates = [
        "youtube-video.md",
        "daily.md",
        "weekly-review.md",
        "fleeting.md",
        "literature.md",
        "permanent.md",
        # ... 7 more templates
    ]
    # Should fail - templates not copied yet
    
def test_template_loader_utility_exists():
    """RED: template_loader.py module should exist with get_template_path()"""
    # Should fail - utility doesn't exist yet
    
def test_templates_have_valid_yaml_frontmatter():
    """RED: Each template should have valid YAML frontmatter"""
    # Should fail - can't read templates that don't exist in fixtures
```

**Run Tests**: Expect 4/4 failures with clear error messages

### Green Phase

**Minimal Implementation**:

1. Create directory:
   ```bash
   mkdir -p development/tests/fixtures/templates/
   ```

2. Copy templates:
   ```bash
   cp knowledge/Templates/*.md development/tests/fixtures/templates/
   ```

3. Create `development/tests/fixtures/template_loader.py`:
   ```python
   from pathlib import Path
   
   FIXTURES_DIR = Path(__file__).parent
   TEMPLATES_DIR = FIXTURES_DIR / "templates"
   
   def get_template_path(template_name: str) -> Path:
       """Get absolute path to template fixture"""
       template_path = TEMPLATES_DIR / template_name
       if not template_path.exists():
           raise FileNotFoundError(f"Template not found: {template_name}")
       return template_path
   ```

4. Run tests again: Expect 4/4 passing

5. Update affected test files (one at a time):
   - Start with `test_templates_auto_inbox.py`
   - Replace hardcoded paths with `template_loader.get_template_path()`
   - Verify FileNotFoundErrors decrease

### Refactor Phase

**Cleanup Opportunities**:

1. **Extract Template Validation Utility**:
   - Create `validate_template_yaml()` helper function
   - Add to `template_loader.py` for reuse
   - Document expected template structure

2. **Add Template Discovery Helper**:
   - Function: `list_available_templates() -> List[str]`
   - Returns all template names in fixtures
   - Useful for parametrized tests

3. **Create Template Fixture Class** (if needed):
   - Class: `TemplateFixture`
   - Methods: `load()`, `get_content()`, `get_frontmatter()`
   - Purpose: Encapsulate template loading logic

4. **Document Template Standards**:
   - Add `fixtures/templates/README.md`
   - Document required YAML fields
   - Explain fixture usage patterns

5. **Verify Test Coverage**:
   - Run full test suite
   - Confirm FileNotFoundError count drops from 65+ to 0
   - Check for any remaining template-related failures

---

## Next Action (for this session)

### Immediate Steps (in order):

1. **Start TDD RED Phase** (5 minutes):
   ```bash
   # Create failing test
   touch development/tests/unit/test_template_fixtures_infrastructure.py
   # Write 4 failing tests as outlined above
   # Run: PYTHONPATH=development python3 -m pytest development/tests/unit/test_template_fixtures_infrastructure.py -v
   # Verify: 4/4 failures with clear messages
   ```

2. **Begin GREEN Phase** (10 minutes):
   ```bash
   # Create directory structure
   mkdir -p development/tests/fixtures/templates/
   
   # Copy all templates
   cp knowledge/Templates/*.md development/tests/fixtures/templates/
   
   # Create loader utility
   touch development/tests/fixtures/template_loader.py
   # Implement get_template_path() function
   ```

3. **Verify GREEN Phase** (5 minutes):
   ```bash
   # Run tests again
   PYTHONPATH=development python3 -m pytest development/tests/unit/test_template_fixtures_infrastructure.py -v
   # Verify: 4/4 passing
   ```

4. **Update First Affected Test** (10 minutes):
   ```bash
   # Start with test_templates_auto_inbox.py
   # Replace TEMPLATES_DIR reference with template_loader.TEMPLATES_DIR
   # Run test to verify it passes
   ```

5. **Systematic Migration** (30-60 minutes):
   - Identify all tests using `knowledge/Templates/`
   - Update imports one file at a time
   - Verify each file's tests pass after update
   - Track FileNotFoundError count reduction

### Reference Files

- **CI Report**: `Projects/ACTIVE/ci-failure-report-2025-10-29.md`
- **Previous Success**: `Projects/ACTIVE/llama-vision-ocr-import-fix-lessons-learned.md`
- **Template Source**: `knowledge/Templates/` (13 template files)
- **Test Patterns**: `development/tests/unit/test_llama_vision_ocr_import_fix.py`

---

## Success Metrics (End of Session)

**Target Error Reduction**: ~291 → ~230 errors (21% reduction)

**Measurable Outcomes**:
- ✅ 4/4 fixture infrastructure tests passing
- ✅ 13/13 templates copied to fixtures
- ✅ Template loader utility created and tested
- ✅ FileNotFoundError count: 65+ → 0
- ✅ At least 3 test files updated to use fixtures
- ✅ Zero breaking changes to existing passing tests
- ✅ CI error count verifiably reduced by 20%+

**Commit Message Template**:
```
feat(P1-2.1): Create centralized template fixtures for test suite

ROOT CAUSE: Tests referenced knowledge/Templates/ which was removed from
public repo, causing 65+ FileNotFoundError failures

SOLUTION:
- Created development/tests/fixtures/templates/ directory
- Copied 13 template files from knowledge/Templates/ to fixtures
- Created template_loader.py utility for centralized template discovery
- Updated [N] test files to use fixture templates

IMPACT:
- ✅ FileNotFoundError reduced: 65 → 0 (100% resolution)
- ✅ Error count reduced: ~291 → ~230 (21% decrease)
- ✅ Template infrastructure centralized and maintainable
- ✅ 4/4 infrastructure tests passing

FILES CHANGED:
- Created: development/tests/fixtures/templates/ (13 template files)
- Created: development/tests/fixtures/template_loader.py
- Created: development/tests/unit/test_template_fixtures_infrastructure.py
- Updated: [list test files modified]

Duration: [XX] minutes via systematic TDD approach
Related: P1-2.1, ci-test-fixes-phase-1-blockers branch
```

---

## Would You Like Me To

Begin with RED phase by creating `test_template_fixtures_infrastructure.py` with 4 failing tests that clearly demonstrate the template fixture requirements?
