# Visual Capture POC - TDD Iteration 1 Plan

**Created**: 2025-09-29 18:45 PDT  
**Branch**: `feat/visual-capture-poc-tdd-1`  
**Timeline**: Oct 1-7, 2025 (1 week)  
**Status**: 🟢 **READY TO START**  
**Priority**: **P0** - Critical validation for project viability  

---

## 🎯 POC Objectives

### **Primary Goal**
Validate that screenshot + voice note temporal pairing (±60s) achieves >90% accuracy with real user data.

### **Secondary Goals**
1. Measure processing time per capture pair (<2min target)
2. Confirm zero disruption to existing automation
3. Generate capture notes that integrate with weekly review
4. Collect user feedback on workflow naturalness

### **Go/No-Go Criteria**
- ✅ **GO**: >90% pairing accuracy + positive user feedback → Proceed to Phase 1
- ❌ **NO-GO**: <80% accuracy or negative UX → Pivot to manual pairing or abandon voice integration

---

## 🔴 RED PHASE: Failing Tests (Day 1)

### **Test Suite: Voice Note Detection & Pairing**

#### **1. Voice Note Detection (5 tests)**
```python
def test_onedrive_voice_folder_detection():
    """Verify OneDrive Voice Recorder path exists and is readable"""
    
def test_voice_note_file_enumeration():
    """Scan folder and collect all .m4a voice recordings"""
    
def test_voice_timestamp_extraction():
    """Extract capture timestamp from voice filename (Samsung format)"""
    
def test_voice_metadata_collection():
    """Build manifest with filename, path, timestamp, file size"""
    
def test_empty_voice_folder_handling():
    """Gracefully handle no voice notes found"""
```

#### **2. Temporal Pairing Algorithm (6 tests)**
```python
def test_exact_timestamp_matching():
    """Match screenshot + voice with identical timestamps"""
    
def test_within_60s_window_matching():
    """Match captures within ±60 seconds"""
    
def test_multiple_candidates_closest_match():
    """When multiple voices match, choose closest timestamp"""
    
def test_unpaired_screenshot_handling():
    """Screenshots without matching voice note handled gracefully"""
    
def test_unpaired_voice_handling():
    """Voice notes without matching screenshot handled gracefully"""
    
def test_pairing_accuracy_measurement():
    """Calculate and report pairing success rate"""
```

#### **3. Capture Note Generation (4 tests)**
```python
def test_capture_note_template_creation():
    """Generate markdown with YAML frontmatter for paired captures"""
    
def test_screenshot_embedding():
    """Embed screenshot image with correct path"""
    
def test_voice_context_placeholder():
    """Add voice note reference (transcription placeholder for later)"""
    
def test_metadata_enrichment():
    """Include device, timestamps, pairing confidence score"""
```

#### **4. Real Data Integration (3 tests)**
```python
def test_process_real_capture_batch():
    """Process 10+ real captures from user's OneDrive"""
    
def test_measure_processing_time():
    """Verify <2min per capture pair processing time"""
    
def test_weekly_review_integration():
    """Capture notes appear in weekly review queue"""
```

**Total Tests**: 18 comprehensive failing tests

---

## 🟢 GREEN PHASE: Minimal Implementation (Day 2-5)

### **Core Components**

#### **1. VoiceNoteDetector (Day 2)**
```python
class VoiceNoteDetector:
    """Scan OneDrive Voice Recorder folder and extract metadata"""
    
    def __init__(self, onedrive_path: Path):
        self.voice_path = onedrive_path / "Voice Recorder"
        
    def scan_voice_notes(self) -> List[VoiceCapture]:
        """Return list of VoiceCapture objects with metadata"""
        
    def extract_timestamp(self, filename: str) -> datetime:
        """Parse Samsung voice recording filename for timestamp"""
```

#### **2. TemporalPairingEngine (Day 3-4)**
```python
class TemporalPairingEngine:
    """Match screenshots with voice notes using temporal proximity"""
    
    def __init__(self, matching_window_seconds: int = 60):
        self.window = matching_window_seconds
        
    def pair_captures(
        self, 
        screenshots: List[ScreenshotCapture],
        voice_notes: List[VoiceCapture]
    ) -> PairingResults:
        """Return paired, unpaired screenshots, unpaired voice notes"""
        
    def calculate_accuracy(self, results: PairingResults) -> float:
        """Measure pairing success rate"""
```

