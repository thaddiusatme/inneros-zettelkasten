# Documentation Maintenance Guide

**Created**: 2025-11-11  
**Purpose**: Keep project documentation synchronized with actual progress

---

## 📋 Files That Need Regular Updates

### 1. **`.windsurf/PROJECT-PRIORITIES.md`** (Weekly)
**Purpose**: AI context for current sprint priorities  
**Update Trigger**: Weekly sprint planning or when P0/P1 issues close

**What to Update**:
- Current Sprint dates
- Issue statuses (Not started → In progress → Complete)
- Recent Completions section
- Last Updated timestamp

**How**:
```bash
# Check latest closed issues
gh issue list --state closed --limit 10 --json number,title,closedAt

# Check open P0/P1 issues
gh issue list --label priority:p0,priority:p1 --json number,title,state

# Update the file manually or use this guide
```

### 2. **`Projects/ACTIVE/README-ACTIVE.md`** (After each session)
**Purpose**: Human-readable project status  
**Update Trigger**: After completing work, before ending session

**What to Update**:
- Last Updated date
- Current Branch
- CURRENT STATE section
- Recent Achievements

**Template**:
```markdown
**Last Updated**: YYYY-MM-DD HH:MM PDT
**Current Branch**: `branch-name` (commits ahead/behind)
**Status**: Brief status message

## ✅ CURRENT STATE (Date)
**Just Completed**: What you finished

**Session Details**:
- What was accomplished
- Action items remaining

**System Status**:
- Tests: X passing
- Branches: X total
- CI/CD: Status
```

### 3. **`.windsurf/rules/updated-session-context.md`** (Monthly)
⚠️ **Cannot edit directly** - This file is in .windsurf/rules/ which is protected

**Update Process**: Request AI to update at session start when major changes occur

### 4. **Session Summary Files** (After each session)
**Location**: Root directory  
**Naming**: `SESSION-SUMMARY-YYYY-MM-DD.md`  
**Purpose**: Track what was done, what's next

**Template**:
```markdown
# Session Summary - Date

## ✅ Work Completed
- Major achievements
- Issues closed
- PRs created

## 📋 Action Items
- Manual tasks (PR creation, issue closure)
- Next session priorities

## 📊 System State
- Branch count
- Test status
- Documentation status
```

---

## 🔄 Recommended Update Workflow

### **After Completing Work** (5 minutes):

1. **Update PROJECT-PRIORITIES.md**:
   ```bash
   # Check what changed
   git log --oneline -10
   gh issue list --state closed --limit 5
   
   # Edit .windsurf/PROJECT-PRIORITIES.md
   # - Move completed issues to "Recent Completions"
   # - Update sprint dates if needed
   # - Update "Last Updated" timestamp
   ```

2. **Update README-ACTIVE.md**:
   ```bash
   # Edit Projects/ACTIVE/README-ACTIVE.md
   # - Update "Last Updated", "Current Branch", "Status"
   # - Update "CURRENT STATE" with session accomplishments
   # - Update "Recent Achievements" if major milestone
   ```

3. **Create Session Summary** (optional but helpful):
   ```bash
   # Create SESSION-SUMMARY-YYYY-MM-DD.md
   # - Document what was done
   # - List action items for next session
   # - Note system state changes
   ```

4. **Commit Documentation Updates**:
   ```bash
   git add .windsurf/PROJECT-PRIORITIES.md Projects/ACTIVE/README-ACTIVE.md
   git commit -m "docs: Update project status (YYYY-MM-DD session)"
   ```

### **Weekly Sprint Planning** (10 minutes):

1. **Sync GitHub Issues**:
   ```bash
   gh issue list --limit 20 --json number,title,state,labels
   ```

2. **Update Sprint Section**:
   - New sprint dates
   - Reprioritize P0/P1 based on completions
   - Archive old "Recent Completions" if >2 weeks old

3. **Archive Old Completions**:
   - Move SESSION-SUMMARY files >1 month old to `Projects/COMPLETED-YYYY-MM/`
   - Keep only current month's summaries in root

### **Monthly Review** (15 minutes):

1. **Request AI Session Context Update**:
   - Ask AI to check if `.windsurf/rules/updated-session-context.md` needs refresh
   - AI will review and update if major changes occurred

2. **Archive Completed Work**:
   ```bash
   # Move old lessons-learned to Projects/COMPLETED-YYYY-MM/
   # Clean up old session summaries
   ```

3. **Update Development Guides** (if patterns changed):
   - Check if `.windsurf/guides/` need updates
   - Document new patterns discovered

---

## 📝 Quick Reference Commands

### Check Current State:
```bash
# Git status
git status
git log --oneline -10

# GitHub issues
gh issue list --limit 15
gh issue list --state closed --limit 5

# Branch count
git branch | wc -l
git branch -r | wc -l

# Test status
cd development && pytest --co -q | tail -1
```

### Common Updates:
```bash
# Update priorities doc
code .windsurf/PROJECT-PRIORITIES.md

# Update active readme
code Projects/ACTIVE/README-ACTIVE.md

# Create session summary
code SESSION-SUMMARY-$(date +%Y-%m-%d).md
```

---

## 🎯 Automation Opportunities

### Future Enhancements:
1. **Auto-generate session summary** from git commits
2. **GitHub Action** to remind to update docs on PR merge
3. **CLI command** to update PROJECT-PRIORITIES.md from GitHub API
4. **Monthly cron** to archive old summaries

---

## 📊 Maintenance Checklist

### After Each Work Session:
- [ ] Update PROJECT-PRIORITIES.md (5 min)
- [ ] Update README-ACTIVE.md (5 min)
- [ ] Create session summary if significant work (5 min)
- [ ] Commit documentation updates

### Weekly (Monday):
- [ ] Review and sync GitHub Issues → PROJECT-PRIORITIES
- [ ] Archive session summaries >1 month old
- [ ] Update sprint dates and priorities

### Monthly (First Monday):
- [ ] Request AI to review session-context.md
- [ ] Archive completed lessons-learned
- [ ] Review development guides for updates
- [ ] Celebrate progress! 🎉

---

**Last Updated**: 2025-11-11  
**Maintained By**: Project owner + AI assistant  
**Review Frequency**: As needed, minimum monthly
