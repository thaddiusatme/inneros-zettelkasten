# Next Session Prompt: Directory Organization Handler - TDD Iteration 10

**Date Created**: 2025-10-08 13:45 PDT  
**Status**: 📋 Ready to Execute  
**Priority**: P2 - High User Value  
**Estimated Duration**: 3 hours

---

## The Prompt

Let's create **Directory Organization Feature Handler - TDD Iteration 10** for the InnerOS Daemon Automation System. We want to automate fixing notes that are in the wrong directories (e.g., `type: permanent` in `Inbox/` instead of `Permanent Notes/`), following the established TDD methodology.

### Context

**Previous Work**: The Directory Organizer CLI exists with comprehensive functionality:
- **Location**: `development/src/utils/directory_organizer.py` (643 lines, 0% coverage in automation tests)
- **Test Suite**: `development/tests/unit/utils/test_directory_organizer.py` (20+ tests passing)
- **Features**: P0-1 Backup System, P0-2 Dry Run System, P0-3 Link Preservation, P1-1 Actual File Moves
- **Safety**: Complete backup/rollback, link preservation, type-based move planning

**The Gap**: Like YouTube before Iteration 9, this powerful CLI tool requires manual execution. Users must remember to run the directory organizer script periodically to fix misplaced notes.

**Reference Documentation**:
- System-retrieved memory: "Safety-First Directory Organization Foundation Complete" (2025-09-16)
- Integration pattern: Follow `YouTubeFeatureHandler` and `ScreenshotFeatureHandler` models
- Automation coverage target: 60% → 80% (4/5 workflows)

---

## Current System State

**Daemon Status** (Post-Iteration 9):
- ✅ 130/130 tests passing
- ✅ 11/11 core components complete
- ✅ 60% automation coverage (Screenshot, SmartLink, YouTube)
- ✅ Production-ready with systemd integration

**Directory Organizer CLI**:
- ✅ Comprehensive safety-first implementation
- ✅ 20+ tests with TDD methodology
- ❌ Not integrated into daemon (manual execution required)
- ❌ No health monitoring or metrics

**User Problem**: 
Notes with mismatched `type` field and directory location accumulate over time. Example: `type: permanent` notes remain in `Inbox/` instead of moving to `Permanent Notes/`. Currently requires manual CLI execution to fix.

---

## P0 — Critical Implementation

### Main Task: DirectoryOrganizationHandler Implementation

**Goal**: Automatically detect and fix directory mismatches on a scheduled basis (e.g., nightly runs)

**Implementation Strategy**:

#### 1. Handler Integration Pattern
Following established `YouTubeFeatureHandler` structure:

```python
# development/src/automation/feature_handlers.py (extend)

class DirectoryOrganizationHandler(FeatureHandler):
    """
    Handler for automatic directory organization.
    Runs on schedule (not file events) to fix misplaced notes.
    """
    
    def __init__(self, config: DirectoryOrgConfig):
        self.vault_path = Path(config.vault_path)
        self.organizer = DirectoryOrganizer(self.vault_path)
        self.dry_run = config.dry_run
        self.auto_fix = config.auto_fix
        
    def can_handle(self, event: FileEvent) -> bool:
        # Directory org runs on schedule, not file events
        return False
    
    def handle(self, event: FileEvent) -> HandlerResult:
        # Not used for scheduled handlers
        pass
    
    def process_scheduled(self) -> HandlerResult:
        """Run directory organization check and optionally fix."""
        # 1. Run dry-run scan
        # 2. If mismatches found and auto_fix=True, execute moves
        # 3. Return metrics
```

#### 2. Scheduled Execution (Not File-Based)
Unlike Screenshot/YouTube handlers that respond to file events, directory organization should run periodically:

**Cron Schedule Configuration**:
```yaml
# development/daemon_config.yaml (add)
directory_org_handler:
  enabled: true
  vault_path: ./knowledge
  schedule: "0 2 * * *"  # 2 AM daily
  dry_run: false  # Set true for testing
  auto_fix: true  # Automatically move files
  backup_enabled: true
```

