---
type: fleeting
created: 2025-07-21 19:31
status: inbox
tags: [#fleeting, #inbox]
visibility: private
---
<!--
NOTE: For actual note creation, use:
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
-->
<%*
// WORKFLOW: New fleeting notes should be created in the Inbox folder (or your default note location) with status: inbox in the YAML frontmatter.
// During triage, move the note to the Fleeting Notes folder to enter the main fleeting note workflow.
const topic = await tp.system.prompt("Enter topic");
if (topic) {
    const sanitizedTopic = topic.toLowerCase().replace(/\s+/g, "-");
    const newFileName = `fleeting-${tp.date.now("YYYY-MM-DD")}-${sanitizedTopic}`;
    const newFolder = "Fleeting Notes";
    await tp.file.rename(newFileName); // Just rename the file
    await tp.file.move(`${newFolder}/${newFileName}`); // Then move it into folder
}
%>
---
type: fleeting
created: 2025-07-21 19:31
status: inbox
tags: [#fleeting, #inbox]
visibility: private
---
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
