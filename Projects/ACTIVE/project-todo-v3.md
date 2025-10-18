---
type: project-manifest
created: 2025-10-12 17:59
updated: 2025-10-13 08:25
status: active
priority: P0
tags: [note-lifecycle, status-management, workflow-automation, directory-integration, tdd]
---

# InnerOS Zettelkasten - Project Todo v3.0

**Last Updated**: 2025-10-17 22:56 PDT  
**Status**: 🚧 **ACTIVE PLANNING** - YouTube Automation Projects Added  
**Reference**: `Projects/inneros-manifest-v3.md` for comprehensive context  
**Latest**: YouTube API Trigger System & Transcript Archival manifests complete

---

## 🎯 Product Vision & Validation Strategy

**Last Updated**: 2025-10-10 (Added streaming validation manifest)  
**Manifest**: `Projects/ACTIVE/streaming-validation-manifest.md` ✅

### **Core Purpose**
**Primary**: Personal knowledge management tool that fills gaps in existing solutions (Obsidian, etc.)
- Built for developer workflow (CLI-first, local files, powerful automation)
- Solves real friction points in note-taking process
- Local-first, markdown-based, privacy-preserving

### **Validation Approach: Streaming + Organic Discovery**
**Strategy**: Demonstrate tool naturally during live streams
- Use InnerOS authentically while streaming development work
- Show AI workflows processing notes in real-time
- Let viewers discover organically ("What's that tool you're using?")
- GitHub link in stream description for interested developers
- **Complete Strategy**: See `streaming-validation-manifest.md`

### **Target User (Phase 1)**
**Developer Power Users**:
- Comfortable with CLI/terminal tools
- Value local markdown files and data ownership
- Want AI-enhanced workflows without SaaS subscriptions
- Technical enough for 15-minute installation

### **NOT Building (Explicitly Ruled Out)**
❌ Web application (Notion-like, browser-based)
❌ Cloud database storage (PostgreSQL on Railway)
❌ Mass-market consumer product
❌ Multi-user SaaS platform (Phase 1)

### **Success Metrics**
- Personal workflow friction eliminated (primary goal)
- Organic GitHub stars/clones after streams
- "What tool was that?" questions in chat
- Small community of power users (5-10 users)
- Dogfooding: Daily use without friction

### **Future Pivot Points** (Only if validated)
- **If demand proven**: Consider web version for non-technical users
- **If community grows**: Multi-user collaboration features
- **If monetization needed**: Premium AI features or hosting
- **Current Phase**: Focus on personal use + developer distribution

---

## 🏗️ Architectural Health Tracking

**Last Review**: 2025-10-05  
**Next Review**: 2025-11-04 (First Monday of November)

### Current Architectural Concerns

⚠️ **1 ACTIVE VIOLATION** - WorkflowManager exceeds architectural thresholds

**Current State:**
- ❌ **WorkflowManager**: 2,420 LOC (484% over 500 LOC limit), 59 methods (295% over 20 method limit)
  - Status: Active god class requiring decomposition
  - Pattern established: NoteLifecycleManager extraction (ADR-002, Oct 14, 2025)
  - Plan: P1 project scheduled post-sprint (Nov 2025)
  - Target: Extract ConnectionManager, AnalyticsCoordinator, PromotionEngine

**Recent Victory:**
- ✅ **NoteLifecycleManager**: Extracted from WorkflowManager (ADR-002, Oct 14, 2025)
  - Single responsibility: Status lifecycle management
  - 222 LOC, 4 methods (well under limits)
  - 16/16 tests passing, zero regressions
  - Proves extraction pattern works

### Refactoring Queue

**P1 - WorkflowManager Decomposition** (Planned - Post Sprint):
- ConnectionManager extraction (~300 LOC)
- AnalyticsCoordinator extraction (~400 LOC)
- PromotionEngine extraction (~200 LOC)
- WorkflowManagerAdapter for migration
- Timeline: 3-4 sprints (12-16 hours)
- Target: End of November 2025

### Architectural Guardrails Status

- [ ] Class size linting enabled (Future: Pre-commit hooks)
- [ ] Method count linting enabled (Future: Pre-commit hooks)
- [x] Architectural constraints documented (`.windsurf/rules/architectural-constraints.md`)
- [x] TDD methodology updated with architectural checks
- [ ] Monthly reviews scheduled (Next: Nov 4, 2025)
- [x] ADR template created (`Projects/TEMPLATES/adr-template.md`)
- [x] Architectural review template created (`Projects/TEMPLATES/architectural-review-template.md`)

### Success Metrics

- **Current Classes >500 LOC**: **1** ⚠️ (WorkflowManager: 2,420 LOC)
  - NoteLifecycleManager extracted Oct 14, 2025 (pattern proven)
  - Decomposition plan: Nov 2025 (3 more extractions)
- **Current Classes >20 methods**: **1** ⚠️ (WorkflowManager: 59 methods)
- **CLI Monoliths >2000 LOC**: **0** ✅ (workflow_demo.py extracted Oct 11, 2025!)
- **Dedicated CLIs**: **10** (avg 400 LOC each)
- **Target**: Zero classes exceeding limits by Nov 30, 2025
- **Progress**: 1 extraction complete (NoteLifecycleManager), 3 planned
- **ADRs Created**: 2 (ADR-002: NoteLifecycleManager ✅ COMPLETE Oct 14, 2025, ADR-003: WorkflowManager Decomposition 📋 PLANNED)

---

## CI/CD & DevOps Plan (Oct 13, 2025)

- **P0 PR CI (today)**: Add `.github/workflows/ci.yml` running ruff, black, isort, pyright, and fast `pytest` with coverage on `ubuntu-latest` and `macos-latest` (Python 3.11). Configure tests to use fast-mode/dry-run to avoid network/AI calls.
- **P0 Security Automation**: Add `.github/workflows/codeql.yml` (CodeQL), `.github/dependabot.yml` (weekly pip updates), and add `pip-audit` to CI to fail on high-severity vulnerabilities.
- **P1 Nightly Jobs**: Add `.github/workflows/nightly.yml` to run heavy/integration tests, a link-integrity scan for `[[wiki-links]]`, and a performance smoke test with regression thresholds.
- **P1 Developer Hygiene**: Add `.pre-commit-config.yaml` (ruff, black, isort, pyupgrade, yamllint, markdownlint, EOF/trailing whitespace) and enable branch protection rules requiring CI checks to pass before merge.
- **P2 Release Automation (optional)**: Tag-driven release workflow to build artifacts and generate GitHub Releases with notes.

These guardrails will catch lifecycle regressions (like `status: inbox` not transitioning), protect link integrity during promotions, and maintain performance as the codebase evolves.

---

## ✅ Recently Completed (Oct 2025)

**Full Archive**: `Projects/COMPLETED-2025-10/major-completions-oct-2025.md`  
**Total**: 14 major projects completed September-October 2025

### Most Recent Completions

#### ✅ System Observability Phase 1: Status Command (Oct 15, 2025)
- **Duration**: 2 hours (RED: 30min, GREEN: 60min, REFACTOR: 30min)
- **Status**: 🎉 **COMPLETE** - TDD Iteration 1 (8/8 tests, 576 LOC)
- **Release**: v2.2.0-status-command ✅
- **Deliverables**:
  - ✅ `inneros status` command with daemon/cron/activity/inbox detection
  - ✅ 209 LOC main file (status_cli.py) - ADR-001 compliant
  - ✅ 367 LOC utilities (5 reusable classes)
  - ✅ Beautiful emoji-enhanced terminal output (🟢/🔴/⚠️)
  - ✅ <5 second performance target (estimated ~3-4s)
- **User Impact**: Solved critical usability gap - zero visibility → complete system status
- **Next**: Phase 2 Dashboard Launcher (dashboard wrapper + live terminal UI)
- **Lessons**: `Projects/ACTIVE/system-observability-phase1-lessons-learned.md` ✅

#### ✅ Testing Infrastructure Revamp (Oct 12-16, 2025)
- **300x faster** integration tests (5-10min → 1.35s)
- 6 TDD iterations, 88 tests, production-safe smoke test infrastructure
- **Summary**: `Projects/COMPLETED-2025-10/testing-infrastructure-week1-2-final-summary.md`

#### ✅ ADR-004 CLI Layer Extraction (Oct 10-11, 2025)

**ARCHITECTURAL VICTORY** - 2-week sprint completed in 2 days (4.7x faster)!

