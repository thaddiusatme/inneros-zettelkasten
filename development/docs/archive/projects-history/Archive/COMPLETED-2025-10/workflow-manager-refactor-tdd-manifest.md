# WorkflowManager Refactor - TDD Manifest

**Created**: 2025-10-05  
**Status**: 🔴 **PRIORITY 1 - ARCHITECTURAL DEBT**  
**Priority**: CRITICAL (P1 - Main Focus)  
**Type**: Architecture Refactoring + TDD  
**Estimated Effort**: 4 weeks (AI-driven TDD approach)

---

## 🎯 **Mission: Split the God Class**

### **Current State: CRITICAL**
```
File: development/src/ai/workflow_manager.py
Lines: 2,374 (Threshold: 500)
Methods: 59 (Threshold: 10-15)
Test Coupling: 13 test files
Total Imports: 17 files
```

### **Problem**
- **Architectural debt compounding exponentially**
- Every new feature adds to the god class
- TDD gave false confidence (tests check features, not architecture)
- User reported "code smell" for weeks (instinct was correct)

### **Goal**
Split WorkflowManager into 4 focused managers:
1. **CoreWorkflowManager** - Orchestration only (~200 LOC)
2. **AnalyticsManager** - Metrics, reviews, orphans (~400 LOC)
3. **AIEnhancementManager** - Tagging, quality, summarization (~600 LOC)
4. **ConnectionManager** - Links, tags, relationships (~400 LOC)

---

## 📊 **Method Categorization (59 Methods)**

### **Category 1: Core Orchestration** (Move to CoreWorkflowManager)
```python
__init__
_load_config
process_inbox_note
promote_note
batch_process_inbox
_fix_template_placeholders
_preprocess_created_placeholder_in_raw
```
**Target LOC**: ~200-300 lines

### **Category 2: Analytics & Metrics** (Move to AnalyticsManager)
```python
generate_workflow_report
_analyze_ai_usage
_generate_workflow_recommendations
scan_review_candidates
_scan_directory_for_candidates
_create_candidate_dict
generate_weekly_recommendations
_initialize_recommendations_result
_process_candidate_for_recommendation
_create_error_recommendation
_update_summary_counts
_extract_weekly_recommendation
detect_orphaned_notes
detect_orphaned_notes_comprehensive
detect_stale_notes
generate_enhanced_metrics
_list_orphans_by_scope
```
**Target LOC**: ~400-500 lines

### **Category 3: AI Enhancement** (Move to AIEnhancementManager)
```python
# AI tagging, quality scoring, summarization
# (Methods to be identified from remaining 59)
```
**Target LOC**: ~500-700 lines

### **Category 4: Connection & Link Management** (Move to ConnectionManager)
```python
remediate_orphaned_notes
_find_default_link_target
_insert_bidirectional_links
_merge_tags
_load_notes_corpus
_vault_root
```
**Target LOC**: ~300-400 lines

---

## 🏗️ **4-Week TDD Refactoring Plan**

### **Week 1: Architecture Design & RED Phase** (Oct 6-12)

**Monday (Oct 6): Method Audit**
- [ ] Extract all 59 method signatures
- [ ] Categorize into 4 managers
- [ ] Identify shared dependencies
- [ ] Document coupling points

**Tuesday-Wednesday (Oct 7-8): Interface Design**
- [ ] Define `IWorkflowManager` interface
- [ ] Define `IAnalyticsManager` interface  
- [ ] Define `IAIEnhancementManager` interface
- [ ] Define `IConnectionManager` interface
- [ ] Plan dependency injection strategy

**Thursday-Friday (Oct 9-10): TDD RED Phase**
- [ ] Write failing tests for CoreWorkflowManager
- [ ] Write failing tests for AnalyticsManager
- [ ] Write failing tests for AIEnhancementManager
- [ ] Write failing tests for ConnectionManager
- [ ] Document expected test failures (~20-30 tests)

**Deliverable**: Architecture Decision Record + 30 failing tests

---

### **Week 2: TDD GREEN Phase - Extract Managers** (Oct 13-19)

**TDD Iteration 11: CoreWorkflowManager**
- [ ] Create `core_workflow_manager.py`
- [ ] Extract orchestration methods (7 methods)
- [ ] Update imports
- [ ] Run tests → GREEN

**TDD Iteration 12: AnalyticsManager**
- [ ] Create `analytics_manager.py`
- [ ] Extract analytics methods (17 methods)
- [ ] Update imports
- [ ] Run tests → GREEN

**TDD Iteration 13: AIEnhancementManager**
- [ ] Create `ai_enhancement_manager.py`
- [ ] Extract AI methods (~20 methods)
- [ ] Update imports
- [ ] Run tests → GREEN

**TDD Iteration 14: ConnectionManager**
- [ ] Create `connection_manager.py`
- [ ] Extract connection methods (~15 methods)
- [ ] Update imports
- [ ] Run tests → GREEN

**Deliverable**: 4 new manager classes, all new tests passing (30/30)

---

### **Week 3: TDD REFACTOR Phase - Migrate Tests** (Oct 20-26)

**Monday-Tuesday: Test Migration Planning**
- [ ] Audit 13 test files using WorkflowManager
- [ ] Create migration strategy for each file
- [ ] Design mock/fixture patterns

**Wednesday-Friday: Execute Migration**
- [ ] Migrate test_workflow_manager.py (primary)
- [ ] Migrate 12 other test files
- [ ] Update all imports
- [ ] Verify all 759 tests still passing

**Deliverable**: All tests passing with new architecture

---

### **Week 4: Production Integration & Cleanup** (Oct 27 - Nov 2)

