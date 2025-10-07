# YouTube CLI Integration - TDD Iteration 2: GREEN Phase Session Prompt

**Session Type**: Implementation (GREEN Phase)  
**Estimated Duration**: 90-120 minutes  
**Branch**: `feat/youtube-cli-integration-tdd-iteration-2` (continue)  
**Prerequisites**: RED Phase complete (commit: `2606d8f`)

## 🎯 Session Objective

Implement YouTubeProcessor integration and CLI workflows to achieve **11/16 additional tests passing** (total 16/16).

## 📊 Current State (RED Phase Complete)

### Test Results: 5/16 Passing (31%)
```
✅ PASSING (5 tests):
- CLI argument parsing validation (--process-youtube-note, --process-youtube-notes)
- Help text verification
- Argument compatibility checks

❌ FAILING (11 tests - Expected in RED):
- Single note processing workflow (4 tests)
- Batch processing (2 tests)
- Preview mode (1 test)
- Quality filtering (1 test)
- Category selection (1 test)
- Export functionality (2 tests)
```

### Files Ready for GREEN Phase
```
✅ development/tests/unit/test_youtube_cli_integration.py (485 lines)
   - 16 comprehensive tests with proper mocks
   - Real test data: 4 sample YouTube notes in temp vault
   - Mock strategy: YouTubeProcessor + YouTubeNoteEnhancer

✅ development/src/cli/workflow_demo.py
   - CLI arguments integrated (lines 735-745, 812-817)
   - Stub implementations ready (lines 1510-1518)
   - Need: Replace NotImplementedError with real logic

✅ development/src/ai/youtube_note_enhancer.py (TDD Iteration 1)
   - Complete enhancement engine
   - QuotesData structure defined
   - EnhanceResult with success/error tracking
   - Backup/rollback system ready
```

## 🚀 GREEN Phase Implementation Plan

### Phase 1: Single Note Processing (Priority: P0)
**Target**: Make 4 tests pass

```python
# File: development/src/cli/workflow_demo.py
# Lines: ~1510-1580 (replace stub)

elif args.process_youtube_note:
    # 1. Validate note path exists
    # 2. Check if YouTube note (source: youtube)
    # 3. Check if already processed (ai_processed: true)
    # 4. Fetch transcript with YouTubeProcessor
    # 5. Extract quotes with AI
    # 6. Enhance note with YouTubeNoteEnhancer
    # 7. Return user-friendly success/error messages
```

**Tests to Pass**:
- ✅ `test_process_single_youtube_note_success`
- ✅ `test_process_single_note_file_not_found`
- ✅ `test_process_single_note_not_youtube_note`
- ✅ `test_process_single_note_transcript_unavailable`

**Implementation Checklist**:
- [ ] Import YouTubeProcessor (need to check if exists from TDD Iteration 1)
- [ ] Import YouTubeNoteEnhancer (already complete)
- [ ] Add note validation helper function
- [ ] Add YouTube type checking (frontmatter `source: youtube`)
- [ ] Add processing status check (`ai_processed` field)
- [ ] Integrate transcript fetching with error handling
- [ ] Integrate quote extraction with error handling
- [ ] Call YouTubeNoteEnhancer.enhance_note()
- [ ] Format success/error messages with emoji
- [ ] Return proper exit codes (0 for success, 1 for error)

### Phase 2: Batch Processing (Priority: P0)
**Target**: Make 2 tests pass

```python
# File: development/src/cli/workflow_demo.py
# Lines: ~1515-1600 (replace stub)

elif args.process_youtube_notes:
    # 1. Scan knowledge/Inbox/ for *.md files
    # 2. Filter by source: youtube
    # 3. Filter by ai_processed: false (or missing)
    # 4. Process each note with progress reporting
    # 5. Track successes, failures, skipped
    # 6. Generate summary report
```

**Tests to Pass**:
- ✅ `test_batch_process_youtube_notes`
- ✅ `test_batch_process_filters_already_processed`

**Implementation Checklist**:
- [ ] Create Inbox scanner function
- [ ] Add YouTube note filter (check frontmatter)
- [ ] Add processing status filter
- [ ] Add progress indicator (emoji + count)
- [ ] Process notes in loop with error handling
- [ ] Track statistics (processed, skipped, failed)
- [ ] Generate summary report
- [ ] Support --format json output

### Phase 3: Preview Mode (Priority: P1)
**Target**: Make 1 test pass

```python
# Enhancement to both commands
if args.preview:
    # Show what would be inserted without modifying
    # Display: quotes, insertion point, preview
    # Return without calling enhance_note()
```

**Test to Pass**:
- ✅ `test_preview_mode_no_modification`

