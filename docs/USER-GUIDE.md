# InnerOS User Guide

> **Your AI-Powered Knowledge Management System**  
> **Version**: 2.0 (December 2025)  
> **Status**: Production Ready - 42 E2E tests passing

---

## Quick Start (5 Commands)

These are the only commands you need for daily use:

```bash
make status    # Check system health - run this first
make up        # Start automation daemon
make down      # Stop automation daemon
make review    # See notes needing attention
make fleeting  # Check fleeting notes health
```

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Daily Workflow](#daily-workflow)
3. [Feature Guides](#feature-guides)
   - [YouTube Quote Extraction](#youtube-quote-extraction)
   - [Smart Link Suggestions](#smart-link-suggestions)
   - [Screenshot Import](#screenshot-import)
   - [Weekly Review](#weekly-review)
4. [Automation Setup](#automation-setup)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.12+
- Ollama with `llama3.2-vision` (for OCR) and `gpt-oss:20b` or similar (for text)
- `youtube-transcript-api` package (for YouTube workflow)
- Obsidian (optional, for viewing notes)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/inneros-zettelkasten.git
cd inneros-zettelkasten

# Install dependencies
make setup

# Verify installation
make status
```

### Directory Structure

```
inneros-zettelkasten/
├── knowledge/           # Your notes live here
│   ├── Inbox/          # New notes, unprocessed
│   ├── Fleeting Notes/ # Quick captures
│   ├── Literature Notes/
│   └── Permanent Notes/ # Promoted, high-quality notes
├── development/        # Code and automation
└── docs/              # Documentation (you are here)
```

---

## Daily Workflow

### Morning Routine (2 minutes)

```bash
# 1. Check system status
make status

# 2. Start automation if needed
make up

# 3. Review pending items
make review
```

### What Each Command Shows

**`make status`** - System health at a glance:
- Daemon status (running/stopped)
- Active handlers (Screenshot, Smart Link, YouTube)
- Pending notes count
- Recent activity

**`make review`** - Notes needing attention:
- Notes in Inbox/ ready for promotion
- Notes with AI quality scores
- Recommendations for each note

**`make fleeting`** - Fleeting notes health:
- Age distribution (how old are your notes?)
- Promotion candidates
- Backlog status

---

## Feature Guides

### YouTube Quote Extraction

**What it does**: Automatically extracts key quotes from YouTube videos you're watching.

#### Creating a YouTube Note

1. Create a note in `Inbox/` with this frontmatter:

```yaml
---
title: "Video Title Here"
created: 2025-12-04
source: youtube
video_id: dQw4w9WgXcQ
url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
ready_for_processing: false
tags: [youtube]
---

# Video Title

Your notes about this video...
```

> ⚠️ **Important**: The `url:` field is required (not `video_url:`). The CLI looks for this exact field name.

2. When you're ready for AI to extract quotes, change:
```yaml
ready_for_processing: true
```

3. Save the file. The automation daemon will:
   - Fetch the video transcript
   - Extract key insights using AI
   - Add quotes to your note
   - Mark it as `ai_processed: true`

#### Manual Processing

```bash
# Process a specific YouTube note (from repo root)
cd ~/repos/inneros-zettelkasten/development
PYTHONPATH=. python3 src/cli/youtube_cli.py --vault ../knowledge process-note "../knowledge/Inbox/YouTube/your-video.md"

# Preview all pending YouTube notes
PYTHONPATH=. python3 src/cli/youtube_cli.py --vault ../knowledge batch-process --preview
```

> **Note**: The `--vault ../knowledge` flag is required. Notes must be in `Inbox/YouTube/` subdirectory.

#### What You Get

- **Key Insights**: Most important quotes with timestamps
- **Actionable Items**: Things you can do based on the video
- **Definitions**: Technical terms explained
- **Preserved Content**: Your original notes are kept intact

---

### Smart Link Suggestions

**What it does**: Suggests connections between your notes based on semantic similarity.

#### How It Works

When you create or modify a note, the Smart Link handler:
1. Analyzes the content using AI embeddings
2. Finds similar notes in your vault
3. Suggests wiki-links to add

#### Using Smart Link CLI

```bash
cd development

# Discover connections for a note
PYTHONPATH=. python3 src/cli/connections_demo.py "../knowledge/Inbox/my-note.md"

# Discover connections across your vault
PYTHONPATH=. python3 src/cli/connections_demo.py "../knowledge" --scan-all
```

#### Interactive Mode

The CLI offers an interactive workflow:
- **[A]ccept** - Add the suggested link to your note
- **[R]eject** - Skip this suggestion
- **[S]kip** - Move to next without deciding
- **[D]etails** - See why this connection was suggested
- **[Q]uit** - Exit

---

### Screenshot Import

**What it does**: Imports screenshots from OneDrive, extracts text with OCR, creates markdown notes.

#### Prerequisites

- Samsung phone syncing screenshots to OneDrive
- OneDrive folder accessible at `~/Library/CloudStorage/OneDrive-Personal/Pictures/Screenshots`

#### How It Works

1. You take screenshots on your phone
2. They sync to OneDrive
3. The evening workflow (11:30 PM) processes them:
   - OCR extracts text
   - AI generates descriptions
   - Markdown notes created in Inbox/

#### Manual Processing

```bash
# Process screenshots now
cd development
PYTHONPATH=. python3 src/cli/workflow_demo.py ../knowledge --evening-screenshots

# Dry run (preview without processing)
PYTHONPATH=. python3 src/cli/workflow_demo.py ../knowledge --evening-screenshots --dry-run
```

#### What You Get

- **OCR Text**: Actual text extracted from screenshots
- **AI Description**: 100+ word description of what's in the image
- **Source Detection**: Automatically detects app (Messenger, Chrome, etc.)
- **Smart Filenames**: Keywords from content, not generic names

---

### Weekly Review

**What it does**: Aggregates notes needing attention and provides AI recommendations.

#### Running Weekly Review

```bash
# Preview what needs review
make review

# Or with more options
cd development
PYTHONPATH=. python3 src/cli/weekly_review_cli.py --vault ../knowledge weekly-review --preview
```

#### Review Output

The weekly review shows:
1. **Inbox Notes**: New notes needing triage
2. **Fleeting Notes**: Quick captures that may need promotion
3. **AI Recommendations**: For each note:
   - Quality score (0-1)
   - Suggested action (promote/enhance/archive)
   - Missing elements (links, tags, structure)

#### Enhanced Metrics

```bash
# Get detailed vault analytics
cd development
PYTHONPATH=. python3 src/cli/workflow_demo.py ../knowledge --enhanced-metrics

# Export to file
PYTHONPATH=. python3 src/cli/workflow_demo.py ../knowledge --enhanced-metrics --export metrics.md
```

This shows:
- **Orphaned Notes**: Notes with no links
- **Stale Notes**: Notes not modified in 90+ days
- **Link Density**: How connected your vault is
- **Productivity Metrics**: Your note-taking patterns

---

## Automation Setup

### Starting Automation

```bash
# Start the daemon
make up

# Check it's running
make status
```

### What Gets Automated

| Handler | Trigger | Action |
|---------|---------|--------|
| Screenshot | File created in OneDrive | OCR + create note |
| Smart Link | Markdown file modified | Suggest connections |
| YouTube | `ready_for_processing: true` | Extract quotes |

### Cron Automation (Optional)

For fully hands-off automation, add to crontab:

```bash
# Edit crontab
crontab -e

# Add these lines:
# Screenshot import at 11:30 PM daily
30 23 * * * cd ~/repos/inneros-zettelkasten && make up

# Weekly review every Sunday at 9 AM
0 9 * * 0 cd ~/repos/inneros-zettelkasten && make review > ~/inneros-weekly-review.md
```

### Checking Automation Health

```bash
# Full health check
make status

# Or detailed health
cd development
PYTHONPATH=. python3 src/cli/inneros_status_cli.py --verbose
```

---

## Troubleshooting

### Common Issues

#### "Daemon not running"
```bash
# Start the daemon
make up

# If it fails, check logs
cat .inneros/daemon.log
```

#### "No notes found"
```bash
# Verify vault path
ls knowledge/Inbox/

# Check you're in the right directory
pwd  # Should be ~/repos/inneros-zettelkasten
```

#### "AI not responding"
```bash
# Check Ollama is running
ollama list

# Test AI model availability
cd development
PYTHONPATH=. python3 -c "from src.ai.ollama_client import OllamaClient; print('Model available:', OllamaClient().is_model_available('gpt-oss:20b'))"
```

#### "YouTube quotes not extracted"
Check that your note has:
- `source: youtube` in frontmatter
- `url: https://www.youtube.com/watch?v=XXXXX` (**required** - not `video_url:`)
- `video_id: XXXXX` (valid YouTube video ID)
- `ready_for_processing: true` (not false)
- NOT `ai_processed: true` (only processes once)

> **Common mistake**: Using `video_url:` instead of `url:`. The CLI expects exactly `url:`.

### Getting Help

1. **Check status**: `make status`
2. **View logs**: `cat .inneros/daemon.log`
3. **Run tests**: `make test`
4. **GitHub Issues**: Open an issue for bugs

---

## Command Reference

### Makefile Commands (Daily Use)

| Command | Description |
|---------|-------------|
| `make status` | Check system health |
| `make up` | Start automation daemon |
| `make down` | Stop automation daemon |
| `make review` | Generate weekly review |
| `make fleeting` | Check fleeting notes health |

### Development Commands

| Command | Description |
|---------|-------------|
| `make setup` | Install dependencies |
| `make test` | Run lint, type check, unit tests |
| `make unit` | Run unit tests only |
| `make integ` | Run integration tests |
| `make cov` | Run tests with coverage |

### CLI Tools (Advanced)

```bash
# All CLIs are in development/src/cli/
cd development

# Core workflows
PYTHONPATH=. python3 src/cli/core_workflow_cli.py --help
PYTHONPATH=. python3 src/cli/weekly_review_cli.py --help
PYTHONPATH=. python3 src/cli/fleeting_cli.py --help

# AI features
PYTHONPATH=. python3 src/cli/youtube_cli.py --help
PYTHONPATH=. python3 src/cli/connections_demo.py --help
PYTHONPATH=. python3 src/cli/enhance_demo.py --help

# Automation
PYTHONPATH=. python3 src/cli/inneros_automation_cli.py --help
PYTHONPATH=. python3 src/cli/inneros_status_cli.py --help
```

---

## Best Practices

### Note Creation

1. **Always add frontmatter** - Status, tags, created date
2. **Use templates** - Obsidian Templater for consistency
3. **Start in Inbox/** - Let AI triage and suggest promotion

### Workflow

1. **Run `make status` daily** - Know your system health
2. **Process weekly review on Sundays** - Don't let backlog grow
3. **Keep automation running** - `make up` is your friend

### YouTube Notes

1. **Watch first, process later** - Set `ready_for_processing: false` initially
2. **Add your notes first** - AI preserves your content
3. **Review AI quotes** - They're suggestions, not gospel

---

*Last updated: December 2025*
