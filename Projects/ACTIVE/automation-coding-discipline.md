# Automation Coding Discipline - Definition of Done

**Status**: 🔒 MANDATORY - Required for ALL automation code  
**Created**: 2025-10-07  
**Enforcement**: Code review, CI/CD checks  
**Scope**: All code in `development/src/automation/`

---

## 🎯 Purpose

This document defines the **non-negotiable standards** for automation components. No code merges to main without meeting these requirements.

**Identified Gap**: TDD Iteration 2 P1.2 revealed missing logging infrastructure in production-ready code.

---

## ✅ Definition of Done Checklist

**Every automation component MUST have:**

### **1. Python Logging Infrastructure** 🔴 MANDATORY

```python
import logging
from pathlib import Path
import time

class AutomationComponent:
    def __init__(self, ...):
        # Setup logger
        log_dir = Path(__file__).parent.parent.parent.parent / '.automation' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f'{self.__class__.__name__.lower()}_{time.strftime("%Y-%m-%d")}.log'
        
        self.logger = logging.getLogger(__name__)
        
        # Configure handler
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        
        # Log initialization
        self.logger.info(f"Initialized: {self.__class__.__name__}")
```

**Required Log Points:**

| Event | Level | Must Include |
|-------|-------|--------------|
| **Initialization** | INFO | Component name, configuration |
| **Success Operations** | INFO | What processed, duration |
| **Errors** | ERROR | File/operation, exception type, full stack trace |
| **State Changes** | INFO | Old state → New state |
| **Warnings** | WARNING | Queue depth, performance issues |

**Example Error Logging:**
```python
except Exception as e:
    self.logger.error(
        f"Failed to process {file_path}: {type(e).__name__}: {str(e)}",
        exc_info=True  # ← REQUIRED: Include stack trace
    )
    # Also update metrics
    self._stats['failed'] += 1
```

---

### **2. Comprehensive Error Handling** 🔴 MANDATORY

**Every method that can fail MUST:**

```python
def risky_operation(self, file_path: Path) -> Dict[str, Any]:
    """Process with comprehensive error handling."""
    try:
        # Operation
        result = self._do_work(file_path)
        
        # Log success
        self.logger.info(f"Successfully processed {file_path}")
        
        return {'success': True, 'result': result}
        
    except SpecificException as e:
        # Handle expected errors gracefully
        self.logger.warning(f"Expected issue in {file_path}: {e}")
        return {'success': False, 'error': str(e), 'retryable': True}
        
    except Exception as e:
        # Log unexpected errors with full context
        self.logger.error(
            f"Unexpected error processing {file_path}: {type(e).__name__}: {str(e)}",
            exc_info=True
        )
        return {'success': False, 'error': str(e), 'retryable': False}
```

**Requirements:**
- ✅ Try-except blocks for all I/O operations
- ✅ Specific exception handling for known failure modes
- ✅ Generic exception catch-all for unknown failures
- ✅ Error details logged with full stack trace
- ✅ Graceful degradation (daemon stays running)
- ✅ Error metrics tracked separately from logging

---

### **3. Health Monitoring Integration** 🔴 MANDATORY

**Every component MUST provide:**

```python
def get_health_status(self) -> Dict[str, Any]:
    """Return component health status for daemon monitoring."""
    return {
        'is_healthy': self._is_healthy(),
        'component': self.__class__.__name__,
        'metrics': {
            'total_processed': self._stats['total'],
            'failed': self._stats['failed'],
            'success_rate': self._calculate_success_rate()
        },
        'warnings': self._get_warnings()
    }

def _is_healthy(self) -> bool:
    """Determine if component is healthy."""
    # Check error rate
    if self._stats['total'] > 0:
        error_rate = self._stats['failed'] / self._stats['total']
        if error_rate > 0.2:  # >20% failures
            return False
    
    # Check queue depth
    if hasattr(self, 'queue') and len(self.queue) > 100:
        return False
    
    return True

def _get_warnings(self) -> List[str]:
    """Return current warnings."""
    warnings = []
    
    if hasattr(self, 'queue') and len(self.queue) > 50:
        warnings.append(f"High queue depth: {len(self.queue)}")
    
    if self._stats['failed'] > 10:
        warnings.append(f"High failure count: {self._stats['failed']}")
    
    return warnings
```

---

### **4. Metrics Tracking** 🔴 MANDATORY

**Track at minimum:**

```python
def __init__(self, ...):
    self._stats = {
        'total_processed': 0,
        'successful': 0,
        'failed': 0,
        'processing_times': [],  # Last 100 operations
        'last_error': None,
        'last_error_time': None
    }

def get_metrics(self) -> Dict[str, Any]:
    """Return component metrics."""
    avg_time = 0.0
    if self._stats['processing_times']:
        avg_time = sum(self._stats['processing_times']) / len(self._stats['processing_times'])
    
    return {
        'total_processed': self._stats['total_processed'],
        'successful': self._stats['successful'],
        'failed': self._stats['failed'],
        'success_rate': self._calculate_success_rate(),
        'avg_processing_time': avg_time,
        'last_error': self._stats['last_error'],
        'last_error_time': self._stats['last_error_time']
    }
```

---

### **5. Test Coverage Requirements** 🔴 MANDATORY

**For component to be production-ready:**

- ✅ **≥80% code coverage** on the component
- ✅ **Error path testing**: Verify logging on failures
- ✅ **Health check testing**: Verify health status accuracy
- ✅ **Metrics testing**: Verify metrics tracking
- ✅ **Integration testing**: Verify component works in daemon
- ✅ **Real data testing**: Validate with actual user data

