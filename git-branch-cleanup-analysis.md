# Git Branch Cleanup Analysis - Issue #24

**Date**: 2025-11-09  
**Current State**: 129 branches (target: <20)  
**Merged into main**: 101 branches (safe to delete)  
**Strategy**: Phased cleanup with safety verification

---

## Phase 1: Delete Merged Branches (Safe - 101 branches)

These branches are already merged into main and can be safely deleted.

### Command
```bash
# List all merged branches (excluding main)
git branch --merged main | grep -v "^\*" | grep -v "main"

# Delete all merged branches locally
git branch --merged main | grep -v "^\*" | grep -v "main" | xargs git branch -d

# After local cleanup, delete from remote
git push origin --delete $(git branch --merged main | grep -v "^\*" | grep -v "main" | tr -d ' ')
```

**Expected Result**: 129 → ~28 branches

---

## Phase 2: Identify Unmerged Active Branches (Keep)

Branches with active work or pending PRs:
- `feat/cli-integration-tests` (PR in progress - keep until merged)
- Any branches with open PRs
- Current development branches

### Command
```bash
# List unmerged branches
git branch --no-merged main

# Check for associated PRs
gh pr list --json headRefName,number,title,state
```

---

## Phase 3: Archive Old Feature Branches (Stale >3 months)

For unmerged branches with no recent activity:
1. Create archive tags before deletion
2. Document in this file
3. Delete branches

### Command
```bash
# Check branch last commit date
for branch in $(git branch --no-merged main | grep -v "^\*"); do
  echo "$branch: $(git log -1 --format=%ci $branch)"
done | sort -k2
```

---

## Phase 4: Final State Target

**Keep (<20 branches)**:
- `main` (production)
- Active feature branches (2-5)
- Hotfix branches if any (0-2)
- Release branches if any (0-1)

**Safety**:
- All merged branches backed up in main
- Archive tags for important unmerged work
- This analysis document preserved

---

## Execution Checklist

- [ ] Phase 1: Delete 101 merged branches
- [ ] Verify no regression (git log, test run)
- [ ] Phase 2: Identify 3-5 active branches to keep
- [ ] Phase 3: Archive/delete stale unmerged branches  
- [ ] Phase 4: Verify final count <20
- [ ] Update issue #24 with results
- [ ] Document lessons learned

---

**Next Action**: Execute Phase 1 (safe deletion of merged branches)
