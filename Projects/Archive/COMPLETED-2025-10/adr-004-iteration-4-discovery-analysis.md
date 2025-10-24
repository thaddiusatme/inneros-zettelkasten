# ADR-004 Iteration 4+ Discovery Analysis

**Date**: 2025-10-10  
**Status**: Discovery Phase Complete

---

## Command Inventory (workflow_demo.py)

### ✅ Already Extracted (18 commands via 11 direct + 7 wrapped)

#### Phase 1 Pre-ADR (9 commands):
1. ✅ `--process-youtube-note` → youtube_cli.py
2. ✅ `--process-youtube-notes` → youtube_cli.py
3. ✅ Advanced tag enhancement (3 commands) → advanced_tag_enhancement_cli.py
4. ✅ Review notes (3 commands) → notes_cli.py  
5. ✅ Performance (1 command) → real_data_performance_cli.py

#### Iteration 1 (2 commands):
6. ✅ `--weekly-review` → weekly_review_cli.py
7. ✅ `--enhanced-metrics` → weekly_review_cli.py

#### Iteration 2 (3 commands):
8. ✅ `--fleeting-health` → fleeting_cli.py
9. ✅ `--fleeting-triage` → fleeting_cli.py
10. ✅ `--promote-note` → fleeting_cli.py (partial)

#### Iteration 3+ (6 commands - wrapped utilities):
11. ✅ `--process-inbox-safe` → safe_workflow_cli.py (wraps safe_workflow_cli_utils.py)
12. ✅ `--batch-process-safe` → safe_workflow_cli.py (wraps safe_workflow_cli_utils.py)
13. ✅ `--performance-report` → safe_workflow_cli.py (wraps safe_workflow_cli_utils.py)
14. ✅ `--integrity-report` → safe_workflow_cli.py (wraps safe_workflow_cli_utils.py)
15. ✅ `--backup` → safe_workflow_cli.py (wraps safe_workflow_cli_utils.py)
16. ✅ `--list-backups` → safe_workflow_cli.py (wraps safe_workflow_cli_utils.py)

**Status**: 16/25 direct commands + 2 wrapped = **18/25 total (72%)**

---

## 🎯 Remaining Commands (7 commands)

### Group A: Core Workflow Operations (4 commands)
**Priority**: HIGH (frequently used, core functionality)

1. ❌ `--status` (line 672) - Show workflow status
2. ❌ `--process-inbox` (line 679) - Process all inbox notes
3. ❌ `--promote` (line 685) - Promote a note (TYPE: permanent|fleeting)
4. ❌ `--report` (line 692) - Generate full workflow report

**Utilities Check**: ❓ May use CoreWorkflowManager or WorkflowManager directly  
**Estimated Time**: 3-4 hours (likely need to build, no dedicated utilities found)

---

### Group B: Advanced Features (2 commands)
**Priority**: MEDIUM (advanced, less frequently used)

5. ❌ `--comprehensive-orphaned` (line 748) - Find ALL orphaned notes
6. ❌ `--remediate-orphans` (line 754) - Remediate orphaned notes with bidirectional links

**Utilities Check**: ❓ May use real_connection_cli_utils.py or build new  
**Estimated Time**: 2-3 hours (connection utilities exist, may wrap)

---

### Group C: Reading Intake Pipeline (2 commands)
**Priority**: LOW (skeleton implementation, P1 feature)

7. ❌ `--import-csv` (line 852) - Import CSV reading list (skeleton)
8. ❌ `--import-json` (line 857) - Import JSON reading list (skeleton)

**Utilities Check**: ❌ No utilities exist yet  
**Estimated Time**: 1-2 hours (skeleton only, validation/dry-run)

---

### Group D: Backup Management (1 command)
**Priority**: LOW (less critical, pruning feature)

9. ❌ `--prune-backups` (line 876) - Remove old backup directories

**Utilities Check**: ✅ Can use DirectoryOrganizer  
**Estimated Time**: 0.5 hours (simple, uses existing organizer)

---

### Group E: Interactive Mode (1 command)
**Priority**: LOW (optional feature)

10. ❌ `--interactive` (line 698) - Run in interactive mode

**Utilities Check**: ✅ interactive_cli_components.py exists  
**Estimated Time**: 1-2 hours (wrap existing components)

---

### Group F: Safe Workflow Sessions (2 commands)
**Priority**: LOW (advanced feature, rarely used)

11. ❌ `--start-safe-session` (line 907) - Start concurrent safe processing session
12. ❌ Additional safe workflow commands (truncated in grep)

**Utilities Check**: ✅ safe_workflow_cli_utils.py exists (already used)  
**Estimated Time**: 0.5-1 hour (wrap existing utilities)

---

## 📊 Utility File Analysis

