<%*
const date = tp.date.now("YYYY-MM-DD");
const fileName = `daily-${date}`;
const folder = "Reviews";
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
%>
---
type: review
scope: daily
created: <% tp.date.now("YYYY-MM-DD HH:mm") %>
status: draft
tags: ["#review", "#daily"]
tz: America/Los_Angeles
---

# 🌅 Daily Review — <% date %>

## 📈 Metrics
- Content published:
- Leads created:
- Days of consistency (streak):
- Sentiment (1–5):

## ✅ Top 3
1.
2.
3.

## 🧠 Notes / Reflection
-

## 🔜 Tomorrow's Focus
-

## 📌 Actions (in-note only)
- [ ] 
