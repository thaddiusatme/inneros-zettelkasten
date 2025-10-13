# ⚡ InnerOS Quick Reference Card

*Keep this handy for daily use!*

> **⚠️ IMPORTANT**: `workflow_demo.py` is deprecated (ADR-004, October 2025). All commands below use dedicated CLIs. See [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for migration from old commands.

## 🚀 Essential Commands

### **Daily Workflow**
```bash
# Check system health
python3 development/src/cli/core_workflow_cli.py status

# Process new notes
python3 development/src/cli/core_workflow_cli.py process-inbox

# Quick analytics
python3 development/src/cli/analytics_demo.py . --interactive
```

### **Tag Cleanup** ⭐ Latest Feature!
```bash
# Safe exploration (always start here)
python3 development/src/ai/enhanced_ai_tag_cleanup_deployment.py --dry-run --max-tags 10

# Live cleanup (after reviewing dry-run report)
python3 development/src/ai/enhanced_ai_tag_cleanup_deployment.py --live --max-tags 10
```

### **Weekly Maintenance**
```bash
# Weekly review & promotion
python3 development/src/cli/weekly_review_cli.py weekly-review

# Enhanced metrics & health
python3 development/src/cli/weekly_review_cli.py enhanced-metrics

# Connection discovery (find similar notes)
python3 development/src/cli/connections_demo.py similar "knowledge/Permanent Notes/your-note.md" knowledge/

# Generate full connection map
python3 development/src/cli/connections_demo.py map knowledge/
```

## 📊 Key Locations

- **Reports**: `knowledge/Reports/` - All AI-generated analysis
- **Inbox**: `knowledge/Inbox/` - New notes to process
- **Templates**: `Templates/` - Note creation templates
- **CLI Help**: Add `--help` to any command

## 🎯 Quality Scores

- **>0.7**: Excellent (ready for promotion)
- **0.4-0.7**: Good (needs development)
- **<0.4**: Needs attention (consider cleanup)

## 🚨 Safety First

1. **Always dry-run** tag cleanup operations first
2. **Check reports** before proceeding with live operations
3. **Start small** - use `--max-tags 5` initially
4. **Backups exist** - tag cleanup creates automatic backups

## 💡 Common Tasks Cheatsheet

| **Task** | **Command** |
|----------|-------------|
| **Daily inbox check** | `python3 development/src/cli/core_workflow_cli.py process-inbox` |
| **Weekly review** | `python3 development/src/cli/weekly_review_cli.py weekly-review` |
| **Fleeting note health** | `python3 development/src/cli/fleeting_cli.py fleeting-health` |
| **Safe batch processing** | `python3 development/src/cli/safe_workflow_cli.py batch-process-safe` |
| **Create backup** | `python3 development/src/cli/safe_workflow_cli.py backup` |
| **Promote note** | `python3 development/src/cli/core_workflow_cli.py promote note.md permanent` |

## 🔧 Troubleshooting

### **Import/Path Errors**
```bash
# Ensure you're in project root
cd /path/to/inneros-zettelkasten

# Set PYTHONPATH if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)/development"
```

### **CLI Not Found**
```bash
# Use full path from project root
python3 development/src/cli/core_workflow_cli.py --help
```

### **Migrating from workflow_demo.py** ⚠️

| **Old (Deprecated)** | **New (Use This)** |
|----------------------|-------------------|
| `workflow_demo.py . --status` | `core_workflow_cli.py status` |
| `workflow_demo.py . --process-inbox` | `core_workflow_cli.py process-inbox` |
| `workflow_demo.py . --weekly-review` | `weekly_review_cli.py weekly-review` |
| `workflow_demo.py . --fleeting-triage` | `fleeting_cli.py fleeting-triage` |
| `workflow_demo.py . --backup` | `backup_cli.py backup` |

**Migration Details**: See [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for all 26 commands  
**Deadline**: November 11, 2025 (workflow_demo.py will be removed)

---
*Need more details? Check `GETTING-STARTED.md` or `CLI-REFERENCE.md`*
