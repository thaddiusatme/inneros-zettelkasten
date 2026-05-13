---
type: project-manifest
created: 2025-10-14 22:45
status: planned
priority: P2
tags: [architecture, refactoring, organization, developer-experience, maintainability]
---

# Source Code Reorganization Project

**Status**: 📋 **PLANNED** - Medium/Low Priority  
**Priority**: P2 - Developer experience & maintainability  
**Timeline**: 4-6 weeks (gradual migration)  
**Effort**: ~20 hours spread over multiple sessions  
**Risk**: LOW - Python imports easily refactorable, strong test coverage

---

## 🎯 Problem Statement

### Current State (October 2025)

**Codebase has grown organically without organizational structure:**
- `src/ai/` - **56 Python files** 🔴 CRITICAL (impossible to navigate)
- `src/cli/` - **44 Python files** 🔴 CRITICAL (cognitive overload)
- `src/automation/` - 19 files ✅ Acceptable
- `src/utils/` - 11 files ✅ Good

**Developer Pain Points:**
- 20+ minutes to find related code
- No clear ownership of features
- 15+ `_utils.py` files scattered randomly
- Difficult onboarding for new contributors
- Can't tell what code does what at a glance

**Impact:**
- Slows feature development
- Increases bug introduction risk
- Makes code reviews harder
- Blocks external contributors

### What Success Looks Like

**After reorganization:**
- <2 minutes to find related code (90% reduction)
- Clear domain ownership
- 70% reduction in "where does this belong?" decisions
- Logical package structure visible at directory level
- Easy navigation for new developers

---

## 📊 80/20 Analysis Results

### High-Impact Changes (80% Value)

#### #1: Split Monolithic `ai/` Directory (40% of value)
**Create domain-driven subpackages:**
```
src/ai/
├── core/              # Core workflow (8 files)
│   ├── workflow_manager.py
│   ├── core_workflow_manager.py
│   ├── auto_processor.py
│   └── note_lifecycle_manager.py
│
├── connections/       # Link management (12 files)
│   ├── connections.py
│   ├── connection_manager.py
│   ├── link_suggestion_engine.py
│   └── link_insertion_engine.py
│
├── tags/              # Tag enhancement (10 files)
│   ├── advanced_tag_enhancement.py
│   ├── ai_tagging_prevention.py
│   └── rag_ready_tag_engine.py
│
├── enhancement/       # Content quality (6 files)
│   ├── enhancer.py
│   ├── real_content_quality_analyzer.py
│   └── summarizer.py
│
├── analytics/         # Metrics & reporting (4 files)
│   ├── analytics.py
│   └── analytics_coordinator.py
│
├── media/             # OCR & images (8 files)
│   ├── llama_vision_ocr.py
│   ├── safe_image_processor.py
│   └── image_integrity_monitor.py
│
└── imports/           # Import & schema (2 files)
    ├── import_manager.py
    └── import_schema.py
```

**Impact**: 56 files → 7 domains with 2-12 files each

#### #2: Split Oversized `cli/` Directory (30% of value)
**Create feature-based subpackages:**
```
src/cli/
├── core/              # Main entry points (3 files)
│   ├── workflow_demo.py
│   ├── interactive_cli.py
│   └── ai_assistant.py
│
├── screenshots/       # Screenshot processing (8 files)
│   ├── screenshot_processor.py
│   └── screenshot_cli_utils.py
│
├── connections/       # Link CLIs (3 files)
│   ├── connections_demo.py
│   └── smart_link_cli_enhanced.py
│
├── tags/              # Tag management (2 files)
│   └── advanced_tag_enhancement_cli.py
│
├── workflows/         # Workflow management (6 files)
│   ├── fleeting_cli.py
│   ├── weekly_review_cli.py
│   └── safe_workflow_cli.py
│
├── monitoring/        # Dashboards & metrics (8 files)
│   ├── terminal_dashboard.py
│   └── performance_metrics_collector.py
│
└── media/             # Media processing (4 files)
    ├── youtube_cli.py
    └── backup_cli.py
```

**Impact**: 44 files → 7 features with 2-8 files each

