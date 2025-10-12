# Daily Usage Guide - Interactive Workflow Dashboard

**Version**: 2.0 (Production Ready)  
**Status**: Ready for daily workflow operations  
**Last Updated**: 2025-10-11

---

## 🚀 Quick Start

### Launch Dashboard (Recommended Method)

```bash
cd development
./start_dashboard.sh
```

Or manually:
```bash
cd development
source venv/bin/activate
python3 src/cli/workflow_dashboard.py ..
```

---

## ⚡ Keyboard Shortcuts Reference

### [P] - Process Inbox
**What it does**: Processes all notes in your Inbox directory  
**CLI**: `core_workflow_cli.py process-inbox`  
**When to use**: Daily or when you have new captures to organize  
**Expected time**: Varies (based on inbox size)

**What happens**:
1. Scans all notes in `Inbox/` directory
2. Applies AI analysis (if configured)
3. Suggests tags and quality scores
4. Helps organize notes into proper locations

**Example workflow**:
- Morning: Check inbox → Press [P] → Process new notes
- After capture sessions → Press [P] → Organize captures

---

### [W] - Weekly Review
**What it does**: Runs comprehensive weekly review workflow  
**CLI**: `weekly_review_cli.py weekly-review`  
**When to use**: Weekly (recommended: Sunday evening or Monday morning)  
**Expected time**: 5-15 minutes

**What happens**:
1. Reviews fleeting notes for promotion
2. Checks permanent notes for quality
3. Identifies orphaned notes (no connections)
4. Detects stale notes (not modified in 90+ days)
5. Generates productivity metrics

**Example workflow**:
- Sunday evening ritual → Press [W] → Review week's knowledge work
- Review suggested promotions → Act on recommendations

---

### [F] - Fleeting Health
**What it does**: Checks health of fleeting notes  
**CLI**: `fleeting_cli.py fleeting-health`  
**When to use**: Daily or when checking note quality  
**Expected time**: <5 seconds

**What happens**:
1. Counts fleeting notes in system
2. Identifies stale fleeting notes (>30 days old)
3. Suggests notes ready for promotion
4. Provides health metrics

**Example workflow**:
- Quick daily check → Press [F] → See fleeting note status
- Before weekly review → Press [F] → Identify promotion candidates

---

### [S] - System Status
**What it does**: Displays comprehensive vault status  
**CLI**: `core_workflow_cli.py status --format json`  
**When to use**: Anytime you want system overview  
**Expected time**: <2 seconds

**What happens**:
1. Counts notes in each directory
2. Shows AI processing statistics
3. Displays analytics overview
4. Reports system health

**Example output**:
```json
{
  "workflow_status": {
    "health": "healthy",
    "directory_counts": {
      "Inbox": 0,
      "Fleeting Notes": 0,
      "Permanent Notes": 0
    }
  },
  "ai_features": {
    "notes_with_ai_tags": 449,
    "notes_with_ai_summaries": 27
  }
}
```

---

### [B] - Create Backup
**What it does**: Creates timestamped backup of entire vault  
**CLI**: `safe_workflow_cli.py backup`  
**When to use**: Before major changes or periodically  
**Expected time**: 10-30 seconds (depends on vault size)

**What happens**:
1. Creates timestamped backup directory
2. Copies all vault files safely
3. Preserves directory structure
4. Confirms backup success

**Example workflow**:
- Before bulk operations → Press [B] → Create safety backup
- Weekly backup ritual → Press [B] → Ensure data safety

---

### [Q] - Quit Dashboard
**What it does**: Cleanly exits the dashboard  
**CLI**: Internal (no subprocess)  
**When to use**: When done with dashboard session  
**Expected time**: Instant

**What happens**:
1. Terminates dashboard gracefully
2. Returns to terminal prompt
3. No cleanup needed (safe to exit anytime)

---

## 📋 Daily Workflow Examples

### Morning Routine (5 minutes)
```
1. ./start_dashboard.sh
2. Press [S] - Check system status
3. Press [F] - Check fleeting health
4. Press [P] - Process any inbox notes
5. Press [Q] - Exit
```

### After Capture Session (2 minutes)
```
1. ./start_dashboard.sh
2. Press [P] - Process new captures
3. Review and organize
4. Press [Q] - Exit
```

### Weekly Review (15 minutes)
```
1. ./start_dashboard.sh
2. Press [B] - Create backup first (safety)
3. Press [W] - Run weekly review
4. Review metrics and recommendations
5. Press [F] - Check fleeting notes
6. Process promotions manually
7. Press [Q] - Exit
```

### Quick Status Check (30 seconds)
```
1. ./start_dashboard.sh
2. Press [S] - View status
3. Press [Q] - Exit
```

---

## 🎯 Best Practices

### Daily Usage
- **Morning Check**: [S] → [F] to start day with overview
- **After Captures**: [P] to process while context is fresh
- **Before Shutdown**: [S] to verify system health

### Weekly Usage
- **Sunday/Monday**: [W] for comprehensive weekly review
- **Before Review**: [B] to backup before major changes
- **After Review**: [F] to check fleeting note health

### Safety Practices
- **Backup First**: Press [B] before major operations
- **Check Status**: Press [S] after significant changes
- **Review Output**: Read CLI messages for errors
- **Take Breaks**: Exit [Q] between long sessions

---

## 🐛 Troubleshooting

### Dashboard Won't Start

