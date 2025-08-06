    # innerOS — Zettelkasten + AI Workflow

    Welcome to the `innerOS` workspace! This vault is designed for frictionless idea capture, structured Zettelkasten note-taking, and AI-assisted workflows, with privacy and future collaboration in mind.

## Key Documents
- **inneros-manifest.md** — Comprehensive project overview, architecture, AI features, and roadmap
- **windsurf-project-changelog.md** — Detailed change history and development milestones
- **project-todo.md** — Current priorities and next development steps

## 🏗️ Project Structure

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
├── Projects/             # 📋 Project documentation
├── Reviews/              # 📊 Weekly reviews and retrospectives
├── Workflows/            # 🔄 Process documentation
└── Media/                # 🖼️ Images and attachments
```

### **Directory Purpose**
- **development/**: All Python code, tests, and technical artifacts
- **knowledge/**: Complete Zettelkasten system (Obsidian vault)
- **Projects/**: Project management and planning documents
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

## 🤖 AI & Automation

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
2. **Quick analysis**: `inneros analytics`
3. **Check workflow status**: `inneros workflow --status`
4. **Process inbox**: `inneros workflow --process-inbox`
5. **Generate weekly review**: `inneros workflow --weekly-review`
6. **Enhance a note**: `inneros enhance knowledge/Inbox/your-note.md`

### 📊 **Proven Results**
- **66/66 tests passing** with comprehensive coverage
- **Real user validation** on 212 notes, 50,027 words
- **Production performance**: <10s summarization, <5s similarity
- **100% success rate** in inbox processing
- **Graceful fallbacks** when AI services unavailable

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

    ## Getting Started
    1. **Read the Manifest**: Start with `inneros-manifest.md` for complete project context
    2. **Quick Demo**: Run `python3 quick_demo.py` to see AI features in action
    3. **Process Your Notes**: Use `python3 src/cli/workflow_demo.py . --process-inbox`
    4. **Explore Templates**: Use provided templates for consistent note creation
    5. **Weekly Review**: Run `python3 src/cli/workflow_demo.py . --weekly-review`

    ---

    _This README is a quickstart guide. For full project context, always consult the Manifest and Changelog._
