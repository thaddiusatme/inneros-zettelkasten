# InnerOS Workflow Diagrams

**Purpose**: Visual documentation of all InnerOS workflows with Mermaid flowcharts  
**Created**: 2025-10-12  
**Total Workflows**: 8

---

## 📊 Overview

This directory contains comprehensive flowcharts and documentation for all major InnerOS workflows. Each diagram includes:

- **Mermaid Flowchart**: Visual representation of workflow flow
- **Command Details**: CLI commands and usage
- **Use Cases**: Real-world scenarios
- **Architecture**: Component relationships
- **Performance Metrics**: Expected performance
- **Best Practices**: Recommendations

---

## 📁 Workflow Index

### 1. [Core Workflow](./01-core-workflow.md)
**CLI**: `core_workflow_cli.py`  
**Purpose**: Main workflow operations for inbox processing, status checking, and note promotion

**Key Commands**:
- `--status` - Display workflow status and note counts
- `--process-inbox` - AI-enhance all inbox notes
- `--promote <path> <type>` - Promote note to permanent/literature
- `--report` - Generate comprehensive workflow report

**Use Cases**:
- Daily inbox processing
- Note promotion to permanent status
- Workflow health monitoring

---

### 2. [Weekly Review Workflow](./02-weekly-review-workflow.md)
**CLI**: `weekly_review_cli.py`  
**Purpose**: AI-powered weekly review and enhanced vault metrics

**Key Commands**:
- `--weekly-review` - Generate AI-powered promotion checklist
- `--enhanced-metrics` - Comprehensive vault health analysis

**Use Cases**:
- Weekly knowledge review ritual
- Monthly vault health assessment
- Promotion candidate identification

**Key Metrics**:
- Orphaned notes detection
- Stale notes identification
- Quality distribution analysis
- Productivity tracking

---

### 3. [Fleeting Notes Lifecycle](./03-fleeting-notes-lifecycle.md)
**CLI**: `fleeting_cli.py`  
**Purpose**: Health monitoring, triage, and promotion of fleeting notes

**Key Commands**:
- `--fleeting-health` - Monitor fleeting note health
- `--fleeting-triage` - AI-powered triage with recommendations

**Lifecycle Stages**:
1. **Capture** (0-7 days) - Initial creation
2. **Maturation** (7-30 days) - Development phase
3. **Triage** - AI classification
4. **Promotion** - Move to permanent status
5. **Permanent** - Final integrated state

**Health Indicators**:
- Age distribution (fresh/mature/stale)
- Quality distribution (high/medium/low)
- Connectivity analysis (well-connected/isolated)

---

### 4. [YouTube Processing Workflow](./04-youtube-processing-workflow.md)
**CLI**: `youtube_cli.py`  
**Daemon**: `YouTubeFeatureHandler`  
**Purpose**: Automated transcript fetching and AI-powered quote extraction

**Key Commands**:
- `process-note <path>` - Process single YouTube note
- `batch-process` - Process all YouTube notes

**Processing Pipeline**:
1. Extract video ID from note
2. Fetch transcript (with 7-day caching)
3. AI quote extraction (Ollama)
4. Quality filtering (default: 0.7)
5. Insert formatted quotes into note

**Features**:
- Automatic daemon processing on save
- 99% API call reduction via caching
- 3-5 quotes per video average
- Cooldown system prevents loops

**Performance**:
- With cache: <2 seconds
- Without cache: 5-10 seconds
- Success rate: 93%

---

### 5. [Connection Discovery Workflow](./05-connection-discovery-workflow.md)
**CLI**: `connections_demo.py`  
**Purpose**: Semantic link discovery using AI embeddings

**Key Commands**:
- `.` - Full vault discovery
- `--target <note>` - Single note discovery
- `--report` - Connection analysis report

**Similarity Calculation**:
- **Method**: Cosine similarity on embeddings
- **Model**: `all-MiniLM-L6-v2`
- **Thresholds**: 0.8+ (very strong), 0.7-0.8 (strong), 0.65+ (suggested)

**Interactive Mode**:
- Review suggestions one by one
- Accept/skip/view full notes
- Automatic bidirectional link insertion
- Real-time note preview

**Use Cases**:
- New note integration
- Orphan resolution
- Knowledge clustering for MOCs

---

### 6. [Tag Enhancement Workflow](./06-tag-enhancement-workflow.md)
**CLI**: `advanced_tag_enhancement_cli.py`  
**Purpose**: AI-powered tag analysis and improvement

**Tag Issue Types**:
1. **Vague Tags**: Too generic (`stuff`, `things`, `misc`)
2. **Inconsistent Tags**: Similar concepts, different names (`js`, `javascript`, `JavaScript`)
3. **Redundant Tags**: Overlapping meaning (`python`, `python-programming`)

**Key Commands**:
- `--analyze` - Identify all tag issues
- `--enhance --interactive` - Review and apply improvements
- `--enhance --preview` - See suggestions without changes
- `--report` - Generate analysis report

**AI Enhancement**:
- Context-aware analysis
- Ranked alternative suggestions
- Batch processing (296 tags/second)
- Interactive or automated application

---

### 7. [Backup Workflow](./07-backup-workflow.md)
**CLI**: `backup_cli.py`  
**Purpose**: Safe vault backup with versioning and rollback

**Key Commands**:
- `--create` - Create timestamped backup
- `--list` - Display all backups
- `--restore <backup>` - Restore from backup
- `--verify <backup>` - Check backup integrity
- `--cleanup` - Remove old backups

**Safety Features**:
- Pre-restore safety backup
- Integrity verification (checksums)
- Manifest tracking
- Automatic rollback on failure

