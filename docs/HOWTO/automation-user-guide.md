# InnerOS Automation User Guide

> **Complete guide to automated knowledge capture workflows**  
> **Created**: 2025-10-31  
> **Sprint**: Issues #29-34 Automation Re-enablement  
> **Status**: Production Ready

---

## 🎯 Overview

InnerOS provides three tiers of automation to transform your knowledge capture workflow from manual tedium to hands-free intelligence:

| Tier | Safety Level | Description | Example |
|------|--------------|-------------|---------|
| **Tier 1** | Fully Safe | Creates new content, never modifies existing | Screenshot import |
| **Tier 2** | Supervised | Enhances metadata, queues for human review | Inbox AI analysis |
| **Tier 3** | Monitored | Full automation with health monitoring | Scheduled processing |

**Time Savings**: 30-60 minutes/day on manual knowledge capture tasks

---

## 📱 Tier 1: Screenshot Import Automation

**What It Does**: Automatically imports Samsung screenshots from OneDrive, extracts text with OCR, generates AI descriptions, creates markdown notes in your Inbox.

### User Experience

**The Problem**: You take 5-20 screenshots daily on your phone. They pile up in OneDrive and never get processed into your knowledge base.

**The Solution**: Wake up to find all yesterday's screenshots converted to AI-enhanced markdown notes, ready for review.

### What You Get

- ✅ **Real OCR text extraction** from conversations, articles, social posts
- ✅ **AI visual descriptions** (>100 words describing UI, layout, content)
- ✅ **Smart filenames** using keywords from actual extracted content
- ✅ **App detection** (Messenger, Chrome, Instagram, Threads, etc.)
- ✅ **Processing time**: <5 minutes for 5-20 screenshots

### Quick Start

**Option 1: Manual Processing** (Test it first)
```bash
# Process today's screenshots manually
cd ~/repos/inneros-zettelkasten
.automation/scripts/automated_screenshot_import.sh
```

**Option 2: Automatic Nightly Processing**
```bash
# Enable nightly screenshot import at 11:30 PM
.automation/scripts/enable_automation_staged.sh phase1

# Check it's working
python3 .automation/scripts/check_automation_health.py
```

### Example Output

```
📸 Processing 7 screenshots...
  ✓ screenshot-20251031-messenger-conversation-alex.md
    • OCR extracted: 342 words
    • AI description: "Messenger conversation interface showing a discussion 
      about project deadlines. Blue and white color scheme with..."
    • App: Facebook Messenger
    
  ✓ screenshot-20251031-chrome-ai-productivity-tips.md
    • OCR extracted: 1,253 words
    • AI description: "Chrome browser displaying an article titled 'AI 
      Productivity Tips'. Clean layout with dark mode enabled..."
    • App: Chrome Browser
    
✅ Created 7 notes in Inbox/ ready for review
⏱️  Processing time: 4 min 23 sec
```

### Scheduled Behavior

**When Enabled** (Phase 1):
- **Runs**: Daily at 11:30 PM
- **Duration**: 3-7 minutes
- **Creates**: 5-20 new notes in `Inbox/`
- **Never touches**: Existing notes (fully safe)
- **Logs**: `.automation/logs/screenshot_import_YYYYMMDD_HHMMSS.log`

### Safety Features

- ✅ **Never modifies existing notes** - only creates new ones
- ✅ **Automatic backup** before processing
- ✅ **Timeout protection** (5-minute max runtime)
- ✅ **Error handling** with graceful fallback
- ✅ **Detailed logging** for troubleshooting

---

## 🧠 Tier 2: Inbox AI Enhancement

**What It Does**: Analyzes all notes in your Inbox, adds quality scores, auto-generates tags, discovers semantic connections, queues results for human review.

### User Experience

**The Problem**: Notes accumulate in Inbox without quality assessment. You don't know which ones are ready for promotion to Permanent Notes.

**The Solution**: AI analyzes every note, scores quality (0.0-1.0), suggests tags, finds connections, and presents a review report highlighting what's ready for promotion.

### What You Get

- ✅ **Quality scores** (0.0-1.0) for every note
  - ≥0.7: Promotion-ready (high quality)
  - 0.4-0.7: Needs work (medium quality)
  - <0.4: Low quality (needs significant revision)
- ✅ **Auto-generated tags** (3-8 relevant tags per note)
- ✅ **Connection suggestions** (AI finds semantically related notes)
- ✅ **Human-readable review reports** in `.automation/review_queue/`
- ✅ **Processing time**: <10 minutes for 20-50 notes

### Quick Start