#### #3: Extract Utilities to Shared Modules (20% of value)
**Pattern for all domains:**
```
src/ai/connections/
├── engine.py          # Core logic
├── coordinator.py
└── utils/             # Utilities subpackage
    ├── suggestion_utils.py
    ├── insertion_utils.py
    └── integration_utils.py
```

**Impact**: Clear separation of core logic vs helpers

#### #4: Create `src/models/` Package (10% of value)
**Extract shared data structures:**
```
src/models/
├── __init__.py
├── note.py            # Note data structures
├── connection.py      # Connection models
├── tag.py             # Tag models
└── schemas.py         # Import schemas
```

**Impact**: Single source of truth for data models

---

## 📋 User Stories & Implementation Plan

### US-1: Domain Organization for AI Package (Week 1-2)
**As a developer**, I want AI features organized by domain so I can find related code quickly.

**Acceptance Criteria:**
- [ ] Create 7 subpackages under `src/ai/`
- [ ] Move files to appropriate domains
- [ ] Create `__init__.py` with re-exports
- [ ] Update all import statements
- [ ] All tests pass (66/66 baseline maintained)
- [ ] Documentation updated

**Tasks:**
1. Create directory structure (30 min)
2. Move `connections/` files (12 files, 2 hours)
3. Move `tags/` files (10 files, 2 hours)
4. Move `core/` files (8 files, 1 hour)
5. Move `enhancement/` files (6 files, 1 hour)
6. Move `analytics/` files (4 files, 1 hour)
7. Move `media/` files (8 files, 1 hour)
8. Move `imports/` files (2 files, 30 min)
9. Update imports throughout codebase (2 hours)
10. Run test suite + fix any issues (1 hour)

**Estimated Effort**: 12 hours

### US-2: Feature Organization for CLI Package (Week 3-4)
**As a developer**, I want CLI commands organized by feature so I can understand the user-facing interface.

**Acceptance Criteria:**
- [ ] Create 7 subpackages under `src/cli/`
- [ ] Move files to appropriate features
- [ ] Create `__init__.py` with re-exports
- [ ] Update all import statements
- [ ] All tests pass
- [ ] CLI commands work identically

**Tasks:**
1. Create directory structure (30 min)
2. Move `core/` files (3 files, 1 hour)
3. Move `screenshots/` files (8 files, 1.5 hours)
4. Move `connections/` files (3 files, 1 hour)
5. Move `tags/` files (2 files, 30 min)
6. Move `workflows/` files (6 files, 1.5 hours)
7. Move `monitoring/` files (8 files, 1.5 hours)
8. Move `media/` files (4 files, 1 hour)
9. Update imports (1.5 hours)
10. Integration testing (1 hour)

**Estimated Effort**: 10 hours

### US-3: Utility Module Consolidation (Week 5)
**As a developer**, I want utilities grouped with their primary modules so I can find helpers easily.

**Acceptance Criteria:**
- [ ] Create `utils/` subdirectories in domains with >3 utils
- [ ] Move `_utils.py` files to appropriate locations
- [ ] Update import paths
- [ ] All tests pass
- [ ] Utilities discoverable within their domains

**Tasks:**
1. Audit all `_utils.py` files (1 hour)
2. Create `utils/` subdirectories (30 min)
3. Move and rename utility files (2 hours)
4. Update imports (1.5 hours)
5. Testing (1 hour)

**Estimated Effort**: 6 hours

### US-4: Shared Models Package (Week 6)
**As a developer**, I want a single location for data models so I can maintain consistency.

**Acceptance Criteria:**
- [ ] Create `src/models/` package
- [ ] Extract `import_schema.py` to models
- [ ] Create `note.py`, `connection.py`, `tag.py` models
- [ ] Update imports to use models package
- [ ] All tests pass
- [ ] Documentation shows model relationships

**Tasks:**
1. Create `models/` package structure (30 min)
2. Extract and refactor data models (2 hours)
3. Update imports (1 hour)
4. Testing (30 min)
5. Documentation (1 hour)

**Estimated Effort**: 5 hours

---

## 🎯 Quick Wins (Start Here)

### Week 1: Proof of Concept
**Goal**: Validate approach with smallest high-value domain

