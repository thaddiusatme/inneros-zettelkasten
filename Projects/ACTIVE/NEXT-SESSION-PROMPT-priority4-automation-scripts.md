# Next Session Prompt: Priority 4 Automation Scripts Vault Config Migration

## The Prompt

Let's continue on branch **feat/vault-config-p1-vault-7-analytics-coordinator** for Priority 4: Automation Scripts Migration. We want to perform TDD framework with RED, GREEN, REFACTOR phases, followed by git commit and lessons learned documentation. This equals one iteration.

**Updated Execution Plan (GitHub Issue #45 - Phase 2 Priority 4)**

Context: Vault configuration centralization project at 94% completion (16/17 Priority 1-4 modules). Priority 3 coordinators are 6/6 complete (100%). Moving to Priority 4 automation scripts migration - 10+ scripts need vault config integration.

I'm following guidance in `.windsurf/rules/updated-development-workflow.md` (TDD methodology) and `.windsurf/rules/architectural-constraints.md` (critical path: complete Priority 4 automation scripts before final integration testing).

## Current Status

**Completed:**
- P1-VAULT-9: safe_image_processing_coordinator (20/20 tests, 45 min) ✅
- P1-VAULT-10: batch_processing_coordinator (18/18 tests, 35 min) ✅
- P1-VAULT-11: orphan_remediation_coordinator (19/19 tests, 30 min) ✅
- **Priority 3 Sprint: 6/6 coordinators complete (100%)** 🎉

**In progress:**
- P1-VAULT-12: Audit and migrate Priority 4 automation scripts to vault config
- Target scripts in `.automation/scripts/` directory

**Lessons from last iteration (P1-VAULT-11):**
- **Efficiency**: 30 minutes (fastest yet, 33% improvement from baseline)
- **Pattern**: vault_with_config fixture + integration test first = systematic success
- **Strategy**: Update base fixtures before individual tests (fixture composition)
- **Home Note discovery**: Check vault base before vault root
- **Success rate**: 19/19 tests (100%), zero regressions

## P0 — Critical/Unblocker (Complete Priority 4 Sprint - First Batch)

**P1-VAULT-12: Audit and prioritize automation scripts for migration**

1. **Identify scripts with hardcoded paths**:
   ```bash
   cd .automation/scripts
   grep -l "Inbox/\|Permanent Notes/\|Fleeting Notes/\|Literature Notes/" *.py
   ```

2. **Prioritize by usage frequency and complexity**:
   - High priority: Daily automation scripts (screenshot import, fleeting triage, weekly review)
   - Medium priority: Maintenance scripts (health checks, cleanup)
   - Low priority: One-time migration scripts

3. **Create migration plan document**:
   - List scripts requiring migration
   - Categorize by complexity (simple/medium/complex)
   - Estimate duration per script (~10-15 min each based on coordinator pattern)

**P1-VAULT-13: Migrate first batch of automation scripts (3-5 scripts)**

1. **Script migration pattern**:
   ```python
   # Add import
   from src.config.vault_config_loader import get_vault_config
   
   # In main() or processing function
   vault_config = get_vault_config(vault_base_dir)
   
   # Replace hardcoded paths
   # Before: inbox_dir = Path("Inbox")
   # After: inbox_dir = vault_config.inbox_dir
   ```

2. **Scripts to migrate first** (highest usage):
   - `fleeting_health_check.py` - Daily automation
   - `generate_weekly_review.py` - Weekly automation
   - `run_fleeting_triage.py` - Daily automation

3. **Testing approach**:
   - Manual testing with dry-run flags where available
   - Verify paths with both vault root and knowledge/ subdirectory layouts
   - Check script output for correct file paths

**Acceptance Criteria:**
- ✅ All Priority 4 scripts audited and categorized
- ✅ Migration plan document created with estimates
- ✅ First batch (3-5 scripts) successfully migrated
- ✅ All migrated scripts tested manually
- ✅ Zero regressions in script functionality
- ✅ Commit with clear documentation
- ✅ Lessons learned documented

## P1 — Continue Script Migration (Second Batch)

**P1-VAULT-14: Migrate remaining high-priority scripts**

Scripts likely needing migration:
- `automated_screenshot_import.sh` - Check if Python scripts it calls need migration
- `check_automation_health.py` - Health monitoring
- `process_onedrive_screenshots.py` - Screenshot processing
- `trigger_ai_processing.py` - AI workflow trigger

**Migration strategy:**
- Follow proven pattern from first batch
- Test each script individually
- Document any script-specific challenges
- Update any configuration files if needed

**P1-VAULT-15: Migrate medium/low priority scripts**

Remaining scripts:
- Cleanup scripts (one-time use, low priority)
- Maintenance scripts (occasional use)
- Legacy migration scripts (may archive instead of migrate)

**Acceptance Criteria:**
- ✅ All automation scripts using hardcoded paths migrated
- ✅ Manual testing confirms correct behavior
- ✅ Script documentation updated if needed
- ✅ Any deprecated scripts archived

## P2 — Final Testing & Documentation (Future session)

**Integration testing:**
- Run automation scripts with live vault directory structure
- Test with knowledge/Inbox vs Inbox behavior
- Verify cron jobs and scheduled automation still work

**Documentation updates:**
- Update `.automation/README.md` with vault config usage
- Update script-specific documentation
- Update main project docs (README.md, GETTING-STARTED.md)

**Final validation:**
- Complete vault config coverage report
- Verify all Phase 2 priorities complete
- Prepare for final PR review

## Task Tracker

- [In progress] P1-VAULT-12 - Audit automation scripts and create migration plan
- [Pending] P1-VAULT-13 - Migrate first batch (3-5 scripts)
- [Pending] P1-VAULT-14 - Migrate remaining high-priority scripts
- [Pending] P1-VAULT-15 - Migrate medium/low priority scripts
- [Pending] Integration testing with live vault
- [Pending] Final documentation updates
- [Pending] GitHub Issue #45 final completion

## TDD Cycle Plan

**Note**: Automation scripts may not need formal TDD with unit tests. Focus on:

**Red Phase (Audit):**
- Identify hardcoded paths in each script
- Document current behavior for comparison
- Note any script-specific edge cases

**Green Phase (Implementation):**
- Add `get_vault_config()` import
- Replace hardcoded paths with vault config attributes
- Ensure script accepts vault base directory parameter

**Refactor Phase (Testing & Documentation):**
- Test script manually with dry-run flags
- Verify behavior matches original
- Update script documentation if needed
- Add inline comments for vault config usage

## Next Action (for this session)

**Step 1: Audit automation scripts**
```bash
cd .automation/scripts
ls -la *.py *.sh
grep -rn "Inbox/\|Permanent Notes/\|Fleeting Notes/" *.py | head -20
```

**Step 2: Create migration plan**
Open new document: `Projects/ACTIVE/vault-config-priority4-script-migration-plan.md`

Document:
- List of scripts requiring migration
- Complexity categorization (simple/medium/complex)
- Prioritized order (high/medium/low usage)
- Estimated duration per script
- Dependencies or special considerations

**Step 3: Begin first script migration**
Select highest priority script (likely `fleeting_health_check.py` or `run_fleeting_triage.py`) and:
1. Add vault config import
2. Update path references
3. Test manually
4. Commit with clear message

Would you like me to start auditing the automation scripts and creating the migration plan now?

---

## Reference Information

**Branch**: `feat/vault-config-p1-vault-7-analytics-coordinator` (continue existing)  
**Expected Duration**: ~2-3 hours total for all scripts (10-15 min per script × 10-12 scripts)  
**Success Pattern**: Simple path replacement + manual testing = quick iterations  

**Previous Context:**
- Priority 3 complete: 6/6 coordinators migrated (79 tests, 100% success)
- Proven patterns: vault_with_config fixture, integration tests, systematic refactoring
- Efficiency gains: 45min → 35min → 30min (pattern mastery)

**Coordinator Migration Reference**: 
- `Projects/ACTIVE/vault-config-p1-vault-11-lessons-learned.md`
- `Projects/ACTIVE/vault-config-p1-vault-10-lessons-learned.md`
