# Example: Filled Prompt Template

> **Purpose**: Shows how to fill out prompt.md at end of iteration  
> **Based on**: Your current automation daemon work  
> **Iteration**: Example from Phase 3 completion

---

## 🔧 Template Variables (Example Fill)

### Iteration Context
- **ITERATION_NUMBER**: `4`
- **FEATURE_NAME**: `automation-daemon-integration`
- **CURRENT_PHASE**: `3: Automation`
- **BRANCH_NAME**: `feature/automation-daemon-integration`

### What Just Completed
- **COMPLETED_TASK**: `FileWatcher integration with dual-layer debouncing`
- **COMMIT_HASH**: `7f3a2b9`
- **COMMIT_MESSAGE**: `GREEN: FileWatcher event processing with AutomationEventHandler integration`
- **KEY_LEARNING**: `Dual-layer debouncing (FileWatcher + EventHandler) prevents duplicate AI processing during rapid file edits`

### Current Situation
- **IN_PROGRESS_TASK**: `Feature handler registration and conditional initialization`
- **WORKING_FILE**: `development/src/automation/daemon.py`
- **WORKING_FUNCTION**: `_setup_feature_handlers`
- **CURRENT_LINE**: `260`
- **CURRENT_BLOCKER**: `None - ready to implement`

### Architecture Context (For Code Map)
- **SYSTEM_COMPONENT**: `AutomationDaemon feature handler integration`
- **KEY_CLASSES**: `AutomationDaemon, ScreenshotEventHandler, SmartLinkEventHandler, FileWatcher`
- **ENTRY_POINT**: `daemon.start()`
- **PROCESSING_LAYER**: `feature_handlers.process()`
- **USER_ACTION**: `a new screenshot is detected in OneDrive`

### Next Tasks (P0)
- **P0_TASK_NAME**: `Complete feature handler registration system`
- **P0_GOAL**: `Enable conditional handler initialization via YAML configuration`
- **P0_STEP_1**: `Add ScreenshotHandlerConfig and SmartLinkHandlerConfig dataclasses to config.py`
- **P0_STEP_2**: `Parse handler config sections in ConfigurationLoader`
- **P0_STEP_3**: `Implement conditional initialization in daemon._setup_feature_handlers()`
- **P0_ACCEPTANCE_1**: `Screenshot handler initializes only when config.screenshot_handler.enabled=true`
- **P0_ACCEPTANCE_2**: `Tests validate handlers skip initialization when disabled`

### Files to Load
- **FILE_1**: `development/src/automation/daemon.py` - **PURPOSE_1**: `Main daemon lifecycle and handler setup`
- **FILE_2**: `development/src/automation/feature_handlers.py` - **PURPOSE_2**: `Handler implementations and interfaces`
- **FILE_3**: `development/tests/unit/test_automation_daemon.py` - **PURPOSE_3**: `Existing test patterns for daemon initialization`

### TDD Phases
- **RED_TEST_FILE**: `development/tests/unit/test_automation_daemon.py`
- **RED_TEST_NAME**: `feature_handlers_initialize_from_config`
- **RED_EXPECTED_FAILURE**: `AttributeError: 'DaemonConfig' has no attribute 'screenshot_handler'`
- **GREEN_STRATEGY**: `Add handler config dataclasses, parse in ConfigurationLoader, conditionally initialize in daemon`
- **REFACTOR_OPPORTUNITY**: `Extract handler initialization to separate utility methods for cleaner separation`

### Next Priority (P1)
- **P1_TASK**: `Add health checks for feature handlers (get_health() and get_metrics())`

### Memory to Create
- **MEMORY_PATTERN**: `Feature handlers use conditional initialization via config with enabled=true/false flags`
- **MEMORY_CONTEXT**: `Allows daemon to run with only needed handlers, reduces resource usage and startup time`
- **MEMORY_LOCATION**: `daemon.py:_setup_feature_handlers() lines 260-286`

---

## 📤 OUTPUT: What You'd Copy to Next Chat

---

# TDD Iteration 4: automation-daemon-integration