**Option 1: Manual Processing** (Test it first)
```bash
# Process all inbox notes with AI enhancement
cd ~/repos/inneros-zettelkasten
.automation/scripts/supervised_inbox_processing.sh
```

**Option 2: Automatic Processing (Mon/Wed/Fri)**
```bash
# Enable inbox processing Mon/Wed/Fri at 6:00 AM
# (Requires Phase 1 to be stable for 24 hours)
.automation/scripts/enable_automation_staged.sh phase2

# Check results
ls -lh .automation/review_queue/
```

### Example Output

```
🧠 Processing 23 inbox notes...

📊 Quality Assessment:
  • 8 notes rated ≥0.7 (promotion-ready) ⭐
  • 12 notes rated 0.4-0.7 (needs work)
  • 3 notes rated <0.4 (low quality)

🏷️  Tags Added:
  • Total tags generated: 127 tags across 23 notes
  • Average: 5.5 tags per note
  • New tag concepts discovered: 18

🔗 Connections Found:
  • 15 semantic connections between notes
  • 3 potential MOC clusters identified
  • 2 orphaned notes that need linking

📋 Review Report Generated:
  .automation/review_queue/inbox_analysis_20251031_060015.md

✅ Completed in 8 min 42 sec
```

### Review Report Format

```markdown
# 📋 Inbox Processing Review Report
**Generated**: 2025-10-31 06:00:15

## 🎯 High-Priority Items for Review

### Notes Recommended for Promotion (Quality ≥ 0.7)
1. **fleeting-20251029-context-engineering-notes.md** (Quality: 0.82)
   - Tags: context-engineering, ai-workflows, tdd, automation
   - Connections: 3 related notes found
   - Action: Ready for promotion to Permanent Notes/

2. **lit-20251028-zettelkasten-principles.md** (Quality: 0.78)
   - Tags: zettelkasten, pkm, methodology, note-taking
   - Connections: 5 related notes found
   - Action: Ready for promotion to Literature Notes/

### New Connections Discovered
- [fleeting-20251029-context-engineering-notes.md] ↔ [zettel-202507231648-context-engineering-improves-tdd-automation.md]
  Semantic similarity: 0.87 (AI workflows, TDD integration)

### Processing Summary
- **Total Notes Processed**: 23 notes
- **Tags Added**: 127 tags (5.5 avg/note)
- **Quality Scores Updated**: 23 notes
- **Connections Found**: 15 connections

## 🔄 Next Steps
- [ ] Review 8 high-quality notes for promotion
- [ ] Validate AI-suggested connections
- [ ] Consider creating MOC from connection clusters
```

### Scheduled Behavior

**When Enabled** (Phase 2):
- **Runs**: Monday, Wednesday, Friday at 6:00 AM
- **Duration**: 5-12 minutes (depends on inbox size)
- **Enhances**: All notes in `Inbox/`
- **Creates**: Review reports in `.automation/review_queue/`
- **Never modifies**: Core note content (only adds metadata)
- **Logs**: `.automation/logs/supervised_processing_YYYYMMDD_HHMMSS.log`

### Safety Features

- ✅ **Supervised approach** - enhances metadata, human reviews content
- ✅ **Never changes core note text** - only adds YAML frontmatter
- ✅ **Review queue** - all results queued for human validation
- ✅ **Backup before processing**
- ✅ **Timeout protection** (10-minute max runtime)
- ✅ **Detailed review reports** for human decision-making

---

## 🎬 YouTube Processing (Rate Limited)

**What It Does**: Processes YouTube notes with 60-second cooldown to prevent API quota exhaustion.

### User Experience

**The Problem** (Pre-Sprint): YouTube automation was disabled Oct 8 due to hitting API quota limits daily, causing request failures.

**The Solution** (Post-Sprint): YouTube processing now includes:
- ✅ 60-second cooldown between API requests
- ✅ Request tracking file (`.automation/cache/youtube_last_request.txt`)
- ✅ Exponential backoff for API failures
- ✅ Quota monitoring and alerts

### Status

- **Fixed**: Issue #29 (Closed)
- **Safe for automation**: Yes (rate limiting in place)
- **Integration**: Works with existing YouTube daemon
- **No user action required**: Automatic rate limiting

---

## 📊 Tier 3: Health Monitoring

**What It Does**: Monitors all automation daemons, checks rate limiters, detects stale processes, exports status for dashboards.

### Quick Check

```bash
# Get full health report in <5 seconds
python3 .automation/scripts/check_automation_health.py

# JSON format for scripting
python3 .automation/scripts/check_automation_health.py --json

# Export to file
python3 .automation/scripts/check_automation_health.py --export .automation/logs/status.json
```

