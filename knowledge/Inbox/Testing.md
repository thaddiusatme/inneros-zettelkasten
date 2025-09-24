---
created: 2025-09-23 18:16
type: dashboard
tags: [dataview-plugin, note-taking-systems, tag-management, vault-organization]
quality_score: 0.4
ai_processed: '2025-09-23T22:19:44.572363'
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

