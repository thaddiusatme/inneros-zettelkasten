<%*
const folder = "Reviews";
const sprint = await tp.system.prompt("Sprint ID (e.g. 001)");
if (!sprint) { await tp.system.alert("Cancelled – no sprint ID given."); return; }
const fileName = `sprint-${sprint}-retro`;
const created = tp.date.now("YYYY-MM-DD HH:mm");
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
tR += `---
type: review
scope: sprint-retrospective
sprint_id: ${sprint}
created: ${created}
status: draft
tags: [retrospective, sprint]
tz: America/Los_Angeles
template_id: core-sprint-retro
template_version: 1.0.0
---`;
%>

# 🔁 Sprint <% sprint %> Retrospective

## ✅ What Went Well
- 

## ⚠️ What Didn’t Go Well
- 

## 🔧 What To Improve (Process/Tools)
- 

## 📈 MVP Metrics
- Content published:
- Leads created:
- Days of consistency (streak):
- Sentiment (1–5):

## 🧭 Decisions & Rationale
- 

## 📌 Actions (in-note only)
- [ ] 