- **Duration**: 8.5 hours over 2 days (vs 40 hours estimated)
- **Status**: 🎉 **100% COMPLETE** (25/25 commands extracted)
- **Efficiency**: 4.7x faster than estimated
- **Deliverables**:
  - ✅ 10 Dedicated CLIs (weekly_review_cli.py, fleeting_cli.py, safe_workflow_cli.py, core_workflow_cli.py, backup_cli.py, interactive_cli.py, + 4 pre-existing)
  - ✅ Eliminated 2,074 LOC monolith (workflow_demo.py)
  - ✅ 100% test coverage (all CLI tests passing)
  - ✅ Bug #3 fixed (fleeting-health AttributeError) during Iteration 2
  - ✅ Clean architecture: CLI ← Manager ← Utilities
- **5 Iterations Completed**:
  1. Iteration 1 (Oct 10): Weekly Review CLI - 2 commands, 1.5 hours
  2. Iteration 2 (Oct 10): Fleeting Notes CLI + Bug #3 fix - 3 commands, 2.0 hours
  3. Iteration 3 (Oct 10): Safe Workflow CLI - 6 commands, 1.0 hour (wrapping pattern)
  4. Iteration 4 (Oct 11): Core Workflow CLI - 4 commands, 2.5 hours
  5. Iteration 5 (Oct 11): Final commands - 3 commands, 1.0 hour
- **Key Lessons**:
  - Discovery phase saved 20+ hours (found 7 remaining, not 25)
  - Wrapping utilities 3.3x faster (0.17 vs 0.67 hrs/cmd)
  - TDD methodology delivered zero regressions
  - Velocity tracking enabled accurate re-planning
- 10 Dedicated CLIs extracted from monolithic workflow_demo.py
- **ADR**: `Projects/ACTIVE/adr-004-cli-layer-extraction.md` ✅

**See full archive for 12 additional completions** (WorkflowManager, YouTube, Screenshots, etc.)

---

## 🎯 Active Projects (ARCHITECTURAL PIVOT)

*Note: WorkflowManager Refactor, Image Linking System, and YouTube Handler Integration all COMPLETE (Oct 2025)*

### 🔴 P0 NEW: YouTube API Trigger System (Oct 17, 2025)

**Status**: 🟡 **PLANNING** - Manifest complete, ready for implementation  
**Priority**: P0 - **ENABLES API-FIRST YOUTUBE WORKFLOW**  
**Timeline**: 4.5 hours (2h API, 1h Templater, 1h Dashboard, 0.5h Testing)  
**Branch**: `feat/youtube-api-trigger-system` (to be created)  
**Manifest**: `Projects/ACTIVE/youtube-api-trigger-system-manifest.md` ✅  
**Parent Epic**: YouTube Processing Automation

#### Vision

Transform YouTube note processing from file-watcher-based to **API-first architecture** enabling:
- Templater-triggered automatic processing on note creation
- External tool integration (mobile apps, browser extensions, webhooks)
- Real-time dashboard monitoring of processing queue
- Foundation for future API-driven features

#### Key Components

**Phase 1: API Foundation** (2 hours)
- Create `youtube_api.py` with REST endpoints
- POST `/api/youtube/process` - Trigger processing for specific note
- GET `/api/youtube/queue` - Get processing queue status
- Wire into existing `http_server.py` Flask app
- Update daemon config with `http_server` section

**Phase 2: Templater Integration** (1 hour)
- Create `.obsidian/scripts/trigger_youtube_processing.js`
- Update YouTube template with automatic hook
- Test template → API call flow
- Error handling for offline daemon

**Phase 3: Dashboard Enhancement** (1 hour)
- Add queue status to YouTube handler
- Create queue table in terminal dashboard
- Show current/queued/completed counts
- Real-time updates (1s refresh)

**Phase 4: Testing & Docs** (30 min)
- Integration tests (API → Handler → Processing)
- Error handling tests
- Update documentation

#### Success Criteria

- ✅ Template creation triggers processing automatically
- ✅ API accepts external processing requests
- ✅ Dashboard shows real-time queue status
- ✅ Processing completes within 30 seconds
- ✅ Graceful error handling when daemon offline

#### Why P0 Priority

**Immediate Value**:
- Zero-friction YouTube note creation
- Foundation for all future API integrations
- Enables mobile/web/automation tool access
- Natural workflow (create template → auto-process)

**Strategic Value**:
- API-first architecture for future features
- External tool integration capability
- Scalable processing infrastructure

---

### 🟡 P1 NEW: YouTube Transcript Archival System (Oct 17, 2025)

**Status**: 🟡 **PLANNING** - Manifest complete, ready for implementation  
**Priority**: P1 - **ENHANCES YOUTUBE PROCESSING**  
**Timeline**: 90 minutes (30min saver, 20min integration, 20min linking, 20min testing)  
**Branch**: `feat/youtube-transcript-archival` (to be created)  
**Manifest**: `Projects/ACTIVE/youtube-transcript-archival-manifest.md` ✅  
**Parent**: YouTube API Trigger System (can be implemented independently)

#### Vision

Automatically save complete YouTube video transcripts as separate, searchable markdown files with bidirectional links to parent notes. Creates comprehensive archive while keeping notes focused on curated insights.

#### Key Components

**Phase 1: Core Transcript Saver** (30 min)
- Create `youtube_transcript_saver.py` utility
- Save transcripts to `Media/Transcripts/youtube-{id}-{date}.md`
- Format with timestamps (MM:SS) and frontmatter
- Include video metadata and parent note link

**Phase 2: Handler Integration** (20 min)
- Add transcript saver to `YouTubeFeatureHandler`
- Call `save_transcript()` after fetching
- Generate wikilink for saved transcript
- No changes to existing quote extraction flow

**Phase 3: Note Linking** (20 min)
- Add `transcript_file` to note frontmatter
- Insert "Full Transcript: [[...]]" link in note body
- Bidirectional linking (note ↔ transcript)
- Test in Obsidian graph view

**Phase 4: Testing & Polish** (20 min)
- Unit tests for `YouTubeTranscriptSaver`
- Integration tests with handler
- Test with various video lengths
- Documentation updates

#### File Structure

```
knowledge/
  Media/
    Transcripts/
      youtube-dQw4w9WgXcQ-2025-10-17.md  ← Full transcript
  Inbox/
    YouTube/
      ai-coding-tutorial.md  ← Note with link to transcript
```

#### Success Criteria

- ✅ Transcript saved for every processed video
- ✅ Bidirectional links work in both directions
- ✅ Timestamps properly formatted (MM:SS)
- ✅ Transcript searchable via Obsidian search
- ✅ No duplicate transcripts created

#### Why P1 Priority

**Immediate Value**:
- Full context preservation (transcripts archived)
- Searchable across all video content
- One-click access from note to full transcript
- No loss if video deleted or cache expires

**Future Capabilities**:
- Search across all transcripts
- Regenerate quotes without re-fetching
- Transcript quality analytics
- Multi-format export (JSON, SRT, TXT)

---

### 🔴 P0 CRITICAL: Note Lifecycle Status Management (Oct 14, 2025)

**Status**: 🚧 **PBI-001 COMPLETE** - Status update bug fixed, auto-promotion pending  
**Priority**: P0 - **ENABLES COMPLETE WORKFLOW AUTOMATION**  
**Timeline**: 6-8 hours total (2h complete, 4-6h remaining)  
**Branch**: `fix/note-lifecycle-status-management` ✅ CREATED  
**User Decision**: "I really want auto-promotion, to enable flow" - Oct 14, 2025

#### ✅ PBI-001: Status Update Bug Fix (COMPLETE - 2h)
- **Architecture**: Extracted NoteLifecycleManager (ADR-002) ✅
- **Tests**: 16/16 passing (10 lifecycle + 6 integration) ✅
- **Bug Fixed**: Notes now transition inbox → promoted with processed_date ✅
- **Error Handling**: Status only updates if AI processing succeeds ✅
- **Lessons**: `Projects/COMPLETED-2025-10/pbi-001-note-lifecycle-status-management-lessons-learned.md` ✅

#### The Critical Bug

**Issue Identified**: Notes are being AI-processed but status field never updates
- ✅ AI adds metadata (tags, quality scores, connections)
- ❌ Status remains `status: inbox` (should be `status: promoted`)
- ❌ Notes accumulate in Inbox/ indefinitely
- ❌ Weekly review shows same notes repeatedly
- ❌ No clear progression through workflow

