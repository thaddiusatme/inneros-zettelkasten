# Next Session Prompt: P2-4.1 YAML Wikilink Preservation Fix

Let's continue on branch `main` for P2-4.1 Medium Complexity fix (YAML wikilink preservation). We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

## Updated Execution Plan (P2-4 Medium Complexity - YAML Critical Fix)

**Context**: Systematic automation test improvement achieving 100% pass rate. Currently at **172/177 passing** (97.2%, +5 from Quick Wins). Medium Complexity phase targets individual investigation approaches for remaining 5 failures + 1 ERROR. Each fix requires custom solution.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` (TDD methodology) and `Projects/ACTIVE/P2-4-Medium-Complexity-Test-Fixes.md` (critical path: HIGH priority YAML serialization → MEDIUM priority date mocking).

## Current Status

**Completed**: P2-3.7 Quick Wins → Medium Complexity Transition
- ✅ 172/177 tests passing (97.2%, +5 from Quick Wins phase)
- ✅ Pattern library documented with 3 proven patterns
- ✅ Zero regressions maintained across 7 TDD iterations
- ✅ Quick Wins phase complete (constructor, mock, date patterns applied)
- ✅ Transition manifest created with prioritized 6-task backlog
- 📦 **5 commits ready to push** (P2-3.4 through P2-3.7)

**In progress**: P2-4.1 YAML Wikilink Preservation (RED Phase)
- Test: `test_bidirectional_navigation_works` in `development/tests/unit/automation/test_youtube_handler_note_linking.py:367`
- File: `development/src/automation/feature_handlers.py` (frontmatter update logic)
- Issue: YAML dumper wrapping wikilink syntax `[[link]]` in quotes → `'[[link]]'`

**Lessons from last iteration** (P2-3.6 Date Mocking):
1. **Pattern Reusability**: Proven patterns from Quick Wins enable 15-minute fixes
2. **Mock Path Precision**: Import location matters (`datetime.datetime` not module path)
3. **Batch Success**: 3/3 tests fixed using consistent pattern application
4. **Documentation Value**: Pattern library accelerates future similar fixes
5. **Transition Clarity**: <2 tests sharing pattern = Medium Complexity threshold

## P0 — Critical/Unblocker (YAML Serialization Fix)

**TASK P2-4.1**: Preserve Wikilink Syntax in YAML Frontmatter (HIGH PRIORITY)

**Root Cause Investigation**:
1. Locate YAML dump operation in `YouTubeFeatureHandler.update_frontmatter()`
   - Expected location: `development/src/automation/feature_handlers.py` (lines ~1000-1100)
2. Identify default YAML behavior with strings containing `[[` and `]]`
   - PyYAML default: Quotes special characters for safe parsing
3. Determine why wikilink syntax triggers quote wrapping
   - Brackets are YAML flow sequence indicators → auto-quoting for safety
4. Test current behavior with wikilink strings in YAML dump

**Solution Approach** (Custom YAML Representer):
```python
import yaml
from yaml.representer import SafeRepresenter

def wikilink_str_representer(dumper, data):
    """Custom representer to preserve wikilink syntax without quotes."""
    if '[[' in data and ']]' in data:
        # Use literal style (|) or plain style without quotes
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')
    return dumper.represent_str(data)