**Example Test:**
```python
def test_error_logging(self, tmp_path, caplog):
    """Verify errors are logged with stack traces."""
    handler = AutomationEventHandler(str(tmp_path))
    
    # Cause an error
    with patch.object(handler.core_workflow, 'process_inbox_note', 
                     side_effect=ValueError("Test error")):
        result = handler.process_file_event(Path("test.md"), "modified")
    
    # Verify logging
    assert result['success'] is False
    assert "ValueError: Test error" in caplog.text
    assert "Traceback" in caplog.text  # Stack trace logged
    
    # Verify metrics
    metrics = handler.get_metrics()
    assert metrics['failed_events'] == 1
```

---

### **6. Documentation Standards** 🔴 MANDATORY

**Every component file MUST have:**

```python
"""
Component Name - Brief Purpose

Detailed description of what this component does, how it fits into the
automation architecture, and key design decisions.

Architecture:
- Size: ~XXX LOC (ADR-001 compliant: <500 LOC)
- Responsibility: Single clear purpose
- Dependencies: List key dependencies
- Integration: How it integrates with daemon/other components

Error Handling:
- Graceful degradation on AI service failures
- Comprehensive logging with stack traces
- Metrics tracking for monitoring

Health Monitoring:
- Provides health status via get_health_status()
- Tracks success/failure rates
- Warns on queue depth/error rate issues

Example:
    handler = AutomationEventHandler(vault_path="/path/to/vault")
    result = handler.process_file_event(Path("note.md"), "modified")
    health = handler.get_health_status()
"""
```

**Every method MUST have:**
- Clear docstring with purpose
- Args documented with types
- Returns documented with structure
- Raises documented for exceptions

---

### **7. ADR-001 Architectural Compliance** 🔴 MANDATORY

**Size Limits:**
- **<500 LOC per class** (hard limit)
- **<200 LOC per class** (recommended for new components)
- **<30 LOC per method** (recommended)

**Single Responsibility:**
- Class does ONE thing clearly
- Class name accurately describes purpose
- No "Manager" classes >300 LOC
- No "Handler" classes >200 LOC

**When approaching limits:**
- 150-180 LOC: Consider utility extraction
- 180-200 LOC: Plan extraction before adding features
- >200 LOC: Extract utilities BEFORE adding features

---

## 🚫 Code Review Blockers

**Pull requests are REJECTED if missing:**

1. ❌ No logging infrastructure
2. ❌ Errors not logged to files
3. ❌ No error handling or generic catch-all only
4. ❌ No health monitoring integration
5. ❌ No metrics tracking
6. ❌ Test coverage <80%
7. ❌ No tests for error paths
8. ❌ Exceeds 500 LOC without ADR
9. ❌ No docstrings or incomplete documentation
10. ❌ Real data testing not performed

---

## 📋 Pre-Commit Checklist

**Before committing ANY automation code:**

```bash
# 1. Check logging exists
grep -q "import logging" development/src/automation/your_component.py || echo "❌ No logging"

# 2. Check error logging with stack traces
grep -q "exc_info=True" development/src/automation/your_component.py || echo "❌ No stack trace logging"

# 3. Check health monitoring
grep -q "get_health_status" development/src/automation/your_component.py || echo "❌ No health monitoring"

# 4. Run tests with coverage
PYTHONPATH=development pytest development/tests/unit/test_your_component.py --cov=development/src/automation/your_component --cov-report=term-missing

# 5. Check LOC
wc -l development/src/automation/your_component.py

# 6. Run real data test
PYTHONPATH=development python3 development/demos/your_component_real_data_test.py
```

**All checks must pass** ✅

---

## 🎯 Enforcement

### **Code Review**
- Reviewer verifies all checklist items
- No approval without full compliance
- Document exceptions in PR description

### **CI/CD Pipeline** (Future)
```yaml
# .github/workflows/automation-compliance.yml
- name: Check Logging Infrastructure
  run: |
    grep -r "import logging" development/src/automation/*.py || exit 1
    grep -r "exc_info=True" development/src/automation/*.py || exit 1

- name: Check Test Coverage
  run: |
    pytest --cov=development/src/automation --cov-fail-under=80
```

### **Monthly Audit**
- First Monday of each month
- Review all automation components
- Verify compliance with standards
- Update standards if needed

---

## 📊 Success Metrics

**Track in project reviews:**

- [ ] 100% of automation components have logging
- [ ] 100% of errors logged with stack traces
- [ ] 100% of components integrate with health monitoring
- [ ] Average test coverage ≥80% across automation/
- [ ] Zero production incidents due to missing logging

---

## 🔗 Related Documents

- **Backlog Item**: `Projects/ACTIVE/logging-monitoring-requirements-automation.md`
- **Architecture**: `.windsurf/rules/architectural-constraints.md`
- **Monitoring**: `.windsurf/rules/automation-monitoring-requirements.md`
- **Example**: Current gap in `development/src/automation/event_handler.py`

---

## 🚀 Immediate Action Items

**For TDD Iteration 2 P1.2:**

1. ⚠️ **BEFORE MERGE**: Add logging to `event_handler.py`
2. ⚠️ **BEFORE MERGE**: Add logging tests
3. ⚠️ **BEFORE MERGE**: Verify real data test shows logs created
4. ✅ **AFTER MERGE**: Update this discipline based on implementation

---

**Last Updated**: 2025-10-07  
**Status**: ACTIVE - Mandatory for all automation code  
**Exceptions**: None - full compliance required
