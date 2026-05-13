# Projects/ACTIVE Cleanup Plan - 2025-10-12

**Current State**: 52 files (overwhelming cognitive load)  
**Goal**: Reduce to <15 truly active files  
**Strategy**: Move completed work to COMPLETED-2025-10/

---

## 📊 Current Inventory Analysis

### ✅ COMPLETED - Move to COMPLETED-2025-10/ (29 files)

#### ADR-004 CLI Extraction (COMPLETE Oct 11)
- [ ] adr-004-cli-layer-extraction.md (keep main ADR in ACTIVE)
- [x] adr-004-iteration-1-weekly-review-lessons-learned.md
- [x] adr-004-iteration-2-fleeting-lessons-learned.md
- [x] adr-004-iteration-3-safe-workflow-lessons-learned.md
- [x] adr-004-iteration-4-core-workflow-lessons-learned.md
- [x] adr-004-iteration-4-discovery-analysis.md
- [x] adr-004-iteration-5-final-commands-plan.md
- [x] adr-004-iteration-5-final-lessons-learned.md

#### Quality Audit (COMPLETE Oct 12)
- [x] audit-report-2025-10-10.md
- [x] AUDIT-SESSION-SUMMARY-2025-10-10.md
- [x] AUDIT-QUICK-START.md
- [x] quality-audit-manifest.md
- [x] quality-audit-bug-remediation-lessons-learned-2025-10-12.md
- [x] bug-fix-execution-plan-2025-10-10.md

#### Bug Reports (Move ALL to COMPLETED - Fixed Oct 12)
- [x] bug-connections-import-error-2025-10-10.md
- [x] bug-enhanced-metrics-keyerror-2025-10-10.md
- [x] bug-fleeting-health-attributeerror-2025-10-10.md
- [x] bug-orphaned-notes-keyerror-2025-10-10.md
- [x] bug-youtube-processing-failures-2025-10-10.md
- [x] bug-empty-video-id-frontmatter-templater-2025-10-08.md
- [x] bug-youtube-api-rate-limiting-2025-10-08.md

#### YouTube Rate Limit Incident (RESOLVED Oct 8-9)
- [x] youtube-rate-limit-investigation-2025-10-08.md
- [x] youtube-rate-limit-mitigation-tdd-manifest.md
- [x] catastrophic-incident-fix-2025-10-08.md

#### Workflow Dashboard Iterations (COMPLETE)
- [x] workflow-dashboard-iteration-1-lessons-learned.md
- [x] workflow-dashboard-iteration-1-testing-summary.md
- [x] workflow-dashboard-iteration-2-lessons-learned.md

#### Workflow Demo Deprecation (COMPLETE Oct 11)
- [x] workflow-demo-deprecation-plan.md
- [x] workflow-demo-phase1-audit-complete.md
- [x] workflow-demo-phase2-docs-complete.md
- [x] workflow-demo-phase3-internal-docs-complete.md

---

### 🏗️ KEEP IN ACTIVE (15 files)

#### Current Sprint (Week 1, Day 3)
- [ ] **testing-infrastructure-revamp-manifest.md** ← ACTIVE NOW
- [ ] **project-todo-v3.md** ← Master todo list
- [ ] **slow-tests-analysis.md** ← Testing context

#### Architectural Documents (Keep for Reference)
- [ ] **adr-001-workflow-manager-refactoring.md** ← Foundation ADR
- [ ] **adr-002-circuit-breaker-rate-limit-protection.md** ← P1 backlog
- [ ] **adr-003-distribution-architecture.md** ← Reference
- [ ] **adr-004-cli-layer-extraction.md** ← Main ADR (keep)

#### P1 Backlog Projects
- [ ] **circuit-breaker-rate-limit-protection-manifest.md**
- [ ] **daemon-automation-system-current-state-roadmap.md**
- [ ] **retro-tui-design-manifest.md**

#### Distribution System (Status: Uncertain)
- [ ] **distribution-system-tdd-iteration-1-lessons-learned.md** (move?)
- [ ] **distribution-documentation-complete.md** (move?)
- [ ] **distribution-productionization-manifest.md** (keep?)
- [ ] **distribution-release-checklist.md** (keep?)
- [ ] **DISTRIBUTION-SYSTEM-SUMMARY.md** (move?)

#### Context/Status Documents
- [ ] **PROJECT-STATUS-UPDATE-2025-10-12.md** ← Recent status
- [ ] **PRODUCT-VISION-UPDATE-2025-10-09.md** ← Strategy
- [ ] **CONTEXT-UPDATE-RECOMMENDATIONS-2025-10-12.md** ← Recent
- [ ] **CURRENT-STATE-2025-10-08.md** ← Move to archive?
- [ ] **streaming-demo-workflow.md** ← Validation strategy

#### Guides/Reference
- [ ] **directory-context-guide.md** ← Reference
- [ ] **design-flaw-audit-framework.md** ← Reference
- [ ] **README-ACTIVE.md** ← Directory readme

#### Subdirectory
- [ ] **workflow-diagrams/** (10 items) ← Keep for now

---

### ❓ ARCHIVE - Move to Archive/ (Status docs >30 days old)
- [x] CURRENT-STATE-2025-10-08.md (4 days old, superseded)

---

## 🎯 Cleanup Actions

### Phase 1: Move Completed Work (29 files → COMPLETED-2025-10/)
```bash
cd Projects/ACTIVE

# ADR-004 Iterations
mv adr-004-iteration-*.md ../COMPLETED-2025-10/

# Quality Audit
mv audit-*.md ../COMPLETED-2025-10/
mv quality-audit-*.md ../COMPLETED-2025-10/
mv bug-*.md ../COMPLETED-2025-10/

# YouTube Incident
mv youtube-rate-limit-*.md ../COMPLETED-2025-10/
mv catastrophic-incident-fix-2025-10-08.md ../COMPLETED-2025-10/

# Workflow Dashboard
mv workflow-dashboard-*.md ../COMPLETED-2025-10/

# Workflow Demo Deprecation
mv workflow-demo-*.md ../COMPLETED-2025-10/
```

### Phase 2: Distribution System Decision
**Review**: Check if distribution system complete or still active
- If complete → Move 5 distribution files to COMPLETED-2025-10/
- If active → Keep productionization-manifest and release-checklist

### Phase 3: Archive Old Status Docs
```bash
mv CURRENT-STATE-2025-10-08.md ../Archive/
```

### Phase 4: Final Result
**Target**: 10-15 files in ACTIVE (vs current 52)
- Current sprint manifest (testing)
- Master todo (project-todo-v3.md)
- 4 ADRs (architectural reference)
- 3 P1 backlog manifests
- 3-4 recent status/context docs
- Reference guides (2-3 files)

---

## 📊 Impact

**Before**: 52 files (overwhelming)  
**After**: ~12 files (manageable)  
**Moved**: 29-34 files to COMPLETED-2025-10/  
**Archived**: 1 file to Archive/

**Cognitive Load Reduction**: 77% (52 → 12 files)

---

**Status**: Ready to execute  
**Duration**: 5 minutes (git mv commands)  
**Risk**: Low (just moving files, preserving git history)