Branch: `feature/automation-daemon-integration` | Workflow: `/complete-feature-development` Phase 3

---

## 🗺️ Architecture Context (Code Map First!)

**Generate code map showing**:
- AutomationDaemon feature handler integration architecture and integration points
- Call chains: daemon.start() → feature_handlers.process()
- Dependencies on AutomationDaemon, ScreenshotEventHandler, SmartLinkEventHandler, FileWatcher

**Trace question**: "What happens when a new screenshot is detected in OneDrive?"

---

## 📊 Status

### Completed (Last Iteration)
- ✅ FileWatcher integration with dual-layer debouncing (7f3a2b9)
- 📝 Key learning: Dual-layer debouncing (FileWatcher + EventHandler) prevents duplicate AI processing during rapid file edits

### In Progress
- 🎯 Feature handler registration and conditional initialization
- 📍 `development/src/automation/daemon.py:_setup_feature_handlers` (line 260)
- 🚧 Blocker: None - ready to implement

**Batch load context**:
```
Read in parallel:
- development/src/automation/daemon.py (focus: Main daemon lifecycle and handler setup)
- development/src/automation/feature_handlers.py (focus: Handler implementations and interfaces)
- development/tests/unit/test_automation_daemon.py (focus: Existing test patterns for daemon initialization)
```

---

## 🎯 This Session (P0)

**Complete feature handler registration system**: Enable conditional handler initialization via YAML configuration

**Steps**:
1. Add ScreenshotHandlerConfig and SmartLinkHandlerConfig dataclasses to config.py
2. Parse handler config sections in ConfigurationLoader
3. Implement conditional initialization in daemon._setup_feature_handlers()

**Acceptance**:
- [ ] Screenshot handler initializes only when config.screenshot_handler.enabled=true
- [ ] Tests validate handlers skip initialization when disabled
- [ ] All tests pass: `pytest development/tests/unit/test_automation_daemon.py`

---

## 🔴 RED Phase

**Test to write**: `development/tests/unit/test_automation_daemon.py::test_feature_handlers_initialize_from_config`

```python
def test_feature_handlers_initialize_from_config():
    # Given: [Daemon with handler config]
    # When: [daemon.start() called]
    # Then: [Handlers initialized conditionally]
    assert [expected_behavior]
```

**Expected failure**: AttributeError: 'DaemonConfig' has no attribute 'screenshot_handler'

---

## 🟢 GREEN Phase

**Implementation**: `development/src/automation/daemon.py:_setup_feature_handlers`
- Strategy: Add handler config dataclasses, parse in ConfigurationLoader, conditionally initialize in daemon
- Minimal viable implementation

---

## 🔵 REFACTOR Phase

**Opportunities**:
- [ ] Extract handler initialization to separate utility methods for cleaner separation
- [ ] Size check: Verify classes remain <500 LOC
- [ ] ADR-001 compliance verification

---

## 🎬 Next Actions

**Immediate**: Begin RED phase - write failing test in `development/tests/unit/test_automation_daemon.py:feature_handlers_initialize_from_config`

**Batch operations after implementation**:
```
Run in parallel:
- pytest development/tests/unit/test_automation_daemon.py
- mypy development/src/automation/daemon.py
- Check: Verify class sizes <500 LOC
```

**Create memory after GREEN phase**:
```
Pattern: Feature handlers use conditional initialization via config with enabled=true/false flags
Context: Allows daemon to run with only needed handlers, reduces resource usage and startup time
Location: daemon.py:_setup_feature_handlers() lines 260-286
```

---

## P1 - Next Priority

**Add health checks for feature handlers (get_health() and get_metrics())**: [Brief description for future iteration]

---

Ready to start RED phase? Begin with test implementation in `development/tests/unit/test_automation_daemon.py`.

---

## 🔄 End-of-Session Checklist

After completing this iteration:
- [ ] Run full test suite: `pytest development/tests/`
- [ ] Git commit with descriptive message
- [ ] Update this prompt.md for next iteration
- [ ] Create memory if pattern discovered
- [ ] Document in lessons-learned if Phase complete

---
