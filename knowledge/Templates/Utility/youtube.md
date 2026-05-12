<%*
/*------------------------------------------------------------------
  YOUTUBE VIDEO CAPTURE TEMPLATE - API POWERED
  Uses YouTube oEmbed API to auto-fetch metadata
  Total prompts: 2 (URL + reason why)
------------------------------------------------------------------*/

// 1. Get YouTube URL (required) - PROMPT 1
const youtubeUrl = await tp.system.prompt("YouTube URL");
if (!youtubeUrl) {
  new Notice("Cancelled – no YouTube URL given.");
  return;
}

// 2. Extract video ID from various YouTube URL formats
let videoId = "";
const patterns = [
  /(?:youtube\.com|m\.youtube\.com)\/watch\?v=([a-zA-Z0-9_-]{11})/,
  /(?:youtube\.com|m\.youtube\.com)\/watch\?.*v=([a-zA-Z0-9_-]{11})/,
  /youtu\.be\/([a-zA-Z0-9_-]{11})/,
  /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
  /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/,
  /youtube\.com\/live\/([a-zA-Z0-9_-]{11})/,
  /^([a-zA-Z0-9_-]{11})$/  // Just the video ID itself
];

for (const pattern of patterns) {
  const match = youtubeUrl.trim().match(pattern);
  if (match) {
    videoId = match[1];
    break;
  }
}

if (!videoId) {
  new Notice("Could not extract video ID from URL. Please check the URL format.");
  return;
}

// 3. Fetch video metadata via user script (handles CORS properly)
let videoTitle = "Loading...";
let channelName = "Unknown";
let thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;

const metadata = await tp.user.fetch_youtube_metadata(youtubeUrl);

if (metadata) {
  videoTitle = metadata.title;
  channelName = metadata.author_name;
  if (metadata.thumbnail_url) thumbnailUrl = metadata.thumbnail_url;
} else {
  // Manual entry - copy title from YouTube page
  videoTitle = await tp.system.prompt("Video title (copy from YouTube)") || "Untitled Video";
  channelName = await tp.system.prompt("Channel name") || "Unknown Channel";
}

// 4. Ask why they're saving this - PROMPT 2
const quickSummary = await tp.system.prompt("Why are you saving this video?");

// 5. Build filename from video title
const slug = videoTitle.toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/(^-|-$)/g, "")
  .substring(0, 60); // Limit length

const stamp = tp.date.now("YYYYMMDD-HHmm");
const fname = `lit-${stamp}-${slug}`;
const target = `Inbox/YouTube/${fname}`;

// 6. Default tags
const allTags = ["youtube", "video-content"];

// 7. Rename file to use video title (fixes issue #82)
await tp.file.move(target);

// 8. Output frontmatter with populated fields
tR += `---
type: literature
created: ${tp.date.now("YYYY-MM-DD HH:mm")}
status: inbox
ready_for_processing: false
tags: [youtube, video-content]
visibility: private
source: youtube
url: ${youtubeUrl}
author: ${channelName}
video_id: ${videoId}
channel: ${channelName}
template_id: literature-youtube
template_version: 1.0.0
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
