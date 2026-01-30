<%*
const folder = "Reviews";
const sprint = await tp.system.prompt("Sprint ID (e.g. 001)");
const fileName = `sprint-${sprint}-retro`;
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
%>
---
type: review
scope: sprint-retrospective
sprint_id: <% sprint %>
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: draft
tags: ["#retrospective", "#sprint"]
tz: America/Los_Angeles
template_id: core-sprint-retro
template_version: 1.0.0
---

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
