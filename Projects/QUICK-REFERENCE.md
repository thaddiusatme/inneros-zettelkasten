# ⚡ InnerOS Quick Reference Card

*Keep this handy for daily use!*

## 🚀 Essential Commands

### **Daily Workflow**
```bash
# Check system health
python3 src/cli/workflow_demo.py . --status

# Process new notes
python3 src/cli/workflow_demo.py . --process-inbox

# Quick analytics
python3 src/cli/analytics_demo.py . --interactive
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
python3 src/cli/workflow_demo.py . --weekly-review

# Enhanced metrics & health
python3 src/cli/workflow_demo.py . --enhanced-metrics

# Connection discovery
python3 src/cli/connections_demo.py .
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

## 💡 Pro Shortcuts

- **Interactive modes**: Add `--interactive` for exploration
- **Batch control**: Use `--batch-size N` for large collections
- **Filter results**: Use `--filter "criteria"` for targeted analysis
- **Export data**: Add `--export --format json` for external tools

---
*Need more details? Check `GETTING-STARTED.md` or `CLI-REFERENCE.md`*
