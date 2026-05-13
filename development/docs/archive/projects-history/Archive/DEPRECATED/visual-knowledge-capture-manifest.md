# Visual Knowledge Capture System - Project Manifest v1

**Created**: 2025-09-21 19:24 PDT  
**Status**: 🟢 **DESIGN PHASE** → Real Workflow Analysis Complete  
**Priority**: High - Replaces Reading Intake Pipeline  
**Owner**: Thaddius • Assistant: Cascade  

---

## 🎯 Vision & Real Problem

### **Discovered Reality**
Your actual knowledge capture workflow is **visual-first, mobile-primary**:
- 50%+ captures happen on mobile via screenshots
- Visual memory is important (remember the LOOK of content)  
- Screenshots auto-sync to cloud but then accumulate unprocessed
- Need batch processing sessions when you have time/energy
- Preservation + Processing (not replacement)

### **Core Promise**
"Process your screenshot captures into searchable, connected knowledge notes while preserving the original visual context - with batch sessions that fit your actual energy patterns."

---

## 🚨 What We're NOT Building

### ❌ Traditional Reading Intake Pipeline
- Bookmark imports and RSS feeds (low usage)
- Text-first processing (doesn't match your capture behavior)
- Linear article → literature note workflow (too rigid)
- Daily processing requirements (doesn't fit energy patterns)

### ✅ What You Actually Need
- **Visual Capture Processing**: Screenshots → annotated notes
- **Preservation + Enhancement**: Keep originals, add searchability
- **Batch Processing**: Handle 10-50 captures when you have energy
- **Mobile-Optimized**: Built around phone as primary capture device

---

## 🏗️ Technical Architecture (Realistic)

### **Core Workflow**
```
Phone Screenshot → 
Cloud Auto-Sync → 
Processing Inbox → 
OCR + URL Detection → 
User Annotation Session → 
Preserved + Searchable Note
```

### **Key Components**

#### 1. **Cloud Sync Watcher** (Phase 1)
- Monitor cloud folder for new screenshots
- Auto-detect device source (iPhone, Desktop, etc.)  
- Move to processing inbox with metadata
- Duplicate detection and cleanup

#### 2. **Visual Capture Processor** (Phase 2)
- OCR text extraction from images
- URL detection (Twitter, articles, etc.)
- Image optimization for embedding
- Metadata extraction (timestamp, device, etc.)

#### 3. **Batch Annotation Interface** (Phase 3)
```bash
# Your processing session
inneros process-captures

# Interactive session:
===========================================
[IMAGE DISPLAYED HERE - 1/12]
===========================================
OCR: "The key insight about systems thinking..."
Source URL: https://twitter.com/...
Device: iPhone 15 | 2024-01-20 14:35
===========================================

Your notes: [cursor here]
Suggested tags: #systems-thinking #complexity
Related notes: [[Systems Theory]]

[q] Quick note  [d] Develop  [s] Skip  [x] Discard
===========================================
```

#### 4. **Knowledge Integration** (Phase 4)
- Auto-link to existing notes via AI
- Quality scoring for capture notes
- Weekly review integration
- Archive/organize processed originals

---

## 🎮 User Experience Design

### **Processing Modes**
```bash
# Quick triage - 20 captures in 10 minutes
inneros process-captures --mode quick --batch 20

# Deep processing - full attention to 5 captures  
inneros process-captures --mode deep --batch 5

# Weekly review - just mark keep/discard
inneros process-captures --mode triage --show-all
```

### **Real Workflow Integration**
- **No behavior change**: Keep taking screenshots exactly as you do
- **Energy-aware processing**: Batch when you have mental bandwidth
- **Visual memory preserved**: Original screenshots always accessible
- **Searchable enhancement**: OCR text makes captures findable

---

## 📊 Technical Requirements

### **Cloud Sync Integration**
```yaml
# Config for your cloud provider
cloud_sync:
  provider: "icloud"  # or your actual provider
  watch_folder: "/Screenshots/"  
  inbox_path: "~/inneros/captures/inbox/"
  processed_path: "~/inneros/captures/processed/"
  auto_detect_duplicates: true
  file_patterns: ["*.png", "*.jpg", "*.jpeg"]
```

### **OCR & Enhancement**
- **OCR Engine**: Tesseract or macOS native OCR
- **URL Extraction**: Regex patterns for Twitter, web URLs
- **Image Processing**: Resize/optimize for embedding
- **Metadata**: EXIF data, device detection, timestamp normalization

### **Note Template (Visual Capture)**
```yaml
---
type: capture
captured: 2024-01-20 14:35
device: iPhone 15
source_url: https://twitter.com/username/status/123
ocr_confidence: 0.89
tags: [systems-thinking, complexity]
quality_score: 0.75
status: inbox
---

# Visual Capture: Systems Thinking Tweet

![[2024-01-20-143523-twitter-systems.png]]

## OCR Text
The key insight about systems thinking is that behavior emerges from structure...

## My Notes
[Your annotation here]

## Related
- [[Systems Theory]]
- [[Emergence]]

## Source
- URL: https://twitter.com/username/status/123
- Captured: 2024-01-20 14:35 (iPhone)
```

---

## 🔧 Implementation Phases

### **Phase 1: Basic Cloud Sync (Weekend)**
- [ ] Set up cloud folder monitoring
- [ ] Create intake directory structure  
- [ ] Basic file move and metadata extraction
- [ ] Test with 5-10 screenshots

### **Phase 2: OCR Integration (Week 1)**
- [ ] Add OCR text extraction
- [ ] URL pattern detection
- [ ] Basic note template creation
- [ ] Test batch processing interface

### **Phase 3: Annotation Interface (Week 2)**  
- [ ] Interactive processing sessions
- [ ] Image display in terminal/browser
- [ ] Quick annotation workflow
- [ ] Export to knowledge vault

### **Phase 4: AI Enhancement (Week 3)**
- [ ] Auto-tagging for capture notes
- [ ] Connection discovery with existing notes
- [ ] Quality scoring integration
- [ ] Weekly review incorporation

---

## 📱 Device Integration

### **Mobile Optimization**
- **iPhone**: Screenshots auto-sync via iCloud
- **Processing**: Desktop/laptop batch sessions
- **Emergency**: Mobile web interface for urgent processing
- **Sync**: Bidirectional sync keeps everything current

### **Cross-Platform Support**
- **macOS**: Native OCR, Shortcuts integration
- **Windows**: Tesseract OCR, cloud sync
- **Linux**: Command-line friendly processing
- **Web**: Browser-based annotation interface

---

## 🚀 Success Metrics (Realistic)

### **Adoption Metrics**
- **Weekly Processing**: 1-2 batch sessions of 10-30 captures
- **Processing Time**: <30 seconds per capture average
- **Completion Rate**: >80% of captures get processed within 2 weeks
- **User Satisfaction**: Actually used vs. abandoned

### **Quality Metrics** 
- **OCR Accuracy**: >90% for clear text screenshots
- **Connection Discovery**: Find 2-3 related existing notes per batch
- **Knowledge Integration**: 30%+ of captures become permanent notes
- **Archive Management**: Original screenshots organized and accessible

---

## 💡 Implementation Strategy

### **Start Simple** 
```bash
#!/bin/bash
# capture_simple.sh - dead simple first version

echo "📸 Processing next capture:"
ls -t ~/captures/inbox/*.png | head -1 | xargs open

read -p "Your notes: " notes
if [ ! -z "$notes" ]; then
    echo "Saved: $notes"
    # Move to processed folder
fi
```

### **Validate Before Building**
- Test simple script for 1 week
- If you actually use it → build full system
- If not → learn what the real friction is

### **Integration with Existing System**
- **Reuse**: Batch processor safety systems
- **Extend**: WorkflowManager for capture note processing  
- **Integrate**: Weekly review includes capture notes
- **Preserve**: All existing CLI commands continue working

---

## 🎯 Next Immediate Steps

1. **Test the simple script** for 3-5 real screenshots
2. **Validate cloud sync** is actually working as expected
3. **Measure real processing time** for your annotation style
4. **Decide**: Build full system or iterate on simple version

---

**This replaces the Reading Intake Pipeline project with something that matches your actual knowledge capture behavior.**

**Key Insight**: You don't need to import bookmarks - you need to process the visual knowledge captures you're already creating daily.
