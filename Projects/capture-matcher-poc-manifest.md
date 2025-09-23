# Capture Matcher POC - Project Manifest

**Created**: 2025-09-22 20:38 PDT  
**Status**: 🟢 **READY TO BUILD** → Immediate Implementation  
**Timeline**: 1 week maximum  
**Priority**: Critical - Validates core system assumption  
**Owner**: Thaddius • Assistant: Cascade  

---

## 🎯 POC Overview

### **Mission**
Validate the core hypothesis: **Screenshots + voice notes can be automatically paired by timestamp to create rich capture context with minimal user friction.**

### **Success Question**
Can we achieve >90% accurate pairing of screenshot + voice note captures with a simple temporal matching algorithm, and does this feel natural in a real knowledge worker's daily workflow?

---

## 📋 Scope Definition

### **✅ IN SCOPE (Minimal Viable Test)**
- **Timestamp Matching**: Screenshot + voice note pairing within ±60 seconds
- **Interactive Processing**: Desktop interface for reviewing matched pairs
- **Basic Note Creation**: Simple markdown template with image + transcription placeholder
- **Real-World Validation**: Process actual captures from daily workflow

### **❌ OUT OF SCOPE (Full System Features)**
- OCR text extraction from screenshots
- Automatic voice transcription 
- AI connection suggestions to existing notes
- Automated file monitoring/processing
- Mobile app or GUI development
- Integration with existing InnerOS AI systems

---

## 🔧 Technical Implementation

### **Core Script Architecture**
```python
# capture_matcher.py - Single file POC
class CaptureMatcherPOC:
    def __init__(self, screenshot_path, voice_path):
        self.screenshots_dir = screenshot_path
        self.voice_dir = voice_path
        self.match_threshold = 60  # seconds
    
    def parse_filename_timestamp(self, filename):
        """Extract timestamp from Samsung/iPhone filename patterns"""
        # Samsung: Screenshot_20250122_143512.png
        # iPhone: IMG_20250122_143512.png  
        # Voice: Recording_20250122_143528.m4a
        
    def scan_captures(self, date_range=7):
        """Find recent screenshots and voice notes with filename timestamps"""
        
    def match_by_filename_timestamp(self, captures):
        """Pair files by parsing filename timestamps within threshold"""
        
    def interactive_review(self, matches):
        """Present matched pairs for user review"""
        
    def create_capture_note(self, pair, annotation):
        """Generate markdown note with metadata"""
```

### **File System Setup**
```
inneros-capture-poc/
├── capture_matcher.py      # Main POC script
├── config.py              # OneDrive paths configuration  
├── test_captures/         # Sample files for development
├── output_notes/          # Generated capture notes
├── requirements.txt       # Minimal dependencies
├── README.md              # Setup and usage instructions
└── test_report.md         # POC results documentation
```

### **OneDrive Path Configuration**
```python
# config.py - User-specific paths
ONEDRIVE_BASE = "/Users/thaddius/Library/CloudStorage/OneDrive-Personal"

PATHS = {
    "screenshots": f"{ONEDRIVE_BASE}/backlog/Pictures/Samsung Gallery/DCIM/Screenshots",
    "voice_notes": f"{ONEDRIVE_BASE}/Voice Recorder", 
    "output_notes": "~/inneros/captures/poc/",
    "archive": "~/inneros/captures/poc/processed/"
}

MATCHING = {
    "time_threshold": 60,      # seconds
    "max_lookback_days": 7,    # process recent captures only
    "min_file_size": 1024      # bytes, filter tiny files
}
```

---

## 🎮 POC Workflow

### **Daily Usage Pattern**
```bash
# Morning routine - process yesterday's captures
cd inneros-capture-poc
python3 capture_matcher.py --yesterday

# Review matched pairs interactively
# [Script shows screenshot + plays voice note]
# [User adds quick annotation]
# [Auto-generates capture note]

# Check processing stats
python3 capture_matcher.py --stats
```

### **Interactive Review Interface**
```
========================================
Capture Pair #3/7 - 2025-01-22 14:35
========================================

Screenshot: screenshot_20250122_143512.png
Voice Note: Recording_20250122_143528.m4a 
Time Gap: 16 seconds

[Opening screenshot...]
[Playing audio: "This connects to my CAP theorem research..."]

Your annotation: [cursor here]

Actions:
[k] Keep & annotate
[s] Skip this pair  
[d] Delete (temporary capture)
[m] Manual pairing mode
[q] Quit and save
========================================
```

---

## 📅 POC Development Timeline

### **Day 1-2: Environment Setup**
- [ ] Verify OneDrive sync paths exist and are accessible
- [ ] Create POC script structure with path configuration
- [ ] Test file scanning and timestamp extraction  
- [ ] Document existing screenshot and voice note naming patterns

### **Day 3-4: Core Algorithm**
- [ ] Implement timestamp-based matching algorithm
- [ ] Add interactive review interface (terminal-based)
- [ ] Create basic capture note template with metadata
- [ ] Test with sample files to refine matching threshold

