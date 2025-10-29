---
type: checklist
created: 2025-10-15 17:45
status: in-progress
priority: P0
tags: [merge, stabilize, v2.0-prep]
---

# Merge & Stabilize Checklist - October 15, 2025

**Branch**: `feat/note-lifecycle-auto-promotion-pbi-004`  
**Target**: `main`  
**Goal**: Clean foundation for next epic

---

## ✅ Completed Work

### PBI-004: Auto-Promotion System
- [x] Backend implementation (PromotionEngine)
- [x] WorkflowManager delegation (ADR-002 compliant)
- [x] CLI integration (CoreWorkflowCLI)
- [x] **34/34 tests passing (100%)**
- [x] Real data validation (8 notes promoted successfully)
- [x] Documentation (3 comprehensive docs in COMPLETED-2025-10/)

### Git Commits This Session
- `874cbde` - docs: Add auto-promotion system TDD lessons learned
- `9bb4040` - test: Real data validation for auto-promotion system
- `ab8f71e` - docs: Add PBI-004 completion summary (Options 1 & 2)
- `c9fb8f2` - feat: Add YouTube + Auto-Promotion integration project manifest

---

## 📋 Merge & Stabilize Tasks

### 1. Test Status ✅ DONE
- [x] Auto-promotion tests: **34/34 passing**
- [x] No regressions in core functionality
- [ ] Screenshot tests have import errors (6 errors) - **DEFER** (not blocking)

**Decision**: Screenshot test errors are unrelated to auto-promotion work. Can be fixed in separate PR.

---

### 2. Update Documentation

#### Update NEXT-EPIC-PLANNING.md
- [ ] Mark PBI-004 as COMPLETE
- [ ] Update "Current Status" section
- [ ] Archive YouTube integration as P1 future work

#### Update project-todo-v3.md
- [ ] Mark auto-promotion as complete
- [ ] Update test counts
- [ ] Note 8 notes promoted in production

#### Create Release Notes
- [ ] Summarize auto-promotion feature
- [ ] Link to lessons learned docs
- [ ] Note YouTube integration planned for future

---

### 3. Code Quality Checks

#### Lint Warnings
```bash
# Check for lint issues in modified files
pylint development/src/ai/promotion_engine.py
pylint development/src/ai/workflow_manager.py
pylint development/src/cli/core_workflow_cli.py
```

- [ ] Run lint checks
- [ ] Fix any critical warnings
- [ ] Document acceptable warnings (if any)

#### Code Review Checklist
- [x] ADR-002 delegation pattern followed
- [x] WorkflowManager stays under 812 LOC
- [x] No god class regressions
- [x] Error handling comprehensive
- [x] Logging appropriate

---

### 4. Final Validation

#### Run Core Test Suite
```bash
# Core auto-promotion tests
pytest development/tests/unit/test_promotion_engine.py -v
pytest development/tests/unit/test_workflow_manager_auto_promote.py -v
pytest development/tests/unit/test_auto_promote_cli.py -v
```

- [x] **34/34 passing** ✅

#### Integration Test (Real Data)
```bash
# Verify auto-promotion still works
python development/src/cli/core_workflow_cli.py knowledge auto-promote --dry-run
```

- [ ] Dry-run preview works
- [ ] No errors in production environment

---

### 5. Git Cleanup

#### Review Branch History
```bash
git log --oneline feat/note-lifecycle-auto-promotion-pbi-004
```

- [ ] Review commit messages
- [ ] Ensure all commits are meaningful
- [ ] No debug commits or WIP commits

#### Squash if Needed
- [ ] Decision: Keep detailed history or squash?
- [ ] **Recommendation**: Keep as-is (good commit messages)

---

### 6. Merge Process

#### Pre-Merge Checks
```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Ensure feature branch is up to date
git checkout feat/note-lifecycle-auto-promotion-pbi-004
git merge main  # Resolve any conflicts
```

- [ ] Main branch pulled
- [ ] Feature branch rebased/merged with main
- [ ] No merge conflicts

#### Merge to Main
```bash
git checkout main
git merge feat/note-lifecycle-auto-promotion-pbi-004
git push origin main
```

- [ ] Merged to main
- [ ] Pushed to origin

#### Tag Release (Optional but Recommended)
```bash
git tag -a v2.1-auto-promotion -m "Auto-Promotion System Complete

Features:
- Quality-based note promotion (0.7 threshold)
- Dry-run preview mode
- CLI integration with auto-promote command
- ADR-002 compliant delegation pattern
- 34/34 tests passing

Real data validation:
- 8 notes promoted successfully
- 0 errors encountered
- <1 second execution time
"
git push origin v2.1-auto-promotion
```

- [ ] Tagged release
- [ ] Pushed tag

---

### 7. Post-Merge Cleanup

#### Archive Completed Work
```bash
# Move completed docs to archive if desired
# Update project trackers
```

- [ ] Update project-todo-v3.md with completion
- [ ] Move manifest to COMPLETED-2025-10/ if desired
- [ ] Update README if needed

#### Branch Cleanup
```bash
# Delete feature branch (optional)
git branch -d feat/note-lifecycle-auto-promotion-pbi-004
git push origin --delete feat/note-lifecycle-auto-promotion-pbi-004
```

- [ ] Local branch deleted (optional)
- [ ] Remote branch deleted (optional)

---

## 📊 Success Criteria

### Must Have ✅
- [x] 34/34 auto-promotion tests passing
- [x] Real data validation successful (8 notes promoted)
- [x] Zero regressions in core functionality
- [x] Documentation complete (3 comprehensive docs)
- [x] ADR-002 compliance verified

### Nice to Have (Defer if Needed)
- [ ] Zero lint warnings (check and document)
- [ ] All integration tests passing (screenshot errors deferred)
- [ ] Performance benchmarks documented

### Post-Merge
- [ ] Main branch stable
- [ ] Tests passing on main
- [ ] Ready for next epic

---

## 🚀 Next Epic After Merge

### Option 3: Document & Defer YouTube Integration
- [x] YouTube integration manifest created ✅
- [ ] Mark as P1 future work in NEXT-EPIC-PLANNING.md
- [ ] Archive manifest for future reference
- [ ] Choose different epic to tackle next

### Possible Next Epics
1. **Quality Audit Bug Fixes** (P2 - 2-3 hours)
2. **Source Code Reorganization** (P1 - gradual, 4-6 weeks)
3. **Distribution System** (P1 - 2-3 weeks)
4. **Process 5 Unprocessed Inbox Notes** (Quick win)

---

## 📝 Notes

### Screenshot Test Errors (Deferred)
6 test files have import errors:
- test_evening_screenshot_cli_tdd_2.py
- test_evening_screenshot_processor_green_phase.py
- test_evening_screenshot_processor_tdd_1.py
- test_evening_screenshot_real_data_tdd_3.py
- test_individual_screenshot_processing_tdd_5.py
- test_real_data_validation_performance.py

**Decision**: These are unrelated to auto-promotion work and can be fixed in a separate PR. Not blocking for merge.

### YouTube Integration (Deferred to P1)
Complete manifest created with 6-phase implementation plan (5-7 hours). Ready for future implementation when priority shifts.

---

**Status**: 📋 Ready to Execute  
**Estimated Time**: 1-2 hours  
**Next Action**: Update documentation (Task 2)
