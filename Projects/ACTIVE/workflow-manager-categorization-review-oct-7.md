# WorkflowManager Domain Categorization Review

**Date**: 2025-10-07 (Tuesday)  
**Purpose**: Review and refine domain categorization from Monday's extraction  
**Status**: 🟡 IN REVIEW - Addressing borderline cases

---

## Executive Summary

**Overall Assessment**: ✅ Domain boundaries are well-defined with clear separation of concerns

**Key Findings**:
- 59 methods confirmed (matches extraction)
- 4 borderline cases identified requiring assignment decisions
- LOC estimates need adjustment based on coupling analysis
- Extraction order recommendation: Analytics → Connections → Core → AI

---

## Borderline Method Decisions

### 1. `_merge_tags` (line 760) - MOVE TO UTILITIES

**Current**: AIEnhancementManager  
**Recommendation**: ✅ **WorkflowUtilities**

**Rationale**:
- Pure utility method (9 LOC) with no AI logic
- Simple set operations + config reference
- Multiple managers may need tag merging
- Keeps AIEnhancementManager focused on AI

**Impact**: -9 LOC from AIEnhancementManager

---

### 2. `_load_notes_corpus` (line 743) - MOVE TO UTILITIES

**Current**: AIEnhancementManager  
**Recommendation**: ✅ **WorkflowUtilities**

**Rationale**:
- Pure file I/O (15 LOC) with no domain logic
- Could be used by both AI and Analytics
- Similar to `_get_all_notes` pattern
- Reduces cross-domain coupling

**Impact**: -15 LOC from AIEnhancementManager

---

### 3. `promote_fleeting_note` (line 1840) - SPLIT ACROSS DOMAINS

**Current**: AIEnhancementManager (134 LOC)  
**Recommendation**: ⚠️ **SPLIT into Core + AI**

**Proposed Split**:

**CoreWorkflowManager.promote_fleeting_note()** (~100 LOC):
- Path resolution and validation
- Auto-detect target type from metadata
- DirectoryOrganizer file moves
- Frontmatter updates
- Promotion workflow orchestration

**AIEnhancementManager.assess_promotion_readiness()** (~30 LOC):
- AI quality assessment
- Return quality score + recommendations

**Rationale**:
- Core owns lifecycle management (note promotion is workflow)
- AI provides assessment (quality scoring is AI domain)
- Clear interface contract for testability

**Impact**: 
- CoreWorkflowManager: +100 LOC
- AIEnhancementManager: +30 LOC (new method)

---

### 4. Session Management (lines 2227-2266) - KEEP IN CORE

**Current**: CoreWorkflowManager  
**Recommendation**: ✅ **Keep in CoreWorkflowManager**

**Rationale**:
- Session management is workflow orchestration
- Core coordinates AI operations within safe transactions
- Proper separation: Core manages when/how, AI manages what
- ~50 LOC doesn't justify 5th manager

**Impact**: No change

---

## Revised Domain Distribution

| Domain | Methods | LOC (Original) | LOC (Revised) | Change |
|--------|---------|----------------|---------------|--------|
| CoreWorkflowManager | 12 | 180-220 | **280-320** | +100 |
| AnalyticsManager | 26 | 380-420 | **380-420** | 0 |
| AIEnhancementManager | 16 | 550-650 | **500-600** | -50 |
| ConnectionManager | 15 | 350-450 | **350-450** | 0 |
| WorkflowUtilities | 5 | 0 | **40-60** | +40-60 |
| **TOTAL** | **74** | **1460-1740** | **1550-1850** | +90-110 |

**Key Changes**:
- Core gains `promote_fleeting_note` orchestration (+100)
- AI loses utilities (-24) but gains assessment method (+30)
- New WorkflowUtilities extracted (+40-60)

---

## Extraction Order: Analytics → Connections → Core → AI

**1. AnalyticsManager** (Week 2, Days 1-2)
- ✅ Lowest coupling - pure metrics
- ✅ No AI dependencies
- **Risk**: LOW

**2. ConnectionManager** (Week 2, Days 3-4)
- ⚠️ Medium coupling - depends on Analytics
- **Risk**: MEDIUM

**3. CoreWorkflowManager** (Week 2, Days 5-6)
- 🔴 High coupling - orchestrates all managers
- **Risk**: MEDIUM-HIGH

**4. AIEnhancementManager** (Week 2, Day 7)
- 🔴 Highest coupling - complex AI operations
- **Risk**: HIGH (mitigated by earlier extractions)

**Strategy**: Extract least coupled → most coupled to minimize integration issues

---

## Critical: `process_inbox_note` Splitting Strategy

**Current**: 268 LOC monolithic method

**Proposed Split**:
```python
# CoreWorkflowManager (orchestration ~50 LOC)
def process_inbox_note(self, note_path, dry_run, fast):
    note_data = self._load_and_validate(note_path)
    analytics_result = self.analytics.assess_quality(note_data)
    ai_result = self.ai_enhancement.enhance_note(note_data, fast)
    connections = self.connections.discover_links(note_data)
    return self._merge_and_save(note_data, results)
```

**Domain Methods**:
- **AnalyticsManager.assess_quality()**: ~60 LOC
- **AIEnhancementManager.enhance_note()**: ~100 LOC
- **ConnectionManager.discover_links()**: ~50 LOC

**Total**: ~260 LOC (distributed vs. 268 monolithic)

**Strategy**: Extract domain methods BEFORE splitting orchestration

---

## Week 1 Updated Schedule

### ✅ Monday Oct 6 (COMPLETED)
- Method extraction (59 methods)
- Preliminary categorization

### 🟢 Tuesday Oct 7 (TODAY)
- [x] Domain categorization review
- [x] Borderline method decisions
- [x] LOC estimate adjustments
- [x] Extraction order defined

### Wednesday Oct 8
- [ ] Interface design for all 4 managers
- [ ] WorkflowUtilities class design
- [ ] Method contracts and return types
- [ ] Manager coordination pattern decision

### Thursday Oct 9
- [ ] Cross-domain dependency mapping
- [ ] `process_inbox_note` split design
- [ ] Manager-to-manager delegation patterns

### Friday Oct 10 - RED Phase
- [ ] Write 30 failing tests for new architecture
- [ ] Test each manager interface
- [ ] Test manager coordination

### Weekend Oct 11-12
- [ ] Review and refine
- [ ] External review
- [ ] Week 2 GREEN phase prep

---

## Decision Points for Wednesday

**1. Manager Coordination Pattern**
- Option A: Direct references (simple)
- Option B: Interface-based (testable)
- Option C: Event-driven (over-engineered)
- **Recommendation**: Start with A, refactor to B if needed

**2. WorkflowUtilities Architecture**
- Single utilities class (simple)
- Multiple modules (FileUtils, TagUtils)
- **Recommendation**: Single class, max 10 methods

**3. `promote_fleeting_note` Split Timeline**
- Week 2 during extraction
- Week 3 during refactoring
- **Recommendation**: Week 2 (part of GREEN phase)

---

## Success Criteria

- [ ] All 59 methods categorized with rationale
- [ ] 4 borderline cases resolved ✅ (DONE)
- [ ] LOC estimates validated ✅ (DONE)
- [ ] Extraction order defined ✅ (DONE)
- [ ] Interface design complete (Wednesday)
- [ ] 30 failing tests written (Friday)
- [ ] Ready for Week 2 GREEN phase

---

**Status**: 🟢 ON TRACK  
**Next Action**: Interface design (Wednesday Oct 8)  
**Blockers**: None
