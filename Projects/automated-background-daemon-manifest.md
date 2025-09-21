# InnerOS Automated Knowledge Processor - Project Manifest v2

**Created**: 2025-09-21 12:24 PDT  
**Revised**: 2025-09-21 15:43 PDT (Conservative Redesign)  
**Status**: 🟡 **DESIGN PHASE** → Beginner-Friendly Implementation  
**Priority**: High - Knowledge Enhancement  
**Owner**: Thaddius • Assistant: Cascade  

---

## 🎯 Vision & Purpose

Transform the InnerOS Zettelkasten from manual CLI processing into a **scheduled, safe, automated knowledge processor** that enhances your notes overnight while you sleep, focusing on **knowledge improvements and idea clustering**.

**Core Promise**: "Wake up every morning to find your Inbox and Fleeting Notes automatically enhanced with better tagging, quality scores, and connection discovery - all safely backed up and reversible."

---

## 🚨 Problem Statement

### Current State Friction

- **Manual Processing**: Must remember to run CLI commands for AI processing
- **Batch Operations**: Weekly reviews and triage happen sporadically  
- **Knowledge Gaps**: Miss connections between related ideas
- **Inconsistent Quality**: No systematic quality assessment of notes

### Target State Vision (Conservative)

- **Overnight Processing**: Daily batch processing during idle hours (2-4 AM)
- **Safe Automation**: All changes backed up and reversible
- **Knowledge Enhancement**: Better tagging, connection discovery, quality scoring
- **Manual Control**: You approve significant changes, auto-apply safe ones

---

## 🏗️ Technical Architecture (Simplified)

### Core Components

#### 1. **Simple Batch Processor** (Python Script)
```
inneros-processor
├── Backup Manager (create timestamped backups)
├── Directory Scanner (Inbox + Fleeting Notes only)
├── AI Processor (existing: auto_processor.py logic)
└── Safety Validator (atomic operations, rollback)
```

#### 2. **Processing Pipeline** (Safe & Conservative)
```
Daily Schedule Trigger (2 AM) → 
Create Backup → 
Scan Target Directories → 
Process Notes (with validation) → 
Generate Summary Report → 
Optional: Email/Log Results
```

#### 3. **Scheduled Tasks** (Conservative)
- **Daily (2 AM)**: Process Inbox and Fleeting Notes
- **Weekly (Sunday 3 AM)**: Full review generation + orphan detection
- **Monthly**: Cleanup old backups (keep 30 days)

### Deployment Strategy

#### Phase 1: Manual Execution (Week 1)
- **Implementation**: Simple Python script
- **Benefits**: Full control, easy debugging, learning-friendly
- **Usage**: Run manually when desired

#### Phase 2: Basic Scheduling (Week 2)
- **Implementation**: APScheduler integration
- **Benefits**: Automated daily processing
- **Fallback**: Manual execution always available

---

## 🎮 User Experience Design (Beginner-Friendly)

### Manual Control Mode (Default)
- **Explicit execution**: You run the script when ready
- **Dry-run first**: Shows what it would do before making changes
- **Extensive logging**: Full visibility into all operations

### Simple Command Interface
```bash
# Show what would be processed (safe)
python3 inneros_processor.py --scan --dry-run

# Create backup and process (with confirmation)
python3 inneros_processor.py --backup --execute

# View last processing results
python3 inneros_processor.py --status --last-run

# Rollback to previous backup if needed
python3 inneros_processor.py --rollback --date 2025-09-21
```

### Safety Features

- **Automatic backups** before any changes
- **Atomic file operations** (no partial writes)
- **Change validation** (verify YAML integrity)
- **Easy rollback** from backup if issues occur

---

## 🔧 Implementation Strategy (Conservative)

### Phase 1: Simple Batch Processor (2-3 days)
- [ ] Create standalone batch processor script
- [ ] Add backup/rollback functionality  
- [ ] Implement dry-run and validation modes
- [ ] Focus on Inbox and Fleeting Notes only

