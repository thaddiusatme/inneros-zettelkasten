# InnerOS Quick Reference

> Print this or keep it handy for daily use

---

## 🎯 Essential Commands

```bash
make status    # Check system health
make up        # Start automation
make down      # Stop automation
make review    # Weekly review
make fleeting  # Fleeting notes health
```

---

## 📥 Create Notes

### Fleeting Note (Quick Capture)

```yaml
---
type: fleeting
created: 2025-12-04
status: inbox
tags: [idea]
---

# My Thought

Content here...
```

### YouTube Note

```yaml
---
title: "Video Title"
source: youtube
video_id: XXXXXXXXXXX
ready_for_processing: false
---

# Video Title

My notes...
```

Change `ready_for_processing: true` when ready for AI quotes.

---

## 🔧 Quick Fixes

| Problem | Solution |
|---------|----------|
| Daemon not running | `make up` |
| No AI response | Check Ollama: `ollama list` |
| Notes not found | Verify path: `ls knowledge/Inbox/` |
| YouTube not processing | Check `ready_for_processing: true` |

---

## 📁 Key Directories

```text
knowledge/
├── Inbox/          # New notes go here
├── Fleeting Notes/ # Quick captures  
├── Literature Notes/
└── Permanent Notes/ # Promoted notes
```

---

## 🔗 Full Documentation

- **User Guide**: [docs/USER-GUIDE.md](USER-GUIDE.md)
- **Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Automation**: [docs/HOWTO/automation-user-guide.md](HOWTO/automation-user-guide.md)
