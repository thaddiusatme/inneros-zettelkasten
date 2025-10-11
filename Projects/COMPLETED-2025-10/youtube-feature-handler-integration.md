# YouTube Feature Handler Integration - TODO

**Priority**: High  
**Status**: Not Started  
**Epic**: Daemon Automation (Iterations 1-8)  
**Gap Identified**: 2025-10-08  

## 🎯 Objective

Integrate the existing YouTube CLI processor into the daemon as a feature handler, enabling automatic quote extraction from YouTube transcripts when notes are saved to Inbox.

## 📋 User Story

**As a** knowledge worker capturing YouTube content  
**I want** the daemon to automatically extract key quotes from video transcripts  
**So that** I don't have to manually run CLI commands after saving each YouTube note

**Acceptance Criteria:**
- [ ] YouTube notes in Inbox are auto-detected when saved
- [ ] Transcript is fetched and quotes extracted automatically
- [ ] Quotes are inserted into note with timestamps and context
- [ ] User's manual notes are preserved (non-destructive)
- [ ] Health metrics track YouTube processing (success/failure/time)
- [ ] Config option to enable/disable YouTube handler
- [ ] Debouncing prevents duplicate processing during editing

## 🏗️ Technical Design

### Architecture Pattern (Follow Existing Handlers)

```
YouTubeFeatureHandler (new)
    ├── Inherits from: FeatureHandler base class
    ├── Uses: YouTubeProcessor (already exists in src/cli/)
    ├── Uses: YouTubeCLIProcessor (already exists)
    └── Integrates: MetricsTracker for health monitoring

Configuration (daemon_config.yaml):
    youtube_handler:
        enabled: true
        vault_path: ./knowledge
        min_quality: 0.7
        max_quotes: 7
        categories: ["key_insights", "actionable", "definitions"]
        processing_timeout: 60
```

### Files to Create/Modify

**New Files:**
1. `development/src/automation/youtube_handler.py` (~200 LOC)
   - YouTubeFeatureHandler class
   - Event detection (source: youtube, ai_processed: false)
   - Integration with YouTubeProcessor

**Modified Files:**
1. `development/src/automation/feature_handlers.py`
   - Add YouTubeFeatureHandler import and registration
   
2. `development/src/automation/daemon.py`
   - Add YouTube handler initialization in `_setup_feature_handlers()`
   
3. `development/src/automation/config.py`
   - Add YouTubeHandlerConfig dataclass

4. `development/daemon_config.yaml`
   - Add youtube_handler configuration section

**Test Files:**
1. `development/tests/unit/automation/test_youtube_handler.py` (~150 LOC)
   - Test handler initialization
   - Test event detection
   - Test processing success/failure
   - Test metrics tracking
   - Test config validation

## 🔄 Implementation Phases

### Phase 1: Configuration (30 min)
- [ ] Add YouTubeHandlerConfig to config.py
- [ ] Add youtube_handler section to daemon_config.yaml
- [ ] Write config validation tests

### Phase 2: Handler Implementation (45 min)
- [ ] Create YouTubeFeatureHandler class
- [ ] Implement event detection logic (check source: youtube)
- [ ] Integrate YouTubeProcessor for quote extraction
- [ ] Add metrics tracking (events_processed, avg_time, failures)
- [ ] Implement error handling and logging

### Phase 3: Daemon Integration (30 min)
- [ ] Register handler in feature_handlers.py
- [ ] Add initialization in daemon._setup_feature_handlers()
- [ ] Test handler lifecycle (start/stop)

### Phase 4: Testing (45 min)
- [ ] Write comprehensive unit tests
- [ ] Test with real YouTube notes from Inbox
- [ ] Verify health monitoring integration
- [ ] Test debouncing (don't reprocess already processed notes)

### Phase 5: Documentation (15 min)
- [ ] Update FEATURE-HANDLERS.md
- [ ] Update daemon_config.yaml with comments
- [ ] Create usage examples

**Total Estimated Time**: ~2.5 hours

## 🧪 Test Plan

### Unit Tests
- [ ] Handler initializes with valid config
- [ ] Handler detects YouTube notes (source: youtube)
- [ ] Handler skips non-YouTube notes
- [ ] Handler skips already processed notes (ai_processed: true)
- [ ] Handler tracks metrics correctly
- [ ] Handler handles processing failures gracefully

### Integration Tests
- [ ] Live test with real YouTube notes
- [ ] Verify quotes inserted without overwriting user content
- [ ] Verify health endpoint includes YouTube handler metrics
- [ ] Verify Prometheus metrics export

## 📊 Success Metrics

- **Functionality**: Daemon auto-processes YouTube notes on file save
- **Performance**: Processes note in <60 seconds (including transcript fetch)
- **Reliability**: >90% success rate with proper error handling
- **Non-Destructive**: 100% preservation of user's manual notes
- **Observability**: Full metrics in health endpoint and Prometheus

## 🔗 Dependencies

**Existing Components (Already Built):**
- ✅ YouTubeProcessor (src/cli/youtube_processor.py)
- ✅ YouTubeCLIProcessor (src/cli/youtube_cli_utils.py)
- ✅ YouTubeTranscriptFetcher (src/ai/youtube_transcript_fetcher.py)
- ✅ YouTubeQuoteExtractor (src/ai/youtube_quote_extractor.py)
- ✅ Feature handler infrastructure (feature_handlers.py)
- ✅ Daemon lifecycle management (daemon.py)
- ✅ Health monitoring (health.py)

**External Dependencies:**
- ✅ youtube-transcript-api (already installed)

## 🚨 Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YouTube API rate limiting | Processing failures | Implement exponential backoff, queue system |
| Long processing time (>60s) | Daemon blocking | Make async, use timeout configuration |
| Malformed LLM responses | Quote extraction fails | Already has JSON repair logic in quote extractor |
| Overwriting user content | Data loss | Use YouTubeNoteEnhancer (already has non-destructive insertion) |

## 📝 Related Files

**Existing YouTube System:**
- `development/src/cli/youtube_cli.py` - Manual CLI
- `development/src/cli/youtube_processor.py` - Core processor
- `development/src/ai/youtube_transcript_fetcher.py` - Transcript fetching
- `development/src/ai/youtube_quote_extractor.py` - Quote extraction with LLM
- `development/src/cli/YOUTUBE_CLI_README.md` - Usage documentation

**Daemon Handler Examples:**
- `development/src/automation/feature_handlers.py` - Screenshot & SmartLink handlers
- `development/src/automation/feature_handler_utils.py` - Base utilities

**Configuration:**
- `development/src/automation/config.py` - Config dataclasses
- `development/daemon_config.yaml` - Active daemon config

## 💡 Future Enhancements

After core integration:
- [ ] Batch processing queue for multiple YouTube notes
- [ ] Retry failed extractions with exponential backoff
- [ ] Video metadata extraction (duration, views, publish date)
- [ ] Custom template selection per note
- [ ] Parallel processing for multiple videos

---

**Created**: 2025-10-08  
**Assignee**: TBD  
**Estimated Effort**: 2.5 hours (TDD approach)  
**Blocked By**: None (all dependencies exist)  
**Blocks**: Full automation workflow for YouTube content capture
