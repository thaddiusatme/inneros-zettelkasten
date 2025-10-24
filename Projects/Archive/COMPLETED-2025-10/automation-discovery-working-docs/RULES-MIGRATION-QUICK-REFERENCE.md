# Rules Migration - Quick Reference Card

> **Copy/paste these commands in order**

---

## 🚀 Execute in Terminal (10 minutes)

```bash
# ============================================
# STEP 1: BACKUP (1 min)
# ============================================
cd /Users/thaddius/repos/inneros-zettelkasten
mkdir -p .windsurf/archive/rules-backup-2025-10-07
cp -r .windsurf/rules/* .windsurf/archive/rules-backup-2025-10-07/
ls -lh .windsurf/archive/rules-backup-2025-10-07/

# ============================================
# STEP 2: DEPRECATE OLD FILES (2 min)
# ============================================
mv .windsurf/rules/file-organization.md \
   .windsurf/archive/rules-backup-2025-10-07/DEPRECATED-file-organization.md

mv .windsurf/rules/updated-windsurfrules-v4-concise.md \
   .windsurf/archive/rules-backup-2025-10-07/DEPRECATED-updated-windsurfrules-v4-concise.md

ls .windsurf/rules/  # Should show 9 files

# ============================================
# STEP 3: ADD NEW AUTOMATION RULES (1 min)
# ============================================
cp Projects/ACTIVE/automation-monitoring-requirements-RULES.md \
   .windsurf/rules/automation-monitoring-requirements.md

ls -lh .windsurf/rules/automation-monitoring-requirements.md
wc -c .windsurf/rules/automation-monitoring-requirements.md  # Should be ~5500

# ============================================
# STEP 4: UPDATE README (3 min) - MANUAL
# ============================================
open .windsurf/rules/README.md
# Copy entire content from Projects/ACTIVE/RULES-MIGRATION-GUIDE.md (Step 4 section)
# Save and close

# ============================================
# STEP 5: VERIFY (2 min)
# ============================================
ls -lh .windsurf/rules/  # Should show 10 files
wc -c .windsurf/rules/*.md | sort -n  # All under 12,000 chars
ls .windsurf/rules/ | grep -E "(^file-organization\.md$|windsurfrules-v4)"  # Should be empty

# ============================================
# STEP 6: TEST AI (1 min)
# ============================================
# Start new Cascade chat and ask:
# "What are the 4 phases required for all new features?"
# Should mention: Engine, CLI, Automation, Monitoring
```

---

## 🚨 If Something Goes Wrong

```bash
# ROLLBACK: Restore from backup
rm -rf .windsurf/rules/*
cp -r .windsurf/archive/rules-backup-2025-10-07/* .windsurf/rules/
ls -lh .windsurf/rules/  # Should show original 11 files
```

---

## ✅ Success Indicators

After Step 5, you should see:

```
$ ls .windsurf/rules/
README.md
architectural-constraints.md
automation-monitoring-requirements.md  ← NEW
content-standards.md
privacy-security.md
updated-ai-integration.md
updated-current-issues.md
updated-development-workflow.md
updated-file-organization.md
updated-session-context.md

Total: 10 files (down from 11)
```

After Step 6, Cascade should mention:
- ✅ Phase 1: Core Engine
- ✅ Phase 2: CLI Integration  
- ✅ Phase 3: Automation Layer
- ✅ Phase 4: Monitoring & Alerts

---

**Ready?** Copy commands from Step 1 and execute! 🎯
