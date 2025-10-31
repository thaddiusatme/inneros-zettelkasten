#!/usr/bin/env bash
# Simplified script - creates issues without milestone (add milestone via web UI)

set -euo pipefail

echo "🚀 Creating Automation Revival Sprint Issues..."
echo ""
echo "Note: Issues will be created WITHOUT milestone."
echo "      Add milestone via web UI: https://github.com/thaddiusatme/inneros-zettelkasten/issues"
echo ""

# Issue #29: Fix YouTube Rate Limiting
echo "Creating Issue #29: Fix YouTube Rate Limiting..."
gh issue create \
  --title "Fix YouTube Rate Limiting" \
  --label "type:bug-fix,priority:p0,size:small,sprint:automation-revival" \
  --body "Add rate limiting to YouTube processing to prevent API quota exhaustion.

## Problem
YouTube automation disabled on Oct 8 due to rate limiting issues.

## Acceptance Criteria
- [ ] Add 60-second cooldown between YouTube API requests
- [ ] Implement request tracking file (\`.automation/cache/youtube_last_request.txt\`)
- [ ] Update \`process_youtube_note.sh\` with rate limit checks
- [ ] Add exponential backoff for API failures

**Estimated**: 2 hours | **Day**: 1-2 (Bug Fixes)" && echo "✅ Created #29" || echo "❌ Failed #29"

# Issue #30: Fix File Watching Loop Bug
echo "Creating Issue #30: Fix File Watching Loop Bug..."
gh issue create \
  --title "Fix File Watching Loop Bug" \
  --label "type:bug-fix,priority:p0,size:small,sprint:automation-revival" \
  --body "Add cooldown/debounce logic to file watching scripts.

## Problem
Scripts running without cooldown causing CPU/memory drain.

## Acceptance Criteria
- [ ] Add 5-minute debounce to screenshot watcher
- [ ] Add duplicate processing prevention (PID lock files)
- [ ] Test resource usage (<5% CPU idle)

**Estimated**: 2 hours | **Day**: 1-2" && echo "✅ Created #30" || echo "❌ Failed #30"

# Issue #31: Test Screenshot Import
echo "Creating Issue #31: Test Screenshot Import..."
gh issue create \
  --title "Test Screenshot Import in Isolation" \
  --label "type:testing,priority:p0,size:medium,sprint:automation-revival" \
  --body "Validate screenshot import automation works correctly.

## Test Command
\`\`\`bash
./.automation/scripts/automated_screenshot_import.sh
\`\`\`

## Success Criteria
- Exit code 0
- Notes created in Inbox/
- Clean logs
- <180s execution

**Estimated**: 2 hours | **Day**: 2-3 | **Depends on**: #29, #30" && echo "✅ Created #31" || echo "❌ Failed #31"

# Issue #32: Test Inbox Processing
echo "Creating Issue #32: Test Inbox Processing..."
gh issue create \
  --title "Test Inbox Processing in Isolation" \
  --label "type:testing,priority:p0,size:medium,sprint:automation-revival" \
  --body "Validate inbox AI enhancement automation.

## Test Command
\`\`\`bash
./.automation/scripts/supervised_inbox_processing.sh
\`\`\`

## Success Criteria
- AI tags added
- Quality scores calculated
- Review report generated
- <300s execution

**Estimated**: 2 hours | **Day**: 2-3 | **Depends on**: #29, #30" && echo "✅ Created #32" || echo "❌ Failed #32"

# Issue #33: Test Health Monitor
echo "Creating Issue #33: Test Health Monitor..."
gh issue create \
  --title "Test Health Monitor" \
  --label "type:testing,priority:p1,size:small,sprint:automation-revival" \
  --body "Validate system health monitoring script.

## Test Command
\`\`\`bash
./.automation/scripts/health_monitor.sh
\`\`\`

**Estimated**: 1 hour | **Day**: 3" && echo "✅ Created #33" || echo "❌ Failed #33"

# Issue #34: Staged Cron Re-enablement
echo "Creating Issue #34: Staged Cron Re-enablement..."
gh issue create \
  --title "Staged Cron Re-enablement" \
  --label "type:deployment,priority:p0,size:medium,sprint:automation-revival" \
  --body "Re-enable cron automation in staged approach.

## Stages
1. Screenshot import only (11:30 PM)
2. Add inbox processing (Mon/Wed/Fri 6 AM)
3. Add health monitoring (every 4 hours)

**Estimated**: 2 hours | **Day**: 4-5 | **Depends on**: #31, #32, #33" && echo "✅ Created #34" || echo "❌ Failed #34"

# Issue #35: Automation Visibility
echo "Creating Issue #35: Automation Visibility..."
gh issue create \
  --title "Automation Visibility Integration (Lite)" \
  --label "type:monitoring,priority:p1,size:medium,sprint:automation-revival" \
  --body "Integrate AutomationStatusCLI into main \`./inneros\` wrapper.

## Commands to Enable
\`\`\`bash
./inneros automation status
./inneros automation logs <daemon>
\`\`\`

**Related**: #20 (full implementation deferred)  
**Estimated**: 3 hours | **Day**: 5-7" && echo "✅ Created #35" || echo "❌ Failed #35"

# Issue #36: 48-Hour Stability
echo "Creating Issue #36: 48-Hour Stability Monitoring..."
gh issue create \
  --title "48-Hour Stability Monitoring" \
  --label "type:monitoring,priority:p0,size:large,sprint:automation-revival" \
  --body "Monitor automation stability for 48 continuous hours.

## Success Metrics
- Zero rate limit errors
- Zero crashes
- Notes created daily
- Clean logs

**Estimated**: 4 hours | **Day**: 5-7 | **Depends on**: #34" && echo "✅ Created #36" || echo "❌ Failed #36"

# Issue #37: Sprint Retrospective
echo "Creating Issue #37: Sprint Retrospective..."
gh issue create \
  --title "Sprint Retrospective & Documentation" \
  --label "type:documentation,priority:p1,size:small,sprint:automation-revival" \
  --body "Document sprint results and lessons learned.

## Deliverables
- \`Projects/COMPLETED-2025-11/automation-revival-sprint-lessons-learned.md\`
- Performance metrics
- Next sprint ideas

**Estimated**: 2 hours | **Day**: 7 | **Depends on**: All issues" && echo "✅ Created #37" || echo "❌ Failed #37"

echo ""
echo "✅ Issues created!"
echo ""
echo "📊 Next steps:"
echo "  1. View issues: gh issue list --label 'sprint:automation-revival'"
echo "  2. Create milestone via web UI: https://github.com/thaddiusatme/inneros-zettelkasten/milestones/new"
echo "     - Title: v0.2.0-automation-revival"
echo "     - Due: 2025-11-06"
echo "  3. Add issues to milestone (bulk select in web UI)"
echo "  4. Start with first issue!"
echo ""
