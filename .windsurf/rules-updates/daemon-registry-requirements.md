# Daemon Registry Requirements

> **Add to**: `.windsurf/rules/automation-monitoring-requirements.md` (append at end before version info)
> **Priority**: CRITICAL - Must update when creating/modifying daemons
> **Created**: 2025-10-23

---

## 🔧 Daemon Registry Maintenance (CRITICAL)

**Location**: `.automation/config/daemon_registry.yaml`

**MANDATORY**: Every automation daemon MUST be registered in the daemon registry for visibility and monitoring.

### When to Update Registry

**ALWAYS update when**:
- ✅ Creating a new background daemon/automation script
- ✅ Converting existing script to daemon mode
- ✅ Adding cron-scheduled automation
- ✅ Implementing Phase 3 automation layer for any feature

**NEVER add for**:
- ❌ One-time scripts or manual operations
- ❌ Non-background processes (CLI commands)
- ❌ External services (GitHub Actions, etc.)

### Required Registry Entry

```yaml
  - name: daemon_name              # REQUIRED: Lowercase, underscores, unique
    script_path: .automation/scripts/script.py  # REQUIRED: Relative to repo root
    log_path: .automation/logs/daemon_name.log  # REQUIRED: Log file location
    pid_file: .automation/logs/daemon_name.pid  # REQUIRED: PID file location
    description: What daemon does    # REQUIRED: Present tense, <80 chars
```

### Registry Update Checklist

When creating a daemon, AI MUST:

- [ ] **Add entry to daemon_registry.yaml** with all 5 required fields
- [ ] **Validate schema** with `pytest tests/unit/cli/test_automation_status_cli.py -k validate`
- [ ] **Test visibility** with AutomationStatusCLI.status()
- [ ] **Update last modified date** in daemon_registry.yaml header
- [ ] **Commit registry update** separately with clear message

### Validation Requirements

**Schema Validation** (automatic via `DaemonRegistry` class):
```python
REQUIRED_FIELDS = ['name', 'script_path', 'log_path', 'pid_file', 'description']
```

**Test Validation** (before committing):
```bash
cd development
pytest tests/unit/cli/test_automation_status_cli.py::TestDaemonRegistry::test_validates_daemon_config -v
```

### Quick Add Template

Copy this template when adding new daemon:

```yaml
  - name: new_daemon_name
    script_path: .automation/scripts/new_daemon.py
    log_path: .automation/logs/new_daemon_name.log
    pid_file: .automation/logs/new_daemon_name.pid
    description: Brief description of daemon purpose
```

### Documentation References

- **Detailed Guide**: `.automation/config/DAEMON-REGISTRY-MAINTENANCE.md`
- **Quick Reference**: `.automation/config/QUICK-ADD-DAEMON.md`
- **Implementation**: `development/src/cli/automation_status_cli.py`
- **Tests**: `development/tests/unit/cli/test_automation_status_cli.py`

### Enforcement

**AI MUST**:
1. Remind user to update daemon registry when creating automation
2. Provide registry entry template in commit message
3. Include registry validation in development checklist
4. Test daemon visibility before marking feature complete

**Red Flags** (AI should alert if):
- New daemon script created without registry entry
- Phase 3 automation implemented without registry update
- Cron job added without corresponding registry entry
- "We'll register it later" mentioned in conversation

### Integration with Phase 3 & 4

**Phase 3 (Automation Layer)**:
- Daemon implementation → MUST update registry
- Scheduler configuration → MUST update registry
- Event handler setup → MUST update registry

**Phase 4 (Monitoring)**:
- AutomationStatusCLI reads from registry
- Health checks reference registry entries
- Alerts use daemon names from registry

### Success Metrics

- **Registry Coverage**: 100% (all daemons registered)
- **Schema Compliance**: 100% (all entries validate)
- **Visibility**: <5 seconds to check all daemon statuses
- **Maintenance**: Registry updated within same commit as daemon creation

---

## 🚨 Critical Path Reminder

**Creating a daemon WITHOUT updating the registry is like deploying a service without monitoring - unacceptable.**

The Automation Visibility CLI (`automation_status_cli.py`) provides zero-friction daemon monitoring, but ONLY for registered daemons. Skipping registry update defeats the entire purpose of automation visibility.

---

**Current Daemon Count** (as of 2025-10-23): 3
- health_monitor
- screenshot_processor  
- youtube_watcher

**Target**: All automation daemons registered and monitored

---
