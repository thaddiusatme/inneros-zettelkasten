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

**Type**: 📌 Permanent Note  
**Created**: <% tp.date.now("YYYY-MM-DD") %> <% tp.date.now("HH:mm") %>  
**Tags**: #permanent #zettelkasten  

---

## Core Idea  
Express the idea in your own words — make it atomic.

## Why It Matters  
Why is this idea important? How does it connect to your interests or work?

## Links  
- Related: [[Note A]], [[Note B]]  
- Source (if applicable): URL or citation
