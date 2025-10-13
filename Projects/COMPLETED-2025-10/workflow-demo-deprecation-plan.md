# workflow_demo.py Deprecation & Removal Plan

**Date**: 2025-10-12  
**Status**: 🔄 **PLANNING**  
**Priority**: P1 - Technical Debt Cleanup  
**Target Removal**: 2025-10-15 (3 days)

---

## 🎯 Objective

Complete removal of deprecated `workflow_demo.py` monolith (2,128 LOC) following ADR-004 CLI extraction. All functionality has been migrated to dedicated CLIs - now remove the deprecated layer entirely.

---

## 📊 Current State (Post ADR-004)

### **What ADR-004 Accomplished** (Oct 10-11, 2025)
- ✅ 25/25 commands extracted to dedicated CLIs
- ✅ 2,074 LOC monolith eliminated (conceptually)
- ✅ 13/13 UX regression tests passing
- ✅ 7/7 contract tests passing

### **What Still Exists**
- ❌ `workflow_demo.py` still present (2,128 lines)
- ❌ Documentation still references workflow_demo.py
- ❌ Quality audit tested workflow_demo.py (wrong layer)
- ❌ Bug fixes applied to workflow_demo.py (wrong layer)

---

## 🗺️ Migration Strategy

### **Phase 1: Audit & Document** (1 hour)

#### **1.1 Complete Command Mapping** ✅

All 26 workflow_demo.py commands mapped to dedicated CLIs:

##### **Weekly Review & Metrics (weekly_review_cli.py)**
```bash
--weekly-review                    → python3 src/cli/weekly_review_cli.py weekly-review
--enhanced-metrics                 → python3 src/cli/weekly_review_cli.py enhanced-metrics
--comprehensive-orphaned           → python3 src/cli/weekly_review_cli.py comprehensive-orphaned
--remediate-orphans                → python3 src/cli/weekly_review_cli.py remediate-orphans
```

##### **Fleeting Notes (fleeting_cli.py)**
```bash
--fleeting-health                  → python3 src/cli/fleeting_cli.py fleeting-health
--fleeting-triage                  → python3 src/cli/fleeting_cli.py fleeting-triage
--promote-note [PATH]              → python3 src/cli/fleeting_cli.py promote-note [PATH]
```

##### **Core Workflow (core_workflow_cli.py)**
```bash
--status                           → python3 src/cli/core_workflow_cli.py status
--process-inbox                    → python3 src/cli/core_workflow_cli.py process-inbox
--promote [FILE] [TYPE]            → python3 src/cli/core_workflow_cli.py promote [FILE] [TYPE]
--report                           → python3 src/cli/core_workflow_cli.py report
```

##### **Safe Workflow Processing (safe_workflow_cli.py)**
```bash
--process-inbox-safe               → python3 src/cli/safe_workflow_cli.py process-inbox-safe
--batch-process-safe               → python3 src/cli/safe_workflow_cli.py batch-process-safe
--performance-report               → python3 src/cli/safe_workflow_cli.py performance-report
--integrity-report                 → python3 src/cli/safe_workflow_cli.py integrity-report
--start-safe-session [NAME]        → python3 src/cli/safe_workflow_cli.py start-safe-session --session-name [NAME]
--process-in-session [ID] [PATH]  → python3 src/cli/safe_workflow_cli.py process-in-session --session-id [ID] --note-path [PATH]
```

##### **Backup Management (backup_cli.py)**
```bash
--backup                           → python3 src/cli/backup_cli.py backup
--list-backups                     → python3 src/cli/backup_cli.py list-backups
--prune-backups                    → python3 src/cli/backup_cli.py prune-backups --keep [N]
```

##### **YouTube Processing (youtube_cli.py)**
```bash
--process-youtube-note [PATH]      → python3 src/cli/youtube_cli.py process-note [PATH]
--process-youtube-notes            → python3 src/cli/youtube_cli.py batch-process
```

##### **Reading Intake (reading_intake_cli.py)**
```bash
--import-csv [PATH]                → python3 src/cli/reading_intake_cli.py import-csv [PATH]
--import-json [PATH]               → python3 src/cli/reading_intake_cli.py import-json [PATH]
```

##### **Screenshot Processing (screenshot_cli.py)**
```bash
--screenshots                      → python3 src/cli/screenshot_cli.py process-screenshots
```

##### **Interactive Mode (interactive_cli.py)**
```bash
--interactive                      → python3 src/cli/interactive_cli.py interactive
```

#### **1.2 Reference Audit**
Find all references to workflow_demo.py:
```bash
grep -r "workflow_demo" . --include="*.md" --include="*.py" --include="*.sh"
```

Expected locations:
- CLI-REFERENCE.md
- QUICK-REFERENCE.md  
- README.md
- GETTING-STARTED.md
- Bug reports (Projects/ACTIVE/)
- Test files
- Shell scripts

