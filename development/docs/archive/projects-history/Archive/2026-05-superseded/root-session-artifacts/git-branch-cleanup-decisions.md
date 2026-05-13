# Git Branch Cleanup Decisions - Issue #24

**Date**: 2025-11-09  
**Phase 1 Complete**: 99 merged branches deleted  
**Current**: 30 branches remaining (129 → 30)  
**Target**: <20 branches

---

## Phase 2: Unmerged Branch Analysis

### Category A: KEEP - Active/Recent (Last 7 days)
1. `feat/cli-integration-tests` (2025-11-09) - PR in progress
2. `feat/cli-migration-iteration-2-supervised-inbox` (2025-11-04) - Active CLI migration work

**Action**: Keep (2 branches)

---

### Category B: REVIEW - Recent but potentially mergeable (7-30 days)
3. `feat/vault-config-phase2-priority1` (2025-11-03)
4. `feat/vault-config-p1-vault-7-analytics-coordinator` (2025-11-03)
5. `feat/cli-migrate-automation-scripts-issue-39` (2025-11-03)
6. `feature/issue-31-screenshot-import-isolation-test` (2025-10-30)
7. `fix/issue-32-inbox-processing-isolation` (2025-10-31)
8. `fix/youtube-rate-limiting-issue-29` (2025-10-30)
9. `fix/screenshot-watcher-debounce-issue-30` (2025-10-30)
10. `fix/ci-workflow-timeout` (2025-10-28)
11. `chore/repo-hygiene-bundle-and-lifecycle-fixes` (2025-10-28)
12. `feat/pr-ci-workflow-quality-gates` (2025-10-27)
13. `fix/test-infrastructure-collection-p1` (2025-10-27)
14. `feat/automation-visibility-cli-tdd-iteration-1` (2025-10-26)
15. `fix/note-lifecycle-p0-completion` (2025-10-26)
16. `feat/evening-screenshots-cli-integration-tdd-2` (2025-10-23)
17. `feat/auto-promotion-subdirectory-support` (2025-10-23)
18. `housekeeping/knowledge-base-cleanup-phase2` (2025-10-22)
19. `housekeeping/cleanup-inventory-execution` (2025-10-22)
20. `housekeeping/cleanup-inventory-demo` (2025-10-22)
21. `housekeeping/cleanup-inventory-decision-log` (2025-10-22)
22. `housekeeping/cleanup-inventory-cli-review` (2025-10-22)
23. `housekeeping/cleanup-inventory-cli` (2025-10-22)

**Action**: Check for open issues/PRs, delete if no active work (21 branches)

---

### Category C: DELETE - Stale (>30 days old)
24. `feat/auto-promotion-workflow` (2025-10-16)
25. `feat/automation-file-watcher-tdd-iteration-2` (2025-10-07)
26. `feat/youtube-note-enhancer-tdd-iteration-1` (2025-10-06)
27. `p1/error-handling-recovery` (2025-08-19) - 3 months old!

**Action**: Delete immediately (4 branches)

---

## Recommended Deletions

### Safe to Delete (Stale, no recent activity)
```bash
git branch -D feat/auto-promotion-workflow
git branch -D feat/automation-file-watcher-tdd-iteration-2
git branch -D feat/youtube-note-enhancer-tdd-iteration-1
git branch -D p1/error-handling-recovery
```

### Bulk Delete October Housekeeping (completed work)
```bash
git branch -D housekeeping/knowledge-base-cleanup-phase2
git branch -D housekeeping/cleanup-inventory-execution
git branch -D housekeeping/cleanup-inventory-demo
git branch -D housekeeping/cleanup-inventory-decision-log
git branch -D housekeeping/cleanup-inventory-cli-review
git branch -D housekeeping/cleanup-inventory-cli
```

---

## Final Target State

**Keep (10-15 branches)**:
- `main` (production)
- `feat/cli-integration-tests` (active PR)
- `feat/cli-migration-iteration-2-supervised-inbox` (active)
- Recent fix branches with open issues (3-5)
- Recent feature branches under development (2-3)

**Total Reduction**: 129 → ~15 branches (88% reduction)
