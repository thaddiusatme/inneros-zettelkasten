<%*
const topic = await tp.system.prompt("Enter topic");
if (topic) {
    const sanitizedTopic = topic.toLowerCase().replace(/\s+/g, "-");
    const newFileName = `fleeting-${tp.date.now("YYYY-MM-DD")}-${sanitizedTopic}`;
    const newFolder = "Fleeting Notes";
    await tp.file.rename(newFileName); // Just rename the file
    await tp.file.move(`${newFolder}/${newFileName}`); // Then move it into folder
}
%>

**Type**: 🧠 Fleeting Note  
**Created**: <% tp.date.now("YYYY-MM-DD") %> <% tp.date.now("HH:mm") %>  
**Tags**: #fleeting #inbox  

---

## Thought  
Write the idea that just popped into your head.

## Context  
Where did this come from? (Article, conversation, reflection, etc.)

## Next Step  
- [ ] Convert to permanent note?
