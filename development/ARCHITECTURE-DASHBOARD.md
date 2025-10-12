# Interactive Workflow Dashboard - Architecture Overview

**Status**: Production Ready (TDD Iterations 1 & 2 Complete)  
**Last Updated**: 2025-10-11  
**Code Health**: 282/500 LOC (56% capacity, 218 LOC margin)

---

## 🏗️ System Architecture

### Component Hierarchy

```
WorkflowDashboard (Main Orchestrator)
│
├── CLIIntegrator
│   ├── call_cli(cli_name, args)
│   └── Subprocess execution with JSON parsing
│
├── StatusPanelRenderer
│   ├── create_inbox_panel(count, age, indicator)
│   ├── format_inbox_metrics(count, age)
│   └── TestablePanel wrapper for Rich UI
│
├── AsyncCLIExecutor
│   ├── execute_with_progress(cli_name, args)
│   ├── Timeout handling (60s default)
│   └── ProgressDisplayManager integration
│
├── ProgressDisplayManager (REFACTOR Phase)
│   ├── format_operation_message(operation, status)
│   └── Foundation for progress spinners
│
└── ActivityLogger (REFACTOR Phase)
    ├── log_operation(action, result, status)
    ├── get_recent_activities(count)
    └── Foundation for P1.2 Activity Log Panel
```

---

## 📊 File Structure

### Core Files

```
development/src/cli/
├── workflow_dashboard.py (282 LOC)
│   ├── WorkflowDashboard class
│   ├── handle_key_press()
│   ├── render_quick_actions_panel()
│   ├── render_inbox_panel()
│   └── display()
│
└── workflow_dashboard_utils.py (376 LOC)
    ├── TestablePanel (wrapper class)
    ├── CLIIntegrator (subprocess handling)
    ├── StatusPanelRenderer (Rich UI)
    ├── ProgressDisplayManager (REFACTOR)
    ├── ActivityLogger (REFACTOR)
    └── AsyncCLIExecutor (async execution)
```

### Test Files

```
development/tests/unit/
└── test_workflow_dashboard.py (700 LOC)
    ├── TestWorkflowDashboardInboxStatus (9 tests)
    ├── TestCLIIntegrator (Integration tests)
    ├── TestStatusPanelRenderer (UI tests)
    ├── TestWorkflowDashboardKeyboardShortcuts (9 tests)
    └── TestAsyncCLIExecutor (4 tests)
```

---

## 🎯 Feature Map

### Iteration 1: P0.1 Inbox Status Panel ✅

**Features Delivered**:
- Inbox note count display
- Health indicator (🟢 0-20, 🟡 21-50, 🔴 51+)
- Oldest note age calculation
- Real vault integration via `core_workflow_cli.py`
- Rich terminal UI panels

**Test Coverage**: 9/9 tests passing
- `test_fetch_inbox_status_from_cli`
- `test_parse_inbox_count_from_status`
- `test_render_inbox_status_panel`
- `test_cli_error_handling`
- `test_health_indicator_coloring`
- `test_call_core_workflow_status`
- `test_parse_json_output`
- `test_create_inbox_panel`
- `test_panel_contains_metrics`

**Code Impact**:
- Dashboard: 179 LOC
- Utils: 182 LOC
- Total: 361 LOC

---

### Iteration 2: P0.2 Quick Actions Panel + Async Execution ✅

**Features Delivered**:
- 6 keyboard shortcuts: [P]rocess, [W]eekly, [F]leeting, [S]tatus, [B]ackup, [Q]uit
- Quick actions panel with formatted shortcuts
- Async CLI executor with timeout protection
- Enhanced error messages with actionable guidance
- Dict-based command mapping for easy extension

**Test Coverage**: 12/12 new tests passing
- `test_keyboard_shortcut_p_calls_process_inbox`
- `test_keyboard_shortcut_w_calls_weekly_review`
- `test_keyboard_shortcut_f_calls_fleeting_health`
- `test_keyboard_shortcut_s_calls_system_status`
- `test_keyboard_shortcut_b_calls_backup`
- `test_keyboard_shortcut_q_exits_dashboard`
- `test_invalid_key_shows_error_message`
- `test_quick_actions_panel_displays`
- `test_async_cli_executor_shows_progress`
- `test_success_message_after_operation`
- `test_error_message_on_cli_failure`
- `test_timeout_handling_for_long_operations`

