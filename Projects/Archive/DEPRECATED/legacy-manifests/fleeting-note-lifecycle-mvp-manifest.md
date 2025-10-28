# Fleeting Note Lifecycle Management MVP - Project Manifest

**Project Type**: Phase 5.6 Extension (Integration Project)  
**Created**: 2025-09-17 14:37 PDT  
**Owner**: Thaddius • Assistant: Cascade  
**Status**: Planning Complete → Ready for Implementation  
**Integration Reference**: `.windsurf/workflows/integration-project-workflow.md`

---

## 🎯 Vision & Purpose

**Problem**: Fleeting notes accumulate in the system without systematic lifecycle management, creating "digital hoarding" where valuable ideas stagnate and low-value content clutters the knowledge graph.

**Solution**: Extend existing Phase 5 AI workflows with systematic fleeting note lifecycle management that provides age detection, quality-based triage, and automated promotion workflows.

**Core Promise**: "Transform fleeting note accumulation into systematic knowledge progression with AI-powered lifecycle management."

---

## 🔍 Integration Analysis Summary

### **Current System Strengths** ✅
- **WorkflowManager**: Robust AI processing infrastructure (quality scoring, tagging, connections)
- **Weekly Review**: Existing candidate scanning and recommendation system
- **Directory Organization**: Production-ready file move system with safety features
- **CLI Infrastructure**: Established patterns for new command integration

### **Identified Gap** ❌
- **No Fleeting Note Aging**: No systematic detection of stale fleeting notes
- **No Lifecycle Workflow**: Notes processed into fleeting status but no progression workflow
- **No Quality-Based Routing**: High-quality fleeting notes not systematically promoted
- **No Bulk Operations**: Individual note processing only, no batch fleeting management

### **Integration Approach** ✅
- **Extend WorkflowManager**: Add fleeting-specific methods to existing class
- **Leverage Existing AI**: Use current quality scoring, tagging, connection discovery
- **CLI Pattern Reuse**: Follow weekly review command patterns for new flags
- **Schema Preservation**: No new metadata fields needed, use existing workflow states

---

## 👥 User Stories (MVP Scope)

### **Epic**: Systematic Fleeting Note Lifecycle Management
*As a knowledge worker, I want systematic fleeting note progression workflows so that valuable ideas get promoted and clutter gets cleared efficiently.*

### **US-1: Fleeting Note Age Detection** (Phase 1)
**Story**: *As a solopreneur, I want to see which fleeting notes are getting stale so I can prioritize which ones need attention.*

**Acceptance Criteria**:
- [ ] System scans `Fleeting Notes/` directory for all markdown files
- [ ] Calculates age based on `created` field in YAML frontmatter
- [ ] Categorizes by age: New (0-7d), Recent (8-30d), Stale (31-90d), Old (90d+)
- [ ] CLI command: `--fleeting-health` displays distribution and summary stats
- [ ] Output includes count per category and oldest note identification

**Technical Integration**:
- Extends `WorkflowManager` with `analyze_fleeting_notes()` method
- Reuses existing `_scan_directory_for_candidates()` pattern
- Uses existing metadata parsing infrastructure

---

### **US-2: Quality-Based Fleeting Triage** (Phase 2)
**Story**: *As a busy professional, I want AI to suggest which fleeting notes are worth promoting so I don't waste time reviewing low-value content.*

**Acceptance Criteria**:
- [ ] Leverages existing `process_inbox_note()` quality scoring (0-1 scale)
- [ ] Generates promotion recommendations: >0.7 promote, >0.4 keep, <0.4 archive
- [ ] CLI command: `--fleeting-triage` displays actionable checklist
- [ ] Output format matches weekly review pattern with rationale
- [ ] Includes confidence scores and improvement suggestions

**Technical Integration**:
- Extends existing AI processing pipeline
- Reuses `_process_candidate_for_recommendation()` pattern
- Uses existing checklist formatting from weekly review

---

### **US-3: Simple Promotion Workflow** (Phase 3)
**Story**: *As a knowledge worker, I want a quick way to promote high-quality fleeting notes to permanent status.*

**Acceptance Criteria**:
- [ ] CLI command: `--promote-note path/to/fleeting.md`
- [ ] Updates YAML: `type: fleeting` → `type: permanent`, `status: promoted` → `status: draft`
- [ ] Moves file from `Fleeting Notes/` → `Permanent Notes/` using existing DirectoryOrganizer
- [ ] Preserves all content, metadata, and links
- [ ] Includes comprehensive backup and rollback safety features