---

### **Phase 2: Documentation Updates** (1-2 hours)

#### **2.1 CLI-REFERENCE.md**
- [ ] Remove all workflow_demo.py examples
- [ ] Replace with dedicated CLI examples
- [ ] Add deprecation notice section
- [ ] Update command index

#### **2.2 QUICK-REFERENCE.md**
- [ ] Update quick command examples
- [ ] Replace workflow_demo.py references
- [ ] Add "Migrating from workflow_demo.py" section

#### **2.3 README.md**
- [ ] Update main usage examples
- [ ] Replace deprecated commands
- [ ] Add migration guide link

#### **2.4 GETTING-STARTED.md**
- [ ] Update tutorial steps
- [ ] Use dedicated CLIs in examples
- [ ] Add workflow_demo.py deprecation note

#### **2.5 Bug Reports**
- [ ] Update all bug reports in Projects/ACTIVE/
- [ ] Note that workflow_demo.py bugs are deprecated
- [ ] Link to dedicated CLI equivalents

---

### **Phase 3: Create MIGRATION-GUIDE.md** (30 min)

Create comprehensive migration guide:

```markdown
# Migrating from workflow_demo.py to Dedicated CLIs

## Quick Command Reference
[Old command] → [New command]

## Why Migrate?
- Better architecture (ADR-004)
- Focused CLIs with clear responsibilities
- Better error messages
- Easier to maintain
- workflow_demo.py will be removed Oct 15, 2025

## Migration Steps
1. Identify commands you use
2. Find dedicated CLI equivalent
3. Update scripts/workflows
4. Test new commands
5. Delete workflow_demo.py references

## Troubleshooting
[Common issues and solutions]
```

---

### **Phase 4: Add Deprecation Warning** (15 min)

Add prominent warning to workflow_demo.py:

```python
#!/usr/bin/env python3
"""
⚠️  DEPRECATED - DO NOT USE ⚠️

This file is deprecated as of 2025-10-12 following ADR-004 CLI extraction.
All functionality has been migrated to dedicated CLIs.

REMOVAL DATE: 2025-10-15

Please use dedicated CLIs instead:
- Weekly Review: python3 src/cli/weekly_review_cli.py
- Fleeting Notes: python3 src/cli/fleeting_cli.py
- YouTube: python3 src/cli/youtube_cli.py
- Backups: python3 src/cli/backup_cli.py
- Core Workflow: python3 src/cli/core_workflow_cli.py

See MIGRATION-GUIDE.md for complete mapping.

This file will be deleted on 2025-10-15.
"""

import sys
import warnings

warnings.warn(
    "workflow_demo.py is deprecated. Use dedicated CLIs instead. "
    "See MIGRATION-GUIDE.md. This file will be removed 2025-10-15.",
    DeprecationWarning,
    stacklevel=2
)

# Rest of file...
```

---

### **Phase 5: Update Quality Audit** (30 min)

#### **5.1 Update Bug Reports**
- [ ] Mark workflow_demo.py bugs as "deprecated layer"
- [ ] Verify dedicated CLIs don't have same bugs
- [ ] Update AUDIT-SESSION-SUMMARY-2025-10-10.md

#### **5.2 Update Test Strategy**
- [ ] Quality audit should test dedicated CLIs only
- [ ] Remove workflow_demo.py from test plans
- [ ] Update audit-report-2025-10-10.md

---

### **Phase 6: Verify Dedicated CLIs** (1 hour)

Test that dedicated CLIs work correctly:

```bash
# Weekly Review
python3 development/src/cli/weekly_review_cli.py knowledge/

# Fleeting Notes
python3 development/src/cli/fleeting_cli.py triage
python3 development/src/cli/fleeting_cli.py health

# YouTube
python3 development/src/cli/youtube_cli.py batch-process

# Backups
python3 development/src/cli/backup_cli.py list

# Core Workflow
python3 development/src/cli/core_workflow_cli.py status

# Orphaned Notes
python3 development/src/cli/weekly_review_cli.py --orphaned

# Enhanced Metrics  
python3 development/src/cli/weekly_review_cli.py --metrics
```

**Success Criteria**: All 11 workflows work via dedicated CLIs

---

### **Phase 7: Final Removal** (15 min)

When ready (2025-10-15):

```bash
# 1. Final verification
git status
git log workflow_demo.py  # Review history

# 2. Archive for reference
mkdir -p .archive/deprecated-2025-10/
git mv development/src/cli/workflow_demo.py .archive/deprecated-2025-10/

# 3. Commit removal
git commit -m "refactor: Remove deprecated workflow_demo.py monolith

Following ADR-004 CLI extraction (Oct 10-11, 2025), all functionality
has been migrated to dedicated CLIs. Removing 2,128 LOC deprecated layer.

All commands now use dedicated CLIs:
- weekly_review_cli.py
- fleeting_cli.py
- youtube_cli.py
- backup_cli.py
- core_workflow_cli.py
- safe_workflow_cli.py
- interactive_cli.py

See MIGRATION-GUIDE.md for complete command mapping.

Resolves: ADR-004 cleanup phase
Impact: -2,128 LOC technical debt eliminated"
```

