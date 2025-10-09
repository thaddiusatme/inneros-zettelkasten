# ACTIVE Projects Directory

**Last Updated**: 2025-10-08  
**Purpose**: Current active projects and immediate priorities

---

## 📁 Directory Contents

### **Master Tracking**
1. **`project-todo-v3.md`** - Master TODO list
   - All active tasks and priorities
   - Cross-project task tracking
   - Recently completed systems summary

2. **`daemon-automation-system-current-state-roadmap.md`** - Automation system progress tracker
   - Status: 9 iterations complete, YouTube Handler integrated ✅
   - 170 passing tests, production-ready
   - Next: Iteration 10 (Directory Organization Handler)

### **Architecture & Decisions**
3. **`adr-001-workflow-manager-refactoring.md`** - Architecture Decision Record
   - Status: ✅ IMPLEMENTED (October 2025)
   - Documents WorkflowManager god class → 4 focused managers refactor
   - 52 passing tests, backward-compatible adapter pattern

### **Active Bugs & Solutions**
4. **`bug-empty-video-id-frontmatter-templater-2025-10-08.md`**
   - **Severity**: HIGH - YouTube template doesn't populate video_id in frontmatter
   - **Impact**: Automation fails for template-created YouTube notes
   - **Status**: Documented, needs fix

5. **`youtube-official-api-integration-manifest.md`** - **MIGRATION IN PROGRESS** 🚀
   - **Project**: Replace unofficial scraping with YouTube Data API v3
   - **Status**: Phase 1 COMPLETE (API key validated ✅), Phase 2 ready (TDD implementation)
   - **Deprecation**: Unofficial transcript scraping being removed (hard migration)
   - **Rationale**: Current network 100% rate-limited, quota-based API solves this
   - **Timeline**: ~3.5 hours implementation (TDD Iteration 1)
   - **Breaking Change**: Will require API key for YouTube features going forward

### **Strategic/Future Projects**
6. **`distribution-productionization-manifest.md`** - Distribution planning
   - Vision: Two-repo model (personal + public distribution)
   - Status: Planning complete, implementation pending
   - Timeline: 2-3 weeks when prioritized

---

## 🗂️ File Organization Rules

### **Keep in ACTIVE/**
- ✅ Current priorities document (updated regularly)
- ✅ Projects actively being worked on (this week/month)
- ✅ POC/TDD iteration plans for immediate implementation
- ✅ Strategic manifests that inform current decisions

### **Move to DEPRECATED/**
- Superseded manifests (e.g., older versions replaced by v2)
- Projects determined not to match actual workflow
- Designs that were replaced by better approaches

### **Move to COMPLETED-2025-XX/**
- Finished projects with all objectives met
- Successfully deployed systems
- Lessons learned documents after project completion

### **Move to REFERENCE/**
- Reusable guides and templates
- Process documentation
- Technical specifications that don't change

---

## 📊 Current Project Status (2025-10-08)

| Project | Status | Priority | Timeline |
|---------|--------|----------|----------|
| YouTube Handler (Iteration 9) | ✅ COMPLETE | P0 | Oct 8 |
| **YouTube Official API Migration** | 🚀 **IN PROGRESS** | **P0** | **3.5 hours** |
| Bug: Empty video_id Template | 🐛 Active | HIGH | TBD |
| Directory Org Handler (Iter 10) | 🟡 Next | P1 | After API migration |
| Fleeting Triage Handler (Iter 11) | 🔵 Future | P2 | TBD |
| Distribution/Productionization | 🔵 Planning | Strategic | 2-3 weeks |

---

## 🎯 Next Actions

1. **Oct 8 (IMMEDIATE)**: Complete YouTube Official API v3 Migration (TDD)
   - Phase 2: RED phase (write failing tests for YouTubeOfficialAPIFetcher)
   - Phase 2: GREEN phase (implement captions.download functionality)
   - Phase 2: REFACTOR phase (extract utilities, polish)
   - Phase 2: COMMIT phase (git commit + lessons learned)
2. **Oct 8-9**: Fix bug-empty-video-id-frontmatter-templater (HIGH priority)
3. **Oct 9+**: Plan Iteration 10 - Directory Organization Handler (P1)
4. **Future**: Evaluate Distribution/Productionization timeline
5. **Strategic**: Consider Fleeting Triage Handler (Iteration 11)

---

**Directory Health**: ✅ Clean and organized (85% reduction on Oct 8)  
**Active Files**: 7 core files (down from 39)  
**Status**: YouTube Handler complete, bug fixes needed before next iteration
