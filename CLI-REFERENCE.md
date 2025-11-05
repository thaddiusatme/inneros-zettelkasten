# InnerOS Zettelkasten - CLI Command Reference

> **Complete reference for dedicated CLI tools and the unified `inneros` wrapper**  
> **Updated**: 2025-11-04 (Issue #39 Automation Script CLI Migration Complete)

## 🚀 **Overview**

InnerOS provides two ways to interact with the knowledge management system:

### **Dedicated CLIs** (Recommended)
Focused, single-purpose command-line tools extracted per ADR-004:
- `core_workflow_cli.py` - Core workflow operations (status, inbox, promote)
- `safe_workflow_cli.py` - Safe processing with image preservation
- `fleeting_cli.py` - Fleeting note health and triage
- `weekly_review_cli.py` - Weekly review generation and metrics
- `connections_demo.py` - Note connection discovery and link suggestions
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
inneros workflow     # Manage knowledge workflows (⚠️ DEPRECATED - use dedicated CLIs)
inneros enhance      # AI-enhance specific notes
inneros notes        # Create review notes from templates
```

> **✅ Migration Complete**: All automation scripts migrated to dedicated CLIs (Issue #39). The monolithic `workflow_demo.py` is deprecated except for evening-screenshots (pending extraction). See migration guide below.

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

# Create review notes (daily, weekly, sprint review, sprint retrospective) with proper frontmatter and minimal body templates.
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

## 🔄 **Workflow Command** ⚠️ **DEPRECATED**

> **⚠️ DEPRECATION NOTICE**: The `inneros workflow` wrapper is deprecated as of October 2025 (ADR-004).  
> **Migration Required**: Use dedicated CLIs listed above for all workflow operations.  
> **Timeline**: `workflow_demo.py` will be removed November 11, 2025.  
> **See**: [MIGRATION-GUIDE.md](MIGRATION-GUIDE.md) for complete migration instructions.

### **Migration Quick Reference**

Instead of `inneros workflow`, use these dedicated CLIs:

| **Old Workflow Command** | **New Dedicated CLI** |
|--------------------------|----------------------|
| `inneros workflow --status` | `python3 development/src/cli/core_workflow_cli.py status` |
| `inneros workflow --process-inbox` | `python3 development/src/cli/core_workflow_cli.py process-inbox` |
| `inneros workflow --weekly-review` | `python3 development/src/cli/weekly_review_cli.py weekly-review` |
| `inneros workflow --enhanced-metrics` | `python3 development/src/cli/weekly_review_cli.py enhanced-metrics` |
| `inneros workflow --remediate-orphans` | `python3 development/src/cli/weekly_review_cli.py remediate-orphans` |
| `inneros workflow --interactive` | `python3 development/src/cli/interactive_cli.py interactive` |

**See "Dedicated CLIs" section above** for complete command reference with all options.

### **Legacy Examples (For Reference Only)**

<details>
<summary>Click to expand legacy inneros workflow examples</summary>

**⚠️ These examples are deprecated. Use dedicated CLIs instead.**

```bash
# Quick health check (OLD)
inneros workflow --status
# NEW: python3 development/src/cli/core_workflow_cli.py status

# Process inbox (OLD)
inneros workflow --process-inbox
# NEW: python3 development/src/cli/core_workflow_cli.py process-inbox

# Generate weekly review (OLD)
inneros workflow --weekly-review
# NEW: python3 development/src/cli/weekly_review_cli.py weekly-review

# Enhanced metrics (OLD)
inneros workflow --enhanced-metrics
# NEW: python3 development/src/cli/weekly_review_cli.py enhanced-metrics

# Orphan remediation (OLD)
inneros workflow --remediate-orphans --remediate-scope permanent --remediate-limit 5
# NEW: python3 development/src/cli/weekly_review_cli.py remediate-orphans --scope permanent --limit 5
```

</details>

### **Why Migrate?**

- ✅ **Faster Performance**: Dedicated CLIs load only required dependencies
- ✅ **Clearer Errors**: Issues identified in correct architectural layer
- ✅ **Better Documentation**: Each CLI has focused, specific examples
- ✅ **Maintainable**: 200-500 LOC per CLI vs 2,128 LOC monolith
- ✅ **Active Development**: New features added to dedicated CLIs only

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

---

## 📋 **CLI Migration Guide** (Issue #39)

### Migration Status: ✅ Complete (5/5 automation scripts migrated)

All automation scripts in `.automation/scripts/` have been successfully migrated from the deprecated `workflow_demo.py` to dedicated CLIs.

### Command Mapping Table

| workflow_demo.py Command | Dedicated CLI Command | Notes |
|-------------------------|----------------------|-------|
| `--status` | `core_workflow_cli.py --vault <path> status` | Read-only health check |
| `--backup` | `safe_workflow_cli.py --vault <path> backup` | Creates timestamped backup |
| `--process-inbox` | `core_workflow_cli.py --vault <path> process-inbox` | With optional `--fast` for dry-run |
| `--process-inbox --dry-run` | `core_workflow_cli.py --vault <path> process-inbox --fast` | Fast mode = dry-run |
| `--fleeting-triage --min-quality X` | `fleeting_cli.py --vault <path> fleeting-triage --quality-threshold X` | Note argument name change |
| `--fleeting-health` | `fleeting_cli.py --vault <path> fleeting-health` | Age analysis and stale note detection |
| `--suggest-links` | `connections_demo.py <note-path> <vault> suggest-links` | Requires manual note path |
| `--weekly-review` | `weekly_review_cli.py --vault <path> weekly-review` | Generate review checklist |
| `--evening-screenshots` | **TEMPORARY**: `workflow_demo.py --vault <path> --evening-screenshots` | Pending extraction (P2_TASK_3) |

### Key Changes

**Argument Name Variations:**
- `--min-quality` → `--quality-threshold` (fleeting_cli.py)
- `--dry-run` → `--fast` (core_workflow_cli.py)
- `--vault` flag now required before subcommands

**Subcommand Pattern:**
All dedicated CLIs follow consistent pattern:
```bash
<cli_name>.py --vault <path> <subcommand> [options]
```

### Migrated Automation Scripts

1. ✅ `automated_screenshot_import.sh` (Iteration 1)
2. ✅ `supervised_inbox_processing.sh` (Iteration 2)
3. ✅ `weekly_deep_analysis.sh` (Iteration 3)
4. ✅ `process_inbox_workflow.sh` (Iteration 4)
5. ✅ `health_monitor.sh` (Iteration 5)

**Only Remaining workflow_demo.py Usage:**
- `process_inbox_workflow.sh`: evening-screenshots only (documented TEMPORARY)

### For Users of workflow_demo.py

**If you have custom scripts using workflow_demo.py:**
1. Identify which commands you're using
2. Look up the dedicated CLI equivalent in the table above
3. Update your scripts with the new CLI paths and argument names
4. Test with `--help` to verify correct syntax

**Example Migration:**
```bash
# Before (deprecated)
python3 development/src/cli/workflow_demo.py knowledge/ --status --process-inbox --dry-run

# After (dedicated CLIs)
python3 development/src/cli/core_workflow_cli.py --vault knowledge/ status
python3 development/src/cli/core_workflow_cli.py --vault knowledge/ process-inbox --fast
```

### CI Validation

All migrated CLIs are validated in CI through smoke tests:
- `.github/workflows/cli-smoke-tests.yml`
- Runs `--help` on all dedicated CLIs
- Ensures CLIs are functional before deployment

---

This CLI reference provides comprehensive documentation for all `inneros` commands and usage patterns!