**Backup Format**:
- Timestamped: `backup_YYYYMMDD_HHMMSS/`
- Includes manifest.json with checksums
- Optional tar.gz compression
- Retention policy support

**Performance**:
- Backup: ~150 MB/s
- Verification: ~200 MB/s
- Small vault (<100MB): <5 seconds

---

### 8. [Daemon Automation Workflow](./08-daemon-automation-workflow.md)
**Service**: `automation_daemon.py`  
**Purpose**: Background automation service for continuous processing

**Core Components**:
1. **File Watcher** - Monitor vault for changes
2. **Task Scheduler** - Run recurring tasks
3. **Feature Handlers** - Process automation events
4. **Health Monitor** - Track system health

**Active Handlers**:
- **YouTube Handler**: Auto-process YouTube notes on save
- **Screenshot Handler**: OCR and note creation for images
- **Smart Link Handler**: Connection discovery suggestions

**Management**:
```bash
inneros daemon start   # Start service
inneros daemon stop    # Stop service
inneros daemon status  # Check status
inneros daemon logs    # View logs
```

**Scheduled Tasks**:
- Weekly review generation (Sunday 9 AM)
- Daily backups (2 AM)
- Hourly health checks

---

## 🎯 Workflow Categories

### Daily Operations
- **Core Workflow**: Inbox processing, status checks
- **Fleeting Notes**: Health monitoring
- **Daemon**: Continuous background automation

### Weekly Maintenance
- **Weekly Review**: Promotion candidates, vault metrics
- **Fleeting Triage**: AI-powered note classification
- **Backup**: Create weekly backup

### Monthly/Quarterly
- **Connection Discovery**: Link orphaned notes, create MOCs
- **Tag Enhancement**: Clean up tag quality
- **Backup Cleanup**: Remove old backups

### On-Demand
- **YouTube Processing**: Extract quotes from videos
- **Backup Restore**: Recover from backup
- **Enhanced Metrics**: Deep vault analysis

---

## 🏗️ Architecture Overview

```
User Commands (CLI)
    ↓
Dedicated CLIs (10 files)
    ↓
WorkflowManager (Facade)
    ↓
    ├─→ CoreWorkflowManager (orchestration)
    ├─→ AnalyticsManager (metrics)
    ├─→ AIEnhancementManager (AI processing)
    ├─→ ConnectionManager (link discovery)
    └─→ TagEnhancementManager (tag analysis)

Background Service:
Daemon → FeatureHandlers → CLIs/Managers
```

**Design Principles**:
- **Separation of Concerns**: Each CLI focuses on one workflow
- **Manager Pattern**: Centralized orchestration
- **Integration-First**: Reuse existing components
- **TDD Methodology**: Test-driven development
- **Clean Architecture**: No god classes, modular design

---

## 📊 Performance Summary

| Workflow | Typical Duration | Success Rate |
|----------|-----------------|--------------|
| Core Workflow | <10s per note | 98% |
| Weekly Review | <5s for 100+ notes | 100% |
| Fleeting Health | <2s for 100+ notes | 100% |
| YouTube Processing | 5-10s per video | 93% |
| Connection Discovery | <5s for 200 notes | 95% |
| Tag Enhancement | ~2s per tag | 85% accuracy |
| Backup Create | ~150 MB/s | 100% |
| Daemon Processing | Event-driven | 95% |

---

## 🚀 Quick Start

### First-Time Setup
```bash
# 1. Start the daemon for automation
inneros daemon start

# 2. Process your inbox
python3 src/cli/core_workflow_cli.py . --process-inbox

# 3. Generate weekly review
python3 src/cli/weekly_review_cli.py . --weekly-review

# 4. Create first backup
python3 src/cli/backup_cli.py --create
```

### Daily Workflow
```bash
# Morning: Check status
python3 src/cli/core_workflow_cli.py . --status

# Process new notes (or let daemon handle it)
python3 src/cli/core_workflow_cli.py . --process-inbox

# Evening: Check fleeting note health
python3 src/cli/fleeting_cli.py . --fleeting-health
```

### Weekly Workflow
```bash
# Sunday morning
# 1. Generate review
python3 src/cli/weekly_review_cli.py . --weekly-review

# 2. Triage fleeting notes
python3 src/cli/fleeting_cli.py . --fleeting-triage

# 3. Promote ready notes
python3 src/cli/core_workflow_cli.py . --promote <path> permanent

# 4. Create backup
python3 src/cli/backup_cli.py --create
```

---

## 🔗 Related Documentation

- **CLI Reference**: `/CLI-REFERENCE.md` - Complete CLI documentation
- **Project Status**: `/Projects/ACTIVE/PROJECT-STATUS-UPDATE-2025-10-12.md`
- **Architecture**: `/Projects/ACTIVE/adr-004-cli-layer-extraction.md`
- **Getting Started**: `/GETTING-STARTED.md`

---

## 📝 Diagram Format

All diagrams use **Mermaid** syntax, which can be rendered in:
- GitHub markdown
- Obsidian (with Mermaid plugin)
- VS Code (with Mermaid preview)
- Online: https://mermaid.live

---

## 🎨 Color Coding

Flowcharts use consistent color coding:
- 🔵 **Blue** - Initialization/Loading
- 🟠 **Orange** - AI/API Processing
- 🟣 **Purple** - Analysis/Metrics
- 🟢 **Green** - Success/Output
- 🔴 **Red** - Errors/Alerts
- 🟡 **Yellow** - Decisions/Branching

---

**Created**: 2025-10-12  
**Author**: Development Team  
**Status**: Complete ✅  
**Total Files**: 8 workflows + README
