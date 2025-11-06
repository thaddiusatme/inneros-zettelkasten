# InnerOS Automation Monitoring - Quick Guide

> **Quick reference for monitoring your automated workflows**  
> **Created**: 2025-11-05  
> **Status**: Production Ready

---

## 🎯 Daily Monitoring Workflow

### 1. **Quick Health Check** (30 seconds)

```bash
# Run automated health monitor
.automation/scripts/health_monitor.sh

# Expected output:
# ✅ Inbox size OK: X notes
# ✅ Log size OK: XMB
# ✅ Disk space OK
# ✅ Backup recent
# ✅ System responsive
```

### 2. **Check Workflow Status** (1 minute)

```bash
# View complete workflow status
python3 development/src/cli/core_workflow_cli.py knowledge/ status

# Shows:
# - Inbox note count
# - Fleeting note count
# - Permanent note count
# - AI processing status
# - Recommendations
```

### 3. **View Recent Activity** (1 minute)

```bash
# See last 10 automation runs
ls -lth .automation/logs/*.log | head -10

# View today's health checks
tail -50 .automation/logs/health_monitor_$(date +%Y-%m-%d)*.log

# View latest screenshot import
tail -50 .automation/logs/screenshot_import_*.log | tail -50
```

---

## 📊 Detailed Monitoring Commands

### **System Health**

```bash
# Full health report
.automation/scripts/health_monitor.sh

# Check fleeting notes health
python3 development/src/cli/fleeting_cli.py --vault knowledge/ fleeting-health

# List recent backups
python3 development/src/cli/safe_workflow_cli.py --vault knowledge/ list-backups
```

### **Workflow Status**

```bash
# Status report (default)
python3 development/src/cli/core_workflow_cli.py knowledge/ status

# JSON format (for scripting)
python3 development/src/cli/core_workflow_cli.py knowledge/ status --format json

# Detailed metrics report
python3 development/src/cli/core_workflow_cli.py knowledge/ report
```

### **Log Monitoring**

```bash
# Watch logs in real-time
tail -f .automation/logs/daemon_$(date +%Y-%m-%d).log

# View all logs from today
ls -lth .automation/logs/*$(date +%Y-%m-%d)*.log

# Search for errors
grep -i "error\|failed" .automation/logs/*.log | tail -20

# Check automation success rate
grep -c "✅\|PASS" .automation/logs/health_monitor_*.log | tail -10
```

---

## 🚨 Alert Types & Actions

### **Inbox Size Alert**
```
🚨 ALERT: Large inbox - X notes (threshold: 50)
```
**Action**: Run inbox processing or review manually
```bash
# Process inbox
python3 development/src/cli/core_workflow_cli.py knowledge/ process-inbox
```

### **Disk Space Alert**
```
🚨 ALERT: Low disk space - Only XGB available (threshold: 5GB)
```
**Action**: Free up space or increase threshold in script

### **Backup Too Old Alert**
```
🚨 ALERT: Backup too old - Latest backup is X days old (threshold: 7 days)
```
**Action**: Create fresh backup
```bash
python3 development/src/cli/safe_workflow_cli.py --vault knowledge/ backup
```

### **System Unresponsive Alert**
```
🚨 ALERT: System unresponsive - Status check failed or timed out
```
**Action**: Check for hanging processes, restart daemon if needed

---

## 📈 Weekly Review Process

### **Manual Weekly Analysis**

```bash
# Generate weekly review checklist
python3 development/src/cli/weekly_review_cli.py --vault knowledge/ weekly-review

# Generate enhanced metrics
python3 development/src/cli/weekly_review_cli.py --vault knowledge/ enhanced-metrics

# Export review to file
python3 development/src/cli/weekly_review_cli.py --vault knowledge/ weekly-review \
  --export-checklist weekly-review-$(date +%Y-%m-%d).md
```

### **Review Generated Reports**

```bash
# View latest analysis report
cat .automation/review_queue/weekly_analysis_*.md | tail -100

# View metrics report
cat .automation/review_queue/weekly_metrics_*.md | tail -100

# View inbox analysis
cat .automation/review_queue/inbox_analysis_*.md | tail -100
```

