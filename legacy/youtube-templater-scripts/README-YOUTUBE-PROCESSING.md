# YouTube Note Processing - Updated Manual Trigger

## Current Issue
The previous automatic trigger had timing issues. The "Replace templates" command doesn't execute JavaScript code.

## ✅ Working Solution

### Method 1: Copy/Paste Trigger (Fastest)

1. **Create YouTube note** from template (as normal)
2. **Copy this line**: `<% await tp.user.simple_youtube_trigger(tp) %>`
3. **Paste it at the very end** of your note (below everything else)
4. **Press Enter** - it will execute and show a notification

### Method 2: Insert Template Trigger

1. **Create YouTube note** from template
2. **Cmd+P** → "Templater: Insert Template" → Select "**Simple YouTube Trigger**"
3. **Done!** Processing starts automatically

### Method 3: Manual API Call

If scripts don't work:
1. Create note from template
2. Run this in browser console:
```javascript
fetch('http://localhost:8080/api/youtube/process', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({note_path: "knowledge/Inbox/YouTube/YOUR-NOTE.md.md"})
}).then(r=>r.json()).then(console.log)
```

---

## Files

- `simple_youtube_trigger.js` - **Current working script**
- `process_current_youtube_note.js` - Advanced version (may need setup)
- `trigger_youtube_processing.js` - Original automatic trigger (deprecated)

---

## Troubleshooting

### "User script not found"
- Ensure Templater user scripts are enabled
- Settings → Community Plugins → Templater → Enable "User Script Functions"

### Server offline
```bash
python3 development/run_youtube_api_server.py
```

### Template doesn't execute
- Try Method 1 (copy/paste) - it's most reliable
- Use Method 2 (insert template) as backup

---

**Pro tip**: Method 1 (copy/paste) is actually the fastest once you get used to it!
