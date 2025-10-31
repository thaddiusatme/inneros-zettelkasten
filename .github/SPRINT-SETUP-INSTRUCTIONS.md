# Sprint Setup Instructions

## Quick Start

### 1. Create GitHub Issues Automatically

```bash
# Run the automated script:
bash .github/scripts/create-automation-sprint-issues.sh
```

This will create:
- ✅ Milestone: `v0.2.0-automation-revival` (due Nov 6)
- ✅ 9 issues with proper labels and dependencies
- ✅ All necessary labels for sprint tracking

### 2. View Your Sprint

```bash
# View all sprint issues:
gh issue list --milestone 'v0.2.0-automation-revival'

# View milestone progress:
gh milestone view 'v0.2.0-automation-revival'

# View specific issue:
gh issue view 29 --web
```

### 3. Create GitHub Project Board (Optional)

**Option A: Via GitHub CLI**
```bash
gh project create --title "Automation Revival Sprint" --owner @me
# Then manually add issues to project
```

**Option B: Via GitHub Web UI** (Recommended)
1. Go to: https://github.com/thaddiusatme/inneros-zettelkasten/projects
2. Click "New project"
3. Choose "Board" template
4. Name: "Automation Revival Sprint"
5. Add issues by clicking "+" and searching for milestone

### 4. Start Working

```bash
# View first issue:
gh issue view 29

# Start work (creates branch):
git checkout -b fix/youtube-rate-limiting

# When done, create PR:
gh pr create --title "Fix YouTube Rate Limiting" --body "Fixes #29"
```

---

## Sprint Structure

### Issues Created

| # | Title | Priority | Size | Day |
|---|-------|----------|------|-----|
| #29 | Fix YouTube Rate Limiting | P0 | Small | 1-2 |
| #30 | Fix File Watching Loop Bug | P0 | Small | 1-2 |
| #31 | Test Screenshot Import | P0 | Medium | 2-3 |
| #32 | Test Inbox Processing | P0 | Medium | 2-3 |
| #33 | Test Health Monitor | P1 | Small | 3 |
| #34 | Staged Cron Re-enablement | P0 | Medium | 4-5 |
| #35 | Automation Visibility Integration | P1 | Medium | 5-7 |
| #36 | 48-Hour Stability Monitoring | P0 | Large | 5-7 |
| #37 | Sprint Retrospective | P1 | Small | 7 |

### Dependencies
- #31, #32 depend on #29, #30
- #34 depends on #31, #32, #33
- #36 depends on #34
- #37 depends on all issues

---

## Daily Workflow

### Morning
```bash
# Check what's assigned to you:
gh issue list --assignee @me --milestone 'v0.2.0-automation-revival'

# View today's work:
gh issue list --label "sprint:automation-revival" --state open
```

### During Work
```bash
# Update issue (mark checklist items):
gh issue view <number> --web  # Edit in browser

# Add comment:
gh issue comment <number> --body "Working on rate limiter implementation"
```

### End of Day
```bash
# Check progress:
gh milestone view 'v0.2.0-automation-revival'

# Close completed issue:
gh issue close <number> --comment "Completed! Rate limiting working correctly."
```

---

## Troubleshooting

### If script fails
```bash
# Check GitHub CLI is installed:
gh --version

# Login if needed:
gh auth login

# Check permissions:
gh auth status
```

### If issues already exist
The script will warn but continue. You can:
1. Delete duplicate issues manually
2. Or just continue with existing issues

### Update issue after creation
```bash
# Edit issue:
gh issue edit <number> --title "New Title" --body "New description"

# Add label:
gh issue edit <number> --add-label "needs-review"

# Change milestone:
gh issue edit <number> --milestone "v0.2.0-automation-revival"
```

---

## Next Steps After Setup

1. **Review Sprint Plan**: `.github/SPRINT-AUTOMATION-REVIVAL.md`
2. **Start Issue #29**: `gh issue view 29 --web`
3. **Update PROJECT-PRIORITIES.md**: Add sprint info
4. **Create branch**: `git checkout -b fix/youtube-rate-limiting`

---

## Quick Reference

**View all sprint issues**: `gh issue list -m 'v0.2.0-automation-revival'`  
**View issue**: `gh issue view <number>`  
**Update issue**: `gh issue edit <number>`  
**Close issue**: `gh issue close <number>`  
**View milestone**: `gh milestone view 'v0.2.0-automation-revival'`

**Full documentation**: `.github/SPRINT-AUTOMATION-REVIVAL.md`
