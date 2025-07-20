<%*
const date = tp.date.now("YYYY-MM-DD");
const fileName = `weekly-review-${date}`;
const folder = "Reviews"; // optional — change or remove if you don’t want a folder
await tp.file.rename(fileName);
await tp.file.move(`${folder}/${fileName}`);
%>

# 🧠 Weekly Review — Week of <% date %>

## 🎯 Goals Check-in
- What worked?
- What didn’t?
- What surprised me?

---

## 📥 Fleeting Notes to Process
- [ ] Review all notes tagged with `#fleeting`
- [ ] Archive/delete anything that’s noise
- [ ] Convert top 1–3 into permanent notes

---

## 🧠 New Permanent Notes This Week
- [[zettel-...]]
- [[zettel-...]]

---

## 🧭 Patterns, Themes, or Questions
- Any ideas worth revisiting?
- Topics you keep circling back to?
- Confusions to explore?

---

## 🧹 Knowledge Housekeeping
- [ ] Tag untagged notes
- [ ] Link orphan notes
- [ ] Backup vault (if not synced)
