---
type: literature
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
tags: [youtube, video-notes, literature]
visibility: private
source: youtube
url: 
video_id: 
channel: 
duration: 
---
<%*
/*------------------------------------------------------------------
  1. Get Video ID
------------------------------------------------------------------*/
const videoId = await tp.system.prompt("YouTube Video ID (from URL)?");
if (!videoId) {
  await tp.system.alert("Cancelled – no video ID provided.");
  return;
}

/*------------------------------------------------------------------
  2. Build File Name & Path
------------------------------------------------------------------*/
const stamp  = tp.date.now("YYYYMMDD-HHmm");
const fname  = `youtube-${stamp}-${videoId}.md`;
const target = `Inbox/${fname}`;

/*------------------------------------------------------------------
  3. Set URL
------------------------------------------------------------------*/
const videoUrl = `https://www.youtube.com/watch?v=${videoId}`;

/*------------------------------------------------------------------
  4. Rename & Move (with graceful error)
------------------------------------------------------------------*/
try {
  await tp.file.rename(fname);
  await tp.file.move(target);
} catch (e) {
  await tp.system.alert("Rename/Move failed – " + e.message);
  return;
}

/*------------------------------------------------------------------
  5. Update Frontmatter
------------------------------------------------------------------*/
tR += `\nurl: ${videoUrl}`;
tR += `\nvideo_id: ${videoId}`;
%>

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
