<%*
const folder = "Reviews";
const sprint = await tp.system.prompt("Sprint ID (e.g. 001)");
const date = tp.date.now("YYYY-MM-DD");
const fileName = `sprint-${sprint}-review`;
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
%>
---
type: review
scope: sprint-review
sprint_id: <% sprint %>
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: draft
tags: ["#review", "#sprint"]
tz: America/Los_Angeles
template_id: core-sprint-review
template_version: 1.0.0
---

# 🚀 Sprint <% sprint %> Review — <% date %>
 
## 📈 MVP Metrics
- Content published:
- Leads created:
- Days of consistency (streak):
- Sentiment (1–5):

## ✅ What Shipped
- 

## 🔍 KPIs & Outcomes
- 

## 🧭 Highlights & Notable Learnings
- 

## 🧹 Minimal Content Pipeline Maintenance
- Review backlog health (5 min)
- Prune stale ideas (5 min)
- Tag/link high-potential items (5 min)

## 🎯 Next Sprint Candidates
- [ ] 

## 📌 Actions (in-note only)
- [ ] 
