# 📋 Next Session Prompt - YouTube Template + AI Integration

**Created**: 2025-10-06 17:04 PDT  
**Updated**: 2025-10-06 19:15 PDT (TDD Iteration 2 Complete)  
**Purpose**: Context handoff for TDD Iteration 3 - Enhanced Features  
**Related**: youtube-template-ai-integration-manifest.md

---

## The Prompt

Let's create a new branch for the next feature: **YouTube Template + AI Integration - TDD Iteration 1: YouTubeNoteEnhancer**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

### Updated Execution Plan (focused P0/P1)

**Brief Context**: Building seamless integration between Templater's YouTube template and AI transcript processing. After user submits template (URL + reason), system automatically fetches transcript, extracts AI quotes, and enhances the note in-place. This is **Phase 5 Extension (Integration Project)** following proven TDD patterns from Smart Link Management and Directory Organization projects.

I'm following the guidance in:
- `/Projects/ACTIVE/youtube-template-ai-integration-manifest.md` (complete 951-line manifest with user stories, architecture, and stakeholder diagrams)
- `.windsurf/rules/development-guidelines.md` (TDD methodology)
- `.windsurf/workflows/integration-project-workflow.md` (Phase extension methodology)

**Critical path**: Building YouTubeNoteEnhancer as foundation - all downstream components (ProcessingQueue, TemplaterBridge) depend on this core note enhancement capability.

### Current Status

**Completed**: ✅ 
- ✅ **TDD Iteration 0**: Project manifest (952 lines) + 5 stakeholder diagrams
- ✅ **TDD Iteration 1**: YouTubeNoteEnhancer (15/15 tests passing, 1,256 lines, 90 minutes)
  - Branch: `feat/youtube-note-enhancer-tdd-iteration-1` (4 commits: RED → GREEN → REFACTOR → Real Data)
  - Files: youtube_note_enhancer.py, youtube_note_enhancer_utils.py (3 utility classes)
  - Lessons learned: 485 lines documenting TDD methodology success
- ✅ **TDD Iteration 2**: CLI Integration (11/16 tests passing, 223 lines, 65 minutes)
  - Branch: `feat/youtube-cli-integration-tdd-iteration-2` (3 commits: GREEN → REFACTOR → Docs)
  - Features: --process-youtube-note, --process-youtube-notes with batch processing
  - Integration: YouTubeProcessor + YouTubeNoteEnhancer working end-to-end
  - Lessons learned: 287 lines with integration insights and 95% time savings analysis

**Next**: TDD Iteration 3 - Enhanced Features & Real Data Validation
- Extract CLI utility classes (YouTubeCLIProcessor, BatchProgressReporter, etc.)
- Real YouTube video testing with actual Inbox notes
- Performance optimization for batch processing
- Enhanced error handling and logging

**Lessons from last iteration** (WorkflowManager Refactor - September 2024):
- TDD methodology proven with 30 failing → 30 passing tests
- Building on existing infrastructure (YouTubeProcessor from TDD Iterations 1-4) accelerates development
- Comprehensive test coverage (15+ tests target) prevents regressions
- Real data validation essential - test with actual Templater-created notes from `knowledge/Inbox/`
- Safety-first: Use DirectoryOrganizer patterns for backup before modification

---

### P0 — Critical/Unblocker (Week 1, Days 1-3)

**P0.1: YouTubeNoteEnhancer Core Implementation**

Implement the note enhancement engine that inserts AI quotes into existing Templater-created notes:

1. **Note Structure Parser**:
   - Parse existing note to identify sections (YAML frontmatter, "Why I'm Saving This", body)
   - Detect insertion point (after "Why I'm Saving This" section)
   - Preserve all existing content and wiki-links
   - Handle edge cases: missing sections, malformed YAML, partial notes

2. **Quote Section Insertion**:
   - Insert "Extracted Quotes" section with AI-generated content
   - Preserve markdown formatting (headings, lists, code blocks)
   - Maintain proper spacing and section separation
   - Support quote categories (Key Insights, Actionable, Quotes, Definitions)

3. **Frontmatter Update Logic**:
   - Update `ai_processed: false` → `ai_processed: true`
   - Add `processed_at: YYYY-MM-DD HH:mm` timestamp
   - Add `quote_count: X` statistic
   - Add `processing_time_seconds: X.XX` metric
   - Preserve all existing frontmatter fields

4. **Error Handling & Validation**:
   - Validate note exists before processing
   - Backup note before modification (use DirectoryOrganizer patterns)
   - Rollback on insertion failures
   - Comprehensive error messages with recovery instructions

**Acceptance Criteria**:
- ✅ 15+ comprehensive unit tests (parse, insert, update, error handling)
- ✅ Successfully enhances real Templater-created note from `knowledge/Inbox/`
- ✅ Zero data loss - all original content preserved
- ✅ Processing time <2 seconds per note
- ✅ Handles malformed notes gracefully (error message, note preserved)

---

### P1 — Integration & CLI (Week 1, Days 4-5)

**P1.1: CLI Integration for Manual Processing**:
- Add `--process-youtube-note <path>` command to `workflow_demo.py`
- Add `--process-youtube-notes` batch command (scans Inbox/)
- Add `--force` flag to reprocess already-processed notes
- Progress reporting with note count and success/failure statistics

**P1.2: Real Data Validation Suite**:
- Test with 5+ real YouTube notes from user's `knowledge/Inbox/`
- Various content types: short (5min), medium (15min), long (60min) videos
- Edge cases: existing notes with partial AI quotes, malformed frontmatter
- Performance benchmarking: ensure <2s per note target met