### Example Output

```
🤖 Automation Health Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2025-10-31 11:04:23

📊 Daemon Status:
  • health_monitor       🟢 Running (PID: 45231, CPU: 0.2%, Mem: 24 MB)
  • screenshot_watcher   🟢 Running (PID: 45232, CPU: 0.1%, Mem: 18 MB)
  • youtube_watcher      🟢 Running (PID: 45233, CPU: 0.1%, Mem: 16 MB)

⏱️  Rate Limiter Status:
  • YouTube API cooldown: 23 seconds remaining
  • Screenshot debounce: Ready (no cooldown)
  • Inbox processing: Ready (no cooldown)

📈 Last Run Status:
  • Screenshot import: 2 min ago (✅ Success)
    - Processed: 7 files
    - Duration: 4m 23s
    - Created: 7 notes in Inbox/
    
  • Inbox processing: 14 hours ago (✅ Success)
    - Processed: 23 notes
    - Duration: 8m 42s
    - High-quality: 8 notes (≥0.7)
    
  • Health monitor: 30 min ago (✅ Success)
    - System health: GOOD
    - No stale processes detected

🚨 Alerts:
  • None - all systems operational

✅ Overall System Health: GOOD
```

### Scheduled Monitoring

**When Enabled** (Phase 1+):
- **Health check**: Every 30 minutes → JSON export
- **Deep monitoring**: Every 4 hours → Full daemon analysis
- **Alerting**: Immediate on failures
- **Logs**: `.automation/logs/health_monitor_YYYYMMDD_HHMMSS.log`

---

## 🛡️ Staged Rollout Safety System

### Phase 1: Screenshot Import Only (24-hour test)

**What's Enabled**:
- ✅ Screenshot import (11:30 PM daily)
- ✅ Health monitoring (every 30 min)
- ✅ Deep health checks (every 4 hours)

**Enable**:
```bash
.automation/scripts/enable_automation_staged.sh phase1
```

**Observe**: Wait 24 hours, check logs daily

---

### Phase 2: Add Inbox Processing (24-hour test)

**What's Added**:
- ✅ Inbox AI enhancement (Mon/Wed/Fri 6:00 AM)
- ✅ Connection discovery
- ✅ Review queue generation

**Enable** (after Phase 1 success):
```bash
.automation/scripts/enable_automation_staged.sh phase2
```

**Observe**: Wait 24 hours, review queue reports

---

### Phase 3: Full Automation (Production)

**What's Added**:
- ✅ Weekly deep analysis
- ✅ All automation features enabled
- ✅ Full monitoring and alerting

**Enable** (after Phase 2 success):
```bash
.automation/scripts/enable_automation_staged.sh phase3
```

**Result**: Complete hands-free knowledge capture automation

---

## 🚨 Emergency Procedures

### Stop All Automation

```bash
# Immediately disable ALL automation
.automation/scripts/disable_automation_emergency.sh "describe the problem"

# This will:
# 1. Back up current crontab
# 2. Remove all automation entries
# 3. Log the reason for emergency stop
# 4. Display rollback instructions
```

### Check What Went Wrong

```bash
# View health status
python3 .automation/scripts/check_automation_health.py

# View recent logs
tail -100 .automation/logs/screenshot_import_*.log
tail -100 .automation/logs/supervised_processing_*.log
tail -100 .automation/logs/health_monitor_*.log

# Check daemon status
python3 development/src/cli/automation_status_cli.py
```

### Restore from Backup

```bash
# Crontab backups are in:
ls -lh .automation/cron/

# Restore previous crontab
crontab .automation/cron/crontab_backup_YYYYMMDD_HHMMSS.txt
```

---

## 📈 Success Metrics

Track your automation value with these metrics:

### Daily Metrics
```bash
# How many screenshots processed today?
grep -c "Screenshot imported" .automation/logs/screenshot_import_*.log

# How many inbox notes enhanced this week?
grep -c "processed" .automation/logs/supervised_processing_*.log

# Current inbox size
find Inbox/ -name "*.md" | wc -l

# Notes promoted to Permanent this week
find "Permanent Notes/" -name "*.md" -mtime -7 | wc -l
```

### Weekly Review
```bash
# Generate comprehensive review
.automation/scripts/weekly_deep_analysis.sh

# Review queue items
ls -lh .automation/review_queue/

# Check health trends
cat .automation/logs/automation_status.json | jq '.overall_healthy'
```

---

## 🎯 Recommended Workflow

### Morning Routine (5 minutes)

