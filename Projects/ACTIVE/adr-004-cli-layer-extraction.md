# Architecture Decision Record: CLI Layer Extraction

**Date**: 2025-10-10  
**Status**: ✅ ACCEPTED (October 2025)  
**Context**: Monolithic CLI crisis - workflow_demo.py at 2,074 LOC blocks clean architecture  
**Decision**: Extract remaining 18 commands to dedicated CLIs, deprecate workflow_demo.py  
**Related**: ADR-001 (WorkflowManager refactoring COMPLETE), workflow-demo-deprecation-plan.md  

---

## Decision Drivers

- **ADR-001 Only Half Complete**: Backend refactored (4 managers ✅), CLI layer still monolithic (❌)
- **CLI God Class**: workflow_demo.py at 2,074 LOC with 25+ commands violates single responsibility
- **28% Extraction Complete**: 7/25 commands already extracted to dedicated CLIs, pattern proven
- **Quality Audit Impact**: Found bugs in monolithic CLI that should be in dedicated CLIs
- **Architecture Debt**: Backend is clean, CLI layer remains coupled and hard to maintain
- **Distribution Ready**: v0.1.0-alpha released but still pointing users to monolithic CLI

---

## Considered Options

### Option 1: Keep workflow_demo.py as Convenience Wrapper
**Description**: Accept monolith, use as orchestrator for dedicated CLIs

**Pros**:
- No immediate CLI extraction effort
- Backward compatibility for existing scripts
- Single entry point for all commands

**Cons**:
- Doesn't address root cause (god class)
- Still 2,074 LOC to maintain
- Confuses users about which CLI to use
- Blocks clean architecture completion
- Quality audit found bugs here instead of dedicated CLIs

**Impact**: Existing code continues working, technical debt compounds

### Option 2: Gradual Extraction (Current State)
**Description**: Continue slow extraction as time permits (28% complete)

**Pros**:
- Already started, some commands extracted
- No deadline pressure
- Can extract based on priority

**Cons**:
- **3+ months stalled at 28%** - no progress since initial extraction
- Partial solution maintains confusion
- Users don't know which CLI is "correct"
- Quality audits test wrong code
- Technical debt accumulating

**Impact**: Current trajectory = 10+ months to completion

### Option 3: Complete CLI Extraction Sprint ✅ **SELECTED**
**Description**: 2-week focused sprint to extract remaining 18 commands, deprecate workflow_demo.py

**Pros**:
- **Completes ADR-001 vision** - backend + frontend architecture clean
- **Proven pattern** - 7 commands already extracted successfully
- **Fast timeline** - 2 weeks vs. 10+ months gradual
- **Clear endpoint** - workflow_demo.py officially deprecated
- **Documentation clarity** - README/guides point to correct CLIs
- **Quality improvement** - Future bugs found in right place
- **Follows TDD** - Extract → Test → Validate for each command

**Cons**:
- **2-week effort** blocks other features
- **18 commands** need extraction and testing
- **Documentation updates** across README, CLI-REFERENCE, guides
- **Backward compatibility** - need adapter/wrapper for old scripts

**Impact**: Clean architecture complete, clear path forward

### Option 4: Build TUI Instead, Bypass CLI Layer
**Description**: Skip CLI extraction, go straight to retro TUI

**Pros**:
- TUI provides better UX than CLI
- Can build on clean backend (4 managers)
- Avoids CLI extraction work entirely

**Cons**:
- **Doesn't solve the problem** - CLI still exists and users will find it
- **README/docs still point to workflow_demo.py** - confusion continues
- **Distribution users** will hit monolith bugs
- **Technical debt unpaid** - kicking can down road
- **TUI doesn't replace CLI** - need both for automation

**Impact**: Problem deferred, not solved

---

## Decision

We chose **Option 3: Complete CLI Extraction Sprint** because:

1. **Completes ADR-001 Architecture** - Backend refactored (✅), CLI layer next logical step
2. **Proven Pattern** - 7/25 commands already extracted, pattern works, just need to finish
3. **Fast Timeline** - 2 weeks focused sprint vs. 10+ months gradual drift
4. **Unblocks Quality** - Future audits test correct architecture, bugs found in right place
5. **User Clarity** - Documentation points to dedicated CLIs, no confusion
6. **Distribution Ready** - Clean architecture for public release
7. **Enables TUI** - TUI can call dedicated CLIs, not monolith

