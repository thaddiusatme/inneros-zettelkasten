# InnerOS Zettelkasten - Migration Guide

> **For existing users migrating to dedicated CLIs (ADR-004) and reorganized project structure**  
> **Updated**: 2025-10-11 (ADR-004 CLI Layer Extraction Complete)

## 🎯 **What Changed?**

The InnerOS Zettelkasten project has been reorganized from a mixed code/notes structure to a clean separation architecture:

### **Before (Mixed Structure)**
```
/ (ROOT - Mixed)
├── src/                  # Python code mixed with notes
├── tests/                # Tests mixed with notes
├── Inbox/                # Notes mixed with code
├── Fleeting Notes/       # Notes mixed with code
├── Permanent Notes/      # Notes mixed with code
├── .obsidian/            # Obsidian config in root
└── various dev files...  # Dev artifacts mixed everywhere
```

### **After (Clean Separation)**
```
/ (ROOT - Clean Navigation)
├── development/          # 🔧 ALL CODE & DEV ARTIFACTS
│   ├── src/             # Python AI/workflow code
│   ├── tests/           # Test suites
│   ├── demos/           # CLI demonstration tools
│   └── README-dev.md    # Developer documentation
├── knowledge/           # 📚 ALL KNOWLEDGE CONTENT
│   ├── Inbox/           # Staging area for new notes
│   ├── Fleeting Notes/  # Quick captures
│   ├── Permanent Notes/ # Atomic, evergreen knowledge
│   ├── Archive/         # Old/deprecated content
│   ├── Templates/       # Obsidian templates
│   ├── .obsidian/       # Obsidian configuration
│   └── README-knowledge.md # Knowledge worker documentation
├── Projects/            # 📋 Project documentation
├── Reviews/             # 📊 Weekly reviews
└── inneros             # 🚀 UNIFIED CLI WRAPPER
```

## 🚀 **New Unified CLI: `inneros`**

### **Before**: Complex Python Script Calls
```bash
# Old way (still works for developers)
python3 src/cli/analytics_demo.py . --interactive
python3 src/cli/workflow_demo.py . --process-inbox
python3 src/cli/enhance_demo.py note.md
```

### **After**: Simple Unified Commands
```bash
# New simplified commands
inneros analytics --interactive
inneros workflow --process-inbox
inneros enhance knowledge/Inbox/note.md
```

## 📋 **Migration Checklist**

### **For Knowledge Workers (Notes Only)**
- [x] **No action needed!** Your notes are automatically in `knowledge/`
- [x] **Obsidian works normally** - open `knowledge/` as your vault
- [x] **Templates unchanged** - all templates work as before
- [x] **Use new CLI**: Replace old Python commands with `inneros` commands

### **For Developers (Code & Notes)**
- [x] **Code moved to `development/`** - all Python code, tests, demos
- [x] **Update import paths** - if you have custom scripts, update imports
- [x] **Use new CLI for demos** - prefer `inneros` commands over direct Python calls
- [x] **Development docs** - check `development/README-dev.md` for setup

### **For Advanced Users (Custom Workflows)**
- [ ] **Check Templater scripts** - verify any hardcoded paths still work
- [ ] **Update automation** - replace Python script calls with `inneros` commands
- [ ] **Custom integrations** - update paths if you built custom tools

## 🚨 **ADR-004: Dedicated CLI Migration** (October 2025)

### **What Changed?**

The monolithic `workflow_demo.py` (2,128 LOC) has been **deprecated** and replaced with **9 dedicated CLIs** for better maintainability and clarity.

**Transition Period**: 1 month (October 11 - November 11, 2025)
- `workflow_demo.py` will show deprecation warnings but continue working
- After November 11, 2025: `workflow_demo.py` moves to `development/legacy/`

**Audit Results** (Phase 1 Complete: Oct 12, 2025):
- ✅ 26 commands mapped to dedicated CLIs
- ✅ 709 references found across 161 files
- ✅ Complete migration path documented below

---

### **Complete Command Migration Reference**

All 26 `workflow_demo.py` commands have dedicated CLI equivalents. Use this table to migrate your workflows:

