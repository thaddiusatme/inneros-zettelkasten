# Next TDD Iteration Prompt Generator

> **Purpose**: Fill this out at END of current iteration → Copy output for NEXT chat  
> **Updated**: 2025-10-07  
> **Status**: Active template

---

## 📋 Instructions

1. **At end of current iteration**, fill in the variables below
2. **Copy the generated prompt** from "OUTPUT" section
3. **Start new chat** and paste as first message
4. **Archive this** with iteration number for reference

---

## 🔧 Template Variables (Fill These Out)

### Iteration Context
- **ITERATION_NUMBER**: `[e.g., 3]`
- **FEATURE_NAME**: `[e.g., smart-link-automation]`
- **CURRENT_PHASE**: `[1: Engine | 2: CLI | 3: Automation | 4: Monitoring]`
- **BRANCH_NAME**: `[e.g., feature/smart-link-automation]`

### What Just Completed
- **COMPLETED_TASK**: `[e.g., FileWatcher integration with EventHandler]`
- **COMMIT_HASH**: `[e.g., a1b2c3d]`
- **COMMIT_MESSAGE**: `[e.g., "GREEN: FileWatcher debouncing with tests passing"]`
- **KEY_LEARNING**: `[e.g., "Dual-layer debouncing prevents AI API spam during file edits"]`

### Current Situation
- **IN_PROGRESS_TASK**: `[e.g., Feature handler registration and callback system]`
- **WORKING_FILE**: `[e.g., development/src/automation/daemon.py]`
- **WORKING_FUNCTION**: `[e.g., _setup_feature_handlers]`
- **CURRENT_LINE**: `[e.g., 260]`
- **CURRENT_BLOCKER**: `[e.g., None | "Need to validate handler callback signatures"]`

### Architecture Context (For Code Map)
- **SYSTEM_COMPONENT**: `[e.g., AutomationDaemon and feature handler integration]`
- **KEY_CLASSES**: `[e.g., AutomationDaemon, ScreenshotEventHandler, SmartLinkEventHandler]`
- **ENTRY_POINT**: `[e.g., daemon.start()]`
- **PROCESSING_LAYER**: `[e.g., feature_handlers.process()]`
- **USER_ACTION**: `[e.g., "a new screenshot is added to OneDrive"]`

### Next Tasks (P0)
- **P0_TASK_NAME**: `[e.g., Complete feature handler registration system]`
- **P0_GOAL**: `[e.g., Enable conditional handler initialization via config]`
- **P0_STEP_1**: `[e.g., Parse screenshot_handler and smart_link_handler config sections]`
- **P0_STEP_2**: `[e.g., Initialize handlers only if enabled=true]`
- **P0_STEP_3**: `[e.g., Register handlers with FileWatcher callbacks]`
- **P0_ACCEPTANCE_1**: `[e.g., Handlers initialize only when configured]`
- **P0_ACCEPTANCE_2**: `[e.g., Tests validate conditional initialization]`

### Files to Load
- **FILE_1**: `[path]` - **PURPOSE_1**: `[e.g., "Main daemon lifecycle"]`
- **FILE_2**: `[path]` - **PURPOSE_2**: `[e.g., "Handler implementations"]`
- **FILE_3**: `[path]` - **PURPOSE_3**: `[e.g., "Test patterns"]`

### TDD Phases
- **RED_TEST_FILE**: `[e.g., development/tests/unit/test_automation_daemon.py]`
- **RED_TEST_NAME**: `[e.g., test_feature_handlers_initialize_from_config]`
- **RED_EXPECTED_FAILURE**: `[e.g., AttributeError: 'DaemonConfig' has no attribute 'screenshot_handler']`
- **GREEN_STRATEGY**: `[e.g., Add ScreenshotHandlerConfig and SmartLinkHandlerConfig to config.py]`
- **REFACTOR_OPPORTUNITY**: `[e.g., Extract handler initialization logic to utility method]`

### Next Priority (P1)
- **P1_TASK**: `[e.g., Add health checks for feature handlers]`

### Memory to Create
- **MEMORY_PATTERN**: `[e.g., "Feature handlers use conditional initialization pattern via config"]`
- **MEMORY_CONTEXT**: `[e.g., "Allows daemon to run with only needed handlers, reduces resource usage"]`
- **MEMORY_LOCATION**: `[e.g., daemon.py:_setup_feature_handlers() lines 260-286]`

---

## 📤 OUTPUT: Generated Prompt for Next Chat

**Copy everything below this line for your next chat:**

---

# TDD Iteration {ITERATION_NUMBER}: {FEATURE_NAME}

Branch: `{BRANCH_NAME}` | Workflow: `/complete-feature-development` Phase {CURRENT_PHASE}

---

## 🗺️ Architecture Context (Code Map First!)

**Generate code map showing**:
- {SYSTEM_COMPONENT} architecture and integration points
- Call chains: {ENTRY_POINT} → {PROCESSING_LAYER}
- Dependencies on {KEY_CLASSES}

