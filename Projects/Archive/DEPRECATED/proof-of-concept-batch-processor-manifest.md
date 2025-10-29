# InnerOS Proof-of-Concept Batch Processor - Project Manifest

**Created**: 2025-09-21 15:43 PDT  
**Status**: 🟢 **READY TO BUILD** → Immediate Implementation  
**Priority**: High - Learning & Validation  
**Owner**: Thaddius • Assistant: Cascade  
**Duration**: 2-3 days maximum

---

## 🎯 Purpose & Goals

Create a **simple, safe, manual batch processor** to validate automation concepts before building the full automated system. This is your **first automation project** - focused on learning and proving the approach works.

**Core Promise**: "Manually process your Inbox and Fleeting Notes with AI enhancement, full backup safety, and complete visibility into every change made."

---

## 🚨 Problem This Solves

### Learning Goals

- **Understand AI Processing**: See exactly what auto-tagging and quality scoring does
- **Validate Safety**: Prove backup/rollback works before automation
- **Test Performance**: Measure how long processing actually takes
- **Build Confidence**: Manual control before automatic scheduling

### Immediate Value

- **Process 10-20 notes safely** with AI enhancement
- **Create reliable backup system** you trust
- **Generate processing reports** showing exactly what changed
- **Learn the workflow** before automating it

---

## 🏗️ Technical Design (Minimal)

### Core Script: `inneros_batch_processor.py`

```python
# Simple structure - no complex architecture
class BatchProcessor:
    def __init__(self, target_dirs=["knowledge/Inbox", "knowledge/Fleeting Notes"]):
        self.dirs = target_dirs
        self.backup_manager = BackupManager()
        self.ai_processor = AutoProcessor()  # Reuse existing
    
    def scan_notes(self, dry_run=True):
        """Show what would be processed"""
        pass
    
    def process_batch(self, create_backup=True):
        """Actually process with safety checks"""
        pass
    
    def rollback(self, backup_date):
        """Restore from backup if needed"""
        pass
```

### Key Components

#### 1. **Directory Scanner**

- Scan only `knowledge/Inbox/` and `knowledge/Fleeting Notes/`
- Skip files modified in last 2 hours (avoid editing conflicts)
- Show file count and types before processing

#### 2. **Safety Manager**

- Create timestamped backup before any changes
- Validate all YAML before modification
- Atomic file operations (write to `.tmp`, then rename)
- Detailed change logging

#### 3. **AI Processing (Reuse Existing)**

- Use existing `AutoProcessor` logic from `auto_processor.py`
- Focus on: auto-tagging, quality scoring, connection discovery  
- Skip: summarization initially (reduce complexity)

#### 4. **Report Generator**

- Show before/after for each file
- List all changes made (tags added, scores assigned)
- Generate markdown summary report

---

## 🎮 User Experience Design

### Command Interface (Simple)

```bash
# Step 1: See what would be processed (SAFE)
python3 inneros_batch_processor.py --scan --dry-run

# Step 2: Create backup and process (WITH CONFIRMATION)  
python3 inneros_batch_processor.py --process --backup --confirm

# Step 3: View results
python3 inneros_batch_processor.py --report --last-run

# Emergency: Rollback if something went wrong
python3 inneros_batch_processor.py --rollback --backup 2025-09-21-15-43
```

### Example Workflow

```bash
# Morning routine - process overnight notes
cd /Users/thaddius/repos/inneros-zettelkasten

# 1. Scan to see what's new
python3 development/inneros_batch_processor.py --scan
# Output: "Found 5 notes in Inbox, 3 in Fleeting Notes (8 total)"

# 2. Dry run to see what would change  
python3 development/inneros_batch_processor.py --dry-run
# Output: Shows proposed tags, quality scores for each file

# 3. Process with backup
python3 development/inneros_batch_processor.py --process --backup
# Output: "Backup created: ~/.inneros/backups/2025-09-21-15-43/"
#         "Processing 8 notes... Done. See report: processing-report-2025-09-21.md"
```

---

## 🔧 Implementation Plan (Conservative)

### Day 1: Basic Structure (3-4 hours)

- [ ] Create `development/inneros_batch_processor.py`
- [ ] Implement directory scanning and file detection
- [ ] Add basic command-line argument parsing
- [ ] Test scanning functionality on real directories

### Day 2: Safety Systems (3-4 hours)

- [ ] Implement backup creation and management
- [ ] Add atomic file operations (write to .tmp, rename)
- [ ] Create rollback functionality
- [ ] Test backup/rollback with sample files

