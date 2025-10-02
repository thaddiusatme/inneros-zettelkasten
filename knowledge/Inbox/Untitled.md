Let's create a new branch for the next feature: **Visual Capture POC - Mobile Screenshot Processing (TDD Iteration 1)**. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

## Updated Execution Plan (focused P0/P1)

**Context**: Screenshot processing system now has complete tracking (prevents reprocessing), batch workflow works end-to-end. Current system processes batches of screenshots into daily notes; need individual processing for mobile-first deep processing with rich context analysis and semantic filenames.

I'm following the guidance in **Windsurf Rules v4 (InnerOS)** (critical path: **Individual screenshot deep processing with contextual filenames and rich metadata**).

## Current Status

**Completed - TDD Iteration 7**: 
- ✅ **RED Phase**: 8 comprehensive failing tests for [ProcessedScreenshotTracker](cci:2://file:///Users/thaddius/repos/inneros-zettelkasten/development/src/cli/screenshot_tracking.py:32:0-204:43)
- ✅ **GREEN Phase**: All 8 tests passing (100% success rate)
- ✅ **REFACTOR Phase**: Extracted optional filelock with graceful degradation, clean class structure
- ✅ **Real Data Validation**: Tested with 1,470 actual screenshots, 17 from last 7 days
- ✅ **Integration**: Tracking integrated into batch workflow with --force flag support
- ✅ **Git Commits**: 5 commits (TDD → Integration → Rename → Cleanup)
- ✅ **Lessons Learned**: Documented in [Projects/ACTIVE/screenshot-tracking-tdd-iteration-7-plan.md](cci:7://file:///Users/thaddius/repos/inneros-zettelkasten/Projects/ACTIVE/screenshot-tracking-tdd-iteration-7-plan.md:0:0-0:0)

**Completed - Refactoring**:
- ✅ Renamed `--evening-screenshots` → `--screenshots` for clarity
- ✅ [EveningScreenshotProcessor](cci:2://file:///Users/thaddius/repos/inneros-zettelkasten/development/src/cli/evening_screenshot_processor.py:54:0-1072:95) → [ScreenshotProcessor](cci:2://file:///Users/thaddius/repos/inneros-zettelkasten/development/src/cli/screenshot_processor.py:53:0-1103:95)
- ✅ All files renamed with `git mv` (history preserved)

**Branch**: `feat/samsung-screenshot-real-ocr-integration-tdd-6` (clean working tree)

**Lessons from TDD Iteration 7**:
1. **Real data validation critical**: Testing with 1,470 screenshots caught edge cases
2. **Tracking ROI immediate**: Already preventing 4 duplicate API calls in test runs
3. **Naming matters**: "Evening" was misleading (processes last 7 days, not just today)
4. **Graceful degradation pattern**: Optional filelock with fallback no-op works perfectly
5. **TDD velocity**: 8 tests → GREEN in <30 minutes with proven patterns

## P0 — Individual Screenshot Processing (Critical for Mobile Workflow)

**Main P0 Task**: Individual Screenshot Deep Processing Workflow (TDD Iteration 8)
- Create `--process-screenshot <path>` CLI command for single-file processing
- Generate contextual filenames using OCR content (e.g., `visual-20251001-0852-twitter-thread-knowledge-graphs.md`)
- Extract rich context: claims, quotes, categories, related_notes
- Render into individual note template (not daily note batch)
- Mark as processed in tracking system (reuse existing tracker)

**Secondary P0 Task**: CLI Integration
- Wire up new command to existing [workflow_demo.py](cci:7://file:///Users/thaddius/repos/inneros-zettelkasten/development/src/cli/workflow_demo.py:0:0-0:0)
- Support direct file path input (for iOS Shortcuts integration)
- Progress indicators for single-file processing

**Acceptance Criteria**:
- ✅ 8-10 passing tests for individual processing workflow
- ✅ Individual screenshot → standalone note in Inbox/
- ✅ Filename generated from OCR content (semantic naming)
- ✅ Rich metadata extraction (claims/quotes/categories)
- ✅ Integration with existing tracker (prevents reprocessing)
- ✅ Real data test: Process 1 actual Samsung screenshot successfully
- ✅ Performance: <45s per screenshot (within batch processing benchmarks)

## P1 — Template & Smart Links (High Priority)

**P1 Task 1**: Template Enhancement
- Create `individual-screenshot.md` template in `knowledge/Templates/`
- Include: source, captured_at, claims, quotes, categories, related_notes
- Follow existing template patterns from batch system

**P1 Task 2**: Smart Link Integration
- Suggest related notes using semantic similarity (reuse connection discovery)
- Auto-insert top 3-5 connections
- Preserve user control with validation step

**P1 Task 3**: Mobile Workflow Testing
- Test with iOS Shortcuts workflow (manual simulation)
- Verify file path handling
- Test error scenarios (missing file, invalid format)

**Acceptance Criteria**:
- ✅ Template renders consistently
- ✅ Smart links generated automatically
- ✅ Mobile workflow path validated

## P2 — Future Enhancements (After MVP)

**P2 Task 1**: Batch vs Individual Detection
- Auto-detect if screenshot already in batch note
- Offer to extract/promote to individual note

**P2 Task 2**: Category Auto-Tagging
- AI-generated category tags from visual content
- Integration with existing smart tagging system

**P2 Task 3**: Duplicate Screenshot Detection
- Hash-based duplicate detection using existing tracker
- Warn before reprocessing same visual content

## Task Tracker

- [✅ Completed] TDD-7: Screenshot tracking system (RED → GREEN → REFACTOR)
- [✅ Completed] Integration: Tracking into batch workflow  
- [✅ Completed] Refactor: Rename to `--screenshots` (5 git commits)
- [✅ Completed] Git cleanup: All changes committed, working tree clean
- [In progress] TDD-8: Individual screenshot processing (NEXT)
- [Pending] TDD-9: Template system for individual notes
- [Pending] TDD-10: Smart link suggestions for individual notes
- [Pending] TDD-11: Mobile workflow integration testing

## TDD Cycle Plan (Iteration 8)

**Red Phase**: 
- Write failing tests for `IndividualScreenshotProcessor.process_single(screenshot_path)`
- Test contextual filename generation from OCR content (e.g., extract key terms → kebab-case)
- Test rich context extraction (claims, quotes, categories from visual content)
- Test individual note template rendering
- Test tracker integration (mark individual screenshots as processed)
- Test error handling (missing file, OCR failure, invalid paths)
- Target: ~8-10 tests covering core workflow

**Green Phase**: 
- Implement minimal `IndividualScreenshotProcessor` class
- Wire up existing `ContextualFilenameGenerator` (already exists)
- Connect `RichContextAnalyzer` for metadata extraction (already exists)
- Use `TemplateNoteRenderer` for note creation (already exists)
- Integrate with [ProcessedScreenshotTracker](cci:2://file:///Users/thaddius/repos/inneros-zettelkasten/development/src/cli/screenshot_tracking.py:32:0-204:43) (reuse from TDD-7)
- All tests passing with minimal implementation

**Refactor Phase**: 
- Extract common patterns between batch and individual processing
- Improve error handling and logging consistency
- Add performance benchmarking (<45s target)
- Document integration patterns
- Create lessons learned doc

## Next Action (for this session)

1. **Review existing implementation**: Read `development/src/cli/individual_screenshot_utils.py` to see what's already built
2. **Create TDD Iteration 8 plan**: Write `Projects/ACTIVE/individual-screenshot-tdd-iteration-8-plan.md` with detailed test specifications
3. **RED Phase Start**: Create `development/tests/unit/test_individual_screenshot_processor.py` with 8-10 failing tests
4. **Real data prep**: Identify 1 unprocessed screenshot from last 7 days (13 available) for validation testing

Would you like me to start by reviewing `individual_screenshot_utils.py` to understand existing classes and then create the TDD Iteration 8 plan with comprehensive test specifications?