---
type: project-manifest
created: 2025-10-15 16:55
status: planning
priority: P1
tags: [youtube-workflow, auto-promotion, integration, workflow-automation]
epic: YouTube + Auto-Promotion Integration
estimated_duration: 5-7 hours
---

# YouTube + Auto-Promotion Integration Project Manifest

**Created**: 2025-10-15 16:55  
**Epic**: Unified YouTube Knowledge Capture Workflow  
**Priority**: P1 (High Value - Workflow Completion)  
**Status**: Planning → Ready for Implementation

---

## 🎯 Vision

Create a seamless workflow where:
1. User finds YouTube video and adds personal notes
2. User flips `ready_to_process: true` when ready
3. AI processes video (transcript + quotes + analysis)
4. System merges AI content with user notes
5. Auto-promotion immediately moves to `Literature Notes/YouTube/` if quality >= 0.7

**Result**: Zero-friction knowledge capture from video sources with quality-gated organization.

---

## 📊 Current State

### Existing Systems
- ✅ YouTube Processor (transcript fetching, quote extraction, formatting)
- ✅ Auto-Promotion System (quality-based note promotion)
- ✅ CoreWorkflowCLI (process-inbox, auto-promote commands)
- ✅ YouTubeCLI (batch-process, process-note commands)

### Current Workflow (Disconnected)
```
User creates YouTube note
  ↓
Manually runs: youtube_cli.py process-note
  ↓
Note gets transcript + quotes
  ↓
Note stays in Inbox/YouTube/ (no auto-promotion)
  ↓
User must manually move to Literature Notes/
```

### Gaps
- No approval mechanism (`ready_to_process` flag)
- YouTube notes not integrated with auto-promotion
- No quality scoring for YouTube content
- No automatic organization to `Literature Notes/YouTube/`
- 37 existing YouTube notes lack proper frontmatter

---

## 🎯 Target State

### Integrated Workflow
```
User creates note with YouTube URL + personal notes
  ↓
Sets: ready_to_process: true
  ↓
AI processes (2-5 min): transcript + quotes + summary
  ↓
Merges AI content with user notes (preserves user content)
  ↓
Calculates quality_score on merged content
  ↓
Auto-promotion runs immediately
  ↓
If quality >= 0.7: Moves to Literature Notes/YouTube/
  ↓
Status: promoted
```

---

## 📋 Implementation Plan

### Phase 1: Metadata Schema Extension (1 hour)
**Goal**: Add new fields to support approval workflow

**Tasks**:
- [ ] Add `ready_to_process: boolean` field to schema
- [ ] Add `video_title: string` field
- [ ] Add `video_duration: string` field  
- [ ] Add `transcript_length: number` field
- [ ] Update metadata validation logic
- [ ] Add type: `literature-youtube` support

**Files Modified**:
- `development/src/utils/frontmatter.py` (schema)
- `development/src/ai/metadata_repair_engine.py` (validation)

**Test Coverage**:
- [ ] Test `ready_to_process` field parsing
- [ ] Test `literature-youtube` type validation
- [ ] Test new video metadata fields

---

### Phase 2: YouTube Processor Enhancement (2 hours)
**Goal**: Add approval mechanism and quality scoring