**Technical Integration**:
- Uses existing `promote_note()` method with fleeting-specific routing
- Leverages Production-ready DirectoryOrganizer (P0+P1 complete)
- Maintains existing safety-first approach with backups

---

## 🏗️ Technical Architecture (Integration Design)

### **Core Integration Points**
```python
class WorkflowManager:
    # Existing methods preserved ✅
    def process_inbox_note(self, ...)     # Keep intact
    def generate_weekly_recommendations(...) # Keep intact
    def promote_note(self, ...)           # Keep intact
    
    # NEW: Fleeting lifecycle extensions
    def analyze_fleeting_notes(self) -> FleetingAnalysis
    def generate_fleeting_health_report(self) -> Dict  
    def generate_fleeting_triage_recommendations(self) -> Dict
    def promote_fleeting_note(self, note_path: str) -> Dict
```

### **CLI Integration Pattern**
```bash
# Extend existing workflow_demo.py (NOT new CLI tool)
python3 src/cli/workflow_demo.py . --fleeting-health
python3 src/cli/workflow_demo.py . --fleeting-triage  
python3 src/cli/workflow_demo.py . --promote-note path/to/note.md
```

### **Data Structures**
```python
@dataclass
class FleetingAnalysis:
    total_notes: int
    age_distribution: Dict[str, int]  # {"new": 5, "recent": 8, "stale": 3, "old": 1}
    oldest_note: Optional[Dict]
    recommendations_count: int
    
@dataclass  
class FleetingRecommendation:
    note_path: str
    age_days: int
    quality_score: float
    action: str  # "promote", "keep", "archive"
    rationale: str
    confidence: float
```

---

## 📊 Integration Success Criteria

### **Functionality Preservation** ✅
- [ ] All existing 66/66 tests pass unchanged
- [ ] All existing CLI commands (`--weekly-review`, `--process-inbox`, etc.) work normally
- [ ] All existing AI workflows (quality scoring, tagging, connections) function properly
- [ ] Performance benchmarks maintained: <10s summarization, <5s similarity, <20s connection mapping

### **Extension Validation** ✅  
- [ ] New fleeting commands integrate seamlessly with existing workflow
- [ ] No new metadata fields needed (uses existing `type`, `created`, `status`)
- [ ] New CLI flags follow established argument patterns
- [ ] Error handling matches existing WorkflowManager patterns

### **User Experience Continuity** ✅
- [ ] Existing weekly review workflow unchanged
- [ ] New fleeting commands discoverable through `--help`
- [ ] Output formatting matches existing CLI tools (checklist, progress, JSON export)
- [ ] Performance impact <1 second for typical fleeting collections

---

## 🚀 Implementation Phases

### **Phase 1: Foundation** (Week 1)
**Focus**: Age detection and health reporting

**Deliverables**:
- [ ] `WorkflowManager.analyze_fleeting_notes()` method
- [ ] `WorkflowManager.generate_fleeting_health_report()` method  
- [ ] CLI flag: `--fleeting-health` with summary stats
- [ ] TDD test suite: 5-8 comprehensive tests
- [ ] Documentation: CLI reference update

**Success Metrics**:
- [ ] Age categorization working for 50+ fleeting notes  
- [ ] Command execution <3 seconds
- [ ] All existing tests remain passing

### **Phase 2: AI Triage** (Week 1-2)
**Focus**: Quality-based recommendations using existing AI

**Deliverables**:
- [ ] `WorkflowManager.generate_fleeting_triage_recommendations()` method
- [ ] CLI flag: `--fleeting-triage` with checklist output
- [ ] Integration with existing quality scoring pipeline
- [ ] TDD test suite: 6-10 tests covering AI integration
- [ ] JSON export support for automation

**Success Metrics**:
- [ ] AI recommendations >80% user satisfaction
- [ ] Triage execution <10 seconds for 50+ notes  
- [ ] Output format matches weekly review quality

### **Phase 3: Promotion Workflow** (Week 2)
**Focus**: Safe file promotion using existing DirectoryOrganizer

**Deliverables**:
- [ ] `WorkflowManager.promote_fleeting_note()` method  
- [ ] CLI flag: `--promote-note` with safety features
- [ ] Integration with existing DirectoryOrganizer (backup, validation, rollback)
- [ ] TDD test suite: 5-8 tests for promotion workflow
- [ ] Complete documentation update

**Success Metrics**:
- [ ] Zero data loss during promotion operations
- [ ] Link integrity preserved (existing P0-3 system)
- [ ] Promotion execution <5 seconds per note

---

## 🔗 Dependencies & Prerequisites