### **Day 5-6: Real-World Testing** 
- [ ] Process 20+ actual screenshot + voice note pairs
- [ ] Measure matching accuracy and user workflow friction
- [ ] Document sync latency and file availability timing
- [ ] Refine threshold and handling of edge cases

### **Day 7: Evaluation & Documentation**
- [ ] Calculate success metrics (match accuracy, processing time)
- [ ] Document user experience friction points
- [ ] Generate go/no-go recommendation for full system
- [ ] Create test report with quantitative results

---

## 🧪 Test Scenarios

### **Scenario 1: Perfect Pair**
- **Setup**: `Screenshot_20250122_143512.png` + `Recording_20250122_143528.m4a`
- **Expected**: Successful automatic pairing via filename parsing
- **Validation**: 16-second gap within 60-second threshold

### **Scenario 2: Screenshot Only**
- **Setup**: Screenshot without corresponding voice note
- **Expected**: Present for processing without voice context
- **Validation**: No error, graceful handling of single capture

### **Scenario 3: Multiple Rapid Captures**
- **Setup**: `Screenshot_20250122_143512.png`, `Screenshot_20250122_143542.png`, `Screenshot_20250122_143601.png` + 2 voice notes
- **Expected**: Correct pairing logic (closest filename timestamps)
- **Validation**: No incorrect pairings, manual resolution option

### **Scenario 4: Delayed Voice Note**
- **Setup**: Voice note 2 minutes after screenshot
- **Expected**: No automatic pairing (outside threshold)
- **Validation**: Both files available for manual review

### **Scenario 5: Sync Latency**
- **Setup**: Capture on phone, check desktop availability
- **Expected**: Files available within 5 minutes
- **Validation**: OneDrive sync performance acceptable

---

## 📊 POC Success Metrics

### **Technical Validation**
- **Match Accuracy**: >90% correct automatic pairings
- **Processing Speed**: <30 seconds per capture pair review
- **Sync Latency**: Files available on desktop <5 minutes after mobile capture
- **File Format Support**: Handle various voice note formats (m4a, mp3, wav)

### **User Experience Validation**  
- **Daily Usage**: Successfully process captures for 7 consecutive days
- **Workflow Friction**: <2 minutes overhead vs current screenshot accumulation
- **Completion Rate**: >80% of matched pairs result in created capture notes
- **Satisfaction**: User would continue using this approach (yes/no)

---

## 🎯 POC Deliverables

### **Working Software**
- [ ] `capture_matcher.py` - Functional POC script with user paths configured
- [ ] Configuration files for OneDrive integration
- [ ] 20+ processed real-world capture pairs
- [ ] Generated capture notes in markdown format

### **Validation Documentation**
- [ ] **Performance Report**: Match accuracy, processing times, sync latency
- [ ] **User Experience Report**: Friction points, workflow integration success
- [ ] **Technical Report**: File format compatibility, error handling
- [ ] **Go/No-Go Recommendation**: Proceed to full system or pivot

### **Setup Documentation**
- [ ] **Installation Guide**: OneDrive path setup, Python environment
- [ ] **Usage Instructions**: Daily workflow, command examples
- [ ] **Troubleshooting Guide**: Common issues and solutions

---

## ⚠️ Risk Mitigation

### **Technical Risks**
- **OneDrive sync unreliable** → Test with local folder monitoring as backup
- **Timestamp extraction failure** → Multiple parsing methods, manual fallback
- **File format incompatibility** → Comprehensive format testing
- **Path configuration errors** → Validation checks and clear error messages

### **Workflow Risks**
- **POC too complex for testing** → Simplify to core matching only
- **Daily testing burden** → Batch processing mode for accumulated captures
- **Insufficient test data** → Generate synthetic test scenarios if needed

---

## 🔄 Decision Matrix

### **Proceed to Full System If:**
- Match accuracy >85% (acceptable threshold)
- User completes 7-day testing without abandoning
- Sync latency consistently <10 minutes
- Voice + screenshot pairing feels valuable vs screenshot-only

### **Pivot or Abort If:**
- Match accuracy <70% (too many false positives)
- Daily testing becomes burdensome friction
- OneDrive sync unreliable for workflow
- Voice notes don't add sufficient value over screenshots alone

---

## 🚀 Quick Start Commands

```bash
# Clone and setup POC
git clone [repo] inneros-capture-poc
cd inneros-capture-poc

# Configure paths for your OneDrive setup  
cp config.template.py config.py
# Edit config.py with your actual paths

# Test with recent captures
python3 capture_matcher.py --scan

# Interactive processing session
python3 capture_matcher.py --process

# Generate test report
python3 capture_matcher.py --report
```

---

**This POC validates the core innovation: automated pairing of visual + audio context to eliminate annotation burden while preserving rich capture information.**

**Success here unlocks the full Knowledge Capture System that transforms mobile screenshots from "capture graveyard" into "knowledge accelerator."**