**Code Impact**:
- Dashboard: +103 LOC (179 → 282)
- Utils: +194 LOC (182 → 376)
- Total: +297 LOC

**REFACTOR Additions**:
- `ProgressDisplayManager` (23 LOC)
- `ActivityLogger` (60 LOC)
- Enhanced `AsyncCLIExecutor` with progress integration

---

## 🔌 Integration Points

### CLI Tool Integration

```python
# Keyboard shortcuts map to existing CLI tools:
{
    'p': core_workflow_cli.py process-inbox
    'w': weekly_review_cli.py weekly-review
    'f': fleeting_cli.py fleeting-health
    's': core_workflow_cli.py status --format json
    'b': safe_workflow_cli.py backup
    'q': (internal quit handling)
}
```

### Data Flow

```
User Input (Keyboard)
    ↓
handle_key_press()
    ↓
AsyncCLIExecutor.execute_with_progress()
    ↓
subprocess.run(cli_tool, args, timeout=60s)
    ↓
Result Dict {returncode, stdout, stderr, duration, timeout}
    ↓
Success/Error Response to User
```

### Rich UI Rendering

```
fetch_inbox_status()
    ↓
StatusPanelRenderer.create_inbox_panel()
    ↓
TestablePanel(Panel, content_str)
    ↓
Rich Console.print(panel.__rich__())
```

---

## 📈 Performance Metrics

### Test Execution
- **Total Tests**: 21 (100% passing)
- **Execution Time**: 0.030s
- **Target**: <100ms ✅ (3000% faster)

### Code Efficiency
- **Dashboard LOC**: 282/500 (56% capacity)
- **Remaining Budget**: 218 LOC
- **Utility Extraction**: 6 classes in utils
- **Test-to-Code Ratio**: 700/658 = 1.06:1 (excellent coverage)

### Keyboard Response
- **Key press to action**: <100ms estimated
- **CLI timeout**: 60s (configurable)
- **Error handling**: Graceful with actionable messages

---

## 🎨 UI/UX Design Patterns

### Panel Layout (Current - Single Column)

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  📥 Inbox Status                         ┃
┃  Notes: 97 🔴                            ┃
┃  Oldest: 8 months                        ┃
┃  Action: Process inbox                   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  ⚡ Quick Actions:                       ┃
┃                                          ┃
┃  [P] Process    [W] Weekly   [F] Fleeting┃
┃  [S] Status     [B] Backup   [Q] Quit    ┃
┃                                          ┃
┃  Press any key to execute action...      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Health Indicators

```python
# Color-coded health status
0-20 notes   → 🟢 Green  (Healthy)
21-50 notes  → 🟡 Yellow (Attention needed)
51+ notes    → 🔴 Red    (Critical)
```

### Error Messages (Enhanced in REFACTOR)

```python
# Before:
"Invalid key 'x'. Valid keys: b, f, p, q, s, w"

# After:
"Invalid key 'x'. Valid shortcuts: [B, F, P, Q, S, W]. 
 Press [?] for help (planned for P2.3)."
```

---

## 🔮 Planned Enhancements

### Next Iteration: P1.1 Multi-Panel Layout

**Goal**: Transform from single-column to 2x2 grid layout

