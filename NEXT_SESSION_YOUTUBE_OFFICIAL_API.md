# Next Session Prompt: YouTube Official API v3 Implementation

Let's create a new branch for the next feature: YouTube Official API v3 Fetcher Implementation. We want to perform TDD framework with red, green, refactor phases, followed by git commit and lessons learned documentation. This equals one iteration.

## Updated Execution Plan (focused P0/P1)

**Branch**: `feat/youtube-official-api-fetcher-tdd-iteration-1`

**Context**: Migrating from unofficial YouTube transcript scraping to official YouTube Data API v3. Current network is 100% rate-limited (0/4 attempts succeeded with unofficial method). API key validated and working on same rate-limited network. This is a **hard deprecation** - removing unofficial scraping entirely and requiring API key for YouTube features going forward.

I'm following the guidance in `.windsurf/rules/updated-development-workflow.md` and `Projects/ACTIVE/youtube-official-api-integration-manifest.md` (critical path: Replace IP-based scraping with quota-based official API to unblock YouTube automation).

## Current Status

**Completed**:
- ✅ Rate Limit Handler (TDD Iteration 1): 12/12 tests passing, exponential backoff validated
- ✅ YouTube Handler (TDD Iteration 9): Daemon integration complete, 170 tests passing
- ✅ API Key Setup: YouTube Data API v3 key validated, working on rate-limited network
- ✅ Planning: Comprehensive manifest created, approach clarified (single new file)
- ✅ Dependencies: google-api-python-client installed and tested
- ✅ Documentation: README.md and README-ACTIVE.md updated

**In progress**: 
- Creating `YouTubeOfficialAPIFetcher` class in `development/src/ai/youtube_official_api_fetcher.py`
- Implementing same interface as existing `YouTubeTranscriptFetcher` for drop-in compatibility
- Writing comprehensive test suite in `development/tests/unit/ai/test_youtube_official_api_fetcher.py`

**Lessons from last iteration (Rate Limit Handler)**:
- TDD methodology delivers production-ready code with 100% confidence (12/12 tests)
- Interface abstraction enables swappable implementations
- Comprehensive error handling critical for external APIs
- Metrics tracking essential for debugging and monitoring
- Validation on real data (rate-limited network) proves design
- Configuration validation prevents operational issues
- Structured logging accelerates troubleshooting

## P0 — Critical/Unblocker (YouTube Automation)

**Create YouTubeOfficialAPIFetcher Class** (replacing unofficial scraping):

1. **Interface Compatibility**: Implement same methods as `YouTubeTranscriptFetcher`
   - `fetch_transcript(video_id: str) -> dict`: Fetch via YouTube Data API v3 captions endpoint
   - `format_for_llm(transcript: list) -> str`: Format with MM:SS timestamps (reuse existing logic)
   - Return format MUST match existing fetcher for downstream compatibility

2. **API Integration**: YouTube Data API v3 captions workflow
   - `captions.list(part='snippet', videoId=video_id)`: Get available caption tracks (50 units)
   - `captions.download(id=caption_id, tfmt='srt')`: Download transcript (200 units)
   - Parse SRT format → normalize to `[{'text': '...', 'start': 0.0, 'duration': 2.5}, ...]`
   - Prefer manual transcripts over auto-generated (same as unofficial)

3. **Quota Management**: Track API usage
   - Each video = 250 units (50 + 200)
   - Free tier = 10,000 units/day (~40 videos)
   - Track `self.quota_used` per session
   - Log quota consumption for monitoring

4. **Error Handling**: YouTube API-specific errors
   - `HttpError 403`: Quota exceeded, API disabled, or key restrictions
   - `HttpError 404`: Video not found or captions unavailable
   - `HttpError 400`: Invalid video ID or key format
   - Map to semantic exceptions: `TranscriptNotAvailableError`, `InvalidVideoIdError`, `QuotaExceededError`

5. **API Key Validation**: Secure configuration
   - Read from environment variable `YOUTUBE_API_KEY`
   - Validate key format on initialization
   - Provide helpful error messages if missing/invalid
   - Never log or expose actual key value

**Update YouTubeFeatureHandler** (minor change):

1. **Remove Unofficial Fetcher**: Delete import and usage of `YouTubeTranscriptFetcher`
2. **Use Official Fetcher**: `self.fetcher = YouTubeOfficialAPIFetcher(api_key=os.getenv('YOUTUBE_API_KEY'))`
3. **Validate API Key**: Fail fast with clear message if `YOUTUBE_API_KEY` not set
4. **Update Tests**: Modify `test_youtube_feature_handler.py` to use official fetcher

**Acceptance Criteria**:
- ✅ 8+ tests passing (basic fetch, no captions, quota tracking, error handling, API key validation, format compatibility)
- ✅ Successfully fetches transcript on rate-limited network (validation test with real video)
- ✅ Output format 100% compatible with existing quote extractor and note enhancer
- ✅ Quota tracking accurate (250 units per video)
- ✅ Error messages clear and actionable for users

## P1 — Production Hardening (Reliability)

**Extract Quota Tracker Utility**:
- `QuotaTracker` class: Track daily usage, predict capacity, reset at midnight
- Thread-safe for concurrent requests
- Persistent storage (optional): Save to file for daemon restarts

**Enhanced Error Messages**:
- API key not set: Link to setup documentation
- Quota exceeded: Show remaining capacity, reset time
- Video unavailable: Distinguish between private/deleted/no-captions