#### **3. CaptureNoteGenerator (Day 5)**
```python
class CaptureNoteGenerator:
    """Generate markdown capture notes from paired captures"""
    
    def generate_note(
        self,
        pair: CapturedPair,
        output_dir: Path
    ) -> Path:
        """Create markdown note with screenshot + voice context"""
        
    def create_yaml_frontmatter(self, pair: CapturedPair) -> str:
        """Generate metadata header"""
```

### **Data Classes**
```python
@dataclass
class VoiceCapture:
    filename: str
    path: Path
    timestamp: datetime
    duration: float
    file_size: int

@dataclass
class ScreenshotCapture:
    filename: str
    path: Path
    timestamp: datetime
    ocr_text: Optional[str]
    
@dataclass
class CapturedPair:
    screenshot: ScreenshotCapture
    voice: VoiceCapture
    time_delta: timedelta
    confidence: float  # 0-1 based on time proximity
    
@dataclass
class PairingResults:
    paired: List[CapturedPair]
    unpaired_screenshots: List[ScreenshotCapture]
    unpaired_voices: List[VoiceCapture]
    accuracy: float
```

---

## 🔵 REFACTOR PHASE: Utility Extraction (Day 6)

### **Extract 3-5 Utility Classes**

#### **1. TimestampExtractor**
- Samsung filename parsing for screenshots
- Samsung filename parsing for voice recordings
- Timezone normalization
- Edge case handling

#### **2. PairingValidator**
- Accuracy calculation
- Confidence scoring
- Statistics reporting
- Edge case detection

#### **3. CaptureMetadataBuilder**
- YAML frontmatter generation
- Device detection
- Source URL extraction (if available)
- Quality metrics

#### **4. FilePathManager**
- OneDrive path validation
- Output directory creation
- File naming conventions
- Duplicate handling

#### **5. PerformanceMonitor**
- Processing time tracking
- Memory usage measurement
- Progress reporting
- Bottleneck identification

---

## 📊 Validation Protocol (Day 7)

### **Real Data Testing**

#### **Data Collection**
1. Gather 10-15 real screenshot + voice pairs from Oct 1-6
2. Include edge cases:
   - Voice notes without screenshots
   - Screenshots without voice notes
   - Multiple captures in quick succession
   - Captures hours apart

#### **Metrics Collection**
| Metric | Target | Measurement |
|--------|--------|-------------|
| Pairing Accuracy | >90% | # correct pairs / # total pairs |
| Processing Time | <2min | Time per capture pair |
| False Positives | <5% | Incorrect pairings |
| False Negatives | <10% | Missed valid pairs |
| User Satisfaction | Positive | Qualitative feedback |

#### **Test Scenarios**
1. **Happy Path**: Screenshot taken, voice note within 30s
2. **Near Boundary**: Screenshot + voice exactly 60s apart
3. **No Match**: Screenshot without voice (e.g., UI reference)
4. **Multiple Candidates**: 3 voice notes within 60s window
5. **Batch Processing**: 10 captures at once

---

## 🎯 Acceptance Criteria

### **Must Have (P0)**
- [x] Voice notes detected from OneDrive path
- [x] Timestamps extracted from both file types
- [x] Pairing algorithm implemented with ±60s window
- [x] Capture notes generated in markdown format
- [x] **>90% pairing accuracy** on real data
- [x] **<2 minutes** processing time per pair
- [x] Zero disruption to existing automation

### **Should Have (P1)**
- [ ] Confidence scoring for pairs (0-1 scale)
- [ ] Statistics dashboard with metrics
- [ ] CLI command for manual validation
- [ ] Export pairing results for review

### **Could Have (P2)**
- [ ] Adjustable matching window (30s, 60s, 90s)
- [ ] Machine learning for pattern detection
- [ ] Location-based matching enhancement

---

## 🚀 Success Indicators

### **Quantitative**
- **Pairing Accuracy**: >90% correct matches
- **Processing Speed**: <2min per capture pair
- **Zero Errors**: No crashes or data loss
- **Integration**: Capture notes in weekly review