**Implementation Checklist**:
- [ ] Add preview mode to single note processing
- [ ] Show quotes that would be inserted
- [ ] Show insertion point in note
- [ ] Add "Preview mode - no changes made" message
- [ ] Verify original file unchanged

### Phase 4: Quality Filtering (Priority: P1)
**Target**: Make 1 test pass

```python
# Pass --min-quality to YouTubeProcessor
quotes = processor.extract_quotes(
    transcript=transcript,
    min_relevance=args.min_quality or 0.7
)
```

**Test to Pass**:
- ✅ `test_quality_filtering`

**Implementation Checklist**:
- [ ] Pass --min-quality to quote extraction
- [ ] Filter quotes by relevance score
- [ ] Show filtered count in output
- [ ] Validate quality threshold (0.0-1.0)

### Phase 5: Category Selection (Priority: P1)
**Target**: Make 1 test pass

```python
# Parse --categories argument
categories = args.categories.split(',') if args.categories else ['all']

# Filter quotes by selected categories
filtered_quotes = filter_by_categories(quotes, categories)
```

**Test to Pass**:
- ✅ `test_category_selection`

**Implementation Checklist**:
- [ ] Parse comma-separated categories
- [ ] Validate category names (key-insights, actionable, notable, definitions)
- [ ] Filter QuotesData by selected categories
- [ ] Show category selection in output

### Phase 6: Export Functionality (Priority: P0)
**Target**: Make 2 tests pass

```python
# Support --export <file> for batch processing
if args.export:
    export_path = Path(args.export)
    if args.format == "json":
        # Export JSON format
    else:
        # Export markdown report
```

**Tests to Pass**:
- ✅ `test_batch_export_to_file`
- ✅ `test_json_output_format`

**Implementation Checklist**:
- [ ] Add export path handling
- [ ] Generate JSON export format
- [ ] Generate markdown report format
- [ ] Write to file with error handling
- [ ] Show export success message

## 🔍 Critical Implementation Details

### YouTubeProcessor Integration
**Question**: Does YouTubeProcessor exist from TDD Iteration 1?

**Check Required**:
```bash
# Look for YouTubeProcessor class
find development/src -name "*youtube*processor*.py"
grep -r "class YouTubeProcessor" development/src/
```

**If NOT exists**: Need to create minimal YouTubeProcessor stub:
```python
class YouTubeProcessor:
    def fetch_transcript(self, url: str) -> str:
        # Use youtube-transcript-api
        pass
    
    def extract_quotes(self, transcript: str, min_relevance: float = 0.7) -> QuotesData:
        # Use LLM to extract quotes
        pass
```

**If EXISTS**: Import and use directly

### Note Validation Pattern
```python
def validate_youtube_note(note_path: Path) -> tuple[bool, str]:
    """Validate if note is a YouTube note ready for processing.
    
    Returns:
        (is_valid, error_message)
    """
    if not note_path.exists():
        return False, f"File not found: {note_path}"
    
    try:
        fm, _ = parse_frontmatter(note_path.read_text())
        
        # Check source type
        if fm.get('source') != 'youtube':
            return False, "Not a YouTube note (source must be 'youtube')"
        
        # Check if already processed
        if fm.get('ai_processed', False):
            return False, "Already processed (ai_processed: true)"
        
        # Check for YouTube URL
        if not fm.get('url'):
            return False, "Missing YouTube URL in frontmatter"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error parsing note: {e}"
```

### Progress Reporting Pattern
```python
def process_batch_with_progress(notes: list[Path], processor, enhancer):
    """Process batch of notes with progress reporting."""
    total = len(notes)
    results = {
        'processed': [],
        'skipped': [],
        'failed': []
    }
    
    for idx, note_path in enumerate(notes, 1):
        print(f"\n🔄 Processing {idx}/{total}: {note_path.name}")
        
        # Validate note
        is_valid, error_msg = validate_youtube_note(note_path)
        if not is_valid:
            print(f"   ⏭️  Skipped: {error_msg}")
            results['skipped'].append({'path': str(note_path), 'reason': error_msg})
            continue
        
        try:
            # Process note
            # ... (implementation)
            results['processed'].append({'path': str(note_path), 'quotes': len(quotes)})
            print(f"   ✅ Enhanced with {len(quotes)} quotes")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results['failed'].append({'path': str(note_path), 'error': str(e)})
    
    return results
```

## 📋 Session Execution Checklist

### Setup (5 minutes)
- [ ] Review RED phase test results
- [ ] Verify branch: `feat/youtube-cli-integration-tdd-iteration-2`
- [ ] Check if YouTubeProcessor exists or needs creation
- [ ] Run tests to confirm 5/16 passing baseline