### **Completed Infrastructure** ✅
- **Phase 5 AI Features**: Quality scoring, tagging, connections all production-ready
- **DirectoryOrganizer**: P0+P1 safety-first file move system complete  
- **WorkflowManager**: Robust AI processing with 48 passing tests
- **CLI Infrastructure**: Established patterns in workflow_demo.py

### **Critical Path Items** ❌
- [ ] **Template Processing Bug**: Must resolve before any template-based features
- [ ] **System Health**: Run comprehensive test suite to ensure clean baseline
- [ ] **Performance Baseline**: Establish current benchmark for impact measurement

### **Technical Requirements**
- **Python 3.9+**: Existing requirement maintained
- **Ollama Integration**: Leverage existing AI infrastructure  
- **Test Coverage**: Maintain current 66/66 test passing rate
- **CLI Patterns**: Follow established argparse and output formatting

---

## 📈 Success Metrics & KPIs

### **Phase 1 Targets**
- **Detection Accuracy**: 100% accurate age categorization
- **Performance**: <3 seconds for health report on 100+ fleeting notes
- **User Value**: Clear identification of stale notes requiring attention

### **Phase 2 Targets**
- **Recommendation Quality**: >80% user acceptance of AI suggestions
- **Processing Speed**: <10 seconds for complete triage of 50+ notes  
- **Decision Support**: Clear action items with confidence scores

### **Phase 3 Targets**
- **Safety**: Zero data loss, 100% link integrity preservation  
- **Efficiency**: 70% reduction in manual promotion time
- **System Health**: Steady reduction in fleeting note accumulation

### **Overall MVP Success**
- **Time Savings**: 50% reduction in fleeting note management overhead
- **Quality Improvement**: Higher rate of valuable idea promotion to permanent status
- **System Cleanliness**: Controlled fleeting note collection size
- **Integration Success**: Seamless operation with existing Phase 5 workflows

---

## 🔄 Workflow Integration

### **Daily Operations**
```bash
# Morning fleeting health check (30 seconds)
python3 src/cli/workflow_demo.py . --fleeting-health

# Quick triage during weekly review
python3 src/cli/workflow_demo.py . --fleeting-triage --export triage-$(date +%Y-%m-%d).md

# Promotion of high-quality notes  
python3 src/cli/workflow_demo.py . --promote-note "Fleeting Notes/high-quality-idea.md"
```

### **Weekly Review Integration**
- Include fleeting health in existing weekly review workflow
- Use triage recommendations as input for promotion decisions
- Track progression metrics (stale note reduction, promotion rate)

### **Monthly Assessment**
- Analyze fleeting note lifecycle health trends
- Evaluate AI recommendation accuracy  
- Adjust quality thresholds based on user feedback

---

## 📝 Risk Assessment & Mitigation

### **Integration Risks**
- **Schema Conflicts**: MITIGATED - Uses existing metadata fields only
- **Performance Impact**: MITIGATED - Leverages existing efficient AI pipeline  
- **Workflow Disruption**: MITIGATED - Extends rather than replaces existing commands
- **Data Safety**: MITIGATED - Uses production-tested DirectoryOrganizer with backups

### **Technical Risks**
- **AI Service Availability**: MITIGATED - Existing graceful fallback patterns
- **File System Operations**: MITIGATED - Proven safety-first approach with rollback
- **Scale Performance**: MITIGATED - Built on existing benchmarked infrastructure

### **User Experience Risks**
- **Command Complexity**: MITIGATED - Follows established CLI patterns
- **Output Overwhelm**: MITIGATED - Uses existing checklist formatting approach
- **Learning Curve**: MITIGATED - Natural extension of known weekly review workflow

---

## 🎯 Next Steps (Immediate Actions)

### **Pre-Implementation** (Today)
1. **System Health Check**: Run full test suite to ensure clean baseline
2. **Performance Baseline**: Measure current WorkflowManager processing times
3. **Integration Analysis**: Review existing code patterns for consistency

### **Phase 1 Start** (This Week)
1. **TDD RED**: Create failing tests for fleeting note age detection
2. **Architecture Setup**: Extend WorkflowManager with fleeting analysis methods
3. **CLI Integration**: Add --fleeting-health flag following existing patterns

### **Validation Approach**
- **Real Data Testing**: Use actual fleeting notes collection for validation
- **Performance Monitoring**: Ensure <3 second execution times maintained  
- **Integration Testing**: Verify existing functionality preserved

---

**Manifest Version**: 1.0  
**Next Review**: Weekly during implementation phases  
**Status**: Ready for TDD Implementation → Phase 1: Foundation
