<%*
const topic = await tp.system.prompt("Enter topic");
if (topic) {
    const timestamp = tp.date.now("YYYYMMDDHHmm");
    const sanitizedTopic = topic.toLowerCase().replace(/\s+/g, "-");
    const newFileName = `zettel-${timestamp}-${sanitizedTopic}`;
    const newFolder = "Permanent Notes";
    await tp.file.rename(newFileName); // Rename file
    await tp.file.move(`${newFolder}/${newFileName}`); // Move to folder
}
%>
---
type: permanent
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: draft
tags: [permanent, zettelkasten]
visibility: private
---

## Core Idea  
Express the idea in your own words — make it atomic.

## Why It Matters  
Why is this idea important? How does it connect to your interests or work?

## Links  
- Related: [[Note A]], [[Note B]]  
- Source (if applicable): URL or citation