#### 3. Integration with Existing DirectoryOrganizer
**Key Insight**: Don't rewrite the logic. The CLI's `DirectoryOrganizer` class is production-ready with:
- ✅ Type-based move planning
- ✅ Link preservation
- ✅ Backup/rollback
- ✅ Comprehensive testing

**Handler Responsibilities**:
1. Schedule management
2. Metrics collection
3. Health monitoring
4. Configuration integration
5. Logging

**DirectoryOrganizer Responsibilities** (unchanged):
1. File scanning
2. Move planning
3. Link updates
4. Safety operations

---

## P1 — Testing & Validation

### Test Strategy (15+ tests)

**Unit Tests** (`test_directory_org_handler.py`):
1. ✅ Handler initialization with config
2. ✅ `can_handle()` returns False (not event-driven)
3. ✅ `process_scheduled()` detects misplaced notes
4. ✅ Dry-run mode doesn't modify files
5. ✅ Auto-fix mode moves files correctly
6. ✅ Backup created before operations
7. ✅ Link preservation during moves
8. ✅ Metrics tracking (files scanned, moved, errors)
9. ✅ Health status reporting
10. ✅ Error handling (permission errors, missing dirs)

**Integration Tests**:
11. ✅ Config loading from `daemon_config.yaml`
12. ✅ Scheduler integration (cron timing)
13. ✅ Health endpoint reports handler status
14. ✅ Metrics exported to Prometheus format

**Real Data Validation**:
15. ✅ Test on user's vault with 31 known misplaced files

---

## P2 — Configuration & Documentation

### Configuration Schema

```yaml
directory_org_handler:
  enabled: true                    # Enable handler
  vault_path: ./knowledge          # Vault root directory
  schedule: "0 2 * * *"            # Cron schedule (2 AM daily)
  dry_run: false                   # Preview without changes
  auto_fix: true                   # Automatically move files
  backup_enabled: true             # Create backup before moves
  min_confidence: 0.9              # Minimum confidence for auto-moves
```

### Health Monitoring

Handler should report:
- **Status**: healthy/unhealthy
- **Last Run**: timestamp of last execution
- **Notes Scanned**: total files checked
- **Mismatches Found**: count of misplaced notes
- **Files Moved**: successful moves
- **Errors**: failures encountered

### Success Criteria

- [ ] Handler integrated into daemon architecture
- [ ] Scheduled execution working (cron-based)
- [ ] 15+ tests passing with comprehensive coverage
- [ ] Dry-run mode validates without modifying vault
- [ ] Auto-fix mode successfully organizes misplaced notes
- [ ] Health monitoring active
- [ ] Metrics tracked in `/health` and `/metrics` endpoints
- [ ] Config validation prevents unsafe operations
- [ ] Documentation updated in `FEATURE-HANDLERS.md`
- [ ] ADR-001 compliant (<500 LOC per file)

---

## Acceptance Criteria

### Functional Requirements
- [ ] Daemon detects misplaced notes on schedule (not file events)
- [ ] Handler respects `dry_run` and `auto_fix` config
- [ ] Backup created before any file operations
- [ ] Links preserved during moves (wiki-link integrity)
- [ ] Real vault validation: 31 known misplaced notes fixed
- [ ] No false positives (correctly placed notes untouched)

### Technical Requirements
- [ ] 130/130 existing tests still passing
- [ ] 15+ new tests for directory org handler
- [ ] ADR-001 compliance: all new files <500 LOC
- [ ] Zero regressions in existing handlers
- [ ] Scheduled execution framework established

### Documentation Requirements
- [ ] `FEATURE-HANDLERS.md` updated with directory org pattern
- [ ] Lessons learned document created
- [ ] Roadmap updated: automation coverage 60% → 80%
- [ ] Config example in `daemon_config.yaml`

---

## Technical Decisions

