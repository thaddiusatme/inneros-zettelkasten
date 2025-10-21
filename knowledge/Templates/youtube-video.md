<%*
/*------------------------------------------------------------------
  YOUTUBE VIDEO CAPTURE TEMPLATE - API POWERED
  Uses YouTube oEmbed API to auto-fetch metadata
  Total prompts: 2 (URL + reason why)
  
  Note: If you want more metadata (description, tags, category),
  add YouTube Data API v3 key to this template
------------------------------------------------------------------*/

// 1. Get YouTube URL (required) - PROMPT 1
const youtubeUrl = await tp.system.prompt("YouTube URL");
if (!youtubeUrl) {
  await tp.system.alert("Cancelled – no YouTube URL given.");
  return;
}

// 2. Extract video ID from various YouTube URL formats
let videoId = "";
const patterns = [
  /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&?\s]+)/,
  /youtube\.com\/watch\?.*v=([^&?\s]+)/
];

for (const pattern of patterns) {
  const match = youtubeUrl.match(pattern);
  if (match) {
    videoId = match[1];
    break;
  }
}

if (!videoId) {
  await tp.system.alert("Could not extract video ID from URL. Please check the URL format.");
  return;
}

// 3. Fetch video metadata from YouTube oEmbed API (no API key needed)
let videoTitle = "Loading...";
let channelName = "Unknown";
let thumbnailUrl = "";

try {
  const oembedUrl = `https://www.youtube.com/oembed?url=${encodeURIComponent(youtubeUrl)}&format=json`;
  const response = await fetch(oembedUrl);
  
  if (response.ok) {
    const data = await response.json();
    videoTitle = data.title || "Unknown Video";
    channelName = data.author_name || "Unknown Channel";
    thumbnailUrl = data.thumbnail_url || "";
  } else {
    await tp.system.alert("Could not fetch video metadata. Using manual entry fallback.");
    videoTitle = await tp.system.prompt("Video title (manual entry)");
    channelName = await tp.system.prompt("Channel name (manual entry)");
  }
} catch (error) {
  await tp.system.alert("API fetch failed: " + error.message + ". Using manual entry.");
  videoTitle = await tp.system.prompt("Video title (manual entry)");
  channelName = await tp.system.prompt("Channel name (manual entry)");
}

// 4. Ask why they're saving this - PROMPT 2
const quickSummary = await tp.system.prompt("Why are you saving this video?");

// 5. Build filename from video title
const slug = videoTitle.toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/(^-|-$)/g, "")
  .substring(0, 60); // Limit length

const stamp = tp.date.now("YYYYMMDD-HHmm");
const fname = `lit-${stamp}-${slug}.md`;
const target = `Inbox/YouTube/${fname}`;

// 6. Default tags
const allTags = ["youtube", "video-content"];

try {
  await tp.file.rename(fname);
  await tp.file.move(target);
} catch (e) {
  await tp.system.alert("Rename/Move failed – " + e.message);
  return;
}

// 7. Output frontmatter with populated fields
tR += `---
type: literature
created: ${tp.date.now("YYYY-MM-DD HH:mm")}
status: draft
ready_for_processing: false
tags: [youtube, video-content]
visibility: private
source: youtube
author: ${channelName}
video_id: ${videoId}
channel: ${channelName}
---

`;
%>

# <% videoTitle %>

## Video Information
- **Channel**: <% channelName %>
- **Video URL**: <% youtubeUrl %>
- **Video ID**: `<% videoId %>`
- **Date Saved**: <% tp.date.now("YYYY-MM-DD") %>
- **Tags**: <% allTags.map(t => `#${t}`).join(" ") %>
<% thumbnailUrl ? `- **Thumbnail**: ![Video Thumbnail](${thumbnailUrl})` : "" %>

## Why I'm Saving This
<% quickSummary %>

## Key Takeaways
<!-- As you watch, capture key points here -->

### Main Insight
> 

**Timestamp**: 

### Supporting Points
<!-- Add more as you watch -->

## My Thoughts & Applications

### How This Connects
<!-- Links to your existing knowledge -->

### Action Items
- [ ] 

## Related Notes
<!-- Add [[wiki-links]] as you make connections -->

## AI Processing Approval

> **📋 Action Required**: Check this box when you're ready for AI processing  
> This will trigger automatic transcript extraction, quote generation, and tag enhancement.  
> Keep unchecked while you're still taking notes to avoid interrupting your workflow.

- [ ] Ready for AI processing #youtube-process

## Video Metadata
<!-- Auto-filled for future reference -->
- **Captured**: <% tp.date.now("YYYY-MM-DD HH:mm") %>
- **Source Type**: YouTube Video
- **Processing Status**: `status: inbox`

---
*YouTube video saved from: <% channelName %>*