### Phase 1: Single Note Processing (30 minutes)
- [ ] Replace stub implementation
- [ ] Add note validation
- [ ] Integrate YouTubeProcessor (or create stub)
- [ ] Integrate YouTubeNoteEnhancer
- [ ] Add error handling
- [ ] Run tests: Target 9/16 passing (4 new)

### Phase 2: Batch Processing (25 minutes)
- [ ] Implement Inbox scanner
- [ ] Add filtering logic
- [ ] Add progress reporting
- [ ] Generate summary report
- [ ] Run tests: Target 11/16 passing (2 new)

### Phase 3-6: Enhanced Features (30 minutes)
- [ ] Implement preview mode (1 test)
- [ ] Add quality filtering (1 test)
- [ ] Add category selection (1 test)
- [ ] Add export functionality (2 tests)
- [ ] Run tests: Target 16/16 passing ✅

### Commit GREEN Phase (10 minutes)
- [ ] Verify all 16 tests passing
- [ ] Review code quality
- [ ] Commit with descriptive message
- [ ] Update progress documentation

## 🎯 Success Criteria

**GREEN Phase Complete When**:
- ✅ All 16 tests passing (100%)
- ✅ Single note processing working with real YouTube notes
- ✅ Batch processing scanning Inbox correctly
- ✅ Preview mode functional
- ✅ Quality filtering and category selection working
- ✅ Export functionality generating files
- ✅ Clean commit with no regressions

## 💡 Implementation Tips

### 1. Start Minimal
Implement just enough to pass tests. Don't over-engineer.

### 2. Test Frequently
Run tests after each phase to catch regressions early:
```bash
python3 -m pytest tests/unit/test_youtube_cli_integration.py -v
```

### 3. Follow Existing Patterns
Reference `--fleeting-triage` and `--promote-note` implementations for:
- Progress reporting format
- Error message style
- Summary report generation
- Export functionality

### 4. Handle Errors Gracefully
Every external call should have try/except:
- Transcript fetching (YouTube API)
- Quote extraction (LLM)
- Note enhancement (file operations)

### 5. Use Helper Functions
Extract reusable logic:
- `validate_youtube_note(path)`
- `scan_inbox_for_youtube_notes(vault_path)`
- `format_processing_summary(results)`

## 📚 Reference Files

**Study these implementations**:
```python
# Fleeting note triage (similar batch processing)
development/src/cli/workflow_demo.py:1405-1433

# Note promotion (similar validation)
development/src/cli/workflow_demo.py:1435-1489

# YouTubeNoteEnhancer usage example
development/demos/test_youtube_note_enhancer_real_data.py
```

## 🚦 Next Session Start Command

```bash
# 1. Checkout branch
git checkout feat/youtube-cli-integration-tdd-iteration-2

# 2. Verify RED phase baseline
cd development
python3 -m pytest tests/unit/test_youtube_cli_integration.py -v
# Expected: 5/16 passing

# 3. Open key files
code src/cli/workflow_demo.py:1510  # Stub to replace
code src/ai/youtube_note_enhancer.py  # Reference
code tests/unit/test_youtube_cli_integration.py  # Test requirements

# 4. Start GREEN Phase implementation
# Follow the plan above, testing after each phase
```

## ⚠️ Known Challenges

### Challenge 1: YouTubeProcessor May Not Exist
**Solution**: Create minimal stub or implement basic version if needed

### Challenge 2: Transcript API Dependencies
**Solution**: May need to add `youtube-transcript-api` to requirements
Check: `grep youtube development/requirements.txt`

### Challenge 3: LLM Integration for Quote Extraction
**Solution**: Reuse existing OllamaClient patterns from TDD Iteration 1

### Challenge 4: Mock Testing with Real YouTubeProcessor
**Solution**: Tests already use `@patch` decorators - mocks are in place

## 📊 Estimated Timeline

| Phase | Duration | Tests Passing | Cumulative |
|-------|----------|---------------|------------|
| Setup & Review | 5 min | 5/16 | 5/16 |
| Phase 1: Single Note | 30 min | +4 | 9/16 |
| Phase 2: Batch | 25 min | +2 | 11/16 |
| Phase 3-6: Enhanced | 30 min | +5 | 16/16 ✅ |
| Commit & Document | 10 min | - | - |
| **Total** | **100 min** | **16/16** | **100%** |

## 🎓 Learning Objectives

By completing GREEN phase, you will have:
1. Integrated external API (YouTube) with CLI workflow
2. Implemented batch processing with progress reporting
3. Added preview/dry-run functionality
4. Created filtering and export systems
5. Demonstrated complete TDD RED → GREEN cycle

---

**Ready to implement?** 🟢  
Start with Phase 1: Single Note Processing and work through systematically.

**Questions before starting?** 💬  
- Is YouTubeProcessor already implemented?
- Are there any dependencies to install?
- Should we validate with real YouTube notes first?