```
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
┃  📥 Inbox Status     ┃  📝 Fleeting Health ┃
┃  Notes: 97 🔴        ┃  Notes: 25 🟡       ┃
┃  Oldest: 8 months    ┃  Stale: 8 (>30 days)┃
┣━━━━━━━━━━━━━━━━━━━━╋━━━━━━━━━━━━━━━━━━━━┫
┃  📅 Weekly Review    ┃  ⚙️ System Status   ┃
┃  Pending: 12 notes   ┃  Backup: 2h ago     ┃
┃  Ready: 5 promotions ┃  Health: 🟢 Healthy ┃
┗━━━━━━━━━━━━━━━━━━━━┻━━━━━━━━━━━━━━━━━━━━┛
┃  ⚡ Quick Actions: [P] [W] [F] [S] [B] [Q] ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

**Implementation**:
- Rich Layout class for grid positioning
- 4 panel data fetchers (fleeting, weekly, system)
- Color-coded panel borders by health
- ~15 new tests, ~80 minutes estimated

---

### Future Iterations

**P1.2 - Activity Log Panel** (Foundation Ready)
- `ActivityLogger` already implemented
- Track last 10 operations
- Timestamp + status icons
- Scrollable with UP/DOWN arrows (stretch)

**P1.3 - Live Refresh** (Timer Infrastructure Ready)
- 5-second auto-refresh loop
- Pause during CLI operations
- Manual refresh [R] key
- Countdown display

**P2.1 - Detailed View Toggle**
- Press [D] for extended metrics
- Larger terminal support
- Drill-down statistics

**P2.2 - Configuration File**
- `~/.inneros/dashboard.yaml`
- Custom shortcut mapping
- Refresh interval settings
- Color theme customization

**P2.3 - Help Overlay** (Error messages ready)
- Press [?] for help panel
- All shortcuts documented
- Context-sensitive help
- Quick reference guide

---

## 🧪 Testing Strategy

### TDD Discipline

**RED Phase**:
- Write failing tests first
- Document expected behavior
- 100% expected failures

**GREEN Phase**:
- Minimal implementation
- Just enough to pass tests
- No premature optimization

**REFACTOR Phase**:
- Extract utilities
- Enhance error messages
- Maintain 100% test pass rate

### Test Patterns

```python
# Mock-based subprocess testing
@patch('subprocess.run')
def test_keyboard_shortcut_p_calls_process_inbox(self, mock_run):
    mock_run.return_value = Mock(returncode=0, stdout="...", stderr="")
    result = dashboard.handle_key_press('p')
    mock_run.assert_called_once()
    # Verify CLI was called correctly

# TestablePanel for Rich UI testing
panel = dashboard.render_quick_actions_panel()
panel_str = str(panel)  # __str__() for tests
self.assertIn('[P]', panel_str)  # Verify content
```

---

## 📚 Dependencies

### Production Dependencies
```python
rich>=13.0.0  # Terminal UI framework
```

### Development Dependencies
```python
unittest  # Test framework (stdlib)
unittest.mock  # Mocking (stdlib)
subprocess  # CLI execution (stdlib)
```

### Optional Dependencies
```python
# All features work without these, graceful degradation:
- matplotlib (for future chart visualizations)
- networkx (for future connection graphs)
```

---

## 🔐 ADR Compliance

### ADR-001: Code Size Limits ✅

**Requirement**: Main dashboard file <500 LOC

**Current Status**:
- Dashboard: 282 LOC (56% of limit)
- Remaining: 218 LOC margin
- Strategy: Extract utilities early and often

**Utility Classes**:
1. CLIIntegrator
2. StatusPanelRenderer
3. AsyncCLIExecutor
4. ProgressDisplayManager
5. ActivityLogger
6. TestablePanel

### ADR Architectural Patterns ✅

**Single Responsibility**: Each utility class has one clear purpose  
**Integration-First**: Build on existing CLI tools  
**Test-Driven**: 100% TDD methodology  
**Safety-First**: Timeout handling, error messages  

---

## 🎯 Success Metrics

### Achieved
- ✅ 21/21 tests passing (100% success rate)
- ✅ 282/500 LOC (44% budget remaining)
- ✅ 0.030s test execution (<100ms target)
- ✅ 6 keyboard shortcuts implemented
- ✅ Zero regressions maintained
- ✅ Production-ready code quality

### In Progress
- 🔄 Multi-panel layout (P1.1)
- 🔄 Activity log panel (P1.2)
- 🔄 Live refresh (P1.3)

### Planned
- 📋 Help overlay (P2.3)
- 📋 Configuration file (P2.2)
- 📋 Detailed view toggle (P2.1)

---

**Architecture Version**: 2.0  
**Last Validated**: 2025-10-11  
**Maintainer**: TDD Methodology Team
