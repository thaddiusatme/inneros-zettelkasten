# RED PHASE: Templater YouTube Hook Test Specification

**TDD Iteration**: Phase 2.1  
**Feature**: Automatic YouTube note processing via Templater hook  
**Status**: 🔴 RED - Tests defined, implementation pending

## Test Environment Setup

### Prerequisites
1. ✅ Obsidian with Templater plugin installed
2. ✅ Template at `knowledge/Templates/Utility/youtube.md` (or use test fixture: `development/tests/fixtures/templates/Utility/youtube.md`)
3. ✅ Background daemon running: `python3 development/src/automation/daemon.py`
4. ✅ HTTP server listening on `http://localhost:8080`

### Test Data
- **Valid YouTube URL**: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **Expected API Endpoint**: `POST http://localhost:8080/api/youtube/process`
- **Expected Response**: `{"job_id": "youtube_<note_path>_<timestamp>", "message": "..."}`

---

## P0 Critical Tests (Must Pass)

### Test 1: Basic API Call Execution
**Given**: Daemon is running  
**When**: User creates note from YouTube template  
**Then**:
- [ ] Templater hook executes without blocking template completion
- [ ] POST request sent to `/api/youtube/process` with note_path
- [ ] Response received within 1 second
- [ ] job_id returned and available to template
- [ ] Daemon logs show API request received

**Expected Console Output**:
```
[Templater] Triggering YouTube processing...
[Templater] Note path: Inbox/youtube-<timestamp>.md
[Templater] Job ID: youtube_Inbox/youtube-<timestamp>.md_1729308000
```

---

### Test 2: Daemon Offline Error Handling
**Given**: Daemon is NOT running  
**When**: User creates note from YouTube template  
**Then**:
- [ ] Template completes successfully (no crash/hang)
- [ ] Error caught gracefully (ECONNREFUSED)
- [ ] Console shows clear error message
- [ ] Returned value indicates offline state: `{error: "daemon_offline"}`
- [ ] User can still use the note normally

**Expected Console Output**:
```
[Templater] Error: Unable to connect to daemon
[Templater] Daemon may be offline. Start with: python3 development/src/automation/daemon.py
[Templater] Note created successfully (manual processing required)
```

---

### Test 3: Invalid Response Handling
**Given**: Daemon returns unexpected response format  
**When**: User creates note from YouTube template  
**Then**:
- [ ] Template completes without error
- [ ] Error logged to console with response details
- [ ] Graceful fallback: returns null or error object
- [ ] Note remains usable

---

