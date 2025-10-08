---
type: bug-report
created: 2025-10-08 11:50
status: active
priority: high
severity: critical
impact: automation-blocking
tags: [bug, templater, youtube, automation, frontmatter]
related_project: youtube-handler-daemon-integration-tdd-9
---

# Bug Report: YouTube Template Leaves video_id Frontmatter Empty

## Summary
The Obsidian YouTube video template (`knowledge/Templates/youtube-video.md`) fails to populate the `video_id` field in the frontmatter, causing the YouTube automation daemon to fail processing with error: `"video_id not found in frontmatter"`.

## Discovered
- **Date**: 2025-10-08 11:48
- **Context**: Live testing of TDD Iteration 9 - YouTube Handler Daemon Integration
- **Reporter**: Development Team
- **Affected System**: YouTube Automation Daemon + Obsidian Templater Integration

## Impact
- **Severity**: CRITICAL
- **User Impact**: ALL YouTube notes created via Obsidian template fail automated processing
- **Workaround**: Manual editing required to add video_id to frontmatter
- **Automation Status**: Broken for template-generated notes

## Technical Details

### Expected Behavior
When a user creates a YouTube note using the Obsidian template:
1. User provides YouTube URL
2. Template extracts `video_id` from URL
3. **Template should populate frontmatter with `video_id: <EXTRACTED_ID>`**
4. Daemon detects note and processes automatically

### Actual Behavior
1. User provides YouTube URL
2. Template extracts `video_id` into JavaScript variable
3. **Frontmatter `video_id:` field remains EMPTY**
4. Video ID only appears in markdown body content
5. Daemon detects note but fails: `"video_id not found in frontmatter"`

### Root Cause

**File**: `knowledge/Templates/youtube-video.md`

**Problem Lines (8-10)**:
```yaml
author: 
video_id: 
channel: 
```

**Templater Script (Lines 12-97)**:
```javascript
// Extracts video ID into JavaScript variable
let videoId = "";
// ... extraction logic ...

// Fetches metadata
let channelName = "Unknown";
// ... API call ...
```

**Body Content (Line 104)**:
```markdown
- **Video ID**: `<% videoId %>`
```

**Analysis**:
- The Templater script creates JavaScript variables (`videoId`, `channelName`, `author`)
- These variables are used for markdown body content interpolation
- **The frontmatter YAML fields (lines 8-10) are static and never updated**
- Templater syntax `<% ... %>` only works in markdown content, not in YAML frontmatter
- Need different syntax for frontmatter injection

## Reproduction Steps

1. Open Obsidian with Templater plugin enabled
2. Create new note using `youtube-video.md` template
3. Enter YouTube URL when prompted: `https://www.youtube.com/watch?v=IeVxir50Q2Q`
4. Enter reason for saving
5. Inspect created note frontmatter

**Result**:
```yaml
---
video_id:    # ❌ EMPTY!
---
```

**Expected**:
```yaml
---
video_id: IeVxir50Q2Q    # ✅ Should be populated
---
```

## Evidence

### Test Case 1
**File**: `lit-20251008-1148-the-must-follow-roadmap-for-all-solo-developers.md.md`
**Created**: 2025-10-08 11:48
**Initial State**:
```yaml
video_id:    # Empty - caused daemon error
```

**Daemon Log**:
```
2025-10-08 11:48:24 [ERROR] automation.feature_handlers.YouTubeFeatureHandler: 
Exception processing lit-20251008-1148-the-must-follow-roadmap-for-all-solo-developers.md.md: 
video_id not found in frontmatter
```

**After Manual Fix**:
```yaml
video_id: IeVxir50Q2Q    # Manually added
```

**Result**: ✅ Daemon processed successfully (3 quotes added in 22.06s)

## Proposed Solution

### Option 1: Update Templater Script (Recommended)
Modify the template to inject values into frontmatter using Templater's frontmatter syntax.

**Change in template** (lines 1-11):
```yaml
---
type: literature
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
tags: [youtube, video-content]
visibility: private
source: youtube
author: <% channelName %>
video_id: <% videoId %>
channel: <% channelName %>
---
```

**Issue**: Templater may not support variable interpolation in frontmatter before script execution.

### Option 2: Use tp.file.update_frontmatter (Recommended)
Add to end of Templater script (after line 96):

```javascript
// Update frontmatter with extracted values
await tp.file.update_frontmatter({
  author: channelName,
  video_id: videoId,
  channel: channelName
});
```

### Option 3: Daemon Fallback Parser
Add fallback to YouTube handler to extract video_id from body content if frontmatter is empty:

**File**: `development/src/automation/feature_handlers.py:YouTubeFeatureHandler.handle()`

```python
video_id = frontmatter.get('video_id')
if not video_id:
    # Fallback: Extract from body content
    # Pattern: - **Video ID**: `<ID>`
    import re
    match = re.search(r'Video ID[*:]+\s*`?([a-zA-Z0-9_-]+)`?', content)
    if match:
        video_id = match.group(1)
        self.logger.info(f"Extracted video_id from body content: {video_id}")
```

## Recommended Fix Priority

**Primary**: Option 2 (Templater script update) - Fixes at source
**Secondary**: Option 3 (Daemon fallback) - Safety net for existing notes

## Affected Components

- ✅ **Obsidian Template**: `knowledge/Templates/youtube-video.md`
- ✅ **YouTube Handler**: `development/src/automation/feature_handlers.py`
- ✅ **User Workflow**: Manual note creation process
- ✅ **Automation Daemon**: All YouTube note processing

## Testing Plan

1. **Fix Template**: Update with Option 2 (tp.file.update_frontmatter)
2. **Test in Obsidian**: Create new note with fixed template
3. **Verify Frontmatter**: Check video_id field populated
4. **Daemon Test**: Let daemon process automatically
5. **Regression Test**: Ensure existing manually-fixed notes still work

## Related Issues

- TDD Iteration 9: YouTube Handler Daemon Integration (COMPLETED with workaround)
- 27 backlog YouTube notes with empty video_id fields

## Next Steps

1. [ ] Update youtube-video.md template with Option 2 fix
2. [ ] Add Option 3 fallback to daemon for robustness
3. [ ] Test fix with new note creation
4. [ ] Bulk fix 27+ existing notes with empty video_id
5. [ ] Document template usage in README
6. [ ] Add validation test for template output

## Status
- **Current**: OPEN - Workaround in place (manual editing)
- **Fix Complexity**: LOW (simple Templater API call)
- **Testing Required**: MEDIUM (Obsidian + daemon integration)
- **Urgency**: HIGH (blocks primary user workflow)

---
**Filed**: 2025-10-08 11:50
**Last Updated**: 2025-10-08 11:50
**Assignee**: Development Team