# Register before YAML dump
yaml.add_representer(str, wikilink_str_representer, Dumper=yaml.SafeDumper)
```

**Implementation Steps**:
1. **RED Phase**: Run failing test to capture exact YAML output
   ```bash
   pytest development/tests/unit/automation/test_youtube_handler_note_linking.py::TestYouTubeHandlerNoteLinking::test_bidirectional_navigation_works -vv --tb=short
   ```

2. **Investigate**: Locate frontmatter update in `feature_handlers.py`
   ```bash
   grep -n "yaml.dump\|yaml.safe_dump" development/src/automation/feature_handlers.py
   grep -n "def update_frontmatter" development/src/automation/feature_handlers.py
   ```

3. **GREEN Phase**: Implement custom representer
   - Add `wikilink_str_representer()` function
   - Register representer before `yaml.safe_dump()` call
   - Test with various wikilink formats: `[[Note]]`, `[[Note|alias]]`, `[[Note#heading]]`

4. **Verify**: Test passes with preserved wikilink syntax
   ```bash
   pytest development/tests/unit/automation/test_youtube_handler_note_linking.py::TestYouTubeHandlerNoteLinking::test_bidirectional_navigation_works -v
   ```

5. **REFACTOR Phase**: Extract if reusable pattern emerges
   - Consider: `yaml_utils.py` with custom dumper if other tests need it
   - Add inline documentation explaining custom representer necessity
   - Update P2-4 lessons learned with YAML serialization pattern

**Acceptance Criteria**:
- ✅ `test_bidirectional_navigation_works` passing (1/1 target)
- ✅ YAML frontmatter contains `transcript_file: [[youtube-dQw4w9WgXcQ-2025-10-18]]` (no quotes)
- ✅ Zero regressions in 172 passing tests
- ✅ Custom representer handles all wikilink formats tested
- ✅ 173/177 passing (98.3% pass rate)

## P1 — Quick Follow-up Fix (Date Mocking Pattern)

**TASK P2-4.2**: Apply Proven Date Mocking Pattern (MEDIUM PRIORITY)

**Known Pattern** (from P2-3.6):
```python
from unittest.mock import patch, MagicMock
from datetime import datetime

@patch("src.automation.feature_handlers.datetime")
def test_handler_generates_transcript_wikilink(self, mock_datetime):
    # Mock datetime to return fixed date
    mock_dt = MagicMock()
    mock_dt.now.return_value = datetime(2025, 10, 17, 14, 30)
    mock_datetime.datetime = mock_dt
    mock_datetime.side_effect = lambda *args, **kw: datetime(*args, **kw)
    
    # Existing test code...
```

**Implementation**:
- Test: `test_handler_generates_transcript_wikilink` (line 330 in `test_youtube_handler_transcript_integration.py`)
- Expected date: `2025-10-17` (currently getting `2025-10-30`)
- Copy proven pattern from commit `06f2e41` (P2-3.6)
- Adjust date to match test expectation
- Estimated: 15-20 minutes (proven pattern)

**Acceptance Criteria**:
- ✅ 1 additional test passing (174/177, 98.3%)
- ✅ Wikilink filename includes mocked date `2025-10-17`
- ✅ Pattern reusability demonstrated

**TASK P2-4.3**: Logging Assertion Investigation (MEDIUM PRIORITY)
- Test: `test_handle_logs_fallback_extraction`
- Action: Review caplog fixture, verify log level configuration
- Estimated: 40-60 minutes (requires investigation)

## P2 — Remaining Medium Complexity Fixes (FUTURE)

**TASK P2-4.4**: Linking Failure Handling
- Test: `test_handler_handles_linking_failure_gracefully`
- Priority: MEDIUM (error handling path)
- Estimate: 60-90 minutes

**TASK P2-4.5**: Rate Limit Integration Test
- Test: `test_integration_with_youtube_feature_handler`
- Priority: LOW (integration mock setup)
- Estimate: 60-90 minutes

**TASK P2-4.6**: Test Setup ERROR Fix
- Test: `test_handler_handles_transcript_save_failure`
- Priority: LOW (decorator/fixture configuration)
- Estimate: 20-30 minutes

**Goal**: Achieve 177/177 passing (100% automation suite coverage)

## Task Tracker

- [x] P2-3.7: Quick Wins → Medium Complexity transition
- [x] Push 5 local commits (P2-3.4 through P2-3.7)
- [In progress] P2-4.1: YAML wikilink preservation (RED phase)
- [Pending] P2-4.2: Date mocking single test fix
- [Pending] P2-4.3: Logging assertion investigation
- [Pending] P2-4.4: Linking failure handling
- [Pending] P2-4.5: Rate limit integration
- [Pending] P2-4.6: Test setup ERROR fix

## TDD Cycle Plan

**Red Phase** (P2-4.1 - Investigation):
1. Run failing test in isolation with verbose output
2. Examine actual YAML content in assertion error
3. Locate `yaml.safe_dump()` call in `feature_handlers.py`
4. Confirm default behavior: brackets trigger quote wrapping
5. Document exact location and current YAML dump configuration

**Green Phase** (P2-4.1 - Minimal Fix):
1. Create `wikilink_str_representer()` function before YAML dump
2. Register custom representer: `yaml.add_representer(str, wikilink_str_representer)`
3. Test with single wikilink format: `[[youtube-dQw4w9WgXcQ-2025-10-18]]`
4. Verify test passes with preserved syntax (no quotes)

**Refactor Phase** (P2-4.1 - Polish):
1. Test additional wikilink formats: `[[Note|alias]]`, `[[Note#heading]]`
2. Consider extraction to `yaml_utils.py` if pattern repeats
3. Add inline comment explaining custom representer purpose
4. Update P2-4 lessons learned with YAML markdown syntax preservation pattern
5. Document for future markdown-in-YAML scenarios

## Next Action (for this session)

**CRITICAL: Push Local Commits First** (~2 minutes):
```bash
# Push 5 unpushed commits (P2-3.4 through P2-3.7)
git push origin main

# Monitor CI to verify 172/177 automation suite passes
gh run watch
```

**Then Begin P2-4.1 Investigation** (~20 minutes):

1. **Run failing test** to capture exact YAML output:
   ```bash
   cd /Users/thaddius/repos/inneros-zettelkasten
   pytest development/tests/unit/automation/test_youtube_handler_note_linking.py::TestYouTubeHandlerNoteLinking::test_bidirectional_navigation_works -vv --tb=short
   ```

2. **Locate YAML dump logic** in feature handlers:
   ```bash
   # Find YAML dump operations
   grep -n "yaml.dump\|yaml.safe_dump" development/src/automation/feature_handlers.py
   
   # Find frontmatter update method
   grep -n -A 5 "def update_frontmatter" development/src/automation/feature_handlers.py
   
   # View the method
   sed -n '1000,1100p' development/src/automation/feature_handlers.py  # Adjust line numbers
   ```

3. **Create custom representer** in `feature_handlers.py`:
   ```python
   # Add before YouTubeFeatureHandler class or in update_frontmatter method
   def wikilink_str_representer(dumper, data):
       """Preserve wikilink [[...]] syntax without YAML quotes."""
       if isinstance(data, str) and '[[' in data and ']]' in data:
           return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')
       return dumper.represent_str(data)
   
   # Register before yaml.safe_dump() call
   yaml.add_representer(str, wikilink_str_representer, Dumper=yaml.SafeDumper)
   yaml.safe_dump(frontmatter_dict, f, default_flow_style=False, allow_unicode=True)
   ```

4. **Verify fix** and check for regressions:
   ```bash
   # Test single test passes
   pytest development/tests/unit/automation/test_youtube_handler_note_linking.py::TestYouTubeHandlerNoteLinking::test_bidirectional_navigation_works -v
   
   # Run full automation suite for regressions
   pytest development/tests/unit/automation/ -v --tb=no -q | tail -3
   ```

Would you like me to **push the 5 local commits** and then **begin P2-4.1 YAML investigation** with the custom representer approach?

---

## Reference Documentation

**Pattern Library**: `Projects/ACTIVE/P2-3-Quick-Wins-Lessons-Learned.md`
- Constructor completeness pattern (P2-3.4)
- Mock interface completeness pattern (P2-3.5)
- Date mocking pattern (P2-3.6) ← **Apply for P2-4.2**

**Medium Complexity Manifest**: `Projects/ACTIVE/P2-4-Medium-Complexity-Test-Fixes.md`
- Complete prioritized backlog (6 tasks)
- Root cause hypotheses for each failure
- 3-phase execution strategy (HIGH → MEDIUM → LOW)

**TDD Methodology**: `.windsurf/rules/updated-development-workflow.md`
- RED → GREEN → REFACTOR → COMMIT cycle
- Lessons learned documentation requirements
- Zero regression validation

**CI Failure Report**: `Projects/ACTIVE/ci-failure-report-2025-10-29.md`
- Complete session history (2025-10-29 through 2025-10-30)
- P2-3.3 session (6 tests fixed, path fixtures)
- Quick Wins phase summary (97.2% pass rate)
- Success patterns and anti-patterns

**Related P2 Documentation**:
- `Projects/ACTIVE/p2-3-3-youtube-handler-lessons-learned.md` (12K)
- `Projects/ACTIVE/p2-3-4-youtube-note-linking-lessons-learned.md` (6.9K)
- `Projects/ACTIVE/p2-3-5-metrics-health-tests-lessons-learned.md` (5.8K)

---

## Quick Commands Reference

```bash
# Check current test status
pytest development/tests/unit/automation/ -v --tb=no -q | tail -3

# Run P2-4.1 target test
pytest development/tests/unit/automation/test_youtube_handler_note_linking.py::TestYouTubeHandlerNoteLinking::test_bidirectional_navigation_works -vv

# Find YAML operations
grep -n "yaml\." development/src/automation/feature_handlers.py

# Push commits and monitor CI
git push origin main && gh run watch

# Check git status
git log origin/main..HEAD --oneline  # Show unpushed commits
git status --short  # Check working directory
```

---

**Expected Outcome**: P2-4.1 complete (173/177 passing, 97.7%) with custom YAML representer pattern documented for future markdown syntax preservation needs. Zero regressions maintained.
