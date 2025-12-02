# Discovery Audit: InnerOS CLI & Automation Status

> **Audit Date**: 2025-12-01  
> **Purpose**: Document what works, what's broken, and what needs fixing  
> **Sprint**: Make InnerOS Usable

---

## 🎉 KEY DISCOVERY: Automation IS Running!

**Cron jobs are active and have been since Nov 1, 2025:**
```
30 23 * * *     Screenshot import (11:30 PM daily)
0 6 * * 1,3,5   Inbox processing (Mon/Wed/Fri 6 AM)
0 6,10,14,18,22 Health monitor (every 4 hours)
*/30 * * * *    Status check (every 30 min)
```

**Recent activity** (from logs):
- Health monitor ran at 18:00 today ✅
- Screenshot handler logs exist through Nov 30 ✅
- YouTube handler logs exist through Nov 30 ✅

**Status CLI mismatch**: Registry expects `youtube_watcher.log` but cron creates `youtube_handler_YYYY-MM-DD.log`

---

## 📊 Executive Summary

| Category | Count | Status |
|----------|-------|--------|
| Total CLI files | 48 | Inventoried |
| Automation modules | 29 | Inventoried |
| **Working CLIs** | 5 | ✅ Functional |
| **Broken CLIs** | 3 | ❌ Import errors |
| **Untested CLIs** | 40 | ⚠️ Need validation |

**Critical Finding**: Core CLIs work but require `--vault knowledge` flag. Default path is wrong.

---

## ✅ Working CLIs

### 1. `inneros_status_cli.py` - Status Dashboard
```bash
PYTHONPATH=development python3 -c "from src.cli.inneros_status_cli import main; main()"
```
**Output**: Shows 3 handlers (youtube_watcher, screenshot_processor, health_monitor)
**Issue**: All show "not running" even when daemon is running

### 2. `inneros_automation_cli.py` - Daemon Control
```bash
# Start daemon
PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py daemon start

# Check status  
PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py daemon status

# Stop daemon
PYTHONPATH=development python3 development/src/cli/inneros_automation_cli.py daemon stop
```
**Status**: ✅ Works - daemon starts/stops correctly

### 3. `weekly_review_cli.py` - Weekly Review
```bash
PYTHONPATH=development python3 development/src/cli/weekly_review_cli.py --vault knowledge weekly-review --preview
```
**Result**: Found 55 notes requiring review
**Commands**: `weekly-review`, `enhanced-metrics`
**Flags**: `--preview`, `--export PATH`, `--format {normal,json}`

### 4. `fleeting_cli.py` - Fleeting Notes Health
```bash
PYTHONPATH=development python3 development/src/cli/fleeting_cli.py --vault knowledge fleeting-health
```
**Result**: 
- 80 fleeting notes total
- 🚨 **CRITICAL**: 68% over 90 days old
- 54 notes need immediate attention
- 26 stale notes (31-90 days)

**Commands**: `fleeting-health`, `fleeting-triage`

### 5. `daemon_cli.py` (via -m only)
```bash
PYTHONPATH=development python3 -m src.cli.daemon_cli status
```
**Note**: Cannot run directly due to relative import issue

---

## ❌ Broken CLIs

### 1. `connections_demo.py`
```
ModuleNotFoundError: No module named 'ai'
```
**Fix needed**: Update import path from `ai.` to `src.ai.`

### 2. `evening_screenshot_processor.py`
```
ImportError: attempted relative import with no known parent package
```
**Fix needed**: Run via `-m` or fix imports

### 3. `daemon_cli.py` (direct execution)
```
ImportError: attempted relative import with no known parent package
```
**Workaround**: Use `-m src.cli.daemon_cli` instead

---

## ⚠️ Critical Issues Found

### Issue 1: Vault Path Default
**Problem**: All CLIs default to current directory (`.`) instead of `knowledge/`
**Impact**: Commands return empty results when run from repo root
**Fix**: Either:
- Always pass `--vault knowledge`
- Change default in CLI initialization
- Add Makefile targets with correct paths