---

## 🔍 Troubleshooting

### **Check if Automation is Running**

```bash
# Check cron schedule
crontab -l | grep -E "screenshot|inbox|health"

# Check daemon status
ps aux | grep -E "daemon|automation" | grep -v grep

# View daemon logs
tail -100 .automation/logs/daemon_$(date +%Y-%m-%d).log
```

### **Common Issues**

**Issue**: No recent logs
```bash
# Check if automation is scheduled
crontab -l

# Manually run automation
.automation/scripts/health_monitor.sh
```

**Issue**: Logs show errors
```bash
# View full error context
tail -100 .automation/logs/[script-name]_*.log

# Check Python environment
python3 --version
pip list | grep -E "anthropic|openai"
```

**Issue**: Automation not processing inbox
```bash
# Check inbox status
ls -la knowledge/Inbox/

# Run manual process
python3 development/src/cli/core_workflow_cli.py knowledge/ process-inbox --dry-run
```

---

## 📱 Quick Reference Card

### **Most Common Commands**

| Task | Command |
|------|---------|
| Health check | `.automation/scripts/health_monitor.sh` |
| Workflow status | `python3 development/src/cli/core_workflow_cli.py knowledge/ status` |
| Fleeting health | `python3 development/src/cli/fleeting_cli.py --vault knowledge/ fleeting-health` |
| View logs | `ls -lth .automation/logs/*.log \| head -10` |
| Process inbox | `python3 development/src/cli/core_workflow_cli.py knowledge/ process-inbox` |
| Weekly review | `python3 development/src/cli/weekly_review_cli.py --vault knowledge/ weekly-review` |
| Create backup | `python3 development/src/cli/safe_workflow_cli.py --vault knowledge/ backup` |

### **Log Locations**

```
.automation/logs/
├── health_monitor_YYYY-MM-DD_HH-MM-SS.log    # Health checks
├── screenshot_import_YYYY-MM-DD_HH-MM-SS.log # Screenshot imports
├── supervised_processing_YYYY-MM-DD_HH-MM-SS.log # Inbox processing
├── weekly_analysis_YYYY-MM-DD_HH-MM-SS.log   # Weekly reviews
└── daemon_YYYY-MM-DD.log                      # Background daemon
```

### **Report Locations**

```
.automation/review_queue/
├── inbox_analysis_YYYY-MM-DD_HH-MM-SS.md     # Inbox AI analysis
├── weekly_analysis_YYYY-MM-DD_HH-MM-SS.md    # Weekly review
└── weekly_metrics_YYYY-MM-DD_HH-MM-SS.md     # Enhanced metrics
```

---

## ⏰ Automation Schedule Reference

**Default Cron Schedule** (if enabled):
```
30 23 * * * # Screenshot import (11:30 PM daily)
0 */4 * * * # Health monitoring (every 4 hours)
0 9 * * 1   # Weekly analysis (9 AM Mondays)
```

**Check your schedule**:
```bash
crontab -l
```

---

## 🎯 Success Metrics

**Healthy System Indicators**:
- ✅ Health monitor runs every 4 hours with no errors
- ✅ Inbox stays under 50 notes
- ✅ Backups created weekly
- ✅ No "ALERT" messages in recent logs
- ✅ Fleeting notes health shows "HEALTHY" status

**When to Take Action**:
- 🚨 Multiple ALERT messages in health logs
- 🚨 Inbox over 100 notes for more than 3 days
- 🚨 No backup in 7+ days
- 🚨 Error messages in automation logs

---

## 📚 Additional Resources

- **Full Automation Guide**: `docs/HOWTO/automation-user-guide.md`
- **CLI Reference**: `CLI-REFERENCE.md`
- **Daemon Health Guide**: `docs/HOWTO/daemon-health.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING.md`

---

**Last Updated**: 2025-11-05  
**Maintainer**: InnerOS Automation Team
