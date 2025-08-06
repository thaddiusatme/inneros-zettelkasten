# InnerOS Zettelkasten - Migration Guide

> **For existing users migrating to the reorganized project structure**  
> **Updated**: 2025-08-05

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

## 🛠️ **Command Migration Reference**

### **Analytics & Reports**
| **Before** | **After (Recommended)** |
|------------|-------------------------|
| `python3 src/cli/analytics_demo.py . --interactive` | `inneros analytics --interactive` |
| `python3 src/cli/analytics_demo.py . --section quality` | `inneros analytics --section quality` |
| `python3 src/cli/analytics_demo.py . --export report.json` | `inneros analytics --export report.json` |

### **Workflow Management**
| **Before** | **After (Recommended)** |
|------------|-------------------------|
| `python3 src/cli/workflow_demo.py . --status` | `inneros workflow --status` |
| `python3 src/cli/workflow_demo.py . --process-inbox` | `inneros workflow --process-inbox` |
| `python3 src/cli/workflow_demo.py . --weekly-review` | `inneros workflow --weekly-review` |
| `python3 src/cli/workflow_demo.py . --enhanced-metrics` | `inneros workflow --enhanced-metrics` |

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
