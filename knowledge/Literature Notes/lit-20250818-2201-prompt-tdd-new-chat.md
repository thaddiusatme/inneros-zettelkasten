---
created: 2025-08-18 22:00
type: literature
status: inbox
visibility: private
tags:
  - acceptance-criteria
  - agile
  - blocker-priority
  - continuous-integration
  - critical-path
  - development-cycle
  - git-commit
source:
author:
ai_processed: 2025-08-31T12:58:24.543500
---
# TDD Iteration [N]: [FEATURE_NAME]
Branch: `feature/[FEATURE_NAME]` | Workflow: `/complete-feature-development` Phase [1/2/3/4]

---

## 🗺️ Architecture Context (Code Map First!)

**Generate code map showing**:
- [SYSTEM_COMPONENT] current architecture and integration points
- Call chains: [ENTRY_POINT] → [PROCESSING] → [OUTPUT]
- Dependencies on [KEY_CLASSES]

**Trace question**: "What happens when [USER_ACTION]?"

---

## 📊 Status

### Completed (Last Iteration)
- ✅ [TASK_1] ([COMMIT_HASH])
- 📝 Key learning: [INSIGHT]

### In Progress
- 🎯 [CURRENT_TASK]
- 📍 `[FILE]:[FUNCTION]` (line [N])
- 🚧 Blocker: [ISSUE]

**Batch load context**:
```
Read in parallel:
- [FILE_1] (focus: [PURPOSE])
- [FILE_2] (focus: [PURPOSE])
- [TEST_FILE] (existing test patterns)
```

---

## 🎯 This Session (P0)

**[TASK_NAME]**: [SPECIFIC_GOAL]

**Steps**:
1. [ACTION_1] in `[FILE_1]`
2. [ACTION_2] in `[FILE_2]`
3. Verify: `pytest [PATH]`

**Acceptance**:
- [ ] [OUTCOME_1]
- [ ] [OUTCOME_2]
- [ ] All tests pass

---

## 🔴 RED Phase
```python
# Test: [TEST_FILE]::test_[BEHAVIOR]
def test_[BEHAVIOR]():
    # Given: [SETUP]
    # When: [ACTION]
    # Then: [ASSERTION]
```
**Expected failure**: [ERROR_TYPE]

## 🟢 GREEN Phase
**Implementation**: `[SOURCE_FILE]:[FUNCTION]`
- Strategy: [MINIMAL_APPROACH]

## 🔵 REFACTOR Phase
- [ ] Extract [UTILITY] → `[UTILS_FILE]`
- [ ] Size check: [CLASS] <500 LOC
- [ ] ADR-001 compliance

---

## 🎬 Next Actions

**Immediate**: [SPECIFIC_TASK] in `[FILE]:[LINE]`

**Batch operations**:
```
Run in parallel:
- pytest [TEST_PATH]
- mypy [SOURCE_PATH]
- Check: [CLASS] size
```

**Create memory after**:
- Pattern: [KEY_DISCOVERY]
- Decision: [ARCHITECTURAL_CHOICE]

---

Ready to start RED phase?