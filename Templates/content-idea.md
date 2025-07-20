---
created: {{date:YYYY-MM-DD HH:mm}}
status: idea
pillar: 
channel: 
tags: [content, idea]
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
                  "Marketing Strategy","Other"];
const pillar   = await tp.system.suggester(pillars, pillars);
if (!pillar) {
  await tp.system.alert("Cancelled – no pillar selected.");
  return;
}

const channels = ["Threads","Instagram Reel","Newsletter",
                  "YouTube","Blog","Other"];
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
const target = `Content Pipeline/Idea Backlog/${fname}`;

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
---
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: idea
pillar: "<% pillar %>"
channel: "<% channel %>"
tags: [content, idea]
---

## Hook  
<% rawTitle %>

## Outline  
- Premise:  
- Key points:  
- CTA:  

## Notes  
Loose thoughts, links, voice memos.