#### **1. Weekly Review & Metrics** (4 commands → `weekly_review_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --weekly-review` | `python3 development/src/cli/weekly_review_cli.py weekly-review` |
| `python3 development/src/cli/workflow_demo.py . --enhanced-metrics` | `python3 development/src/cli/weekly_review_cli.py enhanced-metrics` |
| `python3 development/src/cli/workflow_demo.py . --comprehensive-orphaned` | `python3 development/src/cli/weekly_review_cli.py comprehensive-orphaned` |
| `python3 development/src/cli/workflow_demo.py . --remediate-orphans` | `python3 development/src/cli/weekly_review_cli.py remediate-orphans` |

**Common Options**: `--export-checklist FILE`, `--format json`, `--dry-run`

#### **2. Fleeting Notes Lifecycle** (3 commands → `fleeting_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --fleeting-health` | `python3 development/src/cli/fleeting_cli.py fleeting-health` |
| `python3 development/src/cli/workflow_demo.py . --fleeting-triage` | `python3 development/src/cli/fleeting_cli.py fleeting-triage` |
| `python3 development/src/cli/workflow_demo.py . --promote-note PATH` | `python3 development/src/cli/fleeting_cli.py promote-note PATH` |

**Common Options**: `--min-quality SCORE`, `--export FILE`, `--format json`

#### **3. Core Workflow Processing** (4 commands → `core_workflow_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --status` | `python3 development/src/cli/core_workflow_cli.py status` |
| `python3 development/src/cli/workflow_demo.py . --process-inbox` | `python3 development/src/cli/core_workflow_cli.py process-inbox` |
| `python3 development/src/cli/workflow_demo.py . --promote FILE TYPE` | `python3 development/src/cli/core_workflow_cli.py promote FILE TYPE` |
| `python3 development/src/cli/workflow_demo.py . --report` | `python3 development/src/cli/core_workflow_cli.py report` |

**Common Options**: `--dry-run`, `--verbose`, `--format json`

#### **4. Safe Workflow Processing** (6 commands → `safe_workflow_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --process-inbox-safe` | `python3 development/src/cli/safe_workflow_cli.py process-inbox-safe` |
| `python3 development/src/cli/workflow_demo.py . --batch-process-safe` | `python3 development/src/cli/safe_workflow_cli.py batch-process-safe` |
| `python3 development/src/cli/workflow_demo.py . --performance-report` | `python3 development/src/cli/safe_workflow_cli.py performance-report` |
| `python3 development/src/cli/workflow_demo.py . --integrity-report` | `python3 development/src/cli/safe_workflow_cli.py integrity-report` |
| `python3 development/src/cli/workflow_demo.py . --start-safe-session NAME` | `python3 development/src/cli/safe_workflow_cli.py start-safe-session --session-name NAME` |
| `python3 development/src/cli/workflow_demo.py . --process-in-session ID PATH` | `python3 development/src/cli/safe_workflow_cli.py process-in-session --session-id ID --note-path PATH` |

**Common Options**: `--dry-run`, `--export FILE`, `--session-name NAME`

#### **5. Backup Management** (3 commands → `backup_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --backup` | `python3 development/src/cli/backup_cli.py backup` |
| `python3 development/src/cli/workflow_demo.py . --list-backups` | `python3 development/src/cli/backup_cli.py list-backups` |
| `python3 development/src/cli/workflow_demo.py . --prune-backups --keep N` | `python3 development/src/cli/backup_cli.py prune-backups --keep N` |

**Common Options**: `--keep N`, `--dry-run`, `--export FILE`

#### **6. YouTube Note Processing** (2 commands → `youtube_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --process-youtube-note PATH` | `python3 development/src/cli/youtube_cli.py process-note PATH` |
| `python3 development/src/cli/workflow_demo.py . --process-youtube-notes` | `python3 development/src/cli/youtube_cli.py batch-process` |

**Common Options**: `--dry-run`, `--verbose`

#### **7. Reading Intake Pipeline** (2 commands → `reading_intake_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --import-csv PATH` | `python3 development/src/cli/reading_intake_cli.py import-csv PATH` |
| `python3 development/src/cli/workflow_demo.py . --import-json PATH` | `python3 development/src/cli/reading_intake_cli.py import-json PATH` |

**Common Options**: `--dry-run`, `--format json`

#### **8. Screenshot Processing** (1 command → `screenshot_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --screenshots` | `python3 development/src/cli/screenshot_cli.py process-screenshots` |

