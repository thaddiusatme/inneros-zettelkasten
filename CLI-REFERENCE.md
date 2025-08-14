# InnerOS Zettelkasten - CLI Command Reference

> **Complete reference for the unified `inneros` CLI wrapper**  
> **Updated**: 2025-08-05

## 🚀 **Overview**

The `inneros` CLI provides unified access to all AI-powered knowledge management features through simple, memorable commands.

```bash
# General usage
./inneros <command> [options]

# Available commands
inneros analytics    # Analyze knowledge collection
inneros workflow     # Manage knowledge workflows  
inneros enhance      # AI-enhance specific notes
```

---

## 📊 **Analytics Command**

Analyze your knowledge collection with comprehensive metrics and insights.

### **Basic Usage**
```bash
# Quick overview of your knowledge collection
inneros analytics

# Interactive exploration mode
inneros analytics --interactive

# Specific analysis section
inneros analytics --section quality
```

### **All Options**
```bash
inneros analytics [PATH] [OPTIONS]

Arguments:
  PATH                    # Path to analyze (default: knowledge/)

Options:
  --format {text,json}    # Output format (default: text)
  --export FILENAME       # Export report to JSON file
  --interactive           # Run in interactive mode
  --section SECTION       # Show specific section only

Sections:
  overview               # Total notes, words, quality scores
  distributions          # Note type and status distributions
  quality               # Quality score analysis and recommendations
  temporal              # Creation patterns and date insights
  recommendations       # Actionable improvement suggestions
  insights              # AI-generated insights and patterns
```

### **Examples**
```bash
# Basic analysis
inneros analytics

# Interactive mode with full exploration
inneros analytics --interactive

# Focus on quality metrics only
inneros analytics --section quality

# Export comprehensive report
inneros analytics --export knowledge-report.json

# Analyze specific directory
inneros analytics /path/to/custom/notes

# JSON output for automation
inneros analytics --format json
```

---

## 🔄 **Workflow Command**

Manage knowledge workflows with AI-assisted processing and automation.

### **Basic Usage**
```bash
# Check workflow health status
inneros workflow --status

# Process inbox notes with AI assistance
inneros workflow --process-inbox

# Generate weekly review
inneros workflow --weekly-review
```

### **All Options**
```bash
inneros workflow [PATH] [OPTIONS]

Arguments:
  PATH                     # Path to knowledge directory (default: knowledge/)

Options:
  --status                 # Show workflow status
  --process-inbox          # Process all inbox notes
  --report                 # Generate full workflow report
  --interactive            # Run in interactive mode
  --weekly-review          # Generate weekly review checklist
  --enhanced-metrics       # Enhanced metrics with orphaned/stale detection
  --remediate-orphans      # Remediate orphaned notes (insert links or checklist)
  --remediate-mode MODE    # Remediation mode: link|checklist (default: link)
  --remediate-scope SCOPE  # Scope: permanent|fleeting|all (default: permanent)
  --remediate-limit N      # Max number of orphans to process (default: 10)
  --target-note PATH       # Explicit target note/MOC (relative to vault or absolute)
  --apply                  # Apply changes (disable dry-run); default is dry-run preview
  --format {text,json}     # Output format (default: text)
  --export FILENAME        # Export report to JSON file
  --export-checklist PATH  # Export weekly review checklist to markdown
  --dry-run                # Preview recommendations without processing
```

### **Examples**
```bash
# Quick health check
inneros workflow --status

# Process inbox with AI tagging and quality assessment
inneros workflow --process-inbox

# Preview what would be processed (safe)
inneros workflow --process-inbox --dry-run

# Generate weekly review checklist
inneros workflow --weekly-review

# Export weekly review to markdown file
inneros workflow --weekly-review --export-checklist weekly-review.md

# Enhanced metrics with orphaned note detection
inneros workflow --enhanced-metrics

# Orphan remediation (dry-run by default)
inneros workflow --remediate-orphans --remediate-scope permanent --remediate-limit 5

# Apply link insertions to Home Note (be careful; creates backups)
inneros workflow --remediate-orphans --apply --target-note "knowledge/Home Note.md" \
  --remediate-scope permanent --remediate-limit 10

# Generate a remediation checklist instead of making changes
inneros workflow --remediate-orphans --remediate-mode checklist --export checklist.md

# Interactive workflow management
inneros workflow --interactive

# Full workflow report in JSON
inneros workflow --report --format json --export workflow-report.json

# Work with custom directory
inneros workflow /path/to/custom/knowledge --status
```

---

## 🤖 **Enhance Command**

AI-enhance individual notes with quality assessment, suggestions, and improvements.

### **Basic Usage**
```bash
# Basic enhancement of a note
inneros enhance knowledge/Inbox/my-note.md

# Full enhancement report
inneros enhance knowledge/Inbox/my-note.md --full
```

### **All Options**
```bash
inneros enhance FILE [OPTIONS]

Arguments:
  FILE                     # Path to note file to enhance (required)

Options:
  --model MODEL            # Ollama model to use (default: llama3:latest)
  --min-score SCORE        # Minimum quality score threshold (default: 0.3)
  --links                  # Show link suggestions
  --structure              # Show structure suggestions
  --full                   # Show full enhancement report
```

### **Examples**
```bash
# Basic enhancement
inneros enhance knowledge/Inbox/idea-note.md

# Full enhancement with all suggestions
inneros enhance knowledge/Fleeting\ Notes/research.md --full

# Focus on link suggestions
inneros enhance knowledge/Permanent\ Notes/concept.md --links

# Use different AI model
inneros enhance knowledge/Inbox/draft.md --model mistral:latest

# Lower quality threshold for more suggestions
inneros enhance knowledge/Inbox/rough-note.md --min-score 0.1

# Structure-focused enhancement
inneros enhance knowledge/Literature/book-notes.md --structure
```