---

## Architecture

### Current State (28% Complete)
```
workflow_demo.py (2,074 LOC, 25 commands)
    ├── ✅ YouTube Processing (2 cmds) → youtube_cli.py
    ├── ✅ Tag Enhancement (3 cmds) → advanced_tag_enhancement_cli.py  
    ├── ✅ Review Notes (3 cmds) → notes_cli.py
    ├── ✅ Performance (1 cmd) → real_data_performance_cli.py
    ├── ❌ Weekly Review (2 cmds) → needs extraction
    ├── ❌ Fleeting Notes (3 cmds) → needs extraction
    ├── ❌ Safe Workflow (5 cmds) → needs extraction
    ├── ❌ Core Workflow (5 cmds) → needs extraction
    ├── ❌ Backup (3 cmds) → needs extraction
    └── ❌ Others (reading intake, connections, screenshots)
```

### Target State (100% Complete)
```
Dedicated CLIs (modular, focused, <400 LOC each)
    ├── youtube_cli.py (372 LOC) ✅
    ├── advanced_tag_enhancement_cli.py ✅
    ├── notes_cli.py ✅
    ├── real_data_performance_cli.py ✅
    ├── weekly_review_cli.py (NEW)
    ├── fleeting_cli.py (NEW)
    ├── workflow_cli.py (NEW - safe workflows)
    ├── core_workflow_cli.py (NEW)
    ├── backup_cli.py (NEW)
    └── [others as needed]

workflow_demo.py → DEPRECATED (archived)
inneros (wrapper) → routes to dedicated CLIs
```

---

## Implementation

### Phase 1: High-Priority Extractions (Week 1: Oct 11-18)

**P1.1: Weekly Review CLI** (2 commands, 1 day)
- [ ] Extract `--weekly-review` → `weekly_review_cli.py`
- [ ] Extract `--enhanced-metrics` → same CLI
- [ ] Uses: AnalyticsManager (ADR-001)
- [ ] Test: Compare output with workflow_demo.py
- [ ] Update: CLI-REFERENCE.md examples

**P1.2: Fleeting Notes CLI** (3 commands, 1 day)
- [ ] Extract `--fleeting-health` → `fleeting_cli.py`
- [ ] Extract `--fleeting-triage` → same CLI
- [ ] Extract fleeting note processing → same CLI
- [ ] Uses: AnalyticsManager, CoreWorkflowManager
- [ ] Test: Run full fleeting note lifecycle
- [ ] Fix: Bug #5 (analyze_fleeting_notes) during extraction

**P1.3: Safe Workflow CLI** (5 commands, 2 days)
- [ ] Extract directory organization commands → `workflow_cli.py`
- [ ] Uses: DirectoryOrganizer (already exists!)
- [ ] Quick win: Utilities already built, just wire CLI
- [ ] Test: Dry-run and actual file operations
- [ ] Update: GETTING-STARTED.md examples

**P1.4: Backup CLI** (3 commands, 1 day)
- [ ] Extract backup operations → `backup_cli.py`
- [ ] Extract list/prune commands → same CLI
- [ ] Test: Backup creation, listing, pruning
- [ ] Update: Safety documentation

### Phase 2: Core Workflow & Others (Week 2: Oct 19-25)

**P2.1: Core Workflow CLI** (5 commands, 2 days)
- [ ] Extract inbox processing → `core_workflow_cli.py`
- [ ] Extract note promotion → same CLI
- [ ] Uses: CoreWorkflowManager, AIEnhancementManager
- [ ] Test: End-to-end workflow (inbox → permanent)
- [ ] Update: knowledge-starter-pack examples

**P2.2: Remaining Commands** (3 days)
- [ ] Reading intake → reading_cli.py (if still used)
- [ ] Connections → connections_cli.py (already exists, verify)
- [ ] Screenshots → screenshot_cli.py (already exists, verify)
- [ ] Orphaned notes → analytics_cli.py or weekly_review_cli.py
- [ ] Any other stragglers