**Common Options**: `--onedrive-path PATH`, `--dry-run`, `--progress`

#### **9. Interactive Mode** (1 command → `interactive_cli.py`)

| **Old Command** | **New Dedicated CLI** |
|-----------------|----------------------|
| `python3 development/src/cli/workflow_demo.py . --interactive` | `python3 development/src/cli/interactive_cli.py interactive` |

---

### **Why Migrate?**

✅ **Focused CLIs**: Each CLI handles one domain (weekly review, fleeting notes, etc.)  
✅ **Faster Development**: Bugs found in correct architectural layer  
✅ **Clear Documentation**: Each CLI has specific usage examples  
✅ **Better Testing**: Isolated test suites per CLI  
✅ **Maintainable**: 200-500 LOC per CLI vs 2,128 LOC monolith  
✅ **Faster Performance**: Dedicated CLIs load only required dependencies

---

### **Automation Script Migration Examples**

#### **Example 1: Daily Automation Script**

**Before (workflow_demo.py):**
```bash
#!/bin/bash
# Daily automation - OLD workflow_demo.py approach

VAULT_PATH="."

# Process inbox
python3 development/src/cli/workflow_demo.py $VAULT_PATH --process-inbox --dry-run

# Weekly review on Mondays
if [ $(date +%u) -eq 1 ]; then
    python3 development/src/cli/workflow_demo.py $VAULT_PATH --weekly-review --export-checklist review.md
fi

# Backup
python3 development/src/cli/workflow_demo.py $VAULT_PATH --backup

# Status check
python3 development/src/cli/workflow_demo.py $VAULT_PATH --status
```

**After (Dedicated CLIs):**
```bash
#!/bin/bash
# Daily automation - NEW dedicated CLIs approach

VAULT_PATH="."

# Process inbox
python3 development/src/cli/core_workflow_cli.py process-inbox --dry-run

# Weekly review on Mondays
if [ $(date +%u) -eq 1 ]; then
    python3 development/src/cli/weekly_review_cli.py weekly-review --export-checklist review.md
fi

# Backup
python3 development/src/cli/backup_cli.py backup

# Status check
python3 development/src/cli/core_workflow_cli.py status
```

#### **Example 2: Fleeting Notes Workflow**

**Before:**
```bash
#!/bin/bash
# Check fleeting notes health, triage, and promote high-quality notes

python3 development/src/cli/workflow_demo.py . --fleeting-health
python3 development/src/cli/workflow_demo.py . --fleeting-triage --min-quality 0.7
python3 development/src/cli/workflow_demo.py . --promote-note knowledge/Fleeting\ Notes/note.md
```

**After:**
```bash
#!/bin/bash
# Check fleeting notes health, triage, and promote high-quality notes

python3 development/src/cli/fleeting_cli.py fleeting-health
python3 development/src/cli/fleeting_cli.py fleeting-triage --min-quality 0.7
python3 development/src/cli/fleeting_cli.py promote-note knowledge/Fleeting\ Notes/note.md
```

#### **Example 3: Safe Workflow Processing with Sessions**

**Before:**
```bash
#!/bin/bash
# Safe workflow processing with performance monitoring

python3 development/src/cli/workflow_demo.py . --start-safe-session "morning-processing"
SESSION_ID=$(cat .last_session_id)
python3 development/src/cli/workflow_demo.py . --process-in-session $SESSION_ID knowledge/Inbox/note1.md
python3 development/src/cli/workflow_demo.py . --performance-report
```

**After:**
```bash
#!/bin/bash
# Safe workflow processing with performance monitoring

python3 development/src/cli/safe_workflow_cli.py start-safe-session --session-name "morning-processing"
SESSION_ID=$(cat .last_session_id)
python3 development/src/cli/safe_workflow_cli.py process-in-session --session-id $SESSION_ID --note-path knowledge/Inbox/note1.md
python3 development/src/cli/safe_workflow_cli.py performance-report
```

#### **Example 4: Backup Management with Pruning**

**Before:**
```bash
#!/bin/bash
# Create backup, list all backups, prune old ones

python3 development/src/cli/workflow_demo.py . --backup
python3 development/src/cli/workflow_demo.py . --list-backups
python3 development/src/cli/workflow_demo.py . --prune-backups --keep 5 --dry-run
```

