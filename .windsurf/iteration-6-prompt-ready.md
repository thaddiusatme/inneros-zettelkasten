# TDD Iteration 6: HTTP Monitoring Endpoints

Branch: `feature/daemon-http-monitoring-endpoints` | Workflow: `/complete-feature-development` Phase 4

---

## 🗺️ Architecture Context (Code Map First!)

**Generate code map showing**:
- AutomationDaemon HTTP integration architecture
- Call chains: HTTP request → daemon.get_daemon_health() → handler metrics
- Dependencies on AutomationDaemon, Flask/FastAPI, MetricsTracker

**Trace question**: "What happens when Prometheus scrapes /metrics endpoint?"

---

## 📊 Status

### Completed (Last Iteration)
- ✅ Daemon integration with config-driven handlers (5963925)
- 📝 Key learning: "Daemon as aggregation boundary - handlers export data, daemon combines for monitoring"

### In Progress
- 🎯 HTTP endpoints for health and metrics (not started)
- 📍 `development/src/automation/http_server.py:create_app()` (new file)
- 🚧 Blocker: None

**Batch load context**:
```
Read in parallel:
- development/src/automation/daemon.py (focus: "Existing health/metrics methods")
- development/src/automation/config.py (focus: "HTTP server configuration")
- development/tests/unit/automation/test_daemon.py (focus: "Test patterns for daemon")
```

---

## 🎯 This Session (P0)

**HTTP Monitoring Endpoints**: Enable external monitoring via HTTP

**Steps**:
1. Add HTTPServerConfig to config.py (host, port, enabled)
2. Create http_server.py with Flask app and /health + /metrics routes
3. Integrate HTTP server start/stop with daemon lifecycle

**Acceptance**:
- [ ] GET /health returns JSON with daemon + handler health
- [ ] GET /metrics returns Prometheus text exposition format
- [ ] HTTP server starts/stops with daemon
- [ ] All tests pass: `pytest development/tests/unit/automation/test_http_server.py`

---

## 🔴 RED Phase

**Test to write**: `development/tests/unit/automation/test_http_server.py::test_health_endpoint_returns_daemon_health`

```python
def test_health_endpoint_returns_daemon_health():
    # Given: HTTP server with daemon
    # When: GET /health request
    # Then: JSON response with health data
    assert response.json()['daemon']['is_healthy'] is not None
```

**Expected failure**: ModuleNotFoundError: No module named 'automation.http_server'

---

## 🟢 GREEN Phase

**Implementation**: `development/src/automation/http_server.py:create_app()`
- Strategy: Lightweight Flask app with two routes calling daemon methods
- Minimal viable implementation

---

## 🔵 REFACTOR Phase

**Opportunities**:
- [ ] Extract HTTP response formatting to utility functions
- [ ] Size check: Verify http_server.py remains <200 LOC
- [ ] ADR-001 compliance verification

---

## 🎬 Next Actions

**Immediate**: Begin RED phase - write failing test in `development/tests/unit/automation/test_http_server.py`

**Batch operations after implementation**:
```
Run in parallel:
- pytest development/tests/unit/automation/test_http_server.py
- curl http://localhost:8080/health (manual validation)
- Check: Verify http_server.py size <200 LOC
```

**Create memory after GREEN phase**:
```
Pattern: HTTP endpoints delegate to daemon methods without business logic
Context: Keeps HTTP layer thin, daemon remains testable without HTTP
Location: http_server.py:health_endpoint() and metrics_endpoint()
```

---

## P1 - Next Priority

**Integration with existing automation scripts**: Add daemon start commands to desktop automation

---

Ready to start RED phase? Begin with test implementation in `development/tests/unit/automation/test_http_server.py`.

---

## 🔄 End-of-Session Checklist