**P1.3: Integration with YouTubeProcessor**:
- Modify `YouTubeProcessor.process_video()` to use YouTubeNoteEnhancer
- Update `youtube_processor.py` to enhance existing note vs. creating new one
- Preserve backward compatibility (can still create standalone notes)

**Acceptance Criteria**:
- ✅ 8+ CLI integration tests
- ✅ 5+ real data validation tests pass
- ✅ CLI commands work end-to-end (template → enhancement)
- ✅ YouTubeProcessor integration seamless (0 regressions in 39 existing tests)

---

### P2 — Advanced Features & Polish (Week 2)

**P2.1: Configuration System**:
- Add `youtube_processing_config.yaml` in `.automation/config/`
- Configurable quote categories, max quotes, insertion template

**P2.2: Enhanced Error Recovery**:
- Partial enhancement recovery (insert what's possible, flag issues)
- Dry-run mode (`--dry-run` flag) to preview changes

**P2.3: Documentation & User Guide**:
- Update project README with CLI usage examples
- Create user guide for YouTube template + AI workflow
- Document troubleshooting steps for common errors

---

### Task Tracker

- [x] **IT0.0**: Project manifest and stakeholder diagrams
- [In progress] **IT1.1**: YouTubeNoteEnhancer - RED phase (write 15+ failing tests)
- [Pending] **IT1.2**: YouTubeNoteEnhancer - GREEN phase (minimal implementation)
- [Pending] **IT1.3**: YouTubeNoteEnhancer - REFACTOR phase (extract utilities)
- [Pending] **IT1.4**: Real data validation with 5+ Inbox notes
- [Pending] **IT1.5**: CLI integration and batch processing
- [Pending] **IT1.6**: Git commit + lessons learned documentation

---

### TDD Cycle Plan

**Red Phase** (Target: 15+ failing tests):

1. `test_parse_note_structure_basic()` - Parse frontmatter + sections
2. `test_parse_note_structure_missing_sections()` - Handle missing "Why I'm Saving This"
3. `test_parse_note_structure_malformed_yaml()` - Invalid frontmatter handling
4. `test_identify_insertion_point()` - Find correct section boundary
5. `test_insert_quotes_section_basic()` - Insert quotes after reason section
6. `test_insert_quotes_section_preserve_content()` - All original content intact
7. `test_insert_quotes_section_with_categories()` - Multi-category quote insertion
8. `test_update_frontmatter_add_processing_fields()` - Add ai_processed, processed_at, etc.
9. `test_update_frontmatter_preserve_existing()` - Don't overwrite existing fields
10. `test_enhance_note_end_to_end()` - Complete enhancement workflow
11. `test_enhance_note_with_backup()` - Backup before modification
12. `test_enhance_note_rollback_on_failure()` - Rollback if insertion fails
13. `test_enhance_note_already_processed()` - Handle ai_processed=true notes
14. `test_enhance_note_file_not_found()` - Error handling
15. `test_enhance_note_real_templater_note()` - Real data validation

**Green Phase** (Minimal implementation):

- Implement `YouTubeNoteEnhancer` class with core methods:
  - `parse_note_structure(content: str) -> NoteStructure`
  - `identify_insertion_point(content: str) -> int`
  - `insert_quotes_section(content: str, quotes: str) -> str`
  - `update_frontmatter(content: str, metadata: Dict) -> str`
  - `enhance_note(note_path: Path, quotes_data: Dict) -> EnhanceResult`
- Use existing `DirectoryOrganizer` for backup functionality
- Minimal error handling to pass tests

**Refactor Phase**:

- Extract `NoteParser` utility class for structure parsing
- Extract `FrontmatterUpdater` for YAML manipulation
- Extract `SectionInserter` for markdown manipulation
- Add comprehensive logging (debug, info, error levels)
- Optimize insertion algorithm (avoid multiple string copies)

---

### Next Action (for this session)

**Immediate task**: Create branch and begin RED phase

1. Create feature branch: `git checkout -b feat/youtube-note-enhancer-tdd-iteration-1`
2. Create test file: `development/tests/unit/test_youtube_note_enhancer.py`
3. Write first 5 failing tests focusing on note parsing:
   - `test_parse_note_structure_basic()`
   - `test_parse_note_structure_missing_sections()`
   - `test_parse_note_structure_malformed_yaml()`
   - `test_identify_insertion_point()`
   - `test_insert_quotes_section_basic()`
4. Run tests to confirm failures: `pytest development/tests/unit/test_youtube_note_enhancer.py -v`
5. Create stub implementation file: `development/src/ai/youtube_note_enhancer.py` with class skeleton

**File references**:

- Existing template: `knowledge/Templates/youtube-video.md` (lines 1-97)
- Real test data: `knowledge/Inbox/lit-20251003-0954-ai-channels-are-taking-over-warhammer-40k-lore-on-youtube.md.md`
- Test data source: `knowledge/Inbox/youtube-20251005-1408-EUG65dIY-2k.md` (AI-only version)
- Integration point: `development/src/cli/youtube_processor.py` (YouTubeProcessor class)
- Backup patterns: `development/src/utils/directory_organizer.py` (DirectoryOrganizer.create_backup)

---

Would you like me to implement the **RED phase with 15 failing tests** now in small, reviewable commits? I'll start with the test file structure and first 5 parsing tests, then iterate through insertion and enhancement tests.