**After:**
```bash
#!/bin/bash
# Create backup, list all backups, prune old ones

python3 development/src/cli/backup_cli.py backup
python3 development/src/cli/backup_cli.py list-backups
python3 development/src/cli/backup_cli.py prune-backups --keep 5 --dry-run
```

---

### **Troubleshooting Common Migration Scenarios**

#### **Problem: "Command not found" after migration**

**Symptom**: `bash: python3: command not found` or CLI file not found

**Solution**:
```bash
# Ensure you're running from project root
cd /path/to/inneros-zettelkasten

# Verify Python is available
which python3

# Check CLI file exists
ls -la development/src/cli/weekly_review_cli.py

# Make sure you're using correct relative path
python3 development/src/cli/weekly_review_cli.py --help
```

#### **Problem: Import errors after migration**

**Symptom**: `ModuleNotFoundError: No module named 'src'`

**Solution**:
```bash
# Run from project root, not from development/
cd /path/to/inneros-zettelkasten

# Set PYTHONPATH if needed
export PYTHONPATH=$(pwd)/development:$PYTHONPATH

# Test import
python3 -c "from src.ai.workflow_manager import WorkflowManager"
```

#### **Problem: Different argument syntax in new CLI**

**Symptom**: `error: unrecognized arguments: .` or missing positional arguments

**Solution**: Dedicated CLIs use subcommands, not flags:
```bash
# OLD: workflow_demo.py . --weekly-review
python3 development/src/cli/workflow_demo.py . --weekly-review

# NEW: Remove vault path '.', use subcommand directly
python3 development/src/cli/weekly_review_cli.py weekly-review

# If vault path needed, use --vault-path option
python3 development/src/cli/weekly_review_cli.py weekly-review --vault-path /custom/path
```

#### **Problem: Automation scripts fail silently**

**Symptom**: Script runs but commands don't execute, no error output

**Solution**: Add error handling and verify each CLI call:
```bash
#!/bin/bash
set -e  # Exit on first error

# Test each CLI individually first
python3 development/src/cli/weekly_review_cli.py --help
python3 development/src/cli/fleeting_cli.py --help

# Add explicit error handling
if ! python3 development/src/cli/core_workflow_cli.py status; then
    echo "Error: status command failed"
    exit 1
fi
```

#### **Problem: Missing options in dedicated CLI**

**Symptom**: Option worked in `workflow_demo.py` but not in dedicated CLI

**Solution**: Check dedicated CLI help for equivalent option:
```bash
# Check what options are available
python3 development/src/cli/weekly_review_cli.py weekly-review --help

# Common option name changes:
# --export-checklist → --export
# . (vault path) → --vault-path PATH
# --keep N → --keep N (same, but check placement)
```

#### **Problem: Need to migrate Templater scripts**

**Symptom**: Obsidian Templater scripts use `workflow_demo.py` commands

**Solution**: Update Templater scripts to use dedicated CLIs:
```javascript
// Before
const result = await tp.user.system("python3 development/src/cli/workflow_demo.py . --status");

// After  
const result = await tp.user.system("python3 development/src/cli/core_workflow_cli.py status");
```

---

### **Verification Checklist**

After migrating, verify your workflows work correctly:

- [ ] **Weekly Review**: Run `python3 development/src/cli/weekly_review_cli.py weekly-review`
- [ ] **Fleeting Notes**: Run `python3 development/src/cli/fleeting_cli.py fleeting-health`
- [ ] **Status Check**: Run `python3 development/src/cli/core_workflow_cli.py status`
- [ ] **Backups**: Run `python3 development/src/cli/backup_cli.py list-backups`
- [ ] **Automation Scripts**: Test each migrated script individually
- [ ] **Templater Scripts**: Verify Obsidian templates using CLI commands work
- [ ] **Cron Jobs**: Update any scheduled tasks to use dedicated CLIs

---

### **Getting Help**

If you encounter migration issues:

1. **Check CLI help**: `python3 development/src/cli/[CLI_NAME] --help`
2. **Review this guide**: Complete command mapping table above
3. **Test incrementally**: Migrate one command at a time
4. **Use dry-run mode**: Test with `--dry-run` before making changes
5. **Check logs**: Enable `--verbose` for detailed output