**Phase 1A: Extract `ai/connections/` (2 hours)**
- Create `src/ai/connections/` directory
- Move 12 connection-related files
- Update imports in tests
- Validate all tests pass

**Success Metric**: 56 → 44 files in `ai/` (21% reduction)

**Phase 1B: Extract `ai/tags/` (2 hours)**
- Create `src/ai/tags/` directory
- Move 10 tag-related files
- Update imports
- Validate tests

**Success Metric**: 44 → 34 files in `ai/` (39% cumulative reduction)

**Validation Point**: If successful, continue with full plan. If issues, reassess.

---

## ⚠️ Risk Mitigation

### Critical Risk Identified: Test Import Breakage

**Discovery**: 310 import statements across 64 test files will break when modules move.

**Impact**: Without mitigation, all tests fail immediately after file moves.

### Low-Risk Indicators ✅
- Python imports are easily refactorable
- Strong test coverage (66/66 tests baseline)
- Can migrate one domain at a time
- Facade pattern prevents breaking changes
- IDE refactoring tools available

### Mitigation Strategies

**1. Import Facades (RECOMMENDED - Zero Test Breakage)**

Create `__init__.py` facades that re-export from new locations:

```python
# src/ai/__init__.py (after moving to subpackages)
"""Import facade for backward compatibility."""
from src.ai.core.workflow_manager import WorkflowManager
from src.ai.connections.connection_manager import ConnectionManager
# ... all moved classes

__all__ = ['WorkflowManager', 'ConnectionManager', ...]
```

**Benefits**:
- **Zero test breakage** - old imports continue working
- Tests pass throughout reorganization
- Gradual deprecation over 2-3 releases
- Easy rollback at any point

**Implementation**:
- Create facades when moving files (5 min per domain)
- Add deprecation warnings in Phase 5
- Update imports at leisure after completion

**2. Automated Import Rewriting (Alternative)**

Use Python tooling (bowler, rope) to rewrite all imports automatically:

```bash
# Rewrite all test imports in one pass
bowler do src.ai.workflow_manager src.ai.core.workflow_manager \
  development/tests/**/*.py
```

**Benefits**:
- Clean break, no technical debt
- Single commit with all changes
- Complete in minutes

**Risks**:
- Requires extensive validation
- Difficult to rollback
- All-or-nothing approach

**3. Incremental Domain Migration (Conservative)**

Update test imports for each domain during migration:

- Week 1: Move `connections/` + update 10 test files
- Week 2: Move `tags/` + update 8 test files
- Validate 100% test pass after each domain

**Benefits**:
- Spreads risk across sprints
- Easy per-domain rollback
- Clear validation points

**Risks**:
- Higher total time investment
- Mixed old/new structure temporarily

### Testing Strategy

**With Facades (Recommended)**:
- Run full test suite after each domain move
- Tests pass with zero modifications
- Add deprecation warnings in final phase
- Update imports gradually in new code

**With Rewriting**:
- Run pytest after automated rewrite
- Fix any edge cases manually
- Validate CLI commands
- Check coverage reports

**With Incremental**:
- Update imports for moved domain only
- Run full test suite (not just unit)
- Git commit after each validation
- Monitor for import errors in CI

### Documentation Updates
- Update imports in all docs simultaneously
- Keep architecture decision record
- Document migration for contributors
- Add deprecation notices to facades

---

## 📊 Success Metrics

### Before Reorganization
- Files in `ai/`: 56 (unmanageable)
- Files in `cli/`: 44 (unmanageable)
- Time to find code: 20+ minutes
- Developer frustration: High
- New contributor onboarding: Difficult

### After Reorganization (Target)
- Max files per directory: <12 (manageable)
- Domains/features: 7 each (clear organization)
- Time to find code: <2 minutes (90% reduction)
- Developer frustration: Low
- New contributor onboarding: Easy

### Progress Tracking
- [ ] `ai/connections/` extracted (12 files)
- [ ] `ai/tags/` extracted (10 files)
- [ ] `ai/core/` extracted (8 files)
- [ ] `ai/enhancement/` extracted (6 files)
- [ ] `ai/analytics/` extracted (4 files)
- [ ] `ai/media/` extracted (8 files)
- [ ] `ai/imports/` extracted (2 files)
- [ ] `cli/` reorganized (44 files → 7 features)
- [ ] Utilities consolidated (15+ files organized)
- [ ] Models package created