**P2.3: Deprecation & Cleanup** (2 days)
- [ ] Add deprecation warning to workflow_demo.py
- [ ] Create workflow_demo_legacy.py in Archive/
- [ ] Update README.md (remove workflow_demo examples)
- [ ] Update CLI-REFERENCE.md (all commands use dedicated CLIs)
- [ ] Update QUICK-REFERENCE.md
- [ ] Update GETTING-STARTED.md
- [ ] Update distribution docs
- [ ] Test: Verify all examples in docs work with dedicated CLIs

---

## Consequences

### Positive
- **Architecture Complete**: ADR-001 vision fully realized (backend + frontend clean)
- **Clear User Path**: Documentation points to single correct CLI per feature
- **Maintainable**: Each CLI <400 LOC, focused, easy to understand
- **Testable**: Dedicated test suite per CLI, isolated failures
- **Quality Audits**: Test correct architecture, find bugs in right place
- **Distribution Ready**: Clean public release with clear commands
- **TUI Foundation**: Retro TUI can call dedicated CLIs, not monolith

### Negative
- **2-Week Timeline**: Blocks TUI development until CLI extraction complete
- **18 Commands**: Each needs extraction, testing, documentation
- **Breaking Changes**: Old scripts calling workflow_demo.py need updates
- **Documentation Churn**: Update 5+ docs (README, CLI-REF, QUICK-REF, etc.)
- **Learning Curve**: Users need to learn new command structure

### Neutral
- **More Files**: 10+ CLIs vs. 1 monolith (but each simpler)
- **Command Changes**: `python3 workflow_demo.py --cmd` → `./inneros category cmd`
- **Backward Compat**: Keep workflow_demo.py with deprecation warning for 1 month

### Risks

#### Risk 1: Extraction Causes Regressions
- **Likelihood**: Low (pattern proven with 7 commands)
- **Impact**: Medium (some commands may break)
- **Mitigation**:
  - TDD approach: Extract → Test → Compare with old
  - Run both old and new side-by-side during validation
  - Comprehensive integration tests
  - User acceptance testing on key workflows

#### Risk 2: Timeline Slips (2 weeks → 4 weeks)
- **Likelihood**: Medium (18 commands is significant)
- **Impact**: High (delays TUI development)
- **Mitigation**:
  - Prioritize P1 commands (weekly review, fleeting, workflows)
  - Quick wins first (safe workflow, backup use existing utils)
  - Timebox each extraction to 1 day max
  - Defer low-priority commands if needed

#### Risk 3: User Confusion During Transition
- **Likelihood**: Medium (breaking changes always confuse)
- **Impact**: Medium (support burden)
- **Mitigation**:
  - Clear migration guide in docs
  - Deprecation warnings in workflow_demo.py
  - Keep old CLI working with warnings for 1 month
  - Update all examples proactively

#### Risk 4: Bugs Found in Dedicated CLIs
- **Likelihood**: High (moving code always surfaces issues)
- **Impact**: Medium (need bug fixes during extraction)
- **Mitigation**:
  - Fix bugs in managers (ADR-001), not CLI layer
  - Comprehensive testing before deprecation
  - Bug fix sprint after extraction if needed

---

## Success Criteria

### Definition of Done
- [ ] All 25 commands extracted to dedicated CLIs
- [ ] workflow_demo.py has deprecation warning
- [ ] All documentation updated (README, CLI-REF, QUICK-REF, GETTING-STARTED)
- [ ] All examples in docs work with dedicated CLIs
- [ ] Integration tests pass for all extracted commands
- [ ] Quality audit re-run shows bugs in correct files
- [ ] Distribution docs point to dedicated CLIs

### Metrics
**Before** (workflow_demo.py):
- 2,074 lines of code
- 25+ commands in single file
- Cognitive load: HIGH
- Testability: HARD (coupled)
- Maintainability: LOW

**After** (dedicated CLIs):
- ~400 LOC per CLI
- 5-10 focused CLIs
- Cognitive load: LOW
- Testability: EASY (isolated)
- Maintainability: HIGH

### Validation Checkpoints
- **Day 3 (Oct 13)**: Weekly review + fleeting CLIs extracted and tested
- **Day 5 (Oct 15)**: Safe workflow + backup CLIs extracted  
- **Day 10 (Oct 20)**: Core workflow + remaining commands extracted
- **Day 14 (Oct 24)**: Documentation complete, workflow_demo.py deprecated
- **Month 1 (Nov 10)**: Quality audit re-run validates clean architecture

---

## Related Decisions