---

## 🛠️ **Command Migration Reference** (Legacy Structure)

### **Analytics & Reports**
| **Before** | **After (Recommended)** |
|------------|-------------------------|
| `python3 src/cli/analytics_demo.py . --interactive` | `inneros analytics --interactive` |
| `python3 src/cli/analytics_demo.py . --section quality` | `inneros analytics --section quality` |
| `python3 src/cli/analytics_demo.py . --export report.json` | `inneros analytics --export report.json` |

### **Note Enhancement**
| **Before** | **After (Recommended)** |
|------------|-------------------------|
| `python3 src/cli/enhance_demo.py note.md` | `inneros enhance knowledge/Inbox/note.md` |
| `python3 src/cli/enhance_demo.py note.md --full` | `inneros enhance knowledge/Inbox/note.md --full` |

## 🎯 **Quick Start Guide**

### **1. Verify Your Setup**
```bash
# Check that you can access the wrapper
./inneros --help

# Test analytics on your knowledge collection
inneros analytics
```

### **2. Update Your Workflows**
```bash
# Check workflow health
inneros workflow --status

# Process any inbox notes
inneros workflow --process-inbox
```

### **3. Open Knowledge Vault in Obsidian**
- Open Obsidian
- Open `knowledge/` directory as your vault
- Everything should work exactly as before

## 🔧 **Developer Migration**

### **Running Tests**
```bash
# Old way
pytest tests/

# New way (from project root)
cd development
pytest tests/

# Or with PYTHONPATH
PYTHONPATH=development python3 -m pytest development/tests/
```

### **Import Paths**
```python
# Old imports
from src.ai.tagger import AITagger
from src.ai.analytics import NoteAnalytics

# New imports (if developing)
from src.ai.tagger import AITagger  # Same! (from development/ directory)
from src.ai.analytics import NoteAnalytics  # Same! (from development/ directory)
```

## 🆘 **Troubleshooting**

### **"Command not found: inneros"**
```bash
# Make sure the script is executable
chmod +x inneros

# Run from project root directory
cd /path/to/inneros-zettelkasten
./inneros --help
```

### **"Module not found" errors**
```bash
# Make sure you're running from the project root
pwd  # Should show your inneros-zettelkasten directory

# For developers, set PYTHONPATH
export PYTHONPATH=$(pwd)/development:$PYTHONPATH
```

### **Obsidian can't find notes**
- Open `knowledge/` directory as your vault (not the project root)
- Check that `.obsidian/` folder exists in `knowledge/`
- Verify templates are in `knowledge/Templates/`

### **Old Python scripts not working**
```bash
# From project root, you can still use old commands:
python3 development/src/cli/analytics_demo.py knowledge/ --interactive

# But the new way is simpler:
inneros analytics --interactive
```

## ✅ **Verification Steps**

After migration, verify everything works:

```bash
# 1. Test unified CLI
inneros analytics --section overview
inneros workflow --status

# 2. Test Obsidian vault
# Open knowledge/ in Obsidian - should work normally

# 3. Test note creation
# Create a test note in knowledge/Inbox/
inneros enhance knowledge/Inbox/test-note.md

# 4. Test weekly review
inneros workflow --weekly-review
```

## 🎉 **Benefits of New Structure**

### **For Knowledge Workers**
- **Cleaner Obsidian experience** - no code files cluttering note navigation
- **Simplified commands** - `inneros` instead of long Python commands
- **Faster workflows** - unified CLI with sensible defaults

### **For Developers**
- **Clear separation** - code in `development/`, notes in `knowledge/`
- **Better organization** - tests, demos, docs properly grouped
- **Maintainable architecture** - easier to extend and modify

### **For Everyone**
- **Future-proof** - ready for collaboration features and web interface
- **Professional structure** - follows software development best practices
- **Preserved functionality** - everything works exactly as before, just better organized

---

## 📞 **Need Help?**

If you encounter issues during migration:

1. **Check this guide** - most common issues are covered above
2. **Verify file locations** - make sure `knowledge/` contains your notes
3. **Test step-by-step** - use the verification steps to isolate problems
4. **Check permissions** - ensure `inneros` script is executable

The migration preserves all functionality while making the system more maintainable and user-friendly!
