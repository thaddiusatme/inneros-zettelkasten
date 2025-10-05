<%*
/*------------------------------------------------------------------
  1. Get YouTube URL and Extract Video ID
------------------------------------------------------------------*/
const youtubeUrl = await tp.system.prompt("Paste YouTube URL:");
if (!youtubeUrl) {
  await tp.system.alert("Cancelled – no URL provided.");
  return;
}

// Extract video ID from URL (supports various YouTube URL formats)
let videoId = "";
try {
  const urlObj = new URL(youtubeUrl);
  
  // Standard format: youtube.com/watch?v=ID
  if (urlObj.hostname.includes("youtube.com")) {
    videoId = urlObj.searchParams.get("v");
  }
  // Short format: youtu.be/ID
  else if (urlObj.hostname.includes("youtu.be")) {
    videoId = urlObj.pathname.substring(1);
  }
  
  if (!videoId) {
    await tp.system.alert("Could not extract video ID from URL. Please check the URL format.");
    return;
  }
} catch (e) {
  await tp.system.alert("Invalid URL format: " + e.message);
  return;
}

/*------------------------------------------------------------------
  2. Build File Name & Path
------------------------------------------------------------------*/
const stamp  = tp.date.now("YYYYMMDD-HHmm");
const fname  = `youtube-${stamp}-${videoId}.md`;
const target = `Inbox/${fname}`;

/*------------------------------------------------------------------
  3. Rename & Move (with graceful error)
------------------------------------------------------------------*/
try {
  await tp.file.rename(fname);
  await tp.file.move(target);
} catch (e) {
  await tp.system.alert("Rename/Move failed – " + e.message);
  return;
}
%>
---
type: literature
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
tags: [youtube, video-notes, literature]
visibility: private
source: youtube
url: <% youtubeUrl %>
video_id: <% videoId %>
channel:
duration:
---

# Video Summary

[Auto-generated summary will appear here]

## Key Themes

- theme1
- theme2
- theme3

---

## Extracted Quotes

### 🎯 Key Insights

> [00:00] "Quote text here"
> - **Context**: Why this matters
> - **Relevance**: 0.00

### 💡 Actionable Insights

> [00:00] "Quote text here"
> - **Context**: Why this matters
> - **Relevance**: 0.00

### 📝 Notable Quotes

> [00:00] "Quote text here"
> - **Context**: Why this matters
> - **Relevance**: 0.00

### 📖 Definitions

> [00:00] "Quote text here"
> - **Context**: Why this matters
> - **Relevance**: 0.00

---

## My Notes

[Add your personal reflections and connections here]

## Related Notes

- [[related-note-1]]
- [[related-note-2]]

## Next Actions

- [ ] Review and highlight key quotes
- [ ] Connect to related permanent notes
- [ ] Consider promotion to permanent note