**Impact**: **77 notes in Inbox/** with this issue right now
- All have `ai_processed: true` and quality scores
- All still show `status: inbox`
- Can't be distinguished from unprocessed notes
- Breaks entire workflow automation chain

#### Root Cause Analysis

**File**: `development/src/ai/workflow_manager.py::process_inbox_note()`  
**Location**: After line ~400 (after all AI processing)  
**Missing Code**: 3 lines to update status field

```python
# CURRENT: AI processing completes but status never updated
if not results.get("error"):
    updated_content = build_frontmatter(frontmatter, body)
    safe_write(note_path, updated_content)
    results["file_updated"] = True
    # ❌ MISSING: frontmatter["status"] = "promoted"

# SHOULD BE:
if not results.get("error"):
    frontmatter["status"] = "promoted"  # ✅ ADD THIS
    frontmatter["processed_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    updated_content = build_frontmatter(frontmatter, body)
    safe_write(note_path, updated_content)
    results["file_updated"] = True
    results["status_updated"] = "promoted"  # ✅ ADD THIS
```

#### Complete Implementation Plan - FULL SCOPE ✅

**Sequencing**: Fix code first → Enable auto-promotion → Clean up files

**PBI-001 (P0) - Critical Bug Fix** (60 minutes):
- [ ] Add status update in `process_inbox_note()` (3 lines)
- [ ] Add `processed_date` timestamp
- [ ] Write unit tests for status transition (offline-safe, <2s)
- [ ] Add error handling (status only updates on success)
- [ ] Verify idempotence (re-running doesn't duplicate timestamps)
- [ ] Integration test with real vault

**PBI-002 (P1) - Complete Directory Integration** (90 minutes):
- [ ] Add `self.literature_dir` to `__init__()`
- [ ] Update `promote_note()` to accept `target_type` parameter
- [ ] Handle all 3 types consistently (permanent/literature/fleeting)
- [ ] All promotions set `status: published` + `promoted_date`
- [ ] DirectoryOrganizer integration for backup/rollback
- [ ] Unit tests for each promotion path

**PBI-004 (P2) - Auto-Promotion System** ⭐ (2-3 hours):
- [ ] Implement `auto_promote_ready_notes(min_quality=0.7, preview=False)`
- [ ] Select notes with `status: promoted` + quality >= threshold
- [ ] Preview mode shows candidates with reasons
- [ ] Execute mode moves files + sets `status: published`
- [ ] CLI integration: `--auto-promote --quality 0.7 --preview`
- [ ] Offline-safe (uses existing metadata, no AI calls)
- [ ] Unit tests for filtering logic
- [ ] Integration test for end-to-end flow

**PBI-003 (P1) - Execute Safe File Moves** (30 minutes):
- [ ] Preview command shows detailed move plan (30 files, 0 conflicts)
- [ ] Create backup at `~/backups/knowledge/knowledge-YYYYMMDD-HHMMSS/`
- [ ] Execute moves to correct directories based on `type:` field
- [ ] Post-move validation (file system + link integrity)
- [ ] Document backup path and results

**PBI-005 (P3) - Repair Orphaned Notes** (60 minutes):
- [ ] Create `repair_orphaned_status.py` script
- [ ] Identify 77 orphaned notes (ai_processed: true, status: inbox)
- [ ] Update status to `promoted` + add `processed_date`
- [ ] Dry-run mode shows changes before applying
- [ ] Validation confirms all repairs successful

#### Complete Lifecycle Documentation

**Files Created**:
- ✅ `note-lifecycle-status-management.md` - Complete lifecycle documentation
- ✅ `workflow-diagrams/10-note-lifecycle-complete.md` - Visual flowcharts
- ✅ `workflow-enhancement-directory-integration.md` - Implementation plan

**Flowcharts Created** (4 visualizations):
1. **Main Lifecycle Flowchart** - All pathways from creation → final state
2. **Status State Diagram** - Clean state transitions (inbox → promoted → published)
3. **Type-Based Pathways** - Fleeting/Literature/Permanent paths side-by-side
4. **Bug Impact Visualization** - Current (broken) vs Fixed (working) behavior

#### Directory Integration Analysis

**Already Working** ✅:
- `promote_note()` - Moves notes between directories
- `promote_fleeting_note()` - Uses DirectoryOrganizer with backup
- Directory paths defined (Inbox, Fleeting Notes, Permanent Notes, Archive)
- CLI commands available (`--promote-note`)

**Missing** ❌:
- Status update after AI processing (CRITICAL)
- Literature directory initialization
- Auto-promotion based on quality

#### Success Metrics

**Before Sprint**:
- Notes with `status: inbox`: 77 (stuck)
- Notes with `status: promoted`: <5
- Notes in correct directories: ~80%
- Weekly review effectiveness: Low (shows same notes)
- **Manual intervention required**: Every promotion

**After Sprint (Target)**:
- Notes with `status: inbox`: ~10 (new captures only)
- Notes with `status: promoted`: 10-20 (processed, awaiting promotion)
- Notes with `status: published`: 60-70 (in correct directories)
- Notes in correct directories: 100%
- Weekly review effectiveness: High (accurate triage)
- **Auto-promotion enabled**: High-quality notes (≥0.7) automatically moved ⭐

**Flow Achievement**:
- Inbox processing → AI enhancement → Status update → **Auto-promotion** ← NEW!
- True workflow flow with minimal manual intervention
- Quality-gated automation (threshold: 0.7)

#### Deliverables

- [ ] Status update fix in workflow_manager.py
- [ ] Literature directory initialization
- [ ] Enhanced promote_note() for all types
- [ ] auto_promote_ready_notes() method
- [ ] CLI integration (--auto-promote)
- [ ] Repair script for orphaned notes
- [ ] Unit tests for all transitions
- [ ] Integration tests for complete flow
- [ ] Updated workflow diagrams
- [ ] Migration guide for users

#### Why FULL Scope (Including Auto-Promotion)

1. **User Priority**: "I really want auto-promotion, to enable flow" - Oct 14, 2025
2. **Blocks Workflow Automation**: Notes can't progress through system
3. **Manual Bottleneck**: Every promotion requires human intervention
4. **Accumulating Backlog**: 77 notes stuck in inbox right now
5. **Complete Flow Broken**: Weekly review, triage, promotion all impacted
6. **Foundation Ready**: DirectoryOrganizer (P0+P1), quality scoring, promotion methods all complete

**Value Proposition**: Auto-promotion transforms InnerOS from semi-automated tool → true flow system

**ROI**: 6-8 hours enables complete hands-off knowledge processing pipeline

---

### 🟡 P1: Inbox Metadata Repair System (Jan 8, 2025)

**Status**: 📋 **PLANNED** - Ready for TDD implementation  
**Priority**: P1 - **UNBLOCKS AUTO-PROMOTION WORKFLOW**  
**Timeline**: 3-4 hours (follows proven TDD patterns)  
**Branch**: `feat/inbox-metadata-repair` (to be created)  
**Manifest**: `Projects/ACTIVE/inbox-metadata-repair-system-manifest.md` ✅  
**Depends On**: Auto-promotion system (PBI-002 complete ✅)

#### Problem Statement

**8 notes in Inbox cannot be auto-promoted** due to missing `type:` frontmatter:
- Auto-promotion error rate: 21% (8/40 notes)
- Notes with high quality (0.85) blocked from workflow
- Manual frontmatter editing required
- **Root Cause**: Bulk import on Oct 12, 2024 without validation

```
🚨 ERRORS
------
   voice-note-prompts-for-knowledge-capture.md: Missing 'type' field
   Study link between price risk and trust...md: Missing 'type' field
   sprint 2 8020.md: Missing 'type' field
   newsletter-generator-prompt.md: Missing 'type' field
   zettelkasten-voice-prompts-v1.md: Missing 'type' field
   Progress-8-26.md: Missing 'type' field
   enhanced-connections-live-data-analysis-report.md: Missing 'type' field
   voice-prompts-quick-reference-card.md: Missing 'type' field
```

#### Solution: Automated Template System (Option B)

**New Component**: `MetadataRepairEngine` (ADR-002 Pattern)

**Responsibilities**:
1. Detect notes missing required frontmatter (`type`, `created`)
2. Infer type from filename patterns (`lit-`, `fleeting-`, `capture-`)
3. Repair frontmatter while preserving existing fields
4. Integrate with backup system for safety
5. Support dry-run preview mode

**Architecture Integration**:
```
CoreWorkflowCLI --repair-metadata
  ↓
WorkflowManager.repair_inbox_metadata()  [delegation only]
  ↓
MetadataRepairEngine.repair_batch()
  ↓
BackupSystem (existing)
```

#### Implementation Plan (5 PBIs)

**PBI-001: Detection System (RED Phase)** - 45 min
- Create 8-10 failing tests for metadata detection
- Test fixtures for 8 actual error notes
- Pattern matching test cases

**PBI-002: Repair Engine (GREEN Phase)** - 60 min
- Implement `MetadataRepairEngine` class (250-300 LOC)
- Filename pattern matching (lit-, fleeting-, capture-)
- Content-based inference (fallback)
- Preserve existing frontmatter fields
- All 10 tests passing

**PBI-003: WorkflowManager Integration (REFACTOR)** - 30 min
- Add delegation method following ADR-002 patterns
- 3 new delegation tests
- Total: 13/13 tests passing

**PBI-004: CLI Integration** - 30 min
- Add `--repair-metadata` command
- Dry-run and execute modes
- Rich output formatting

**PBI-005: Real Data Validation** - 20 min
- Test on 8 actual error notes
- Verify auto-promotion runs with 0 errors
- Document results

#### Success Metrics

**Before Repair**:
- Inbox errors: 8 notes (21%)
- Auto-promotion error rate: 21%
- Manual intervention: Required

**After Repair (Target)**:
- Inbox errors: 0 notes (0%)
- Auto-promotion error rate: 0%
- Manual intervention: Not required
- Additional notes promoted: 5+ (high-quality notes that were blocked)

#### Why P1 Priority

**Immediate Value**:
- Unblocks 8 high-quality notes (quality: 0.85)
- Reduces auto-promotion errors to 0%
- Enables complete hands-off workflow
- Proves pattern for future bulk imports

**Prevention Strategy**:
- Documents inference rules for manual imports
- Foundation for Phase 2: Import Validation Pipeline
- Prevents recurring metadata issues

#### Timeline & Dependencies

**Prerequisites**:
- ✅ Auto-promotion system working (PBI-002, Jan 8, 2025)
- ✅ ADR-002 delegation patterns proven
- ✅ TDD infrastructure established

**Estimated Completion**: 3-4 hours (single focused session)

**Completion Target**: Within 1 week of auto-promotion deployment

---

### 🔵 P2: Source Code Reorganization (Planned)

**Status**: 📋 **PLANNED** - Medium/Low Priority, Gradual Implementation  
**Priority**: P2 - **DEVELOPER EXPERIENCE & MAINTAINABILITY**  
**Timeline**: 4-6 weeks (gradual, ~20 hours total)  
**Risk**: LOW - Python imports easily refactorable, strong test coverage  
**Manifest**: `Projects/ACTIVE/source-code-reorganization-manifest.md` ✅

#### Problem Statement

**Current Pain Points:**
- `src/ai/` - **56 Python files** (impossible to navigate)
- `src/cli/` - **44 Python files** (cognitive overload)
- 20+ minutes to find related code
- 15+ scattered `_utils.py` files
- Difficult onboarding for contributors

**Goal**: Domain-driven organization with <2 minute code discovery (90% improvement)

#### 80/20 High-Impact Changes

**#1: Split `ai/` into 7 domains** (40% of value)
- `core/`, `connections/`, `tags/`, `enhancement/`, `analytics/`, `media/`, `imports/`
- 56 files → 7 packages with 2-12 files each

**#2: Split `cli/` into 7 features** (30% of value)
- `core/`, `screenshots/`, `connections/`, `tags/`, `workflows/`, `monitoring/`, `media/`
- 44 files → 7 packages with 2-8 files each

**#3: Consolidate utilities** (20% of value)
- Group `_utils.py` files with their primary modules
- Create `utils/` subdirectories where appropriate

**#4: Create `models/` package** (10% of value)
- Extract shared data structures (Note, Connection, Tag, Schema models)
- Single source of truth for data models

#### Implementation Plan

**Week 1 (Proof of Concept)**:
- Extract `ai/connections/` (12 files, 2 hours)
- Extract `ai/tags/` (10 files, 2 hours)
- Validate tests pass, document lessons
- Go/No-Go decision point

**Week 2 (AI Package Completion)**:
- Extract remaining 5 domains from `ai/`
- Update imports, test validation

**Week 3-4 (CLI Package)**:
- Reorganize 44 CLI files into 7 feature packages
- Test all CLI commands

**Week 5-6 (Polish)**:
- Consolidate utilities
- Create models package
- Documentation updates

#### Success Metrics

**Before**: 56 files in `ai/`, 44 in `cli/`, 20+ min code discovery  
**After**: <12 files per directory, <2 min code discovery (90% improvement)

#### Why P2 Priority

**Timing Considerations:**
- Not urgent, but high long-term value
- Best done during maintenance periods
- Can be paused/resumed anytime
- Low risk with strong test coverage
- Enables future contributor onboarding

**Recommended Start**: After Note Lifecycle sprint complete, during lower-intensity period

---

### 🟡 P1: WorkflowManager Deprecation & Decomposition (Post-Sprint)

**Status**: 📋 **PLANNED** - Extract after Note Lifecycle sprint complete  
**Priority**: P1 - **ARCHITECTURAL DEBT REDUCTION**  
**Timeline**: 3-4 sprints (12-16 hours total)  
**Trigger**: Current sprint completion (PBI-001 through PBI-005)  
**Goal**: Deprecate monolithic WorkflowManager while maintaining 100% functionality

#### Current State (Architectural Violation)

**WorkflowManager god class metrics:**
```
LOC: 2,420 (limit: 500) - 384% over limit
Methods: 59 (limit: 20) - 295% over limit
Responsibilities: 8+ (should be 1)
```

**Violations:**
- ❌ Exceeds 500 LOC hard limit by 1,920 lines
- ❌ Exceeds 20 methods hard limit by 39 methods
- ❌ Multiple unrelated responsibilities
- ❌ High coupling (imported by 10+ files)
- ❌ Difficult to test (extensive mocking required)

#### Decomposition Strategy (ADR-003 Required)

**Phase 1: Extract Managers (~8 hours over 2 sprints)**

1. **ConnectionManager** (~300 LOC extraction)
   - Responsibility: Connection discovery and link suggestions
   - Extract from: Lines 329-356 + related methods
   - Benefits: Reusable by smart link system
   - Tests: 15+ unit tests
   - Pattern: Follow NoteLifecycleManager (ADR-002)

2. **AnalyticsCoordinator** (~400 LOC extraction)
   - Responsibility: Analytics and metrics aggregation
   - Extract from: Analytics methods + weekly review logic
   - Benefits: Reusable by reporting systems
   - Tests: 20+ unit tests

3. **PromotionEngine** (~200 LOC extraction)
   - Responsibility: Quality-gated note promotion
   - Extract from: Promotion methods + auto-promote logic
   - Benefits: Clear separation of promotion concerns
   - Tests: 12+ unit tests
   - Depends on: NoteLifecycleManager integration

**Phase 2: Create Facade/Adapter (~4 hours)**

4. **WorkflowManagerAdapter** (Deprecation wrapper)
   - Purpose: Maintain backward compatibility during migration
   - Pattern: Facade that delegates to new managers
   - Migration path: Change imports gradually
   - Timeline: 1-2 releases to fully deprecate

**Phase 3: Migration & Deprecation (~4 hours)**

5. **Update Imports** across codebase
   - CLI files: Use specific managers directly
   - Tests: Update to test managers, not god class
   - Documentation: Migration guide for any external users

6. **Deprecate WorkflowManager**
   - Add `@deprecated` decorator
   - Emit warnings when used
   - Document migration path
   - Remove in Phase 6 (multi-user foundation)

#### Success Metrics

**Architectural Compliance:**
- [ ] Zero classes >500 LOC
- [ ] Zero classes >20 methods
- [ ] All managers follow single responsibility principle
- [ ] Test coverage maintained >95%

**Functionality Preservation:**
- [ ] 100% backward compatibility during migration
- [ ] Zero regressions in existing tests
- [ ] All CLI commands work identically
- [ ] Performance maintained or improved

**Migration Completion:**
- [ ] All internal imports updated
- [ ] Deprecation warnings active
- [ ] Migration guide published
- [ ] WorkflowManagerAdapter tested

#### Timeline & Dependencies

**Prerequisites:**
- ✅ Note Lifecycle sprint complete (PBI-001 through PBI-005)
- ✅ NoteLifecycleManager pattern proven (ADR-002)
- ✅ TDD methodology established

**Sprint Breakdown:**
- **Sprint 1** (Week 1): Extract ConnectionManager + AnalyticsCoordinator
- **Sprint 2** (Week 2): Extract PromotionEngine + Create Adapter
- **Sprint 3** (Week 3): Migration + Deprecation + Testing
- **Sprint 4** (Week 4): Buffer + Documentation + Lessons Learned

**Completion Target:** End of November 2025

#### References & Documentation

**Pattern Established:**
- ADR-002: NoteLifecycleManager extraction (completed Oct 14, 2025)
- Lessons: `Projects/COMPLETED-2025-10/pbi-001-note-lifecycle-status-management-lessons-learned.md`
- Constraints: `.windsurf/rules/architectural-constraints.md`

**To Be Created:**
- ADR-003: WorkflowManager Decomposition Strategy
- ADR-004: Migration & Deprecation Path
- Lessons: Complete after each extraction

---

### ✅ Testing Infrastructure Revamp - Week 1-2 (Oct 12-16, 2025)

**Status**: ✅ **COMPLETE** - P0 objectives exceeded, infrastructure proven safe  
**Duration**: 5 days (Oct 12-16, 2025)  
**Performance**: **200-400x faster** test suite (5-10 min → 1.56s)  
**Deliverables**: 6 TDD iterations, 88 tests, comprehensive documentation  
**Summary**: `Projects/COMPLETED-2025-10/testing-infrastructure-week1-2-final-summary.md` ✅  
**Branch**: `feat/testing-week2-tdd-iteration-6-smoke-tests` → **MERGED TO MAIN** ✅

#### Key Achievements

**Week 1 - Core Infrastructure** (Days 1-3):
- ✅ Iteration 1: Test organization (47x faster unit tests)
- ✅ Iteration 2: Vault factories (**300x faster** integration tests: 5-10min → 1.35s)
- ✅ Iteration 3: Integration migration (37 tests migrated)
- ✅ Iteration 4: Marker verification (6,000x faster: 5-10min → 0.05s)

**Week 2 - Production Validation** (Days 4-5):
- ✅ Iteration 5: Projects/ACTIVE cleanup (52 → 19 files)
- ✅ Iteration 6: Smoke test infrastructure (production-safe with critical safety fixes)

**Performance Impact**:
- Integration tests: 5-10 min → 1.35s (**300x faster**)
- Marker verification: 5-10 min → 0.05s (**6,000x faster**)
- Total fast suite: 5-10 min → 1.56s (**200-400x faster**)

**Key Lessons**:
1. **Vault Factories Critical**: 300x improvement from single pattern change
2. **Static Analysis > Subprocess**: 6,000x faster for validation
3. **Fast Rewrites > Slow Patches**: 15min rewrite vs 30+ min patching
4. **Safety First**: Always use --dry-run with production vault
5. **Path Handling**: conftest.py must handle tests outside tests/ directory

**Future Enhancements** (Optional - if needed):
- P1: Performance benchmarks (baselines.json, regression detection)
- P1: Load tests (500/1000 note vault simulations)
- P2: CI/CD pipeline (.github/workflows/fast-tests.yml)
- P2: Test documentation (comprehensive test README)

---

### 🏗️ P0 CRITICAL: ADR-004 CLI Layer Extraction (Oct 11-25, 2025)

**Status**: ✅ **ACCEPTED** - Architectural pivot approved  
**Priority**: P0 - **COMPLETES ADR-001 ARCHITECTURE VISION**  
**Timeline**: 2 weeks (Oct 11-25)  
**ADR**: `adr-004-cli-layer-extraction.md` ✅  
**Branch**: `feat/adr-004-cli-extraction` (to be created)

#### Why This is P0

**ADR-001 Only Half Complete**:
- ✅ Backend refactored: WorkflowManager → 4 managers (COMPLETE Oct 5)
- ❌ Frontend still monolithic: workflow_demo.py at 2,074 LOC (28% extracted)
- Quality audit found bugs in **wrong architectural layer** (monolithic CLI)

**Decision**: Complete the architecture before continuing features
- Backend clean ✅ + Frontend clean ❌ = System half-broken
- 18/25 commands need extraction from workflow_demo.py
- Bug fixes should go to **dedicated CLIs**, not monolith

#### Current CLI Extraction Status: 28% Complete (7/25)

**✅ Already Extracted** (7 commands):
- YouTube processing (2) → `youtube_cli.py` (372 LOC)
- Tag enhancement (3) → `advanced_tag_enhancement_cli.py`
- Review notes (3) → `notes_cli.py`
- Performance (1) → `real_data_performance_cli.py`

**❌ Needs Extraction** (18 commands):
- Weekly review (2) → `weekly_review_cli.py` [P1.1 - Week 1]
- Fleeting notes (3) → `fleeting_cli.py` [P1.2 - Week 1]
- Safe workflows (5) → `workflow_cli.py` [P1.3 - Week 1]
- Backup (3) → `backup_cli.py` [P1.4 - Week 1]
- Core workflow (5) → `core_workflow_cli.py` [P2.1 - Week 2]

#### 2-Week Sprint Plan

**Week 1 (Oct 11-18)**: High-priority extractions
- Days 1-2: Weekly review + fleeting CLIs
- Days 3-4: Safe workflow + backup CLIs
- Day 5: Integration testing, bug fixes

**Week 2 (Oct 19-25)**: Core workflow + completion
- Days 1-2: Core workflow CLI
- Days 3-4: Remaining commands
- Days 5-6: Documentation, deprecation, final testing

#### Success Criteria
- [ ] All 25 commands extracted to dedicated CLIs
- [ ] workflow_demo.py has deprecation warning
- [ ] All docs updated (README, CLI-REF, QUICK-REF, GETTING-STARTED)
- [ ] Quality audit re-run validates bugs in correct files
- [ ] Each CLI <400 LOC, focused, testable

**After Completion**: TUI development can begin with clean architecture foundation

---

### 🐛 P1 DEFERRED: Quality Audit Bug Fixes (Oct 10, 2025)

**Status**: ⏸️ **DEFERRED** - Waiting for ADR-004 CLI extraction  
**Priority**: P1 - Deferred until dedicated CLIs exist  
**Timeline**: Fix bugs in dedicated CLIs after extraction  
**Manifest**: `quality-audit-manifest.md` ✅

**Why Deferred**: Quality audit found bugs in monolithic workflow_demo.py. Rather than fix bugs in deprecated code, we're extracting commands to dedicated CLIs first (ADR-004), then fixing bugs in the correct architectural layer.

#### Audit Results Summary

**Tested**: 11/11 workflows (100% coverage) ✅  
**Working**: 3/11 (27%) - Backup, Directory Preview, Daemon Status  
**Broken**: 4/11 (36%) - Connection Discovery, Enhanced Metrics, Fleeting Health, Orphaned Notes  
**Partial**: 1/11 (9%) - YouTube Processing  
**With Issues**: 1/11 (9%) - Weekly Review  

#### Critical Bugs Found

**Systemic Issue**: 4 KeyError bugs with identical root cause (unsafe dictionary access)
- All use `note['key']` instead of `note.get('key', default)`
- Indicates need for typed `Note` dataclass

**Bug Reports Created** (5):
1. **`bug-connections-import-error-2025-10-10.md`** 🔴 CRITICAL
   - Import paths wrong: `from cli.` should be `from src.cli.`
   - **Impact**: Connection Discovery completely broken
   - **Fix Time**: 5 minutes

2. **`bug-enhanced-metrics-keyerror-2025-10-10.md`** 🟠 HIGH
   - KeyError: 'directory' in `weekly_review_formatter.py` line 313
   - **Impact**: Cannot view vault analytics
   - **Fix Time**: 10 minutes

3. **`bug-fleeting-health-attributeerror-2025-10-10.md`** 🟠 HIGH
   - Missing method after WorkflowManager refactoring (Oct 5)
   - **Impact**: Cannot monitor fleeting note health
   - **Fix Time**: 60 minutes (needs investigation)

4. **`bug-orphaned-notes-keyerror-2025-10-10.md`** 🟠 HIGH
   - KeyError: 'path' at line 1394 (4th KeyError bug)
   - **Impact**: Cannot identify disconnected knowledge
   - **Fix Time**: 5 minutes

5. **`bug-youtube-processing-failures-2025-10-10.md`** 🟠 HIGH
   - Silent failures with no error messages
   - **Impact**: Feature broken, no debugging info
   - **Fix Time**: 30 minutes

#### Deliverables

- ✅ **Audit Report**: `audit-report-2025-10-10.md` (live test results)
- ✅ **Session Summary**: `AUDIT-SESSION-SUMMARY-2025-10-10.md` (complete findings)
- ✅ **Bug Reports**: 5 comprehensive reports with fixes proposed
- ✅ **Audit Manifest**: `quality-audit-manifest.md` (strategy)
- [ ] **Bug Fixes**: Implement all 5 fixes (2-3 hours)
- [ ] **Regression Tests**: Validate all workflows working
- [ ] **TUI Development**: Begin after bugs fixed

#### Next Steps (Priority Order)

1. **Fix Import Error** (5 min) - Unblocks Connection Discovery
2. **Fix KeyErrors** (20 min) - 3 bugs, same pattern
3. **Investigate Fleeting Health** (60 min) - Find missing method
4. **Improve YouTube Errors** (30 min) - Add error messages
5. **Code Review** (30 min) - Find other unsafe dict accesses
6. **Consider Note Dataclass** (optional) - Prevent future KeyErrors

#### Success Metrics

**Current**: 27% workflows working (3/11)  
**After Quick Fixes**: 63% workflows working (7/11)  
**Target**: 100% workflows working before TUI

**ROI**: 1 hour audit found 5 bugs, saved 2.5-5 hours of debugging during TUI development

---

### 🚨 CATASTROPHIC INCIDENT - RESOLVED (Oct 8, 2025)

**Incident**: File watching loop caused YouTube IP ban

#### Root Cause Analysis
- **File**: `Projects/ACTIVE/youtube-rate-limit-investigation-2025-10-08.md` ✅
- **Problem**: File watching loop + no caching → 2,165 processing events → ~1,000 API calls → IP ban
- **Evidence**: youtube-note.md processed 758 times in one day (should be 1-2 times)
- **Peak Burst**: 1,868 events in 2 minutes (8-16 requests/second)
- **YouTube Response**: Network-wide IP ban for bot-like behavior

#### Fixes Implemented ✅
- **File**: `Projects/ACTIVE/catastrophic-incident-fix-2025-10-08.md` ✅
- **Fix 1**: Cooldown System (60-second default)
  - Prevents file from being processed <60 seconds after last processing
  - Tracks processing time per file
  - Prevents concurrent processing of same file
  - **Impact**: 98% reduction in processing events (2,165 → ~50/day)
  
- **Fix 2**: Transcript Caching (7-day TTL)
  - New file: `development/src/automation/transcript_cache.py` (272 lines)
  - Persistent JSON storage in `.automation/cache/`
  - Cache-first strategy: check cache before API call
  - Thread-safe with hit/miss metrics tracking
  - **Impact**: 99% reduction in API calls for repeated videos

#### Validation ✅
- **Test File**: `development/demos/test_catastrophic_incident_fix.py`
- **Results**: 3/3 tests passing
  - Cooldown prevents file watching loops ✅
  - Cache prevents redundant API calls ✅
  - Combined protection validated ✅

#### YouTube Official API Migration: CANCELED ❌ (Oct 9, 2025)
- **Decision**: Migration not needed - API v3 doesn't support arbitrary video transcripts
- **Discovery**: `captions.download()` only works for videos you own, not any video
- **Cleanup**: Removed 1,677 lines of unused implementation code (commit 8a6ba34)
- **Files Removed**: youtube_official_api_fetcher.py, youtube_api_utils.py, tests
- **Result**: Continue using unofficial API with protection (cooldown + caching)
- **Manifest**: Archived to `youtube-official-api-integration-manifest-deprecated-2025-10-09.md`

#### Current Status
- 🛑 **Automation DISABLED** (safety lock active)
- ⏰ **Awaiting YouTube IP unblock** (24-48 hours expected)
- ✅ **Fixes validated and ready** for re-enable
- ✅ **Codebase clean** - No breaking changes, all tests passing
- 📊 **Combined Impact**: 99.87% fewer API calls

#### Next Steps
1. **Choose pivot work** (Distribution System recommended)
2. Wait 24-48 hours for YouTube IP unblock (passive)
3. Test single file with fixes active
4. Monitor for 1 hour (verify no loops)
5. Re-enable automation (remove `.automation/AUTOMATION_DISABLED`)
6. Monitor cache hit rate (target >80%)

---

### 🐛 Active Bugs (Priority: HIGH → P0)

**NEW P0 BUGS** (Oct 10, 2025) - From Quality Audit:
- See "P0 CRITICAL: Quality Audit Bug Fixes" section above for 5 new bugs
- **Total Fix Time**: 2-3 hours
- **Blocking**: TUI development

#### Bug: Empty video_id Frontmatter in YouTube Template
- **File**: `bug-empty-video-id-frontmatter-templater-2025-10-08.md`
- **Severity**: MEDIUM - Has workaround (daemon extracts from body)
- **Issue**: Obsidian template extracts video_id but doesn't populate frontmatter field
- **Workaround**: Daemon has fallback parser for body content
- **Status**: ✅ FIXED with workaround (template + daemon fallback)
- **Priority**: Low (workaround sufficient)

#### ~~YouTube API Rate Limiting~~ → PERMANENTLY FIXED ✅
- **Original Issue**: YouTube blocking unofficial scraping (100% rate limited)
- **Investigation**: `youtube-rate-limit-investigation-2025-10-08.md`
- **Root Cause**: File watching loop, not rate limiting
- **Solution**: Cooldown + Caching (not Official API needed)
- **Status**: ✅ **FIXED** - Both root causes eliminated
- **Result**: Can continue using free unofficial API with protection

### 🛡️ Circuit Breaker & Rate Limit Protection (P1 - CRITICAL SAFETY)

**Status**: 📋 BACKLOG - Planned after Distribution System  
**Priority**: P1 - HIGH (Prevents catastrophic incidents)  
**Trigger**: YouTube incident (2,165 events could have cost $120-1,000+ with paid API)

**Problem**: Without protection, infinite loops can cause unlimited financial damage

**What Could Have Happened**:
- YouTube incident was FREE API (just IP ban)
- If OpenAI GPT-4: 1,000 calls × $0.12 = **$120+ in hours**
- If AWS/GCP API: Could rack up **$1,000+ easily**
- No automatic shutoff = unlimited burn 🔥

**Solution**: Multi-layer protection system
1. **Circuit Breakers**: Per-feature request limits (50/hour, 200/day)
2. **Budget Enforcer**: Daily cost ceiling ($10 default, auto-shutdown at 80%)
3. **Anomaly Detection**: Burst detection, file thrashing, error spikes
4. **Emergency Kill Switch**: Manual override for immediate shutdown

**Deliverables**:
- ✅ Circuit breaker pattern implementation
- ✅ Budget tracking and enforcement
- ✅ Anomaly detection (bursts, loops, errors)
- ✅ CLI monitoring: `inneros protection-status`
- ✅ HTTP endpoints: `/protection/budget`, `/protection/circuits`
- ✅ macOS notifications for threshold alerts
- ✅ Integration with all existing handlers

**Timeline**: 4-5 days
- Phase 1: Circuit Breaker (1 day)
- Phase 2: Budget Enforcer (1 day)
- Phase 3: Anomaly Detection (2 days)
- Phase 4: Integration & Monitoring (1 day)

**Dependencies**: None (can implement anytime)

**Blockers**: BLOCKS any paid API integration (OpenAI, AWS, etc.)

**Manifest**: `circuit-breaker-rate-limit-protection-manifest.md` ✅

**ROI**: One prevented incident pays for entire development cost

---

### 🔴 Automation Completion System (P0 - CRITICAL FOUNDATION)

**Status**: 📋 DISCOVERY COMPLETE → Ready for Implementation  
**Priority**: P0 - Unblocks all future workflow automation  
**Duration**: 5 weeks (4 sprints)

**Problem Identified** (Oct 6, 2025):
- Built 8 exceptional AI features with TDD rigor
- Only 15% automation coverage (features require manual CLI triggers)
- Zero complete Phase 3 (Automation) or Phase 4 (Monitoring) implementations
- Design pattern gap: TDD stops at CLI integration instead of completing workflows

**Goal**: Transform InnerOS from manually-triggered toolbox → self-running knowledge pipeline

**Deliverables**:
- ✅ **Audit Complete**: `Projects/ACTIVE/automation-completion-retrofit-manifest.md`
  - Phase completion matrix for 8 features
  - Gap analysis (Phase 3: 15%, Phase 4: 12.5%)
  - 5-week implementation roadmap
- ✅ **Workflow Created**: `.windsurf/workflows/complete-feature-development.md`
  - Mandatory 4-phase methodology (Engine, CLI, Automation, Monitoring)
  - TDD patterns for Phase 3 & 4
  - Daemon integration templates
- ✅ **Rules Update**: `Projects/ACTIVE/rules-update-phase-3-4.md`
  - Instructions for updating `.windsurf/rules/`
  - Enforcement of Phase 3 & 4 requirements
- ✅ **Summary**: `Projects/ACTIVE/automation-system-implementation-summary.md`

**Implementation Plan**:
- **Sprint 1** (Week 1): Background daemon + event watchers
- **Sprint 2** (Week 2-3): P0 features automation (screenshots, smart links, inbox)
- **Sprint 3** (Week 4): Monitoring layer (metrics, health checks, alerts)
- **Sprint 4** (Week 5): Integration, testing, production deployment

**Success Metrics**:
- 100% automation coverage (all 8 features have Phase 3)
- 100% monitoring coverage (all 8 features have Phase 4)
- 80% time savings (manual → automatic workflows)
- <5s event response time (file change → processing)

**Current Progress**:
- ✅ Sprint 1-2: Daemon core + event watchers COMPLETE
- ✅ Sprint 2: Screenshot, SmartLink, YouTube handlers COMPLETE
- ✅ Sprint 3: Health monitoring and metrics COMPLETE
- ✅ Sprint 4: Production deployment with systemd COMPLETE
- 🎯 **Next**: Directory Organization Handler (Iteration 10)

---

### 🟡 Knowledge Capture System - POC PHASE

- **Goal**: Transform mobile screenshots + voice notes into connected Zettelkasten knowledge
- **Innovation**: Temporal pairing of screenshot + voice context eliminates annotation burden
- **Real Workflow**: Samsung S23 captures → OneDrive sync → timestamp matching → knowledge integration
- **POC Focus**: Validate screenshot + voice note pairing accuracy (>90% target)
- **Deliverables**:
  - **POC Manifest**: `Projects/capture-matcher-poc-manifest.md` ✅
  - **Full System Manifest**: `Projects/knowledge-capture-system-manifest.md` ✅
  - Capture matcher script with OneDrive integration
  - 1-week real-world validation with success metrics
  - Go/No-Go decision for full system development

### 🟡 Automated Background Daemon (Core Infrastructure)

- **Goal**: Transform InnerOS into always-running, autonomous knowledge processing system
- **Approach**: Extract existing AutoProcessor into standalone daemon service  
- **Dependencies**: Current AI workflow system ✅, system service configuration ⏳
- **Deliverables**:
  - Background daemon with file watching and scheduling
  - System service configuration (macOS LaunchD/Linux systemd)
  - Automated maintenance tasks (weekly review, orphan detection)
  - **Manifest**: `Projects/automated-background-daemon-manifest.md` ✅

### 📚 Reading Intake Pipeline (Phase 5 Extension)

- **Approach**: Integration-first; reuse Phase 5 AI workflows
- **Dependencies**: Template system ✅, schema integration ⏳, image linking ⏳
- **Deliverables**:
  - Schema extension for `source:` and `saved_at`
  - Literature templates with claims/quotes
  - CLI import adapters + triage
  - [ ] **User journey flowchart** (NEEDS REVIEW: `Projects/reading-intake-user-journey-flowchart.md`)

### 🚀 Distribution & Productionization System - ✅ COMPLETE (Oct 9, 2025)

**Status**: ✅ **SHIPPED** - v0.1.0-alpha live on GitHub  
**Priority**: P0 - **STREAMING VALIDATION ENABLER**  
**Timeline**: 2-3 days → **COMPLETED**

**Achievement**:
- ✅ GitHub repository: https://github.com/thaddiusatme/inneros-zettelkasten-public
- ✅ v0.1.0-alpha release tagged and published
- ✅ 437 files in public distribution (98.4% size reduction)
- ✅ 680/775 tests passing (88%)
- ✅ Security audit passed
- ✅ Installation guide complete

**Deliverables** (ALL COMPLETE):
  - ✅ Distribution creation script (`scripts/create-distribution.sh`)
  - ✅ Security audit script (`scripts/security-audit.py`)
  - ✅ Sample knowledge structure (`knowledge-starter-pack/` with 6 example notes)
  - ✅ Distribution .gitignore (excludes all personal content)
  - ✅ Installation guide (INSTALLATION.md)
  - ✅ Streaming demo workflow guide (`streaming-demo-workflow.md`)
  - ✅ README with features documented
  - ✅ Public GitHub repository
  - ✅ v0.1.0-alpha release
  - **Architecture**: `Projects/ACTIVE/adr-003-distribution-architecture.md` ✅
  - **Directory Guide**: `Projects/ACTIVE/directory-context-guide.md` ✅
  - **Summary**: `Projects/ACTIVE/DISTRIBUTION-SYSTEM-SUMMARY.md` ✅
  - **Manifest**: `Projects/ACTIVE/distribution-productionization-manifest.md` ✅
  - **Lessons Learned**: `Projects/ACTIVE/distribution-system-tdd-iteration-1-lessons-learned.md` ✅

---

### 🎨 Retro TUI Development (P1 - PLANNED)

**Status**: 📋 **BLOCKED** - Awaiting bug fixes  
**Priority**: P1 - High value after bugs fixed  
**Timeline**: 1 week (After bugs fixed - Oct 11-18)  
**Manifest**: `retro-tui-design-manifest.md` ✅

**Goal**: Unified retro terminal UI for all InnerOS workflows

**Design**:
- ASCII-based retro aesthetic (nostalgic, fun)
- Keyboard-driven navigation (no mouse)
- Single `inneros` command for everything
- Main menu → workflow selection → execution → results
- Tech stack: Rich/Textual (Python TUI libraries)

**Prerequisites**:
- ✅ Quality audit complete (11/11 workflows tested)
- ✅ Bugs documented (5 comprehensive reports)
- [ ] **BLOCKING**: All critical bugs must be fixed first
- [ ] All workflows must be working reliably

**Why After Bugs**:
- Can't build UI on broken foundation
- Audit found 36% workflows completely broken
- Fixing bugs first = smooth TUI development
- No painful debugging during UI integration

**Timeline**:
- **Week 1** (Oct 11-18): TUI implementation after bugs fixed
- **Week 2** (Oct 19-25): Polish, testing, integration
- **Target**: Oct 25 for production-ready TUI

---

### 🎬 Streaming Validation Strategy (BACKLOG - LOW PRIORITY)

**Status**: 📋 **BACKLOG** - Not needed for months  
**Priority**: Backlog - Focus on tool quality first  
**Timeline**: TBD (After TUI + dogfooding period)  
**Manifest**: `Projects/ACTIVE/streaming-validation-manifest.md` ✅

**Rationale for Deprioritization**:
- Tool needs to be **excellent** before showing anyone
- Currently only 27% of workflows working
- Need months of personal dogfooding first
- Distribution system already complete (v0.1.0-alpha)
- Can share GitHub link anytime without streaming

**Prerequisites Before Streaming**:
- [ ] All workflows 100% working and tested
- [ ] Retro TUI complete and polished
- [ ] 3+ months of daily personal use without friction
- [ ] Tool feels "magical" to use
- [ ] Clear value proposition proven through own use

**When Ready** (Months from now):
- Use tool naturally during streams
- Let organic discovery happen
- GitHub link available in description
- No forced demos, no pressure

---

## 🛣️ Next Steps Roadmap

### Immediate Actions (Oct 9-11) - DISTRIBUTION SYSTEM IMPLEMENTATION

**Current Phase**: Implement distribution system while waiting for YouTube IP unblock

1. ✅ **Fix YouTube Template Bug** - COMPLETED 2025-10-08 (commit ac70aa2)
   - Template now uses tp.file.update_frontmatter() to inject video_id
   - Daemon has fallback parser for empty frontmatter
   - 21 YouTube notes migrated to Inbox/YouTube/
   - 3 TDD tests passing

2. ✅ **Product Vision Clarified** - COMPLETED 2025-10-09
   - Personal tool + streaming validation strategy
   - Desktop distribution (NOT web app)
   - Developer power user focus
   - Organic discovery through live streams

3. 🎯 **Distribution System Implementation** (Priority: P0) 🚀
   **Day 1-2 (Oct 9-10)**: Core Infrastructure
   - [ ] Create `.gitignore-distribution` file (30 min)
   - [ ] Create `scripts/create-distribution.sh` (2 hours)
   - [ ] Create `scripts/security-audit.py` (1 hour)
   - [ ] Test distribution creation locally (1 hour)
   
   **Day 2-3 (Oct 10-11)**: Content & Documentation
   - [ ] Build `knowledge-starter-pack/` directory (4 hours)
     - 3 permanent note examples (demonstrate AI features)
     - 2 literature note examples (YouTube workflow)
     - README files for each directory
   - [ ] Write INSTALLATION.md (15-minute setup guide)
   - [ ] Polish main README with screenshots
   - [ ] Create streaming demo workflow guide
   
   **Day 3 (Oct 11)**: Validation & Release
   - [ ] Run security audit (verify no personal data)
   - [ ] Test installation on clean environment
   - [ ] Create public GitHub repository
   - [ ] Push v0.1.0-alpha release
   - [ ] Add GitHub link to stream setup

4. **Streaming Setup Preparation** (Priority: P0) 📺
   - [ ] Create `Projects/ACTIVE/streaming-demo-workflow.md`
   - [ ] Identify 3-5 "wow moments" to show naturally
   - [ ] Test terminal output visibility (font size, colors)
   - [ ] Prepare stream overlay with GitHub link
   - [ ] Set up !inneros chat command

5. **Plan Iteration 10: Directory Organization Handler** (Priority: P1) 📋
   - Defer until after distribution system complete
   - **Estimated**: 2 hours (planning) + 3 hours (implementation)

### Upcoming Priorities

3. **Knowledge Capture System - POC** (Priority: P2) 🔥
   - [ ] Create branch: `feat/visual-capture-poc-tdd-1`
   - [ ] Voice note detection from OneDrive
   - [ ] Screenshot + voice temporal pairing (±60s)
   - [ ] Combined capture note template
   - [ ] 1-week real-world validation
   - [ ] Go/No-Go decision based on >90% pairing accuracy

3. **Smart Link Management — Iteration 6** (Priority 3)
   - [ ] Create branch: `feat/smart-link-management-undo-tdd-6`
   - [ ] Add failing tests for `UndoManager` and CLI `--undo`
   - [ ] Implement minimal undo stack with backup integration
   - [ ] Plan bidirectional link consistency and atomic operations

4. **Automated Background Daemon** (Priority 4)
   - [ ] Extract AutoProcessor into daemon controller
   - [ ] Add APScheduler for automated maintenance tasks
   - [ ] Create daemon control CLI (`inneros daemon --start/stop/status`)
   - [ ] Design macOS LaunchD service configuration
   - [ ] Test background processing and scheduling

5. **Reading Intake Pipeline** (Priority 5)
   - [ ] Extend YAML validator for `source:` and `saved_at`
   - [ ] Add literature templates + import adapters (CSV/JSON, bookmarks)
   - [ ] CLI: `--import-bookmarks`, `--process-literature`
   - [ ] Performance: <30s per item triage

6. **Phase 6 Preparation** (Background)
   - [ ] Define multi-user data model and permissions
   - [ ] API surface (read-only) and events design
   - [ ] UI scaffolding plan (analytics dashboard)

---

## 📋 Tracking

- Tests must remain 66/66 passing (baseline) or expand with new features
- Performance targets must be preserved or improved
- Maintain backward compatibility and workflow integrity
- **Architectural constraints**: All classes must be <500 LOC, <20 methods
- **Pre-development check**: Run class size audit before adding features
- **Monthly architectural review**: First Monday of each month

---

## 🔁 Backlog (Future Phases)

### Model Migration: llama3 → gpt-oss:20b 🎯 P1 (High Value, Medium Effort)
**Status**: 📋 BACKLOG - Research Complete, Manifest Ready  
**Manifest**: `Projects/ACTIVE/model-migration-gpt-oss-20b-manifest.md` ✅  
**Effort**: ~8-10 hours (JSON hardening + validation)  
**Impact**: Better AI quality (2.5x parameters), improved auto-promotion accuracy

**User Story**: "Upgrade to 20B model for better tagging, quote extraction, and quality assessment"

**Key Benefits**:
- 2.5x larger model (20B vs 8B) → better instruction following
- Native JSON mode → eliminates regex parsing failures (~15% reduction)
- Extended context (8K) → handles longer YouTube transcripts
- Local/private → maintains privacy-first architecture
- Instant rollback → environment variable switching

**Critical Components**:
- 🔴 `tagger.py` - JSON mode hardening required
- 🔴 `youtube_quote_extractor.py` - Schema-constrained outputs required
- 🟡 `enhancer.py` - JSON mode recommended
- 🟢 `summarizer.py` - No changes needed

**Why Medium Effort**:
- ✅ Environment variable foundation (1 hour)
- ⚠️ JSON mode hardening for brittle components (3 hours)
- ✅ Extended context Modelfile creation (1 hour)
- ✅ Per-component configuration system (1 hour)
- ⚠️ Comprehensive testing & validation (3 hours)

**Prerequisites**:
- 16GB+ VRAM or unified memory
- Ollama installed and running
- `ollama pull gpt-oss:20b`

**Next Steps**: TDD implementation when prioritized (post-sprint)

---

### YouTube CLI: User Context Integration 🎯 P2 (High Value, Low Effort)
**Status**: 📋 BACKLOG - Feature Spec Complete  
**Manifest**: `Projects/ACTIVE/youtube-cli-user-context-feature.md` ✅  
**Effort**: ~4 hours (Low complexity, existing infrastructure)  
**Impact**: More relevant quote extraction based on user's Key Takeaways

**User Story**: "Process YouTube video with AI extracting quotes that match my Key Takeaways"

**Key Features**:
- Automatic parsing of "Key Takeaways" section from notes
- Optional `--context` CLI parameter for manual override
- Uses existing `user_context` parameter (already in API!)
- Hybrid approach: auto-parse + manual override
- Zero new dependencies

**Why Low Effort**:
- ✅ `YouTubeQuoteExtractor` already has `user_context` parameter
- ✅ Just need markdown section parser + data passing
- ✅ Follows existing patterns (Smart Link Management, Tag Enhancement)
- ✅ No breaking changes to existing functionality

**Next Steps**: TDD Iteration 4 when prioritized

---

## 📋 Next Priorities

### ✅ Recently Completed
- **Quality Audit Bug Fixes** (Oct 12, 2025) - ✅ **COMPLETE**
  - 4/5 bugs fixed in 25 minutes (Bug #1, #2, #4, #5)
  - Branch: `fix/quality-audit-bug-remediation` → merged to main
  - Lessons: `Projects/COMPLETED-2025-10/quality-audit-bug-remediation-lessons-learned-2025-10-12.md`

### Immediate Actions

1. **Note Lifecycle Status Management - FULL SPRINT** (P0 - ACTIVE) 🚀
   - **Sprint Scope**: FULL (PBI-001 through PBI-005 including auto-promotion)
   - **Timeline**: 6-8 hours total
   - **Deliverables**:
     - PBI-001: Status update bug fix (60 min)
     - PBI-002: Directory integration (90 min)
     - PBI-004: Auto-promotion system ⭐ (2-3 hours)
     - PBI-003: Safe file moves (30 min)
     - PBI-005: Repair orphaned notes (60 min)
   - **Planning**: `Projects/ACTIVE/PBI-PLANNING-SESSION-2025-10-14.md` ✅
   - **Manifest**: `Projects/ACTIVE/note-lifecycle-status-management.md` ✅
   - **Flowcharts**: `Projects/ACTIVE/workflow-diagrams/10-note-lifecycle-complete.md` ✅
   - **Implementation**: `Projects/ACTIVE/workflow-enhancement-directory-integration.md` ✅

2. **Circuit Breaker & Rate Limit Protection** (4-5 days)
   - Prevents catastrophic incidents (like YouTube IP ban)
   - Multi-layer protection: circuit breakers, budget enforcer, anomaly detection
   - Manifest: `Projects/ACTIVE/circuit-breaker-rate-limit-protection-manifest.md`

3. **Streaming Validation** (Ongoing)
   - Demonstrate InnerOS during live coding streams
   - Organic discovery strategy (see `Projects/ACTIVE/streaming-validation-manifest.md`)
   - Build audience organically through authentic use

### Future Phases
- **Phase 7**: Packaging, distribution, monitoring, configuration
- **Phase 8**: Mobile/voice integrations, multi-modal AI, plugin architecture
- **Phase 9**: Multi-user collaboration, team features, enterprise deployment

---

Version: 3.0  
Next Review: Weekly during Phase 6 preparation  
Status: Active Development → Knowledge Graph & Multi-User Foundations