### Test 4: Network Timeout Handling
**Given**: Daemon is slow to respond (>5 seconds)  
**When**: User creates note from YouTube template  
**Then**:
- [ ] Request times out after 5 seconds
- [ ] Template completes (doesn't hang indefinitely)
- [ ] Timeout error logged to console
- [ ] User can proceed with note

---

### Test 5: File Path Resolution
**Given**: Note created in various locations  
**When**: Template processes notes in:
  - `Inbox/youtube-test.md`
  - `Fleeting Notes/youtube-test.md`
  - Subdirectory: `Inbox/YouTube/test.md`
**Then**:
- [ ] `tp.file.path(true)` returns correct absolute path
- [ ] API receives correct note_path parameter
- [ ] Daemon can locate and process each file

---

## P1 Enhanced Tests (User Experience)

### Test 6: Successful Processing Notification (P1)
**Given**: Daemon processes note successfully  
**When**: Quotes are added to note  
**Then**:
- [ ] User sees "🎥 Processing YouTube note..." on template creation
- [ ] Polling checks queue every 2 seconds
- [ ] Success notification appears: "✅ Quotes added!"
- [ ] Polling stops after completion
- [ ] Total notification time: ~30-60 seconds

---

### Test 7: Processing Timeout Notification (P1)
**Given**: Processing takes >60 seconds  
**When**: Timeout reached  
**Then**:
- [ ] User sees "⏱️ Processing taking longer than expected"
- [ ] Polling stops after timeout
- [ ] Note still functional, quotes may appear later

---

### Test 8: Clear Offline Instructions (P1)
**Given**: Daemon offline  
**When**: Error occurs  
**Then**:
- [ ] Obsidian Notice shows clear message
- [ ] Includes actionable command to start daemon
- [ ] Template usage not blocked

---

## Performance Tests

### Test 9: API Response Time
**Target**: <1 second for API validation + queue add  
**Measurement**: Time from POST to response received  
**Pass Criteria**: 95% of requests complete in <1 second

---

### Test 10: Template Completion Time
**Target**: Template available for user input immediately  
**Measurement**: Time from template trigger to cursor ready  
**Pass Criteria**: <2 seconds regardless of API state

---

## Integration Tests

### Test 11: End-to-End Workflow
**Scenario**: Complete YouTube note lifecycle  
**Steps**:
1. Start daemon
2. Create note from template with valid URL
3. Verify API called
4. Wait for processing
5. Verify quotes added to note
**Expected**: Full workflow completes without manual intervention

---

### Test 12: Multiple Concurrent Notes
**Scenario**: Create 3 YouTube notes rapidly  
**Expected**:
- [ ] All 3 API calls succeed
- [ ] Queue handles all 3 notes
- [ ] No race conditions or conflicts
- [ ] Each note gets unique job_id

---

## Error Recovery Tests

### Test 13: Daemon Restart During Processing
**Scenario**: Daemon crashes/restarts while note in queue  
**Expected**:
- [ ] Graceful handling (note may need reprocessing)
- [ ] No corrupted note state
- [ ] Clear error/status indication

---

### Test 14: Invalid YouTube URL
**Scenario**: Template created with non-YouTube URL  
**Expected**:
- [ ] API returns error (400 Bad Request)
- [ ] Error logged but template completes
- [ ] User notified of invalid URL

---

## Acceptance Criteria Summary

**P0 Critical (Must Pass)**:
- ✅ Template triggers API call automatically
- ✅ job_id returned within 1 second
- ✅ Template completes even if daemon offline
- ✅ Console logging for debugging
- ✅ Works in Obsidian with Templater

**P1 Enhanced (Should Pass)**:
- ⏳ User notifications (processing, completion, timeout)
- ⏳ Clear offline error messages
- ⏳ Polling for completion status

**P2 Optional (Nice to Have)**:
- ⏳ Queue visualization in dashboard
- ⏳ Retry on transient failures
- ⏳ Template placeholder updates

---

## Manual Test Execution Checklist

### Setup
- [ ] Install Templater plugin in Obsidian
- [ ] Configure Templater user scripts folder: `.obsidian/scripts/`
- [ ] Copy `trigger_youtube_processing.js` to scripts folder
- [ ] Start daemon: `python3 development/src/automation/daemon.py`
- [ ] Verify HTTP server: `curl http://localhost:8080/health`

### Execution
- [ ] Run Test 1-5 (P0 Critical)
- [ ] Run Test 6-8 (P1 Enhanced) 
- [ ] Run Test 9-10 (Performance)
- [ ] Run Test 11-12 (Integration)
- [ ] Run Test 13-14 (Error Recovery)

### Results Documentation
- [ ] Record pass/fail for each test
- [ ] Capture console logs for failures
- [ ] Document any unexpected behavior
- [ ] Note performance metrics

---

## Implementation Requirements (Derived from Tests)

Based on these tests, the implementation must include:

1. **Core Functionality**:
   - Fetch POST to `http://localhost:8080/api/youtube/process`
   - Extract note path: `tp.file.path(true)`
   - Parse JSON response for job_id
   - Return job_id or error object

2. **Error Handling**:
   - Catch network errors (ECONNREFUSED)
   - Handle invalid response formats
   - Implement 5-second timeout
   - Never throw errors (always complete template)

3. **Logging**:
   - Log all API calls to console
   - Log errors with context
   - Log success with job_id

4. **P1 Enhancements**:
   - Import Obsidian Notice API
   - Implement polling for completion
   - Show status notifications
   - Timeout after 60 seconds

---

**Next Step**: Implement `trigger_youtube_processing.js` to pass all P0 tests (GREEN phase)
