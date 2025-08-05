---
type: fleeting
created: {{date:YYYY-MM-DD HH:mm}}
status: inbox
tags: [fleeting, inbox]
visibility: private
---
<%*
/*------------------------------------------------------------------
  1. Capture Topic/Idea
------------------------------------------------------------------*/
const rawTopic = await tp.system.prompt("What's the main topic or idea?");
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
const fname  = `fleeting-${stamp}-${slug}.md`;
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
<!--
NOTE: This file uses a static date for validation. For new notes, use:
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
-->

## Thought  
Write the idea that just popped into your head.

## Context  
Where did this come from? (Article, conversation, reflection, etc.)

## Next Step  
- [ ] Convert to permanent note?