---

## 🎯 **Common Workflows**

### **Daily Knowledge Work**
```bash
# Morning routine: check system health
inneros workflow --status

# Process any new inbox items
inneros workflow --process-inbox

# Enhance a specific note you're working on
inneros enhance knowledge/Inbox/todays-idea.md --full
```

### **Weekly Review**
```bash
# Generate comprehensive weekly metrics
inneros workflow --enhanced-metrics

# Create weekly review checklist
inneros workflow --weekly-review --export-checklist this-week.md

# Export analytics for deeper analysis
inneros analytics --export weekly-analytics.json
```

### **Review Templates (Obsidian Templater)**
- Templates live in `knowledge/Templates/`: `daily.md`, `weekly-review.md`, `sprint-review.md`, `sprint-retro.md`.
- Obsidian: Command Palette → “Templater: Insert template”, then select a template.
- Behavior: renames to canonical name, moves into `Reviews/`, and stamps `created` in America/Los_Angeles.
- Sprint templates prompt for `sprint_id` (e.g., 001).
- Actions are tracked in-note only.

### **Knowledge Audit**
```bash
# Full system analysis
inneros analytics --interactive

# Find orphaned and stale notes
inneros workflow --enhanced-metrics

# Quality assessment across collection
inneros analytics --section quality
```

### **Automation & Integration**
```bash
# JSON outputs for scripting
inneros analytics --format json > analytics.json
inneros workflow --report --format json > workflow.json

# Batch processing
find knowledge/Inbox -name "*.md" -exec inneros enhance {} \;
```

---

## ⚙️ **Configuration & Setup**

### **Prerequisites**
```bash
# Ensure Ollama is running
ollama serve

# Verify models are available
ollama list
# Should show: llama3:latest (or your preferred model)
```

### **Permissions**
```bash
# Ensure inneros script is executable
chmod +x inneros

# Verify it works
./inneros --help
```

### **Directory Structure**
The CLI expects this directory structure:
```
/your-project-root/
├── inneros              # CLI wrapper script
├── development/         # Python code and tests
├── knowledge/          # Default knowledge directory
│   ├── Inbox/          # New notes staging
│   ├── Fleeting Notes/ # Quick captures
│   ├── Permanent Notes/ # Processed knowledge
│   └── Templates/      # Obsidian templates
```

---

## 🔧 **Advanced Usage**

### **Custom Paths**
```bash
# Work with different knowledge directories
inneros analytics ~/Documents/MyNotes
inneros workflow ~/Research/Papers --status
inneros enhance ~/Projects/idea.md
```

### **Automation Examples**
```bash
#!/bin/bash
# Daily automation script

echo "🌅 Daily Knowledge System Check"

# Health check
inneros workflow --status

# Process new items
inneros workflow --process-inbox --dry-run

# Quick analytics
inneros analytics --section overview
```

### **Integration with Other Tools**
```bash
# Export to tools like jq for JSON processing
inneros analytics --format json | jq '.quality_metrics'

# Use with git hooks
git add -A && inneros workflow --status && git commit -m "Knowledge update"

# Combine with find for bulk operations
find knowledge/Inbox -name "*.md" -newer yesterday \
  -exec inneros enhance {} --links \;
```

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### Command not found
```bash
# Ensure you're in the project root
pwd
ls inneros  # Should exist

# Make executable
chmod +x inneros
```

#### AI model errors
```bash
# Check Ollama is running
ollama ps

# Verify model exists
ollama list | grep llama3

# Pull model if needed
ollama pull llama3:latest
```

#### Permission errors
```bash
# Check file permissions
ls -la knowledge/
# Ensure directories are readable

# Fix permissions if needed
chmod -R u+rw knowledge/
```

### **Performance Tips**
- Use `--dry-run` for safe testing
- Use `--section` for focused analytics
- Use JSON format for automation
- Process smaller batches for large collections

### **Getting Help**
```bash
# General help
inneros --help

# Command-specific help
inneros analytics --help
inneros workflow --help
inneros enhance --help
```

---

## 📈 **Output Examples**

### **Analytics Overview**
```
🔍 Analyzing notes in: knowledge/
📊 Generating analytics report...

============================================================
  ZETTELKASTEN ANALYTICS REPORT
============================================================
Generated: 2025-08-05 17:17:47
Directory: knowledge/

📊 OVERVIEW STATISTICS
----------------------------------------
   Total Notes              : 164
   Total Words              : 36,834
   Average Words/Note       : 224.60
   Average Quality Score    : 0.44/1.0
   Notes with AI Summaries  : 0
   Total Internal Links     : 176
   Average Links/Note       : 1.10
```

### **Workflow Status**
```
🔄 WORKFLOW STATUS
----------------------------------------
   Health Status: ✅ HEALTHY
   Total Notes: 114

   Directory Distribution:
     Inbox               :    9
     Fleeting Notes      :   32
     Permanent Notes     :   54
     Archive             :   19

🔄 AI FEATURE USAGE
----------------------------------------
   AI Summaries   :   0/164 (  0.0%)
   AI Processing  :  31/164 ( 18.9%)
   AI Tags        :  31/164 ( 18.9%)
```

### **Note Enhancement**
```
🤖 AI Content Enhancement Analysis
📄 File: knowledge/Inbox/my-idea.md
🧠 Model: llama3:latest
==================================================
📊 Quality Score: 0.85/1.0

💡 Suggestions:
  • Add practical examples
  • Include links to related concepts
  • Expand on technical details
```

This CLI reference provides comprehensive documentation for all `inneros` commands and usage patterns!