---

## 📋 Checklist

### **Phase 1: Audit** ✅ COMPLETE (2025-10-12)
- [x] Create command mapping (workflow_demo → dedicated CLIs)
- [x] Find all references in codebase
- [x] Document current usage locations

**Audit Results**:
- **709 matches** across **161 files**
- **26 command flags** mapped to dedicated CLIs
- Top reference locations:
  - Test files: 30-32 matches (test_evening_screenshot_cli_tdd_2.py, test_weekly_review_cli.py)
  - Documentation: 8-29 matches (MIGRATION-GUIDE.md, ADR-004, getting-started)
  - Project docs: 5-12 matches (manifests, workflows, lessons learned)
  - Archive files: 5-20 matches (legacy documentation)
  - Automation scripts: References in .automation/ and cron scripts

### **Phase 2: Documentation** ⏸️ Not Started
- [ ] Update CLI-REFERENCE.md
- [ ] Update QUICK-REFERENCE.md
- [ ] Update README.md
- [ ] Update GETTING-STARTED.md
- [ ] Update bug reports

### **Phase 3: Migration Guide** ⏸️ Not Started
- [ ] Create MIGRATION-GUIDE.md
- [ ] Add command mapping table
- [ ] Add migration steps
- [ ] Add troubleshooting section

### **Phase 4: Deprecation Warning** ⏸️ Not Started
- [ ] Add warning to workflow_demo.py header
- [ ] Add DeprecationWarning in code
- [ ] Set removal date (2025-10-15)

### **Phase 5: Quality Audit Update** ⏸️ Not Started
- [ ] Mark workflow_demo bugs as deprecated
- [ ] Update audit strategy
- [ ] Update bug reports

### **Phase 6: Verification** ⏸️ Not Started
- [ ] Test all 11 workflows via dedicated CLIs
- [ ] Verify bug fixes not needed (proper architecture)
- [ ] Document any remaining issues

### **Phase 7: Removal** ⏸️ Not Started
- [ ] Archive workflow_demo.py
- [ ] Final commit
- [ ] Update project status

---

## 🎯 Success Metrics

**Before**:
- 2,128 LOC deprecated monolith still present
- Documentation references old patterns
- Bug fixes applied to wrong layer
- Confusion about which CLI to use

**After**:
- 0 references to workflow_demo.py
- All documentation uses dedicated CLIs
- Clear migration path documented
- Technical debt eliminated

---

## ⚠️ Risks & Mitigation

### **Risk 1: Breaking User Workflows**
**Mitigation**:
- 3-day deprecation notice
- Comprehensive migration guide
- Clear error messages pointing to new CLIs

### **Risk 2: Undiscovered Dependencies**
**Mitigation**:
- Thorough grep audit
- Archive file instead of delete (can restore)
- Test all workflows before removal

### **Risk 3: Documentation Gaps**
**Mitigation**:
- Complete command mapping
- Troubleshooting section
- Examples for common use cases

---

## 🚀 Timeline

**Day 1 (Oct 12)** - Planning & Audit:
- ✅ Create this manifest
- [ ] Complete Phase 1 audit
- [ ] Start Phase 2 documentation

**Day 2 (Oct 13)** - Documentation & Warning:
- [ ] Complete Phase 2 documentation
- [ ] Create Phase 3 migration guide  
- [ ] Add Phase 4 deprecation warning

**Day 3 (Oct 14)** - Verification:
- [ ] Complete Phase 5 quality audit update
- [ ] Complete Phase 6 verification testing
- [ ] Final review

**Day 4 (Oct 15)** - Removal:
- [ ] Phase 7 final removal
- [ ] Commit and close

---

## 💡 Lessons for Future

1. **Complete the job**: ADR-004 extracted commands but left monolith
2. **Documentation matters**: Update docs immediately after refactoring
3. **Deprecation strategy**: Always plan removal timeline
4. **Test the right layer**: Quality audit should test current architecture

---

## 📁 Related Documents

- `Projects/ACTIVE/adr-004-cli-layer-extraction.md` - Original extraction work
- `Projects/ACTIVE/AUDIT-SESSION-SUMMARY-2025-10-10.md` - Quality audit (tested wrong layer)
- `Projects/ACTIVE/quality-audit-bug-remediation-lessons-learned-2025-10-12.md` - Bug fixes (wrong layer)

---

**Created**: 2025-10-12 17:03 PDT  
**Status**: Planning phase  
**Next Action**: Begin Phase 1 audit  
**Target Completion**: 2025-10-15