### **Qualitative**
- Workflow feels natural and unforced
- Voice context adds value (not just noise)
- Processing is fast enough to be done regularly
- You actually want to use this vs. current flow

---

## 🔗 Integration Points

### **Existing Systems to Leverage**
- ✅ **Samsung Screenshot Detector**: Reuse from TDD Iteration 1-6
- ✅ **OneDrive Path Detection**: Already working
- ✅ **LlamaVisionOCR**: For screenshot text extraction
- ✅ **Daily Note Generator**: Template patterns
- ✅ **WorkflowManager**: For note processing

### **New Systems to Build**
- 🆕 **VoiceNoteDetector**: POC core component
- 🆕 **TemporalPairingEngine**: POC innovation
- 🆕 **CaptureNoteGenerator**: New note type

---

## 📁 File Structure

```
development/
├── src/
│   ├── ai/
│   │   ├── voice_note_detector.py          # NEW
│   │   ├── temporal_pairing_engine.py      # NEW
│   │   ├── capture_note_generator.py       # NEW
│   │   └── visual_capture_utils.py         # NEW (utilities)
│   └── cli/
│       └── visual_capture_demo.py          # NEW (POC CLI)
└── tests/
    └── unit/
        ├── test_voice_detection_poc.py     # NEW (5 tests)
        ├── test_temporal_pairing_poc.py    # NEW (6 tests)
        ├── test_capture_generation_poc.py  # NEW (4 tests)
        └── test_real_data_integration.py   # NEW (3 tests)

Projects/
└── ACTIVE/
    └── visual-capture-poc-results.md       # NEW (Day 7 results)
```

---

## 🎯 Day-by-Day Plan

### **Day 1 (Oct 1): RED Phase**
- Create branch `feat/visual-capture-poc-tdd-1`
- Write all 18 failing tests
- Verify tests fail correctly
- Commit: "RED: 18 failing tests for Visual Capture POC"

### **Day 2 (Oct 2): Voice Detection**
- Implement `VoiceNoteDetector`
- Pass 5 voice detection tests
- Test with real OneDrive data
- Commit: "GREEN: Voice note detection working"

### **Day 3-4 (Oct 3-4): Temporal Pairing**
- Implement `TemporalPairingEngine`
- Pass 6 pairing algorithm tests
- Test with real capture pairs
- Commit: "GREEN: Temporal pairing algorithm complete"

### **Day 5 (Oct 5): Note Generation**
- Implement `CaptureNoteGenerator`
- Pass 4 note generation tests
- Generate sample capture notes
- Commit: "GREEN: Capture note generation working"

### **Day 6 (Oct 6): REFACTOR + Integration**
- Extract 3-5 utility classes
- Pass 3 real data integration tests
- Full system test with week's captures
- Commit: "REFACTOR: Utility extraction complete"

### **Day 7 (Oct 7): Validation & Decision**
- Process full week of real captures
- Measure all success metrics
- Document results in `visual-capture-poc-results.md`
- **Go/No-Go Decision** by end of day

---

## 📊 Expected Outcomes

### **If POC Succeeds (>90% accuracy)**
**Immediate Actions**:
1. Commit POC code with lessons learned
2. Plan Phase 1 implementation (2-3 weeks)
3. Update project priorities
4. Celebrate with user 🎉

**Next Steps**:
- Phase 1: Production-ready voice detection
- Phase 2: Voice transcription integration
- Phase 3: Full workflow automation

### **If POC Fails (<80% accuracy)**
**Fallback Options**:
1. **Manual Pairing UI**: User manually links screenshots + voice
2. **Screenshot Only**: Drop voice integration, focus on visual capture
3. **Wider Window**: Test 120s or 180s matching window
4. **Pivot to Reading Intake**: Return to bookmark import approach

---

## 🎉 Success Criteria Summary

**POC is successful if**:
- ✅ Pairing accuracy >90%
- ✅ Processing time <2min per pair
- ✅ User feedback is positive
- ✅ Workflow feels natural

**Decision Point**: October 8, 2025 (Go/No-Go)

---

**This POC validates the core innovation (temporal pairing) before committing to full system development. One week to prove viability.**