1. **Check automation health**:
   ```bash
   python3 .automation/scripts/check_automation_health.py
   ```

2. **Review overnight screenshot imports**:
   ```bash
   ls -lh Inbox/screenshot-*
   ```

3. **Quick scan new notes**:
   Open 2-3 screenshot notes, verify OCR quality

### Mon/Wed/Fri Morning (10 minutes)

1. **Check health** (same as above)

2. **Open review queue report**:
   ```bash
   # Find today's report
   ls -lh .automation/review_queue/inbox_analysis_*.md
   ```

3. **Promote high-quality notes** (≥0.7 quality):
   - Open report
   - Review "Promotion-Ready" section
   - Move notes to Permanent Notes/ or Literature Notes/
   - Update any suggested connections

### Weekly Deep Review (30 minutes)

1. **Run deep analysis**:
   ```bash
   .automation/scripts/weekly_deep_analysis.sh
   ```

2. **Review connection clusters**: Consider creating new MOCs

3. **Process remaining inbox**: Handle notes that didn't auto-promote

4. **Check automation metrics**: Adjust schedules if needed

---

## 📚 Additional Resources

### Documentation
- **CLI Reference**: `CLI-REFERENCE.md` - All CLI commands
- **Daemon Health**: `docs/HOWTO/daemon-health.md` - Monitoring guide
- **Architecture**: `docs/ARCHITECTURE.md` - System design

### Scripts Location
- **Automation scripts**: `.automation/scripts/`
- **Health monitoring**: `.automation/scripts/check_automation_health.py`
- **Staged enablement**: `.automation/scripts/enable_automation_staged.sh`
- **Emergency stop**: `.automation/scripts/disable_automation_emergency.sh`

### Logs & Reports
- **Logs**: `.automation/logs/` (timestamped log files)
- **Review queue**: `.automation/review_queue/` (human-readable reports)
- **Crontab backups**: `.automation/cron/` (safety backups)

### Support
- **GitHub Issues**: [thaddiusatme/inneros-zettelkasten/issues](https://github.com/thaddiusatme/inneros-zettelkasten/issues)
- **Sprint Lessons**: `Projects/COMPLETED-2025-10/issue-34-complete-lessons-learned.md`

---

## ⚙️ Configuration

### Adjust Schedules

Edit `.automation/scripts/enable_automation_staged.sh` to customize:

```bash
# Screenshot import schedule (default: 11:30 PM)
30 23 * * * cd "$REPO_ROOT" && ./.automation/scripts/automated_screenshot_import.sh

# Inbox processing schedule (default: Mon/Wed/Fri 6:00 AM)
0 6 * * 1,3,5 cd "$REPO_ROOT" && ./.automation/scripts/supervised_inbox_processing.sh

# Health monitoring (default: every 30 minutes)
*/30 * * * * cd "$REPO_ROOT" && python3 .automation/scripts/check_automation_health.py --export .automation/logs/status.json --json
```

### Adjust Quality Thresholds

Edit `.automation/scripts/supervised_inbox_processing.sh`:

```bash
# Default: 0.7 (only highlight high-quality notes)
MIN_QUALITY_THRESHOLD=0.7

# Lower to see more promotion candidates (e.g., 0.6)
MIN_QUALITY_THRESHOLD=0.6
```

### Adjust Timeouts

Edit automation scripts to increase/decrease timeouts:

```bash
# Screenshot import timeout (default: 300s = 5 min)
MAX_RUNTIME=300

# Inbox processing timeout (default: 600s = 10 min)
MAX_RUNTIME=600
```

---

## 🎉 Quick Start Summary

### Get Immediate Value (5 minutes)

```bash
# 1. Test screenshot processing manually
cd ~/repos/inneros-zettelkasten
.automation/scripts/automated_screenshot_import.sh

# 2. Check what got created
ls -lh Inbox/screenshot-*

# 3. Review one note to see AI magic
cat Inbox/screenshot-20251031-*.md
```

### Enable Automation (2 minutes)

```bash
# Enable Phase 1 (screenshot import nightly)
.automation/scripts/enable_automation_staged.sh phase1

# Verify it's working
python3 .automation/scripts/check_automation_health.py
```

### Full Automation (1 week)

- **Day 1**: Enable Phase 1, observe 24 hours
- **Day 2**: Check health, verify screenshots processing
- **Day 3**: Enable Phase 2, observe 24 hours
- **Day 4**: Review inbox analysis reports
- **Day 5**: Enable Phase 3 (full automation)
- **Week 2**: Enjoy hands-free knowledge capture! 🎉

---

**Ready to automate your knowledge capture?** Start with the Quick Start test above!
