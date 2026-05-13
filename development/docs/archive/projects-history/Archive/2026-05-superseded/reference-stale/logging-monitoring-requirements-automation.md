# Logging & Monitoring Requirements - Automation Components

**Status**: 📋 BACKLOG - Definition of Done  
**Priority**: HIGH (Production Requirement)  
**Created**: 2025-10-07  
**Context**: Identified during TDD Iteration 2 P1.2 production validation

---

## 🎯 Problem Statement

Current automation components (EventHandler, Daemon) lack proper logging infrastructure. Errors are tracked in memory metrics but not persisted to log files, making production debugging impossible.

**Risk**: When daemon runs 24/7, errors occur silently with no audit trail for investigation.

---

## ✅ Definition of Done - Logging Requirements

### **For ALL Automation Components**

Every component in `development/src/automation/` MUST implement:

#### **1. Python Logging Setup**
```python
import logging
from pathlib import Path

class AutomationComponent:
    def __init__(self, ...):
        # Setup logging
        log_dir = Path(__file__).parent.parent.parent.parent / '.automation' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'{self.__class__.__name__.lower()}_{time.strftime("%Y-%m-%d")}.log'
        
        self.logger = logging.getLogger(__name__)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
```

#### **2. Mandatory Log Points**

**Initialization:**
```python
self.logger.info(f"Initialized with config: {config}")
```

**Success Operations:**
```python
self.logger.info(f"Processed {file_path} in {duration:.2f}s")
```

**Errors (CRITICAL):**
```python
except Exception as e:
    self.logger.error(
        f"Failed to process {file_path}: {type(e).__name__}: {str(e)}",
        exc_info=True  # Include full stack trace
    )
```

**State Changes:**
```python
self.logger.info(f"State changed: {old_state} → {new_state}")
```

**Health Issues:**
```python
self.logger.warning(f"Queue depth high: {queue_depth} items")
```

#### **3. Log File Standards**

**Location**: `.automation/logs/`

**Naming**: `{component_name}_{YYYY-MM-DD}.log`
- Example: `event_handler_2025-10-07.log`
- Example: `daemon_2025-10-07.log`
- Example: `file_watcher_2025-10-07.log`

**Rotation**: Daily log files (automatically by date in filename)

**Retention**: Clean up logs older than 7 days (via health monitor)

**Format**:
```
2025-10-07 17:30:45 [INFO] automation.event_handler: Initialized with vault: /path/to/vault
2025-10-07 17:30:47 [INFO] automation.event_handler: Processed note.md in 0.23s
2025-10-07 17:30:50 [ERROR] automation.event_handler: Failed to process bad.md: ValueError: Invalid YAML
Traceback (most recent call last):
  File "event_handler.py", line 145, in _execute_processing
    result = self.core_workflow.process_inbox_note(str(file_path))
ValueError: Invalid YAML frontmatter
```

#### **4. Integration with Health Monitoring**

Health monitor (`health_monitor.sh`) should check:
```bash
check_automation_logs() {
    # Check for error patterns in last 24 hours
    local error_count=$(grep -c "\[ERROR\]" "$LOG_DIR"/event_handler_*.log 2>/dev/null || echo "0")
    
    if [[ $error_count -gt 10 ]]; then
        send_alert "High error rate" "Event handler logged $error_count errors in 24h"
        return 1
    fi
}
```

---

## 📋 Components Requiring Logging

### **Phase 1 - Critical (Before Production)**
- [x] `event_handler.py` - ⚠️ **MISSING LOGGING** (identified 2025-10-07)
- [ ] `daemon.py` - Needs comprehensive logging
- [ ] `file_watcher.py` - Needs event logging

### **Phase 2 - Important**
- [ ] `scheduler.py` - Job execution logging
- [ ] `health.py` - Health check result logging
- [ ] `config.py` - Configuration loading logging

---

## 🔧 Implementation Checklist

For each component:

- [ ] Add `import logging` statement
- [ ] Initialize logger in `__init__`
- [ ] Create daily log file in `.automation/logs/`
- [ ] Log initialization with configuration details
- [ ] Log all success operations (INFO level)
- [ ] Log all errors with full stack traces (ERROR level)
- [ ] Log state changes (INFO level)
- [ ] Log performance metrics (DEBUG level)
- [ ] Add tests verifying logging behavior
- [ ] Update component documentation with logging info

---

## 🎯 Acceptance Criteria

**A component is NOT production-ready unless:**

1. ✅ All errors are logged to files (not just counted in metrics)
2. ✅ Log files exist in `.automation/logs/`
3. ✅ Log format matches standard (timestamp, level, component, message)
4. ✅ Stack traces included for exceptions
5. ✅ Log retention configured (7 days via health monitor)
6. ✅ Tests verify logging behavior
7. ✅ Documentation updated

---

## 📊 Benefits

**Debugging:**
- Know exactly what failed, when, and why
- Full stack traces for error investigation
- Audit trail for all operations

**Monitoring:**
- Health monitor can detect error patterns
- Alert on high error rates
- Track system behavior over time

**Compliance:**
- Production systems require audit logs
- Troubleshooting customer issues
- Performance analysis

---

## 🔗 Related Files

- `.automation/logs/` - Log file directory
- `.automation/scripts/health_monitor.sh` - Health monitoring script
- `.windsurf/rules/automation-monitoring-requirements.md` - Phase 3 & 4 requirements
- `Projects/ACTIVE/automation-event-handler-tdd-iteration-2-p1.2-lessons-learned.md` - Where gap was identified

---

## 💡 Example: Before/After

### **Before (Current - BAD):**
```python
except Exception as e:
    self._processing_stats['failed_events'] += 1
    return {'success': False, 'error': str(e)}
    # ❌ Error lost forever after metrics reset
```

### **After (Required - GOOD):**
```python
except Exception as e:
    self._processing_stats['failed_events'] += 1
    
    # ✅ Permanent record for debugging
    self.logger.error(
        f"Failed to process {file_path}: {type(e).__name__}: {str(e)}",
        exc_info=True
    )
    
    return {'success': False, 'error': str(e)}
```

---

## 🚀 Next Steps

1. **Immediate**: Add logging to `event_handler.py` before merging to main
2. **Short-term**: Add logging to all automation components (P1)
3. **Medium-term**: Integrate log monitoring into health checks (P2)
4. **Long-term**: Consider centralized logging (Prometheus, Grafana) (P3)

---

**This is now a MANDATORY requirement for all future automation code.**  
**No automation component ships to production without proper logging.**
