# Visual Knowledge Capture System - Project Manifest v2

**Created**: 2025-09-22 20:38 PDT  
**Updated**: 2025-09-29 18:40 PDT  
**Status**: 🟢 **READY FOR POC** → Implementation Starting Oct 1, 2025  
**Priority**: **P0** - Core Knowledge Workflow Enhancement  
**Owner**: Thaddius • Assistant: Cascade  

---

## 🎯 Project Overview

### **Vision**
Transform mobile screenshots and voice notes into connected knowledge within a Zettelkasten system, eliminating "capture graveyards" and accelerating content creation workflow.

### **Core Problem**
- **50+ screenshots weekly** accumulate across mobile/desktop without processing
- **Valuable insights lost** in device folders and cloud storage
- **No connection** between visual captures and existing knowledge base  
- **Mobile capture 90%** of workflow but zero processing capability
- **Screenshots + voice context** often captured together but never paired

### **Success Metric**
Screenshots no longer accumulate unprocessed; captured insights integrate seamlessly into content creation workflow with **80% processing rate within one week**.

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

## 🏗️ Solution Architecture

### **Three-Layer System**

#### **CAPTURE LAYER (Mobile - Zero Friction)**
```
Samsung S23: Screenshots + Voice Notes
├── Auto-sync: OneDrive  
├── Zero apps required
├── No processing burden
└── Natural capture behavior preserved
```

#### **PROCESSING LAYER (Desktop - Intelligence)**
```
Temporal Matching: Pair screenshots with voice notes
├── OCR Extraction: Text from images (LlamaVisionOCR ✅)
├── Voice Transcription: Speech to text
├── AI Enhancement: Tags, connections, quality scoring
└── Zettelkasten Integration: Link to existing notes
```

#### **KNOWLEDGE LAYER (Output - Creation Ready)**
```
Capture Notes: Image + annotation + metadata
├── Fleeting Notes: Quick insights
├── Permanent Notes: Synthesized knowledge  
└── Content Creation: Blog posts, videos, presentations
```

---

## 🔧 Core Features

### **1. Proximity Pairing (Innovation)** 🌟
- **Temporal Matching**: Screenshot + voice note within ±60 seconds
- **No Manual Linking**: Automatic association by timestamp
- **Graceful Degradation**: Handle unpaired captures elegantly
- **Smart Thresholds**: Adjust matching window based on capture patterns

### **2. Desktop Processing Station**
- **OCR Text Extraction**: Real LlamaVisionOCR integration (complete ✅)
- **Voice Transcription**: Whisper or cloud service integration
- **AI-Suggested Connections**: Link to existing Zettelkasten notes
- **Quality Filtering**: Separate "keeper" vs "temporary" captures
- **Batch Processing**: Energy-aware sessions fitting your workflow

### **3. Knowledge Integration**
- **Visual + Textual Preservation**: Embed images in markdown with searchable text
- **Auto-linking**: Connect to existing vault notes via AI analysis
- **Metadata Enrichment**: Device, timestamp, source URL detection
- **Weekly Review Integration**: Capture notes in promotion workflow

---

## 🛠️ Technical Requirements

### **Infrastructure Stack**
- **Sync**: OneDrive Samsung S23 → MacBook pipeline (operational ✅)
- **Runtime**: Python 3.8+ with processing frameworks
- **OCR**: LlamaVisionOCR (production-ready ✅)
- **Speech**: OpenAI Whisper or Azure Speech Services
- **AI**: Ollama GPT-4/Claude for connection discovery
- **Notes**: Markdown system compatible with Obsidian

### **File System Architecture**
```
OneDrive Paths (Samsung S23):
├── Screenshots: /Users/thaddius/Library/CloudStorage/OneDrive-Personal/backlog/Pictures/Samsung Gallery/DCIM/Screenshots
├── Voice Notes: /Users/thaddius/Library/CloudStorage/OneDrive-Personal/Voice Recorder
└── Processing: ~/inneros/captures/

Local Processing:
├── inbox/           # New captures awaiting processing
├── processed/       # Completed captures with notes
├── archived/        # Original files preserved
└── temp/            # Discarded/temporary captures
```

### **Metadata Schema**
```yaml
---
type: capture
captured: 2025-01-22 14:35:12
device: Samsung S23
source_url: https://example.com
voice_note: Recording_20250122_143528.m4a
transcription: "This connects to my CAP theorem research"
ocr_text: "Extracted text from image..."
quality_score: 0.75
tags: [distributed-systems, eventual-consistency]
connections: [[CAP Theorem]], [[System Design]]
status: processed
---

# Visual Capture - CAP Theorem Discussion

![Screenshot](screenshot_20250122_143512.png)

## Voice Context
This connects to my CAP theorem research - the consistency vs availability trade-off.

## OCR Content
"In distributed systems, the CAP theorem states that you can only guarantee two of three properties..."

## My Analysis
[Your synthesis and insights here]

## Related Notes
- [[CAP Theorem]]
- [[System Design Patterns]]
- [[Distributed Consensus]]
```

---

## 📅 Development Phases

### **Phase 0: POC Validation (Week 1 - Oct 1-7, 2025)** 🔥
**Goal**: Validate temporal pairing hypothesis with real data

- [ ] OneDrive voice note path detection and scanning
- [ ] Timestamp extraction from voice recordings
- [ ] Temporal pairing algorithm (±60s matching window)
- [ ] Basic capture note template generation
- [ ] Test with 10+ real screenshot + voice pairs from this week
- [ ] Measure pairing accuracy (target: >90%)
- [ ] **Go/No-Go Decision**: Oct 8 based on results

