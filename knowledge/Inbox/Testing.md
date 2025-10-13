---
created: 2025-09-23 18:16
type: dashboard
tags: [dataview, dataview-plugin, markdown, note-taking, note-taking-systems, plugin,
  tag-management, tagging-system]
quality_score: 0.85
ai_processed: '2025-10-12T19:27:08.924519'
---
$
# 🏷️ Tag Dashboard

This note gives you a live view of all tags in your vault.  
Requires the **Dataview** plugin.

---

## 📊 All Tags with Counts

```dataview
TABLE length(rows) AS "Count"
FROM ""
FLATTEN file.tags AS tag
GROUP BY tag
SORT length(rows) DESC
```
```

