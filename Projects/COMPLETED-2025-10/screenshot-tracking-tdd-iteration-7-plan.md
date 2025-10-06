# TDD Iteration 7: Processed Screenshot Tracking System

**Date**: 2025-09-30  
**Status**: 🔴 RED Phase (Planning)  
**Branch**: `feat/screenshot-tracking-tdd-iteration-7`

## Objective
Implement tracking system to prevent reprocessing of already-handled screenshots, enabling "unprocessed only" workflow.

## User Story
**As a** daily screenshot processor  
**I want** the system to skip already-processed screenshots  
**So that** I don't waste time/API calls on duplicate OCR analysis

## Success Criteria
- ✅ Track processed screenshots in persistent storage
- ✅ Skip screenshots that have already been processed
- ✅ Report statistics (new vs already-processed)
- ✅ Provide --force flag to reprocess if needed
- ✅ Maintain backward compatibility with existing workflow

## Technical Design

### P0: Core Tracking System
1. **ProcessedScreenshotTracker** class
   - Store processed screenshot paths with timestamps
   - JSON file storage: `.screenshot_processing_history.json`
   - Methods: `is_processed()`, `mark_processed()`, `get_history()`

2. **Integration Points**
   - `EveningScreenshotProcessor.scan_todays_screenshots()` - filter processed
   - `EveningScreenshotProcessor.process_evening_batch()` - mark as processed
   - Statistics in results: `new_screenshots`, `already_processed`, `skipped`

3. **CLI Flag**
   - `--force` flag to reprocess all screenshots regardless of history

### Storage Format
```json
{
  "processed_screenshots": {
    "Screenshot_20250927_131418_Threads.jpg": {
      "processed_at": "2025-09-30T20:15:04",
      "daily_note": "daily-screenshots-2025-09-30.md",
      "file_hash": "sha256:abc123..."
    }
  },
  "version": "1.0"
}
```

## Test Plan (RED Phase)

### Test 1: `test_tracker_initialization`
- Initialize tracker with empty history
- Verify JSON file creation
- Check default structure

### Test 2: `test_mark_screenshot_processed`
- Mark a screenshot as processed
- Verify entry in history
- Check timestamp format

### Test 3: `test_is_processed_detection`
- Mark screenshot as processed
- Verify `is_processed()` returns True
- Verify unprocessed screenshot returns False

### Test 4: `test_filter_unprocessed_screenshots`
- Given list with mix of processed/unprocessed
- Filter to unprocessed only
- Verify correct subset returned

### Test 5: `test_force_flag_bypasses_tracking`
- Mark screenshots as processed
- Use --force flag
- Verify all screenshots included (no filtering)

### Test 6: `test_statistics_reporting`
- Process mixed batch (some already processed)
- Verify results include: `new_screenshots`, `already_processed`, `skipped`

### Test 7: `test_history_persistence`
- Mark screenshots processed
- Create new tracker instance
- Verify history loads from disk

### Test 8: `test_concurrent_safety`
- Simulate concurrent writes
- Verify no data corruption
- Check file locking

## Performance Targets
- History lookup: <10ms per screenshot
- Mark processed: <50ms including disk write
- Filter 100 screenshots: <100ms

## Integration Safety
- Must not break existing `--evening-screenshots` command
- Backward compatible with existing daily notes
- Graceful handling if history file is missing/corrupt

## Implementation Steps
1. ✅ Commit current work (DONE)
2. 🔴 RED: Write failing tests
3. 🟢 GREEN: Implement minimal tracker
4. 🔵 REFACTOR: Extract utilities, optimize
5. 📝 COMMIT: Document lessons learned

## Next After This
- TDD Iteration 8: Individual screenshot processing (POC integration)
- Enhanced metadata (claims extraction, quote analysis)
