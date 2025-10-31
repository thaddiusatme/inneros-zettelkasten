#!/usr/bin/env bash
# Script to create GitHub issues for Automation Revival Sprint
# Run from repo root: bash .github/scripts/create-automation-sprint-issues.sh

set -euo pipefail

echo "🚀 Creating Automation Revival Sprint in GitHub..."
echo ""

# Create milestone
echo "📅 Creating milestone..."
gh milestone create "v0.2.0-automation-revival" \
  --due-date 2025-11-06 \
  --description "Revive and stabilize existing cron-based automation system for daily note creation workflow" \
  2>/dev/null || echo "  ⚠️  Milestone already exists"

# Create labels
echo "🏷️  Creating labels..."
gh label create "sprint:automation-revival" --color "7057ff" --description "Automation revival sprint" --force
gh label create "type:bug-fix" --color "d73a4a" --description "Bug fix" --force
gh label create "type:testing" --color "fbca04" --description "Testing task" --force
gh label create "type:monitoring" --color "0075ca" --description "Monitoring/observability" --force
gh label create "type:deployment" --color "008672" --description "Deployment/operations" --force
gh label create "type:documentation" --color "0e8a16" --description "Documentation" --force
gh label create "priority:p0" --color "b60205" --description "Critical priority" --force
gh label create "priority:p1" --color "d93f0b" --description "High priority" --force
gh label create "size:small" --color "c2e0c6" --description "1-2 hours" --force
gh label create "size:medium" --color "fbca04" --description "2-4 hours" --force
gh label create "size:large" --color "d93f0b" --description "4-8 hours" --force

echo ""
echo "📝 Creating issues..."

# Issue #29: Fix YouTube Rate Limiting
echo "  Creating Issue: Fix YouTube Rate Limiting..."
gh issue create \
  --title "Fix YouTube Rate Limiting" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:bug-fix,priority:p0,size:small,sprint:automation-revival" \
  --body "Add rate limiting to YouTube processing to prevent API quota exhaustion.

## Problem
YouTube automation disabled on Oct 8 due to rate limiting issues. Need to implement request throttling.

