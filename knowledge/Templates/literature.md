---
type: literature
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: inbox
tags: [literature]
visibility: private
source: 
author: 
---
<%*
/*------------------------------------------------------------------
  1. Capture Source Information
------------------------------------------------------------------*/
const sourceTitle = await tp.system.prompt("Source title (article, book, etc.)");
if (!sourceTitle) {
  await tp.system.alert("Cancelled – no source title given.");
  return;
}

const author = await tp.system.prompt("Author name");
const sourceUrl = await tp.system.prompt("URL or citation (optional)", "");
const tags = await tp.system.prompt("Additional tags (comma-separated, optional)", "");

/*------------------------------------------------------------------
  2. Build File Name & Path
------------------------------------------------------------------*/
const slug   = sourceTitle.toLowerCase()
                          .replace(/[^a-z0-9]+/g,"-")
                          .replace(/(^-|-$)/g,"");
const stamp  = tp.date.now("YYYYMMDD-HHmm");
const fname  = `lit-${stamp}-${slug}.md`;
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