### **Phase 1: Foundation (Week 2-3)**
*Only proceed if POC succeeds*

- [ ] OneDrive sync path monitoring and file detection
- [ ] Production-ready timestamp-based pairing
- [ ] Enhanced capture note template with metadata
- [ ] Manual processing workflow with file organization

### **Phase 2: Intelligence (Week 4-5)**  
- [ ] Voice transcription pipeline (Whisper integration)
- [ ] AI connection discovery to existing Zettelkasten notes
- [ ] Quality scoring and content classification

### **Phase 3: Workflow Integration (Week 6-7)**
- [ ] Weekly review system integration for capture notes
- [ ] Batch processing interface with quality filtering
- [ ] Archive management and duplicate detection
- [ ] CLI integration with existing InnerOS tools

### **Phase 4: Scale & Polish (Week 8)**
- [ ] Performance optimization for 100+ weekly captures
- [ ] Advanced matching algorithms (location, content similarity)
- [ ] Content creation template integration
- [ ] Analytics dashboard and processing metrics

---

## 📊 Success Criteria

### **POC Success Criteria (Phase 0)**
- **>90% pairing accuracy**: Correctly match screenshot + voice note pairs
- **<2 minutes processing time**: Per capture pair with note generation
- **Zero disruption**: Existing automation continues working
- **User satisfaction**: Workflow feels natural, not forced

### **Processing Metrics (Full System)**
- **80% processing rate**: Captures processed within one week of creation
- **50% note generation**: Captures that become fleeting or permanent notes
- **10+ weekly connections**: Links discovered to existing knowledge base
- **Searchable content**: Screenshots findable by visual and textual content

### **Workflow Impact**
- **Content creation velocity**: 25% increase in blog posts/presentations
- **Knowledge integration**: Captures successfully linked to existing notes
- **User adoption**: Daily use without abandonment after 30 days
- **Processing efficiency**: <2 minutes average per capture pair

### **Technical Performance**
- **Sync latency**: <5 minutes from mobile capture to desktop availability
- **Matching accuracy**: >90% correct screenshot + voice pairings
- **OCR quality**: >85% accuracy on clear text screenshots (achieved ✅)
- **Transcription quality**: >90% accuracy for clear voice recordings

---

## 🚨 Risk Mitigation

### **Technical Risks**
- **OneDrive sync delays** → Test alternative cloud providers, local sync options
- **Timestamp matching failures** → Manual pairing interface, fuzzy matching
- **Voice transcription errors** → Human review step, confidence scoring
- **Processing overwhelm** → Smart batching, priority scoring, auto-filtering

### **Workflow Risks**
- **Mobile friction** → Zero-change capture behavior, desktop-only processing
- **Knowledge integration complexity** → Gradual rollout, manual override options
- **POC failure** → Pivot to manual pairing or abandon voice note integration

---

## 🔗 Integration Points

### **Existing InnerOS Systems (70% Built)**
- ✅ **Samsung Screenshot OCR**: TDD Iterations 1-6 complete with real LlamaVisionOCR
- ✅ **OneDrive Detection**: Samsung naming patterns and path scanning
- ✅ **Daily Note Generation**: With embedded images and metadata
- ✅ **Smart Linking**: Automatic connection discovery
- ✅ **Batch Processor**: Safety systems with backup/rollback
- ✅ **AI Workflow**: Auto-tagging, quality scoring for capture notes
- ✅ **Weekly Review**: Integration points ready for capture notes
- ✅ **Directory Organizer**: Safe file moves with backup/rollback capability

### **External Services**
- **OneDrive API**: Monitoring and file management
- **OCR**: LlamaVisionOCR (production ✅)
- **Speech Services**: OpenAI Whisper, Azure Speech, Google Speech-to-Text
- **AI Services**: Ollama GPT-4/Claude for connection discovery and enhancement

---

## 🎯 Immediate Next Steps (POC - Week 1)

### **Day 1-2: Voice Detection & Timestamp Extraction**
1. Scan OneDrive Voice Recorder folder
2. Extract timestamps from voice recording filenames
3. Build file manifest with metadata

### **Day 3-4: Temporal Pairing Algorithm**
1. Implement ±60s matching window
2. Test with 10+ real capture pairs
3. Measure accuracy and edge cases

### **Day 5-6: Capture Note Generation**
1. Create combined markdown notes
2. Embed screenshots with voice context
3. Add metadata and placeholders

### **Day 7: Validation & Go/No-Go**
1. Process full week of captures
2. Measure success criteria
3. User feedback and decision

---

## 💡 Key Insights

**Why This Replaces Reading Intake Pipeline**:
- You don't save bookmarks regularly (observed behavior)
- You DO take 50+ screenshots per week (actual workflow)
- Visual memory is important (remember the LOOK of content)
- Voice context adds annotation without typing burden

**Innovation: Temporal Pairing**:
- Eliminates manual screenshot annotation
- Captures context in natural speech (easier than typing)
- ±60s window handles real-world capture patterns
- Graceful handling of unpaired items

**Foundation Already Built**:
- Samsung Screenshot system (TDD Iterations 1-6) provides 70% of infrastructure
- Only missing: Voice note detection + temporal pairing logic
- POC can be completed in 1 week using existing components

---

**This system transforms the most natural knowledge capture behavior (mobile screenshots + voice context) into the most powerful knowledge building system (connected Zettelkasten network).**

**Status**: Ready for POC implementation starting October 1, 2025.