After completing this iteration:
- [ ] Run full test suite: `pytest development/tests/unit/automation/`
- [ ] **Run live data test**: `python3 development/demos/http_server_live_test.py`
- [ ] Git commit with descriptive message following template:
  ```
  GREEN: HTTP monitoring endpoints with health and metrics
  
  TDD Iteration 6 - Phase 4 Complete
  
  Changes:
  - http_server.py:create_app(): Flask app with /health and /metrics
  - Added HTTPServerConfig to config.py
  - daemon.py:start(): Integrated HTTP server lifecycle
  
  Tests Added (8 new tests):
  - test_health_endpoint_returns_daemon_health
  - test_metrics_endpoint_returns_prometheus_format
  - test_http_server_starts_with_daemon
  - test_http_server_stops_with_daemon
  
  Test Results:
  ✅ 8/8 HTTP tests passing
  ✅ 94/94 automation tests passing (zero regressions)
  ✅ http_server.py: 156 LOC (ADR-001 compliant: <200 LOC)
  
  Production Ready:
  - /health endpoint operational
  - /metrics endpoint functional
  - Prometheus scraping verified
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
Live Data Test: HTTP Monitoring Endpoints

Validates:
- /health endpoint returns real daemon health
- /metrics endpoint returns Prometheus format
- HTTP server starts/stops cleanly
- Performance with actual requests
"""

def main():
    # Use real paths from user's system
    vault_path = Path(__file__).parent.parent.parent / "knowledge"
    
    # Create minimal test double for file watcher
    class DummyWatcher:
        def register_callback(self, cb): pass
        def is_running(self): return True
    
    # Initialize daemon with HTTP enabled
    config = DaemonConfig(
        http_server=HTTPServerConfig(enabled=True, host='127.0.0.1', port=8080)
    )
    daemon = AutomationDaemon(config=config)
    daemon.file_watcher = DummyWatcher()
    
    # Run 5 core validation tests
    # 1. Server starts successfully
    # 2. GET /health returns 200
    # 3. GET /metrics returns Prometheus format
    # 4. Response times <100ms
    # 5. Server stops cleanly
    
    # Print formatted results
    return 0 if all_passed else 1
```

**Create results document**: `development/demos/LIVE_TEST_RESULTS_HTTP.md`

---

## 📋 Variables Used (Iteration 5 → 6)

### Iteration Context
- **ITERATION_NUMBER**: `6`
- **FEATURE_NAME**: `daemon-http-monitoring-endpoints`
- **CURRENT_PHASE**: `4: Monitoring`
- **BRANCH_NAME**: `feature/daemon-http-monitoring-endpoints`

### What Just Completed (Iteration 5)
- **COMPLETED_TASK**: `Daemon integration with config-driven handlers, health aggregation, Prometheus metrics`
- **COMMIT_HASH**: `5963925`
- **COMMIT_MESSAGE**: `"Add complete TDD Iteration 5 session summary"`
- **KEY_LEARNING**: `"Daemon as aggregation boundary - handlers export data, daemon combines for monitoring"`

### Current Situation
- **IN_PROGRESS_TASK**: `HTTP endpoints for health and metrics (not started)`
- **WORKING_FILE**: `development/src/automation/http_server.py`
- **WORKING_FUNCTION**: `create_app()`
- **CURRENT_LINE**: `N/A (new file)`
- **CURRENT_BLOCKER**: `None`

### Architecture Context
- **SYSTEM_COMPONENT**: `AutomationDaemon HTTP integration`
- **KEY_CLASSES**: `AutomationDaemon, Flask app, HTTPServerConfig`
- **ENTRY_POINT**: `HTTP GET /health or /metrics`
- **PROCESSING_LAYER**: `daemon.get_daemon_health() / daemon.export_prometheus_metrics()`
- **USER_ACTION**: `"Prometheus scrapes /metrics endpoint"`

### Next Tasks (P0)
- **P0_TASK_NAME**: `HTTP Monitoring Endpoints`
- **P0_GOAL**: `Enable external monitoring via HTTP`
- **P0_STEP_1**: `Add HTTPServerConfig to config.py`
- **P0_STEP_2**: `Create http_server.py with Flask routes`
- **P0_STEP_3**: `Integrate HTTP lifecycle with daemon`
- **P0_ACCEPTANCE_1**: `GET /health returns daemon health JSON`
- **P0_ACCEPTANCE_2**: `GET /metrics returns Prometheus format`

### Files to Load
- **FILE_1**: `development/src/automation/daemon.py` - **PURPOSE_1**: `"Existing health/metrics methods"`
- **FILE_2**: `development/src/automation/config.py` - **PURPOSE_2**: `"Configuration patterns"`
- **FILE_3**: `development/tests/unit/automation/test_daemon.py` - **PURPOSE_3**: `"Test patterns"`

### TDD Phases
- **RED_TEST_FILE**: `development/tests/unit/automation/test_http_server.py`
- **RED_TEST_NAME**: `health_endpoint_returns_daemon_health`
- **RED_EXPECTED_FAILURE**: `ModuleNotFoundError: No module named 'automation.http_server'`
- **GREEN_STRATEGY**: `Create Flask app with two routes delegating to daemon methods`
- **REFACTOR_OPPORTUNITY**: `Extract HTTP response formatting to utility functions`

### Next Priority (P1)
- **P1_TASK**: `Integration with existing automation scripts - add daemon start commands`

### Memory to Create
- **MEMORY_PATTERN**: `HTTP endpoints delegate to daemon methods without business logic`
- **MEMORY_CONTEXT**: `Keeps HTTP layer thin, daemon remains testable without HTTP overhead`
- **MEMORY_LOCATION**: `http_server.py:health_endpoint() and metrics_endpoint() lines 25-45`
