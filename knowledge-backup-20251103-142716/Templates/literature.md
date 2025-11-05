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
  STREAMLINED LITERATURE NOTE TEMPLATE
  For articles, books, papers, podcasts (NOT YouTube - use youtube-video.md)
  Total prompts: 6 (down from 17)
------------------------------------------------------------------*/

// 1. Source Information (asked once, reused)
const sourceTitle = await tp.system.prompt("Source title (article, book, paper, etc.)");
if (!sourceTitle) {
  await tp.system.alert("Cancelled – no source title given.");
  return;
}

const author = await tp.system.prompt("Author name");
const sourceUrl = await tp.system.prompt("URL or citation (optional)", "");
const additionalTags = await tp.system.prompt("Additional tags (comma-separated, optional)", "");

// 2. Build filename and move to Inbox
const slug = sourceTitle.toLowerCase()
  .replace(/[^a-z0-9]+/g, "-")
  .replace(/(^-|-$)/g, "");
const stamp = tp.date.now("YYYYMMDD-HHmm");
const fname = `lit-${stamp}-${slug}.md`;
const target = `Inbox/${fname}`;

try {
  await tp.file.rename(fname);
  await tp.file.move(target);
} catch (e) {
  await tp.system.alert("Rename/Move failed – " + e.message);
  return;
}
%>

# <% sourceTitle %>

## Source Information
- **Author**: <% author || "Unknown" %>
- **Title**: <% sourceTitle %>
- **URL/Reference**: <% sourceUrl || "N/A" %>
- **Date Accessed**: <% tp.date.now("YYYY-MM-DD") %>
- **Tags**: <% additionalTags ? additionalTags.split(",").map(t => `#${t.trim()}`).join(" ") : "" %>

## Key Highlights

### Main Takeaway
> "<% await tp.system.prompt("What's the ONE key quote or insight?") %>"

**Why This Matters**: <% await tp.system.prompt("Why is this important to you? What does it connect to?") %>

### Additional Notes
<!-- Add more quotes/highlights as you read -->

## My Thoughts & Connections

<!-- Your synthesis, questions, and connections to existing knowledge -->

## Related Notes
<!-- Add [[wiki-links]] to related notes as you make connections -->

## Next Actions
- [ ] Review and potentially promote key insights to permanent notes
- [ ] Update status to 'promoted' when processed

---
*Literature note created from: <% sourceTitle %> by <% author || "Unknown" %>*