**Monitoring Integration**:
- Expose quota metrics via `YouTubeFeatureHandler.get_metrics()`
- Log quota consumption at INFO level
- Alert when approaching daily limit (80%)

**Acceptance Criteria**:
- ✅ Quota tracker accurate across multiple requests
- ✅ Error messages include troubleshooting steps
- ✅ Metrics visible in daemon logs

## P2 — Future Enhancements (Post-MVP)

**Multiple API Key Rotation**: Round-robin across keys for higher quotas
**Cache Transcripts**: Store fetched transcripts to avoid re-fetching
**Fallback Strategy**: Try multiple caption languages if preferred not available
**Cost Tracking**: Estimate costs if user exceeds free tier

## Task Tracker

- [In progress] P0-1: Create YouTubeOfficialAPIFetcher class with interface compatibility
- [Pending] P0-2: Implement captions.list and captions.download API calls
- [Pending] P0-3: Parse SRT format and normalize to standard format
- [Pending] P0-4: Add comprehensive error handling for YouTube API errors
- [Pending] P0-5: Update YouTubeFeatureHandler to use official fetcher only
- [Pending] P0-6: Validate output format compatibility with existing pipeline
- [Pending] P1-1: Extract QuotaTracker utility class
- [Pending] P1-2: Enhance error messages with troubleshooting steps
- [Pending] P1-3: Integrate metrics with daemon monitoring

## TDD Cycle Plan

**Red Phase** (30 minutes):
Write 8-10 failing tests:
1. `test_fetch_transcript_success`: Happy path with real API call (mocked)
2. `test_fetch_transcript_no_captions`: Video with transcripts disabled
3. `test_fetch_transcript_invalid_video_id`: Malformed video ID
4. `test_quota_tracking`: Verify 250 units charged per video
5. `test_api_key_validation`: Missing or invalid API key
6. `test_format_for_llm_compatibility`: Output matches existing fetcher format
7. `test_error_classification`: HttpError mapped to semantic exceptions
8. `test_prefer_manual_transcripts`: Choose manual over auto-generated
9. `test_handle_quota_exceeded`: Graceful failure when quota hit
10. `test_integration_with_feature_handler`: End-to-end with YouTubeFeatureHandler

**Green Phase** (90 minutes):
Minimal implementation to pass all tests:
1. Create `youtube_official_api_fetcher.py` with `YouTubeOfficialAPIFetcher` class
2. Implement `__init__(api_key)`: Validate key, build YouTube API client
3. Implement `fetch_transcript(video_id)`: Call captions.list → captions.download → parse SRT
4. Implement `format_for_llm(transcript)`: Reuse existing timestamp formatting or create compatible
5. Add error handling: HttpError → semantic exceptions
6. Track quota: Increment by 250 per successful fetch
7. Update `feature_handlers.py`: Remove unofficial, use official fetcher
8. Update existing tests: Mock official fetcher instead of unofficial

**Refactor Phase** (45 minutes):
Extract utilities and polish:
1. Extract `QuotaTracker` utility class (track usage, predict capacity)
2. Extract `SRTParser` utility (parse SRT format → normalized transcript)
3. Extract `YouTubeAPIErrorHandler` utility (HttpError → semantic exceptions)
4. Add comprehensive docstrings with usage examples
5. Enhance error messages with troubleshooting steps
6. Add structured logging with quota context
7. Validate ADR-001 compliance (< 500 LOC per file)

## Next Action (for this session)

**Start RED Phase**: Write failing tests in `development/tests/unit/ai/test_youtube_official_api_fetcher.py`

Key test structure:
```python
class TestYouTubeOfficialAPIFetcher:
    def test_fetch_transcript_success(self, mocker):
        """Test successful transcript fetch via YouTube Data API v3"""
        # Mock captions.list() and captions.download()
        # Assert correct API calls made
        # Assert output format matches existing fetcher
        
    def test_quota_tracking(self, mocker):
        """Verify 250 units charged per video (50 list + 200 download)"""
        # Fetch transcript
        # Assert quota_used incremented by 250
        
    def test_api_key_validation(self):
        """Test API key missing or invalid"""
        # Initialize without YOUTUBE_API_KEY env var
        # Assert raises clear error with setup instructions
```

**Environment Setup**:
```bash
# API key already set in ~/.zshrc
export YOUTUBE_API_KEY='AIzaSyDbzJLcSZRGAIaC1Wdulmku8KTdYV4P2Zw'

# Dependencies already installed
# google-api-python-client==2.108.0
# google-auth-httplib2==0.1.1
# google-auth-oauthlib==1.1.0
```

**Reference Files**:
- Existing fetcher: `development/src/ai/youtube_transcript_fetcher.py` (interface to match)
- Feature handler: `development/src/automation/feature_handlers.py` (integration point)
- Manifest: `Projects/ACTIVE/youtube-official-api-integration-manifest.md` (full plan)
- Rate limit handler: `development/src/automation/youtube_rate_limit_handler.py` (retry patterns)

Would you like me to implement the RED phase now (write 8-10 failing tests for YouTubeOfficialAPIFetcher) in small, reviewable commits?

---

**Expected Outcome**: After this iteration (3.5 hours), YouTube Handler will use official API exclusively, solving rate limiting permanently. Users will need to set up API key (one-time, 30 min) but get reliable transcript fetching with predictable quota management.