### Day 3: AI Integration & Polish (2-3 hours)

- [ ] Integrate existing `AutoProcessor` logic
- [ ] Add dry-run mode with change preview
- [ ] Create processing report generation
- [ ] Test end-to-end workflow with 3-5 real notes

### Success Criteria

- [ ] Process 5 real notes without any data loss
- [ ] Backup and rollback works perfectly
- [ ] Generate useful report showing improvements
- [ ] Takes <10 minutes to process typical daily batch

---

## 📊 Testing Strategy

### Phase 1: Safe Testing

```bash
# Create test notes in separate directory
mkdir knowledge/Test-Inbox
cp "knowledge/Inbox/some-note.md" "knowledge/Test-Inbox/"

# Test on copies first
python3 inneros_batch_processor.py --scan --dir knowledge/Test-Inbox
```

### Phase 2: Real Data (Small Batch)

```bash  
# Process only 3-5 real notes initially
python3 inneros_batch_processor.py --scan --limit 5
python3 inneros_batch_processor.py --process --backup --limit 5
```

### Phase 3: Full Daily Batch

```bash
# Process normal daily intake (10-20 notes)
python3 inneros_batch_processor.py --process --backup
```

---

## 🔐 Safety Features (Paranoid Mode)

### Backup Strategy

- **Before every run**: Create timestamped backup
- **Retention**: Keep 30 days of backups (auto-cleanup older)
- **Verification**: Validate backup completeness before processing
- **Easy access**: Backups stored in `~/.inneros/backups/YYYY-MM-DD-HH-MM/`

### File Safety

```python
# Atomic operation pattern
def update_note_safely(file_path, new_content):
    tmp_path = file_path + '.tmp'
    try:
        # Write to temporary file
        with open(tmp_path, 'w') as f:
            f.write(new_content)
        
        # Validate YAML integrity
        validate_yaml_frontmatter(tmp_path)
        
        # Atomic rename (this step cannot fail partially)
        os.rename(tmp_path, file_path)
        
    except Exception as e:
        # Cleanup temp file on any error
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise e
```

### Validation Checks

- **YAML integrity**: Verify frontmatter parses correctly
- **File size**: Ensure file didn't become empty or corrupted  
- **Encoding**: Maintain UTF-8 encoding throughout
- **Permissions**: Preserve original file permissions

---

## 📋 Success Metrics

### Learning Objectives

- [ ] **Understand AI processing**: See what tagging/scoring actually does
- [ ] **Trust the safety**: Prove backup/rollback works reliably
- [ ] **Measure performance**: Know how long daily processing takes
- [ ] **Build workflow**: Establish routine you're comfortable with

### Technical Validation

- [ ] **Process 20+ notes** without any issues
- [ ] **Zero data loss**: Every change backed up and reversible
- [ ] **Useful improvements**: See actual quality enhancements
- [ ] **Time efficiency**: Reduce manual tagging time significantly

### Confidence Building

- [ ] **Manual control**: You approve all changes before they happen
- [ ] **Full visibility**: Detailed reports of all modifications
- [ ] **Easy recovery**: Can rollback anything within minutes
- [ ] **Ready for automation**: Comfortable with automating this process

---

## 🚀 Next Steps After Success

### If This Works Well

1. **Add scheduling**: Use this as base for automated daily processing
2. **Extend directories**: Add other note types after validation
3. **Enhanced features**: Add summarization, connection discovery
4. **System integration**: Consider LaunchD/systemd automation

### If This Reveals Issues

1. **Refine safety**: Improve backup or validation as needed
2. **Adjust AI processing**: Tune tagging/scoring parameters  
3. **Simplify further**: Remove features that don't add value
4. **Learning iteration**: Use insights to improve approach

---

## 💡 Development Environment Setup

### Prerequisites

```bash
# Ensure dependencies are installed
pip install pyyaml requests  # Minimal requirements

# Test existing AutoProcessor first
cd /Users/thaddius/repos/inneros-zettelkasten
python3 development/src/ai/auto_processor.py --help
```

### File Structure

```
development/
├── inneros_batch_processor.py     # Main script (new)
├── backup_manager.py              # Backup utilities (new)  
├── processing_report.py           # Report generation (new)
└── src/ai/auto_processor.py       # Existing AI logic (reuse)
```

---

**This proof-of-concept will give you confidence and understanding needed for the full automated system. Start simple, build trust, then expand!**