**Tasks**:
- [ ] Modify YouTubeProcessor to check `ready_to_process` flag
- [ ] Skip processing if `ready_to_process: false`
- [ ] Preserve user notes during AI enrichment (don't overwrite)
- [ ] Add quality score calculation for YouTube notes
  - Consider: transcript quality, user notes depth, combined value
- [ ] Set `status: ai_processed` after successful processing
- [ ] Set `status: processing_failed` on errors (keep `ready_to_process: true`)
- [ ] Add retry logic for rate limits

**Files Modified**:
- `development/src/cli/youtube_processor.py`
- `development/src/ai/youtube_note_enhancer.py` (quality scoring)

**Quality Score Algorithm**:
```python
def calculate_youtube_quality_score(note):
    # Base score from AI analysis of merged content
    content_quality = ai_analyze_quality(note.full_content)
    
    # Boost for user contribution
    user_notes_length = len(note.user_notes)
    user_boost = min(0.2, user_notes_length / 500 * 0.2)
    
    # Boost for transcript quality
    transcript_quality = assess_transcript_coherence(note.transcript)
    
    final_score = (
        content_quality * 0.6 +
        transcript_quality * 0.2 +
        user_boost * 0.2
    )
    
    return min(1.0, final_score)
```

**Test Coverage**:
- [ ] Test `ready_to_process: false` skips processing
- [ ] Test `ready_to_process: true` triggers processing
- [ ] Test user notes preservation
- [ ] Test quality score calculation
- [ ] Test error state handling

---

### Phase 3: Auto-Promotion Integration (1 hour)
**Goal**: Connect YouTube notes to auto-promotion system

**Tasks**:
- [ ] Update `PromotionEngine.auto_promote_ready_notes()` to handle YouTube notes
- [ ] Add special handling for `type: literature-youtube`
- [ ] Create `Literature Notes/YouTube/` subdirectory structure
- [ ] Route YouTube notes to `Literature Notes/YouTube/` on promotion
- [ ] Ensure quality threshold (0.7) applies to YouTube notes
- [ ] Trigger auto-promotion immediately after YouTube processing

**Files Modified**:
- `development/src/ai/promotion_engine.py`

**Promotion Logic**:
```python
def auto_promote_ready_notes(self, dry_run=False, quality_threshold=0.7):
    for note in inbox_notes:
        # Existing logic...
        
        # Special handling for YouTube notes
        if note.type == 'literature-youtube':
            if note.status != 'ai_processed':
                skip_note("YouTube note not AI-processed yet")
                continue
            
            target_dir = self.literature_dir / "YouTube"
            target_dir.mkdir(exist_ok=True)
            
            # Promote if meets quality threshold
            if note.quality_score >= quality_threshold:
                move_note(note, target_dir)
                update_status(note, "promoted")
```

**Test Coverage**:
- [ ] Test YouTube notes are detected
- [ ] Test routing to `Literature Notes/YouTube/`
- [ ] Test quality threshold enforcement
- [ ] Test immediate promotion after AI processing
- [ ] Test dry-run mode for YouTube notes

---

### Phase 4: Migration Script for Existing Notes (1 hour)
**Goal**: Update 37 existing YouTube notes with new frontmatter

**Tasks**:
- [ ] Create migration script `migrate_youtube_notes.py`
- [ ] Scan `knowledge/Inbox/YouTube/*.md`
- [ ] Add `ready_to_process: false` to all existing notes
- [ ] Add `type: literature-youtube` if missing
- [ ] Add `status: draft` if missing
- [ ] Generate migration report

**Script**:
```python
# development/demos/migrate_youtube_notes.py

def migrate_youtube_note(note_path):
    """Add new frontmatter fields to existing YouTube note."""
    content = read_file(note_path)
    frontmatter, body = parse_frontmatter(content)
    
    # Add new fields
    if 'ready_to_process' not in frontmatter:
        frontmatter['ready_to_process'] = False
    
    if 'type' not in frontmatter:
        frontmatter['type'] = 'literature-youtube'
    
    if 'status' not in frontmatter:
        frontmatter['status'] = 'draft'
    
    # Write back
    new_content = build_frontmatter(frontmatter, body)
    write_file(note_path, new_content)
    
    return {'note': note_path.name, 'fields_added': [...]}
```

**Test Coverage**:
- [ ] Test migration on sample YouTube notes
- [ ] Test idempotency (running twice doesn't break)
- [ ] Test report generation

---

### Phase 5: CLI Integration & UX (1 hour)
**Goal**: Update CLI commands for new workflow

**Tasks**:
- [ ] Add `--check-ready` flag to youtube_cli.py (only process if approved)
- [ ] Update batch-process to respect `ready_to_process` flag
- [ ] Add status reporting: "3 notes ready to process, 5 awaiting approval"
- [ ] Add `--force` flag to override checkmarks (for batch migration)
- [ ] Update help text and examples

**CLI Commands**:
```bash
# Process only approved YouTube notes
youtube_cli.py batch-process --check-ready

# Show what's waiting for approval
youtube_cli.py status

# Force process all (migration scenario)
youtube_cli.py batch-process --force

# Process single note (respects ready_to_process)
youtube_cli.py process-note note.md
```

**Test Coverage**:
- [ ] Test `--check-ready` flag respects checkmarks
- [ ] Test status command shows approval states
- [ ] Test `--force` overrides checkmarks

---

### Phase 6: End-to-End Testing (1 hour)
**Goal**: Validate complete workflow with real data

**Test Scenarios**:

1. **New YouTube Note Workflow**:
   ```
   Create note with URL + notes
   → Set ready_to_process: true
   → Run youtube_cli.py process-note
   → Verify AI enrichment
   → Verify quality_score calculated
   → Run auto-promote
   → Verify moved to Literature Notes/YouTube/
   ```

2. **Batch Processing**:
   ```
   Create 5 YouTube notes
   → Set 3 with ready_to_process: true
   → Run batch-process
   → Verify only 3 processed
   → Verify quality-based promotion
   ```

3. **Error Handling**:
   ```
   Create note with invalid URL
   → Set ready_to_process: true
   → Run process-note
   → Verify status: processing_failed
   → Fix URL
   → Retry processing
   → Verify success
   ```

4. **Existing Notes Migration**:
   ```
   Run migration script on 37 notes
   → Verify all have ready_to_process: false
   → Manually flip 3 to true
   → Run batch-process
   → Verify selective processing
   ```

---

## 🎯 Success Criteria

### Functional Requirements
- [x] User can set `ready_to_process: true` to trigger processing ✅
- [ ] AI processing preserves user notes
- [ ] Quality score calculated on merged content
- [ ] Auto-promotion runs immediately after AI processing
- [ ] YouTube notes route to `Literature Notes/YouTube/`
- [ ] Error states allow retry without losing data
- [ ] Batch processing respects approval flags

### Technical Requirements
- [ ] All tests passing (existing + new tests)
- [ ] Zero regressions in current workflows
- [ ] Migration script updates 37 existing notes
- [ ] Documentation updated (CLI help, README)

### Performance Requirements
- [ ] YouTube processing: <5 minutes per note
- [ ] Auto-promotion: <1 second
- [ ] Batch processing: <10 minutes for 10 notes

### User Experience Requirements
- [ ] Clear status indicators (draft, processing, ai_processed, promoted)
- [ ] Informative error messages
- [ ] Dry-run preview mode available
- [ ] CLI output shows approval status

---

## 📊 Decisions Made

### Gap 1: Quality Score Timing
**Decision**: Option A - Calculate after AI processing on merged content  
**Rationale**: Single score, simpler logic, reflects final value

### Gap 2: State Management
**Decision**: States: draft → processing → ai_processed → promoted  
**Rationale**: Clear progression, explicit intermediate states

### Gap 3: Auto-Promotion Trigger
**Decision**: Option A - Immediate after AI processing  
**Rationale**: Seamless workflow, instant gratification

### Gap 6: Existing 37 Notes
**Decision**: Option B - Update frontmatter with `ready_to_process: false`  
**Rationale**: Safe migration, user controls processing timing

### Gap 7: Error Handling
**Decision**: Option A - Clear failure state with retry  
**Rationale**: User can fix issues and retry without recreating note

### Gap 8: Batch Processing
**Decision**: Option A - Respect checkmarks by default  
**Rationale**: User control, explicit approval required

---

## 🗂️ Directory Structure (Target State)

```
knowledge/
├── Inbox/
│   ├── [regular fleeting notes]
│   └── YouTube/
│       ├── draft-video-1.md (ready_to_process: false)
│       ├── processing-video-2.md (ready_to_process: true, status: processing)
│       └── ready-video-3.md (ready_to_process: true, status: ai_processed)
│
├── Literature Notes/
│   ├── [regular literature notes]
│   └── YouTube/
│       ├── youtube-rick-astley-leadership-20251015.md (promoted)
│       └── youtube-ai-explained-20251014.md (promoted)
│
├── Fleeting Notes/
│   └── [fleeting captures]
│
└── Permanent Notes/
    └── [permanent knowledge]
```

---

## 🔧 Technical Architecture

### Component Integration
```
User edits note (ready_to_process: true)
  ↓
YouTubeCLI.process_note()
  ↓
YouTubeProcessor.process_video()
  ↓
- YouTubeTranscriptFetcher (transcript)
- ContextAwareQuoteExtractor (quotes)
- YouTubeNoteEnhancer (quality score)
  ↓
Note updated: status: ai_processed, quality_score: 0.85
  ↓
PromotionEngine.auto_promote_ready_notes()
  ↓
Note moved: Literature Notes/YouTube/
  ↓
Status updated: promoted
```

### Data Flow
```yaml
# Initial state (user created)
---
type: literature-youtube
source: youtube
url: https://youtube.com/watch?v=...
status: draft
ready_to_process: false
---
# My notes
...

# After user approval
ready_to_process: true

# During processing
status: processing

# After AI processing
status: ai_processed
quality_score: 0.85
video_title: "..."
video_duration: "10:30"
transcript_length: 5000
ai_processed: 2025-10-15T17:00:00

# After auto-promotion
status: promoted
promoted_date: 2025-10-15 17:01
```

---

## 🚀 Implementation Timeline

**Total Estimate**: 5-7 hours

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 1: Metadata Schema | 1 hour | P0 (foundation) |
| Phase 2: YouTube Processor | 2 hours | P0 (core logic) |
| Phase 3: Auto-Promotion | 1 hour | P0 (integration) |
| Phase 4: Migration Script | 1 hour | P1 (cleanup) |
| Phase 5: CLI Integration | 1 hour | P1 (UX) |
| Phase 6: E2E Testing | 1 hour | P0 (validation) |

**Critical Path**: Phase 1 → 2 → 3 → 6  
**Parallel Work**: Phase 4 and 5 can be done anytime after Phase 1

---

## 🧪 Testing Strategy

### Unit Tests (New)
- [ ] Metadata field validation (ready_to_process, video_title, etc.)
- [ ] Quality score calculation for YouTube notes
- [ ] User notes preservation during AI enrichment
- [ ] Error state handling and retry logic
- [ ] Auto-promotion routing to YouTube subdirectory

### Integration Tests (New)
- [ ] Full workflow: draft → processed → promoted
- [ ] Batch processing with mixed approval states
- [ ] Migration script on sample notes
- [ ] Error recovery scenarios

### Existing Tests (Must Pass)
- [ ] All 34 auto-promotion tests
- [ ] All YouTube processor tests
- [ ] All CLI tests

---

## 📝 Documentation Updates

### Files to Update
- [ ] README.md (add YouTube + auto-promotion workflow)
- [ ] CLI help text (youtube_cli.py, core_workflow_cli.py)
- [ ] Projects/ACTIVE/NEXT-EPIC-PLANNING-2025-10-15.md (mark as complete)

### New Documentation
- [ ] YouTube workflow guide (`docs/YOUTUBE-WORKFLOW.md`)
- [ ] Migration guide for existing notes
- [ ] Troubleshooting guide for common errors

---

## 🎓 Key Learnings to Capture

### After Implementation
- [ ] Document quality score effectiveness (does it accurately predict note value?)
- [ ] Document user experience feedback (is immediate promotion too fast?)
- [ ] Document error patterns (what are common YouTube processing failures?)
- [ ] Document performance metrics (actual processing times)

---

## ✅ Ready to Start?

**Next Steps**:
1. Review this manifest for accuracy
2. Confirm all decisions
3. Begin Phase 1: Metadata Schema Extension
4. TDD cycle: RED → GREEN → REFACTOR for each phase

**Branch**: Create `feat/youtube-auto-promotion-integration`

---

**Status**: 📋 Planning Complete - Ready for Implementation  
**Created**: 2025-10-15 16:55  
**Author**: Cascade (AI Assistant) + User Design Session
