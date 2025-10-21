# YouTube Transcript API Migration Guide

## Version History & Breaking Changes

### v0.6.2 → v1.2.3 (Oct 2025)

**What Broke:**
1. ❌ `YouTubeTranscriptApi.list_transcripts(video_id)` → ✅ `YouTubeTranscriptApi().list(video_id)`
2. ❌ `transcript.fetch()` returned list → ✅ Returns `FetchedTranscript` object with `.snippets`
3. ❌ Error class `TooManyRequests` → ✅ Split into `RequestBlocked` and `IpBlocked`

**How We Fixed It:**
- Updated `src/ai/youtube_transcript_fetcher.py`
- Changed method calls and data access patterns
- Updated error handling imports

**Commit Reference:** See git history for detailed changes

---

## Testing for Compatibility

### Before Upgrading

1. **Run compatibility tests:**
   ```bash
   pytest development/tests/test_youtube_transcript_api_compat.py -v
   ```

2. **Check current version:**
   ```bash
   pip3 show youtube-transcript-api
   ```

### After Upgrading

1. **Run full test suite:**
   ```bash
   pytest development/tests/ -v
   ```

2. **Test transcript fetching:**
   ```bash
   python3 << 'EOF'
   import sys
   sys.path.insert(0, 'development')
   from src.ai.youtube_transcript_fetcher import YouTubeTranscriptFetcher
   
   fetcher = YouTubeTranscriptFetcher()
   result = fetcher.fetch_transcript("h6fcK_fRYaI")  # Test video
   print(f"✅ Success! Got {len(result['transcript'])} entries")
   EOF
   ```

3. **Test YouTube API server:**
   ```bash
   # Start server
   python3 development/run_youtube_api_server.py
   
   # In another terminal, test endpoint
   curl -X POST http://localhost:8080/api/youtube/process \
     -H "Content-Type: application/json" \
     -d '{"note_path": "knowledge/Inbox/YouTube/YOUR-TEST-NOTE.md.md"}'
   ```

---

## Version Requirements

**Minimum:** `youtube-transcript-api>=1.2.3`  
**Maximum:** `<2.0.0` (to avoid future breaking changes)

**Why Version Pinning?**
- The library has a history of breaking API changes between minor versions
- Pinning to 1.x ensures stability while allowing patches
- Tests will catch if v2.x introduces incompatibilities

---

## Future Upgrade Checklist

When upgrading `youtube-transcript-api`:

- [ ] Check release notes for breaking changes
- [ ] Update version in `development/requirements.txt`
- [ ] Run compatibility tests
- [ ] Test with real YouTube videos
- [ ] Update this migration guide if changes needed
- [ ] Update `test_youtube_transcript_api_compat.py` for new API
- [ ] Test YouTube API server end-to-end
- [ ] Update `src/ai/youtube_transcript_fetcher.py` if needed

---

## Known Issues

### Issue: XML Parsing Error ("no element found: line 1, column 0")

**Cause:** YouTube blocking requests or library too old  
**Solution:** Upgrade to v1.2.3+

### Issue: "AttributeError: 'YouTubeTranscriptApi' object has no attribute 'list_transcripts'"

**Cause:** Using old API methods with new library version  
**Solution:** Update code to use `.list()` instead of `.list_transcripts()`

### Issue: Import error for `TooManyRequests`

**Cause:** Error class renamed in v1.2.3+  
**Solution:** Import `RequestBlocked` and `IpBlocked` instead

---

## Related Files

- `development/src/ai/youtube_transcript_fetcher.py` - Main integration
- `development/tests/test_youtube_transcript_api_compat.py` - Compatibility tests
- `development/requirements.txt` - Version specifications

---

**Last Updated:** 2025-10-20  
**Current Stable Version:** 1.2.3