### Phase 2: Safety & Testing (2-3 days)
- [ ] Add comprehensive logging and error handling
- [ ] Test with small batches of real notes
- [ ] Implement atomic file operations
- [ ] Create rollback and recovery procedures

### Phase 3: Basic Scheduling (1-2 days)
- [ ] Add APScheduler for daily automation
- [ ] Create simple start/stop commands
- [ ] Add configuration file management
- [ ] Test overnight processing

### Phase 4: Polish & Extend (1-2 days)
- [ ] Add summary reporting and notifications
- [ ] Performance monitoring and optimization
- [ ] Documentation and user guides
- [ ] Optional: Extend to other directories

---

## 📊 Success Metrics (Realistic)

### Technical Performance
- **Processing Time**: Complete daily batch in <30 minutes
- **Resource Usage**: Reasonable during 2-4 AM processing window
- **Error Rate**: <1% of processed notes have issues
- **Data Safety**: Zero data loss, all changes reversible

### Knowledge Enhancement
- **Better Connections**: Discover 3-5 new note relationships daily
- **Quality Improvement**: Consistent tagging and scoring
- **Time Savings**: Reduce manual processing from 30min to 5min daily
- **Learning Value**: Understand automation patterns for future projects

---

## 🔐 Configuration & Security

### Default Configuration
```yaml
# ~/.inneros/daemon.yaml
daemon:
  enabled: true
  log_level: INFO
  pid_file: ~/.inneros/daemon.pid
  
processing:
  auto_tag: true
  auto_summarize: true
  auto_enhance: false
  batch_size: 10
  
scheduling:
  process_inbox: "*/5 * * * *"    # Every 5 minutes
  daily_health: "0 9 * * *"       # 9 AM daily  
  weekly_review: "0 8 * * 0"      # Sunday 8 AM
  
notifications:
  level: minimal
  methods: [log]  # Future: [log, email, webhook]
```

### Security Considerations
- **Local-only**: No external network access required
- **User Permissions**: Runs under user account, not root
- **Data Privacy**: All processing remains local
- **Backup Safety**: 30-day backup retention, easy rollback
- **File Integrity**: Atomic operations prevent corruption

---

## 🚀 Integration with Existing System

### Preserves Current Workflow
- All existing CLI commands continue to work
- Manual processing still available via `inneros workflow`
- No breaking changes to note schema or templates

### Enhances Existing Features  
- **Auto_processor.py**: Becomes core of daemon engine
- **Weekly Review**: Automated generation with manual approval
- **Analytics**: Always fresh, no manual refresh needed
- **File Watching**: Extended with scheduling and persistence

### Future Extension Points (After Success)
- **System Service Integration**: LaunchD/systemd after comfort gained
- **Real-time Processing**: File watching for immediate processing
- **Reading Intake Pipeline**: Auto-process bookmarks/RSS
- **Advanced Features**: Web dashboard, multi-user support

---

## ⚡ Quick Start Plan

### Development Environment
```bash
# Create daemon development branch
git checkout -b automated-background-daemon

# Install additional dependencies
pip install apscheduler psutil

# Test existing auto-processor
python3 development/src/ai/auto_processor.py knowledge/Inbox/
```

### Milestone 1 (This Weekend)
- [ ] Create daemon wrapper around AutoProcessor
- [ ] Add scheduling for inbox processing
- [ ] Implement daemon control commands
- [ ] Test background operation

### Milestone 2 (Next Week)  
- [ ] System service configuration
- [ ] Installation/setup automation
- [ ] Weekly review scheduling
- [ ] Health monitoring basics

---

## 🎯 Immediate Next Steps

1. **Create daemon controller script** (`development/src/daemon/daemon_controller.py`)
2. **Update project-todo-v3.md** with this new project
3. **Test current AutoProcessor** to validate existing foundation
4. **Design service configuration** for your macOS system

---

**Ready to transform your Zettelkasten into an always-on knowledge processing system?** 

This daemon will make your second brain truly autonomous while preserving all the human decision-making that makes it valuable.