## Acceptance Criteria
- [ ] Add 60-second cooldown between YouTube API requests
- [ ] Implement request tracking file (\`.automation/cache/youtube_last_request.txt\`)
- [ ] Update \`process_youtube_note.sh\` with rate limit checks
- [ ] Add exponential backoff for API failures
- [ ] Document rate limit configuration

## Technical Details
Files to modify:
- \`process_youtube_note.sh\`
- Add: \`.automation/cache/youtube_last_request.txt\`

Implementation:
- Check last request timestamp before API call
- Sleep if < 60 seconds elapsed
- Log rate limit hits for monitoring

**Estimated**: 2 hours
**Day**: 1-2 (Bug Fixes)" || echo "  ⚠️  Issue creation failed"

# Issue #30: Fix File Watching Loop Bug
echo "  Creating Issue: Fix File Watching Loop Bug..."
gh issue create \
  --title "Fix File Watching Loop Bug" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:bug-fix,priority:p0,size:small,sprint:automation-revival" \
  --body "Add cooldown/debounce logic to file watching scripts to prevent resource exhaustion.

## Problem
Scripts running without cooldown causing CPU/memory drain. Identified in \`.automation/AUTOMATION_DISABLED\` on Oct 8.

## Acceptance Criteria
- [ ] Identify all file watching loops in automation scripts
- [ ] Add 5-minute debounce to screenshot watcher
- [ ] Add duplicate processing prevention (check PID lock files)
- [ ] Test resource usage after fix (<5% CPU idle)
- [ ] Update daemon registry with cooldown settings

## Technical Details
Files to review:
- \`.automation/scripts/automated_screenshot_import.sh\`
- \`.automation/scripts/health_monitor.sh\`

Implementation:
- Add PID file checks: \`.automation/logs/*.pid\`
- Add last-run timestamp checks
- Skip if already running or ran <5 min ago

**Estimated**: 2 hours
**Day**: 1-2 (Bug Fixes)" || echo "  ⚠️  Issue creation failed"

# Issue #31: Test Screenshot Import
echo "  Creating Issue: Test Screenshot Import in Isolation..."
gh issue create \
  --title "Test Screenshot Import in Isolation" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:testing,priority:p0,size:medium,sprint:automation-revival" \
  --body "Validate screenshot import automation works correctly before re-enabling cron.

## Acceptance Criteria
- [ ] Run \`automated_screenshot_import.sh\` manually
- [ ] Verify health check passes
- [ ] Verify backup created successfully
- [ ] Confirm screenshots imported to \`knowledge/Inbox/\`
- [ ] Check log file for errors: \`.automation/logs/screenshot_import_*.log\`
- [ ] Validate note YAML frontmatter correct
- [ ] Test with 0, 1, and 5+ screenshots

## Test Command
\`\`\`bash
cd /Users/thaddius/repos/inneros-zettelkasten
./.automation/scripts/automated_screenshot_import.sh
\`\`\`

## Success Metrics
- Exit code 0
- Notes created in Inbox/
- Clean logs (no errors)
- <180s execution time

**Estimated**: 2 hours
**Day**: 2-3 (Testing)
**Depends on**: #29, #30" || echo "  ⚠️  Issue creation failed"

# Issue #32: Test Inbox Processing
echo "  Creating Issue: Test Inbox Processing in Isolation..."
gh issue create \
  --title "Test Inbox Processing in Isolation" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:testing,priority:p0,size:medium,sprint:automation-revival" \
  --body "Validate inbox AI enhancement automation works correctly.

## Acceptance Criteria
- [ ] Run \`supervised_inbox_processing.sh\` manually
- [ ] Verify AI tags added to notes
- [ ] Confirm quality scores calculated (>0.7 for good notes)
- [ ] Check review report generated: \`.automation/review_queue/inbox_analysis_*.md\`
- [ ] Validate no content loss/corruption
- [ ] Test with 0, 1, and 10+ inbox notes

## Test Command
\`\`\`bash
./.automation/scripts/supervised_inbox_processing.sh
\`\`\`

## Success Metrics
- Exit code 0
- AI tags present in YAML
- Review report readable
- <300s execution time

**Estimated**: 2 hours
**Day**: 2-3 (Testing)
**Depends on**: #29, #30" || echo "  ⚠️  Issue creation failed"

# Issue #33: Test Health Monitor
echo "  Creating Issue: Test Health Monitor..."
gh issue create \
  --title "Test Health Monitor" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:testing,priority:p1,size:small,sprint:automation-revival" \
  --body "Validate system health monitoring script works correctly.

## Acceptance Criteria
- [ ] Run \`health_monitor.sh\` manually
- [ ] Verify system metrics logged
- [ ] Confirm <10s execution time
- [ ] Check no critical issues reported
- [ ] Validate log format parseable by AutomationStatusCLI

## Test Command
\`\`\`bash
./.automation/scripts/health_monitor.sh
\`\`\`

**Estimated**: 1 hour
**Day**: 3 (Testing)" || echo "  ⚠️  Issue creation failed"

# Issue #34: Staged Cron Re-enablement
echo "  Creating Issue: Staged Cron Re-enablement..."
gh issue create \
  --title "Staged Cron Re-enablement" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:deployment,priority:p0,size:medium,sprint:automation-revival" \
  --body "Re-enable cron automation in staged approach (screenshot import first, then expand).

## Acceptance Criteria
- [ ] Remove \`.automation/AUTOMATION_DISABLED\` flag
- [ ] Stage 1: Enable screenshot import only (11:30 PM daily)
- [ ] Monitor first automated run (check logs)
- [ ] Stage 2: Add inbox processing (Mon/Wed/Fri 6 AM)
- [ ] Stage 3: Add health monitoring (every 4 hours)
- [ ] Verify \`crontab -l\` shows correct schedule
- [ ] Document rollback procedure

## Cron Schedule
\`\`\`bash
# Stage 1 (Day 4):
30 23 * * * cd \"/path/to/repo\" && ./.automation/scripts/automated_screenshot_import.sh >/dev/null 2>&1

# Stage 2 (Day 5):
0 6 * * 1,3,5 cd \"/path/to/repo\" && ./.automation/scripts/supervised_inbox_processing.sh >/dev/null 2>&1

# Stage 3 (Day 5):
0 6,10,14,18,22 * * * cd \"/path/to/repo\" && ./.automation/scripts/health_monitor.sh >/dev/null 2>&1
\`\`\`

**Estimated**: 2 hours (spread across 2 days)
**Day**: 4-5 (Re-enablement)
**Depends on**: #31, #32, #33" || echo "  ⚠️  Issue creation failed"

# Issue #35: Automation Visibility Integration
echo "  Creating Issue: Automation Visibility Integration..."
gh issue create \
  --title "Automation Visibility Integration (Lite)" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:monitoring,priority:p1,size:medium,sprint:automation-revival" \
  --body "Integrate existing AutomationStatusCLI into main \`./inneros\` wrapper for easy status checks.

**Related**: #20 (full implementation deferred)

## Acceptance Criteria
- [ ] Verify AutomationStatusCLI tests passing
- [ ] Add \`./inneros automation status\` command
- [ ] Add \`./inneros automation logs <daemon>\` command
- [ ] Test with all 3 daemons (youtube_watcher, screenshot_processor, health_monitor)
- [ ] Document usage in CLI-REFERENCE.md

## Commands to Enable
\`\`\`bash
./inneros automation status           # Show all daemon status
./inneros automation logs screenshot  # Show recent logs
./inneros automation health           # System health summary
\`\`\`

**Note**: This is a lite version of Issue #20. Full web UI dashboard deferred to future sprint.

**Estimated**: 3 hours
**Day**: 5-7 (Monitoring)" || echo "  ⚠️  Issue creation failed"

# Issue #36: 48-Hour Stability Monitoring
echo "  Creating Issue: 48-Hour Stability Monitoring..."
gh issue create \
  --title "48-Hour Stability Monitoring" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:monitoring,priority:p0,size:large,sprint:automation-revival" \
  --body "Monitor automation stability for 48 continuous hours to validate production readiness.

## Acceptance Criteria
- [ ] All 3 cron jobs running for 48 hours
- [ ] Zero rate limit errors
- [ ] Zero crashes/hangs
- [ ] Notes created successfully each day
- [ ] Review reports generated correctly
- [ ] Logs clean (no ERROR level messages)
- [ ] Resource usage acceptable (<10% CPU, <500MB RAM)

## Monitoring Checklist (Run 2x daily)
\`\`\`bash
# Morning check (9 AM):
tail -50 .automation/logs/screenshot_import_*.log | grep ERROR
find knowledge/Inbox -name \"*.md\" -mtime -1 | wc -l

# Evening check (9 PM):
./inneros automation status
tail -50 .automation/logs/supervised_processing_*.log | grep ERROR
ls -la .automation/review_queue/
\`\`\`

## Success Metrics
- ✅ Screenshot import: 2/2 successful runs
- ✅ Inbox processing: 1-2 successful runs (Mon/Wed/Fri)
- ✅ Health monitor: 24+ successful runs (every 4 hours)
- ✅ Review reports: 1-2 generated
- ✅ Zero errors in logs

**Estimated**: 4 hours (distributed over 2 days)
**Day**: 5-7 (Monitoring)
**Depends on**: #34" || echo "  ⚠️  Issue creation failed"

# Issue #37: Sprint Retrospective
echo "  Creating Issue: Sprint Retrospective & Documentation..."
gh issue create \
  --title "Sprint Retrospective & Documentation" \
  --milestone "v0.2.0-automation-revival" \
  --label "type:documentation,priority:p1,size:small,sprint:automation-revival" \
  --body "Document sprint results, lessons learned, and plan next sprint improvements.

## Acceptance Criteria
- [ ] Create \`Projects/COMPLETED-2025-11/automation-revival-sprint-lessons-learned.md\`
- [ ] Document what worked, what didn't
- [ ] Record performance metrics (notes created, processing times, error rates)
- [ ] Identify improvements for next sprint
- [ ] Update \`.automation/README.md\` with operational procedures
- [ ] Archive sprint planning docs

## Metrics to Document
\`\`\`bash
# Notes created this week:
find knowledge/Inbox -name \"*.md\" -mtime -7 | wc -l

# Automation runs:
ls -l .automation/logs/ | grep screenshot_import | wc -l
ls -l .automation/logs/ | grep supervised_processing | wc -l

# Review reports:
ls -l .automation/review_queue/ | wc -l

# Error rate:
grep ERROR .automation/logs/*.log | wc -l
\`\`\`

## Next Sprint Ideas to Document
- Add weekly deep analysis automation?
- Expand to full cron schedule?
- Enhance monitoring dashboard?
- Add SMS/email notifications?

**Estimated**: 2 hours
**Day**: 7 (Documentation)
**Depends on**: All other issues" || echo "  ⚠️  Issue creation failed"

echo ""
echo "✅ Sprint setup complete!"
echo ""
echo "📊 Summary:"
echo "  • Milestone: v0.2.0-automation-revival (due: 2025-11-06)"
echo "  • Issues: 9 created"
echo "  • Estimated effort: 20 hours"
echo ""
echo "🔗 View in GitHub:"
echo "  gh issue list --milestone 'v0.2.0-automation-revival'"
echo "  gh milestone view 'v0.2.0-automation-revival'"
echo ""
echo "🚀 Next steps:"
echo "  1. Create GitHub Project board (optional): gh project create --title 'Automation Revival Sprint'"
echo "  2. Start with Issue #29: gh issue view 29 --web"
echo ""
