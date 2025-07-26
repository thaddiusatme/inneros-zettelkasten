---
type: literature
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
tags: [literature, <% tp.system.prompt("Add relevant tags (comma-separated)") %>]
visibility: private
source: <% tp.system.prompt("Source (URL, book title, etc.)") %>
author: <% tp.system.prompt("Author name") %>
---

# <% tp.file.title %>

## Source Information
- **Author**: <% tp.system.prompt("Author name") %>
- **Title**: <% tp.system.prompt("Full title") %>
- **URL/Reference**: <% tp.system.prompt("URL or citation") %>
- **Date Accessed**: <% tp.date.now("YYYY-MM-DD") %>

## Key Highlights

### Quote/Highlight 1
> "<% tp.system.prompt("First key quote or highlight") %>"

**Context**: <% tp.system.prompt("Why is this important? What does it connect to?") %>

### Quote/Highlight 2
> "<% tp.system.prompt("Second key quote or highlight") %>"

**Context**: <% tp.system.prompt("Why is this important? What does it connect to?") %>

### Quote/Highlight 3
> "<% tp.system.prompt("Third key quote or highlight") %>"

**Context**: <% tp.system.prompt("Why is this important? What does it connect to?") %>

## My Thoughts & Connections

<% tp.system.prompt("What are your thoughts on this material? How does it connect to your existing knowledge?") %>

## Related Notes
- [[<% tp.system.prompt("Link to related permanent note") %>]]
- [[<% tp.system.prompt("Link to related concept") %>]]

## Next Actions
- [ ] <% tp.system.prompt("What should you do with this information?") %>
- [ ] Review and potentially promote key insights to permanent notes
- [ ] Update status to 'promoted' when processed

---
*Literature note created from: <% tp.system.prompt("Brief source description") %>*