**Issue**: Script fails or crashes  
**Solution**:
```bash
# Check virtual environment
source venv/bin/activate
python3 -c "import rich, requests"

# If error, install dependencies
pip install rich requests

# Try launching directly
python3 src/cli/workflow_dashboard.py ..
```

### CLI Operation Times Out

**Issue**: Operation takes >60 seconds  
**Solution**:
- This is normal for very large operations
- Dashboard protects against hangs with timeout
- Operation is killed after 60s
- Try breaking into smaller batches

### Invalid Key Error

**Issue**: Pressed wrong key  
**Solution**:
- Dashboard shows valid keys in error message
- Valid keys: B, F, P, Q, S, W
- Case insensitive (p or P both work)
- Future: [?] will show help (P2.3)

### Terminal Display Issues

**Issue**: UI looks broken or garbled  
**Solution**:
```bash
# Check terminal size
echo $COLUMNS $LINES  # Should be ≥80x24

# Try resizing terminal
# Restart dashboard

# Check Rich installation
python3 -c "from rich.console import Console; c = Console(); c.print('[green]OK[/green]')"
```

---

## 📊 Understanding Output

### Health Indicators
```
🟢 Green  = Healthy (0-20 notes in inbox)
🟡 Yellow = Attention (21-50 notes)
🔴 Red    = Critical (51+ notes)
```

### CLI Messages
```
INFO    = Normal operation
WARNING = Potential issue (not critical)
ERROR   = Operation failed (check message)
```

### Performance Expectations
```
Status Check:     <2 seconds
Fleeting Health:  <5 seconds
Process Inbox:    Varies (depends on size)
Weekly Review:    5-15 minutes
Backup:           10-30 seconds
```

---

## 💡 Pro Tips

### Efficiency Tips
1. **Keyboard Only**: Entire workflow is keyboard-driven
2. **Quick Checks**: [S] for instant status anytime
3. **Batch Processing**: [P] handles all inbox notes at once
4. **Safety First**: [B] before risky operations

### Workflow Integration
1. **Morning Ritual**: Dashboard → Status → Process → Exit
2. **After Capture**: Dashboard → Process → Exit (2 min)
3. **Weekly Review**: Dashboard → Backup → Review → Exit (15 min)
4. **Quick Peek**: Dashboard → Status → Exit (30 sec)

### Performance Tips
1. Keep inbox <20 notes for best performance
2. Run [W] weekly to maintain system health
3. Use [B] before bulk operations
4. Monitor [S] for system metrics

---

## 🔮 Coming Soon (Planned Features)

### P1.1 - Multi-Panel Layout (Next)
- 4-panel 2x2 grid display
- All status at once: Inbox, Fleeting, Weekly, System
- No more switching between views
- Estimated: Ready in ~80 minutes of development

### P1.2 - Activity Log
- See last 10 operations
- Timestamps and results
- Scrollable history
- Foundation already built (ActivityLogger)

### P1.3 - Live Refresh
- Auto-update every 5 seconds
- Pause during operations
- Manual refresh [R] key
- Countdown display

### P2.3 - Help Overlay
- Press [?] for help
- Keyboard shortcuts reference
- Context-sensitive help
- Quick troubleshooting guide

---

## 📈 Tracking Your Usage

### Suggested Metrics to Track
- **Daily**: How often do you use [P]?
- **Weekly**: Is [W] helpful for review?
- **Pain Points**: What features are missing?
- **Performance**: Are operations fast enough?

### Feedback to Collect
- Which shortcuts do you use most?
- What additional shortcuts would help?
- Are error messages clear enough?
- Is the UI intuitive?

### Share Feedback
- Note improvements in usage patterns
- Track time saved vs manual CLI usage
- Document any bugs or issues
- Suggest new features

---

## 🎯 Success Metrics

After 1 week of daily usage, evaluate:

**Efficiency**:
- [ ] Faster than manual CLI commands?
- [ ] Reduced typing by >75%?
- [ ] Workflow feels smooth?

**Reliability**:
- [ ] Zero crashes or hangs?
- [ ] All operations complete successfully?
- [ ] Error messages helpful?

**Usability**:
- [ ] Shortcuts easy to remember?
- [ ] UI clear and readable?
- [ ] Would recommend to others?

---

## 📞 Support

### Documentation
- `ARCHITECTURE-DASHBOARD.md` - System architecture
- `PRODUCTION-TEST-GUIDE.md` - Testing procedures
- `PRODUCTION-TEST-RESULTS.md` - Test results
- `PRODUCTION-READY-FINAL.md` - Production approval

### Getting Help
1. Check this guide first
2. Review error messages carefully
3. Run tests to verify system health
4. Check documentation for details
5. Create GitHub issue if needed

### Emergency Reset
If dashboard is completely broken:
```bash
# Deactivate and reactivate venv
deactivate
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade rich requests

# Run tests
python3 test_dashboard_ui.py
python3 test_dashboard_cli_integration.py

# If tests pass, dashboard should work
```

---

## 🎉 Enjoy Your Dashboard!

You have a production-ready workflow automation tool:
- ✅ 6 instant keyboard shortcuts
- ✅ Real CLI integration
- ✅ Beautiful terminal UI
- ✅ 100% tested and validated
- ✅ Ready for daily use

**Start your journey**:
```bash
./start_dashboard.sh
```

**Master the shortcuts**, integrate into your workflow, and enjoy the productivity boost! 🚀

---

**Guide Version**: 1.0  
**Dashboard Version**: 2.0  
**Status**: Production Ready  
**Last Updated**: 2025-10-11