### Builds On
- **ADR-001**: WorkflowManager Refactoring (backend complete, CLI next)
- **workflow-demo-deprecation-plan.md**: Detailed extraction status (28% complete)
- **workflow-demo-extraction-status.md**: Command-by-command tracking

### Impacts
- **Quality Audit**: Re-run after extraction to validate bugs in correct files
- **Bug Fix Sprint**: Pause current sprint, fix manager bugs only
- **TUI Development**: Blocked until CLI extraction complete
- **Documentation**: Major updates across 5+ docs
- **Distribution**: Update v0.1.0-alpha docs to point to dedicated CLIs

### Supersedes
- **Gradual Extraction**: Abandon "extract when convenient" approach

---

## Timeline

**Start Date**: 2025-10-11 (Tomorrow)  
**Target Completion**: 2025-10-25 (2 weeks)  
**Owner**: Development Team  
**Priority**: P0 - Blocks TUI development, clean architecture completion

**Week 1 (Oct 11-18)**:
- Days 1-2: Weekly review CLI + fleeting CLI
- Days 3-4: Safe workflow CLI + backup CLI  
- Day 5: Integration testing, bug fixes

**Week 2 (Oct 19-25)**:
- Days 1-2: Core workflow CLI
- Days 3-4: Remaining commands (reading, connections, etc.)
- Days 5-6: Documentation updates, deprecation, final testing

---

## Implementation Progress

### Extraction Status: 72% Complete (18/25 commands when counting wrapped)

**✅ Phase 1 Complete (Pre-ADR)**:
- YouTube CLI (2 commands) → `youtube_cli.py`
- Tag Enhancement CLI (3 commands) → `advanced_tag_enhancement_cli.py`
- Review Notes CLI (3 commands) → `notes_cli.py`
- Performance CLI (1 command) → `real_data_performance_cli.py`

**✅ Iteration 1 Complete (2025-10-10)**:
- Weekly Review CLI (2 commands) → `weekly_review_cli.py`
  - Command: `weekly-review` (checklist generation)
  - Command: `enhanced-metrics` (comprehensive metrics)
  - LOC: 340 (under 400 target)
  - Tests: 4/4 passing
  - Commit: `600672d`
  - Lessons: `adr-004-iteration-1-weekly-review-lessons-learned.md`