---

## 🔄 Implementation Strategy

### Phase 1: Proof of Concept (Week 1)
**Goal**: Validate approach, build confidence
- Extract 2 smallest domains (`connections/`, `tags/`)
- Update tests and validate
- Document lessons learned
- Go/No-Go decision point

### Phase 2: AI Package Completion (Week 2)
**Goal**: Complete `ai/` reorganization
- Extract remaining 5 domains
- Update all imports
- Full test validation
- Documentation updates

### Phase 3: CLI Package (Week 3-4)
**Goal**: Reorganize `cli/` by features
- Create 7 feature packages
- Move 44 files systematically
- Test all CLI commands
- Update user documentation

### Phase 4: Utilities & Models (Week 5-6)
**Goal**: Final polish and shared packages
- Consolidate utilities
- Create models package
- Final testing and validation
- Complete documentation

### Phase 5: Cleanup & Documentation (Week 6)
**Goal**: Polish and communicate
- Remove deprecated imports
- Update architecture docs
- Create migration guide
- Lessons learned document

---

## 📚 Dependencies & Blockers

### Prerequisites
- ✅ Strong test coverage exists (66/66 baseline)
- ✅ Git version control in place
- ✅ TDD methodology established
- ✅ Understanding of codebase structure

### No Blockers
- Can start immediately
- No dependencies on other projects
- Low risk to ongoing work
- Can pause/resume anytime

### Recommended Timing
**Best Time**: During maintenance sprint or between features
- Not during active feature development
- After major releases stabilize
- When team bandwidth available
- When code churn is low

**Avoid During**:
- Active sprint with tight deadlines
- Major feature releases
- External demos/presentations
- Critical bug fix periods

---

## 🎓 Expected Outcomes

### Technical Benefits
- **Navigability**: 90% faster code discovery
- **Maintainability**: Clear ownership and boundaries
- **Testability**: Easier to test isolated domains
- **Scalability**: Structure supports growth
- **Documentation**: Self-documenting organization

### Team Benefits
- **Onboarding**: New developers productive faster
- **Reviews**: Code reviews more focused
- **Collaboration**: Clear feature ownership
- **Quality**: Easier to spot architectural issues
- **Velocity**: Less time navigating, more building

### Future Proofing
- Supports Phase 6+ expansion
- Enables external contributors
- Facilitates plugin architecture
- Prepares for potential multi-repo split
- Foundation for eventual microservices

---

## 📖 References

### Architectural Context
- **Constraints**: `.windsurf/rules/architectural-constraints.md`
- **ADR-002**: NoteLifecycleManager extraction pattern
- **ADR-004**: CLI Layer Extraction (completed Oct 2025)

### Similar Successful Refactorings
- CLI Layer Extraction: 2,074 LOC → 10 focused CLIs
- WorkflowManager Decomposition: Pattern proven (ADR-002)
- NoteLifecycleManager: 222 LOC, clean extraction

### Lessons from Past Refactorings
1. Start small with proof-of-concept
2. Test coverage is critical for confidence
3. One domain at a time prevents overwhelm
4. Commit frequently for easy rollback
5. Documentation updates are essential

---

## 📝 Next Steps

### Immediate (When Prioritized)
1. **Review & Approve**: Team reviews this manifest
2. **Schedule Time**: Block 2-3 weeks on calendar
3. **Create Branch**: `refactor/source-code-reorganization`
4. **Start POC**: Extract `ai/connections/` first

### Week 1 Actions
- [ ] Extract `ai/connections/` (2 hours)
- [ ] Extract `ai/tags/` (2 hours)
- [ ] Validate tests pass
- [ ] Document lessons
- [ ] Go/No-Go decision

### Success Checkpoint
If Week 1 POC successful → Continue with full plan
If issues arise → Reassess approach, possibly smaller scope

---

**Version**: 1.0  
**Last Updated**: 2025-10-14  
**Next Review**: After Week 1 POC completion
