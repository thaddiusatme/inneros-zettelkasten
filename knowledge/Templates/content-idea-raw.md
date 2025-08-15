---
type: content
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: idea
pillar: 
channel: 
tags: [content, idea]
---
<%*
/*------------------------------------------------------------------
  1. Capture Idea Title
------------------------------------------------------------------*/
const rawTitle = await tp.system.prompt("Content idea title (required)");
if (!rawTitle) {
  await tp.system.alert("Cancelled – no idea title given.");
  return;
}

/*------------------------------------------------------------------
  2. Pick Pillar and Channel (Optional for Raw Ideas)
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
const fname  = `content-raw-${stamp}-${slug}.md`;
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

# <% rawTitle %>

## Initial Idea
<!-- Capture the raw idea quickly -->

## Potential Angles
<!-- Different ways to approach this topic -->
- 

## Target Audience
<!-- Who would this resonate with? -->

## Why Now?
<!-- Why is this relevant/timely? -->

## Quick Notes
<!-- Any additional thoughts, links, inspiration -->

---

## Workflow Notes
- **Status**: Raw idea - needs development and triage
- **Next Steps**: 
  - [ ] Develop concept further
  - [ ] Research audience/market fit
  - [ ] Move to Content Pipeline when ready
  - [ ] Update status to 'promoted' when processed

## Pillar: <% pillar %>
## Channel: <% channel %>