**✅ Iteration 2 Complete (2025-10-10)**:
- Fleeting Notes CLI (3 commands) → `fleeting_cli.py` + `fleeting_formatter.py`
  - Command: `fleeting-health` (health report with age analysis)
  - Command: `fleeting-triage` (AI-powered quality assessment)
  - LOC: 350 (CLI) + 227 (formatter) = 577 total
  - Tests: 4/4 passing (includes Bug #3 validation)
  - Commit: `1522ed2`
  - Lessons: `adr-004-iteration-2-fleeting-lessons-learned.md`
  - **Bug #3 FIXED**: AttributeError in fleeting_health (bypassed buggy adapter)

**✅ Iteration 3+ Complete (2025-10-10)**:
- Safe Workflow CLI (6 commands) → `safe_workflow_cli.py` + `safe_workflow_formatter.py`
  - Command: `process-inbox-safe` (inbox with image preservation)
  - Command: `batch-process-safe` (batch with safety guarantees)
  - Command: `performance-report` (performance metrics)
  - Command: `integrity-report` (image integrity monitoring)
  - Command: `backup` (timestamped vault backup)
  - Command: `list-backups` (backup inventory)
  - LOC: 517 (CLI) + 131 (formatter) = 648 total
  - Tests: 10/10 passing
  - Commit: `0400109`
  - Lessons: `adr-004-iteration-3-safe-workflow-lessons-learned.md`
  - **Unique**: Wrapped pre-existing safe_workflow_cli_utils.py (464 LOC from TDD Iteration 4)
  - **Velocity**: 3.3x faster (1 hour vs 3-4 hours) due to existing utilities

**🔄 Next: Iteration 4+ (2025-10-11+)**:
- Remaining workflow commands (7 commands estimated)
  - Core workflow operations
  - Reading intake pipeline
  - Miscellaneous utilities

**📋 Remaining Work**:
- Safe Workflow CLI (5 commands) → `workflow_cli.py`
- Backup CLI (3 commands) → `backup_cli.py`
- Core Workflow CLI (5 commands) → `core_cli.py`
- Miscellaneous (5 commands) → TBD

---

## Updates

### [2025-10-10] - Iteration 3+ Complete: Safe Workflow CLI (Wrapping Existing Utilities)
**Extracted**: 6 safe workflow commands (process-inbox-safe, batch-process-safe, performance-report, integrity-report, backup, list-backups)  
**Files**: `development/src/cli/safe_workflow_cli.py` (517 LOC) + `safe_workflow_formatter.py` (131 LOC)  
**Tests**: 10/10 passing (RED → GREEN → REFACTOR complete)  
**Unique Discovery**: Wrapped pre-existing safe_workflow_cli_utils.py (464 LOC) from TDD Iteration 4  
**Progress**: 72% complete (18/25 commands when counting wrapped)  
**Duration**: 1 hour actual vs 3-4 hours estimated (3.3x faster!)  
**Pattern**: Wrapping existing utilities dramatically faster than building from scratch  
**Learning**: Always check for existing utilities first - saved 3-4 hours  
**Next**: Remaining workflow commands on 2025-10-11+ (check for utilities first)

### [2025-10-10] - Iteration 2 Complete: Fleeting Notes CLI + Bug #3 Fix
**Extracted**: `fleeting-health` and `fleeting-triage` commands  
**Files**: `development/src/cli/fleeting_cli.py` (350 LOC) + `fleeting_formatter.py` (227 LOC)  
**Tests**: 4/4 passing (RED → GREEN → REFACTOR complete)  
**Bug #3 Fixed**: AttributeError in fleeting_health - used WorkflowManager directly (bypassed buggy adapter)  
**Progress**: 44% complete (11/25 commands extracted)  
**Duration**: 2 hours actual vs 2-3 hours estimated  
**Pattern**: Formatter extraction proven again (2nd CLI to need it)  
**Learning**: Bug fixes belong in dedicated CLIs, not monolith  
**Next**: Safe workflow CLI on 2025-10-11+ (estimated 3-4 hours)

### [2025-10-10] - Iteration 1 Complete: Weekly Review CLI
**Extracted**: `weekly-review` and `enhanced-metrics` commands  
**File**: `development/src/cli/weekly_review_cli.py` (340 LOC)  
**Tests**: 4/4 passing (RED → GREEN → REFACTOR complete)  
**Progress**: 32% complete (8/25 commands extracted)  
**Duration**: 1.5 hours actual vs 2-4 hours estimated  
**Learning**: TDD cycle faster than expected, extraction patterns proven  
**Next**: Fleeting notes CLI on 2025-10-11 (includes Bug #3 fix)

### [2025-10-10] - Status: Accepted
**Reason**: Quality audit found bugs in monolithic CLI; ADR-001 only completed backend  
**Impact**: Architectural pivot - prioritize CLI extraction over bug fixes/TUI  
**Decision**: User approved 2-week sprint to complete clean architecture  
**Action Required**: Begin extraction sprint Monday Oct 11 with weekly review CLI  
**Branch**: Create `feat/adr-004-cli-extraction` from current branch

---

## References

### Documentation
- **Deprecation Plan**: `Projects/Archive/workflow-demo-deprecation-plan.md` (28% status)
- **Extraction Status**: `Projects/Archive/workflow-demo-extraction-status.md` (command tracking)
- **ADR-001**: `Projects/ACTIVE/adr-001-workflow-manager-refactoring.md` (backend complete)
- **Quality Audit**: `Projects/ACTIVE/audit-report-2025-10-10.md` (found CLI bugs)

### Code Analysis
- **workflow_demo.py**: 2,074 LOC, 25+ commands (monolithic)
- **Existing Dedicated CLIs**: youtube_cli.py (372 LOC), advanced_tag_enhancement_cli.py, notes_cli.py
- **Backend Managers**: CoreWorkflowManager, AnalyticsManager, AIEnhancementManager, ConnectionManager (ADR-001)

### Team Decisions
- Quality audit (Oct 10) found bugs in wrong architectural layer
- User confirmed: "I don't want monolithic code per ADR-001"
- Decision: Complete CLI extraction before continuing feature work
- Timeline: 2 weeks acceptable to complete architecture

---

**This ADR completes the vision started in ADR-001, delivering a fully clean architecture at both backend and frontend layers.**
