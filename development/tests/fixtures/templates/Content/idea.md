---
type: content
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: idea
pillar: "<%* /* set later via suggester */ _ = null; %>"
channel: "<%* /* set later via suggester */ _ = null; %>"
tags: [content, idea]
template_id: project-content-idea
template_version: 1.0.0
---
<%*
/*------------------------------------------------------------------
  1. Capture Title
------------------------------------------------------------------*/
const rawTitle = await tp.system.prompt("Idea title (required)");
if (!rawTitle) {
  await tp.system.alert("Cancelled – no title given.");
  return;
}

/*------------------------------------------------------------------
  2. Pick Pillar and Channel
------------------------------------------------------------------*/
const pillars  = ["AI Automation","Productivity","Personal Story",
                  "Marketing Strategy","Other","Skip for now"];
const pillar   = await tp.system.suggester(pillars, pillars);
if (!pillar) {
  await tp.system.alert("Cancelled – no pillar selected.");
  return;
}

const channels = ["Threads","Instagram Reel","Newsletter",
                  "YouTube","Blog","Other","Skip for now"];
const channel  = await tp.system.suggester(channels, channels);
if (!channel) {
  await tp.system.alert("Cancelled – no channel selected.");
  return;
}

/*------------------------------------------------------------------
  3. Build File Name & Path
------------------------------------------------------------------*/
const slug   = rawTitle.toLowerCase()
                       .replace(/[^a-z0-9]+/g,"-")
                       .replace(/(^-|-$)/g,"");
const stamp  = tp.date.now("YYYYMMDD-HHmm");
const fname  = `${stamp}-${slug}.md`;
// Default to Inbox for triage, or move to pipeline if mature
const target = `Inbox/${fname}`;

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
%>
<!-- Dynamic fields pillar/channel populated below -->

> **Pillar**: <% pillar %>
> **Channel**: <% channel %>

# <% rawTitle %>

## Core Concept
<!-- What is the single main idea? -->

## Outline / Angle
- **Hook**:
- **Key Points**:
- **CTA/Takeaway**:

## Research & Notes
<!-- Links, voice memos, loose thoughts -->

## Next Steps
- [ ] Refine concept
- [ ] Move to Content Pipeline