### Existing Utility Files:
1. ✅ `safe_workflow_cli_utils.py` (19KB) - **USED in Iteration 3+**
2. ✅ `advanced_tag_enhancement_cli_utils.py` (15KB) - Used in Phase 1
3. ✅ `youtube_cli_utils.py` (22KB) - Used in Phase 1
4. ✅ `real_connection_cli_utils.py` (11KB) - **Available for orphan remediation**
5. ✅ `smart_link_cli_utils.py` (4KB) - **Available for linking features**
6. ✅ `screenshot_cli_utils.py` (35KB) - Not relevant for current extraction
7. ✅ `interactive_cli_components.py` - **Available for interactive mode**

### Utility Status for Remaining Commands:
- **Group A (Core Workflow)**: ❌ No dedicated utilities → Build from scratch (3-4 hours)
- **Group B (Orphan Features)**: ✅ real_connection_cli_utils.py available → Wrap (2-3 hours)
- **Group C (Reading Intake)**: ❌ No utilities → Build skeleton (1-2 hours)
- **Group D (Prune Backups)**: ✅ DirectoryOrganizer available → Simple build (0.5 hours)
- **Group E (Interactive)**: ✅ interactive_cli_components.py available → Wrap (1-2 hours)
- **Group F (Safe Sessions)**: ✅ safe_workflow_cli_utils.py available → Wrap (0.5-1 hour)

---

## 🎯 Recommended Next Iteration (Iteration 4)

### Option 1: Core Workflow CLI (HIGH PRIORITY) ⭐ **RECOMMENDED**
**Commands**: `--status`, `--process-inbox`, `--promote`, `--report` (4 commands)  
**Rationale**: Most frequently used, core functionality  
**Estimated Time**: 3-4 hours (no utilities, build from scratch)  
**Manager**: CoreWorkflowManager or WorkflowManager  
**Value**: Highest user impact, completes core workflow extraction

---

### Option 2: Quick Wins - Wrap Existing Utilities (FAST)
**Commands**: `--prune-backups`, `--start-safe-session`, `--interactive` (3 commands)  
**Rationale**: Utilities exist, fast completion  
**Estimated Time**: 2-3 hours total (wrapping existing)  
**Value**: Rapid progress boost to ~90% completion

---

### Option 3: Advanced Features CLI (MEDIUM PRIORITY)
**Commands**: `--comprehensive-orphaned`, `--remediate-orphans` (2 commands)  
**Rationale**: Connection utilities exist, advanced features  
**Estimated Time**: 2-3 hours (wrap real_connection_cli_utils.py)  
**Value**: Complete orphan management features

---

## 💡 Strategic Recommendation

**Iteration 4**: **Option 1 - Core Workflow CLI** ⭐

**Why**:
1. **Highest user impact** - Most frequently used commands
2. **Completes core workflow** - Status, inbox, promote, report
3. **Logical grouping** - All related to basic workflow operations
4. **Build experience** - No utilities exist, full TDD from scratch
5. **Progress**: Would reach **80% completion** (22/25 commands)

**Next After Iteration 4**:
- Iteration 5: Quick wins (Option 2) → 90% completion
- Iteration 6: Advanced features (Option 3) → 95% completion  
- Iteration 7: Reading intake (Option 3) → 100% completion ✅

---

## 📋 Iteration 4 Execution Plan (Core Workflow CLI)

### Commands to Extract:
1. `--status` → core_workflow_cli.py
2. `--process-inbox` → core_workflow_cli.py
3. `--promote` → core_workflow_cli.py
4. `--report` → core_workflow_cli.py

### Manager Investigation Needed:
- Check `CoreWorkflowManager` for these methods
- Check `WorkflowManager` for these methods
- Verify which manager handles core workflow operations

### TDD Approach:
- RED: Write 6-8 failing tests (4 commands + utilities + formats)
- GREEN: Build CLI from scratch (~3-4 hours)
- REFACTOR: Extract formatter if needed (CLI > 400 LOC)

### Expected LOC:
- CLI: ~400-500 LOC (4 commands = ~100-125 LOC each)
- Formatter: ~150-200 LOC (if needed)
- Tests: ~200-250 LOC (comprehensive coverage)

---

## ✅ Discovery Phase Complete

**Ready to proceed with**:
- ✅ All commands identified and categorized
- ✅ Utilities analyzed and documented
- ✅ Strategic recommendation: Core Workflow CLI (Iteration 4)
- ✅ Time estimates calculated
- ✅ Manager investigation plan ready

**Next Action**: Investigate managers and begin RED phase for Core Workflow CLI

---

**Progress After Iteration 4**: 80% complete (22/25 commands)  
**Remaining After Iteration 4**: 3 commands (reading intake + advanced features)
