---
type: permanent
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: draft
tags: [permanent, zettelkasten]
visibility: private
template_id: core-permanent
template_version: 1.0.0
---
<%*
/*------------------------------------------------------------------
  1. Capture Topic/Title
------------------------------------------------------------------*/
const rawTopic = await tp.system.prompt("What's the core concept or idea?");
if (!rawTopic) {
  await tp.system.alert("Cancelled – no topic given.");
  return;
}

/*------------------------------------------------------------------
  2. Build File Name & Path
------------------------------------------------------------------*/
const slug   = rawTopic.toLowerCase()
                       .replace(/[^a-z0-9]+/g,"-")
                       .replace(/(^-|-$)/g,"");
const stamp  = tp.date.now("YYYYMMDD-HHmm");
const fname  = `${stamp}-${slug}.md`;
const target = `Permanent Notes/${fname}`;

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

## Core Idea  
Express the idea in your own words — make it atomic.

## Why It Matters  
Why is this idea important? How does it connect to your interests or work?

## Links  
- Related: [[Note A]], [[Note B]]  
- Source (if applicable): URL or citation