**Trace question**: "What happens when {USER_ACTION}?"

---

## 📊 Status

### Completed (Last Iteration)
- ✅ {COMPLETED_TASK} ({COMMIT_HASH})
- 📝 Key learning: {KEY_LEARNING}

### In Progress
- 🎯 {IN_PROGRESS_TASK}
- 📍 `{WORKING_FILE}:{WORKING_FUNCTION}` (line {CURRENT_LINE})
- 🚧 Blocker: {CURRENT_BLOCKER}

**Batch load context**:
```
Read in parallel:
- {FILE_1} (focus: {PURPOSE_1})
- {FILE_2} (focus: {PURPOSE_2})
- {FILE_3} (focus: {PURPOSE_3})
```

---

## 🎯 This Session (P0)

**{P0_TASK_NAME}**: {P0_GOAL}

**Steps**:
1. {P0_STEP_1}
2. {P0_STEP_2}
3. {P0_STEP_3}

**Acceptance**:
- [ ] {P0_ACCEPTANCE_1}
- [ ] {P0_ACCEPTANCE_2}
- [ ] All tests pass: `pytest {RED_TEST_FILE}`

---

## 🔴 RED Phase

**Test to write**: `{RED_TEST_FILE}::test_{RED_TEST_NAME}`

```python
def test_{RED_TEST_NAME}():
    # Given: [Daemon with handler config]
    # When: [daemon.start() called]
    # Then: [Handlers initialized conditionally]
    assert [expected_behavior]
```

**Expected failure**: {RED_EXPECTED_FAILURE}

---

## 🟢 GREEN Phase

**Implementation**: `{WORKING_FILE}:{WORKING_FUNCTION}`
- Strategy: {GREEN_STRATEGY}
- Minimal viable implementation

---

## 🔵 REFACTOR Phase

**Opportunities**:
- [ ] {REFACTOR_OPPORTUNITY}
- [ ] Size check: Verify classes remain <500 LOC
- [ ] ADR-001 compliance verification

---

## 🎬 Next Actions

**Immediate**: Begin RED phase - write failing test in `{RED_TEST_FILE}:{RED_TEST_NAME}`

**Batch operations after implementation**:
```
Run in parallel:
- pytest {RED_TEST_FILE}
- mypy {WORKING_FILE}
- Check: Verify class sizes <500 LOC
```

**Create memory after GREEN phase**:
```
Pattern: {MEMORY_PATTERN}
Context: {MEMORY_CONTEXT}
Location: {MEMORY_LOCATION}
```

---

## P1 - Next Priority

**{P1_TASK}**: [Brief description for future iteration]

---

Ready to start RED phase? Begin with test implementation in `{RED_TEST_FILE}`.

---

## 🔄 End-of-Session Checklist

After completing this iteration:
- [ ] Run full test suite: `pytest development/tests/unit/automation/`
- [ ] **Run live data test**: `python3 development/demos/{FEATURE}_live_test.py`
- [ ] Git commit with descriptive message following template:
  ```
  GREEN: [Feature] with [Key Achievement]
  
  TDD Iteration N - Phase M Complete
  
  Changes:
  - [Component].[method](): [Purpose]
  - Added [functionality]
  - Extracted [helper] to reduce duplication
  
  Tests Added ([N] new tests):
  - test_[behavior_1]
  - test_[behavior_2]
  
  Test Results:
  ✅ [N]/[N] tests passing
  ✅ [N]/[N] automation tests passing (zero regressions)
  ✅ [Component]: [LOC] LOC (ADR-001 compliant: <500 LOC)
  
  Production Ready:
  - [Feature 1] operational
  - [Feature 2] functional
  - [Feature 3] verified
  ```
- [ ] Update lessons-learned document with new patterns
- [ ] Create memory for key architectural decisions
- [ ] Fill out this prompt.md template for next iteration

---

## 💾 Live Data Testing Pattern

After GREEN phase, validate with real data:

```python
#!/usr/bin/env python3
"""
Live Data Test: {FEATURE_NAME}

Validates:
- Config-driven initialization
- Integration with real vault/paths
- Health/metrics endpoints
- Performance with actual data
"""

def main():
    # Use real paths from user's system
    vault_path = Path(__file__).parent.parent.parent / "knowledge"
    
    # Create minimal test double for dependencies
    class DummyDependency:
        def required_method(self):
            return expected_value
    
    # Initialize system under test
    system = YourSystem(config=real_config)
    system.dependency = DummyDependency()
    
    # Run 5 core validation tests
    # 1. Initialization test
    # 2. Health check test  
    # 3. Metrics export test
    # 4. Integration test
    # 5. Config consistency test
    
    # Print formatted results
    return 0 if all_passed else 1
```

**Create results document**: `development/demos/LIVE_TEST_RESULTS.md`

---

