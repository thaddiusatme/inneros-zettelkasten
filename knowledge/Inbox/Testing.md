---
created: {{date}}
type: dashboard
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
