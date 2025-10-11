# InnerOS Zettelkasten - CLI Command Reference

> **Complete reference for dedicated CLI tools and the unified `inneros` wrapper**  
> **Updated**: 2025-10-11 (ADR-004 CLI Layer Extraction Complete)

## 🚀 **Overview**

InnerOS provides two ways to interact with the knowledge management system:

### **Dedicated CLIs** (Recommended)
Focused, single-purpose command-line tools extracted per ADR-004:
- `weekly_review_cli.py` - Weekly review generation and metrics
- `fleeting_cli.py` - Fleeting note health and triage
- `safe_workflow_cli.py` - Safe processing with image preservation
- `core_workflow_cli.py` - Core workflow operations (status, inbox, promote)
- `backup_cli.py` - Backup management and pruning
- `interactive_cli.py` - Interactive workflow mode
- Plus 4 specialized CLIs (YouTube, tags, notes, performance)

### **Unified Wrapper** (Legacy)
The `inneros` wrapper provides backward compatibility:
```bash
# General usage
./inneros <command> [options]

# Available commands  
inneros analytics    # Analyze knowledge collection
inneros workflow     # Manage knowledge workflows (⚠️ see migration guide)
inneros enhance      # AI-enhance specific notes
inneros notes        # Create review notes from templates
```

