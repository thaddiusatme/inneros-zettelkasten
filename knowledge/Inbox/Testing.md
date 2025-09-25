---
created: 2025-09-23 18:16
type: dashboard
tags: [dataview, dataview-plugin, note-taking, note-taking-systems, plugin, tag-management,
  tags, vault-organization]
quality_score: 0.85
ai_processed: '2025-09-24T14:10:09.391960'
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