### Issue 2: Argument Order
**Problem**: `--vault` flag must come BEFORE subcommand
```bash
# ❌ Wrong
python3 fleeting_cli.py fleeting-health --vault knowledge

# ✅ Correct  
python3 fleeting_cli.py --vault knowledge fleeting-health
```
**Fix**: Document clearly or restructure argparse

### Issue 3: Status Mismatch
**Problem**: `inneros_status_cli.py` shows handlers as "not running" even when daemon is running
**Cause**: Status CLI checks different state than daemon process
**Fix**: Align status detection between daemon and status CLI

### Issue 4: No User-Friendly Makefile Targets
**Problem**: Current Makefile only has dev commands (`lint`, `test`, `unit`)
**Missing**:
```makefile
up:      # Start automation
down:    # Stop automation
status:  # Check health
review:  # Run weekly review
```

---

## 📋 Handler Status Checklist

### Screenshot Handler
- [ ] **OneDrive path configured?** - Unknown
- [ ] **OCR integration working?** - Untested
- [ ] **Note creation working?** - Untested
- [ ] **Smart link integration?** - Untested

### Smart Link Handler
- [ ] **Connection discovery?** - ❌ `connections_demo.py` has import error
- [ ] **Link suggestions?** - Untested

### YouTube Handler
- [ ] **IP ban status?** - Unknown
- [ ] **Transcript extraction?** - Untested
- [ ] **Note creation?** - Untested

### Weekly Review
- [x] **Triage working?** - ✅ Yes, found 55 notes
- [x] **Preview mode?** - ✅ Yes
- [ ] **Export working?** - Untested
- [ ] **Promotion working?** - Untested

---

## 📁 File Inventory

### CLI Files (48 total)
**Core User CLIs:**
- `inneros_status_cli.py` - Status dashboard
- `inneros_automation_cli.py` - Daemon control
- `weekly_review_cli.py` - Weekly review
- `fleeting_cli.py` - Fleeting notes management
- `backup_cli.py` - Backup management
- `notes_cli.py` - Note operations

**Feature CLIs:**
- `screenshot_processor.py` - Screenshot processing
- `evening_screenshot_processor.py` - Evening workflow
- `connections_demo.py` - Smart linking
- `analytics_demo.py` - Analytics

**Deprecated:**
- `workflow_demo.py` - ⚠️ DEPRECATED per ADR-004

### Automation Modules (29 total)
**Core:**
- `daemon.py` - Main daemon process
- `scheduler.py` - Job scheduling
- `file_watcher.py` - File monitoring
- `health.py` - Health checks

**Handlers:**
- `feature_handlers.py` - Feature routing
- `youtube_api.py` - YouTube integration
- `event_handler.py` - Event processing

---

## 🎯 Recommended Fix Order

### Phase 1: Make Status Work (Day 1-2)
1. [ ] Fix status CLI to align with daemon state
2. [ ] Add Makefile `status` target
3. [ ] Document correct vault path

### Phase 2: Make Automation Start (Day 2-3)
1. [ ] Fix handler registration in daemon
2. [ ] Add Makefile `up` and `down` targets
3. [ ] Test daemon start → status shows healthy

### Phase 3: Fix Broken Imports (Day 3-4)
1. [ ] Fix `connections_demo.py` import error
2. [ ] Fix `evening_screenshot_processor.py` import
3. [ ] Standardize import patterns

### Phase 4: End-to-End Validation (Day 4-5)
1. [ ] Test screenshot → OCR → note workflow
2. [ ] Test weekly review → promotion workflow
3. [ ] Document any additional issues

---

## 📝 Notes

### Vault Health (as of 2025-12-01)
- **Inbox**: 24 files (including automation folder)
- **Fleeting Notes**: 80 files (68% over 90 days - CRITICAL backlog)
- **Weekly Review**: 55 notes requiring action

### Current Makefile Commands
```makefile
setup    # Install dependencies
lint     # Run linters
type     # Type checking
unit     # Unit tests (fast)
unit-all # All unit tests
integ    # Integration tests
cov      # Coverage report
test     # lint + type + unit
run      # Weekly review (deprecated path)
ui       # Web UI
```

---

*Audit completed: 2025-12-01 17:51 PST*
*Next action: Start Phase 1 fixes*