> **Migration Note**: The monolithic `workflow_demo.py` is deprecated. See [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for transition to dedicated CLIs.

---

## 📋 **Dedicated CLIs** (ADR-004 Extraction)

### **Weekly Review CLI** (`weekly_review_cli.py`)

Generate weekly review checklists and enhanced metrics.

**Commands:**
```bash
# Generate weekly review checklist
python3 development/src/cli/weekly_review_cli.py weekly-review

# Enhanced metrics with orphaned/stale note detection
python3 development/src/cli/weekly_review_cli.py enhanced-metrics

# Export checklist to file
python3 development/src/cli/weekly_review_cli.py weekly-review --export-checklist review.md

# JSON output for automation
python3 development/src/cli/weekly_review_cli.py weekly-review --format json
```

**Options:**
- `--export-checklist PATH` - Export markdown checklist to file
- `--format {text,json}` - Output format (default: text)
- `--dry-run` - Preview without processing

**Use Cases:**
- Weekly knowledge work review
- Identify promotion candidates
- Find orphaned/stale notes
- Generate action items

---

### **Fleeting Notes CLI** (`fleeting_cli.py`)

Health monitoring and AI-powered triage for fleeting notes.

**Commands:**
```bash
# Health report with age analysis
python3 development/src/cli/fleeting_cli.py fleeting-health

# AI-powered quality triage
python3 development/src/cli/fleeting_cli.py fleeting-triage

# Export triage results
python3 development/src/cli/fleeting_cli.py fleeting-triage --export triage-report.md
```

**Options:**
- `--vault PATH` - Vault path (default: current directory)
- `--export PATH` - Export report to file
- `--format {text,json}` - Output format

**Use Cases:**
- Monitor fleeting note aging
- AI quality assessment
- Identify promotion candidates
- Track fleeting→permanent conversion rate

---

### **Safe Workflow CLI** (`safe_workflow_cli.py`)

Safe processing operations with image preservation and backup guarantees.

**Commands:**
```bash
# Process inbox with image preservation
python3 development/src/cli/safe_workflow_cli.py process-inbox-safe

# Batch processing with safety guarantees
python3 development/src/cli/safe_workflow_cli.py batch-process-safe

# Performance metrics
python3 development/src/cli/safe_workflow_cli.py performance-report

# Image integrity monitoring
python3 development/src/cli/safe_workflow_cli.py integrity-report

# Create timestamped backup
python3 development/src/cli/safe_workflow_cli.py backup

# List available backups
python3 development/src/cli/safe_workflow_cli.py list-backups

# Start concurrent safe session
python3 development/src/cli/safe_workflow_cli.py start-safe-session --session-name evening-batch
```

**Options:**
- `--vault PATH` - Vault root path
- `--dry-run` - Preview changes without executing
- `--format {text,json}` - Output format
- `--session-name NAME` - Session identifier for concurrent processing

**Use Cases:**
- Process notes without breaking image links
- Batch operations with rollback capability
- Performance monitoring
- Concurrent processing sessions

---

### **Core Workflow CLI** (`core_workflow_cli.py`)

Core workflow operations for inbox processing and note promotion.

**Commands:**
```bash
# Workflow status report
python3 development/src/cli/core_workflow_cli.py status

# Batch process inbox notes
python3 development/src/cli/core_workflow_cli.py process-inbox

# Promote note to permanent/literature
python3 development/src/cli/core_workflow_cli.py promote path/to/note.md permanent

# Comprehensive workflow report
python3 development/src/cli/core_workflow_cli.py report --export report.json
```

**Options:**
- `--vault PATH` - Vault root path (default: current directory)
- `--format {text,json}` - Output format
- `--export PATH` - Export report to file
- `--dry-run` - Preview operations

**Use Cases:**
- Daily inbox processing
- Note promotion workflows
- Workflow health monitoring
- Comprehensive reporting

---

### **Backup CLI** (`backup_cli.py`)

Backup management and pruning operations.

**Commands:**
```bash
# Prune old backups (keep 5 most recent)
python3 development/src/cli/backup_cli.py prune-backups --keep 5

# Dry-run mode
python3 development/src/cli/backup_cli.py prune-backups --keep 3 --dry-run

# JSON output
python3 development/src/cli/backup_cli.py prune-backups --keep 5 --format json
```

**Options:**
- `--keep N` - Number of recent backups to keep (default: 5)
- `--dry-run` - Preview deletions without removing
- `--format {text,json}` - Output format

**Use Cases:**
- Regular backup cleanup
- Storage management
- Backup inventory

---

### **Interactive CLI** (`interactive_cli.py`)

Interactive workflow management with command loop.

**Commands:**
```bash
# Start interactive mode
python3 development/src/cli/interactive_cli.py interactive

# With specific vault
python3 development/src/cli/interactive_cli.py interactive --vault /path/to/vault
```

**Interactive Commands:**
- `status` - Show workflow status
- `inbox` - Process inbox notes
- `promote <file> [type]` - Promote note to permanent/fleeting
- `report` - Generate full workflow report
- `list <directory>` - List notes (inbox|fleeting|permanent)
- `help` - Show help
- `quit` - Exit

**Use Cases:**
- Exploratory workflow management
- Quick status checks
- Interactive note promotion

---

### **YouTube CLI** (`youtube_cli.py`)

YouTube transcript processing and note generation.

**Commands:**
```bash
# Process YouTube video
python3 development/src/cli/youtube_cli.py process VIDEO_URL

# Batch process from file
python3 development/src/cli/youtube_cli.py batch urls.txt
```

**Options:**
- `--output DIR` - Output directory for notes
- `--format {text,json}` - Output format

---

### **Advanced Tag Enhancement CLI** (`advanced_tag_enhancement_cli.py`)

AI-powered tag quality enhancement and suggestions.

**Commands:**
```bash
# Analyze tag quality
python3 development/src/cli/advanced_tag_enhancement_cli.py analyze-tags

# Generate tag suggestions
python3 development/src/cli/advanced_tag_enhancement_cli.py suggest-improvements

# Batch enhancement
python3 development/src/cli/advanced_tag_enhancement_cli.py batch-enhance
```

**Use Cases:**
- Tag quality improvement
- Semantic tag organization
- Bulk tag enhancement

---

### **Notes CLI** (`notes_cli.py`)

Review note creation from templates.

**Commands:**
```bash
# Create daily review note
python3 development/src/cli/notes_cli.py new --daily

# Create weekly review note
python3 development/src/cli/notes_cli.py new --weekly

# Create sprint review
python3 development/src/cli/notes_cli.py new --sprint-review --sprint-id 012

# Open in editor
python3 development/src/cli/notes_cli.py new --daily --open

# Auto-commit
python3 development/src/cli/notes_cli.py new --weekly --git
```

---

### **Performance CLI** (`real_data_performance_cli.py`)

System performance benchmarking and validation.

**Commands:**
```bash
# Run performance benchmarks
python3 development/src/cli/real_data_performance_cli.py benchmark

# Validate real data processing
python3 development/src/cli/real_data_performance_cli.py validate
```

---

## 📝 **Notes Command**

Create review notes (daily, weekly, sprint review, sprint retrospective) with proper frontmatter and minimal body templates. Files are written atomically, with optional editor open and git commit.

### **Basic Usage**
```bash
inneros notes [PATH] new (--daily | --weekly | --sprint-review | --sprint-retro) \
  [--sprint-id ID] [--dir REVIEWS_DIR] [--open] [--editor CMD] [--git]
```

### **Options**
```bash
PATH                 # Repo root or knowledge dir (default: .)
--daily              # Create daily review note
--weekly             # Create weekly review note
--sprint-review      # Create sprint review note (requires --sprint-id)
--sprint-retro       # Create sprint retrospective note (requires --sprint-id)
--sprint-id ID       # Sprint identifier, e.g., 001
--dir REVIEWS_DIR    # Override Reviews directory path
--open               # Open created note in your editor (uses $VISUAL/$EDITOR if unset)
--editor CMD         # Explicit editor command
--git                # git add + commit the new note
```

### **Examples**
```bash
# Daily note for today, open in editor
inneros notes new --daily --open

# Weekly review with auto commit
inneros notes new --weekly --git

# Sprint review for sprint 012
inneros notes new --sprint-review --sprint-id 012 --open --git

# Sprint retrospective to a custom Reviews dir
inneros notes new --sprint-retro --sprint-id 012 --dir Reviews/
```

#### Frontmatter Schema (generated by `notes new`)
- All review notes use a unified schema:
  - `type: review`
  - `scope: daily | weekly | sprint-review | sprint-retrospective`
  - Common fields: `created`, `status`, `visibility`, `tags` (no leading `#`)
- Daily:
  - `week_id: YYYY-Www`
- Weekly:
  - `week_id: YYYY-Www`, `period_start: YYYY-MM-DD`, `period_end: YYYY-MM-DD`
- Sprint Review / Retrospective:
  - `sprint_id: <ID>`, `tz: America/Los_Angeles`

This aligns with the project’s unified review model and preserves backward compatibility.

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

# Create a weekly review note file (template + frontmatter)
inneros notes new --weekly --open

# Export analytics for deeper analysis
inneros analytics --export weekly-analytics.json
```

### **Review Templates (Obsidian Templater — optional)**
- Templates live in `knowledge/Templates/`: `daily.md`, `weekly-review.md`, `sprint-review.md`, `sprint-retro.md`.
- Obsidian: Command Palette → “Templater: Insert template”, then select a template.
- Behavior: renames to canonical name, moves into `Reviews/`, and stamps `created` in America/Los_Angeles.
- Sprint templates prompt for `sprint_id` (e.g., 001).
- Actions are tracked in-note only.
- Alternative (no Obsidian required): use the CLI — e.g., `inneros notes new --daily` or `inneros notes new --sprint-retro --sprint-id 012`.

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