**Monday-Wednesday: CLI Integration**
- [ ] Update workflow_demo.py (uses WorkflowManager)
- [ ] Update analytics_demo.py
- [ ] Update all 17 files importing WorkflowManager
- [ ] Verify CLI commands work

**Thursday: Deprecation**
- [ ] Add deprecation warning to old WorkflowManager
- [ ] Create migration guide
- [ ] Update documentation

**Friday: Validation & Deploy**
- [ ] Run full test suite (759 tests)
- [ ] Performance benchmarking
- [ ] Real data validation
- [ ] Commit & lessons learned

**Deliverable**: Production-ready refactored architecture

---

## 🎯 **Success Metrics**

### **Code Quality Targets**
- [ ] Max class size: <500 LOC per manager
- [ ] Max methods: <20 per manager
- [ ] Test coverage: Maintain 77%+ ratio
- [ ] All 759 tests passing
- [ ] Zero regressions

### **Architecture Targets**
- [ ] Separation of concerns achieved
- [ ] Dependency injection working
- [ ] Mock/test isolation improved
- [ ] Plugin architecture foundation laid

### **Performance Targets**
- [ ] No performance degradation
- [ ] Maintain <10s summarization
- [ ] Maintain <5s similarity search
- [ ] Maintain current CLI speeds

---

## 🚨 **Risk Management**

### **Risk 1: Test Coupling**
**Issue**: 13 test files directly instantiate WorkflowManager  
**Mitigation**: Migrate tests incrementally, one file at a time  
**Rollback**: Keep old WorkflowManager until all tests passing

### **Risk 2: Breaking Changes**
**Issue**: 17 files import WorkflowManager  
**Mitigation**: Facade pattern - old API delegates to new managers  
**Rollback**: Revert commits if production breaks

### **Risk 3: Time Overrun**
**Issue**: 4 weeks might not be enough  
**Mitigation**: Weekly checkpoints, adjust scope if needed  
**Rollback**: Phase deployment - complete 1 manager at a time

---

## 📝 **Architecture Decision Record (ADR)**

### **Decision: Split WorkflowManager into 4 Domain Managers**

**Context**:
- Current WorkflowManager is 2,374 lines, 59 methods (god class)
- TDD iterations kept adding to same class (no refactoring trigger)
- User experienced "code smell" but TDD gave false confidence
- Every new feature makes refactoring harder (exponential debt)

**Options Considered**:
1. **Extract utilities** - Insufficient, doesn't address god class
2. **Create facade** - Hides problem, doesn't fix it
3. **Plugin architecture** - Too complex, premature
4. **Split by domain** - ✅ **SELECTED**: Clean separation, testable

**Decision**:
Split into 4 managers by domain:
- CoreWorkflowManager: Orchestration only
- AnalyticsManager: Metrics and reporting
- AIEnhancementManager: AI processing
- ConnectionManager: Links and relationships

**Consequences**:
- ✅ **Pros**: Clean architecture, testable, maintainable
- ✅ **Pros**: Plugin architecture foundation
- ✅ **Pros**: Easier to add features without coupling
- ❌ **Cons**: 4 weeks refactoring time
- ❌ **Cons**: 13 test files need migration
- ❌ **Cons**: Temporary complexity during migration

**Implementation**:
- AI-driven TDD approach (user's preferred method)
- Incremental migration (maintain green tests throughout)
- Deprecation period (keep old API working via facade)

---

## 🎓 **Lessons Learned (Pre-mortem)**

### **Why TDD Didn't Catch This**
1. **Tests checked features, not architecture**
2. **No architectural guardrails** (max class size linting)
3. **No refactoring trigger defined** (when to split?)
4. **"Just add another method" culture**

### **What Should Have Happened**
1. **Refactoring trigger at 500 LOC or 15 methods**
2. **Architectural reviews in lessons learned**
3. **Class size tests** (fail if >500 LOC)
4. **Interface-based testing** (not concrete classes)

### **What We'll Do Differently**
1. **Add class size linting** to CI/CD
2. **Architectural reviews** in all future iterations
3. **Interface-first design** for new features
4. **Refactoring as part of TDD** (not just feature completion)

---

## 📋 **Immediate Next Steps**

### **Today (Oct 5)**
- [x] Create this manifest
- [ ] Commit manifest to git
- [ ] Extract all 59 method signatures
- [ ] Begin method categorization
- [ ] Share categorization for review

### **Monday (Oct 6)**
- [ ] Complete method categorization
- [ ] Design 4 manager interfaces
- [ ] Start RED phase (write failing tests)

### **End of Week 1 (Oct 12)**
- [ ] 30 failing tests written
- [ ] Architecture Decision Record complete
- [ ] Ready for GREEN phase

---

## 🔗 **Related Documents**

- **Technical Health Assessment**: `Projects/REFERENCE/technical-health-assessment-oct-2025.md`
- **Team Feedback**: (Incorporated into this manifest)
- **Project TODO**: `Projects/ACTIVE/project-todo-v3.md` (update with P1 priority)
- **TDD Lessons Learned**: `Projects/COMPLETED-2025-10/` (28+ previous iterations)

---

## 🎯 **Commitment**

**This is now Priority 1** (after confirming image bug already fixed).

**Why**:
- User's architectural instinct was correct ("code smell")
- Team feedback confirmed critical issue
- Exponential debt if delayed
- Daemon/features blocked until this is fixed

**Timeline**: 4 weeks (Oct 6 - Nov 2, 2025)  
**Owner**: Development Team  
**Blocker**: All new features until refactor complete  
**Go/No-Go**: Weekly checkpoint every Friday

---

**Document Status**: ✅ Planning Complete - Ready for Execution  
**Next Action**: Method categorization (complete list of 59 methods)  
**Target Start**: Monday, October 6, 2025  
**Risk Level**: Medium (incremental approach reduces risk)
