# Templater YouTube Hook Installation Guide

## Phase 2.1: Templater Integration Setup

This guide explains how to integrate the YouTube processing hook with your Obsidian Templater setup.

## Step 1: Configure Templater Plugin

1. Open Obsidian Settings → Templater
2. Enable "User Scripts" if not already enabled
3. Set "Script files folder location" to: `.obsidian/scripts`
4. Restart Obsidian if prompted

## Step 2: Copy the Hook Script

The script has been created at two locations:

- **Tracked (in repo)**: `development/src/automation/templater_scripts/trigger_youtube_processing.js`
- **Working copy**: `.obsidian/scripts/trigger_youtube_processing.js`

If the working copy doesn't exist:
```bash
cp development/src/automation/templater_scripts/trigger_youtube_processing.js .obsidian/scripts/
```

## Step 3: Modify YouTube Template

Add the following code to your YouTube template at `knowledge/Templates/youtube-video.md`.

### Where to Add

Insert after the frontmatter section (after line ~106, right after the closing `%>` and blank line):

```javascript
<%*
/* ========================================
   AUTOMATIC YOUTUBE PROCESSING TRIGGER
   ======================================== */
// Trigger background processing via daemon API
// This happens automatically - no user intervention needed
const processingResult = await tp.user.trigger_youtube_processing(tp);

// Log result for debugging
if (typeof processingResult === 'string') {
    console.log('[Template] Processing queued with job_id:', processingResult);
} else if (processingResult.error) {
    console.log('[Template] Processing skipped:', processingResult.error);
    if (processingResult.error === 'daemon_offline') {
        console.log('[Template] You can process manually later with the daemon');
    }
}
%>
<!-- YouTube processing triggered automatically via API -->
```

### Full Template Structure

Your template should now have this structure:

```
<%*
// ... existing prompts and metadata fetching ...
// ... frontmatter output ...
%>

<%*
// NEW: Automatic processing trigger
const processingResult = await tp.user.trigger_youtube_processing(tp);
// ... error handling ...
%>

# <% videoTitle %>
// ... rest of template content ...
```

## Step 4: Test the Integration

### Prerequisites
1. Start the background daemon:
   ```bash
   python3 development/src/automation/daemon.py
   ```

2. Verify daemon is running:
   ```bash
   curl http://localhost:8080/health
   # Expected: {"status": "healthy"}
   ```

### Test Cases

#### Test 1: Normal Operation (Daemon Running)
1. Open Obsidian
2. Create new note from YouTube template (Cmd/Ctrl + P → "Templater: Create new note from template")
3. Enter a YouTube URL when prompted
4. Enter reason for saving when prompted
5. **Expected Results**:
   - Template completes within 2 seconds
   - Console shows: `[Templater] Job ID: youtube_...`
   - Note is created in `Inbox/YouTube/`
   - Daemon logs show: `[INFO] POST /api/youtube/process`
   - Within ~30 seconds, quotes appear in note

#### Test 2: Daemon Offline
1. Stop the daemon (Ctrl+C if running in terminal)
2. Create new note from YouTube template
3. **Expected Results**:
   - Template still completes successfully
   - Console shows: `[Templater] Unable to connect to daemon`
   - Console shows helpful message about starting daemon
   - Note is created normally but not processed
   - You can process manually later by starting daemon

#### Test 3: Invalid URL
1. Start daemon
2. Create note from template
3. Enter a non-YouTube URL
4. **Expected Results**:
   - Template handles gracefully
   - API returns 400 error
   - Console shows error but template completes

## Troubleshooting

### Script Not Found
**Error**: `tp.user.trigger_youtube_processing is not a function`

**Solution**:
1. Check Templater settings → User Scripts folder is set correctly
2. Verify script exists at `.obsidian/scripts/trigger_youtube_processing.js`
3. Restart Obsidian
4. Check Obsidian Developer Console (Ctrl+Shift+I) for errors

### Daemon Connection Errors
**Error**: `[Templater] Unable to connect to daemon`

**Solution**:
1. Start daemon: `python3 development/src/automation/daemon.py`
2. Verify it's listening: `curl http://localhost:8080/health`
3. Check firewall isn't blocking localhost:8080
4. Check daemon logs for errors

### Template Hangs/Freezes
**Cause**: Network timeout or blocking operation

**Solution**:
- The script has a 5-second timeout built in
- If still hanging, check console for errors
- Restart Obsidian as last resort

### No Quotes Added
**Cause**: Processing may have failed silently

**Solution**:
1. Check daemon logs for errors
2. Verify note has `video_url` in frontmatter
3. Check note is in queue: `curl http://localhost:8080/api/youtube/queue`
4. Manually trigger: See manual processing documentation

## Advanced: Manual Testing with cURL

You can test the API directly without Obsidian:

```bash
# 1. Start daemon
python3 development/src/automation/daemon.py

# 2. In another terminal, trigger processing
curl -X POST http://localhost:8080/api/youtube/process \
  -H "Content-Type: application/json" \
  -d '{"note_path": "Inbox/YouTube/lit-20241018-1230-test-video.md"}'

# Expected response:
# {"job_id": "youtube_Inbox/YouTube/lit-20241018-1230-test-video.md_1729267800", "message": "..."}

# 3. Check queue
curl http://localhost:8080/api/youtube/queue

# 4. Watch daemon logs for processing
```

## Next Steps

Once basic integration is working:

1. **P1 Features**: Add user notifications (see Phase 2.2)
2. **Dashboard**: Queue visualization (Phase 3)
3. **Monitoring**: Add health checks and alerting

## Support

If issues persist:
1. Check daemon logs: Look for HTTP request logs
2. Check Obsidian console: Ctrl+Shift+I → Console tab
3. Review test specification: `development/tests/manual/test_templater_youtube_hook.md`
4. Run manual tests to isolate the issue