### Why Scheduled (Not Event-Driven)?

**Event-driven** (like Screenshot/YouTube):
- Pros: Immediate response to file changes
- Cons: Triggers on every note save, excessive processing

**Scheduled** (proposed):
- Pros: Batch processing, predictable timing, less resource intensive
- Cons: Delay between misplacement and fix (acceptable for this use case)

**Decision**: Scheduled execution is appropriate because:
1. Directory mismatches are **not urgent** (can wait hours)
2. Batch processing is **more efficient** than per-file checks
3. **Predictable timing** (nightly) vs unpredictable file events
4. Aligns with weekly review workflow

### Integration with Existing Code

**Pattern**: Composition over reimplementation
- Handler wraps `DirectoryOrganizer` (don't duplicate logic)
- Reuse tested CLI functionality
- Handler adds: scheduling, metrics, health monitoring

---

## Deliverables

### Code Files
1. **Handler Implementation** (NEW):
   - `development/src/automation/feature_handlers.py` - Add `DirectoryOrganizationHandler` class (~150 LOC)
   
2. **Configuration** (MODIFY):
   - `development/src/automation/config.py` - Add `DirectoryOrgConfig` dataclass (~30 LOC)
   - `development/daemon_config.yaml` - Add `directory_org_handler` section

3. **Tests** (NEW):
   - `development/tests/unit/automation/test_directory_org_handler.py` (~15 tests, ~200 LOC)

4. **Documentation** (UPDATE):
   - `development/docs/FEATURE-HANDLERS.md` - Document scheduled handler pattern
   - `Projects/COMPLETED-2025-10/directory-org-handler-tdd-iteration-10-lessons-learned.md`

### Metrics Updates
- Automation coverage: 60% → 80% (4/5 workflows)
- Test count: 130 → 145+ tests
- Weekly time savings: ~70 min → ~75 min (+5 min from auto-organization)

---

## Next Actions

### Immediate (This Session)
1. Create branch: `feat/directory-org-handler-tdd-iteration-10`
2. **RED Phase**: Write 15+ failing tests
3. **GREEN Phase**: Minimal implementation to pass tests
4. **REFACTOR Phase**: Extract utilities, improve architecture
5. **COMMIT Phase**: Git commit with detailed message
6. **LESSONS Phase**: Document insights

### Follow-up (Future Sessions)
- **Iteration 11**: Fleeting Triage Handler (3.5 hours)
- **Iteration 12**: Production Hardening - Log rotation, alerting (2 hours)

---

## Key Files to Reference

**Existing Implementation**:
- `development/src/utils/directory_organizer.py` - Proven CLI logic
- `development/tests/unit/utils/test_directory_organizer.py` - Test patterns

**Handler Patterns**:
- `development/src/automation/feature_handlers.py` - `YouTubeFeatureHandler`, `ScreenshotFeatureHandler`
- `development/tests/unit/automation/test_youtube_handler.py` - Test structure

**Scheduler Integration**:
- `development/src/automation/scheduler.py` - Cron scheduling
- `development/src/automation/daemon.py` - Daemon lifecycle

---

## TDD Workflow Reference

Following `.windsurf/workflows/complete-feature-development.md`:

**Phase 1 - RED**: Write comprehensive failing tests
- Test handler initialization
- Test scheduled processing
- Test dry-run behavior
- Test auto-fix execution
- Test error handling

**Phase 2 - GREEN**: Minimal working implementation
- DirectoryOrganizationHandler class
- Integration with DirectoryOrganizer
- Config loading
- Metrics collection

**Phase 3 - REFACTOR**: Production-ready architecture
- Extract utility methods if >500 LOC
- Improve error messages
- Optimize performance
- Enhance logging

**Phase 4 - COMMIT & LESSONS**: Documentation
- Git commit with detailed message
- Lessons learned document
- Update roadmap and metrics

---

**Ready to execute**: This prompt provides complete specification for TDD Iteration 10, building on proven patterns from Iterations 1-9.
