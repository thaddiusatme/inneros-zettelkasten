# 🧠 InnerOS Zettelkasten

> **A powerful personal knowledge management system combining the Zettelkasten method with AI assistance**

[![CI](https://github.com/thaddiusatme/inneros-zettelkasten/workflows/CI%20-%20Quality%20Gates/badge.svg)](https://github.com/thaddiusatme/inneros-zettelkasten/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.1.0--beta-blue)]() 
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()
[![Python](https://img.shields.io/badge/python-3.13-blue)]()
[![Obsidian](https://img.shields.io/badge/obsidian-1.0+-purple)]()

---

## ✨ What is InnerOS Zettelkasten?

InnerOS is a **ready-to-use Zettelkasten system** that helps you:
- 📝 **Capture ideas** quickly and process them systematically
- 🔗 **Build connections** between concepts naturally
- 🤖 **Enhance with AI** for auto-tagging, quality assessment, and connection discovery
- 🌱 **Grow your knowledge** organically over time

Perfect for researchers, writers, developers, students, and lifelong learners.

---

## 🚀 Quick Start

### **15-Minute Setup**
```bash
# 1. Clone the repository
git clone https://github.com/yourusername/inneros-zettelkasten.git
cd inneros-zettelkasten

# 2. Open in Obsidian
# File → Open folder as vault → Select inneros-zettelkasten directory

# 3. Explore the starter pack
# Open knowledge-starter-pack/README.md in Obsidian
```

**→ See [INSTALLATION.md](INSTALLATION.md) for detailed setup instructions**

---

## 🎬 YouTube Automation (60-Second Setup)

Automatically process YouTube videos into enhanced notes with AI-extracted quotes:

```bash
# 1. Copy environment template
cp .env.sample .env

# 2. Add your API keys to .env
# YOUTUBE_API_KEY=your_key_here
# OPENAI_API_KEY=your_key_here

# 3. Run dry-run smoke test
cd development
python3 src/cli/youtube_cli.py batch-process --preview

# 4. Process YouTube notes (when ready)
python3 src/cli/youtube_cli.py batch-process
```

**Features:**
- ✅ Automatic transcript fetching
- ✅ AI-powered quote extraction (key insights, actionable items, definitions)
- ✅ Status backups before modifications
- ✅ Metrics tracking for monitoring
- ✅ Production-ready with CI-lite

**Monitoring:** Metrics saved to `.automation/metrics/youtube_metrics.json`

---

## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** — Step-by-step setup guide (~15 minutes)
- **[knowledge-starter-pack/README.md](knowledge-starter-pack/README.md)** — Learn the Zettelkasten workflow
- **[QUICK-REFERENCE.md](QUICK-REFERENCE.md)** — Essential commands and shortcuts
- **[CLI-REFERENCE.md](CLI-REFERENCE.md)** — AI features and automation (optional)

---

## 🎯 Key Features

### **📝 Systematic Knowledge Capture**
- **Fleeting Notes** → Quick captures in `Inbox/`
- **Permanent Notes** → Processed, atomic ideas
- **Literature Notes** → Source material summaries
- **MOCs** → Maps of Content for navigation

### **🔗 Natural Connection Building**
- Wiki-style `[[linking]]` between notes
- Bidirectional backlinks automatically
- Graph view visualization in Obsidian
- Organic structure emerges from connections

### **🤖 Optional AI Enhancement**
```bash
# AI-powered features (requires Python setup)
python3 development/src/cli/workflow_demo.py knowledge/ --process-inbox
python3 development/src/cli/connections_demo.py knowledge/
python3 development/src/cli/workflow_demo.py knowledge/ --weekly-review
```

- **Auto-tagging** based on content
- **Connection discovery** using semantic similarity
- **Quality assessment** for note completeness
- **Weekly review automation** with metrics

### **📦 Ready-to-Use Starter Pack**
Includes 6 example notes demonstrating:
- Zettelkasten methodology principles
- Permanent note structure
- MOC navigation patterns
- Literature note format

---

## 📖 The Zettelkasten Workflow

```
1. CAPTURE → Quick ideas in Inbox
2. PROCESS → Review and refine weekly
3. CONNECT → Link to existing knowledge
4. DISCOVER → Explore your knowledge graph
```

**Example Note Structure**:
```markdown
---
type: permanent
created: 2025-10-09 10:00
status: published
tags: [topic, concept]
---

# Your Atomic Idea

One clear concept explained in your own words.

## Related Notes
- [[another-related-note]]
- [[foundational-concept]]
```

---

## 🎨 What Makes InnerOS Different?

| Feature | InnerOS | Traditional Notes |
|---------|---------|-------------------|
| **Structure** | Emerges from connections | Rigid folders/hierarchy |
| **Capture** | Quick fleeting → process later | Perfect note required upfront |
| **Discovery** | Graph-based exploration | Manual search/browse |
| **AI** | Optional enhancement | Usually absent |
| **Privacy** | Local-first (optional cloud AI) | Often cloud-only |

---

## 📂 Project Structure

### **Clean Separation Architecture**
```
/ (ROOT - Clean Navigation)
├── development/           # 🔧 ALL CODE & DEV ARTIFACTS
│   ├── src/              # Python AI/workflow code
│   ├── tests/            # Test suites
│   ├── demos/            # CLI demonstration tools
│   └── README-dev.md     # Developer documentation
├── knowledge/            # 📚 ALL KNOWLEDGE CONTENT
│   ├── Inbox/            # Staging area for new notes
│   ├── Fleeting Notes/   # Quick captures and temporary notes
│   ├── Permanent Notes/  # Atomic, evergreen knowledge
│   ├── Archive/          # Old/deprecated content
│   ├── Templates/        # Obsidian templates and Templater scripts
│   ├── .obsidian/        # Obsidian configuration
│   └── README-knowledge.md # Knowledge worker documentation
├── Projects/             # 📋 Project documentation & management
│   ├── ACTIVE/           # Current priority projects (8 items)
│   ├── REFERENCE/        # Essential docs (manifests, guides, DFDs)
│   ├── COMPLETED-2025-XX/ # Monthly archives of completed work
│   └── DEPRECATED/       # Superseded plans and manifests
├── Reviews/              # 📊 Weekly reviews and retrospectives
├── Workflows/            # 🔄 Process documentation
└── Media/                # 🖼️ Images and attachments
```

### **Directory Purpose**
- **development/**: All Python code, tests, and technical artifacts
- **knowledge/**: Complete Zettelkasten system (Obsidian vault)
- **Projects/**: Clean project management with systematic organization:
  - **ACTIVE/**: Current priority projects and manifests (8 items)
  - **REFERENCE/**: Essential documentation, guides, and architecture docs (7 items)  
  - **COMPLETED-2025-XX/**: Monthly archives of completed lessons learned and reports
  - **DEPRECATED/**: Superseded manifests and planning documents
- **Reviews/**: Weekly reviews and progress tracking
- **Workflows/**: Process documentation and SOPs

## Note Schema (YAML/Markdown Example)
```markdown
---
type: permanent | fleeting | literature | MOC
created: YYYY-MM-DD HH:mm
status: inbox | promoted | draft | published
tags: [permanent, zettelkasten, ...]
visibility: private | shared | team
---
```
- **status: inbox** in YAML is the primary indicator for notes needing triage, regardless of folder location.
- The `Inbox/` folder is a temporary staging area, not a workflow state.

## How Inbox Works
- All new notes are created in the `Inbox/` folder with `status: inbox` in YAML.
- During triage (weekly or as needed), notes are moved to their permanent location:
    - Fleeting notes → `Fleeting Notes/`
    - Permanent notes → `Permanent Notes/`
    - Reference/actionable notes → appropriate folder
- Only notes with `status: inbox` in YAML are considered active for triage, regardless of folder.
  - The `fleeting.md` template (and others) now include workflow guidance comments to reinforce this process.

## Templates: ChatGPT Prompt (Templater)
- File: `knowledge/Templates/Utility/chatgpt-prompt.md`
- Purpose: Quickly scaffold a high-quality ChatGPT prompt for a fresh session.
- How it works:
  - Uses Obsidian Templater (EJS) tokens like `<% tp.date.now("YYYY-MM-DD HH:mm") %>`
  - Prompts once for a feature/branch name (single prompt)
  - Renames and moves the file to `Prompts/prompt-YYYYMMDD-HHmm.md`
  - YAML includes `type: fleeting`, `status: inbox` and tags `[prompt, chatgpt, inbox]`
- GitHub issue #112 shipped the routing update so generated prompt files now land in `Prompts/`.
- When to use:
  - Before starting a new coding/chat iteration to set scope and acceptance criteria

## 🤖 AI & Automation

### **Quick Commands** (Developer Helper Script)
```bash
# Check automation status
./inneros.sh status

# Start automation daemon
./inneros.sh up

# Run AI inbox sweep
./inneros.sh ai inbox-sweep

# Show all available commands
./inneros.sh help
```

> **Note**: `inneros.sh` wraps `make` commands for convenience. For production use, prefer `make status`, `make up`, etc.

### **Development Tools** (in `development/`)
```bash
# Run AI analytics on knowledge base
python3 development/src/cli/analytics_demo.py knowledge/ --interactive

# Process inbox with AI
python3 development/src/cli/workflow_demo.py knowledge/ --process-inbox

# Weekly review automation
python3 development/src/cli/workflow_demo.py knowledge/ --weekly-review
```

### **Knowledge Base Tools** (from `knowledge/`)
```bash
# AI-enhanced note processing
python3 ../development/src/cli/workflow_demo.py . --process-inbox

# Analytics dashboard
python3 ../development/src/cli/analytics_demo.py . --interactive
```

- **Templater scripts** automate file naming, sorting, and metadata
- **LLM/AI integration** for summarization, tagging, linking, and triage
- **Zero setup required** - tools work from both directories

## 🤖 AI Features (Production Ready)

### 🏆 **Phase 5.4 Complete: Advanced Analytics & Workflow Management**

The InnerOS Zettelkasten now includes a comprehensive AI-powered knowledge management system:

#### 📊 **Analytics & Quality Assessment**
```bash
# Interactive analytics with rich visuals
inneros analytics --interactive

# Targeted quality analysis
inneros analytics --section quality

# Quick analysis with default knowledge directory
inneros analytics
```
- **Quality Scoring**: 0-1 assessment based on content, tags, links, metadata
- **Temporal Analysis**: Creation patterns and date range insights
- **Recommendations**: Actionable suggestions for improvement
- **Export**: JSON reports for external analysis

#### 🔄 **Smart Workflow Management**
```bash
# Process inbox with AI assistance
inneros workflow --process-inbox

# Interactive workflow management
inneros workflow --interactive

# Check workflow health status
inneros workflow --status

# Generate weekly review
inneros workflow --weekly-review
```
- **AI-Enhanced Processing**: Automatic tagging and quality assessment
- **Intelligent Promotion**: Inbox → Fleeting → Permanent with AI guidance
- **Batch Operations**: Process multiple notes efficiently
- **Health Monitoring**: Real-time workflow status

#### 🔗 **Connection Discovery**
```bash
# Find semantic connections
python3 src/cli/connections_demo.py /path/to/notes
```
- **Semantic Similarity**: AI-powered embedding comparison
- **Link Suggestions**: Intelligent recommendations with explanations
- **Connection Mapping**: Visual relationship discovery

#### 📝 **Note Summarization**
```bash
# Generate summaries
python3 src/cli/summarizer_demo.py /path/to/notes
```
- **Abstractive**: AI-generated summaries using LLM
- **Extractive**: Keyword-based sentence selection
- **Smart Length Detection**: Automatic threshold handling

#### 📈 **Enhanced Weekly Review Analytics**
```bash
# Generate comprehensive weekly metrics
inneros workflow --enhanced-metrics

# Export enhanced metrics to markdown
inneros workflow --enhanced-metrics --export metrics.md

# JSON output for automation
inneros workflow --enhanced-metrics --format json
```
- **Orphaned Note Detection**: Identifies notes with no incoming/outgoing links
- **Stale Note Analysis**: Flags notes not updated in 90+ days
- **Link Density Metrics**: Average connections per note
- **Productivity Insights**: Creation/modification patterns
- **Actionable Recommendations**: Specific improvement suggestions

#### 🎮 **Interactive Demos**
```bash
# Experience complete user journeys
python3 demo_user_journeys.py

# Test on your real notes
python3 test_real_analytics.py
```
- **User Journey Simulations**: New user, power user, maintenance workflows
- **Real Data Testing**: Validate features on actual collections
- **Rich CLI Experience**: Color-coded output with progress indicators

### 🚀 **Getting Started with AI Features**

1. **Ensure Ollama is running**: `ollama serve` (with llama3:latest model)
   - **Upgrade option**: `gpt-oss:20b` for 2.5x better quality (see [model migration guide](Projects/ACTIVE/model-migration-gpt-oss-20b-manifest.md))
2. **Quick analysis**: `inneros analytics`
3. **Check workflow status**: `inneros workflow --status`
4. **Process inbox**: `inneros workflow --process-inbox`
5. **Generate weekly review**: `inneros workflow --weekly-review`
6. **Enhance a note**: `inneros enhance knowledge/Inbox/your-note.md`

### 📊 **Proven Results**
- **72/72 tests passing** with comprehensive coverage (updated Oct 2025)
- **Real user validation** on 212 notes, 50,027 words
- **Production performance**: <10s summarization, <5s similarity
- **100% success rate** in inbox processing
- **Graceful fallbacks** when AI services unavailable

### 🔄 **Model Upgrade Path** (Optional)
**Current**: `llama3:latest` (8B parameters) - Fast, reliable baseline  
**Upgrade**: `gpt-oss:20b` (20B parameters) - 2.5x better quality

**Benefits of upgrading**:
- ✅ **Better instruction following** → More accurate tagging and quote extraction
- ✅ **Native JSON mode** → Eliminates ~15% parsing failures
- ✅ **Extended context (8K)** → Handles longer YouTube transcripts
- ✅ **Instant rollback** → Environment variable switching
- ✅ **Local/private** → Same privacy-first architecture

**Requirements**: 16GB+ VRAM or unified memory

**See**: [Model Migration Guide](Projects/ACTIVE/model-migration-gpt-oss-20b-manifest.md) for complete implementation plan (8-10 hours with TDD approach)

### 🏗️ **Architecture** (ADR-002 Complete - Oct 2025)
- **WorkflowManager**: 812 LOC (66% reduction from 2,397 LOC)
- **12 Specialized Coordinators**: 4,250 LOC properly organized
- **Clean Composition Pattern**: Dependency injection, testable components
- **Zero Technical Debt**: Within architectural limits, 100% test coverage
- **Modular & Maintainable**: Each coordinator has single, clear responsibility

### 🎬 **YouTube Knowledge Capture** (TDD Iteration 9 + Official API)

**Automated YouTube video → Zettelkasten notes workflow**

```bash
# Process YouTube notes with AI-extracted quotes and insights
# Daemon automatically watches for new YouTube notes
inneros daemon start

# Or manual processing
python3 src/cli/workflow_demo.py knowledge/ --process-youtube
```

**Features**:
- **Dual Transcript Fetching**:
  - Official YouTube Data API v3 (quota-based, reliable) ✅ **NEW**
  - Unofficial scraping (fallback for rate-limited networks)
  - Automatic retry with exponential backoff
- **AI Quote Extraction**: 5-7 highest-quality quotes with timestamps
- **Note Enhancement**: Auto-generate tags, summaries, connections
- **Template Integration**: Works with Obsidian Templater templates
- **Daemon Integration**: Automatic processing on file creation

**Configuration** (`daemon_config.yaml`):
```yaml
youtube_handler:
  enabled: true
  fetcher_type: official_api  # or 'unofficial_scraping'
  
  # Official API (recommended for rate-limited networks)
  official_api:
    api_key: ${YOUTUBE_API_KEY}  # Set in environment
    quota_limit: 10000  # Free tier: ~40 videos/day
  
  # Retry logic for both fetchers
  rate_limit:
    max_retries: 3
    base_delay: 5
    max_delay: 60
```

**Setup**:
1. **Get API Key** (optional, for official API):
   - Create Google Cloud project
   - Enable YouTube Data API v3
   - Generate API key
   - Set: `export YOUTUBE_API_KEY='your-key'`
2. **Works out-of-box** with unofficial scraping (no setup)
3. **Fallback enabled**: Auto-switches if quota exhausted

**Status**: Production ready (TDD Iterations 1-9 complete)

    ## Privacy & Collaboration
    - All notes default to private. Future-proofed for multi-user and compliance needs.
    - Manifest and Changelog document all conventions and changes.

    ## Version Control
    This repository is version controlled with Git to:
    - Track changes to notes, templates, and workflow documentation (see recent changelog entries for template and workflow alignment)
    - Enable safe experimentation with new workflows and organization
    - Facilitate collaboration while maintaining change history
    - Provide backup and restore capabilities
    - Support branching for experimental features or major reorganizations

    Key Git files:
    - `.gitignore` — Excludes temporary files, system files, and optional private content
    - `.git/hooks/pre-commit` — Validates metadata in staged markdown files before committing.
    - `.git/hooks/post-commit` — Automatically updates `Windsurf Project Changelog.md` with the commit message after a successful commit.

    ## 🗂️ Project Organization (Updated September 2024)

    The **Projects/** directory has been systematically reorganized for maximum clarity and minimal cognitive load:

    ### **ACTIVE/** - Current Focus (8 files)
    - `project-todo-v3.md` — Current task management and 2-week roadmap
    - `smart-link-management-system-manifest-v1.md` — TDD Iteration 4 complete
    - `intelligent-tag-management-system-manifest.md` — Next major AI project
    - `visual-knowledge-capture-manifest.md` — Mobile workflow requirements
    - `knowledge-capture-system-manifest.md` — Voice note integration
    - Plus project planning and priority summaries

    ### **REFERENCE/** - Essential Docs (7 files)  
    - `inneros-manifest-v3.md` — Complete project overview
    - `windsurf-project-changelog.md` — Development history
    - `CONNECTION-DISCOVERY-DFD.md` — System architecture diagrams
    - `FEATURE-STATUS.md`, `GETTING-STARTED.md`, `QUICK-REFERENCE.md`, `README.md`

    ### **COMPLETED-2025-XX/** - Monthly Archives
    - **September 2025**: 15 completed TDD lessons learned (Advanced Tag Enhancement, Smart Link Management, Enhanced Connections)
    - **August 2025**: 13 completed items (Capture System, Directory Organization, Voice Integration, Bug fixes)

    ### **DEPRECATED/** - Historical Context (10 files)
    - Superseded manifests and completed proof-of-concepts
    - Legacy project versions (v2 docs replaced by v3)
    - Integration analyses that have been implemented

    **Result**: 97% reduction in main directory clutter (35+ files → 1 cleanup plan), crystal clear focus on 8 active priorities.

    ## Getting Started
    1. **Read the Manifest**: Start with `Projects/REFERENCE/inneros-manifest-v3.md` for complete project context
    2. **Check Current Priorities**: Review `Projects/ACTIVE/project-todo-v3.md` for active tasks
    3. **Quick Demo**: Run `python3 quick_demo.py` to see AI features in action
    4. **Process Your Notes**: Use `python3 src/cli/workflow_demo.py . --process-inbox`
    5. **Explore Templates**: Use provided templates for consistent note creation
    6. **Weekly Review**: Run `python3 src/cli/workflow_demo.py . --weekly-review`

    ---

    _This README is a quickstart guide. For full project context, always consult the Manifest and Changelog._
